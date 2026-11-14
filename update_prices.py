import json, urllib.request, datetime

SYMBOLS = [
    ("Ngô", "ZC", "ZC=F", "¢/giạ"),
    ("Lúa mì", "ZW", "ZW=F", "¢/giạ"),
    ("Đậu tương", "ZS", "ZS=F", "¢/giạ"),
    ("Dầu đậu tương", "ZL", "ZL=F", "¢/pound"),
    ("Khô đậu tương", "ZM", "ZM=F", "$/tấn thiếu"),
]

def fetch_one(name, code, sym, unit):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=15m&range=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.loads(r.read().decode())["chart"]["result"][0]
    meta = res["meta"]
    closes = [x for x in (res["indicators"]["quote"][0].get("close") or []) if x is not None]
    price = closes[-1] if closes else meta.get("regularMarketPrice", 0)
    prev = meta.get("chartPreviousClose") or meta.get("previousClose") or (closes[0] if closes else price)
    ch = ((price - prev) / prev * 100) if prev else 0
    # downsample to ~32 points for clean sparkline
    step = max(1, len(closes) // 32)
    intraday = [round(x, 2) for x in closes[::step]]
    if len(intraday) < 2:
        intraday = [round(prev, 2), round(price, 2)]
    return {
        "name": name,
        "code": code,
        "price": f"{price:.2f}",
        "unit": unit,
        "ch": round(ch, 2),
        "intraday": intraday,
    }

out = {"updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(), "prices": []}
for item in SYMBOLS:
    try:
        out["prices"].append(fetch_one(*item))
    except Exception as e:
        print(f"WARN {item[1]}: {e}")

if out["prices"]:
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Saved prices.json with", len(out["prices"]), "items")
