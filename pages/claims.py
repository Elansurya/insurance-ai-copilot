"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Page: Claims
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

DATA_DIR: Path = Path("data")
CLAIMS_PATH: Path = DATA_DIR / "claims.csv"
CUSTOMERS_PATH: Path = DATA_DIR / "customers.csv"

CLAIM_STATUSES: list[str] = ["Approved", "Pending", "Rejected"]

CARD_STYLE: str = """
<style>
.glass-card {
    background: rgba(17, 24, 39, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.10);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.75rem;
}
.status-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
}
.status-approved {
    background-color: #dcfce7;
    color: #166534;
}
.status-pending {
    background-color: #fef9c3;
    color: #854d0e;
}
.status-rejected {
    background-color: #fee2e2;
    color: #991b1b;
}
</style>
"""


# --------------------------------------------------------------------------
# Demo Data Fallback
# --------------------------------------------------------------------------

def _build_demo_claims() -> pd.DataFrame:
    """Build an in-memory demo claims dataset."""
    today = date.today()
    claim_dates = [
        today - timedelta(days=d)
        for d in [45, 30, 90, 10, 5, 60, 120, 15]
    ]

    return pd.DataFrame(
        {
            "ClaimID": [f"CLM{i:04d}" for i in range(1, 9)],
            "CustomerID": [f"CUST{i:04d}" for i in range(1, 9)],
            "PolicyID": [f"POL{i:04d}" for i in range(1, 9)],
            "ClaimDate": [d.isoformat() for d in claim_dates],
            "ClaimAmount": [
                14984, 193796, 116682, 131497, 22500,
                8700, 45200, 12300,
            ],
            "ClaimStatus": [
                "Approved", "Approved", "Rejected", "Pending",
                "Pending", "Approved", "Rejected", "Pending",
            ],
            "ClaimReason": [
                "Natural Calamity (Flood)", "Vandalism", "Windshield Damage",
                "Third-Party Liability", "Collision", "Theft",
                "Engine Damage", "Accidental Damage",
            ],
        }
    )


def _build_demo_customers() -> pd.DataFrame:
    """Build a minimal in-memory demo customers dataset for name lookups."""
    names = [
        "Amit Chopra", "Priya Sharma", "Rahul Verma", "Sneha Iyer",
        "Vikram Singh", "Anita Rao", "Karan Mehta", "Divya Nair",
    ]
    return pd.DataFrame(
        {
            "CustomerID": [f"CUST{i:04d}" for i in range(1, len(names) + 1)],
            "CustomerName": names,
        }
    )


# --------------------------------------------------------------------------
# Data Loading
# --------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_claims() -> pd.DataFrame:
    """
    Load claims data from disk, falling back to demo data
    if the file is missing or empty.
    """
    if not CLAIMS_PATH.exists():
        return _build_demo_claims()

    try:
        dataframe = pd.read_csv(CLAIMS_PATH)
    except (pd.errors.EmptyDataError, OSError):
        return _build_demo_claims()

    if dataframe.empty:
        return _build_demo_claims()

    if "ClaimDate" in dataframe.columns:
        dataframe["ClaimDate"] = pd.to_datetime(
            dataframe["ClaimDate"], errors="coerce"
        )

    return dataframe


@st.cache_data(show_spinner=False)
def load_customers() -> pd.DataFrame:
    """
    Load customer data from disk for name lookups, falling back to
    demo data if the file is missing, empty, or unreadable.
    """
    if not CUSTOMERS_PATH.exists():
        return _build_demo_customers()

    try:
        dataframe = pd.read_csv(CUSTOMERS_PATH)
    except (pd.errors.EmptyDataError, OSError):
        return _build_demo_customers()

    if dataframe.empty or "CustomerName" not in dataframe.columns:
        return _build_demo_customers()

    return dataframe


