"""
utils/ai_engine.py

Rule-based AI engine for the Insurance AI Copilot.

Answers natural-language questions about customers, policies, renewals,
premiums, and claims using deterministic keyword/intent matching and
DataFrame lookups — no external LLM/OpenAI API is used.

Supported intents:
    - Customer Details
    - Policy Details
    - Renewal Date
    - Premium
    - Claim Status
    - Pending Claims
    - Generate Email (renewal reminder)
"""

from __future__ import annotations

import re

import pandas as pd

from utils.email_generator import generate_renewal_email
from utils.search import search_claim, search_customer, search_policy

# ---------------------------------------------------------------------------
# Column candidates (case-insensitive) used to locate display fields across
# possibly-varying CSV schemas.
# ---------------------------------------------------------------------------
_CUSTOMER_NAME_COLS = ["customer_name", "customername", "name"]
_CUSTOMER_ID_COLS = ["customer_id", "customerid", "cust_id"]
_PHONE_COLS = ["phone_number", "phonenumber", "phone", "contact_number", "mobile"]
_EMAIL_COLS = ["email", "email_address", "customer_email"]
_POLICY_NUMBER_COLS = ["policy_number", "policynumber", "policy_no", "policy_id"]
_POLICY_TYPE_COLS = ["policy_type", "policytype", "type"]
_VEHICLE_COLS = ["vehicle", "vehicle_name", "vehicle_model", "vehicle_number", "vehicle_id"]
_PREMIUM_COLS = ["premium", "premium_amount", "renewal_premium"]
_RENEWAL_DATE_COLS = ["renewal_date", "renewaldate", "renewal_due_date", "due_date"]
_CLAIM_ID_COLS = ["claim_id", "claimid", "claim_number"]
_CLAIM_STATUS_COLS = ["status", "claim_status"]
_CLAIM_AMOUNT_COLS = ["claim_amount", "amount"]
_CLAIM_DATE_COLS = ["claim_date", "date_filed", "filed_date"]

_STOPWORDS = {
    "the", "a", "an", "of", "for", "is", "are", "was", "were", "what",
    "when", "where", "who", "whom", "how", "much", "does", "do", "did",
    "please", "show", "me", "tell", "about", "find", "get", "give",
    "and", "to", "on", "in", "with", "details", "detail", "info",
    "information", "status", "date", "amount", "my", "i", "want",
    "need", "can", "you", "generate", "send", "write", "draft", "an",
    "email", "renewal", "reminder", "premium", "policy", "claim",
    "claims", "customer", "pending", "his", "her", "their", "its",
}

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "generate_email": ["generate email", "renewal email", "send email", "draft email", "write email"],
    "pending_claims": ["pending claim", "pending claims", "open claims", "outstanding claims"],
    "claim_status": ["claim status", "status of claim", "claim"],
    "renewal_date": ["renewal date", "when does", "when will", "when is", "renew", "renewal"],
    "premium": ["premium", "how much do i pay", "how much is the premium", "cost"],
    "policy_details": ["policy details", "policy number", "policy info", "policy"],
    "customer_details": ["customer details", "customer info", "who is", "customer"],
}


def _clean(text: str) -> str:
    """Lowercase and strip a string, collapsing internal whitespace."""
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _detect_intent(question: str) -> str:
    """
    Detect the user's intent from the question using ordered keyword
    matching (most specific intents are checked first).

    Args:
        question: The raw user question.

    Returns:
        An intent name (see _INTENT_KEYWORDS keys), or "unknown" if no
        keyword matches.
    """
    cleaned = _clean(question)
    for intent, keywords in _INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in cleaned:
                return intent
    return "unknown"


def _extract_search_terms(question: str) -> list[str]:
    """
    Extract candidate search terms from the question by stripping
    punctuation and known stopwords/intent keywords.

    Args:
        question: The raw user question.

    Returns:
        A list of candidate search terms ordered from most specific
        (the full cleaned phrase) to individual tokens (longest first).
        Returns an empty list if nothing meaningful remains.
    """
    cleaned = re.sub(r"[^\w\s]", " ", question or "").lower()
    tokens = [t for t in cleaned.split() if t and t not in _STOPWORDS]

    if not tokens:
        return []

    terms = [" ".join(tokens)]
    unique_tokens = sorted(set(tokens), key=len, reverse=True)
    terms.extend(unique_tokens)
    return terms


