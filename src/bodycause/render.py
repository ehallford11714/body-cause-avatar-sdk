"""SVG / JSON skeleton frame helpers (no OpenCV required)."""

from __future__ import annotations

from typing import Any

from bodycause.skeleton import BONES


def skeleton_svg(
    positions: dict[str, tuple[float, float]],
    *,
    face_aspects: dict[str, float] | None = None,
    width: int = 200,
    height: int = 280,
    caption: str = "",
) -> str:
    """Render a stick-figure SVG from 2D joint positions."""
    lines: list[str] = []
    for a, b in BONES:
        if a not in positions or b not in positions:
            continue
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#9ec9ff" stroke-width="2.5" stroke-linecap="round"/>'
        )
    dots: list[str] = []
    for name, (x, y) in positions.items():
        r = 6 if name == "head" else 3
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#cfe6ff"/>')

    # Tiny face cue near head
    face_note = ""
    if face_aspects and "head" in positions:
        hx, hy = positions["head"]
        mouth = float(face_aspects.get("mouth_curve", 0.0))
        cy = hy + 4 - mouth * 3
        face_note = (
            f'<path d="M{hx - 6:.1f} {hy + 2:.1f} Q{hx:.1f} {cy:.1f} {hx + 6:.1f} {hy + 2:.1f}" '
            f'stroke="#6b3a4a" stroke-width="1.5" fill="none"/>'
        )

    cap = caption.replace("<", "").replace(">", "")[:64]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#141820"/>
  {"".join(lines)}
  {"".join(dots)}
  {face_note}
  <text x="{width / 2:.0f}" y="{height - 8}" text-anchor="middle" fill="#8a93a6" font-size="10" font-family="sans-serif">{cap}</text>
</svg>"""


def skeleton_frame_json(
    joints: dict[str, float],
    positions_2d: dict[str, list[float]],
    face_aspects: dict[str, float],
) -> dict[str, Any]:
    return {
        "joints": joints,
        "positions_2d": positions_2d,
        "bones": [{"from": a, "to": b} for a, b in BONES],
        "face_aspects": face_aspects,
    }
