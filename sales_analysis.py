import json
import numpy as np
import pandas as pd

RAW_CSV = "raw_sales.csv"
CLEAN_CSV = "cleaned_sales.csv"
TEMPLATE = "dashboard_template.html"
DASHBOARD = "sales_dashboard.html"

PRODUCTS = [  # name, category, price, cost ratio, popularity weight
    ("Laptop", "Electronics", 52000, .78, 3), ("Smartphone", "Electronics", 24000, .80, 5),
    ("Headphones", "Electronics", 3500, .55, 6), ("Smartwatch", "Electronics", 8000, .65, 3),
    ("Office Chair", "Furniture", 7500, .62, 3), ("Study Desk", "Furniture", 9500, .60, 1.5),
    ("Bookshelf", "Furniture", 6000, .58, 1.2), ("Sofa Set", "Furniture", 32000, .70, .8),
    ("Notebook Pack", "Office Supplies", 250, .45, 12), ("Pen Set", "Office Supplies", 180, .40, 12),
    ("Printer", "Office Supplies", 9000, .75, 1.5), ("File Organizer", "Office Supplies", 450, .50, 5),
    ("T-Shirt", "Clothing", 700, .50, 10), ("Jeans", "Clothing", 1800, .55, 8),
    ("Jacket", "Clothing", 3500, .60, 4), ("Sneakers", "Clothing", 3000, .62, 6),
    ("Mixer Grinder", "Home & Kitchen", 4200, .65, 4), ("Air Fryer", "Home & Kitchen", 6500, .68, 3),
    ("Cookware Set", "Home & Kitchen", 3800, .55, 4), ("Water Bottle", "Home & Kitchen", 500, .40, 9),
]
REGIONS = ["North", "South", "East", "West"]


def generate_raw_data(n=6000, seed=42):
    rng = np.random.default_rng(seed)
    days = pd.date_range("2022-01-01", "2024-12-31")
    trend = 1 + 0.35 * (np.arange(len(days)) / len(days))          # business grows over 3 years
    season = np.where(days.month >= 10, 1.25, np.where(days.month <= 2, 0.9, 1.0))
    w = trend * season
    dates = rng.choice(days, size=n, p=w / w.sum())
    pw = np.array([p[4] for p in PRODUCTS], float)
    idx = rng.choice(len(PRODUCTS), size=n, p=pw / pw.sum())
    rows = []
    for i in range(n):
        name, cat, price, cost, _ = PRODUCTS[idx[i]]
        qty = int(rng.integers(1, 4) if price > 5000 else rng.integers(1, 8))
        unit = round(price * rng.uniform(0.97, 1.03), 2)
        disc = float(rng.choice([0, .05, .10, .15, .20], p=[.4, .25, .2, .1, .05]))
        revenue = round(qty * unit * (1 - disc), 2)
        profit = round(revenue - qty * price * cost, 2)
        rows.append([f"ORD-{100000+i}", dates[i], rng.choice(REGIONS, p=[.30, .28, .17, .25]),
                     cat, name, qty, unit, disc, revenue, profit])
    df = pd.DataFrame(rows, columns=["order_id", "order_date", "region", "category", "product",
                                     "quantity", "unit_price", "discount", "revenue", "profit"])
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m-%d")
    # Make the data "dirty": ~2% nulls in several columns, then ~150 duplicate rows
    for col in ["region", "quantity", "unit_price", "order_date", "product"]:
        df.loc[rng.choice(n, size=int(n * .02), replace=False), col] = np.nan
    df = pd.concat([df, df.sample(150, random_state=seed)], ignore_index=True)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def clean(df):
    report = {"raw_rows": len(df), "null_cells": int(df.isna().sum().sum())}
    df = df.drop_duplicates()
    report["duplicates_removed"] = report["raw_rows"] - len(df)
    before = len(df)
    df = df.dropna()
    report["rows_with_nulls_removed"] = before - len(df)
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["quantity"] = df["quantity"].astype(int)
    df["year"], df["month"] = df["order_date"].dt.year, df["order_date"].dt.month
    df["quarter"] = df["order_date"].dt.quarter
    report["clean_rows"] = len(df)
    return df, report


def analyze(df):
    out = {}
    out["yearly"] = df.groupby("year")[["revenue", "profit"]].sum().round(0)
    out["quarterly"] = df.groupby(["year", "quarter"])[["revenue", "profit"]].sum().round(0)
    out["monthly"] = df.groupby(["year", "month"])[["revenue", "profit"]].sum().round(0)
    prod = df.groupby(["product", "category"])[["revenue", "profit", "quantity"]].sum().round(0)
    prod = prod.sort_values("revenue", ascending=False)
    out["top5"], out["bottom5"] = prod.head(5), prod.tail(5)
    out["region"] = df.groupby("region")[["revenue", "profit"]].sum().round(0).sort_values("revenue", ascending=False)
    out["category"] = df.groupby("category")[["revenue", "profit"]].sum().round(0).sort_values("revenue", ascending=False)
    y = out["yearly"]["revenue"]
    out["growth"] = (y.pct_change() * 100).round(1)
    out["kpi"] = {"revenue": df.revenue.sum(), "profit": df.profit.sum(),
                  "margin_pct": df.profit.sum() / df.revenue.sum() * 100, "units": int(df.quantity.sum())}
    return out


def build_dashboard(df):
    agg = (df.groupby(["year", "month", "region", "category", "product"])
             .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"))
             .round(2).reset_index())
    data = {
        "rows": [[int(r.year), int(r.month), r.region, r.category, r.product,
                  r.revenue, r.profit, int(r.units)] for r in agg.itertuples()],
        "years": sorted(int(v) for v in df.year.unique()),
        "regions": sorted(df.region.unique().tolist()),
        "categories": sorted(df.category.unique().tolist()),
        "note": "Sample dataset generated for this project (nulls and duplicates removed). Amounts in INR.",
    }
    html = open(TEMPLATE, encoding="utf-8").read().replace("__DATA__", json.dumps(data, separators=(",", ":")))
    open(DASHBOARD, "w", encoding="utf-8").write(html)


if __name__ == "__main__":
    raw = generate_raw_data()
    raw.to_csv(RAW_CSV, index=False)
    df, rep = clean(pd.read_csv(RAW_CSV))
    df.drop(columns=["quarter"]).assign(order_date=df.order_date.dt.strftime("%Y-%m-%d")).to_csv(CLEAN_CSV, index=False)
    print("CLEANING REPORT", rep)
    res = analyze(df)
    for k in ["yearly", "growth", "quarterly", "top5", "bottom5", "region", "category"]:
        print(f"\n--- {k} ---\n{res[k]}")
    print("\nKPI", {k: round(v, 2) for k, v in res["kpi"].items()})
    build_dashboard(df)