def _resolve_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first actual column in `df` matching any candidate name."""
    if df is None or df.empty:
        return None
    lower_map = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def _get_field(row: pd.Series, df: pd.DataFrame, candidates: list[str], default: str = "N/A") -> str:
    """Fetch a display value from a row using flexible column matching."""
    col = _resolve_column(df, candidates)
    if col is None or col not in row or pd.isna(row[col]):
        return default
    return str(row[col])


def _first_match(df: pd.DataFrame, search_fn, terms: list[str]) -> pd.DataFrame:
    """
    Try each candidate term against a search function until a non-empty
    result is found.

    Args:
        df: DataFrame to search.
        search_fn: One of search_customer, search_policy, search_claim.
        terms: Ordered list of candidate search terms.

    Returns:
        The first non-empty match DataFrame, or an empty DataFrame if no
        term produced a match.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    for term in terms:
        result = search_fn(df, term)
        if result is not None and not result.empty:
            return result

    return pd.DataFrame()


def _format_customer_details(row: pd.Series, customers_df: pd.DataFrame) -> str:
    name = _get_field(row, customers_df, _CUSTOMER_NAME_COLS)
    cust_id = _get_field(row, customers_df, _CUSTOMER_ID_COLS)
    phone = _get_field(row, customers_df, _PHONE_COLS)
    email = _get_field(row, customers_df, _EMAIL_COLS)
    return (
        f"Here are the customer details I found:\n\n"
        f"• Name: {name}\n"
        f"• Customer ID: {cust_id}\n"
        f"• Phone: {phone}\n"
        f"• Email: {email}"
    )


def _format_policy_details(row: pd.Series, policies_df: pd.DataFrame) -> str:
    policy_number = _get_field(row, policies_df, _POLICY_NUMBER_COLS)
    policy_type = _get_field(row, policies_df, _POLICY_TYPE_COLS)
    vehicle = _get_field(row, policies_df, _VEHICLE_COLS)
    premium = _get_field(row, policies_df, _PREMIUM_COLS)
    renewal_date = _get_field(row, policies_df, _RENEWAL_DATE_COLS)
    return (
        f"Here are the policy details I found:\n\n"
        f"• Policy Number: {policy_number}\n"
        f"• Policy Type: {policy_type}\n"
        f"• Vehicle: {vehicle}\n"
        f"• Premium: {premium}\n"
        f"• Renewal Date: {renewal_date}"
    )


def _format_claim_details(row: pd.Series, claims_df: pd.DataFrame) -> str:
    claim_id = _get_field(row, claims_df, _CLAIM_ID_COLS)
    policy_number = _get_field(row, claims_df, _POLICY_NUMBER_COLS)
    status = _get_field(row, claims_df, _CLAIM_STATUS_COLS)
    amount = _get_field(row, claims_df, _CLAIM_AMOUNT_COLS)
    claim_date = _get_field(row, claims_df, _CLAIM_DATE_COLS)
    return (
        f"Here is the claim status I found:\n\n"
        f"• Claim ID: {claim_id}\n"
        f"• Policy Number: {policy_number}\n"
        f"• Status: {status}\n"
        f"• Claim Amount: {amount}\n"
        f"• Claim Date: {claim_date}"
    )


def _handle_pending_claims(claims_df: pd.DataFrame) -> str:
    status_col = _resolve_column(claims_df, _CLAIM_STATUS_COLS)
    if claims_df is None or claims_df.empty or status_col is None:
        return "I couldn't find any claims data to check for pending claims."

    pending = claims_df[claims_df[status_col].astype(str).str.contains("pending", case=False, na=False)]

    if pending.empty:
        return "There are no pending claims at the moment."

    claim_id_col = _resolve_column(pending, _CLAIM_ID_COLS)
    policy_col = _resolve_column(pending, _POLICY_NUMBER_COLS)

    lines = [f"I found {len(pending)} pending claim(s):", ""]
    for _, row in pending.iterrows():
        claim_id = row[claim_id_col] if claim_id_col else "N/A"
        policy_number = row[policy_col] if policy_col else "N/A"
        lines.append(f"• Claim {claim_id} — Policy {policy_number}")

    return "\n".join(lines)


