import streamlit as st
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional, Dict

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
# PERSISTENT STATE + Σ
# =====================================================

@dataclass
class PersistentState:
    expected_fragments: float = 0.0
    pressure: float = 0.0      # Z
    sigma: float = 0.0         # Σ
    last_pressure: float = 0.0
    region_bias: Dict[str, float] = field(
        default_factory=lambda: {"top": 0.0, "bottom": 0.0}
    )
    alpha: float = 0.3         # expectation smoothing
    sigma_gain: float = 0.5
    sigma_decay: float = 0.9


    def update_from_frame(self, frame: Frame):
        n = len(frame.fragments)

        # --- expectation (EMA) ---
        if self.expected_fragments == 0:
            self.expected_fragments = n
        else:
            self.expected_fragments = (
                self.alpha * n
                + (1 - self.alpha) * self.expected_fragments
            )

        # --- pressure (Z) ---
        self.last_pressure = self.pressure
        self.pressure = n - self.expected_fragments

        # --- Σ (entropy release) ---
        if abs(self.pressure) < abs(self.last_pressure):
            # surprise reduced → entropy released
            delta = abs(self.last_pressure) - abs(self.pressure)
            self.sigma += self.sigma_gain * delta

        # Σ always decays (no free entropy)
        self.sigma *= self.sigma_decay

        # Σ relaxes pressure
        self.pressure *= (1 - min(self.sigma, 0.8))

        # --- slow region bias ---
        for frag in frame.fragments:
            if frag.action == "contact":
                region = frag.payload.get("region")
                if region in self.region_bias:
                    self.region_bias[region] += 0.2

        for r in self.region_bias:
            self.region_bias[r] *= 0.95


# =====================================================
# SESSION STATE
# =====================================================

if "frame_store" not in st.session_state:
    st.session_state.frame_store = FrameStore()

if "ledger" not in st.session_state:
    st.session_state.ledger = Ledger()

if "persistent" not in st.session_state:
    st.session_state.persistent = PersistentState()

fs = st.session_state.frame_store
ledger = st.session_state.ledger
ps = st.session_state.persistent

# =====================================================
# PAGE
# =====================================================

st.set_page_config(page_title="A7DO Cognitive World", layout="wide")
st.title("🧠 A7DO Cognitive Dashboard")
st.caption("Explicit Frames • Persistent State • Z–Σ Dynamics")

# =====================================================
# FRAME CONTROLS
# =====================================================

st.subheader("🎛️ Frame Controls")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("▶️ Start Frame", key="start_frame"):
        try:
            fs.open(Frame(domain="world", label="interaction"))
        except RuntimeError as e:
            st.error(str(e))

with c2:
    if st.button("⏹️ End Frame", key="end_frame"):
        frame = fs.close()
        if frame:
            ledger.record(frame)
            ps.update_from_frame(frame)

with c3:
    st.write("ACTIVE FRAME:", "✅" if fs.active else "❌")

# =====================================================
# WORLD INTERACTION
# =====================================================

st.subheader("🌍 World Interaction")

w1, w2 = st.columns(2)

with w1:
    if st.button("⬆️ Contact Top", key="contact_top"):
        try:
            fs.add_fragment(Fragment("world", "contact", {"region": "top"}))
        except RuntimeError as e:
            st.error(str(e))

with w2:
    if st.button("⬇️ Contact Bottom", key="contact_bottom"):
        try:
            fs.add_fragment(Fragment("world", "contact", {"region": "bottom"}))
        except RuntimeError as e:
            st.error(str(e))

# =====================================================
# ACTIVE FRAME INSPECTOR
# =====================================================

st.divider()
st.subheader("🧠 Active Frame Inspector")

if fs.active:
    st.json({
        "fragments": len(fs.active.fragments),
        "expected": round(ps.expected_fragments, 2),
        "Z (pressure)": round(ps.pressure, 2),
        "Σ (entropy)": round(ps.sigma, 2)
    })
else:
    st.caption("No active frame")

# =====================================================
# COGNITIVE VISUALISATIONS
# =====================================================

st.divider()
st.subheader("📊 Z–Σ Dynamics")

if ledger.frames:

    frame_ids = list(range(1, len(ledger.frames) + 1))
    frag_counts = [len(f.fragments) for f in ledger.frames]

    # --- Z vs expectation ---
    fig1, ax1 = plt.subplots()
    ax1.plot(frame_ids, frag_counts, label="Fragments")
    ax1.axhline(ps.expected_fragments, linestyle="--", label="Expectation")
    ax1.set_title("Z: Pressure vs Expectation")
    ax1.legend()
    st.pyplot(fig1)

    # --- Σ ---
    fig2, ax2 = plt.subplots()
    ax2.bar(["Σ"], [ps.sigma])
    ax2.set_title("Entropy Release (Σ)")
    st.pyplot(fig2)

    # --- Bias ---
    fig3, ax3 = plt.subplots()
    ax3.bar(ps.region_bias.keys(), ps.region_bias.values())
    ax3.set_title("Persistent World Bias")
    st.pyplot(fig3)

else:
    st.caption("No completed frames yet")

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
    "Σ allows pressure to relax when surprise reduces. "
    "Z–Σ dynamics restore coherence without time."
)
