"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Page: AI Copilot (Rule-Based Chat Assistant)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

DATA_DIR: Path = Path("data")
CUSTOMERS_PATH: Path = DATA_DIR / "customers.csv"
POLICIES_PATH: Path = DATA_DIR / "policies.csv"
CLAIMS_PATH: Path = DATA_DIR / "claims.csv"

EXPIRY_WINDOW_DAYS: int = 30
ASSISTANT_NAME: str = "Insurance AI Copilot"

SUGGESTED_QUESTIONS: list[str] = [
    "Show pending claims",
    "Show expiring policies",
    "Customer details for Amit Chopra",
    "Policy details for CUST0001",
    "What is the renewal date for CUST0001?",
    "What is the premium for CUST0001?",
    "Claim status for CUST0001",
    "Generate renewal email for CUST0001",
]

CUSTOMER_ID_PATTERN = re.compile(r"\bCUST\d{3,6}\b", re.IGNORECASE)
POLICY_ID_PATTERN = re.compile(r"\bPOL\d{3,6}\b", re.IGNORECASE)
CLAIM_ID_PATTERN = re.compile(r"\bCLM\d{3,6}\b", re.IGNORECASE)


# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------

THEME_STYLE: str = """
<style>
.stApp {
    background: radial-gradient(circle at top left, #0f1b3d 0%, #060b1f 60%, #04060f 100%);
}

.copilot-hero {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}
.copilot-hero h1 {
    color: #f8fafc;
    margin-bottom: 0.25rem;
}
.copilot-hero p {
    color: #93c5fd;
    margin: 0;
}

.glass-panel {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.30);
}

.panel-title {
    color: #e2e8f0;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
}

.chat-bubble-user {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #ffffff;
    padding: 0.85rem 1.1rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.4rem 0;
    max-width: 85%;
    margin-left: auto;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    font-size: 0.95rem;
    line-height: 1.5;
}

.chat-bubble-assistant {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    color: #e2e8f0;
    padding: 0.85rem 1.1rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.4rem 0;
    max-width: 85%;
    margin-right: auto;
    border: 1px solid rgba(255, 255, 255, 0.10);
    font-size: 0.95rem;
    line-height: 1.6;
    white-space: pre-wrap;
}

.chat-scroll-area {
    max-height: 520px;
    overflow-y: auto;
    padding-right: 0.5rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1230 0%, #050914 100%);
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


def _build_demo_claims() -> pd.DataFrame:
    """Build an in-memory demo claims dataset."""
    today = date.today()
    claim_dates = [
        today - timedelta(days=d) for d in [45, 30, 90, 10, 5, 60, 120, 15]
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


# --------------------------------------------------------------------------
# Data Loading
# --------------------------------------------------------------------------

def _load_csv_or_none(path: Path) -> pd.DataFrame | None:
    """Load a CSV file if it exists and is non-empty, otherwise return None."""
    if not path.exists():
        return None
    try:
        dataframe = pd.read_csv(path)
    except (pd.errors.EmptyDataError, OSError):
        return None
    return None if dataframe.empty else dataframe


@st.cache_data(show_spinner=False)
def load_customers() -> pd.DataFrame:
    """Load customer data from disk, falling back to demo data."""
    dataframe = _load_csv_or_none(CUSTOMERS_PATH)
    return dataframe if dataframe is not None else _build_demo_customers()


@st.cache_data(show_spinner=False)
def load_policies() -> pd.DataFrame:
    """Load policy data from disk, falling back to demo data."""
    dataframe = _load_csv_or_none(POLICIES_PATH)
    if dataframe is None:
        dataframe = _build_demo_policies()
    if "RenewalDate" in dataframe.columns:
        dataframe["RenewalDate"] = pd.to_datetime(
            dataframe["RenewalDate"], errors="coerce"
        )
    if "StartDate" in dataframe.columns:
        dataframe["StartDate"] = pd.to_datetime(
            dataframe["StartDate"], errors="coerce"
        )
    return dataframe


@st.cache_data(show_spinner=False)
def load_claims() -> pd.DataFrame:
    """Load claims data from disk, falling back to demo data."""
    dataframe = _load_csv_or_none(CLAIMS_PATH)
    if dataframe is None:
        dataframe = _build_demo_claims()
    if "ClaimDate" in dataframe.columns:
        dataframe["ClaimDate"] = pd.to_datetime(
            dataframe["ClaimDate"], errors="coerce"
        )
    return dataframe


# --------------------------------------------------------------------------
# Data Access Helpers
# --------------------------------------------------------------------------

@dataclass
class DataStore:
    """Container bundling the three core datasets for lookup operations."""

    customers: pd.DataFrame
    policies: pd.DataFrame
    claims: pd.DataFrame


def find_customer_row(store: DataStore, query: str) -> pd.Series | None:
    """
    Resolve a customer record from a free-text query using
    CustomerID or CustomerName matching.

    Args:
        store: The bundled datasets.
        query: The raw user query text.

    Returns:
        The matching customer row as a Series, or None if not found.
    """
    id_match = CUSTOMER_ID_PATTERN.search(query)
    if id_match and "CustomerID" in store.customers.columns:
        customer_id = id_match.group(0).upper()
        matches = store.customers[
            store.customers["CustomerID"].str.upper() == customer_id
        ]
        if not matches.empty:
            return matches.iloc[0]

    if "CustomerName" in store.customers.columns:
        query_lower = query.lower()
        for _, row in store.customers.iterrows():
            name = str(row.get("CustomerName", "")).lower()
            if name and name in query_lower:
                return row

        name_tokens = re.findall(r"[A-Za-z]+", query)
        if name_tokens:
            candidate = " ".join(name_tokens).lower()
            partial_matches = store.customers[
                store.customers["CustomerName"]
                .str.lower()
                .apply(lambda n: any(tok in n for tok in name_tokens if len(tok) > 2))
            ]
            if not partial_matches.empty:
                return partial_matches.iloc[0]

    return None


def find_policy_row(store: DataStore, query: str, customer_row: pd.Series | None) -> pd.Series | None:
    """
    Resolve a policy record from a free-text query, either via
    an explicit PolicyID or via a previously resolved customer.

    Args:
        store: The bundled datasets.
        query: The raw user query text.
        customer_row: A previously resolved customer row, if any.

    Returns:
        The matching policy row as a Series, or None if not found.
    """
    id_match = POLICY_ID_PATTERN.search(query)
    if id_match and "PolicyID" in store.policies.columns:
        policy_id = id_match.group(0).upper()
        matches = store.policies[
            store.policies["PolicyID"].str.upper() == policy_id
        ]
        if not matches.empty:
            return matches.iloc[0]

    if customer_row is not None and "CustomerID" in store.policies.columns:
        matches = store.policies[
            store.policies["CustomerID"] == customer_row.get("CustomerID")
        ]
        if not matches.empty:
            return matches.iloc[0]

    return None


def find_claims_for_customer(store: DataStore, customer_row: pd.Series) -> pd.DataFrame:
    """Return all claims associated with a given customer."""
    if "CustomerID" not in store.claims.columns:
        return pd.DataFrame()
    return store.claims[store.claims["CustomerID"] == customer_row.get("CustomerID")]


def get_pending_claims(store: DataStore) -> pd.DataFrame:
    """Return all claims currently in Pending status."""
    if "ClaimStatus" not in store.claims.columns:
        return pd.DataFrame()
    return store.claims[store.claims["ClaimStatus"] == "Pending"]


def get_expiring_policies(store: DataStore, window_days: int = EXPIRY_WINDOW_DAYS) -> pd.DataFrame:
    """Return all policies renewing within the given window of days."""
    if "RenewalDate" not in store.policies.columns:
        return pd.DataFrame()

    today_ts = pd.Timestamp(datetime.now().date())
    window_end = today_ts + pd.Timedelta(days=window_days)
    renewal_dates = pd.to_datetime(store.policies["RenewalDate"], errors="coerce")
    mask = (renewal_dates >= today_ts) & (renewal_dates <= window_end)
    return store.policies[mask]


# --------------------------------------------------------------------------
# Response Formatting Helpers
# --------------------------------------------------------------------------

def _format_currency(value: object) -> str:
    """Format a numeric value as an Indian Rupee currency string."""
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def _format_date(value: object) -> str:
    """Format a date-like value as YYYY-MM-DD, or return N/A."""
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return "N/A"
    return parsed.strftime("%Y-%m-%d")


def format_customer_details(customer_row: pd.Series) -> str:
    """Format a customer record as a readable summary."""
    lines = [
        f"**Customer Details — {customer_row.get('CustomerName', 'N/A')}**",
        f"- Customer ID: {customer_row.get('CustomerID', 'N/A')}",
        f"- Phone: {customer_row.get('Phone', 'N/A')}",
        f"- Email: {customer_row.get('Email', 'N/A')}",
        f"- Address: {customer_row.get('Address', 'N/A')}",
        f"- City: {customer_row.get('City', 'N/A')}",
        f"- Vehicle: {customer_row.get('VehicleBrand', 'N/A')} {customer_row.get('VehicleModel', '')}".strip(),
    ]
    return "\n".join(lines)


def format_policy_details(policy_row: pd.Series) -> str:
    """Format a policy record as a readable summary."""
    lines = [
        f"**Policy Details — {policy_row.get('PolicyID', 'N/A')}**",
        f"- Policy Number: {policy_row.get('PolicyNumber', 'N/A')}",
        f"- Policy Type: {policy_row.get('PolicyType', 'N/A')}",
        f"- Premium Amount: {_format_currency(policy_row.get('PremiumAmount'))}",
        f"- Start Date: {_format_date(policy_row.get('StartDate'))}",
        f"- Renewal Date: {_format_date(policy_row.get('RenewalDate'))}",
        f"- Status: {policy_row.get('PolicyStatus', 'N/A')}",
    ]
    return "\n".join(lines)


def format_claims_table(claims_df: pd.DataFrame, title: str) -> str:
    """Format a claims DataFrame as a readable Markdown list."""
    if claims_df.empty:
        return f"**{title}**\n\nNo matching claims found."

    lines = [f"**{title} ({len(claims_df)})**", ""]
    for _, row in claims_df.iterrows():
        lines.append(
            f"- {row.get('ClaimID', 'N/A')} | "
            f"Customer: {row.get('CustomerID', 'N/A')} | "
            f"Amount: {_format_currency(row.get('ClaimAmount'))} | "
            f"Status: {row.get('ClaimStatus', 'N/A')} | "
            f"Reason: {row.get('ClaimReason', 'N/A')}"
        )
    return "\n".join(lines)


def format_expiring_policies(policies_df: pd.DataFrame) -> str:
    """Format an expiring-policies DataFrame as a readable Markdown list."""
    if policies_df.empty:
        return (
            f"**Policies Expiring in the Next {EXPIRY_WINDOW_DAYS} Days**\n\n"
            "No policies are expiring soon."
        )

    lines = [
        f"**Policies Expiring in the Next {EXPIRY_WINDOW_DAYS} Days "
        f"({len(policies_df)})**",
        "",
    ]
    for _, row in policies_df.iterrows():
        lines.append(
            f"- {row.get('PolicyID', 'N/A')} | "
            f"Customer: {row.get('CustomerID', 'N/A')} | "
            f"Renewal: {_format_date(row.get('RenewalDate'))} | "
            f"Premium: {_format_currency(row.get('PremiumAmount'))}"
        )
    return "\n".join(lines)


def generate_renewal_email(customer_row: pd.Series, policy_row: pd.Series) -> str:
    """Generate a professional renewal email draft as plain text."""
    customer_name = customer_row.get("CustomerName", "Valued Customer")
    policy_number = policy_row.get("PolicyNumber", "N/A")
    renewal_date = _format_date(policy_row.get("RenewalDate"))
    premium = _format_currency(policy_row.get("PremiumAmount"))
    policy_type = policy_row.get("PolicyType", "N/A")

    email_body = f"""**Generated Renewal Email**

