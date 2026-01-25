# interfaces/dashboard/prebirth_ui.py

import streamlit as st


def render_prebirth_panel(
    *,
    womb_state: dict,
    birth_readiness: dict,
    birth_status: str,
) -> None:
    """
    Read-only visualization of prebirth and birth state.
    """

    st.subheader("Prebirth / Birth Monitor")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Exposure Time",
        round(birth_readiness.get("exposure_time", 0.0), 2),
    )

    c2.metric(
        "Avg Stability",
        round(birth_readiness.get("stability_score", 0.0), 3),
    )

    c3.metric(
        "Birth Status",
        birth_status,
    )

    st.markdown("### Womb Signals")
    st.json(
        {
            "heartbeat_rate": womb_state.get("heartbeat_rate"),
            "ambient_load": womb_state.get("ambient_load"),
            "womb_active": womb_state.get("womb_active"),
        }
    )

    st.markdown("### Birth Evaluation")
    st.json(birth_readiness)