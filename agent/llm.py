"""ترجمهٔ وفادارانه و کاملِ متن مقاله + واژه‌نامهٔ اجباری اسم‌های خاص."""
import json
import os
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

CATS = ["copper", "precious", "battery", "rare", "iron", "geo", "market",
        "industry", "politics", "defense", "analysis"]

GLOSSARY = [
    ("Ecuador", "اکوادور"), ("Armenia", "ارمنستان"), ("Chile", "شیلی"), ("Peru", "پرو"),
    ("Argentina", "آرژانتین"), ("Bolivia", "بولیوی"), ("Colombia", "کلمبیا"),
    ("Venezuela", "ونزوئلا"), ("Guyana", "گویان"), ("Suriname", "سورینام"),
    ("Brazil", "برزیل"), ("Mexico", "مکزیک"), ("Panama", "پاناما"), ("Canada", "کانادا"),
    ("United States", "ایالات متحده"), ("USA", "آمریکا"), ("China", "چین"),
    ("Japan", "ژاپن"), ("South Korea", "کره جنوبی"), ("North Korea", "کره شمالی"),
    ("Indonesia", "اندونزی"), ("Philippines", "فیلیپین"), ("India", "هند"),
    ("Pakistan", "پاکستان"), ("Australia", "استرالیا"), ("Papua New Guinea", "پاپوآ گینه نو"),
    ("Russia", "روسیه"), ("Kazakhstan", "قزاقستان"), ("Uzbekistan", "ازبکستان"),
    ("Mongolia", "مغولستان"), ("Myanmar", "میانمار"), ("Vietnam", "ویتنام"),
    ("Thailand", "تایلند"), ("Malaysia", "مالزی"), ("Singapore", "سنگاپور"),
    ("Iran", "ایران"), ("Iraq", "عراق"), ("Turkey", "ترکیه"), ("Saudi Arabia", "عربستان سعودی"),
    ("United Arab Emirates", "امارات متحده عربی"), ("UAE", "امارات"), ("Qatar", "قطر"),
    ("Oman", "عمان"), ("Egypt", "مصر"), ("Libya", "لیبی"), ("Algeria", "الجزایر"),
    ("Morocco", "مراکش"), ("Tunisia", "تونس"), ("Sudan", "سودان"), ("Ethiopia", "اتیوپی"),
    ("Kenya", "کنیا"), ("Tanzania", "تانزانیا"), ("Democratic Republic of Congo", "جمهوری دموکراتیک کنگو"),
    ("DRC", "کنگو"), ("Congo", "کنگو"), ("Zambia", "زامبیا"), ("Zimbabwe", "زیمبابوه"),
    ("South Africa", "آفریقای جنوبی"), ("Ghana", "غنا"), ("Guinea", "گینه"),
    ("Mali", "مالی"), ("Burkina Faso", "بورکینافاسو"), ("Niger", "نیجر"),
    ("Nigeria", "نیجریه"), ("Cameroon", "کامرون"), ("Gabon", "گابن"),
    ("Angola", "آنگولا"), ("Mozambique", "موزامبیک"), ("Madagascar", "ماداگاسکار"),
    ("Botswana", "بوتسوانا"), ("Namibia", "نامیبیا"), ("Sierra Leone", "سیرالئون"),
    ("Liberia", "لیبریا"), ("Ivory Coast", "ساحل عاج"), ("Senegal", "سنگال"),
    ("Mauritania", "موریتانی"), ("Eritrea", "اریتره"), ("Somalia", "سومالی"),
    ("Uganda", "اوگاندا"), ("Rwanda", "رواندا"), ("Malawi", "مالاوی"),
    ("BHP", "بی‌اچ‌پی"), ("Rio Tinto", "ریو تینتو"), ("Glencore", "گلنکور"),
    ("Freeport", "فری‌پورت"), ("Codelco", "کودلکو"), ("Vale", "واله"),
    ("First Quantum", "فرست کوانتوم"), ("Teck", "تک"), ("Newmont", "نیومانت"),
    ("Barrick", "بریک"), ("Albemarle", "آلبمارل"), ("SQM", "اس‌کیو‌ام"),
    ("Antofagasta", "آنتوفاگاستا"), ("Anglo American", "انگلو امریکن"),
    ("Zijin", "زیجین"), ("CMOC", "سی‌ام‌او‌سی"), ("Jiangxi Copper", "جیانگشی مس"),
    ("Norilsk", "نوریلسک"), ("Grasberg", "گراسبرگ"), ("Simandou", "سیماندو"),
    ("Escondida", "اسکوندیدا"), ("Kamoa-Kakula", "کاموآ-کاکولا"),
    ("Thacker Pass", "تکر پس"), ("Oyu Tolgoi", "اویو تولگوی"),
]

