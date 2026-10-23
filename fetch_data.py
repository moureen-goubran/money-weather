"""
Money Weather data bot.

Downloads the public economic data behind the Money Weather Report and saves it
as CSV files in the data/ folder. Runs for free on GitHub Actions every week.

Needs one secret: a free FRED API key, read from the FRED_API_KEY environment
variable. The key is never written into this file or into the data.

Uses only Python's built-in libraries, so there is nothing to install.
"""

import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

START = "2014-01-01"
DATA = Path(__file__).parent / "data"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
GOLD_URL = "https://raw.githubusercontent.com/datasets/gold-prices/main/data/monthly.csv"

# Column name in our CSV  ->  FRED series id
MONTHLY = {
    "cpi": "CPIAUCSL",             # consumer prices
    "core_cpi": "CPILFESL",        # prices without food and gas
    "m2_bn": "M2SL",               # money supply, $ billions
    "fed_funds": "FEDFUNDS",       # Fed's interest rate
    "treasury_10y": "GS10",        # 10-year government bond rate
    "treasury_2y": "GS2",          # 2-year government bond rate
    "real_10y": "FII10",           # 10-year rate after inflation
    "unemployment": "UNRATE",
    "saving_rate": "PSAVERT",
    "sentiment": "UMCSENT",        # University of Michigan consumer mood
    "card_debt_bn": "REVOLSL",     # revolving credit, $ millions -> converted to billions below
    "hourly_pay": "CES0500000003", # average hourly pay, private jobs
}
RETAIL = {
    "total": "RSAFS",
    "restaurants_bars": "RSFSDP",
    "groceries": "RSDBS",
    "health_beauty": "RSHPCS",
    "clothing": "RSCCAS",
    "online": "RSNSR",
}
QUARTERLY = {
    "profits_bn": "CP",            # company profits after tax
    "cash_flow_bn": "CNCF",        # company net cash flow
    "real_gdp_growth": "A191RL1Q225SBEA",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "money-weather-bot"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def fred(series_id, key):
    """Return {'YYYY-MM-DD': float or None} for one FRED series."""
    query = urllib.parse.urlencode({
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
        "observation_start": START,
    })
    data = json.loads(get(f"{FRED_URL}?{query}"))
    out = {}
    for obs in data["observations"]:
        value = obs["value"]
        out[obs["date"]] = None if value in (".", "") else float(value)
    return out


def gold():
    """Return {'YYYY-MM-01': price} from the open gold-prices dataset."""
    rows = csv.DictReader(get(GOLD_URL).splitlines())
    return {f"{r['Date'][:7]}-01": float(r["Price"]) for r in rows if r["Date"] >= START[:7]}


def write(path, key_name, key_fmt, columns, series):
    """Write one CSV: a date column plus one column per series."""
    dates = sorted(set().union(*[s.keys() for s in series.values()]))
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow([key_name] + columns)
        for d in dates:
            row = [series[c].get(d) for c in columns]
            if all(v is None for v in row):
                continue
            w.writerow([key_fmt(d)] + [clean(v) for v in row])
    print(f"wrote {path.name}: {len(dates)} rows")


def clean(v):
    """Blank for missing, whole numbers without .0, otherwise up to 4 decimals."""
    if v is None:
        return ""
    v = round(v, 4)
    return int(v) if v == int(v) else v


def quarter(d):
    return f"{d[:4]}-Q{(int(d[5:7]) - 1) // 3 + 1}"


def main():
    key = os.environ.get("FRED_API_KEY")
    if not key:
        sys.exit("Missing FRED_API_KEY. Add it as a repository secret (see README).")
    DATA.mkdir(exist_ok=True)

    monthly = {col: fred(sid, key) for col, sid in MONTHLY.items()}
    monthly["card_debt_bn"] = {d: (v / 1000 if v is not None else None)
                               for d, v in monthly["card_debt_bn"].items()}
    monthly["gold_usd"] = gold()
    cols = ["cpi", "core_cpi", "m2_bn", "fed_funds", "treasury_10y", "treasury_2y", "real_10y",
            "gold_usd", "unemployment", "saving_rate", "sentiment", "card_debt_bn", "hourly_pay"]
    write(DATA / "monthly.csv", "month", lambda d: d[:7], cols, monthly)

    retail = {col: fred(sid, key) for col, sid in RETAIL.items()}
    retail = {c: {d: v for d, v in s.items() if d >= "2017-01-01"} for c, s in retail.items()}
    write(DATA / "retail.csv", "month", lambda d: d[:7], list(RETAIL), retail)

    q = {col: fred(sid, key) for col, sid in QUARTERLY.items()}
    write(DATA / "profits.csv", "quarter", quarter, ["profits_bn", "cash_flow_bn"],
          {c: {d: v for d, v in q[c].items() if d >= "2015-01-01"} for c in ["profits_bn", "cash_flow_bn"]})
    write(DATA / "gdp.csv", "quarter", quarter, ["real_gdp_growth"], {"real_gdp_growth": q["real_gdp_growth"]})


if __name__ == "__main__":
    main()
