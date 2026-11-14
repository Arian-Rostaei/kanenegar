"""ترجمه و دسته‌بندی خبر با مدل زبانی (سازگار با فرمت OpenAI).
این نسخه مستقل از نام مدل است: خودش فهرست زندهٔ مدل‌ها را از سرویس
می‌گیرد و یکی‌یکی امتحان می‌کند تا به اولین مدل سالم برسد.
"""
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
    "لحن رسمی و خبری باشد و ۳ تا ۶ پاراگراف تولید کن."
)

PREFER = ["gpt-oss-120b", "llama-3.3-70b", "llama-4-maverick", "llama-4-scout",
          "qwen3-32b", "kimi-k2", "llama-3.1-8b"]


def _with_ua(headers):
    headers = dict(headers)
    headers["User-Agent"] = UA
    return headers


def _http_json(url, headers, payload, timeout=90):
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
            print("  [llm] مدل‌های زندهٔ سرویس:", ", ".join(ids))
            return ids
    except Exception as e:
        print("  [llm] گرفتن فهرست مدل‌ها نشد:", str(e)[:100])
    return ["openai/gpt-oss-120b", "openai/gpt-oss-20b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


def _ordered_candidates(live):
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


def translate_article(title, summary, source_name, url):
    provider = os.environ.get("AGENT_LLM_PROVIDER", "openai").lower()
    key = os.environ.get("AGENT_LLM_API_KEY", "").strip()
    if not key:
        print("  [llm] کلید ای‌پی‌آی تنظیم نشده.")
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
        api = ("https://generativelanguage.googleapis.com/v1beta/models/"
               + model + ":generateContent?key=" + key)
        try:
            resp = _http_json(api, {"Content-Type": "application/json"}, {
                "contents": [{"role": "user",
                              "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
            })
            raw = resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print("  [llm] جمینای خطا:", str(e)[:100])

    elif provider == "anthropic":
        model = os.environ.get("AGENT_LLM_MODEL", "claude-3-5-sonnet-latest")
        try:
            resp = _http_json("https://api.anthropic.com/v1/messages", {
                "Content-Type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            }, {
                "model": model, "max_tokens": 2048,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user}],
            })
            raw = resp["content"][0]["text"]
        except Exception as e:
            print("  [llm] آنتروپیک خطا:", str(e)[:100])

    else:
        base = os.environ.get("AGENT_LLM_BASE_URL",
                              "https://api.openai.com/v1").rstrip("/")
        live = _live_models(base, key)
        candidates = _ordered_candidates(live)
        for model in candidates:
            try:
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
                raw = resp["choices"][0]["message"]["content"]
                print("  [llm] ✅ مدل سالم:", model)
                break
            except Exception as e:
                print("  [llm] مدل", model, "رد شد:", str(e)[:90])

    if not raw:
        print("  [llm] هیچ مدلی جواب نداد.")
        return None
    obj = _extract_json(raw)
    if not obj or "title" not in obj:
        print("  [llm] خروجی قابل تجزیه نبود.")
        return None
    if obj.get("category") not in CATS:
        obj["category"] = "market"
    return obj
