"""
Insurance AI Copilot
Enterprise Insurance CRM Dashboard

Component: Chatbot UI (GPT-style)
"""

from __future__ import annotations

import streamlit as st

from components.theme import apply_global_theme

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

DEFAULT_SESSION_KEY: str = "chatbot_history"
DEFAULT_USER_AVATAR: str = "🧑"
DEFAULT_AI_AVATAR: str = "🤖"

CHATBOT_STYLE: str = """
<style>
.chatbot-container {
    background: rgba(15, 23, 42, 0.55);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
}

.chatbot-scroll-area {
    max-height: 540px;
    overflow-y: auto;
    padding-right: 0.4rem;
}
.chatbot-scroll-area::-webkit-scrollbar {
    width: 6px;
}
.chatbot-scroll-area::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.35);
    border-radius: 999px;
}

.chat-row {
    display: flex;
    align-items: flex-end;
    gap: 0.6rem;
    margin: 0.55rem 0;
}
.chat-row-user {
    flex-direction: row-reverse;
}

.chat-avatar {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.14);
}
.chat-avatar-user {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    border: 1px solid rgba(96, 165, 250, 0.5);
}
.chat-avatar-ai {
    background: linear-gradient(135deg, #0ea5e9, #0369a1);
    border: 1px solid rgba(56, 189, 248, 0.5);
}

.chat-bubble {
    max-width: 78%;
    padding: 0.75rem 1rem;
    border-radius: 16px;
    font-size: 0.95rem;
    line-height: 1.55;
    white-space: pre-wrap;
    word-wrap: break-word;
}
.chat-bubble-user {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #ffffff;
    border-radius: 16px 16px 4px 16px;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
}
.chat-bubble-ai {
    background: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 16px 16px 16px 4px;
}
.chat-bubble-ai code {
    background: rgba(0, 0, 0, 0.35);
    padding: 0.1rem 0.3rem;
    border-radius: 4px;
}

.chat-typing-dots {
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.chat-typing-dots span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #94a3b8;
    animation: chat-typing-bounce 1.2s infinite ease-in-out;
}
.chat-typing-dots span:nth-child(2) {
    animation-delay: 0.15s;
}
.chat-typing-dots span:nth-child(3) {
    animation-delay: 0.3s;
}
@keyframes chat-typing-bounce {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.5;
    }
    30% {
        transform: translateY(-5px);
        opacity: 1;
    }
}

@media (max-width: 640px) {
    .chat-bubble {
        max-width: 88%;
    }
}
</style>
"""

_styles_injected: bool = False


# --------------------------------------------------------------------------
# Internal Helpers
# --------------------------------------------------------------------------

def _ensure_styles_injected() -> None:
    """Inject the chatbot CSS styling into the page, once per session."""
    global _styles_injected
    if not _styles_injected:
        apply_global_theme()
        st.markdown(CHATBOT_STYLE, unsafe_allow_html=True)
        _styles_injected = True


def _ensure_history_initialized(session_key: str) -> None:
    """Ensure the chat history list exists in session state."""
    if session_key not in st.session_state:
        st.session_state[session_key] = []


def _render_message_row(role: str, content: str, avatar: str) -> None:
    """
    Render a single chat message row with avatar and bubble.

    Args:
        role: Either "user" or "ai".
        content: The Markdown-capable message text.
        avatar: The emoji/glyph avatar for this message.
    """
    row_class = "chat-row-user" if role == "user" else "chat-row-ai"
    bubble_class = "chat-bubble-user" if role == "user" else "chat-bubble-ai"
    avatar_class = "chat-avatar-user" if role == "user" else "chat-avatar-ai"

    st.markdown(
        f"""
        <div class="chat-row {row_class}">
            <div class="chat-avatar {avatar_class}">{avatar}</div>
            <div class="chat-bubble {bubble_class}">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Public Component API
# --------------------------------------------------------------------------

def display_user_message(
    message: str,
    avatar: str = DEFAULT_USER_AVATAR,
    session_key: str = DEFAULT_SESSION_KEY,
) -> None:
    """
    Append a user message to chat history and render it immediately.

    Args:
        message: The Markdown-capable message text from the user.
        avatar: The emoji/glyph avatar to display for the user.
        session_key: The session state key used to store chat history.
    """
    _ensure_styles_injected()
    _ensure_history_initialized(session_key)

    st.session_state[session_key].append(
        {"role": "user", "content": message, "avatar": avatar}
    )
    _render_message_row("user", message, avatar)


def display_ai_message(
    message: str,
    avatar: str = DEFAULT_AI_AVATAR,
    session_key: str = DEFAULT_SESSION_KEY,
) -> None:
    """
    Append an AI message to chat history and render it immediately.

    Args:
        message: The Markdown-capable message text from the assistant.
        avatar: The emoji/glyph avatar to display for the assistant.
        session_key: The session state key used to store chat history.
    """
    _ensure_styles_injected()
    _ensure_history_initialized(session_key)

    st.session_state[session_key].append(
        {"role": "ai", "content": message, "avatar": avatar}
    )
    _render_message_row("ai", message, avatar)


def display_typing_indicator(avatar: str = DEFAULT_AI_AVATAR) -> None:
    """
    Render an animated typing indicator bubble for the assistant.

    This message is ephemeral and is not persisted to chat history.
    Wrap the call in a placeholder (e.g. ``st.empty()``) if it needs
    to be cleared once the actual response is ready.

    Args:
        avatar: The emoji/glyph avatar to display alongside the indicator.
    """
    _ensure_styles_injected()

    st.markdown(
        f"""
        <div class="chat-row chat-row-ai">
            <div class="chat-avatar chat-avatar-ai">{avatar}</div>
            <div class="chat-bubble chat-bubble-ai">
                <span class="chat-typing-dots">
                    <span></span><span></span><span></span>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_chat(session_key: str = DEFAULT_SESSION_KEY) -> None:
    """
    Render the full, scrollable chat history in a dark enterprise
    themed container.

    Args:
        session_key: The session state key used to store chat history.
    """
    _ensure_styles_injected()
    _ensure_history_initialized(session_key)

    st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
    st.markdown('<div class="chatbot-scroll-area">', unsafe_allow_html=True)

    history: list[dict[str, str]] = st.session_state[session_key]

    if not history:
        st.markdown(
            '<div class="chat-bubble chat-bubble-ai">'
            "No messages yet. Start the conversation below."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        for entry in history:
            role = entry.get("role", "ai")
            content = entry.get("content", "")
            avatar = entry.get(
                "avatar",
                DEFAULT_USER_AVATAR if role == "user" else DEFAULT_AI_AVATAR,
            )
            _render_message_row(role, content, avatar)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)