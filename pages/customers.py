"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Page: Customers
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

DATA_DIR: Path = Path("data")
CUSTOMERS_PATH: Path = DATA_DIR / "customers.csv"

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
.detail-label {
    font-size: 0.8rem;
    color: #ffffff;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-top: 0.75rem;
}
.detail-value {
    font-size: 1.05rem;
    color: #ffffff;
    font-weight: 600;
}
</style>
"""


# --------------------------------------------------------------------------
# Demo Data Fallback
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
            "Phone": [
                "9339670711", "9128492780", "9266944844", "9506448196",
                "9812345670", "9765432109", "9654321098", "9543210987",
                "9432109876", "9321098765",
            ],
            "Email": [
                "amit.chopra@gmail.com", "priya.sharma@gmail.com",
                "rahul.verma@yahoo.com", "sneha.iyer@outlook.com",
                "vikram.singh@gmail.com", "anita.rao@gmail.com",
                "karan.mehta@yahoo.com", "divya.nair@gmail.com",
                "suresh.kumar@gmail.com", "neha.gupta@outlook.com",
            ],
            "Address": [
                "45, Vasant Kunj, Ludhiana", "215, MG Road, Delhi",
                "195, Anna Nagar Main Road, Hyderabad",
                "454, Ashok Nagar, Lucknow", "12, Camp Area, Pune",
                "88, Banjara Hills, Hyderabad", "23, Park Street, Kolkata",
                "67, Rajaji Nagar, Bengaluru", "301, Civil Lines, Jaipur",
                "19, JP Nagar, Bengaluru",
            ],
            "City": [
                "Ludhiana", "Delhi", "Hyderabad", "Lucknow", "Pune",
                "Hyderabad", "Kolkata", "Bengaluru", "Jaipur", "Bengaluru",
            ],
            "VehicleBrand": [
                "Mahindra", "Hyundai", "Maruti Suzuki", "Honda", "Toyota",
                "Kia", "Tata", "Hyundai", "Maruti Suzuki", "Tata",
            ],
            "VehicleModel": [
                "Thar", "Aura", "Brezza", "WR-V", "Fortuner",
                "Seltos", "Nexon", "i20", "Baleno", "Punch",
            ],
            "RegistrationNumber": [
                "PB-03-AB-2535", "UP-38-DE-1106", "TS-55-EF-5333",
                "UP-37-CD-2139", "MH-12-XY-4410", "TS-09-KL-7781",
                "WB-06-MN-3320", "KA-05-GH-9012", "RJ-14-BC-5567",
                "KA-03-AC-8843",
            ],
        }
    )


# --------------------------------------------------------------------------
# Data Loading
# --------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_customers() -> pd.DataFrame:
    """
    Load customer data from disk, falling back to demo data
    if the file is missing or empty.
    """
    if not CUSTOMERS_PATH.exists():
        return _build_demo_customers()

    try:
        dataframe = pd.read_csv(CUSTOMERS_PATH)
    except (pd.errors.EmptyDataError, OSError):
        return _build_demo_customers()

    if dataframe.empty:
        return _build_demo_customers()

    return dataframe


# --------------------------------------------------------------------------
# Filtering Helpers
# --------------------------------------------------------------------------

def apply_filters(
    customers_df: pd.DataFrame,
    search_term: str,
    selected_cities: list[str],
    selected_brands: list[str],
    selected_names: list[str],
) -> pd.DataFrame:
    """
    Apply search and filter criteria to the customer dataset.

    Args:
        customers_df: Source customer dataset.
        search_term: Free-text search term.
        selected_cities: List of selected cities to filter by.
        selected_brands: List of selected vehicle brands to filter by.
        selected_names: List of selected customer names to filter by.

    Returns:
        The filtered customer DataFrame.
    """
    filtered_df = customers_df.copy()

    if search_term:
        search_lower = search_term.strip().lower()
        searchable_columns = [
            col
            for col in ["CustomerName", "CustomerID", "Phone", "Email"]
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

    if selected_cities and "City" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["City"].isin(selected_cities)]

    if selected_brands and "VehicleBrand" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["VehicleBrand"].isin(selected_brands)
        ]

    if selected_names and "CustomerName" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["CustomerName"].isin(selected_names)
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
    st.title("👥 Customer Management")
    st.caption("Search, filter, and review customer profiles")
    st.markdown("---")


def render_filters(customers_df: pd.DataFrame) -> tuple[str, list[str], list[str], list[str]]:
    """
    Render the search box and filter controls.

    Args:
        customers_df: Source customer dataset used to populate filter options.

    Returns:
        A tuple of (search_term, selected_cities, selected_brands, selected_names).
    """
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🔍 Search &amp; Filter</div>',
        unsafe_allow_html=True,
    )

    search_term = st.text_input(
        "Search Customer",
        placeholder="Search by name, ID, phone, or email...",
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        city_options = (
            sorted(customers_df["City"].dropna().unique().tolist())
            if "City" in customers_df.columns
            else []
        )
        selected_cities = st.multiselect("City", options=city_options)

    with filter_col2:
        brand_options = (
            sorted(customers_df["VehicleBrand"].dropna().unique().tolist())
            if "VehicleBrand" in customers_df.columns
            else []
        )
        selected_brands = st.multiselect("Vehicle Brand", options=brand_options)

    with filter_col3:
        name_options = (
            sorted(customers_df["CustomerName"].dropna().unique().tolist())
            if "CustomerName" in customers_df.columns
            else []
        )
        selected_names = st.multiselect("Customer Name", options=name_options)

    st.markdown("</div>", unsafe_allow_html=True)

    return search_term, selected_cities, selected_brands, selected_names


def render_customer_table(filtered_df: pd.DataFrame) -> str | None:
    """
    Render the customer table with a selection mechanism.

    Args:
        filtered_df: The filtered customer DataFrame to display.

    Returns:
        The CustomerID of the selected row, or None if no selection was made.
    """
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-title">📋 Customer Table ({len(filtered_df)} results)</div>',
        unsafe_allow_html=True,
    )

    selected_customer_id: str | None = None

    if filtered_df.empty:
        st.info("No customers match the current search and filter criteria.")
    else:
        display_df = filtered_df.reset_index(drop=True)

        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="customer_table",
        )

        selected_rows = event.selection.rows if event and event.selection else []
        if selected_rows and "CustomerID" in display_df.columns:
            selected_index = selected_rows[0]
            selected_customer_id = str(display_df.loc[selected_index, "CustomerID"])

    st.markdown("</div>", unsafe_allow_html=True)

    return selected_customer_id


def render_customer_details(customers_df: pd.DataFrame, customer_id: str) -> None:
    """
    Render the detail panel for a selected customer.

    Args:
        customers_df: Full customer dataset.
        customer_id: The CustomerID of the selected customer.
    """
    matching_rows = customers_df[customers_df["CustomerID"] == customer_id]
    if matching_rows.empty:
        return

    customer = matching_rows.iloc[0]

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">🧑‍💼 Customer Details</div>',
        unsafe_allow_html=True,
    )

    name = customer.get("CustomerName", "N/A")
    st.subheader(str(name))

    detail_col1, detail_col2 = st.columns(2)

    vehicle_brand = customer.get("VehicleBrand", "N/A")
    vehicle_model = customer.get("VehicleModel", "N/A")
    registration_number = customer.get("RegistrationNumber", "N/A")
    phone = customer.get("Phone", "N/A")
    email = customer.get("Email", "N/A")
    address = customer.get("Address", "N/A")
    city = customer.get("City", "N/A")

    with detail_col1:
        st.markdown('<div class="detail-label">Vehicle</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="detail-value">{vehicle_brand} {vehicle_model}</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="detail-label">Registration Number</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{registration_number}</div>', unsafe_allow_html=True)

        st.markdown('<div class="detail-label">Phone</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{phone}</div>', unsafe_allow_html=True)

    with detail_col2:
        st.markdown('<div class="detail-label">Email</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{email}</div>', unsafe_allow_html=True)

        st.markdown('<div class="detail-label">Address</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{address}</div>', unsafe_allow_html=True)

        st.markdown('<div class="detail-label">City</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{city}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Page Entry Point
# --------------------------------------------------------------------------

def render_customers_page() -> None:
    """Render the full Customer Management page."""
    inject_styles()
    render_header()

    customers_df = load_customers()

    search_term, selected_cities, selected_brands, selected_names = render_filters(
        customers_df
    )

    filtered_df = apply_filters(
        customers_df, search_term, selected_cities, selected_brands, selected_names
    )

    selected_customer_id = render_customer_table(filtered_df)

    if selected_customer_id:
        render_customer_details(customers_df, selected_customer_id)


render_customers_page()