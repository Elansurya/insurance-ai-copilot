"""
utils/data_loader.py

Reusable, cached data-loading utilities for the Insurance AI Copilot.

Loads customers.csv, policies.csv, and claims.csv from the data/ directory.
If a file does not exist, an empty DataFrame is returned instead of raising
an exception, so the rest of the app can degrade gracefully.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

# Base directory for all data files (project_root/data)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CUSTOMERS_FILE = "customers.csv"
POLICIES_FILE = "policies.csv"
CLAIMS_FILE = "claims.csv"


@st.cache_data(show_spinner=False)
def _load_csv(file_name: str) -> pd.DataFrame:
    """
    Load a CSV file from the data directory into a DataFrame.

    Args:
        file_name: Name of the CSV file (e.g., "customers.csv").

    Returns:
        A pandas DataFrame with the file's contents. If the file does not
        exist or fails to load, an empty DataFrame is returned instead of
        raising an exception.
    """
    file_path = DATA_DIR / file_name

    if not file_path.exists() or not os.path.isfile(file_path):
        return pd.DataFrame()

    try:
        return pd.read_csv(file_path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError):
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_customers() -> pd.DataFrame:
    """
    Load customer records from customers.csv.

    Returns:
        DataFrame containing customer data, or an empty DataFrame if the
        file is missing or unreadable.
    """
    return _load_csv(CUSTOMERS_FILE)


@st.cache_data(show_spinner=False)
def load_policies() -> pd.DataFrame:
    """
    Load policy records from policies.csv.

    Returns:
        DataFrame containing policy data, or an empty DataFrame if the
        file is missing or unreadable.
    """
    return _load_csv(POLICIES_FILE)


@st.cache_data(show_spinner=False)
def load_claims() -> pd.DataFrame:
    """
    Load claim records from claims.csv.

    Returns:
        DataFrame containing claims data, or an empty DataFrame if the
        file is missing or unreadable.
    """
    return _load_csv(CLAIMS_FILE)


def load_all_data() -> dict[str, pd.DataFrame]:
    """
    Load all core datasets (customers, policies, claims) in one call.

    Returns:
        A dictionary mapping dataset names to their DataFrames:
        {"customers": ..., "policies": ..., "claims": ...}
    """
    return {
        "customers": load_customers(),
        "policies": load_policies(),
        "claims": load_claims(),
    }