FIXES = [
    ("عکدک", "اکوادور"), ("عکوادور", "اکوادور"), ("اکوادر", "اکوادور"),
    ("آرمانستان", "ارمنستان"), ("آرمنستان", "ارمنستان"), ("ارمنیستان", "ارمنستان"),
    ("چیلی", "شیلی"), ("فریپورت", "فری‌پورت"), ("ریوتینتو", "ریو تینتو"),
    ("نیومنت", "نیومانت"),
]

_FAITHFUL = (
    "قوانین وفاداری (بسیار مهم): "
    "۱) هیچ واقعیت، عدد، درصد، تاریخ یا نامی را تغییر نده، حذف نکن یا اضافه نکن. "
    "۲) سال‌ها و تاریخ‌ها دقیقاً همان مقدار متن اصلی باشند (مثلاً اگر متن 2026 گفته، خروجی هم 2026 باشد؛ فقط رقم‌ها فارسی شوند). "
    "۳) چیزی از خودت نساز؛ اگر چیزی در متن نیست، ننویس. "
    "۴) نقل‌قول‌ها را با ذکر گویندهٔ اصلی ترجمه کن. "
    "۵) اسم‌های خاص فقط از واژه‌نامه؛ هر اسم خارج از واژه‌نامه عیناً لاتین بماند. "
)

_WA = "; ".join(en + "=" + fa for en, fa in GLOSSARY)

PROMPT_FULL = (
    "تو مترجم تخصصی معدن/فلزات/ژئوپلیتیک هستی. متن کامل یک مقاله در ادامه آمده است. "
    "آن را بند‌به‌بند و وفادارانه به فارسی روان ترجمه کن. " + _FAITHFUL +
    "واژه‌نامه: " + _WA + "\n"
    "پوشش کامل: همهٔ بخش‌ها و پاراگراف‌های متن اصلی را ترجمه کن؛ طول ترجمه باید با طول متن اصلی متناسب باشد "
    "(متن بلند = ترجمهٔ بلند، نه خلاصه). برای سرفصل‌های فرعی از پیشوند «زیرتیتر|» و برای نقل‌قول از «نقل|متن||گوینده» استفاده کن. "
    "فقط یک JSON معتبر برگردان با کلیدهای: title, lede, category, tags, facts, body. "
    "category از: " + "|".join(CATS) + ". "
    "facts شامل اعداد/تاریخ‌های کلیدیِ خود متن (دست‌کم ۴ مورد). "
    "body آرایه‌ای از رشته‌هاست که کل مقاله را به‌ترتیب پوشش می‌دهد. "
    "تنها افزودهٔ مجاز: یک پاراگراف پایانی با «زیرتیتر|تحلیل قیمت و چشم‌انداز» که صرفاً بر پایهٔ خود متن تحلیل کند."
)

PROMPT_SHORT = (
    "تو مترجم تخصصی معدن/فلزات هستی. فقط یک خلاصهٔ کوتاه در ادامه آمده است. "
    "فقط همان را وفادارانه به فارسی ترجمه کن و هیچ چیزی اضافه نکن (متن کامل در دسترس نیست). " + _FAITHFUL +
    "واژه‌نامه: " + _WA + "\n"
    "فقط یک JSON معتبر با کلیدهای: title, lede, category, tags, facts, body. "
    "category از: " + "|".join(CATS) + ". body کوتاه و فقط بر پایهٔ همین خلاصه باشد."
)

PREFER = ["gpt-oss-120b", "llama-3.3-70b", "llama-4-maverick", "llama-4-scout",
          "qwen3-32b", "kimi-k2", "llama-3.1-8b"]


def _with_ua(h):
    h = dict(h); h["User-Agent"] = UA; return h


