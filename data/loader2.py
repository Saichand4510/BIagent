import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
MONDAY_URL = "https://api.monday.com/v2"


# ============================================================
# 🔥 CORE: generic monday fetch
# ============================================================

def _fetch_board_items(board_id: str) -> pd.DataFrame:
    """Fetch board data live from monday.com"""

    query = f"""
    query {{
      boards(ids: {board_id}) {{
        items_page(limit: 500) {{
          items {{
            name
            column_values {{
              id
              text
            }}
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(
        MONDAY_URL,
        json={"query": query},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    items = data["data"]["boards"][0]["items_page"]["items"]

    records = []

    for item in items:
        row = {"Deal Name": item["name"]}

        for col in item["column_values"]:
            row[col["id"]] = col["text"]

        records.append(row)

    return pd.DataFrame(records)


# ============================================================
# 🔥 DEAL DATA (LIVE)
# ============================================================

def load_deal_data() -> pd.DataFrame:
    """
    LIVE fetch from monday.
    Called inside tools → satisfies assignment requirement.
    """

    df = _fetch_board_items(DEALS_BOARD_ID)
   # print(df.columns)
    # --------------------------------------------------------
    # 🚨 IMPORTANT: map monday column IDs → business names
    # You MUST update these after printing df.columns once
    # --------------------------------------------------------
    COLUMN_MAP = {
    "text_mm12ztpe": "Owner code",
    "text_mm12s1hk": "Client Code",
    "color_mm12p6m": "Deal Status",
    "date_mm12w3yc": "Close Date (A)",
    "color_mm123rhv": "Closure Probability",
    "numeric_mm12757v": "Masked Deal value",
    "date_mm12sx7p": "Tentative Close Date",
    "color_mm12t6vq": "Deal Stage",
    "text_mm12fm8b": "Product deal",
    "color_mm1240a9": "Sector/service",
    "date_mm126em7": "Created Date",
}

    df = df.rename(columns=COLUMN_MAP)

    # --------------------------------------------------------
    # ✅ Cleaning (your existing logic — good!)
    # --------------------------------------------------------

    df.columns = df.columns.str.strip()

    if "Masked Deal value" in df.columns:
        df["Masked Deal value"] = pd.to_numeric(
            df["Masked Deal value"], errors="coerce"
        ).fillna(0)

    if "Tentative Close Date" in df.columns:
        df["Tentative Close Date"] = pd.to_datetime(
            df["Tentative Close Date"], errors="coerce"
        )

    if "Deal Status" in df.columns:
        df["Deal Status"] = (
            df["Deal Status"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    if "Closure Probability" in df.columns:
        df["Closure Probability"] = (
            df["Closure Probability"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    df = df.dropna(how="all")

    return df


# ============================================================
# 🔥 WORK ORDER DATA (LIVE)
# ============================================================

def load_work_order_data() -> pd.DataFrame:
    df = _fetch_board_items(WORK_ORDERS_BOARD_ID)

    WORK_ORDER_MAP = {
        "text_mm128tj": "Customer Name Code",
        "text_mm1210tn": "Serial #",
        "dropdown_mm1236q5": "Nature of Work",
        "color_mm12r15z": "Execution Status",
        "date_mm127cez": "Data Delivery Date",
        "color_mm122ev": "WO Status (billed)",
        "color_mm12nq0e": "Billing Status",
        "color_mm12kw6q": "Collection status",
        "numeric_mm12x6qc": "Quantity billed (till date)",
        "numeric_mm1213kr": "Balance in quantity",
    }

    df = df.rename(columns=WORK_ORDER_MAP)
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")

    # normalize status
    if "Execution Status" in df.columns:
        df["Execution Status"] = (
            df["Execution Status"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    return df 
load_work_order_data()