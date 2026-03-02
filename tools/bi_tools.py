import json
from pathlib import Path

from langchain_core.tools import tool
from data.loader2 import load_deal_data, load_work_order_data





@tool
def get_pipeline_summary():
    """Return high-level sales pipeline metrics."""
    df = load_deal_data()

    total_value = df["Masked Deal value"].sum()
    open_deals = df[df["Deal Status"] == "open"].shape[0]

    return {
        "total_pipeline_value": float(total_value),
        "open_deals": int(open_deals),
    }

@tool
def get_at_risk_deals():
    """Return deals with low closure probability."""
    df = load_deal_data()

    risk = df[
        df["Closure Probability"]
        .astype(str)
        .str.lower()
        .isin(["low", "medium"])
    ]

    top_risk = risk.sort_values(
        "Masked Deal value",
        ascending=False
    ).head(10)

    return top_risk[
        ["Deal Name", "Masked Deal value", "Closure Probability"]
    ].to_dict(orient="records")
@tool
def get_weighted_forecast():
    """Return probability-weighted revenue forecast."""
    df = load_deal_data()

    prob_map = {
        "high": 0.9,
        "medium": 0.5,
        "low": 0.2
    }

    df["prob_score"] = (
        df["Closure Probability"]
        .astype(str)
        .str.lower()
        .map(prob_map)
        .fillna(0.3)
    )

    weighted = (df["Masked Deal value"] * df["prob_score"]).sum()

    return {
        "weighted_forecast": float(weighted)
    }


@tool
def get_operational_risks():
    """Identify work orders not started or delayed."""
    df = load_work_order_data()

    # adjust column names if needed after you inspect
    status_cols = [c for c in df.columns if "status" in c.lower()]

    if not status_cols:
        return {"message": "No status column found"}

    status_col = status_cols[0]

    risk = df[
        df[status_col]
        .astype(str)
        .str.lower()
        .isin(["not started", "delayed", "pending"])
    ]

    return {
        "at_risk_work_orders": int(risk.shape[0])
    }

