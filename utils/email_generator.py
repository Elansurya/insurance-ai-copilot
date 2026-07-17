"""
utils/email_generator.py

Reusable email-generation utilities for the Insurance AI Copilot.

Provides generate_renewal_email(), which builds a professional,
ready-to-send policy renewal email from customer and policy details.
"""

from __future__ import annotations

from datetime import date, datetime
from numbers import Number


def _format_renewal_date(renewal_date: str | date | datetime) -> str:
    """
    Normalize a renewal date value into a human-readable string.

    Args:
        renewal_date: The renewal date as a string, date, or datetime.

    Returns:
        A formatted date string (e.g., "17 July 2026"). If the value
        cannot be parsed, it is returned as-is (stringified).
    """
    if isinstance(renewal_date, (date, datetime)):
        return renewal_date.strftime("%d %B %Y")

    renewal_date_str = str(renewal_date).strip()

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d %B %Y"):
        try:
            parsed = datetime.strptime(renewal_date_str, fmt)
            return parsed.strftime("%d %B %Y")
        except ValueError:
            continue

    return renewal_date_str


def _format_premium(premium: str | int | float) -> str:
    """
    Normalize a premium amount into a readable currency-style string.

    Args:
        premium: The premium amount as a number or string.

    Returns:
        A formatted string (e.g., "1,250.00"). If the value cannot be
        parsed as a number, it is returned as-is (stringified).
    """
    if isinstance(premium, Number):
        return f"{float(premium):,.2f}"

    premium_str = str(premium).strip()
    try:
        return f"{float(premium_str):,.2f}"
    except ValueError:
        return premium_str


def generate_renewal_email(
    customer_name: str,
    policy_number: str,
    renewal_date: str | date | datetime,
    premium: str | int | float,
    currency_symbol: str = "$",
    sender_name: str = "Insurance AI Copilot Team",
    company_name: str = "Our Insurance Company",
) -> str:
    """
    Generate a professional policy renewal email.

    Args:
        customer_name: Full name of the customer.
        policy_number: The policy number being renewed.
        renewal_date: The renewal due date (string, date, or datetime).
        premium: The renewal premium amount (numeric or string).
        currency_symbol: Currency symbol to prefix the premium with.
            Defaults to "$".
        sender_name: Name to sign the email with. Defaults to
            "Insurance AI Copilot Team".
        company_name: Name of the insurance company. Defaults to
            "Our Insurance Company".

    Returns:
        A complete, professional renewal email as a plain-text string,
        including subject line and body.
    """
    customer_display_name = (customer_name or "Valued Customer").strip()
    policy_display_number = (policy_number or "N/A").strip()
    formatted_date = _format_renewal_date(renewal_date)
    formatted_premium = _format_premium(premium)

    subject = f"Subject: Your Policy {policy_display_number} Renewal is Approaching\n\n"

    body = (
        f"Dear {customer_display_name},\n\n"
        f"We hope this message finds you well. This is a friendly reminder "
        f"that your insurance policy with {company_name} is due for renewal.\n\n"
        f"Policy Details:\n"
        f"  • Policy Number: {policy_display_number}\n"
        f"  • Renewal Date: {formatted_date}\n"
        f"  • Renewal Premium: {currency_symbol}{formatted_premium}\n\n"
        f"To ensure uninterrupted coverage, we kindly request that you "
        f"review and confirm your renewal on or before the renewal date "
        f"listed above. Should you have any questions about your coverage, "
        f"premium, or policy terms, our team is here to help.\n\n"
        f"You can renew your policy online, by phone, or by replying "
        f"directly to this email, and one of our representatives will "
        f"assist you promptly.\n\n"
        f"Thank you for continuing to trust {company_name} with your "
        f"insurance needs. We look forward to serving you for another year.\n\n"
        f"Warm regards,\n"
        f"{sender_name}\n"
        f"{company_name}"
    )

    return subject + body