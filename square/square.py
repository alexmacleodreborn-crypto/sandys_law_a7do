from square.repetition import RepetitionTracker

class Square:
    """
    Collapses repeated sensory packets into proto-structure.
    """

    def __init__(self):
        self.repetition = RepetitionTracker()

    def observe_packets(self, packets: list[dict]):
        for p in packets:
            # key is intentionally crude
            key = f"{p['channel']}:{p.get('region', 'global')}"
            self.repetition.observe(key)

    def snapshot(self):
        return self.repetition.snapshot()