Subject: Your Insurance Policy Renewal is Due Soon

Dear {customer_name},

This is a friendly reminder that your {policy_type} policy \
(Policy Number: {policy_number}) is due for renewal on {renewal_date}.

Renewal Premium: {premium}

To ensure uninterrupted coverage for your vehicle, please renew your \
policy before the due date. Our team is happy to assist with the \
renewal process or answer any questions regarding your coverage.

Thank you for choosing us for your insurance needs.

Warm regards,
Insurance AI Copilot Team"""
    return email_body


# --------------------------------------------------------------------------
# Intent Handling
# --------------------------------------------------------------------------

def process_query(store: DataStore, query: str) -> str:
    """
    Interpret a user query using rule-based keyword matching and
    return a formatted natural-language response.

    Args:
        store: The bundled datasets.
        query: The raw user query text.

    Returns:
        The formatted assistant response string.
    """
    query_lower = query.lower().strip()

    if not query_lower:
        return "Please enter a question so I can help you."

    if "pending claim" in query_lower or "show pending claims" in query_lower:
        pending_df = get_pending_claims(store)
        return format_claims_table(pending_df, "Pending Claims")

    if "expiring polic" in query_lower or "expiring soon" in query_lower:
        expiring_df = get_expiring_policies(store)
        return format_expiring_policies(expiring_df)

    if "renewal email" in query_lower or "generate email" in query_lower or "draft email" in query_lower:
        customer_row = find_customer_row(store, query)
        if customer_row is None:
            return (
                "I couldn't identify a customer from your request. "
                "Please include a Customer ID or Customer Name, "
                "e.g. 'Generate renewal email for CUST0001'."
            )
        policy_row = find_policy_row(store, query, customer_row)
        if policy_row is None:
            return f"No policy record found for {customer_row.get('CustomerName', 'this customer')}."
        return generate_renewal_email(customer_row, policy_row)

    if "claim status" in query_lower or "claim" in query_lower:
        customer_row = find_customer_row(store, query)
        claim_id_match = CLAIM_ID_PATTERN.search(query)

        if claim_id_match and "ClaimID" in store.claims.columns:
            claim_id = claim_id_match.group(0).upper()
            matches = store.claims[store.claims["ClaimID"].str.upper() == claim_id]
            if not matches.empty:
                return format_claims_table(matches, f"Claim Status — {claim_id}")

        if customer_row is not None:
            claims_df = find_claims_for_customer(store, customer_row)
            return format_claims_table(
                claims_df, f"Claims for {customer_row.get('CustomerName', 'Customer')}"
            )

        return (
            "I couldn't identify a customer or claim from your request. "
            "Please include a Customer ID, Customer Name, or Claim ID."
        )

    if "renewal date" in query_lower:
        customer_row = find_customer_row(store, query)
        policy_row = find_policy_row(store, query, customer_row)
        if policy_row is None:
            return "I couldn't find a matching policy for your request."
        return (
            f"**Renewal Date — {policy_row.get('PolicyID', 'N/A')}**\n\n"
            f"{_format_date(policy_row.get('RenewalDate'))}"
        )

    if "premium" in query_lower:
        customer_row = find_customer_row(store, query)
        policy_row = find_policy_row(store, query, customer_row)
        if policy_row is None:
            return "I couldn't find a matching policy for your request."
        return (
            f"**Premium Amount — {policy_row.get('PolicyID', 'N/A')}**\n\n"
            f"{_format_currency(policy_row.get('PremiumAmount'))}"
        )

    if "policy detail" in query_lower or "policy info" in query_lower or query_lower.startswith("policy"):
        customer_row = find_customer_row(store, query)
        policy_row = find_policy_row(store, query, customer_row)
        if policy_row is None:
            return "I couldn't find a matching policy for your request."
        return format_policy_details(policy_row)

    if "customer detail" in query_lower or "customer info" in query_lower or query_lower.startswith("customer"):
        customer_row = find_customer_row(store, query)
        if customer_row is None:
            return "I couldn't identify a customer from your request."
        return format_customer_details(customer_row)

    customer_row = find_customer_row(store, query)
    if customer_row is not None:
        return format_customer_details(customer_row)

    return (
        "I'm not sure how to answer that yet. Try asking about customer "
        "details, policy details, renewal dates, premiums, claim status, "
        "pending claims, expiring policies, or request a renewal email."
    )


# --------------------------------------------------------------------------
# Session State
# --------------------------------------------------------------------------

def initialize_chat_state() -> None:
    """Initialize chat-related session state variables."""
    if "ai_copilot_chat_history" not in st.session_state:
        st.session_state["ai_copilot_chat_history"] = [
            {
                "role": "assistant",
                "content": (
                    f"Hello! I'm your {ASSISTANT_NAME}. I can help you look up "
                    "customer details, policy information, renewal dates, "
                    "premiums, claim status, pending claims, expiring "
                    "policies, and draft renewal emails. How can I help you today?"
                ),
            }
        ]
    if "ai_copilot_pending_query" not in st.session_state:
        st.session_state["ai_copilot_pending_query"] = None


# --------------------------------------------------------------------------
# UI Rendering Helpers
# --------------------------------------------------------------------------

def inject_styles() -> None:
    """Inject the dark blue glassmorphism theme CSS."""
    st.markdown(THEME_STYLE, unsafe_allow_html=True)


def render_header() -> None:
    """Render the AI Copilot hero header."""
    st.markdown(
        f"""
        <div class="copilot-hero">
            <h1>🤖 {ASSISTANT_NAME}</h1>
            <p>Enterprise AI Assistant for Insurance CRM &mdash; ask about
            customers, policies, renewals, premiums, and claims.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_suggested_questions() -> str | None:
    """
    Render suggested question buttons.

    Returns:
        The text of the clicked suggestion, or None if none was clicked.
    """
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-title">💡 Suggested Questions</div>',
        unsafe_allow_html=True,
    )

    clicked_question: str | None = None
    columns = st.columns(2)

    for index, question in enumerate(SUGGESTED_QUESTIONS):
        column = columns[index % 2]
        with column:
            if st.button(question, key=f"suggested_q_{index}", use_container_width=True):
                clicked_question = question

    st.markdown("</div>", unsafe_allow_html=True)
    return clicked_question


