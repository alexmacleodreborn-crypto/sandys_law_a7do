"""
A7DO Chat Interface — Phase 0 (OBSERVATION ONLY)

This UI:
- exposes system state conversationally
- does NOT modify system state
- does NOT write memory
- does NOT open gates
- does NOT trigger embodiment

Language is an INTERFACE, not cognition.
"""

from __future__ import annotations

import streamlit as st
from typing import Dict, Any


# ---------------------------------------------------------
# Safe language adapter (minimal, non-semantic)
# ---------------------------------------------------------

class LanguageAdapter:
    """
    Extremely conservative language interface.

    Converts user text into:
    - observation requests
    - status queries

    NEVER:
    - issues commands
    - alters state
    - injects beliefs
    """

    @staticmethod
    def parse(text: str) -> Dict[str, Any]:
        t = text.lower().strip()

        if any(k in t for k in ("status", "state", "how are you", "what's happening")):
            return {"intent": "status"}

        if any(k in t for k in ("memory", "remember", "learned")):
            return {"intent": "memory"}

        if any(k in t for k in ("gate", "gates")):
            return {"intent": "gates"}

        if any(k in t for k in ("embodiment", "body", "self")):
            return {"intent": "embodiment"}

        return {"intent": "unknown"}

    @staticmethod
    def respond(intent: Dict[str, Any], state: dict) -> str:
        i = intent.get("intent")

        if i == "status":
            return (
                f"Ticks: {state.get('ticks')}\n"
                f"Active frame: {bool(state.get('active_frame'))}\n"
                f"Stability: {state['metrics'].get('Stability'):.3f}"
            )

        if i == "memory":
            return f"Memory traces recorded: {state.get('memory_count')}"

        if i == "gates":
            gates = state.get("gates", {})
            if not gates:
                return "No gate activity recorded."
            return "\n".join(
                f"{name}: {info.get('state')} (score={info.get('score')})"
                for name, info in gates.items()
            )

        if i == "embodiment":
            return (
                "Embodiment exists as a ledger of invariants.\n"
                "No embodiment entries are exposed through chat."
            )

        return (
            "I can describe my current state.\n"
            "I cannot take instructions or form beliefs."
        )


# ---------------------------------------------------------
# Streamlit Chat UI
# ---------------------------------------------------------

def render_chat(snapshot_callable):
    """
    snapshot_callable: () -> dict
    """

    st.subheader("🧠 A7DO — Observational Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display history
    for speaker, msg in st.session_state.chat_history:
        with st.chat_message(speaker):
            st.markdown(msg)

    # Input
    user_input = st.chat_input("Ask about system state…")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))

        # SAFE SNAPSHOT ONLY
        state_view = snapshot_callable()

        intent = LanguageAdapter.parse(user_input)
        reply = LanguageAdapter.respond(intent, state_view)

        st.session_state.chat_history.append(("assistant", reply))

        st.experimental_rerun()