# 🛒 PriceScope — Cross-Platform Price Tracker

Tracks prices across Amazon, eBay, Walmart, Best Buy, Target, Newegg and more using **Google Shopping RSS** — no API keys needed.

## 📁 File Structure

```
├── fetch_prices.py           # Python price fetcher
├── items.json                # List of items to track (edit this!)
├── docs/
│   ├── prices.json           # Auto-generated price data (committed by GitHub Actions)
│   └── index.jsx             # Dashboard (deploy to GitHub Pages or Vercel)
└── .github/
    └── workflows/
        └── daily_prices.yml  # GitHub Actions cron job
```

## 🚀 Setup (5 minutes)

### 1. Create a GitHub Repo
```bash
git init price-tracker
cd price-tracker
# copy all files here
git add .
git commit -m "init"
git remote add origin https://github.com/YOUR_USERNAME/price-tracker.git
git push -u origin main
```

### 2. Enable GitHub Actions
- Go to your repo → **Settings → Actions → General**
- Set "Workflow permissions" to **Read and write permissions**

### 3. Enable GitHub Pages (for the dashboard)
- Go to **Settings → Pages**
- Source: **Deploy from branch** → `main` / `docs` folder
- Your dashboard will be at: `https://YOUR_USERNAME.github.io/price-tracker/`

### 4. Edit `items.json` to track your items
```json
[
  { "id": "1", "name": "Sony WH-1000XM5 Headphones" },
  { "id": "2", "name": "Nintendo Switch OLED" },
  { "id": "3", "name": "Dyson V15 Vacuum" }
]
```

### 5. Run manually to test
- Go to **Actions tab** → "Daily Price Tracker" → **Run workflow**

## ⏰ Schedule
The action runs at **08:00 UTC daily**. To change, edit `.github/workflows/daily_prices.yml`:
```yaml
cron: "0 8 * * *"   # min hour day month weekday (UTC)
```

## 🧩 Dashboard
The `docs/index.jsx` is a React component. To use it:

**Option A — Vercel (easiest):**
- Connect your GitHub repo to [vercel.com](https://vercel.com) — free tier
- It auto-deploys on every push

**Option B — Run locally:**
```bash
npm create vite@latest dashboard -- --template react
# copy index.jsx into src/App.jsx
npm install recharts
npm run dev
```

Update `PRICES_JSON_URL` in `index.jsx` to your deployed URL to load live data.

## 🤖 AI Recommendations
The **Alternatives** tab calls the Claude API to suggest similar products.
This uses your Claude.ai session — no extra API key needed when running in Claude artifacts.

## 📊 How it works
1. GitHub Actions runs `fetch_prices.py` every morning
2. Script queries Google Shopping RSS for each item in `items.json`
3. Prices are parsed per-platform and saved to `docs/prices.json`
4. GitHub commits the file back to the repo
5. Dashboard reads `prices.json` and displays comparisons + 14-day history