def render_chat_history() -> None:
    """Render the full chat history using styled bubbles."""
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-title">💬 Conversation</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="chat-scroll-area">', unsafe_allow_html=True)

    for message in st.session_state["ai_copilot_chat_history"]:
        bubble_class = (
            "chat-bubble-user" if message["role"] == "user" else "chat-bubble-assistant"
        )
        st.markdown(
            f'<div class="{bubble_class}">{message["content"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def handle_user_message(store: DataStore, user_text: str) -> None:
    """Append a user message and the assistant's response to chat history."""
    st.session_state["ai_copilot_chat_history"].append(
        {"role": "user", "content": user_text}
    )
    response = process_query(store, user_text)
    st.session_state["ai_copilot_chat_history"].append(
        {"role": "assistant", "content": response}
    )


# --------------------------------------------------------------------------
# Page Entry Point
# --------------------------------------------------------------------------

def render_ai_copilot_page() -> None:
    """Render the full AI Copilot chat page."""
    inject_styles()
    initialize_chat_state()
    render_header()

    customers_df = load_customers()
    policies_df = load_policies()
    claims_df = load_claims()
    store = DataStore(customers=customers_df, policies=policies_df, claims=claims_df)

    clicked_question = render_suggested_questions()
    if clicked_question:
        handle_user_message(store, clicked_question)
        st.rerun()

    render_chat_history()

    user_input = st.chat_input("Ask about a customer, policy, renewal, premium, or claim...")
    if user_input:
        handle_user_message(store, user_input)
        st.rerun()


render_ai_copilot_page()