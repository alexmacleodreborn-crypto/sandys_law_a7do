class GateManager:
    def __init__(self):
        self.perception = PerceptionGate()
        self.consolidation = ConsolidationGate()
        self.education = EducationGate()
        self.role = RoleGate()

    def evaluate(self, *, coherence, fragmentation, block_rate, load):
        return {
            "perception": self.perception.evaluate(
                block_rate=block_rate,
                fragmentation=fragmentation,