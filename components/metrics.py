"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Component: KPI Metric Cards
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from components.theme import apply_global_theme

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

METRIC_CARD_STYLE: str = """
<style>
.metric-card {
    position: relative;
    background: rgba(17, 24, 39, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    overflow: hidden;
}
.metric-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
    background: var(--accent-color);
}
.metric-card-icon {
    font-size: 1.6rem;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.metric-card-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.35rem;
}
.metric-card-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
}
</style>
"""


# --------------------------------------------------------------------------
# Data Model
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class MetricCardConfig:
    """Configuration for a single KPI metric card."""

    icon: str
    title: str
    value: int
    accent_color: str


# --------------------------------------------------------------------------
# Rendering Helpers
# --------------------------------------------------------------------------

def _inject_styles() -> None:
    """Inject the metric card CSS styling into the page."""
    apply_global_theme()
    st.markdown(METRIC_CARD_STYLE, unsafe_allow_html=True)


def _render_metric_card(config: MetricCardConfig) -> None:
    """
    Render a single KPI metric card.

    Args:
        config: The metric card configuration to render.
    """
    st.markdown(
        f"""
        <div class="metric-card" style="--accent-color: {config.accent_color};">
            <div class="metric-card-icon">{config.icon}</div>
            <div class="metric-card-title">{config.title}</div>
            <div class="metric-card-value">{config.value:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Public Component API
# --------------------------------------------------------------------------

def display_metrics(
    total_customers: int,
    active_policies: int,
    expiring_policies: int,
    pending_claims: int,
) -> None:
    """
    Render four modern, responsive KPI metric cards summarizing
    core Insurance CRM statistics.

    Args:
        total_customers: Total number of customers on record.
        active_policies: Number of currently active policies.
        expiring_policies: Number of policies expiring soon.
        pending_claims: Number of claims currently pending review.
    """
    _inject_styles()

    card_configs: list[MetricCardConfig] = [
        MetricCardConfig(
            icon="👥",
            title="Total Customers",
            value=total_customers,
            accent_color="#2563eb",
        ),
        MetricCardConfig(
            icon="📄",
            title="Active Policies",
            value=active_policies,
            accent_color="#16a34a",
        ),
        MetricCardConfig(
            icon="⏳",
            title="Policies Expiring Soon",
            value=expiring_policies,
            accent_color="#d97706",
        ),
        MetricCardConfig(
            icon="🧾",
            title="Pending Claims",
            value=pending_claims,
            accent_color="#dc2626",
        ),
    ]

    columns = st.columns(len(card_configs))

    for column, config in zip(columns, card_configs):
        with column:
            _render_metric_card(config)