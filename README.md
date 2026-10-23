# Money Weather

A free bot that downloads public US economic data every Monday and saves it as CSV files.
It powers the Money Weather Report dashboard: inflation, pay, money supply, interest rates,
gold, jobs, spending by store type and company profits.

All data is public, from FRED (Federal Reserve Bank of St. Louis) and the open
[gold-prices](https://github.com/datasets/gold-prices) dataset.

## Set up (about 20 minutes, once)

1. **Get a free FRED API key.** Create an account at fred.stlouisfed.org, then go to
   My Account → API Keys → Request API Key. Copy the key. Never paste it into a chat,
   a file in this repo, or a screenshot.
2. **Create a new public repository** on GitHub called `money-weather`, then upload these
   files, keeping the folders (`fetch_data.py`, `README.md`, `.gitignore`,
   `.github/workflows/update-data.yml`).
3. **Store the key as a secret.** In the repo: Settings → Secrets and variables → Actions →
   New repository secret. Name it `FRED_API_KEY` and paste the key. GitHub encrypts it, and
   it is never shown again, even to you.
4. **Run it once by hand.** Actions tab → "Update economy data" → Run workflow. After a minute
   or two, a `data/` folder with four CSV files appears.

From then on it runs every Monday by itself.

## Files it makes

| File | What's in it |
| --- | --- |
| `data/monthly.csv` | Prices, core prices, money supply, rates, gold, unemployment, saving rate, mood, card debt, hourly pay |
| `data/retail.csv` | Store sales by type ($ millions) |
| `data/profits.csv` | Company profits and cash flow ($ billions, yearly pace) |
| `data/gdp.csv` | Real GDP growth by quarter |

## Privacy rule

This repo is public, so it holds public data only. Anything personal, such as Robinhood
exports, goes in a `private/` folder on your own computer. The `.gitignore` file makes sure
that folder is never uploaded.
