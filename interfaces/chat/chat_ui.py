"""
A7DO Chat Interface — OBSERVER ONLY (LOCKED)

Purpose:
- Provide a conversational observational interface to A7DO
- Read-only access via snapshot()
- NO state mutation
- NO cognition
- NO learning
- NO memory writes

Chat is an INTERFACE, not an agent.
"""

from __future__ import annotations

import streamlit as st
from typing import Callable, Dict, Any


# ============================================================
# CHAT RENDERER
# ============================================================

def render_chat(snapshot: Callable[[], Dict[str, Any]]) -> None:
    """
    Render a read-only conversational interface.

    snapshot(): () -> dict
    Must be the SAME snapshot used by the dashboard.
    """

    st.subheader("💬 A7DO — Observational Chat")

    # ---------------------------------
    # SESSION CHAT HISTORY (LOCAL UI ONLY)
    # ---------------------------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ---------------------------------
    # USER INPUT
    # ---------------------------------
    user_input = st.text_input(
        "Ask A7DO (observation only):",
        placeholder="What is your current state?",
        key="a7do_chat_input",
    )

    if user_input:
        # Store user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        # Generate response (OBSERVATIONAL)
        response = _generate_observational_response(
            user_input=user_input,
            snapshot=snapshot,
        )

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

    # ---------------------------------
    # DISPLAY CHAT
    # ---------------------------------
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**A7DO:** {msg['content']}")


# ============================================================
# RESPONSE GENERATION (READ-ONLY)
# ============================================================

def _generate_observational_response(
    *,
    user_input: str,
    snapshot: Callable[[], Dict[str, Any]],
) -> str:
    """
    Convert a user query into an observational response.

    This function:
    - Reads snapshot only
    - Never mutates state
    - Never infers beliefs
    - Never claims intent or desire
    """

    data = snapshot()

    ticks = data.get("ticks", 0)
    metrics = data.get("metrics", {})
    gates = data.get("gates", {})
    memory_count = data.get("memory_count", 0)
    prediction_error = data.get("prediction_error", 0.0)

    text = user_input.lower()

    # ---------------------------------
    # SIMPLE OBSERVATIONAL INTENTS
    # ---------------------------------
    if "state" in text or "status" in text:
        return (
            f"I am currently at tick {ticks}. "
            f"Stability is {metrics.get('Stability', 0.0):.2f}, "
            f"coherence is {metrics.get('Coherence', 0.0):.2f}, "
            f"fragmentation is {metrics.get('Z', 0.0):.2f}."
        )

    if "memory" in text:
        return f"I have {memory_count} recorded memory traces."

    if "gate" in text:
        if not gates:
            return "No gate information is currently available."
        lines = []
        for name, g in gates.items():
            lines.append(
                f"{name}: state={g.get('state')}, open={g.get('open')}"
            )
        return "Current gate states:\n" + "\n".join(lines)

    if "prediction" in text or "error" in text:
        return f"My current prediction error signal is {prediction_error:.3f}."

    if "who are you" in text or "what are you" in text:
        return (
            "I am A7DO. I do not have beliefs or intentions. "
            "I expose my internal structural state through observation."
        )

    # ---------------------------------
    # DEFAULT RESPONSE
    # ---------------------------------
    return (
        "I can report my current structural state, memory count, "
        "gate conditions, and stability. "
        "I do not decide or act through this interface."
    )