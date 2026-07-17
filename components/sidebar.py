"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Component: Sidebar Navigation
"""

from __future__ import annotations

import streamlit as st

from components.theme import apply_global_theme, render_brand_logo

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

MENU_ITEMS: list[str] = [
    "🏠 Dashboard",
    "👥 Customers",
    "📄 Policies",
    "📋 Claims",
    "🤖 AI Copilot",
    "📊 Reports",
    "⚙ Settings",
    "🚪 Logout",
]

DEFAULT_MENU_ITEM: str = MENU_ITEMS[0]
NAV_STATE_KEY: str = "sidebar_selected_page"

SIDEBAR_STYLE: str = """
<style>
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1230 0%, #060a1c 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

section[data-testid="stSidebar"] > div:first-child {
    background-image: repeating-linear-gradient(
        to bottom,
        rgba(255, 255, 255, 0.04) 0px,
        rgba(255, 255, 255, 0.04) 1px,
        transparent 1px,
        transparent 30px
    );
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0.25rem 1.25rem 0.25rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.10);
}
.ic-brand-logo img { border-radius: 12px; }
.sidebar-brand-text {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    min-width: 0;
}
.sidebar-brand-title {
    color: #f8fafc;
    font-size: 1.08rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.sidebar-brand-subtitle {
    color: #93c5fd;
    font-size: 0.76rem;
    font-weight: 500;
}

.sidebar-user {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 12px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 1rem;
}
.sidebar-user-label {
    color: #ffffff;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 700;
}
.sidebar-user-name {
    color: #e2e8f0;
    font-size: 0.95rem;
    font-weight: 700;
}

.sidebar-nav-heading {
    color: #ffffff;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0.25rem 0.35rem 0.5rem 0.35rem;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    width: 100%;
    text-align: left;
    background: transparent;
    color: #ffffff;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 0.55rem 0.9rem;
    margin-bottom: 0.3rem;
    font-weight: 600;
    font-size: 0.92rem;
    transition: background-color 0.16s ease, color 0.16s ease,
        border-color 0.16s ease, transform 0.16s ease;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(59, 130, 246, 0.15);
    color: #f8fafc;
    border: 1px solid rgba(59, 130, 246, 0.35);
    transform: translateX(2px);
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:focus {
    box-shadow: none;
}

.sidebar-active-marker > div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #ffffff;
    border: 1px solid rgba(96, 165, 250, 0.55);
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
}
.sidebar-active-marker > div[data-testid="stButton"] > button:hover {
    transform: none;
}

.sidebar-footer {
    margin-top: 1.5rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.10);
    color: #ffffff;
    font-size: 0.72rem;
    text-align: center;
}
</style>
"""


# --------------------------------------------------------------------------
# Session State
# --------------------------------------------------------------------------

def _initialize_navigation_state() -> None:
    """Ensure the currently selected navigation item is tracked in state."""
    if NAV_STATE_KEY not in st.session_state:
        st.session_state[NAV_STATE_KEY] = DEFAULT_MENU_ITEM


# --------------------------------------------------------------------------
# Rendering Helpers
# --------------------------------------------------------------------------

def _render_brand() -> None:
    """Render the sidebar brand header with the company logo."""
    st.markdown('<div class="sidebar-brand">', unsafe_allow_html=True)
    render_brand_logo(width=42, align="flex-start")
    st.markdown(
        """
        <div class="sidebar-brand-text">
            <div class="sidebar-brand-title">Insurance AI Copilot</div>
            <div class="sidebar-brand-subtitle">Enterprise CRM Suite</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_user_info() -> None:
    """Render the current user's identity, if logged in."""
    username = st.session_state.get("username", "")
    logged_in = st.session_state.get("logged_in", False)

    if logged_in and username:
        st.markdown(
            f"""
            <div class="sidebar-user">
                <div class="sidebar-user-label">Signed in as</div>
                <div class="sidebar-user-name">{username}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_menu() -> str:
    """
    Render the navigation menu buttons and update the active selection.

    Returns:
        The currently selected menu item.
    """
    st.markdown('<div class="sidebar-nav-heading">Navigation</div>', unsafe_allow_html=True)

    for item in MENU_ITEMS:
        is_active = st.session_state[NAV_STATE_KEY] == item
        wrapper_class = "sidebar-active-marker" if is_active else "sidebar-inactive-marker"

        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        clicked = st.button(item, key=f"nav_{item}", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if clicked:
            st.session_state[NAV_STATE_KEY] = item

    return st.session_state[NAV_STATE_KEY]


def _render_footer() -> None:
    """Render the sidebar footer."""
    st.markdown(
        """
        <div class="sidebar-footer">
            Developed using Python + Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Public Component API
# --------------------------------------------------------------------------

def render_sidebar() -> str:
    """
    Render the enterprise sidebar navigation component.

    Returns:
        The label of the currently selected menu item
        (e.g. "🏠 Dashboard", "🚪 Logout").
    """
    _initialize_navigation_state()

    # Guarantees the same background/fonts/logo are available even if
    # this is the first component rendered on a given page.
    apply_global_theme()

    with st.sidebar:
        st.markdown(SIDEBAR_STYLE, unsafe_allow_html=True)
        _render_brand()
        _render_user_info()
        selected_page = _render_menu()
        _render_footer()

    return selected_page