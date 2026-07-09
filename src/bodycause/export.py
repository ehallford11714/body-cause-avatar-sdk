"""JSON trajectory export for Unity / Web consumers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bodycause.avatar import AvatarFrame
from bodycause.skeleton import BONES, FACE_ASPECTS, JOINTS

SCHEMA_VERSION = "bodycause.trajectory.v1"


def trajectory_schema() -> dict[str, Any]:
    """Documented schema for Unity/Web importers."""
    return {
        "schema": SCHEMA_VERSION,
        "description": (
            "BodyCause avatar trajectory: per-frame joint angles (radians), "
            "optional 2D positions, and face aspect scalars in [-1, 1]-ish range."
        ),
        "fields": {
            "schema": "string — always bodycause.trajectory.v1",
            "fps": "number — nominal frames per second for playback",
            "joints_order": "string[] — canonical joint names",
            "bones": "{from,to}[] — stick/skeleton edges",
            "face_aspects_order": "string[] — face channel names",
            "frames": "Frame[]",
        },
        "Frame": {
            "t": "int — frame index (1-based from avatar.step)",
            "intent": "string",
            "emotion": "string",
            "phase": "float — gait / wave phase",
            "joints": "map<string,float> — radians",
            "positions_2d": "map<string,[x,y]> — optional normalized/pixel 2D FK",
            "face_aspects": "map<string,float>",
            "backend": "string",
        },
        "unity_notes": (
            "Map joints.* to Humanoid Avatar muscle/bone local Euler or use as "
            "additive offsets on a T-pose. face_aspects can drive blendshapes "
            "(mouth_curve→Smile, brow_raise→BrowsUp, etc.)."
        ),
        "web_notes": (
            "positions_2d + bones are enough for Canvas/SVG stick preview; "
            "joints are the portable control signal for 3D rigs."
        ),
        "joints_order": list(JOINTS),
        "bones": [{"from": a, "to": b} for a, b in BONES],
        "face_aspects_order": list(FACE_ASPECTS),
    }


def frames_to_trajectory(
    frames: list[AvatarFrame],
    *,
    fps: float = 30.0,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA_VERSION,
        "fps": fps,
        "joints_order": list(JOINTS),
        "bones": [{"from": a, "to": b} for a, b in BONES],
        "face_aspects_order": list(FACE_ASPECTS),
        "frames": [f.to_dict(include_svg=False) for f in frames],
    }


def export_trajectory_json(
    frames: list[AvatarFrame],
    path: str | Path,
    *,
    fps: float = 30.0,
) -> Path:
    """Write trajectory JSON for Unity/Web."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = frames_to_trajectory(frames, fps=fps)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
