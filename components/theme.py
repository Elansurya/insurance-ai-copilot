"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Component: Global Theme (shared styling used across all pages)
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

# This file lives at <project_root>/components/theme.py, so its parent's
# parent is the project root. Anchoring to __file__ (rather than the
# current working directory) makes asset loading work regardless of
# where `streamlit run` is launched from, exactly like app.py does.
BASE_DIR: Path = Path(__file__).resolve().parent.parent
STYLE_SHEET_PATH: Path = BASE_DIR / "assets" / "style.css"
BACKGROUND_IMAGE_PATH: Path = BASE_DIR / "assets" / "background.png"
LOGO_PATH: Path = BASE_DIR / "assets" / "logo.png"


# --------------------------------------------------------------------------
# Asset Loading Helpers
# --------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _encode_file_base64(file_path: str) -> str | None:
    """
    Read a binary file and return its base64-encoded contents.

    Cached so the disk read + encode only happens once per file, even
    though this may run on every page load/rerun.

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


# --------------------------------------------------------------------------
# Styling Steps
# --------------------------------------------------------------------------

def _load_css(css_path: Path = STYLE_SHEET_PATH) -> None:
    """Safely load and inject the external CSS stylesheet if it exists."""
    if not css_path.exists():
        return

    try:
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except OSError:
        # Fail silently to avoid breaking the application on style load errors.
        pass


def _apply_background(image_path: Path = BACKGROUND_IMAGE_PATH) -> None:
    """
    Apply the enterprise background image to the entire Streamlit app
    using a base64-encoded data URI (relative/static URLs are not
    reliably servable from within injected CSS in Streamlit).

    If the image is missing, this silently no-ops and the app falls
    back to whatever base background is defined in style.css.
    """
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


def _apply_logo(logo_path: Path = LOGO_PATH) -> None:
    """
    Display the enterprise logo in the sidebar/header using Streamlit's
    native st.logo API. Falls back silently if the logo file is not
    present or unreadable, so the app never breaks on a missing asset.
    """
    if not logo_path.exists():
        return

    try:
        st.logo(str(logo_path), size="large")
    except Exception:
        # st.logo can raise if the image is unreadable/corrupted; never
        # let a branding asset break the app.
        pass


# --------------------------------------------------------------------------
# Public Component API
# --------------------------------------------------------------------------

def apply_global_theme() -> None:
    """
    Apply the shared enterprise dark theme (stylesheet, background image,
    logo) to the current page.

    This is the single reusable entry point every page and every styled
    component should call near the top of its render function — mirroring
    exactly what app.py's own apply_theme() does for the main entry point,
    so styling stays perfectly consistent across the whole multipage app.

    Safe to call multiple times per run; each underlying step degrades
    gracefully (no-ops) if its asset is missing, so this can never raise
    or break page rendering.
    """
    _load_css()
    _apply_background()
    _apply_logo()