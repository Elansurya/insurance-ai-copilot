"""
Insurance AI Copilot
Enterprise AI Assistant for Insurance CRM

Application entry point / Home Page.
"""

from __future__ import annotations

import base64
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from components.theme import apply_global_theme
from components.metrics import display_metrics
from components.cards import info_card
from utils.data_loader import load_claims, load_customers, load_policies

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

APP_TITLE: str = "Insurance AI Copilot"
APP_ICON: str = "🚗"
APP_VERSION: str = "1.0"

# Resolve all asset paths relative to THIS file, not the current working
# directory. `streamlit run` can be invoked from any folder, so a bare
# relative path like Path("assets/style.css") silently fails to resolve
# (load_css() then no-ops) and the app falls back to a plain white
# background. Anchoring to __file__ makes asset loading work regardless
# of where the app is launched from, and on every page.
BASE_DIR: Path = Path(__file__).resolve().parent
STYLE_SHEET_PATH: Path = BASE_DIR / "assets" / "style.css"
BACKGROUND_IMAGE_PATH: Path = BASE_DIR / "assets" / "background.png"
LOGO_PATH: Path = BASE_DIR / "assets" / "logo.png"

EXPIRY_WINDOW_DAYS: int = 30
RECENT_ACTIVITY_LIMIT: int = 5

# --------------------------------------------------------------------------
# Home Page Styling (page-local, additive only — mirrors the pattern
# already used in pages/dashboard.py, pages/customers.py, etc. Does not
# touch assets/style.css, so nothing else in the app is affected.)
# --------------------------------------------------------------------------

HOME_STYLE: str = """
<style>
.ic-hero {
    position: relative;
    padding: 2.75rem 2.5rem;
    margin-bottom: 1.75rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #0b1f3a 0%, #13294b 55%, #2563eb 150%);
    border: 1px solid rgba(255, 255, 255, 0.10);
    box-shadow: 0 10px 30px rgba(6, 14, 31, 0.5);
    overflow: hidden;
}
.ic-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: repeating-linear-gradient(
        to bottom,
        rgba(255, 255, 255, 0.05) 0px,
        rgba(255, 255, 255, 0.05) 1px,
        transparent 1px,
        transparent 28px
    );
    pointer-events: none;
}
.ic-hero-eyebrow {
    position: relative;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.18);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #ffffff !important;
    margin-bottom: 1rem;
}
.ic-hero-title {
    position: relative;
    z-index: 1;
    font-size: 2.3rem;
    font-weight: 800;
    color: #ffffff !important;
    margin: 0 0 0.5rem 0;
    line-height: 1.15;
}
.ic-hero-subtitle {
    position: relative;
    z-index: 1;
    font-size: 1.02rem;
    font-weight: 500;
    color: #ffffff !important;
    opacity: 0.9;
    max-width: 640px;
    margin: 0;
}
.ic-hero-meta {
    position: relative;
    z-index: 1;
    margin-top: 1.4rem;
    display: flex;
    gap: 1.75rem;
    flex-wrap: wrap;
}
.ic-hero-meta-item {
    color: #ffffff !important;
    font-size: 0.82rem;
    font-weight: 600;
    opacity: 0.85;
}
.ic-hero-meta-item strong {
    color: #ffffff !important;
    font-weight: 800;
}

.ic-section-heading {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff !important;
    margin: 0 0 1rem 0;
}

.ic-quick-action {
    display: block;
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    text-decoration: none !important;
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
    height: 100%;
}
.ic-quick-action:hover {
    transform: translateY(-3px);
    border-color: rgba(59, 130, 246, 0.45);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
}
.ic-quick-action-icon {
    font-size: 1.5rem;
    margin-bottom: 0.4rem;
}
.ic-quick-action-label {
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff !important;
    margin-bottom: 0.2rem;
}
.ic-quick-action-desc {
    font-size: 0.78rem;
    color: #ffffff !important;
    opacity: 0.7;
}

.ic-insight-card {
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-left: 4px solid #3b82f6;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}
.ic-insight-icon {
    font-size: 1.3rem;
    margin-bottom: 0.35rem;
}
.ic-insight-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #ffffff !important;
    opacity: 0.75;
    margin-bottom: 0.2rem;
}
.ic-insight-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff !important;
    margin-bottom: 0.2rem;
}
.ic-insight-desc {
    font-size: 0.82rem;
    color: #ffffff !important;
    opacity: 0.75;
}

.ic-panel {
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.ic-activity-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.ic-activity-row:last-child { border-bottom: none; }
.ic-activity-main {
    color: #ffffff !important;
    font-size: 0.88rem;
    font-weight: 600;
}
.ic-activity-sub {
    color: #ffffff !important;
    opacity: 0.65;
    font-size: 0.76rem;
}
.ic-activity-badge {
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    white-space: nowrap;
}
.ic-badge-approved, .ic-badge-active { background: rgba(52, 211, 153, 0.16); color: #34d399 !important; }
.ic-badge-pending { background: rgba(251, 191, 36, 0.16); color: #fbbf24 !important; }
.ic-badge-rejected, .ic-badge-expired { background: rgba(248, 113, 113, 0.16); color: #f87171 !important; }
.ic-badge-neutral { background: rgba(255, 255, 255, 0.10); color: #ffffff !important; }

.ic-status-row {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.55rem 0;
}
.ic-status-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
}
.ic-dot-online { background: #34d399; box-shadow: 0 0 8px rgba(52, 211, 153, 0.7); }
.ic-dot-warning { background: #fbbf24; box-shadow: 0 0 8px rgba(251, 191, 36, 0.7); }
.ic-status-label {
    color: #ffffff !important;
    font-size: 0.88rem;
    font-weight: 600;
    flex: 1;
}
.ic-status-value {
    color: #ffffff !important;
    opacity: 0.7;
    font-size: 0.8rem;
    font-weight: 600;
}
.ic-empty-note {
    color: #ffffff !important;
    opacity: 0.65;
    font-size: 0.85rem;
    font-style: italic;
    padding: 0.5rem 0;
}
</style>
"""


