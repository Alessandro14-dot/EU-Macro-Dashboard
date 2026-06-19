"""
fetchers/ecb_fetcher.py
-----------------------
Fetches European macro data from the ECB Statistical Data Warehouse API.
Falls back to realistic simulated data if the API is unavailable (offline/demo mode).

Real API docs: https://data-api.ecb.europa.eu/
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

ECB_BASE = "https://data-api.ecb.europa.eu/service/data"
HEADERS  = {"Accept": "application/json"}


def _date_range_monthly(start: str, end: str = None) -> pd.DatetimeIndex:
    end = end or datetime.today().strftime("%Y-%m")
    return pd.date_range(start=start, end=end, freq="MS")


def _ecb_request(dataset: str, key: str, params: dict) -> pd.Series | None:
    """
    Makes a request to the ECB API and parses the time series.
    Returns None if the request fails.
    """
    url = f"{ECB_BASE}/{dataset}/{key}"
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        data   = r.json()
        values = data["dataSets"][0]["series"]["0:0:0:0:0:0"]["observations"]
        dates  = data["structure"]["dimensions"]["observation"][0]["values"]
        series = pd.Series(
            {pd.to_datetime(d["id"]): float(v[0]) for d, (_, v) in zip(dates, values.items())},
            name=key
        )
        return series
    except Exception:
        return None


# ── Individual series fetchers ────────────────────────────────────────────────

def get_ecb_deposit_rate(start: str = "2019-01") -> pd.Series:
    """ECB Deposit Facility Rate (DFR) — key policy rate."""
    series = _ecb_request(
        "FM", "M.U2.EUR.RT0.MM.EURIBOR3MD_.HSTA",
        {"startPeriod": start, "format": "jsondata"}
    )
    if series is not None:
        return series.rename("ECB Deposit Rate (%)")

    # ── Offline fallback: realistic ECB DFR 2019–2025 ──
    dates  = _date_range_monthly(start)
    # Mirrors real ECB path: low/negative → hiking cycle 2022 → plateau → cuts 2024
    values = []
    for d in dates:
        if d < pd.Timestamp("2022-07"):
            values.append(-0.50)
        elif d < pd.Timestamp("2023-01"):
            values.append(-0.50 + (d.month - 6) * 0.50)
        elif d < pd.Timestamp("2023-10"):
            values.append(2.50 + (d.month - 1) * 0.25)
        elif d < pd.Timestamp("2024-06"):
            values.append(4.00)
        else:
            values.append(max(2.50, 4.00 - (d.month - 5) * 0.25))
    return pd.Series(values[:len(dates)], index=dates, name="ECB Deposit Rate (%)")


def get_euribor_3m(start: str = "2019-01") -> pd.Series:
    """3-month Euribor — key interbank benchmark rate."""
    series = _ecb_request(
        "FM", "M.U2.EUR.RT0.MM.EURIBOR3MD_.HSTA",
        {"startPeriod": start, "format": "jsondata"}
    )
    if series is not None:
        return series.rename("Euribor 3M (%)")

    dates  = _date_range_monthly(start)
    base   = get_ecb_deposit_rate(start)
    spread = np.random.default_rng(0).normal(0.10, 0.05, len(dates))
    values = (base.values + spread).clip(-0.6, 5.5)
    return pd.Series(values, index=dates, name="Euribor 3M (%)")


def get_euro_inflation(start: str = "2019-01") -> pd.Series:
    """Eurozone HICP inflation YoY (%)."""
    series = _ecb_request(
        "ICP", "M.U2.N.000000.4.ANR",
        {"startPeriod": start, "format": "jsondata"}
    )
    if series is not None:
        return series.rename("Eurozone Inflation YoY (%)")

    dates  = _date_range_monthly(start)
    values = []
    for d in dates:
        if d < pd.Timestamp("2021-06"):
            values.append(round(np.random.uniform(0.2, 1.5), 1))
        elif d < pd.Timestamp("2022-03"):
            values.append(round(np.random.uniform(1.5, 5.0), 1))
        elif d < pd.Timestamp("2023-03"):
            values.append(round(np.random.uniform(7.0, 10.6), 1))
        elif d < pd.Timestamp("2024-01"):
            values.append(round(np.random.uniform(2.5, 7.0), 1))
        else:
            values.append(round(np.random.uniform(2.0, 3.2), 1))
    return pd.Series(values, index=dates, name="Eurozone Inflation YoY (%)")


def get_all_ecb_series(start: str = "2019-01") -> pd.DataFrame:
    """Returns all ECB series as a single aligned DataFrame."""
    dfr      = get_ecb_deposit_rate(start)
    euribor  = get_euribor_3m(start)
    cpi      = get_euro_inflation(start)
    df = pd.concat([dfr, euribor, cpi], axis=1).sort_index()
    df.index.name = "Date"
    return df
