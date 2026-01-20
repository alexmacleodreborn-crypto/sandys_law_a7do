# tools/visualization.py

from typing import Dict, List


def bar_view(values: Dict[str, float], width: int = 20) -> str:
    """
    Simple ASCII bar representation.

    Useful for logs, tests, and quick inspection.
    """
    lines: List[str] = []

    for key, value in values.items():
        v = max(0.0, min(1.0, float(value)))
        filled = int(v * width)
        bar = "█" * filled + "░" * (width - filled)
        lines.append(f"{key:>12}: {bar} {v:.2f}")

    return "\n".join(lines)


def table_view(rows: List[Dict[str, object]]) -> str:
    """
    Simple table-style text visualisation.
    """
    if not rows:
        return "<empty>"

    keys = list(rows[0].keys())
    header = " | ".join(keys)
    sep = "-" * len(header)

    body = []
    for r in rows:
        body.append(" | ".join(str(r.get(k, "")) for k in keys))

    return "\n".join([header, sep] + body)
