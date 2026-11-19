#!/usr/bin/env python3
"""ایجنت روزانه: متن کامل مقاله را می‌خواند و وفادارانه ترجمه می‌کند."""
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import feeds
import llm
import extract

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ARTICLES_JSON = DATA_DIR / "articles.json"
ARTICLES_JS = DATA_DIR / "articles.js"
HISTORY_JS = DATA_DIR / "market-history.js"

MAX_NEW_PER_RUN = int(os.environ.get("AGENT_MAX_NEW", "6"))
MAX_PER_SOURCE = 2
MAX_TOTAL = int(os.environ.get("AGENT_MAX_TOTAL", "80"))
AGENT_NAME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

YAHOO = {"Au": "GC=F", "Ag": "SI=F", "Cu": "HG=F", "Pt": "PL=F",
         "Pd": "PA=F", "Ni": "NI=F", "Fe": "TIO=F"}


def log(*a):
    print("[agent]", *a)


def load_existing():
    if ARTICLES_JSON.exists():
        try:
            return json.loads(ARTICLES_JSON.read_text(encoding="utf-8"))
        except Exception as e:
            log("هشدار خواندن موجود:", e)
    return []


def fetch_feed(feed):
    items = []
    try:
        req = urllib.request.Request(feed["url"], headers={"User-Agent": AGENT_NAME})
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read()
        root = ET.fromstring(raw)
    except Exception as e:
        log(f"فید {feed['name']} در دسترس نبود:", str(e)[:100])
        return items
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall(".//item") or root.findall(".//atom:entry", ns)
    for it in entries[:30]:
        def text_of(tags):
            for t in tags:
                node = it.find(t)
                if node is None and ":" not in t:
                    node = it.find("atom:" + t, ns)
                if node is not None and (node.text or "").strip():
                    return node.text.strip()
            return ""
        title = html.unescape(text_of(["title"]))
        link = text_of(["link"])
        if not link:
            lnk = it.find("atom:link", ns)
            if lnk is not None:
                link = lnk.get("href", "")
        desc = html.unescape(re.sub(r"<[^>]+>", " ", text_of(["description", "summary", "content"]) or ""))
        if not (title and link):
            continue
        source, headline = feed["name"], title
        if feed["type"] == "gnews" and " - " in title:
            headline, _, tail = title.rpartition(" - ")
            if 2 <= len(tail) <= 40:
                source, title = tail.strip(), headline.strip()
        items.append({"title": title, "link": link.strip(),
                      "summary": desc.strip()[:900], "source": source})
    return items


def is_relevant(item):
    blob = (item["title"] + " " + item["summary"]).lower()
    return any(k.lower() in blob for k in feeds.KEYWORDS)


