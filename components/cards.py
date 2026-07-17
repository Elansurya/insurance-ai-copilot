"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Component: Info Cards
"""

from __future__ import annotations

import streamlit as st

from components.theme import apply_global_theme

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

INFO_CARD_STYLE: str = """
<style>
.info-card {
    position: relative;
    background: rgba(17, 24, 39, 0.85);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease,
        background-color 0.2s ease;
    width: 100%;
    box-sizing: border-box;
}
.info-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 32px rgba(0, 0, 0, 0.45);
    background: rgba(17, 24, 39, 0.95);
}
.info-card-icon {
    font-size: 1.75rem;
    line-height: 1;
    margin-bottom: 0.6rem;
}
.info-card-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.3rem;
}
.info-card-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 0.4rem;
}
.info-card-description {
    font-size: 0.88rem;
    color: #ffffff;
    line-height: 1.45;
}

@media (max-width: 640px) {
    .info-card {
        padding: 1.1rem 1.25rem;
    }
    .info-card-value {
        font-size: 1.5rem;
    }
}
</style>
"""

_styles_injected: bool = False


# --------------------------------------------------------------------------
# Internal Helpers
# --------------------------------------------------------------------------

def _ensure_styles_injected() -> None:
    """Inject the info card CSS styling into the page, once per session."""
    global _styles_injected
    if not _styles_injected:
        apply_global_theme()
        st.markdown(INFO_CARD_STYLE, unsafe_allow_html=True)
        _styles_injected = True


# --------------------------------------------------------------------------
# Public Component API
# --------------------------------------------------------------------------

def info_card(title: str, value: str, icon: str, description: str) -> None:
    """
    Render a reusable enterprise glassmorphism info card.

    Args:
        title: The short label displayed at the top of the card.
        value: The primary value or headline metric to highlight.
        icon: An emoji or short glyph representing the card's context.
        description: Supporting descriptive text shown beneath the value.
    """
    _ensure_styles_injected()

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-card-icon">{icon}</div>
            <div class="info-card-title">{title}</div>
            <div class="info-card-value">{value}</div>
            <div class="info-card-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )