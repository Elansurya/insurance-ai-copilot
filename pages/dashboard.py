"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Page: Dashboard
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

DATA_DIR: Path = Path("data")
CUSTOMERS_PATH: Path = DATA_DIR / "customers.csv"
POLICIES_PATH: Path = DATA_DIR / "policies.csv"
CLAIMS_PATH: Path = DATA_DIR / "claims.csv"

EXPIRY_WINDOW_DAYS: int = 30
RECENT_RENEWALS_LIMIT: int = 8
PENDING_CLAIMS_LIMIT: int = 8

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
.kpi-label {
    font-size: 0.85rem;
    color: #ffffff;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.25rem;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.75rem;
}
</style>
"""


# --------------------------------------------------------------------------
# Demo Data Generation
# --------------------------------------------------------------------------

def _build_demo_customers() -> pd.DataFrame:
    """Build an in-memory demo customers dataset."""
    return pd.DataFrame(
        {
            "CustomerID": [f"CUST{i:04d}" for i in range(1, 11)],
            "CustomerName": [
                "Amit Chopra", "Priya Sharma", "Rahul Verma", "Sneha Iyer",
                "Vikram Singh", "Anita Rao", "Karan Mehta", "Divya Nair",
                "Suresh Kumar", "Neha Gupta",
            ],
            "Gender": [
                "Male", "Female", "Male", "Female", "Male",
                "Female", "Male", "Female", "Male", "Female",
            ],
            "Age": [36, 29, 44, 31, 52, 38, 27, 41, 58, 33],
            "City": [
                "Mumbai", "Delhi", "Bengaluru", "Chennai", "Pune",
                "Hyderabad", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
            ],
            "VehicleBrand": [
                "Maruti Suzuki", "Hyundai", "Tata", "Kia", "Mahindra",
                "Toyota", "Honda", "Hyundai", "Maruti Suzuki", "Tata",
            ],
            "VehicleModel": [
                "Swift", "Creta", "Nexon", "Seltos", "Scorpio",
                "Fortuner", "City", "i20", "Baleno", "Punch",
            ],
        }
    )


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


def _build_demo_claims() -> pd.DataFrame:
    """Build an in-memory demo claims dataset."""
    today = date.today()
    claim_dates = [
        today - timedelta(days=d) for d in [45, 30, 90, 10, 5, 60, 120, 15]
    ]

    return pd.DataFrame(
        {
            "ClaimID": [f"CLM{i:04d}" for i in range(1, 9)],
            "CustomerID": [f"CUST{i:04d}" for i in [1, 2, 3, 4, 5, 6, 7, 8]],
            "PolicyID": [f"POL{i:04d}" for i in [1, 2, 3, 4, 5, 6, 7, 8]],
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


# --------------------------------------------------------------------------
# Data Loading
# --------------------------------------------------------------------------

def _load_csv_or_none(path: Path) -> pd.DataFrame | None:
    """
    Load a CSV file if it exists and is non-empty.

    Args:
        path: Path to the CSV file.

    Returns:
        A DataFrame if the file exists and contains data, otherwise None.
    """
    if not path.exists():
        return None

    try:
        dataframe = pd.read_csv(path)
    except (pd.errors.EmptyDataError, OSError):
        return None

    if dataframe.empty:
        return None

    return dataframe


@st.cache_data(show_spinner=False)
def load_customers() -> pd.DataFrame:
    """Load customer data from disk, falling back to demo data."""
    dataframe = _load_csv_or_none(CUSTOMERS_PATH)
    return dataframe if dataframe is not None else _build_demo_customers()


@st.cache_data(show_spinner=False)
def load_policies() -> pd.DataFrame:
    """Load policy data from disk, falling back to demo data."""
    dataframe = _load_csv_or_none(POLICIES_PATH)
    return dataframe if dataframe is not None else _build_demo_policies()


@st.cache_data(show_spinner=False)
def load_claims() -> pd.DataFrame:
    """Load claims data from disk, falling back to demo data."""
    dataframe = _load_csv_or_none(CLAIMS_PATH)
    return dataframe if dataframe is not None else _build_demo_claims()


# --------------------------------------------------------------------------
# Data Preparation Helpers
# --------------------------------------------------------------------------

def _to_datetime_safe(series: pd.Series) -> pd.Series:
    """Convert a series to datetime, coercing invalid values to NaT."""
    return pd.to_datetime(series, errors="coerce")


def compute_kpis(
    customers_df: pd.DataFrame,
    policies_df: pd.DataFrame,
    claims_df: pd.DataFrame,
) -> dict[str, int]:
    """
    Compute headline KPI values for the dashboard.

    Args:
        customers_df: Customer dataset.
        policies_df: Policy dataset.
        claims_df: Claims dataset.

    Returns:
        A dictionary of KPI labels to computed integer values.
    """
    total_customers = len(customers_df)

    active_policies = 0
    expiring_soon = 0

    if "PolicyStatus" in policies_df.columns:
        active_policies = int((policies_df["PolicyStatus"] == "Active").sum())

    if "RenewalDate" in policies_df.columns:
        renewal_dates = _to_datetime_safe(policies_df["RenewalDate"])
        today_ts = pd.Timestamp(datetime.now().date())
        window_end = today_ts + pd.Timedelta(days=EXPIRY_WINDOW_DAYS)
        expiring_mask = (
            (renewal_dates >= today_ts) & (renewal_dates <= window_end)
        )
        expiring_soon = int(expiring_mask.sum())

    pending_claims = 0
    if "ClaimStatus" in claims_df.columns:
        pending_claims = int((claims_df["ClaimStatus"] == "Pending").sum())

    return {
        "Total Customers": total_customers,
        "Active Policies": active_policies,
        "Policies Expiring Soon": expiring_soon,
        "Pending Claims": pending_claims,
    }


def get_recent_renewals(policies_df: pd.DataFrame, limit: int) -> pd.DataFrame:
    """Return the most recently upcoming policy renewals."""
    if "RenewalDate" not in policies_df.columns:
        return policies_df.head(limit)

    working_df = policies_df.copy()
    working_df["_RenewalDateParsed"] = _to_datetime_safe(
        working_df["RenewalDate"]
    )
    working_df = working_df.sort_values(
        by="_RenewalDateParsed", ascending=True, na_position="last"
    )
    working_df = working_df.drop(columns=["_RenewalDateParsed"])
    return working_df.head(limit)


def get_pending_claims(claims_df: pd.DataFrame, limit: int) -> pd.DataFrame:
    """Return the most recent pending claims."""
    if "ClaimStatus" not in claims_df.columns:
        return claims_df.head(limit)

    pending_df = claims_df[claims_df["ClaimStatus"] == "Pending"].copy()

    if "ClaimDate" in pending_df.columns:
        pending_df["_ClaimDateParsed"] = _to_datetime_safe(
            pending_df["ClaimDate"]
        )
        pending_df = pending_df.sort_values(
            by="_ClaimDateParsed", ascending=False, na_position="last"
        )
        pending_df = pending_df.drop(columns=["_ClaimDateParsed"])

    return pending_df.head(limit)


# --------------------------------------------------------------------------
# UI Rendering Helpers
# --------------------------------------------------------------------------

def inject_styles() -> None:
    """Inject glass-card CSS styling into the page."""
    st.markdown(CARD_STYLE, unsafe_allow_html=True)


def render_header() -> None:
    """Render the dashboard header and subtitle."""
    st.title("🚗 Insurance AI Copilot")
    st.caption("Enterprise Insurance CRM Dashboard")
    st.markdown("---")


def render_kpi_cards(kpis: dict[str, int]) -> None:
    """Render the KPI summary cards in a responsive grid."""
    columns = st.columns(len(kpis))

    for column, (label, value) in zip(columns, kpis.items()):
        with column:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_recent_renewals(policies_df: pd.DataFrame) -> None:
    """Render the recent policy renewals panel."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">📅 Recent Policy Renewals</div>',
        unsafe_allow_html=True,
    )

    renewals_df = get_recent_renewals(policies_df, RECENT_RENEWALS_LIMIT)

    if renewals_df.empty:
        st.info("No policy renewal data available.")
    else:
        display_columns = [
            col
            for col in [
                "PolicyID", "CustomerID", "PolicyType",
                "RenewalDate", "PolicyStatus",
            ]
            if col in renewals_df.columns
        ]
        st.dataframe(
            renewals_df[display_columns] if display_columns else renewals_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_pending_claims_panel(claims_df: pd.DataFrame) -> None:
    """Render the pending claims panel."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🧾 Pending Claims</div>',
        unsafe_allow_html=True,
    )

    pending_df = get_pending_claims(claims_df, PENDING_CLAIMS_LIMIT)

    if pending_df.empty:
        st.info("No pending claims at this time.")
    else:
        display_columns = [
            col
            for col in [
                "ClaimID", "CustomerID", "ClaimDate",
                "ClaimAmount", "ClaimReason",
            ]
            if col in pending_df.columns
        ]
        st.dataframe(
            pending_df[display_columns] if display_columns else pending_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_customer_overview_table(customers_df: pd.DataFrame) -> None:
    """Render the customer overview table."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">👥 Customer Overview</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(customers_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_policy_status_pie_chart(policies_df: pd.DataFrame) -> None:
    """Render a pie chart summarizing policy status distribution."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">📊 Policy Status Distribution</div>',
        unsafe_allow_html=True,
    )

    if "PolicyStatus" not in policies_df.columns or policies_df.empty:
        st.info("No policy status data available.")
    else:
        status_counts = (
            policies_df["PolicyStatus"]
            .value_counts()
            .rename_axis("PolicyStatus")
            .reset_index(name="Count")
        )
        fig = px.pie(
            status_counts,
            names="PolicyStatus",
            values="Count",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_claim_status_bar_chart(claims_df: pd.DataFrame) -> None:
    """Render a bar chart summarizing claim status counts."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">📈 Claim Status Overview</div>',
        unsafe_allow_html=True,
    )

    if "ClaimStatus" not in claims_df.columns or claims_df.empty:
        st.info("No claim status data available.")
    else:
        status_counts = (
            claims_df["ClaimStatus"]
            .value_counts()
            .rename_axis("ClaimStatus")
            .reset_index(name="Count")
        )
        fig = px.bar(
            status_counts,
            x="ClaimStatus",
            y="Count",
            color="ClaimStatus",
            color_discrete_sequence=px.colors.qualitative.Set2,
            text="Count",
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis_title="",
            yaxis_title="Number of Claims",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Page Entry Point
# --------------------------------------------------------------------------

def render_dashboard_page() -> None:
    """Render the full Insurance CRM dashboard page."""
    inject_styles()
    render_header()

    customers_df = load_customers()
    policies_df = load_policies()
    claims_df = load_claims()

    kpis = compute_kpis(customers_df, policies_df, claims_df)
    render_kpi_cards(kpis)

    left_column, right_column = st.columns(2)
    with left_column:
        render_recent_renewals(policies_df)
    with right_column:
        render_pending_claims_panel(claims_df)

    chart_left, chart_right = st.columns(2)
    with chart_left:
        render_policy_status_pie_chart(policies_df)
    with chart_right:
        render_claim_status_bar_chart(claims_df)

    render_customer_overview_table(customers_df)


render_dashboard_page()