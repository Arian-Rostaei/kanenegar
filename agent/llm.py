"""ترجمهٔ کامل و وفادارانهٔ مقاله (بخش‌بخش ولی پیوسته) + سه هایلایت کلیدی در ابتدا."""
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
    ("چیلی", "شیلی"), ("فریپورت", "فری‌پورت"), ("ریوتینتو", "ریو تینتو"), ("نیومنت", "نیومانت"),
]

_FAITHFUL = (
    "قوانین وفاداری: هیچ واقعیت/عدد/درصد/تاریخ/نامی را تغییر نده، حذف نکن یا اضافه نکن. "
    "سال و تاریخ دقیقاً همان مقدار متن اصلی باشد (2026 همان 2026 بماند؛ فقط رقم فارسی شود). "
    "چیزی از خودت نساز. نقل‌قول را با گویندهٔ اصلی بیاور. "
    "اسم خاص فقط از واژه‌نامه؛ خارج از واژه‌نامه عیناً لاتین بماند. "
)
_WA = "; ".join(en + "=" + fa for en, fa in GLOSSARY)

PROMPT_FIRST = (
    "تو مترجم تخصصی معدن/فلزات/ژئوپلیتیک هستی. این نخستین بخش از یک مقاله است که قرار است کامل ترجمه شود. " + _FAITHFUL +
    "واژه‌نامه: " + _WA + "\n"
    "این بخش را بند‌به‌بند، کامل و پیوسته ترجمه کن (خلاصه نکن، پاراگرافی جا نینداز). "
    "فقط یک JSON معتبر برگردان با کلیدهای: title, lede, category, highlights, body. "
    "category از: " + "|".join(CATS) + ". "
    "highlights: دقیقاً سه رشتهٔ کوتاه و مستقل که مهم‌ترین نکات کل خبر باشند (هر کدام یک جمله). "
    "body: آرایه‌ای از رشته‌ها؛ ترجمهٔ کامل و پیوستهٔ همین بخش به‌ترتیب پاراگراف‌های اصلی. "
    "برای سرفصل فرعی فقط اگر خود متن سرفصل دارد از «زیرتیتر|» استفاده کن؛ برای نقل‌قول «نقل|متن||گوینده». "
    "هیچ سرفصل یا مقدمهٔ اضافه نساز."
)

PROMPT_PART = (
    "تو مترجم تخصصی معدن/فلزات هستی. این ادامهٔ همان مقاله است که در حال ترجمهٔ کامل آن هستیم. " + _FAITHFUL +
    "واژه‌نامه: " + _WA + "\n"
    "فقط همین بخش را بند‌به‌بند، کامل و پیوسته ترجمه کن؛ نه خلاصه، نه حذف، نه اضافه. "
    "این ادامه است: تیتر/مقدمه/هایلایت ننویس. "
    "فقط یک JSON معتبر با یک کلید body (آرایهٔ رشته‌ها) برگردان که ترجمهٔ کامل همین بخش به‌ترتیب باشد. "
    "سرفصل فرعی فقط با «زیرتیتر|» اگر خود متن سرفصل دارد؛ نقل‌قول با «نقل|متن||گوینده»."
)

