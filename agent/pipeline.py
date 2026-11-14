#!/usr/bin/env python3
"""ایجنت روزانهٔ کانه‌نگار

هر اجرا: ۱) خوراک‌های خبری را می‌خواند ۲) اخبار مرتبط را فیلتر می‌کند
۳) اخبار تکراری را حذف می‌کند ۴) با مدل زبانی به فارسی ترجمه می‌کند
۵) پایگاه دادهٔ مقالات و بازار را به‌روزرسانی می‌کند.

فایل‌های خروجی:
  data/articles.json   ← منبع حقیقت (برای پایپلاین)
  data/articles.js     ← داده‌ای که سایت می‌خواند
  data/market.js       ← اعداد بازار (فعلاً دستی/پس‌فرض؛ می‌توان بعداً خودکار کرد)

اجرای محلی:  python3 agent/pipeline.py
"""
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
MARKET_JS = DATA_DIR / "market.js"

MAX_NEW_PER_RUN = int(os.environ.get("AGENT_MAX_NEW", "6"))
MAX_TOTAL = int(os.environ.get("AGENT_MAX_TOTAL", "80"))
AGENT_NAME = "KaneNegarBot/1.0 (news-agent)"


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
        log(f"فید {feed['name']} در دسترس نبود:", str(e)[:120])
        return items

    # پشتیبانی از RSS 2.0 و Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall(".//item")
    if not entries:
        entries = root.findall(".//atom:entry", ns)

    for it in entries[:25]:
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
        pub = text_of(["pubDate", "published"])
        if title and link:
            items.append({"title": title, "link": link.strip(), "summary": desc.strip()[:900],
                          "published": pub, "source": feed["name"]})
    return items


def is_relevant(item):
    blob = (item["title"] + " " + item["summary"]).lower()
    return any(k.lower() in blob for k in feeds.KEYWORDS)


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
    today = dt.date.today().isoformat()
    facts = fa.get("facts") or []
    facts = [[str(f[0]), str(f[1])] for f in facts if isinstance(f, (list, tuple)) and len(f) == 2][:6]
    return {
        "id": slugify(item["title"], item["link"]),
        "cat": fa.get("category", "market"),
        "date": today,
        "title": clean_text(fa.get("title", "")) or item["title"],
        "lede": clean_text(fa.get("lede", "")) or item["summary"][:220],
        "tags": [str(t) for t in (fa.get("tags") or [])][:8],
        "facts": facts,
        "body": to_body(fa.get("body") or []),
        "src": {"name": item["source"], "url": item["link"], "orig": item["title"]},
    }


def write_outputs(articles, market, copper):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_JSON.write_text(json.dumps(articles, ensure_ascii=False, indent=1), encoding="utf-8")
    ARTICLES_JS.write_text(
        "/* این فایل پایگاه دادهٔ مقالات است. ایجنت روزانه آن را بازنویسی می‌کند؛ دستی ویرایش نکنید. */\n"
        "window.ARTICLES_DATA = " + json.dumps(articles, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    MARKET_JS.write_text(
        "window.MARKET_DATA = " + json.dumps(market, ensure_ascii=False) + ";\n"
        "window.COPPER_POINTS = " + json.dumps(copper, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    log(f"نوشتن {len(articles)} مقاله → {ARTICLES_JS.name} و {ARTICLES_JSON.name}")


def default_market():
    # اعداد پایهٔ بازار؛ در نسخهٔ بعدی می‌توان از یک منبع قیمت به‌روز خودکار کرد.
    return [
        {"fa": "مس", "en": "Copper · LME 3M", "sym": "Cu", "price": 13712, "unit": "دلار / تن", "chg": -1.18,
         "date": dt.date.today().isoformat(), "src": "LME", "c": "#E08D4F",
         "note": "سقف 2026: 14٬875 دلار — 10 سپتامبر"},
    ], [
        {"d": "2026-01-29", "v": 14527.5, "label": "رکورد ژانویه", "src": "Benchmark"},
        {"d": "2026-09-10", "v": 14875, "label": "سقف 2026", "src": "Fastmarkets"},
        {"d": "2026-11-12", "v": 13712, "label": "آخرین ثبت", "src": "Westmetall"},
    ]


def main():
    existing = load_existing()
    seen_urls = {a["src"]["url"] for a in existing if a.get("src", {}).get("url")}
    seen_titles = {a["src"].get("orig", "") for a in existing if a.get("src")}

    # ۱+۲) جمع‌آوری و فیلتر
    candidates = []
    for feed in feeds.FEEDS:
        got = fetch_feed(feed)
        log(f"{feed['name']}: {len(got)} خبر دریافت شد")
        for it in got:
            if it["link"] in seen_urls or it["title"] in seen_titles:
                continue
            if is_relevant(it):
                candidates.append(it)
    log(f"پس از فیلتر و حذف تکراری: {len(candidates)} نامزد تازه")

    # ۳+۴) ترجمه با مدل زبانی (تا سقف تعیین‌شده)
    new_articles = []
    for it in candidates[:MAX_NEW_PER_RUN]:
        log("ترجمه:", it["title"][:70])
        try:
            fa = llm.translate_article(it["title"], it["summary"], it["source"], it["link"])
        except Exception as e:
            log("خطای ترجمه:", str(e)[:150])
            fa = None
        if fa:
            new_articles.append(build_article(it, fa))

    if not new_articles:
        log("خبر تازه‌ای برای انتشار نبود؛ پایگاه داده تغییر نمی‌کند.")
        market, copper = default_market()
        write_outputs(existing, market, copper)
        return

    merged = new_articles + existing
    merged.sort(key=lambda a: a.get("date", ""), reverse=True)
    merged = merged[:MAX_TOTAL]

    market, copper = default_market()
    write_outputs(merged, market, copper)
    log(f"✅ {len(new_articles)} خبر جدید منتشر شد.")


if __name__ == "__main__":
    main()
