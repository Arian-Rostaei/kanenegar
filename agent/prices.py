#!/usr/bin/env python3
"""گرفتن قیمت زندهٔ طلا/نقره/پلاتین/پالادیم از چند منبع (سمت سرور، بدون CORS)."""
import csv
import io
import json
import urllib.request
import datetime as dt
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "prices-live.js"

METALS = {"Au": "XAU", "Ag": "XAG", "Pt": "XPT", "Pd": "XPD"}
STOOQ = {"Au": "xauusd", "Ag": "xagusd", "Pt": "xptusd", "Pd": "xpdusd"}


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def from_goldapi(code):
    d = get_json("https://api.gold-api.com/price/" + code)
    p = d.get("price")
    return float(p) if p is not None else None


def from_goldprice():
    d = get_json("https://data-asg.goldprice.org/dbXRates/USD")
    item = (d.get("items") or [{}])[0]
    return {"Au": item.get("xauPrice"), "Ag": item.get("xagPrice")}


def from_stooq(pair):
    url = "https://stooq.com/q/l/?s=" + pair + "&f=sd2t2ohlcv&h&e=csv"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    txt = urllib.request.urlopen(req, timeout=20).read().decode()
    rows = list(csv.reader(io.StringIO(txt)))
    if len(rows) >= 2 and len(rows[1]) > 6:
        return float(rows[1][6])
    return None


def main():
    out = {}
    gp = None
    try:
        gp = from_goldprice()
    except Exception as e:
        print("goldprice.org:", str(e)[:80])

    for sym, code in METALS.items():
        price, src = None, ""
        try:
            price = from_goldapi(code); src = "gold-api.com"
        except Exception as e:
            print(f"gold-api {code}:", str(e)[:80])
        if price is None and gp and gp.get(sym):
            try:
                price = float(gp[sym]); src = "goldprice.org"
            except Exception:
                price = None
        if price is None:
            try:
                price = from_stooq(STOOQ[sym]); src = "stooq.com"
            except Exception as e:
                print(f"stooq {STOOQ[sym]}:", str(e)[:80])
        if price is not None:
            out[sym] = {"price": round(price, 2), "src": src,
                        "ts": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
            print(f"{sym}: {price} ({src})")

    OUT.write_text("window.LIVE_PRICES = " + json.dumps(out) + ";\n", encoding="utf-8")
    print("نوشتن", len(out), "قیمت →", OUT.name)


if __name__ == "__main__":
    main()