# --------------------------------------------------------------------------
# Page Configuration
# --------------------------------------------------------------------------

def configure_page() -> None:
    """Configure global Streamlit page settings. Must run first."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )


# --------------------------------------------------------------------------
# Session State
# --------------------------------------------------------------------------

def initialize_session_state() -> None:
    """Initialize required session state variables if not already set."""
    default_state: dict[str, object] = {
        "logged_in": False,
        "username": "",
        "theme": "dark",
    }

    for key, default_value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# --------------------------------------------------------------------------
# Legacy Asset Helpers
# --------------------------------------------------------------------------
# Kept in place (not removed) for backward compatibility, in case any
# other module does `from app import apply_theme` or similar. The actual
# theming work is now delegated to components/theme.py's
# apply_global_theme(), which is the single shared theming entry point
# used consistently across the whole multipage app.

@st.cache_data(show_spinner=False)
def _encode_file_base64(file_path: str) -> str | None:
    """
    Read a binary file and return its base64-encoded contents.

    Args:
        file_path: Absolute path to the file, as a string (str, so the
            result is cache-key-hashable across reruns).

    Returns:
        The base64-encoded string, or None if the file does not exist
        or cannot be read.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return None

    try:
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    except OSError:
        return None


def _mime_type_for(path: Path) -> str:
    """Return an appropriate image MIME type based on file extension."""
    suffix = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }.get(suffix, "image/png")


def load_css(css_path: Path = STYLE_SHEET_PATH) -> None:
    """Safely load and inject the external CSS stylesheet if it exists."""
    if not css_path.exists():
        return

    try:
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except OSError:
        pass