def merge_customer_names(
    claims_df: pd.DataFrame, customers_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich the claims dataset with the corresponding customer name.

    Args:
        claims_df: Source claims dataset.
        customers_df: Source customers dataset containing CustomerName.

    Returns:
        The claims DataFrame with a CustomerName column merged in.
    """
    if "CustomerID" not in claims_df.columns or "CustomerID" not in customers_df.columns:
        merged_df = claims_df.copy()
        merged_df["CustomerName"] = "Unknown"
        return merged_df

    name_lookup = customers_df[["CustomerID", "CustomerName"]].drop_duplicates(
        subset="CustomerID"
    )
    merged_df = claims_df.merge(name_lookup, on="CustomerID", how="left")
    merged_df["CustomerName"] = merged_df["CustomerName"].fillna("Unknown")
    return merged_df


# --------------------------------------------------------------------------
# Filtering Helpers
# --------------------------------------------------------------------------

def apply_filters(
    claims_df: pd.DataFrame,
    search_term: str,
    selected_statuses: list[str],
    claim_amount_range: tuple[int, int] | None,
    selected_customer_names: list[str],
) -> pd.DataFrame:
    """
    Apply search and filter criteria to the claims dataset.

    Args:
        claims_df: Source claims dataset (enriched with CustomerName).
        search_term: Free-text search term.
        selected_statuses: List of selected claim statuses to filter by.
        claim_amount_range: Tuple of (min_amount, max_amount) for filtering.
        selected_customer_names: List of selected customer names to filter by.

    Returns:
        The filtered claims DataFrame.
    """
    filtered_df = claims_df.copy()

    if search_term:
        search_lower = search_term.strip().lower()
        searchable_columns = [
            col
            for col in [
                "ClaimID", "CustomerID", "PolicyID",
                "ClaimReason", "CustomerName",
            ]
            if col in filtered_df.columns
        ]
        if searchable_columns:
            mask = pd.Series(False, index=filtered_df.index)
            for col in searchable_columns:
                mask |= (
                    filtered_df[col]
                    .astype(str)
                    .str.lower()
                    .str.contains(search_lower, na=False)
                )
            filtered_df = filtered_df[mask]

    if selected_statuses and "ClaimStatus" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["ClaimStatus"].isin(selected_statuses)
        ]

    if claim_amount_range and "ClaimAmount" in filtered_df.columns:
        min_amount, max_amount = claim_amount_range
        filtered_df = filtered_df[
            (filtered_df["ClaimAmount"] >= min_amount)
            & (filtered_df["ClaimAmount"] <= max_amount)
        ]

    if selected_customer_names and "CustomerName" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["CustomerName"].isin(selected_customer_names)
        ]

    return filtered_df


# --------------------------------------------------------------------------
# UI Rendering Helpers
# --------------------------------------------------------------------------

def inject_styles() -> None:
    """Inject glass-card CSS styling into the page."""
    st.markdown(CARD_STYLE, unsafe_allow_html=True)


def render_header() -> None:
    """Render the page header and subtitle."""
    st.title("🧾 Claims Management")
    st.caption("Search, filter, and review insurance claims")
    st.markdown("---")


def render_filters(
    claims_df: pd.DataFrame,
) -> tuple[str, list[str], tuple[int, int] | None, list[str]]:
    """
    Render the search box and filter controls.

    Args:
        claims_df: Source claims dataset (enriched with CustomerName),
            used to populate filter options.

    Returns:
        A tuple of (search_term, selected_statuses, claim_amount_range,
        selected_customer_names).
    """
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🔍 Search &amp; Filter</div>',
        unsafe_allow_html=True,
    )

    search_term = st.text_input(
        "Search Claim",
        placeholder="Search by Claim ID, Customer ID, Policy ID, or Reason...",
    )

    status_col1, status_col2, status_col3 = st.columns(3)
    selected_statuses: list[str] = []

    with status_col1:
        if st.checkbox("Approved", value=False):
            selected_statuses.append("Approved")
    with status_col2:
        if st.checkbox("Pending", value=False):
            selected_statuses.append("Pending")
    with status_col3:
        if st.checkbox("Rejected", value=False):
            selected_statuses.append("Rejected")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        claim_amount_range: tuple[int, int] | None = None
        if "ClaimAmount" in claims_df.columns and not claims_df.empty:
            min_amount = int(claims_df["ClaimAmount"].min())
            max_amount = int(claims_df["ClaimAmount"].max())
            if min_amount < max_amount:
                claim_amount_range = st.slider(
                    "Claim Amount (₹)",
                    min_value=min_amount,
                    max_value=max_amount,
                    value=(min_amount, max_amount),
                )
            else:
                st.caption(f"Claim Amount (₹): {min_amount:,}")
        else:
            st.caption("Claim Amount (₹): N/A")

    with filter_col2:
        customer_name_options = (
            sorted(claims_df["CustomerName"].dropna().unique().tolist())
            if "CustomerName" in claims_df.columns
            else []
        )
        selected_customer_names = st.multiselect(
            "Customer Name", options=customer_name_options
        )

    st.markdown("</div>", unsafe_allow_html=True)

    return search_term, selected_statuses, claim_amount_range, selected_customer_names


def _status_badge_html(status: str) -> str:
    """Return HTML markup for a colored claim status badge."""
    status_class_map = {
        "Approved": "status-approved",
        "Pending": "status-pending",
        "Rejected": "status-rejected",
    }
    css_class = status_class_map.get(status, "status-pending")
    return f'<span class="status-badge {css_class}">{status}</span>'


def render_summary_metrics(filtered_df: pd.DataFrame) -> None:
    """Render summary KPI metrics for the filtered claims."""
    total_claims = len(filtered_df)
    approved_count = (
        int((filtered_df["ClaimStatus"] == "Approved").sum())
        if "ClaimStatus" in filtered_df.columns
        else 0
    )
    pending_count = (
        int((filtered_df["ClaimStatus"] == "Pending").sum())
        if "ClaimStatus" in filtered_df.columns
        else 0
    )
    rejected_count = (
        int((filtered_df["ClaimStatus"] == "Rejected").sum())
        if "ClaimStatus" in filtered_df.columns
        else 0
    )
    total_amount = (
        int(filtered_df["ClaimAmount"].sum())
        if "ClaimAmount" in filtered_df.columns and not filtered_df.empty
        else 0
    )

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    with metric_col1:
        st.metric("Total Claims", f"{total_claims:,}")
    with metric_col2:
        st.metric("Approved", f"{approved_count:,}")
    with metric_col3:
        st.metric("Pending", f"{pending_count:,}")
    with metric_col4:
        st.metric("Rejected", f"{rejected_count:,}")
    with metric_col5:
        st.metric("Total Claim Amount (₹)", f"{total_amount:,}")


def render_claims_table(filtered_df: pd.DataFrame) -> None:
    """Render the claims table with formatted columns and status badges."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-title">📋 Claims ({len(filtered_df)} results)</div>',
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        st.info("No claims match the current search and filter criteria.")
    else:
        display_df = filtered_df.copy()

        if "ClaimDate" in display_df.columns:
            display_df["ClaimDate"] = pd.to_datetime(
                display_df["ClaimDate"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

        if "ClaimAmount" in display_df.columns:
            display_df["ClaimAmount"] = display_df["ClaimAmount"].apply(
                lambda amount: f"₹{amount:,.0f}"
            )

        preferred_order = [
            "ClaimID", "CustomerID", "CustomerName", "PolicyID",
            "ClaimDate", "ClaimAmount", "ClaimStatus", "ClaimReason",
        ]
        ordered_columns = [
            col for col in preferred_order if col in display_df.columns
        ]
        remaining_columns = [
            col for col in display_df.columns if col not in ordered_columns
        ]
        display_df = display_df[ordered_columns + remaining_columns]

        st.dataframe(
            display_df.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Page Entry Point
# --------------------------------------------------------------------------

def render_claims_page() -> None:
    """Render the full Claims Management page."""
    inject_styles()
    render_header()

    claims_df = load_claims()
    customers_df = load_customers()
    enriched_claims_df = merge_customer_names(claims_df, customers_df)

    search_term, selected_statuses, claim_amount_range, selected_customer_names = (
        render_filters(enriched_claims_df)
    )

    filtered_df = apply_filters(
        enriched_claims_df,
        search_term,
        selected_statuses,
        claim_amount_range,
        selected_customer_names,
    )

    render_summary_metrics(filtered_df)
    render_claims_table(filtered_df)


render_claims_page()