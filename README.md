# European Macro & Market Intelligence Dashboard

A Python project that aggregates and visualises key European macroeconomic and market indicators — designed to provide the macro context required for private equity investment analysis.

**Live data sources (when connected):** ECB Statistical Data Warehouse · FRED (St. Louis Fed) · Yahoo Finance  
**Offline/demo mode:** realistic simulated series with historically accurate patterns (COVID crash, energy crisis, ECB hiking cycle)

---

## What This Project Covers

| Section | Indicators | Source |
|---|---|---|
| Monetary Policy | ECB Deposit Rate, Euribor 3M | ECB SDW API |
| Inflation | Eurozone HICP YoY | ECB SDW API |
| Equity Markets | EURO STOXX 50, DAX, CAC 40, FTSE MIB, IBEX 35 | Yahoo Finance |
| Energy Prices | EU Natural Gas (TTF), Brent Crude | FRED API |
| Correlation Analysis | Cross-asset Pearson matrix | Derived |
| Macro Regime | Rate cycle × equity performance | Derived |

---

## Project Structure

```
macro_intelligence_dashboard/
│
├── fetchers/
│   ├── ecb_fetcher.py       # ECB API client with offline fallback
│   └── market_fetcher.py    # Yahoo Finance + FRED client with offline fallback
│
├── notebooks/
│   └── macro_dashboard.ipynb  # Full visual dashboard (6 charts + snapshot table)
│
├── data/
│   └── outputs/               # CSV exports + chart PNGs (generated)
│
├── requirements.txt
└── README.md
```

---

## Key Visualisations

1. **ECB Rate Cycle** — Deposit Rate and Euribor 3M with regime annotations (hiking, cutting, stable)
2. **Eurozone Inflation** — Monthly HICP bar chart vs ECB 2% target
3. **Equity Indices** — Rebased performance (100 = Jan 2019) + rolling 3M returns
4. **Energy Prices** — Dual-axis chart: TTF gas and Brent crude with energy crisis overlay
5. **Cross-Asset Correlation Matrix** — Heatmap of monthly return correlations
6. **Macro Regime Analysis** — EURO STOXX 50 returns segmented by ECB rate regime

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/macro_intelligence_dashboard.git
cd macro_intelligence_dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Open the notebook
jupyter notebook notebooks/macro_dashboard.ipynb
```

The notebook runs fully in **offline/demo mode** out of the box — no API key required.

### Enable Live Data (optional)

```bash
pip install yfinance fredapi
```

For FRED data, get a free API key at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) and set it in `fetchers/market_fetcher.py`:

```python
FRED_API_KEY = "your_key_here"
```

---

## Design Notes

- **Dual-mode architecture**: every fetcher tries the real API first and falls back to simulation automatically — no code changes needed.
- **PE relevance**: the macro regime analysis (Section 6) directly informs PE entry/exit timing; energy price data supports sector analysis for climate-focused funds.
- **Extensible**: add new series by extending `ecb_fetcher.py` or `market_fetcher.py` with additional ECB dataset keys or FRED series IDs.

---

## Skills Demonstrated

`Python` · `pandas` · `matplotlib` · `REST APIs` · `ECB SDW` · `FRED` · `Yahoo Finance` · `Time Series Analysis` · `Macro Analysis` · `Jupyter`

---

## Author

**Alessandro Petrucci**  
MSc Quantitative Finance, University of Bologna  
[LinkedIn](https://www.linkedin.com/in/alessandro-petrucci-86b7ab234/) · alessandropetrucci55@gmail.com
