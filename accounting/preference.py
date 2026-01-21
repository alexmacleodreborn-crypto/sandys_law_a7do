    def attention_field(self) -> Dict[str, float]:
        """
        Convert preferences into attention weights.

        Preference ∈ [-1, +1]
        Attention ∈ [0.5, 1.5]
        """
        field: Dict[str, float] = {}

        for k, v in self.store.prefs.items():
            field[k] = 1.0 + 0.5 * float(v)

        return field