PROMPT_SHORT = (
    "تو مترجم تخصصی معدن/فلزات هستی. فقط یک خلاصهٔ کوتاه در دسترس است (متن کامل نیست). " + _FAITHFUL +
    "واژه‌نامه: " + _WA + "\n"
    "فقط همان را وفادارانه ترجمه کن و چیزی اضافه نکن. "
    "فقط JSON با کلیدهای title, lede, category, highlights, body. "
    "category از: " + "|".join(CATS) + ". highlights دقیقاً سه جملهٔ کلیدی از همین خلاصه. body کوتاه و فقط بر پایهٔ همین خلاصه."
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


def _call(system, user):
    provider = os.environ.get("AGENT_LLM_PROVIDER", "openai").lower()
    key = os.environ.get("AGENT_LLM_API_KEY", "").strip()
    if not key:
        return None
    if provider == "gemini":
        model = os.environ.get("AGENT_LLM_MODEL", "gemini-1.5-flash")
        api = ("https://generativelanguage.googleapis.com/v1beta/models/" + model +
               ":generateContent?key=" + key)
        try:
            resp = _http_json(api, {"Content-Type": "application/json"}, {
                "contents": [{"role": "user", "parts": [{"text": system + "\n\n" + user}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8000}})
            return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print("  [llm] gemini:", str(e)[:90]); return None
    if provider == "anthropic":
        model = os.environ.get("AGENT_LLM_MODEL", "claude-3-5-sonnet-latest")
        try:
            resp = _http_json("https://api.anthropic.com/v1/messages", {
                "Content-Type": "application/json", "x-api-key": key,
                "anthropic-version": "2023-06-01"}, {
                "model": model, "max_tokens": 8000, "system": system,
                "messages": [{"role": "user", "content": user}]})
            return resp["content"][0]["text"]
        except Exception as e:
            print("  [llm] anthropic:", str(e)[:90]); return None
    base = os.environ.get("AGENT_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    for model in _ordered(_live_models(base, key)):
        try:
            resp = _http_json(base + "/chat/completions", {
                "Content-Type": "application/json", "Authorization": "Bearer " + key}, {
                "model": model, "temperature": 0.1, "max_tokens": 8000,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}]})
            return resp["choices"][0]["message"]["content"]
        except Exception as e:
            print("  [llm] مدل", model, "رد شد:", str(e)[:80])
    return None


def _split(text, size=6000):
    paras = text.split("\n")
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 > size and cur:
            chunks.append(cur); cur = p
        else:
            cur = cur + "\n" + p if cur else p
    if cur:
        chunks.append(cur)
    return chunks or [text]


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
    b["highlights"] = [normalize_text(h) for h in (a.get("highlights") or [])]
    b["facts"] = [[normalize_text(f[0]), normalize_text(f[1])]
                  for f in (a.get("facts") or []) if isinstance(f, (list, tuple)) and len(f) == 2]
    nb = []
    for p in (a.get("body") or []):
        if isinstance(p, dict):
            q = dict(p); q["x"] = normalize_text(p.get("x", ""))
            if p.get("by"):
                q["by"] = normalize_text(p["by"])
            nb.append(q)
        else:
            nb.append(p)
    b["body"] = nb
    return b


def translate_article(title, text, source_name, url, full=False):
    if not os.environ.get("AGENT_LLM_API_KEY", "").strip():
        print("  [llm] کلید تنظیم نشده.")
        return None
    text = text or ""
    if not full or len(text) < 400:
        raw = _call(PROMPT_SHORT, "منبع: " + source_name + "\nعنوان: " + title + "\nخلاصه:\n" + text)
        obj = _extract_json(raw or "")
        if not obj:
            return None
        obj.setdefault("body", [])
        obj.setdefault("highlights", [])
    else:
        chunks = _split(text, 6000)
        obj = None
        bodies = []
        for i, ch in enumerate(chunks):
            system = PROMPT_FIRST if i == 0 else PROMPT_PART
            user = ("منبع: " + source_name + "\nعنوان اصلی: " + title +
                    "\n\n=== بخش " + str(i + 1) + " از " + str(len(chunks)) + " ===\n" + ch + "\n=== پایان بخش ===\n")
            raw = _call(system, user)
            o = _extract_json(raw or "")
            if not o:
                print(f"  [llm] بخش {i+1} ناموفق؛ ادامه با بخش‌های دیگر.")
                continue
            if i == 0:
                obj = o
            bodies += (o.get("body") or [])
        if obj is None:
            return None
        obj["body"] = bodies
    if obj.get("category") not in CATS:
        obj["category"] = "market"
    # سه هایلایت در قالب facts تا در بالای صفحهٔ خبر نمایش داده شوند
    hl = (obj.get("highlights") or [])[:3]
    obj["facts"] = [[h, ""] for h in hl]
    obj["title"] = normalize_text(obj.get("title", ""))
    obj["lede"] = normalize_text(obj.get("lede", ""))
    obj["tags"] = [normalize_text(t) for t in (obj.get("tags") or [])]
    obj["body"] = [normalize_text(p) if isinstance(p, str) else p for p in (obj.get("body") or [])]
    return obj