def norm_title(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def clean_text(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def to_body(paras):
    out = []
    for p in paras:
        p = clean_text(p)
        if not p:
            continue
        if p.startswith("زیرتیتر|"):
            out.append({"t": "h", "x": p.split("زیرتیتر|", 1)[1].strip()})
        elif p.startswith("نقل|"):
            seg = p.split("نقل|", 1)[1]
            if "||" in seg:
                q, by = seg.split("||", 1)
                out.append({"t": "q", "x": q.strip(), "by": by.strip()})
            else:
                out.append({"t": "q", "x": seg.strip()})
        else:
            out.append({"t": "p", "x": p})
    return out


def slugify(title, url):
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] or "news"
    return base + "-" + hashlib.md5(url.encode()).hexdigest()[:6]


def build_article(item, fa, real_url):
    facts = fa.get("facts") or []
    facts = [[str(f[0]), str(f[1])] for f in facts if isinstance(f, (list, tuple)) and len(f) == 2][:8]
    return {
        "id": slugify(item["title"], real_url),
        "cat": fa.get("category", "market"),
        "date": dt.date.today().isoformat(),
        "title": clean_text(fa.get("title", "")) or item["title"],
        "lede": clean_text(fa.get("lede", "")) or item["summary"][:220],
        "tags": [str(t) for t in (fa.get("tags") or [])][:8],
        "facts": facts,
        "body": to_body(fa.get("body") or []),
        "source": item["source"],
        "src": {"name": item["source"], "url": real_url, "orig": item["title"]},
    }


def fetch_history():
    hist = {}
    for sym, tick in YAHOO.items():
        try:
            url = ("https://query1.finance.yahoo.com/v8/finance/chart/" +
                   urllib.parse.quote(tick) + "?range=1y&interval=1d")
            req = urllib.request.Request(url, headers={"User-Agent": AGENT_NAME})
            data = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
            res = data["chart"]["result"][0]
            ts = res.get("timestamp") or []
            closes = (res.get("indicators", {}).get("quote", [{}]) or [{}])[0].get("close") or []
            t, p = [], []
            for i, c in enumerate(closes):
                if c is None or i >= len(ts):
                    continue
                t.append(dt.datetime.utcfromtimestamp(ts[i]).strftime("%Y-%m-%d"))
                p.append(round(float(c), 2))
            if t:
                hist[sym] = {"t": t, "p": p}
        except Exception as e:
            log(f"تاریخچه {sym} دریافت نشد:", str(e)[:80])
    if not hist and HISTORY_JS.exists():
        try:
            txt = HISTORY_JS.read_text(encoding="utf-8")
            m = re.search(r"window\.MARKET_HISTORY = (\{.*\});", txt, re.S)
            if m:
                hist = json.loads(m.group(1))
                log("تاریخچه از فایل موجود بازیابی شد.")
        except Exception:
            pass
    return hist


def write_outputs(articles, hist):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_JSON.write_text(json.dumps(articles, ensure_ascii=False, indent=1), encoding="utf-8")
    ARTICLES_JS.write_text(
        "/* پایگاه دادهٔ مقالات — ایجنت بازنویسی می‌کند. */\n"
        "window.ARTICLES_DATA = " + json.dumps(articles, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    HISTORY_JS.write_text(
        "/* تاریخچهٔ روزانه قیمت. */\n"
        "window.MARKET_HISTORY = " + json.dumps(hist, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    log(f"نوشتن {len(articles)} مقاله + تاریخچهٔ {len(hist)} فلز")


def main():
    existing = load_existing()
    seen_urls = {a.get("src", {}).get("url") for a in existing if a.get("src")}
    seen_titles = {norm_title(a.get("src", {}).get("orig", "")) for a in existing if a.get("src")}

    candidates = []
    for feed in feeds.FEEDS:
        got = fetch_feed(feed)
        log(f"{feed['name']}: {len(got)} خبر دریافت شد")
        for it in got:
            if it["link"] in seen_urls or norm_title(it["title"]) in seen_titles:
                continue
            if is_relevant(it):
                candidates.append(it)
    log(f"پس از فیلتر و حذف تکراری: {len(candidates)} نامزد تازه")

    picked, per_source = [], {}
    for it in candidates:
        if len(picked) >= MAX_NEW_PER_RUN:
            break
        if per_source.get(it["source"], 0) >= MAX_PER_SOURCE:
            continue
        per_source[it["source"]] = per_source.get(it["source"], 0) + 1
        picked.append(it)

    new_articles = []
    for it in picked:
        real_url = extract.resolve_url(it["link"])
        full = extract.extract_text(real_url)
        if full and len(full) > 400:
            log(f"متن کامل ({len(full)} نویسه) از {it['source']}: {it['title'][:50]}")
            fa = llm.translate_article(it["title"], full, it["source"], real_url, full=True)
        else:
            log(f"متن کامل در دسترس نبود؛ فقط خلاصهٔ وفادارانه: {it['title'][:50]}")
            fa = llm.translate_article(it["title"], it["summary"], it["source"], it["link"], full=False)
        if fa:
            new_articles.append(build_article(it, fa, real_url))

    hist = fetch_history()

    if not new_articles:
        log("خبر تازه‌ای برای انتشار نبود.")
        write_outputs(existing, hist)
        return

    merged = new_articles + existing
    merged.sort(key=lambda a: a.get("date", ""), reverse=True)
    merged = merged[:MAX_TOTAL]
    write_outputs(merged, hist)
    log("✅ " + str(len(new_articles)) + " خبر جدید از منابع: " + ", ".join(sorted({a['source'] for a in new_articles})))


if __name__ == "__main__":
    main()
