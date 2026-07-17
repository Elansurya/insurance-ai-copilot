"""
utils/search.py

Reusable search utilities for the Insurance AI Copilot.

Provides search_customer(), search_policy(), and search_claim() functions
that perform case-insensitive, partial-match searches across relevant
columns (Customer Name, Customer ID, Policy Number, Vehicle, Phone Number).

All functions are defensive: if a DataFrame is empty, missing expected
columns, or the query is blank, they return a DataFrame safely instead
of raising an exception.
"""

from __future__ import annotations

import pandas as pd

# Candidate column names (case-insensitive) that each searchable field
# may appear under, to stay resilient to minor naming variations in the
# underlying CSV data.
_CUSTOMER_NAME_COLS = ["customer_name", "customername", "name"]
_CUSTOMER_ID_COLS = ["customer_id", "customerid", "cust_id"]
_POLICY_NUMBER_COLS = ["policy_number", "policynumber", "policy_no", "policy_id"]
_VEHICLE_COLS = ["vehicle", "vehicle_name", "vehicle_model", "vehicle_number", "vehicle_id"]
_PHONE_COLS = ["phone_number", "phonenumber", "phone", "contact_number", "mobile"]
_CLAIM_ID_COLS = ["claim_id", "claimid", "claim_number"]


def _resolve_columns(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    """
    Resolve which of the given candidate column names actually exist in
    the DataFrame, matched case-insensitively.

    Args:
        df: The DataFrame to inspect.
        candidates: A list of possible column names to look for.

    Returns:
        A list of actual column names present in the DataFrame that
        match (case-insensitively) any of the candidates.
    """
    if df is None or df.empty:
        return []

    lower_map = {col.lower(): col for col in df.columns}
    resolved = []
    for candidate in candidates:
        actual = lower_map.get(candidate.lower())
        if actual and actual not in resolved:
            resolved.append(actual)
    return resolved


def _search_columns(df: pd.DataFrame, query: str, columns: list[str]) -> pd.DataFrame:
    """
    Perform a case-insensitive, partial-match search for `query` across
    the given columns of `df`.

    Args:
        df: DataFrame to search.
        query: Search text.
        columns: List of column names to search within.

    Returns:
        A DataFrame containing matching rows. Returns an empty DataFrame
        (preserving original columns where possible) if there is no
        data, no query, or no matching columns.
    """
    if df is None or df.empty or not query or not query.strip():
        return pd.DataFrame(columns=df.columns if df is not None else None)

    if not columns:
        return pd.DataFrame(columns=df.columns)

    query = query.strip()
    mask = pd.Series(False, index=df.index)

    for col in columns:
        try:
            mask = mask | df[col].astype(str).str.contains(
                query, case=False, na=False, regex=False
            )
        except (KeyError, ValueError, TypeError):
            continue

    return df[mask].copy()


def search_customer(customers_df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Search customers by Customer Name, Customer ID, or Phone Number.

    Args:
        customers_df: DataFrame containing customer records.
        query: Search text (partial, case-insensitive match).

    Returns:
        DataFrame of matching customer rows. Empty DataFrame if no
        matches, no data, or an empty query is provided.
    """
    columns = (
        _resolve_columns(customers_df, _CUSTOMER_NAME_COLS)
        + _resolve_columns(customers_df, _CUSTOMER_ID_COLS)
        + _resolve_columns(customers_df, _PHONE_COLS)
    )
    return _search_columns(customers_df, query, columns)


def search_policy(policies_df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Search policies by Policy Number, Customer ID, Customer Name, or
    Vehicle.

    Args:
        policies_df: DataFrame containing policy records.
        query: Search text (partial, case-insensitive match).

    Returns:
        DataFrame of matching policy rows. Empty DataFrame if no
        matches, no data, or an empty query is provided.
    """
    columns = (
        _resolve_columns(policies_df, _POLICY_NUMBER_COLS)
        + _resolve_columns(policies_df, _CUSTOMER_ID_COLS)
        + _resolve_columns(policies_df, _CUSTOMER_NAME_COLS)
        + _resolve_columns(policies_df, _VEHICLE_COLS)
    )
    return _search_columns(policies_df, query, columns)


def search_claim(claims_df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Search claims by Claim ID, Policy Number, Customer ID, Customer Name,
    or Vehicle.

    Args:
        claims_df: DataFrame containing claim records.
        query: Search text (partial, case-insensitive match).

    Returns:
        DataFrame of matching claim rows. Empty DataFrame if no matches,
        no data, or an empty query is provided.
    """
    columns = (
        _resolve_columns(claims_df, _CLAIM_ID_COLS)
        + _resolve_columns(claims_df, _POLICY_NUMBER_COLS)
        + _resolve_columns(claims_df, _CUSTOMER_ID_COLS)
        + _resolve_columns(claims_df, _CUSTOMER_NAME_COLS)
        + _resolve_columns(claims_df, _VEHICLE_COLS)
    )
    return _search_columns(claims_df, query, columns)