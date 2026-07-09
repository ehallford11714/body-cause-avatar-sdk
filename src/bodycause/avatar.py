"""BodyCauseAvatar — public step API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bodycause.render import skeleton_frame_json, skeleton_svg
from bodycause.signals import IntentKPIs
from bodycause.skeleton import FACE_ASPECTS, SkeletonIntegrator, _face_from_signals


@dataclass
class AvatarFrame:
    """One avatar output frame: joints + face aspects + optional SVG/JSON."""

    t: int
    joints: dict[str, float]
    positions_2d: dict[str, list[float]]
    face_aspects: dict[str, float]
    intent: str
    emotion: str
    phase: float
    svg: str | None = None
    skeleton_json: dict[str, Any] | None = None
    backend: str = "bodycause"
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, *, include_svg: bool = False) -> dict[str, Any]:
        out: dict[str, Any] = {
            "t": self.t,
            "joints": self.joints,
            "positions_2d": self.positions_2d,
            "face_aspects": self.face_aspects,
            "intent": self.intent,
            "emotion": self.emotion,
            "phase": round(self.phase, 4),
            "backend": self.backend,
            "meta": self.meta,
        }
        if include_svg and self.svg is not None:
            out["svg"] = self.svg
        if self.skeleton_json is not None:
            out["skeleton"] = self.skeleton_json
        return out


class BodyCauseAvatar:
    """Game/avatar SDK: causal limb+face from intent/KPI streams.

    Optional conceptual path from NextFrameSeq ``motion/`` when importable;
    otherwise uses the built-in damped skeleton integrator (same public API).
    """

    def __init__(self, *, prefer_nfs_motion: bool = True, damp: float = 0.78) -> None:
        self.prefer_nfs_motion = prefer_nfs_motion
        self._body = SkeletonIntegrator(damp=damp)
        self._nfs_note: str | None = None
        if prefer_nfs_motion:
            self._nfs_note = self._probe_nfs_motion()

    @staticmethod
    def _probe_nfs_motion() -> str | None:
        """Document optional NextFrameSeq motion path concepts (no hard dep)."""
        try:
            import nextframeseq.motion  # noqa: F401

            return "nextframeseq.motion importable — use as upstream world-model later"
        except Exception:
            return None

    def reset(self) -> None:
        self._body.reset()

    def step(
        self,
        intent: str | IntentKPIs | dict[str, Any] = "idle",
        kpis: dict[str, Any] | IntentKPIs | None = None,
        *,
        render_svg: bool = True,
        render_json: bool = True,
        width: float = 200.0,
        height: float = 280.0,
    ) -> AvatarFrame:
        """Advance one frame.

        Parameters
        ----------
        intent:
            Intent label string, full ``IntentKPIs``, or mapping.
        kpis:
            Optional KPI overrides / full ``IntentKPIs`` when ``intent`` is a string.
        """
        sig = self._resolve_signals(intent, kpis)
        joint_state = self._body.step(sig)
        face = _face_from_signals(sig)
        positions = {
            k: [round(x, 2), round(y, 2)] for k, (x, y) in joint_state.positions_2d.items()
        }
        angles = {k: round(v, 4) for k, v in joint_state.angles.items()}

        svg = None
        if render_svg:
            svg = skeleton_svg(
                joint_state.positions_2d,
                face_aspects=face,
                width=int(width),
                height=int(height),
                caption=f"t={joint_state.t} · {sig.intent}/{sig.emotion}",
            )
        skel = None
        if render_json:
            skel = skeleton_frame_json(angles, positions, face)

        meta: dict[str, Any] = {"face_aspect_keys": list(FACE_ASPECTS)}
        if self._nfs_note:
            meta["nfs_motion"] = self._nfs_note

        return AvatarFrame(
            t=joint_state.t,
            joints=angles,
            positions_2d=positions,
            face_aspects=face,
            intent=sig.intent,
            emotion=sig.emotion,
            phase=joint_state.phase,
            svg=svg,
            skeleton_json=skel,
            backend="bodycause",
            meta=meta,
        )

    @staticmethod
    def _resolve_signals(
        intent: str | IntentKPIs | dict[str, Any],
        kpis: dict[str, Any] | IntentKPIs | None,
    ) -> IntentKPIs:
        if isinstance(intent, IntentKPIs):
            base = intent
        elif isinstance(intent, dict):
            base = IntentKPIs.from_mapping(intent)
        else:
            base = IntentKPIs(intent=str(intent))

        if kpis is None:
            return base
        if isinstance(kpis, IntentKPIs):
            return kpis
        merged = base.to_dict()
        merged.update(kpis)
        return IntentKPIs.from_mapping(merged)
