from __future__ import annotations

from sandys_law_a7do.language.intent import LanguageIntent
from sandys_law_a7do.language.utterance import Utterance


class LanguageAdapter:
    """
    Translates between English and structural signals.

    This layer:
    - does not think
    - does not remember
    - does not decide
    """

    # --------------------------------------------------
    # INPUT: English → Intent
    # --------------------------------------------------

    def parse(self, text: str) -> LanguageIntent:
        """
        Very conservative parsing.

        Early A7DO understands *interaction intent*,
        not semantics.
        """
        t = text.lower().strip()

        if t.endswith("?"):
            return LanguageIntent(
                kind="query",
                target="system",
                confidence=0.6,
            )

        if any(w in t for w in ("do", "can", "will", "should")):
            return LanguageIntent(
                kind="request",
                target="system",
                confidence=0.5,
            )

        if any(w in t for w in ("hello", "hi", "hey")):
            return LanguageIntent(
                kind="ack",
                target=None,
                confidence=0.9,
            )

        return LanguageIntent(
            kind="describe",
            target=None,
            confidence=0.4,
        )

    # --------------------------------------------------
    # OUTPUT: Structure → English
    # --------------------------------------------------

    def respond(self, *, state: dict, intent: LanguageIntent) -> Utterance:
        """
        Render a safe, grounded response.

        Uses ONLY visible system state.
        """

        birth = state.get("birth_state")

        if birth and not birth.born:
            return Utterance(
                text="I am not yet born.",
                certainty=1.0,
            )

        if intent.kind == "ack":
            return Utterance(
                text="Hello.",
                certainty=0.9,
            )

        if intent.kind == "query":
            ticks = state.get("ticks", 0)
            return Utterance(
                text=f"I am active. Current tick is {ticks}.",
                certainty=0.6,
            )

        return Utterance(
            text="I am present.",
            certainty=0.4,
        )