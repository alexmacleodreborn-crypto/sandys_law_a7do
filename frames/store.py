class FrameStore:
    def __init__(self):
        self.active = None
        self._buffer = []

    # -------------------------------------------------
    # SENSORY INGEST (TRANSPORT PACKETS ONLY)
    # -------------------------------------------------

    def observe_sensory(self, packets: list[dict]) -> None:
        """
        Observe pre-semantic sensory packets.

        Packets are dictionaries with:
        - channel
        - region
        - value
        - confidence
        - repetition
        """

        for p in packets:
            confidence = p.get("confidence", 0.0)
            if confidence < 0.4:
                continue  # too noisy, ignore

            self._buffer.append({
                "key": f"{p['channel']}:{p.get('region', 'global')}",
                "strength": p.get("value", 0.0),
                "confidence": confidence,
                "repetition": p.get("repetition", 0.0),
            })

        # Very early frame emergence (still pre-meaning)
        if self._buffer:
            self.active = self._buffer[-1]["key"]