# sandys_law_a7do/interfaces/dashboard/streamlit_app.py

import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional

# =====================================================
# CORE DATA STRUCTURES (INLINE SAFE)
# =====================================================

@dataclass
class Fragment:
    domain: str
    action: str
    payload: dict


@dataclass
class Frame:
    domain: str
    label: str
    fragments: List[Fragment] = field(default_factory=list)

    def add(self, fragment: Fragment):
        self.fragments.append(fragment)


class FrameStore:
    def __init__(self):
        self.active: Optional[Frame] = None

    def open(self, frame: Frame):
        if self.active:
            raise RuntimeError("Frame already active")
        self.active = frame

    def add_fragment(self, fragment: Fragment):
        if not self.active:
            raise RuntimeError("No active frame")
        self.active.add(fragment)

    def close(self) -> Optional[Frame]:
        frame = self.active
        self.active = None
        return frame


class Ledger:
    def __init__(self):
        self.frames: List[Frame] = []

    def record(self, frame: Frame):
        self.frames.append(frame)


# =====================================================
# SESSION STATE INIT
# =====================================================

if "frame_store" not in st.session_state:
    st.session_state.frame_store = FrameStore()

if "ledger" not in st.session_state:
    st.session_state.ledger = Ledger()


fs = st.session_state.frame_store
ledger = st.session_state.ledger

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="A7DO — Cognitive Frame Dashboard",
    layout="wide"
)

st.title("🧠 A7DO Cognitive World")
st.caption("Explicit Frames • Episodic Cognition • No-Time Processing")

# =====================================================
# FRAME CONTROLS
# =====================================================

st.subheader("🎛️ Frame Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start Frame"):
        try:
            fs.open(Frame(domain="world", label="dashboard_interaction"))
        except RuntimeError as e:
            st.error(str(e))

with col2:
    if st.button("⏹️ End Frame"):
        frame = fs.close()
        if frame:
            ledger.record(frame)

with col3:
    if fs.active:
        st.success("Frame ACTIVE")
    else:
        st.warning("No active frame")

# =====================================================
# WORLD INTERACTIONS
# =====================================================

st.subheader("🌍 World Interaction")

colA, colB = st.columns(2)

with colA:
    if st.button("⬆️ Contact Top"):
        try:
            fs.add_fragment(
                Fragment("world", "contact", {"region": "top"})
            )
        except RuntimeError as e:
            st.error(str(e))

with colB:
    if st.button("⬇️ Contact Bottom"):
        try:
            fs.add_fragment(
                Fragment("world", "contact", {"region": "bottom"})
            )
        except RuntimeError as e:
            st.error(str(e))

# =====================================================
# FRAME INSPECTOR (LIVE VISUALISATION)
# =====================================================

st.divider()
st.subheader("🧠 Frame Inspector")

# --- Active Frame ---
st.markdown("### 🔴 Active Frame")

if fs.active:
    st.json({
        "domain": fs.active.domain,
        "label": fs.active.label,
        "fragment_count": len(fs.active.fragments)
    })
else:
    st.caption("No active frame")

# --- Fragment Stream ---
st.markdown("### 📡 Fragment Stream")

if fs.active and fs.active.fragments:
    for frag in fs.active.fragments:
        st.code(f"{frag.domain} :: {frag.action} :: {frag.payload}")
else:
    st.caption("No fragments recorded")

# =====================================================
# EPISODIC MEMORY TIMELINE
# =====================================================

st.divider()
st.subheader("🧾 Episodic Memory (Ledger)")

if ledger.frames:
    for i, frame in enumerate(ledger.frames):
        with st.expander(f"Frame {i+1} — {frame.domain} / {frame.label}"):
            for frag in frame.fragments:
                st.write(f"- {frag.action} | {frag.payload}")
else:
    st.caption("No completed frames yet")

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption(
    "A7DO operates on explicit cognitive frames. "
    "Fragments cannot exist without experience."
)