def _http_json(url, headers, payload, timeout=120):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=_with_ua(headers), method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _http_get_json(url, headers, timeout=30):
    req = urllib.request.Request(url, headers=_with_ua(headers), method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _live_models(base, key):
    try:
        data = _http_get_json(base + "/models", {"Authorization": "Bearer " + key})
        ids = sorted({d.get("id", "") for d in data.get("data", []) if d.get("id")})
        if ids:
            return ids
    except Exception as e:
        print("  [llm] فهرست مدل‌ها نشد:", str(e)[:100])
    return ["openai/gpt-oss-120b", "openai/gpt-oss-20b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


def _ordered(live):
    chosen = []
    for kw in PREFER:
        for m in live:
            if kw in m and m not in chosen:
                chosen.append(m)
    for m in live:
        if m not in chosen:
            chosen.append(m)
    return chosen


def _extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def normalize_text(s):
    if not isinstance(s, str):
        return s
    for wrong, right in FIXES:
        s = s.replace(wrong, right)
    for en, fa in GLOSSARY:
        s = re.sub(r"\b" + re.escape(en) + r"\b", fa, s, flags=re.I)
    return s


def normalize_article(a):
    if not isinstance(a, dict):
        return a
    b = dict(a)
    b["title"] = normalize_text(a.get("title", ""))
    b["lede"] = normalize_text(a.get("lede", ""))
    b["tags"] = [normalize_text(t) for t in (a.get("tags") or [])]
    b["facts"] = [[normalize_text(f[0]), normalize_text(f[1])]
                  for f in (a.get("facts") or []) if isinstance(f, (list, tuple)) and len(f) == 2]
    nb = []
    for p in (a.get("body") or []):
        if isinstance(p, dict):
            q = dict(p)
            q["x"] = normalize_text(p.get("x", ""))
            if p.get("by"):
                q["by"] = normalize_text(p["by"])
            nb.append(q)
        else:
            nb.append(p)
    b["body"] = nb
    return b


def translate_article(title, text, source_name, url, full=False):
    provider = os.environ.get("AGENT_LLM_PROVIDER", "openai").lower()
    key = os.environ.get("AGENT_LLM_API_KEY", "").strip()
    if not key:
        print("  [llm] کلید تنظیم نشده.")
        return None
    system = PROMPT_FULL if full else PROMPT_SHORT
    user = ("منبع: " + source_name + "\nپیوند: " + url + "\nعنوان اصلی: " + title +
            "\n\n=== متن مقاله ===\n" + (text or "(خالی)") + "\n=== پایان متن ===\n")
    raw = None
    if provider == "gemini":
        model = os.environ.get("AGENT_LLM_MODEL", "gemini-1.5-flash")
        api = ("https://generativelanguage.googleapis.com/v1beta/models/" + model +
               ":generateContent?key=" + key)
        try:
            resp = _http_json(api, {"Content-Type": "application/json"}, {
                "contents": [{"role": "user", "parts": [{"text": system + "\n\n" + user}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8000}})
            raw = resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print("  [llm] جمینای خطا:", str(e)[:100])
    elif provider == "anthropic":
        model = os.environ.get("AGENT_LLM_MODEL", "claude-3-5-sonnet-latest")
        try:
            resp = _http_json("https://api.anthropic.com/v1/messages", {
                "Content-Type": "application/json", "x-api-key": key,
                "anthropic-version": "2023-06-01"}, {
                "model": model, "max_tokens": 8000, "system": system,
                "messages": [{"role": "user", "content": user}]})
            raw = resp["content"][0]["text"]
        except Exception as e:
            print("  [llm] آنتروپیک خطا:", str(e)[:100])
    else:
        base = os.environ.get("AGENT_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        for model in _ordered(_live_models(base, key)):
            try:
                resp = _http_json(base + "/chat/completions", {
                    "Content-Type": "application/json", "Authorization": "Bearer " + key}, {
                    "model": model, "temperature": 0.1, "max_tokens": 8000,
                    "messages": [{"role": "system", "content": system},
                                 {"role": "user", "content": user}]})
                raw = resp["choices"][0]["message"]["content"]
                print("  [llm] ✅ مدل سالم:", model)
                break
            except Exception as e:
                print("  [llm] مدل", model, "رد شد:", str(e)[:90])
    if not raw:
        return None
    obj = _extract_json(raw)
    if not obj or "title" not in obj:
        return None
    if obj.get("category") not in CATS:
        obj["category"] = "market"
    obj["title"] = normalize_text(obj.get("title", ""))
    obj["lede"] = normalize_text(obj.get("lede", ""))
    obj["tags"] = [normalize_text(t) for t in (obj.get("tags") or [])]
    obj["facts"] = [[normalize_text(f[0]), normalize_text(f[1])]
                    for f in (obj.get("facts") or []) if isinstance(f, (list, tuple)) and len(f) == 2]
    obj["body"] = [normalize_text(p) if isinstance(p, str) else p for p in (obj.get("body") or [])]
    return obj
