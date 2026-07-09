"""Intent + KPI signal bundle driving the avatar step."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class IntentKPIs:
    """Coarse intent + dimensional KPIs for causal avatar control."""

    intent: str = "idle"
    emotion: str = "neutral"
    valence: float = 0.0
    arousal: float = 0.25
    motion: float = 0.1
    cognitive_load: float = 0.2
    extras: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None = None, **kwargs: Any) -> IntentKPIs:
        raw = dict(data or {})
        raw.update(kwargs)
        known = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        extras = {k: float(v) for k, v in raw.items() if k not in known and isinstance(v, (int, float))}
        filtered = {k: v for k, v in raw.items() if k in known and k != "extras"}
        if extras:
            filtered["extras"] = {**(filtered.get("extras") or {}), **extras}
        return cls(**filtered)


def synthetic_intent(scenario: str = "walk", *, seed: int = 0) -> IntentKPIs:
    """Deterministic intent/KPI presets for demos and tests."""
    s = (scenario or "idle").lower()
    _ = seed  # reserved for future jitter
    if s in ("walk", "locomote"):
        return IntentKPIs(intent="walk", emotion="neutral", valence=0.1, arousal=0.4, motion=0.55)
    if s in ("wave", "greet"):
        return IntentKPIs(intent="wave", emotion="happy", valence=0.55, arousal=0.45, motion=0.35)
    if s in ("think", "deliberate"):
        return IntentKPIs(
            intent="think", emotion="focused", valence=0.0, arousal=0.3, motion=0.08, cognitive_load=0.7
        )
    if s in ("celebrate", "happy"):
        return IntentKPIs(intent="celebrate", emotion="happy", valence=0.7, arousal=0.65, motion=0.5)
    if s in ("sad", "withdraw"):
        return IntentKPIs(intent="withdraw", emotion="sad", valence=-0.45, arousal=0.2, motion=0.05)
    if s in ("point", "indicate"):
        return IntentKPIs(intent="point", emotion="neutral", valence=0.1, arousal=0.35, motion=0.25)
    return IntentKPIs(intent="idle", emotion="neutral", valence=0.0, arousal=0.2, motion=0.05)
