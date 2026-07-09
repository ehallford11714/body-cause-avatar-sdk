"""Example: BodyCauseAvatar.step → JSON trajectory for Unity/Web."""

from __future__ import annotations

from pathlib import Path

from bodycause import BodyCauseAvatar, export_trajectory_json
from bodycause.signals import synthetic_intent


def main() -> None:
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    avatar = BodyCauseAvatar(prefer_nfs_motion=False)
    sig = synthetic_intent("wave")
    frames = [avatar.step(sig, render_svg=True) for _ in range(12)]

    traj_path = export_trajectory_json(frames, out_dir / "wave_trajectory.json", fps=30)
    svg_path = out_dir / "wave_last.svg"
    if frames[-1].svg:
        svg_path.write_text(frames[-1].svg, encoding="utf-8")

    print(f"frames={len(frames)} joints={list(frames[-1].joints)[:4]}...")
    print(f"trajectory -> {traj_path}")
    print(f"svg -> {svg_path}")
    print("face_aspects:", frames[-1].face_aspects)


if __name__ == "__main__":
    main()
