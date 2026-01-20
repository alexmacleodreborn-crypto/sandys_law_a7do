# tests/test_frames.py

from frames.frame import Frame
from frames.fragment import Fragment


def test_frame_accepts_fragments():
    frame = Frame()
    frag = Fragment(kind="test", payload={})
    frame.add(frag)
    assert len(frame.fragments) == 1
