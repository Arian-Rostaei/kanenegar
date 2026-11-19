"""خواندن و استخراج متن کامل مقاله از سایت منبع (بدون کتابخانهٔ خارجی)."""
import base64
import re
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

SKIP = {"script", "style", "nav", "header", "footer", "aside", "form", "svg",
        "noscript", "iframe", "button", "select", "figure"}
CAPTURE = {"p", "h1", "h2", "h3", "h4", "li", "blockquote", "figcaption", "pre"}


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", "ignore")


def resolve_url(url):
    """لینک‌های خبرگزاری گوگل را به لینک اصلی مقاله تبدیل می‌کند."""
    if "news.google.com" not in url:
        return url
    try:
        page = fetch(url)
        m = re.search(r'data-n-au="([^"]+)"', page)
        if m:
            return m.group(1)
        m = re.search(r'href="(https?://(?!news\.google|www\.google|policies\.google|support\.google|accounts\.google)[^"]+)"', page)
        if m:
            return m.group(1)
        m = re.search(r"/articles/([A-Za-z0-9_\-]+)", url)
        if m:
            s = m.group(1)
            raw = base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
            mm = re.search(rb"https?://[^\x00-\x20\"<>]+", raw)
            if mm:
                return mm.group(0).decode("utf-8", "ignore")
    except Exception:
        pass
    return url


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        self.stack.append(tag)
        if tag in ("br", "p", "li", "h1", "h2", "h3", "h4", "blockquote"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip > 0:
            self.skip -= 1
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "blockquote"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip == 0 and self.stack and self.stack[-1] in CAPTURE:
            self.parts.append(data)

    def text(self):
        t = "".join(self.parts)
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n\s*\n+", "\n\n", t)
        lines = [ln.strip() for ln in t.split("\n")]
        lines = [ln for ln in lines if len(ln) > 2]
        return "\n".join(lines)


def extract_text(url, limit=24000):
    try:
        page = fetch(url)
    except Exception:
        return ""
    p = _TextExtractor()
    try:
        p.feed(page)
    except Exception:
        pass
    txt = p.text()
    if len(txt) < 200:
        return ""
    return txt[:limit]