def _handle_generate_email(
    terms: list[str],
    customers_df: pd.DataFrame,
    policies_df: pd.DataFrame,
) -> str:
    policy_match = _first_match(policies_df, search_policy, terms)

    if policy_match.empty:
        return (
            "I couldn't find a matching policy to generate a renewal email. "
            "Please include the customer name or policy number in your request."
        )

    policy_row = policy_match.iloc[0]
    policy_number = _get_field(policy_row, policies_df, _POLICY_NUMBER_COLS)
    premium = _get_field(policy_row, policies_df, _PREMIUM_COLS)
    renewal_date = _get_field(policy_row, policies_df, _RENEWAL_DATE_COLS)

    customer_name = _get_field(policy_row, policies_df, _CUSTOMER_NAME_COLS, default="")
    if not customer_name:
        customer_match = _first_match(customers_df, search_customer, terms)
        if not customer_match.empty:
            customer_name = _get_field(customer_match.iloc[0], customers_df, _CUSTOMER_NAME_COLS)
        else:
            customer_name = "Valued Customer"

    email_body = generate_renewal_email(
        customer_name=customer_name,
        policy_number=policy_number,
        renewal_date=renewal_date,
        premium=premium,
    )

    return f"Here is the renewal email draft:\n\n{email_body}"


def process_query(
    question: str,
    customers_data: pd.DataFrame,
    policies_data: pd.DataFrame,
    claims_data: pd.DataFrame,
) -> str:
    """
    Process a natural-language question and return a clean, professional
    response using rule-based intent detection and DataFrame lookups.

    Args:
        question: The user's question, in plain English.
        customers_data: DataFrame of customer records.
        policies_data: DataFrame of policy records.
        claims_data: DataFrame of claim records.

    Returns:
        A professional, human-readable response string. Never raises an
        exception — returns a helpful fallback message if no answer can
        be determined.
    """
    if not question or not question.strip():
        return "Please enter a question so I can help you."

    intent = _detect_intent(question)
    terms = _extract_search_terms(question)

    if not terms and intent != "pending_claims":
        return (
            "I couldn't identify a customer, policy, or claim reference in "
            "your question. Please include a name, ID, or policy number."
        )

    if intent == "generate_email":
        return _handle_generate_email(terms, customers_data, policies_data)

    if intent == "pending_claims":
        return _handle_pending_claims(claims_data)

    if intent == "claim_status":
        match = _first_match(claims_data, search_claim, terms)
        if match.empty:
            return "I couldn't find any claim matching your request."
        return _format_claim_details(match.iloc[0], claims_data)

    if intent in ("renewal_date", "premium", "policy_details"):
        match = _first_match(policies_data, search_policy, terms)
        if match.empty:
            return "I couldn't find any policy matching your request."

        row = match.iloc[0]

        if intent == "renewal_date":
            renewal_date = _get_field(row, policies_data, _RENEWAL_DATE_COLS)
            policy_number = _get_field(row, policies_data, _POLICY_NUMBER_COLS)
            return f"The renewal date for policy {policy_number} is {renewal_date}."

        if intent == "premium":
            premium = _get_field(row, policies_data, _PREMIUM_COLS)
            policy_number = _get_field(row, policies_data, _POLICY_NUMBER_COLS)
            return f"The premium for policy {policy_number} is {premium}."

        return _format_policy_details(row, policies_data)

    if intent == "customer_details":
        match = _first_match(customers_data, search_customer, terms)
        if match.empty:
            return "I couldn't find any customer matching your request."
        return _format_customer_details(match.iloc[0], customers_data)

    # Unknown intent: try customers, then policies, then claims as a fallback.
    customer_match = _first_match(customers_data, search_customer, terms)
    if not customer_match.empty:
        return _format_customer_details(customer_match.iloc[0], customers_data)

    policy_match = _first_match(policies_data, search_policy, terms)
    if not policy_match.empty:
        return _format_policy_details(policy_match.iloc[0], policies_data)

    claim_match = _first_match(claims_data, search_claim, terms)
    if not claim_match.empty:
        return _format_claim_details(claim_match.iloc[0], claims_data)

    return (
        "I couldn't find an answer to your question. Try asking about a "
        "customer, policy, renewal date, premium, or claim status."
    )