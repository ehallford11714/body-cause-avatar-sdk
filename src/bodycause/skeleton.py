"""Humanoid joints + face aspects — causal step from intent/KPIs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from bodycause.signals import IntentKPIs

JOINTS = (
    "root",
    "spine",
    "neck",
    "head",
    "l_shoulder",
    "l_elbow",
    "l_wrist",
    "r_shoulder",
    "r_elbow",
    "r_wrist",
    "l_hip",
    "l_knee",
    "l_ankle",
    "r_hip",
    "r_knee",
    "r_ankle",
)

BONES = (
    ("root", "spine"),
    ("spine", "neck"),
    ("neck", "head"),
    ("spine", "l_shoulder"),
    ("l_shoulder", "l_elbow"),
    ("l_elbow", "l_wrist"),
    ("spine", "r_shoulder"),
    ("r_shoulder", "r_elbow"),
    ("r_elbow", "r_wrist"),
    ("root", "l_hip"),
    ("l_hip", "l_knee"),
    ("l_knee", "l_ankle"),
    ("root", "r_hip"),
    ("r_hip", "r_knee"),
    ("r_knee", "r_ankle"),
)

FACE_ASPECTS = (
    "mouth_curve",
    "mouth_open",
    "brow_raise",
    "brow_knit",
    "eye_open",
    "gaze_yaw",
)


@dataclass
class JointState:
    angles: dict[str, float] = field(default_factory=dict)
    positions_2d: dict[str, tuple[float, float]] = field(default_factory=dict)
    phase: float = 0.0
    t: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "angles": {k: round(v, 4) for k, v in self.angles.items()},
            "positions_2d": {k: [round(x, 2), round(y, 2)] for k, (x, y) in self.positions_2d.items()},
            "phase": round(self.phase, 4),
            "t": self.t,
        }


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _intent_pose(intent: str, emotion: str) -> dict[str, float]:
    i = (intent or "").lower()
    e = (emotion or "").lower()
    pose = {j: 0.0 for j in JOINTS}

    if i in ("wave", "greet"):
        pose["r_shoulder"] = 1.1
        pose["r_elbow"] = 0.9
        pose["r_wrist"] = 0.3
        pose["spine"] = -0.05
    elif i in ("point", "indicate"):
        pose["r_shoulder"] = 0.7
        pose["r_elbow"] = 0.15
        pose["r_wrist"] = 0.0
        pose["neck"] = 0.1
    elif i in ("celebrate",):
        pose["l_shoulder"] = 1.2
        pose["r_shoulder"] = 1.2
        pose["l_elbow"] = 0.4
        pose["r_elbow"] = 0.4
        pose["spine"] = -0.1
    elif i in ("think", "deliberate"):
        pose["r_elbow"] = 1.1
        pose["r_shoulder"] = 0.35
        pose["neck"] = 0.15
        pose["head"] = 0.1
    elif i in ("withdraw",) or e == "sad":
        pose["spine"] = 0.28
        pose["neck"] = 0.22
        pose["l_shoulder"] = -0.25
        pose["r_shoulder"] = -0.25
    elif e == "happy":
        pose["l_shoulder"] = 0.2
        pose["r_shoulder"] = 0.25
        pose["spine"] = -0.05
    return pose


def _face_from_signals(sig: IntentKPIs) -> dict[str, float]:
    e = (sig.emotion or "").lower()
    aspects = {a: 0.0 for a in FACE_ASPECTS}
    aspects["eye_open"] = 0.85
    aspects["mouth_curve"] = _clip(sig.valence * 0.45, -0.5, 0.6)
    aspects["brow_raise"] = _clip(sig.arousal * 0.25 - sig.cognitive_load * 0.1, -0.2, 0.5)
    aspects["brow_knit"] = _clip(sig.cognitive_load * 0.35, 0.0, 0.6)
    aspects["mouth_open"] = _clip(sig.arousal * 0.15 if e in ("happy", "surprise") else 0.02, 0.0, 0.4)
    aspects["gaze_yaw"] = 0.0
    if e == "sad":
        aspects["mouth_curve"] = min(aspects["mouth_curve"], -0.15)
        aspects["eye_open"] = 0.7
    if e in ("focused",) or sig.intent == "think":
        aspects["brow_knit"] = max(aspects["brow_knit"], 0.25)
    return {k: round(v, 4) for k, v in aspects.items()}


def _fk_positions(angles: dict[str, float], width: float = 200.0, height: float = 280.0) -> dict[str, tuple[float, float]]:
    cx, cy = width / 2.0, height * 0.55
    scale = min(width, height) * 0.22

    def offset(base: tuple[float, float], ang: float, length: float) -> tuple[float, float]:
        return (base[0] + math.sin(ang) * length, base[1] - math.cos(ang) * length)

    a = angles
    root = (cx, cy)
    spine = offset(root, a.get("spine", 0.0), scale * 0.9)
    neck = offset(spine, a.get("neck", 0.0), scale * 0.35)
    head = offset(neck, a.get("head", 0.0), scale * 0.35)

    l_sh = offset(spine, -0.9 + a.get("l_shoulder", 0.0), scale * 0.45)
    l_el = offset(l_sh, -0.5 + a.get("l_elbow", 0.0), scale * 0.4)
    l_wr = offset(l_el, a.get("l_wrist", 0.0), scale * 0.35)

    r_sh = offset(spine, 0.9 + a.get("r_shoulder", 0.0), scale * 0.45)
    r_el = offset(r_sh, 0.5 + a.get("r_elbow", 0.0), scale * 0.4)
    r_wr = offset(r_el, a.get("r_wrist", 0.0), scale * 0.35)

    l_hip = offset(root, -0.35 + a.get("l_hip", 0.0), scale * 0.15)
    l_knee = offset(l_hip, 0.15 + a.get("l_knee", 0.0), scale * 0.5)
    l_ankle = offset(l_knee, a.get("l_ankle", 0.0), scale * 0.45)

    r_hip = offset(root, 0.35 + a.get("r_hip", 0.0), scale * 0.15)
    r_knee = offset(r_hip, -0.15 + a.get("r_knee", 0.0), scale * 0.5)
    r_ankle = offset(r_knee, a.get("r_ankle", 0.0), scale * 0.45)

    return {
        "root": root,
        "spine": spine,
        "neck": neck,
        "head": head,
        "l_shoulder": l_sh,
        "l_elbow": l_el,
        "l_wrist": l_wr,
        "r_shoulder": r_sh,
        "r_elbow": r_el,
        "r_wrist": r_wr,
        "l_hip": l_hip,
        "l_knee": l_knee,
        "l_ankle": l_ankle,
        "r_hip": r_hip,
        "r_knee": r_knee,
        "r_ankle": r_ankle,
    }


@dataclass
class SkeletonIntegrator:
    """Damped joint integrator with gait from motion KPI."""

    damp: float = 0.78
    angles: dict[str, float] = field(default_factory=lambda: {j: 0.0 for j in JOINTS})
    phase: float = 0.0
    t: int = 0

    def reset(self) -> None:
        self.angles = {j: 0.0 for j in JOINTS}
        self.phase = 0.0
        self.t = 0

    def step(self, sig: IntentKPIs) -> JointState:
        target = _intent_pose(sig.intent, sig.emotion)
        gait = 0.12 + 0.55 * _clip(sig.motion, 0.0, 1.0) + 0.15 * _clip(sig.arousal, 0.0, 1.0)
        self.phase += gait
        phase = self.phase

        if sig.intent in ("walk", "locomote", "idle") or sig.motion > 0.2:
            target["l_hip"] = 0.35 * math.sin(phase) * (0.3 + sig.motion)
            target["r_hip"] = 0.35 * math.sin(phase + math.pi) * (0.3 + sig.motion)
            target["l_knee"] = 0.45 * max(0.0, math.sin(phase)) * (0.3 + sig.motion)
            target["r_knee"] = 0.45 * max(0.0, math.sin(phase + math.pi)) * (0.3 + sig.motion)
            target["l_shoulder"] = target.get("l_shoulder", 0.0) + 0.22 * math.sin(phase + math.pi)
            target["r_shoulder"] = target.get("r_shoulder", 0.0) + 0.22 * math.sin(phase)

        if sig.intent in ("wave", "greet"):
            target["r_wrist"] = 0.35 * math.sin(phase * 2.2)

        new_angles: dict[str, float] = {}
        for j in JOINTS:
            cur = self.angles.get(j, 0.0)
            tgt = target.get(j, 0.0)
            new_angles[j] = self.damp * cur + (1.0 - self.damp) * tgt

        self.angles = new_angles
        self.t += 1
        positions = _fk_positions(new_angles)
        return JointState(angles=dict(new_angles), positions_2d=positions, phase=self.phase, t=self.t)
