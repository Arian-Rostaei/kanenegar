"""ترجمه و دسته‌بندی خبر با مدل زبانی (سازگار با فرمت OpenAI)."""
import json
import os
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

CATS = ["copper", "precious", "battery", "rare", "iron", "geo", "market"]

SYSTEM_PROMPT = (
    "تو یک خبرنگار-مترجم تخصصی معدن و زمین‌شناسی هستی. خبر داده‌شده را به فارسی روان و دقیق ترجمه و بازنویسی خبری می‌کنی. "
    "اعداد، نام شرکت‌ها و اصطلاحات فنی را حفظ کن و چیزی از خود اضافه یا اختراع نکن. "
    "فقط یک شیء JSON معتبر (بدون متن اضافه) با این کلیدها برگردان:\n"
    '{\n'
    '  "title": "تیتر فارسی کوتاه و جذاب",\n'
    '  "lede": "چکیده یک‌خطی فارسی",\n'
    '  "category": "یکی از: ' + "|".join(CATS) + '",\n'
    '  "tags": ["برچسب فارسی", "..."],\n'
    '  "facts": [["مقدار","توضیح کوتاه"], ...],\n'
    '  "body": ["پاراگراف فارسی", "زیرتیتر|...", "..."]\n'
    "}\n"
    'در آرایهٔ body، هر عنصر یک پاراگراف است؛ اگر عنصری با "زیرتیتر|" شروع شد، به‌عنوان سرفصل فرعی رندر می‌شود. '
    "لحن رسمی و خبری باشد و ۳ تا  پاراگراف تولید کن."
)


def _http_json(url, headers, payload, timeout=60):
    headers = dict(headers)
    headers["User-Agent"] = UA
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


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


def translate_article(title, summary, source_name, url):
    provider = os.environ.get("AGENT_LLM_PROVIDER", "openai").lower()
    key = os.environ.get("AGENT_LLM_API_KEY", "").strip()
    if not key:
        print("  [llm] کلید ای‌پی‌آی تنظیم نشده؛ از ترجمهٔ این خبر صرف‌نظر می‌شود.")
        return None

    user = (
        "منبع: " + source_name + "\n"
        "پیوند: " + url + "\n"
        "عنوان: " + title + "\n"
        "خلاصه: " + (summary or "(خلاصه‌ای در دسترس نیست)") + "\n"
    )

    raw = None
    if provider == "gemini":
        model = os.environ.get("AGENT_LLM_MODEL", "gemini-1.5-flash")
        api = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + key
        resp = _http_json(api, {"Content-Type": "application/json"}, {
            "contents": [{"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
        })
        try:
            raw = resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            raw = None
    elif provider == "anthropic":
        model = os.environ.get("AGENT_LLM_MODEL", "claude-3-5-sonnet-latest")
        resp = _http_json("https://api.anthropic.com/v1/messages", {
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        }, {
            "model": model,
            "max_tokens": 2048,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user}],
        })
        try:
            raw = resp["content"][0]["text"]
        except Exception:
            raw = None
    else:
        base = os.environ.get("AGENT_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.environ.get("AGENT_LLM_MODEL", "gpt-4o-mini")
        resp = _http_json(base + "/chat/completions", {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
        }, {
            "model": model,
            "temperature": 0.3,
            "max_tokens": 2048,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
        })
        try:
            raw = resp["choices"][0]["message"]["content"]
        except Exception:
            raw = None

    if not raw:
        print("  [llm] پاسخی از مدل دریافت نشد.")
        return None
    obj = _extract_json(raw)
    if not obj or "title" not in obj:
        print("  [llm] خروجی مدل قابل تجزیه نبود.")
        return None
    if obj.get("category") not in CATS:
        obj["category"] = "market"
    return obj
