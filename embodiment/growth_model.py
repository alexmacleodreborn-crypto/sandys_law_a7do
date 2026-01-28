class EmbodimentGrowthModel:
    """
    Pure structural growth model.
    No time ownership.
    No side effects.
    """

    def compute(
        self,
        *,
        tick: int,
        stability: float,
        exposure_time: float,
        min_exposure: float,
    ) -> dict:
        """
        Returns normalized growth signals [0..1].
        """

        body_growth = min(1.0, exposure_time / min_exposure)

        limb_growth = min(
            1.0,
            max(0.0, (exposure_time - 20.0) / min_exposure),
        )

        brain_coherence = stability * min(1.0, tick / 100.0)

        return {
            "body_growth": body_growth,
            "limb_growth": limb_growth,
            "brain_coherence": brain_coherence,
        }