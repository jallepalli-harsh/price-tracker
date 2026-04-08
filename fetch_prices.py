import requests
import feedparser
import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

# ── Configuration ────────────────────────────────────────────────────────────
ITEMS_FILE  = "items.json"
PRICES_FILE = "docs/prices.json"

PLATFORM_PATTERNS = {
    "Amazon.in":         r"amazon\.in",
    "Flipkart":          r"flipkart\.com",
    "Myntra":            r"myntra\.com",
    "Snapdeal":          r"snapdeal\.com",
    "Croma":             r"croma\.com",
    "Reliance Digital":  r"reliancedigital\.in",
    "Tata CLiQ":         r"tatacliq\.com",
    "Meesho":            r"meesho\.com",
    "JioMart":           r"jiomart\.com",
    "Nykaa":             r"nykaa\.com",
    "PaytmMall":         r"paytmmall\.com",
    "ShopClues":         r"shopclues\.com",
    "Vijay Sales":       r"vijaysales\.com",
    "Ajio":              r"ajio\.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

def detect_platform(url: str) -> str:
    for name, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return name
    if re.search(r"amazon\.", url, re.IGNORECASE):
        return "Amazon.in"
    return "Other"

def extract_price_inr(text: str) -> float | None:
    match = re.search(r"(?:₹|Rs\.?\s*|INR\s*)([\d,]+\.?\d*)", text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(",", ""))
    match = re.search(r"\b(\d{3,6})\b", text)
    if match:
        return float(match.group(1))
    return None

def fetch_google_shopping_india(query: str) -> list[dict]:
    india_query = f"{query} India price"
    url = f"https://www.google.com/search?q={quote_plus(india_query)}&tbm=shop&output=rss&gl=in&hl=en"
    results = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:25]:
            link  = getattr(entry, "link", "")
            title = getattr(entry, "title", "")
            price = None
            for field in ("price", "g_price"):
                raw = entry.get(field)
                if raw:
                    price = extract_price_inr(str(raw))
                    if price: break
            if price is None: price = extract_price_inr(title)
            if price is None: price = extract_price_inr(getattr(entry, "summary", ""))
            if not price: continue
            results.append({"platform": detect_platform(link), "title": title, "price": price, "url": link, "currency": "INR"})
    except Exception as e:
        print(f"  ⚠ Google RSS failed for '{query}': {e}")
    if not results:
        results = _bing_fallback(query)
    return results

def _bing_fallback(query: str) -> list[dict]:
    url = f"https://www.bing.com/shop?q={quote_plus(query + ' India')}&format=rss&mkt=en-IN"
    results = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:25]:
            link  = getattr(entry, "link", "")
            title = getattr(entry, "title", "")
            price = extract_price_inr(title) or extract_price_inr(entry.get("summary", ""))
            if not price: continue
            results.append({"platform": detect_platform(link), "title": title, "price": price, "url": link, "currency": "INR"})
    except Exception as e:
        print(f"  ⚠ Bing fallback failed: {e}")
    return results

def load_items() -> list[dict]:
    if not os.path.exists(ITEMS_FILE):
        default = [
            {"id": "1", "name": "boAt Rockerz 450 Bluetooth Headphones"},
            {"id": "2", "name": "Samsung Galaxy S24 5G"},
            {"id": "3", "name": "Sony Bravia 55 inch 4K TV"},
            {"id": "4", "name": "Apple iPhone 15"},
            {"id": "5", "name": "OnePlus Nord CE 4"},
        ]
        with open(ITEMS_FILE, "w") as f:
            json.dump(default, f, indent=2)
        return default
    with open(ITEMS_FILE) as f:
        return json.load(f)

def run():
    os.makedirs("docs", exist_ok=True)
    history: dict = {}
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE) as f:
            history = json.load(f)
    items = load_items()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for item in items:
        iid, name = item["id"], item["name"]
        print(f"🔍 {name}")
        results = fetch_google_shopping_india(name)
        if iid not in history:
            history[iid] = {"name": name, "history": [], "latest": []}
        history[iid]["name"]   = name
        history[iid]["latest"] = results
        by_platform: dict[str, float] = {}
        for r in results:
            p = r["platform"]
            if p not in by_platform or r["price"] < by_platform[p]:
                by_platform[p] = r["price"]
        history[iid]["history"].append({"date": today, "platforms": by_platform})
        history[iid]["history"] = history[iid]["history"][-90:]
        print(f"  ✓ {len(results)} results | {list(by_platform.keys())}")
    history["_updated"] = datetime.now(timezone.utc).isoformat()
    with open(PRICES_FILE, "w") as f:
        json.dump(history, f, indent=2)
    print(f"\n✅ Saved → {PRICES_FILE}")

if __name__ == "__main__":
    run()
