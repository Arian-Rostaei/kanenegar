#!/usr/bin/env python3
"""ایجنت روزانهٔ کانه‌نگار: دریافت خبر از چند منبع، ترجمهٔ فارسی، انتشار با تنوع منبع."""
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import feeds
import llm

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ARTICLES_JSON = DATA_DIR / "articles.json"
ARTICLES_JS = DATA_DIR / "articles.js"

MAX_NEW_PER_RUN = int(os.environ.get("AGENT_MAX_NEW", "6"))
MAX_PER_SOURCE = 2          # حداکثر ۲ خبر از هر منبع → تنوع رسانه‌ای
MAX_TOTAL = int(os.environ.get("AGENT_MAX_TOTAL", "80"))
AGENT_NAME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def log(*a):
    print("[agent]", *a)


def load_existing():
    if ARTICLES_JSON.exists():
        try:
            return json.loads(ARTICLES_JSON.read_text(encoding="utf-8"))
        except Exception as e:
            log("هشدار: مقالات موجود قابل خواندن نبود:", e)
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
    entries = root.findall(".//item")
    if not entries:
        entries = root.findall(".//atom:entry", ns)

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

        source = feed["name"]
        headline = title
        # در حالت gnews، نام رسانهٔ واقعی انتهای تیتر می‌آید:  "Headline - Reuters"
        if feed["type"] == "gnews" and " - " in title:
            headline, _, tail = title.rpartition(" - ")
            if 2 <= len(tail) <= 40:
                source = tail.strip()
                title = headline.strip()

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
        else:
            out.append({"t": "p", "x": p})
    return out


def slugify(title, url):
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] or "news"
    return base + "-" + hashlib.md5(url.encode()).hexdigest()[:6]


def build_article(item, fa):
    facts = fa.get("facts") or []
    facts = [[str(f[0]), str(f[1])] for f in facts if isinstance(f, (list, tuple)) and len(f) == 2][:6]
    return {
        "id": slugify(item["title"], item["link"]),
        "cat": fa.get("category", "market"),
        "date": dt.date.today().isoformat(),
        "title": clean_text(fa.get("title", "")) or item["title"],
        "lede": clean_text(fa.get("lede", "")) or item["summary"][:220],
        "tags": [str(t) for t in (fa.get("tags") or [])][:8],
        "facts": facts,
        "body": to_body(fa.get("body") or []),
        "source": item["source"],
        "src": {"name": item["source"], "url": item["link"], "orig": item["title"]},
    }


def write_outputs(articles):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_JSON.write_text(json.dumps(articles, ensure_ascii=False, indent=1), encoding="utf-8")
    ARTICLES_JS.write_text(
        "/* این فایل پایگاه دادهٔ مقالات است. ایجنت روزانه آن را بازنویسی می‌کند؛ دستی ویرایش نکنید. */\n"
        "window.ARTICLES_DATA = " + json.dumps(articles, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    log(f"نوشتن {len(articles)} مقاله → articles.js و articles.json")


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

    # انتخاب با سقف هر منبع تا تنوع رسانه‌ای حفظ شود
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
        log(f"ترجمه ({it['source']}):", it["title"][:60])
        try:
            fa = llm.translate_article(it["title"], it["summary"], it["source"], it["link"])
        except Exception as e:
            log("خطای ترجمه:", str(e)[:150])
            fa = None
        if fa:
            new_articles.append(build_article(it, fa))

    if not new_articles:
        log("خبر تازه‌ای برای انتشار نبود؛ پایگاه داده تغییر نمی‌کند.")
        write_outputs(existing)
        return

    merged = new_articles + existing
    merged.sort(key=lambda a: a.get("date", ""), reverse=True)
    merged = merged[:MAX_TOTAL]
    write_outputs(merged)
    log(f"✅ {len(new_articles)} خبر جدید از منابع: " + ", ".join(sorted({a['source'] for a in new_articles})))


if __name__ == "__main__":
    main()
