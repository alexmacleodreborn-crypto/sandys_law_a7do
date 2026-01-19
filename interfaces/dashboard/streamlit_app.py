import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional

# =====================================================
# CORE DATA STRUCTURES
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
# SESSION STATE
# =====================================================

if "frame_store" not in st.session_state:
    st.session_state.frame_store = FrameStore()

if "ledger" not in st.session_state:
    st.session_state.ledger = Ledger()

fs = st.session_state.frame_store
ledger = st.session_state.ledger

# =====================================================
# PAGE
# =====================================================

st.set_page_config(page_title="A7DO Cognitive World", layout="wide")
st.title("🧠 A7DO Cognitive Dashboard")
st.caption("Explicit Frames • Episodic Cognition • No Global Time")

# =====================================================
# FRAME CONTROLS
# =====================================================

st.subheader("🎛️ Frame Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start Frame", key="start_frame_btn"):
        try:
            fs.open(Frame(domain="world", label="interaction"))
        except RuntimeError as e:
            st.error(str(e))

with col2:
    if st.button("⏹️ End Frame", key="end_frame_btn"):
        frame = fs.close()
        if frame:
            ledger.record(frame)

with col3:
    st.write("ACTIVE FRAME:", "✅" if fs.active else "❌")

# =====================================================
# WORLD INTERACTION
# =====================================================

st.subheader("🌍 World Interaction")

c1, c2 = st.columns(2)

with c1:
    if st.button("⬆️ Contact Top", key="contact_top_btn"):
        try:
            fs.add_fragment(
                Fragment("world", "contact", {"region": "top"})
            )
        except RuntimeError as e:
            st.error(str(e))

with c2:
    if st.button("⬇️ Contact Bottom", key="contact_bottom_btn"):
        try:
            fs.add_fragment(
                Fragment("world", "contact", {"region": "bottom"})
            )
        except RuntimeError as e:
            st.error(str(e))

# =====================================================
# FRAME INSPECTOR
# =====================================================

st.divider()
st.subheader("🧠 Active Frame Inspector")

if fs.active:
    st.json({
        "domain": fs.active.domain,
        "label": fs.active.label,
        "fragments": len(fs.active.fragments)
    })
else:
    st.caption("No active frame")

# =====================================================
# GRAPHS
# =====================================================

st.divider()
st.subheader("📊 Cognitive Visualisations")

if ledger.frames:

    frame_ids = list(range(1, len(ledger.frames) + 1))
    frag_counts = [len(f.fragments) for f in ledger.frames]

    # --- Graph 1: Fragments per Frame ---
    fig1, ax1 = plt.subplots()
    ax1.bar(frame_ids, frag_counts)
    ax1.set_title("Fragments per Frame (Perceptual Density)")
    ax1.set_xlabel("Frame")
    ax1.set_ylabel("Fragments")
    st.pyplot(fig1)

    # --- Graph 2: Contact Regions ---
    regions = {"top": 0, "bottom": 0}
    for frame in ledger.frames:
        for frag in frame.fragments:
            if frag.action == "contact":
                r = frag.payload.get("region")
                if r in regions:
                    regions[r] += 1

    fig2, ax2 = plt.subplots()
    ax2.bar(regions.keys(), regions.values())
    ax2.set_title("World Contact Regions")
    ax2.set_ylabel("Count")
    st.pyplot(fig2)

    # --- Graph 3: Cognitive Load (Proto-Z) ---
    fig3, ax3 = plt.subplots()
    ax3.plot(frame_ids, frag_counts, marker="o")
    ax3.set_title("Cognitive Load Across Frames (Proto-Z)")
    ax3.set_xlabel("Frame")
    ax3.set_ylabel("Load")
    st.pyplot(fig3)

else:
    st.caption("Graphs will appear once at least one frame is completed.")

# =====================================================
# EPISODIC MEMORY
# =====================================================

st.divider()
st.subheader("🧾 Episodic Memory")

for i, frame in enumerate(ledger.frames):
    with st.expander(f"Frame {i+1}"):
        for frag in frame.fragments:
            st.write(f"- {frag.action} | {frag.payload}")

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption(
    "A7DO enforces explicit experience frames. "
    "Fragments cannot exist without perception."
)
