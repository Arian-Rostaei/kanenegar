#!/usr/bin/env python3
"""به‌روزرسانی ساعتی: قیمت زنده + تاریخچهٔ یک‌سالهٔ فلزها، از چند منبع با جایگزین.
هرگز دادهٔ خوب قبلی را با دادهٔ خالی بازنویسی نمی‌کند.
"""
import csv
import io
import json
import re
import urllib.request
import datetime as dt
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
ROOT = Path(__file__).resolve().parent.parent
PRICES_JS = ROOT / "data" / "prices-live.js"
HISTORY_JS = ROOT / "data" / "market-history.js"

# نمادهای یاهو (فیوچرز) برای قیمت و تاریخچه
YAHOO = {
    "Au": "GC=F", "Ag": "SI=F", "Pt": "PL=F", "Pd": "PA=F",
    "Cu": "HG=F", "Ni": "NI=F", "Zn": "ZNC=F", "Al": "ALI=F", "Fe": "TIO=F",
}
# نمادهای stooq فقط برای فلزهای گرانبها (منبع جایگزین تاریخچه/قیمت)
STOOQ = {"Au": "xauusd", "Ag": "xagusd", "Pt": "xptusd", "Pd": "xpdusd"}


def _req(url, timeout=25):
    return urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})


def get_json(url):
    with urllib.request.urlopen(_req(url), timeout=25) as r:
        return json.loads(r.read().decode())


def yahoo_quote_and_history(symbol):
    """برمی‌گرداند (آخرین قیمت, سری تاریخچه) یا استثنا."""
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/" + symbol +
           "?range=1y&interval=1d")
    data = get_json(url)
    res = data["chart"]["result"][0]
    ts = res.get("timestamp") or []
    closes = (res.get("indicators", {}).get("quote", [{}]) or [{}])[0].get("close") or []
    t, p = [], []
    for i, c in enumerate(closes):
        if c is None or i >= len(ts):
            continue
        t.append(dt.datetime.utcfromtimestamp(ts[i]).strftime("%Y-%m-%d"))
        p.append(round(float(c), 2))
    last = None
    meta = res.get("meta") or {}
    if meta.get("regularMarketPrice") is not None:
        last = round(float(meta["regularMarketPrice"]), 2)
    elif p:
        last = p[-1]
    return last, {"t": t, "p": p}


def stooq_history(pair):
    url = "https://stooq.com/q/d/l/?s=" + pair + "&i=d"
    with urllib.request.urlopen(_req(url), timeout=25) as r:
        txt = r.read().decode()
    rows = list(csv.reader(io.StringIO(txt)))
    t, p = [], []
    for row in rows[1:]:
        if len(row) >= 5:
            try:
                t.append(row[0]); p.append(round(float(row[4]), 2))
            except ValueError:
                continue
    return {"t": t, "p": p}


def stooq_last(pair):
    url = "https://stooq.com/q/l/?s=" + pair + "&f=sd2t2ohlcv&h&e=csv"
    with urllib.request.urlopen(_req(url), timeout=25) as r:
        rows = list(csv.reader(io.StringIO(r.read().decode())))
    if len(rows) >= 2 and len(rows[1]) > 6:
        return round(float(rows[1][6]), 2)
    return None


def goldapi_last(code):
    d = get_json("https://api.gold-api.com/price/" + code)
    return round(float(d["price"]), 2) if d.get("price") is not None else None


def goldprice_last():
    d = get_json("https://data-asg.goldprice.org/dbXRates/USD")
    item = (d.get("items") or [{}])[0]
    return {"Au": item.get("xauPrice"), "Ag": item.get("xagPrice")}


def load_old_history():
    if not HISTORY_JS.exists():
        return {}
    try:
        txt = HISTORY_JS.read_text(encoding="utf-8")
        m = re.search(r"window\.MARKET_HISTORY = (\{.*\});", txt, re.S)
        return json.loads(m.group(1)) if m else {}
    except Exception:
        return {}


def main():
    now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    prices = {}
    history = {}
    old = load_old_history()
    gp = None
    try:
        gp = goldprice_last()
    except Exception as e:
        print("goldprice.org spot:", str(e)[:80])

    for sym, ysym in YAHOO.items():
        last, hist = None, None
        # ۱) یاهو
        try:
            last, hist = yahoo_quote_and_history(ysym)
            if last is not None:
                prices[sym] = {"price": last, "src": "yahoo", "ts": now}
            if hist and hist["t"]:
                history[sym] = hist
            print(f"{sym}: yahoo ok (price={last}, hist={len(hist['t']) if hist else 0})")
        except Exception as e:
            print(f"{sym}: yahoo fail:", str(e)[:80])
        # ۲) جایگزین‌ها برای گرانبها
        if sym in STOOQ:
            if last is None:
                try:
                    last = goldapi_last(sym if sym != "Au" else "XAU") if False else goldapi_last({"Au":"XAU","Ag":"XAG","Pt":"XPT","Pd":"XPD"}[sym])
                    prices[sym] = {"price": last, "src": "gold-api", "ts": now}
                    print(f"{sym}: gold-api ok ({last})")
                except Exception as e:
                    print(f"{sym}: gold-api fail:", str(e)[:80])
            if last is None and gp and gp.get(sym):
                last = round(float(gp[sym]), 2)
                prices[sym] = {"price": last, "src": "goldprice.org", "ts": now}
                print(f"{sym}: goldprice ok ({last})")
            if not history.get(sym):
                try:
                    h = stooq_history(STOOQ[sym])
                    if h["t"]:
                        history[sym] = h
                        print(f"{sym}: stooq hist ok ({len(h['t'])})")
                except Exception as e:
                    print(f"{sym}: stooq hist fail:", str(e)[:80])
        # ۳) هرگز دادهٔ خوب قبلی را پاک نکن
        if not history.get(sym) and old.get(sym):
            history[sym] = old[sym]
            print(f"{sym}: history kept from previous run")

    PRICES_JS.write_text("window.LIVE_PRICES = " + json.dumps(prices) + ";\n", encoding="utf-8")
    HISTORY_JS.write_text("window.MARKET_HISTORY = " + json.dumps(history) + ";\n", encoding="utf-8")
    print(f"✅ قیمت {len(prices)} فلز + تاریخچه {len(history)} فلز نوشته شد.")


if __name__ == "__main__":
    main()
