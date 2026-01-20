# streamlit_app.py
"""
A7DO + Sandy's Law
Streamlit Interface (FINAL)
"""

import streamlit as st


def run():
    # Lazy imports (Streamlit-safe)
    from bootstrap import (
        build_system,
        inject_demo_frame,
        add_fragment,
        close_frame,
        tick_system,
    )

    # --------------------------------------------------
    # PERSIST SYSTEM ACROSS RERUNS
    # --------------------------------------------------
    if "system_bundle" not in st.session_state:
        system, snapshot, state = build_system()
        st.session_state.system_bundle = {
            "system": system,
            "snapshot": snapshot,
            "state": state,
        }

    bundle = st.session_state.system_bundle
    snapshot = bundle["snapshot"]
    state = bundle["state"]

    # --------------------------------------------------
    # PAGE SETUP
    # --------------------------------------------------
    st.set_page_config(page_title="A7DO Dashboard", layout="wide")
    st.title("A7DO — Sandy’s Law System")

    # --------------------------------------------------
    # SIDEBAR CONTROLS
    # --------------------------------------------------
    st.sidebar.header("Frame Controls")

    if st.sidebar.button("▶ Open Demo Frame"):
        inject_demo_frame(state)

    if st.sidebar.button("➕ Add Fragment"):
        try:
            add_fragment(state)
        except RuntimeError as e:
            st.sidebar.warning(str(e))

    if st.sidebar.button("⏹ Close Frame"):
        close_frame(state)

    st.sidebar.divider()

    if st.sidebar.button("⏱ Tick"):
        tick_system(state)

    # --------------------------------------------------
    # SNAPSHOT VIEW
    # --------------------------------------------------
    data = snapshot()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("System State")
        st.json(
            {
                "roles": data["roles"],
                "ticks": data["ticks"],
                "active_frame": (
                    {
                        "domain": data["active_frame"].domain,
                        "label": data["active_frame"].label,
                        "fragments": len(data["active_frame"].fragments),
                    }
                    if data["active_frame"]
                    else None
                ),
            }
        )

    with col2:
        st.subheader("Regulation")
        st.json(data["regulation"])

    # --------------------------------------------------
    # METRICS
    # --------------------------------------------------
    st.subheader("Metrics")
    for k, v in data["metrics"].items():
        st.progress(min(1.0, float(v)))
        st.caption(f"{k}: {float(v):.3f}")

    # --------------------------------------------------
    # FRAME INSPECTION
    # --------------------------------------------------
    st.subheader("Frames")

    if data["active_frame"]:
        with st.expander("Active Frame"):
            st.write(
                {
                    "domain": data["active_frame"].domain,
                    "label": data["active_frame"].label,
                    "fragments": [
                        f.kind for f in data["active_frame"].fragments
                    ],
                }
            )

    if data["last_frame"]:
        with st.expander("Last Closed Frame"):
            st.write(
                {
                    "domain": data["last_frame"].domain,
                    "label": data["last_frame"].label,
                    "fragments": [
                        f.kind for f in data["last_frame"].fragments
                    ],
                }
            )


if __name__ == "__main__":
    run()