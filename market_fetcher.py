"""
fetchers/market_fetcher.py
--------------------------
Fetches European equity indices and energy prices.
Data sources:
  - FRED API (https://fred.stlouisfed.org) for macro series
  - Yahoo Finance for equity indices (via yfinance if installed)

Falls back to realistic simulated data in offline/demo mode.
"""

import pandas as pd
import numpy as np
from datetime import datetime

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False


FRED_API_KEY = "YOUR_FRED_API_KEY"   # free at https://fred.stlouisfed.org/docs/api/api_key.html

EQUITY_TICKERS = {
    "EURO STOXX 50":  "^STOXX50E",
    "DAX":            "^GDAXI",
    "CAC 40":         "^FCHI",
    "FTSE MIB":       "FTSEMIB.MI",
    "IBEX 35":        "^IBEX",
}

FRED_SERIES = {
    "EU Natural Gas Price (€/MWh)":  "PNGASEUUSDM",
    "EU Carbon Price (EUA €/t)":     "DCOILBRENTEU",  # proxy; real EUA from ICE
}


def _date_range_monthly(start: str, end: str = None) -> pd.DatetimeIndex:
    end = end or datetime.today().strftime("%Y-%m")
    return pd.date_range(start=start, end=end, freq="MS")


def _simulated_equity_index(
    name: str,
    start: str,
    base: float,
    vol: float,
    drift: float,
    seed: int
) -> pd.Series:
    """Generates a realistic equity index via geometric Brownian motion."""
    rng   = np.random.default_rng(seed)
    dates = _date_range_monthly(start)
    n     = len(dates)
    # Monthly log-returns: drift + volatility shock
    log_returns = (drift / 12) + (vol / np.sqrt(12)) * rng.standard_normal(n)
    # Inject 2020 COVID crash and 2022 rate shock
    for i, d in enumerate(dates):
        if pd.Timestamp("2020-02") <= d <= pd.Timestamp("2020-03"):
            log_returns[i] -= 0.18
        if pd.Timestamp("2020-04") <= d <= pd.Timestamp("2020-05"):
            log_returns[i] += 0.12
        if pd.Timestamp("2022-01") <= d <= pd.Timestamp("2022-09"):
            log_returns[i] -= 0.025
    prices = base * np.exp(np.cumsum(log_returns))
    return pd.Series(prices.round(1), index=dates, name=name)


def get_equity_indices(start: str = "2019-01") -> pd.DataFrame:
    """
    Returns monthly closing prices for major European equity indices.
    Uses yfinance if available; otherwise uses GBM simulation.
    """
    if YFINANCE_AVAILABLE:
        frames = []
        for name, ticker in EQUITY_TICKERS.items():
            try:
                raw = yf.download(ticker, start=start, interval="1mo",
                                  auto_adjust=True, progress=False)
                s = raw["Close"].resample("MS").first().rename(name)
                frames.append(s)
            except Exception:
                pass
        if frames:
            return pd.concat(frames, axis=1).sort_index()

    # ── Offline fallback ──────────────────────────────────────────────────────
    params = [
        ("EURO STOXX 50", 3600, 0.16, 0.07, 0),
        ("DAX",           13000, 0.17, 0.08, 1),
        ("CAC 40",        5500,  0.16, 0.07, 2),
        ("FTSE MIB",      23000, 0.18, 0.06, 3),
        ("IBEX 35",       9200,  0.17, 0.05, 4),
    ]
    series = [_simulated_equity_index(n, start, b, v, d, s) for n, b, v, d, s in params]
    df = pd.concat(series, axis=1)
    df.index.name = "Date"
    return df


def get_energy_prices(start: str = "2019-01") -> pd.DataFrame:
    """
    Returns European natural gas (TTF) and Brent crude prices.
    Uses FRED if API key is set; otherwise uses simulation.
    """
    if FRED_AVAILABLE and FRED_API_KEY != "YOUR_FRED_API_KEY":
        try:
            fred   = Fred(api_key=FRED_API_KEY)
            gas    = fred.get_series("PNGASEUUSDM", observation_start=start).rename("EU Gas ($/MMBtu)")
            brent  = fred.get_series("DCOILBRENTEU", observation_start=start).rename("Brent Crude ($/bbl)")
            return pd.concat([gas, brent], axis=1).resample("MS").mean()
        except Exception:
            pass

    # ── Offline fallback ──────────────────────────────────────────────────────
    rng   = np.random.default_rng(42)
    dates = _date_range_monthly(start)
    n     = len(dates)

    # Gas: spike in 2021-22 energy crisis, then normalise
    gas_vals = []
    for d in dates:
        if d < pd.Timestamp("2021-06"):
            gas_vals.append(round(np.random.uniform(10, 25), 1))
        elif d < pd.Timestamp("2022-09"):
            gas_vals.append(round(np.random.uniform(80, 340), 1))
        elif d < pd.Timestamp("2023-06"):
            gas_vals.append(round(np.random.uniform(40, 130), 1))
        else:
            gas_vals.append(round(np.random.uniform(25, 55), 1))

    # Brent: COVID crash + recovery + Ukraine spike
    brent_vals = []
    for d in dates:
        if d < pd.Timestamp("2020-04"):
            brent_vals.append(round(np.random.uniform(50, 70), 1))
        elif d < pd.Timestamp("2020-06"):
            brent_vals.append(round(np.random.uniform(18, 35), 1))
        elif d < pd.Timestamp("2022-04"):
            brent_vals.append(round(np.random.uniform(45, 90), 1))
        elif d < pd.Timestamp("2022-09"):
            brent_vals.append(round(np.random.uniform(95, 128), 1))
        else:
            brent_vals.append(round(np.random.uniform(72, 95), 1))

    df = pd.DataFrame({
        "EU Gas TTF (€/MWh)":    gas_vals,
        "Brent Crude ($/bbl)":   brent_vals,
    }, index=dates)
    df.index.name = "Date"
    return df


def get_all_market_series(start: str = "2019-01") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (equity_df, energy_df)."""
    return get_equity_indices(start), get_energy_prices(start)
