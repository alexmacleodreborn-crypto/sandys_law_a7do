class Gate:
    def is_open(self) -> bool:
        """Structural availability, not permission"""
    
    def admit(self, payload) -> bool:
        """Structural admissibility check"""
    
    def transmit(self, payload):
        """Return transformed payload or None"""
