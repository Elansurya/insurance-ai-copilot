"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Page: Policies
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
POLICIES_PATH: Path = DATA_DIR / "policies.csv"

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
.status-active {
    background-color: #dcfce7;
    color: #166534;
}
.status-expired {
    background-color: #fee2e2;
    color: #991b1b;
}
</style>
"""


# --------------------------------------------------------------------------
# Demo Data Fallback
# --------------------------------------------------------------------------

def _build_demo_policies() -> pd.DataFrame:
    """Build an in-memory demo policies dataset."""
    today = date.today()
    start_dates = [
        today - timedelta(days=d)
        for d in [400, 300, 200, 100, 20, 340, 15, 250, 5, 60]
    ]
    renewal_dates = [start + timedelta(days=365) for start in start_dates]
    statuses = [
        "Expired" if renewal < today else "Active" for renewal in renewal_dates
    ]

    return pd.DataFrame(
        {
            "PolicyID": [f"POL{i:04d}" for i in range(1, 11)],
            "CustomerID": [f"CUST{i:04d}" for i in range(1, 11)],
            "PolicyNumber": [f"INS-{100000 + i}-A" for i in range(1, 11)],
            "PolicyType": [
                "Comprehensive", "Third-Party", "Zero Depreciation",
                "Comprehensive", "Own Damage", "Third-Party + Own Damage",
                "Comprehensive", "Third-Party", "Zero Depreciation",
                "Comprehensive",
            ],
            "PremiumAmount": [
                23938, 14127, 19231, 10788, 32450,
                12980, 27650, 15990, 41200, 9800,
            ],
            "StartDate": [d.isoformat() for d in start_dates],
            "RenewalDate": [d.isoformat() for d in renewal_dates],
            "PolicyStatus": statuses,
        }
    )


# --------------------------------------------------------------------------
# Data Loading
# --------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_policies() -> pd.DataFrame:
    """
    Load policy data from disk, falling back to demo data
    if the file is missing or empty.
    """
    if not POLICIES_PATH.exists():
        return _build_demo_policies()

    try:
        dataframe = pd.read_csv(POLICIES_PATH)
    except (pd.errors.EmptyDataError, OSError):
        return _build_demo_policies()

    if dataframe.empty:
        return _build_demo_policies()

    if "RenewalDate" in dataframe.columns:
        dataframe["RenewalDate"] = pd.to_datetime(
            dataframe["RenewalDate"], errors="coerce"
        )
    if "StartDate" in dataframe.columns:
        dataframe["StartDate"] = pd.to_datetime(
            dataframe["StartDate"], errors="coerce"
        )

    return dataframe


# --------------------------------------------------------------------------
# Filtering Helpers
# --------------------------------------------------------------------------

def apply_filters(
    policies_df: pd.DataFrame,
    search_term: str,
    selected_statuses: list[str],
    renewal_range: tuple[date, date] | None,
    premium_range: tuple[int, int] | None,
) -> pd.DataFrame:
    """
    Apply search and filter criteria to the policies dataset.

    Args:
        policies_df: Source policies dataset.
        search_term: Free-text search term.
        selected_statuses: List of selected policy statuses to filter by.
        renewal_range: Tuple of (start_date, end_date) for renewal filtering.
        premium_range: Tuple of (min_premium, max_premium) for filtering.

    Returns:
        The filtered policies DataFrame.
    """
    filtered_df = policies_df.copy()

    if search_term:
        search_lower = search_term.strip().lower()
        searchable_columns = [
            col
            for col in ["PolicyID", "PolicyNumber", "CustomerID", "PolicyType"]
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

    if selected_statuses and "PolicyStatus" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["PolicyStatus"].isin(selected_statuses)
        ]

    if renewal_range and "RenewalDate" in filtered_df.columns:
        start_date, end_date = renewal_range
        renewal_dates = pd.to_datetime(filtered_df["RenewalDate"], errors="coerce")
        mask = (
            (renewal_dates.dt.date >= start_date)
            & (renewal_dates.dt.date <= end_date)
        )
        filtered_df = filtered_df[mask]

    if premium_range and "PremiumAmount" in filtered_df.columns:
        min_premium, max_premium = premium_range
        filtered_df = filtered_df[
            (filtered_df["PremiumAmount"] >= min_premium)
            & (filtered_df["PremiumAmount"] <= max_premium)
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
    st.title("📄 Policy Management")
    st.caption("Search, filter, and review insurance policies")
    st.markdown("---")


def render_filters(
    policies_df: pd.DataFrame,
) -> tuple[str, list[str], tuple[date, date] | None, tuple[int, int] | None]:
    """
    Render the search box and filter controls.

    Args:
        policies_df: Source policies dataset used to populate filter options.

    Returns:
        A tuple of (search_term, selected_statuses, renewal_range, premium_range).
    """
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🔍 Search &amp; Filter</div>',
        unsafe_allow_html=True,
    )

    search_term = st.text_input(
        "Search Policy",
        placeholder="Search by Policy ID, Policy Number, Customer ID, or Type...",
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        status_options = (
            sorted(policies_df["PolicyStatus"].dropna().unique().tolist())
            if "PolicyStatus" in policies_df.columns
            else []
        )
        selected_statuses = st.multiselect("Policy Status", options=status_options)

    with filter_col2:
        renewal_range: tuple[date, date] | None = None
        if "RenewalDate" in policies_df.columns:
            renewal_series = pd.to_datetime(
                policies_df["RenewalDate"], errors="coerce"
            ).dropna()
            if not renewal_series.empty:
                min_date = renewal_series.min().date()
                max_date = renewal_series.max().date()
                selected_range = st.date_input(
                    "Renewal Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                )
                if isinstance(selected_range, tuple) and len(selected_range) == 2:
                    renewal_range = selected_range
                elif isinstance(selected_range, date):
                    renewal_range = (selected_range, selected_range)
            else:
                st.date_input("Renewal Date Range", value=(), disabled=True)
        else:
            st.date_input("Renewal Date Range", value=(), disabled=True)

    with filter_col3:
        premium_range: tuple[int, int] | None = None
        if "PremiumAmount" in policies_df.columns and not policies_df.empty:
            min_premium = int(policies_df["PremiumAmount"].min())
            max_premium = int(policies_df["PremiumAmount"].max())
            if min_premium < max_premium:
                premium_range = st.slider(
                    "Premium Amount (₹)",
                    min_value=min_premium,
                    max_value=max_premium,
                    value=(min_premium, max_premium),
                )
            else:
                st.caption(f"Premium Amount (₹): {min_premium:,}")
        else:
            st.caption("Premium Amount (₹): N/A")

    st.markdown("</div>", unsafe_allow_html=True)

    return search_term, selected_statuses, renewal_range, premium_range


def _status_badge_html(status: str) -> str:
    """Return HTML markup for a colored policy status badge."""
    css_class = "status-active" if status == "Active" else "status-expired"
    return f'<span class="status-badge {css_class}">{status}</span>'


def render_policy_table(filtered_df: pd.DataFrame) -> None:
    """Render the policies table with formatted status badges."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-title">📋 Policies ({len(filtered_df)} results)</div>',
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        st.info("No policies match the current search and filter criteria.")
    else:
        display_df = filtered_df.copy()

        if "RenewalDate" in display_df.columns:
            display_df["RenewalDate"] = pd.to_datetime(
                display_df["RenewalDate"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
        if "StartDate" in display_df.columns:
            display_df["StartDate"] = pd.to_datetime(
                display_df["StartDate"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
        if "PremiumAmount" in display_df.columns:
            display_df["PremiumAmount"] = display_df["PremiumAmount"].apply(
                lambda amount: f"₹{amount:,.0f}"
            )

        st.dataframe(
            display_df.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_summary_metrics(filtered_df: pd.DataFrame) -> None:
    """Render summary KPI metrics for the filtered policies."""
    total_policies = len(filtered_df)
    total_premium = (
        int(filtered_df["PremiumAmount"].sum())
        if "PremiumAmount" in filtered_df.columns and not filtered_df.empty
        else 0
    )
    active_count = (
        int((filtered_df["PolicyStatus"] == "Active").sum())
        if "PolicyStatus" in filtered_df.columns
        else 0
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Total Policies", f"{total_policies:,}")
    with metric_col2:
        st.metric("Active Policies", f"{active_count:,}")
    with metric_col3:
        st.metric("Total Premium (₹)", f"{total_premium:,}")


# --------------------------------------------------------------------------
# Page Entry Point
# --------------------------------------------------------------------------

def render_policies_page() -> None:
    """Render the full Policy Management page."""
    inject_styles()
    render_header()

    policies_df = load_policies()

    search_term, selected_statuses, renewal_range, premium_range = render_filters(
        policies_df
    )

    filtered_df = apply_filters(
        policies_df, search_term, selected_statuses, renewal_range, premium_range
    )

    render_summary_metrics(filtered_df)
    render_policy_table(filtered_df)


render_policies_page()