def apply_background(image_path: Path = BACKGROUND_IMAGE_PATH) -> None:
    """Apply the enterprise background image via a base64 data URI."""
    encoded = _encode_file_base64(str(image_path))
    if not encoded:
        return

    mime_type = _mime_type_for(image_path)
    st.markdown(
        f"""
        <style>
        :root {{
            --ic-bg-image: url("data:{mime_type};base64,{encoded}");
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_logo(logo_path: Path = LOGO_PATH) -> None:
    """Display the enterprise logo using Streamlit's native st.logo API."""
    if not logo_path.exists():
        return

    try:
        st.logo(str(logo_path), size="large")
    except Exception:
        pass


def apply_theme(
    css_path: Path = STYLE_SHEET_PATH,
    background_path: Path = BACKGROUND_IMAGE_PATH,
    logo_path: Path = LOGO_PATH,
) -> None:
    """
    Apply the full enterprise theme.

    Delegates to components.theme.apply_global_theme() — the single
    shared theming entry point used by every page — so the stylesheet,
    background, and logo stay perfectly consistent app-wide. Retained
    under its original name/signature for backward compatibility.
    """
    apply_global_theme()


# --------------------------------------------------------------------------
# Loading Experience
# --------------------------------------------------------------------------

def show_loading_spinner() -> None:
    """Display a professional loading spinner during application startup."""
    with st.spinner("Loading Insurance AI Copilot..."):
        time.sleep(0.6)


# --------------------------------------------------------------------------
# Home Page Data Helpers
# --------------------------------------------------------------------------

def _to_datetime_safe(series: pd.Series) -> pd.Series:
    """Convert a series to datetime, coercing invalid values to NaT."""
    return pd.to_datetime(series, errors="coerce")


@st.cache_data(show_spinner=False)
def _load_home_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load customers, policies, and claims via the shared data loader."""
    return load_customers(), load_policies(), load_claims()


def compute_home_kpis(
    customers_df: pd.DataFrame,
    policies_df: pd.DataFrame,
    claims_df: pd.DataFrame,
) -> dict[str, int]:
    """
    Compute headline KPI values for the home page, using the same
    column assumptions and logic already proven on the Dashboard page.
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
        expiring_soon = int(((renewal_dates >= today_ts) & (renewal_dates <= window_end)).sum())

    pending_claims = 0
    if "ClaimStatus" in claims_df.columns:
        pending_claims = int((claims_df["ClaimStatus"] == "Pending").sum())

    return {
        "total_customers": total_customers,
        "active_policies": active_policies,
        "expiring_policies": expiring_soon,
        "pending_claims": pending_claims,
    }


def compute_ai_insights(
    customers_df: pd.DataFrame,
    policies_df: pd.DataFrame,
    claims_df: pd.DataFrame,
    expiring_soon: int,
) -> list[dict[str, str]]:
    """
    Derive a handful of rule-based insights straight from the live
    datasets. Every value is computed on the fly — nothing here is
    hardcoded — and each insight degrades gracefully if its source
    column isn't present.
    """
    insights: list[dict[str, str]] = []

    insights.append({
        "icon": "⏳",
        "title": "Renewals Due Soon",
        "value": str(expiring_soon),
        "desc": f"policies renewing in the next {EXPIRY_WINDOW_DAYS} days",
    })

    if "City" in customers_df.columns and not customers_df.empty:
        top_city = customers_df["City"].value_counts().idxmax()
        top_city_count = int(customers_df["City"].value_counts().max())
        insights.append({
            "icon": "🏙️",
            "title": "Top Customer City",
            "value": str(top_city),
            "desc": f"{top_city_count} customers based here",
        })

    if {"PremiumAmount", "PolicyStatus"}.issubset(policies_df.columns):
        active_premium = policies_df.loc[
            policies_df["PolicyStatus"] == "Active", "PremiumAmount"
        ].sum()
        insights.append({
            "icon": "💰",
            "title": "Active Premium Value",
            "value": f"₹{active_premium:,.0f}",
            "desc": "combined premium across active policies",
        })

    if "ClaimStatus" in claims_df.columns and not claims_df.empty:
        total_claims = len(claims_df)
        approved = int((claims_df["ClaimStatus"] == "Approved").sum())
        approval_rate = (approved / total_claims * 100) if total_claims else 0
        insights.append({
            "icon": "✅",
            "title": "Claim Approval Rate",
            "value": f"{approval_rate:.0f}%",
            "desc": f"{approved} of {total_claims} claims approved",
        })

    return insights


def get_recent_claims(claims_df: pd.DataFrame, limit: int) -> pd.DataFrame:
    """Return the most recently filed claims, newest first."""
    if "ClaimDate" not in claims_df.columns or claims_df.empty:
        return claims_df.head(limit)

    working_df = claims_df.copy()
    working_df["_ClaimDateParsed"] = _to_datetime_safe(working_df["ClaimDate"])
    working_df = working_df.sort_values(
        by="_ClaimDateParsed", ascending=False, na_position="last"
    )
    return working_df.drop(columns=["_ClaimDateParsed"]).head(limit)


def get_upcoming_renewals(policies_df: pd.DataFrame, limit: int) -> pd.DataFrame:
    """Return the soonest-upcoming policy renewals."""
    if "RenewalDate" not in policies_df.columns or policies_df.empty:
        return policies_df.head(limit)

    working_df = policies_df.copy()
    working_df["_RenewalDateParsed"] = _to_datetime_safe(working_df["RenewalDate"])
    working_df = working_df.sort_values(
        by="_RenewalDateParsed", ascending=True, na_position="last"
    )
    return working_df.drop(columns=["_RenewalDateParsed"]).head(limit)


def _status_badge_class(status: str) -> str:
    """Map a status string to its badge CSS class."""
    normalized = str(status).strip().lower()
    mapping = {
        "approved": "ic-badge-approved",
        "active": "ic-badge-active",
        "pending": "ic-badge-pending",
        "rejected": "ic-badge-rejected",
        "expired": "ic-badge-expired",
    }
    return mapping.get(normalized, "ic-badge-neutral")


# --------------------------------------------------------------------------
# Home Page Rendering
# --------------------------------------------------------------------------

def render_hero(customers_df: pd.DataFrame, policies_df: pd.DataFrame, claims_df: pd.DataFrame) -> None:
    """Render the top hero banner with a personalized greeting."""
    username = st.session_state.get("username", "")
    logged_in = st.session_state.get("logged_in", False)

    subtitle = (
        f"Welcome back, {username} 👋 — here's what's happening across your book of business today."
        if logged_in and username
        else "Your enterprise AI assistant for customers, policies, claims, and renewals — all in one place."
    )

    st.markdown(
        f"""
        <div class="ic-hero">
            <div class="ic-hero-eyebrow">🚗 {APP_TITLE} · v{APP_VERSION}</div>
            <h1 class="ic-hero-title">Enterprise Insurance CRM, powered by AI</h1>
            <p class="ic-hero-subtitle">{subtitle}</p>
            <div class="ic-hero-meta">
                <div class="ic-hero-meta-item"><strong>{len(customers_df)}</strong> customers</div>
                <div class="ic-hero-meta-item"><strong>{len(policies_df)}</strong> policies</div>
                <div class="ic-hero-meta-item"><strong>{len(claims_df)}</strong> claims on file</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_section(kpis: dict[str, int]) -> None:
    """Render the KPI summary row using the shared metrics component."""
    st.markdown('<div class="ic-section-heading">📊 Key Metrics</div>', unsafe_allow_html=True)
    display_metrics(
        total_customers=kpis["total_customers"],
        active_policies=kpis["active_policies"],
        expiring_policies=kpis["expiring_policies"],
        pending_claims=kpis["pending_claims"],
    )


def render_quick_actions() -> None:
    """Render quick-navigation cards to every major page."""
    st.markdown('<div class="ic-section-heading">⚡ Quick Actions</div>', unsafe_allow_html=True)

    actions = [
        {"page": "pages/dashboard.py", "icon": "📊", "label": "Dashboard", "desc": "Analytics & trends"},
        {"page": "pages/customers.py", "icon": "👥", "label": "Customers", "desc": "Search & manage"},
        {"page": "pages/policies.py", "icon": "📄", "label": "Policies", "desc": "Track renewals"},
        {"page": "pages/claims.py", "icon": "📋", "label": "Claims", "desc": "Review & process"},
        {"page": "pages/ai_copilot.py", "icon": "🤖", "label": "AI Copilot", "desc": "Ask a question"},
    ]

    columns = st.columns(len(actions))
    for column, action in zip(columns, actions):
        with column:
            try:
                st.page_link(
                    action["page"],
                    label=f'{action["icon"]}  {action["label"]}',
                    help=action["desc"],
                    use_container_width=True,
                )
            except Exception:
                # st.page_link requires the target to be a registered
                # multipage file; fall back silently if unavailable so
                # the home page never breaks because of navigation.
                st.markdown(
                    f"""
                    <div class="ic-quick-action">
                        <div class="ic-quick-action-icon">{action['icon']}</div>
                        <div class="ic-quick-action-label">{action['label']}</div>
                        <div class="ic-quick-action-desc">{action['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_ai_insights(insights: list[dict[str, str]]) -> None:
    """Render the AI-derived insight cards."""
    st.markdown('<div class="ic-section-heading">🤖 AI Insights</div>', unsafe_allow_html=True)

    if not insights:
        st.markdown(
            '<div class="ic-panel"><div class="ic-empty-note">'
            "No data available yet — add records to the data/ folder to see live insights."
            "</div></div>",
            unsafe_allow_html=True,
        )
        return

    columns = st.columns(len(insights))
    for column, insight in zip(columns, insights):
        with column:
            st.markdown(
                f"""
                <div class="ic-insight-card">
                    <div class="ic-insight-icon">{insight['icon']}</div>
                    <div class="ic-insight-title">{insight['title']}</div>
                    <div class="ic-insight-value">{insight['value']}</div>
                    <div class="ic-insight-desc">{insight['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_recent_activity(policies_df: pd.DataFrame, claims_df: pd.DataFrame) -> None:
    """Render the recent claims and upcoming renewals feed."""
    st.markdown('<div class="ic-section-heading">🕒 Recent Activity</div>', unsafe_allow_html=True)

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown('<div class="ic-panel">', unsafe_allow_html=True)
        st.markdown(
            '<div style="color:#ffffff;font-weight:700;margin-bottom:0.5rem;">Recent Claims</div>',
            unsafe_allow_html=True,
        )
        recent_claims = get_recent_claims(claims_df, RECENT_ACTIVITY_LIMIT)
        if recent_claims.empty:
            st.markdown('<div class="ic-empty-note">No claims on file yet.</div>', unsafe_allow_html=True)
        else:
            for _, row in recent_claims.iterrows():
                claim_id = row.get("ClaimID", "N/A")
                status = row.get("ClaimStatus", "N/A")
                amount = row.get("ClaimAmount", "")
                claim_date = row.get("ClaimDate", "")
                amount_str = f"₹{amount:,.0f}" if isinstance(amount, (int, float)) else str(amount)
                st.markdown(
                    f"""
                    <div class="ic-activity-row">
                        <div>
                            <div class="ic-activity-main">Claim {claim_id} · {amount_str}</div>
                            <div class="ic-activity-sub">{claim_date}</div>
                        </div>
                        <div class="ic-activity-badge {_status_badge_class(status)}">{status}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_column:
        st.markdown('<div class="ic-panel">', unsafe_allow_html=True)
        st.markdown(
            '<div style="color:#ffffff;font-weight:700;margin-bottom:0.5rem;">Upcoming Renewals</div>',
            unsafe_allow_html=True,
        )
        upcoming = get_upcoming_renewals(policies_df, RECENT_ACTIVITY_LIMIT)
        if upcoming.empty:
            st.markdown('<div class="ic-empty-note">No upcoming renewals found.</div>', unsafe_allow_html=True)
        else:
            for _, row in upcoming.iterrows():
                policy_id = row.get("PolicyID", "N/A")
                status = row.get("PolicyStatus", "N/A")
                renewal_date = row.get("RenewalDate", "")
                policy_type = row.get("PolicyType", "")
                st.markdown(
                    f"""
                    <div class="ic-activity-row">
                        <div>
                            <div class="ic-activity-main">Policy {policy_id} · {policy_type}</div>
                            <div class="ic-activity-sub">Renews {renewal_date}</div>
                        </div>
                        <div class="ic-activity-badge {_status_badge_class(status)}">{status}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)


def render_system_status(
    customers_df: pd.DataFrame,
    policies_df: pd.DataFrame,
    claims_df: pd.DataFrame,
) -> None:
    """Render a live system/data status panel."""
    st.markdown('<div class="ic-section-heading">🖥️ System Status</div>', unsafe_allow_html=True)

    has_data = not (customers_df.empty and policies_df.empty and claims_df.empty)
    data_source_label = "Live CSV Data" if has_data else "No Data Found (demo/empty)"
    data_dot = "ic-dot-online" if has_data else "ic-dot-warning"

    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")

    st.markdown('<div class="ic-panel">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ic-status-row">
            <span class="ic-status-dot {data_dot}"></span>
            <span class="ic-status-label">Data Source</span>
            <span class="ic-status-value">{data_source_label}</span>
        </div>
        <div class="ic-status-row">
            <span class="ic-status-dot ic-dot-online"></span>
            <span class="ic-status-label">AI Copilot Engine</span>
            <span class="ic-status-value">Online</span>
        </div>
        <div class="ic-status-row">
            <span class="ic-status-dot ic-dot-online"></span>
            <span class="ic-status-label">Records Loaded</span>
            <span class="ic-status-value">{len(customers_df)} customers · {len(policies_df)} policies · {len(claims_df)} claims</span>
        </div>
        <div class="ic-status-row">
            <span class="ic-status-dot ic-dot-online"></span>
            <span class="ic-status-label">Last Refreshed</span>
            <span class="ic-status-value">{now_str}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_home() -> None:
    """Render the full enterprise Home Page."""
    st.markdown(HOME_STYLE, unsafe_allow_html=True)

    customers_df, policies_df, claims_df = _load_home_data()
    kpis = compute_home_kpis(customers_df, policies_df, claims_df)
    insights = compute_ai_insights(
        customers_df, policies_df, claims_df, kpis["expiring_policies"]
    )

    render_hero(customers_df, policies_df, claims_df)
    render_kpi_section(kpis)
    render_quick_actions()
    render_ai_insights(insights)
    render_recent_activity(policies_df, claims_df)
    render_system_status(customers_df, policies_df, claims_df)


def render_footer() -> None:
    """Render the application footer."""
    st.markdown("---")
    st.markdown(
        "<div class='ic-app-footer'>"
        "<span>Developed using Python + Streamlit</span>"
        f"<span><strong>{APP_TITLE}</strong> · v{APP_VERSION}</span>"
        "</div>",
        unsafe_allow_html=True,
    )


def route() -> None:
    """Render the Home Page. Multipage navigation to other pages is
    handled natively by Streamlit via the pages/ directory."""
    render_home()


# --------------------------------------------------------------------------
# Application Entry Point
# --------------------------------------------------------------------------

def main() -> None:
    """Application bootstrap and execution entry point."""
    configure_page()
    apply_global_theme()
    initialize_session_state()
    show_loading_spinner()
    route()
    render_footer()


if __name__ == "__main__":
    main()