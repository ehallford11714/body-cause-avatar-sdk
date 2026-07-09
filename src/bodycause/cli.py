"""BodyCause Avatar SDK CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_demo(args: argparse.Namespace) -> int:
    from bodycause.avatar import BodyCauseAvatar
    from bodycause.export import export_trajectory_json
    from bodycause.signals import synthetic_intent

    avatar = BodyCauseAvatar(prefer_nfs_motion=not args.offline)
    sig = synthetic_intent(args.scenario)
    frames = []
    for _ in range(args.steps):
        frames.append(
            avatar.step(sig, render_svg=bool(args.svg_dir), render_json=True)
        )

    summary = {
        "scenario": args.scenario,
        "steps": args.steps,
        "last": frames[-1].to_dict(include_svg=False) if frames else {},
    }
    print(json.dumps(summary, indent=2))

    if args.out:
        path = export_trajectory_json(frames, args.out, fps=args.fps)
        print(f"Wrote trajectory -> {path}", file=sys.stderr)
    if args.svg_dir:
        d = Path(args.svg_dir)
        d.mkdir(parents=True, exist_ok=True)
        for fr in frames:
            if fr.svg:
                (d / f"frame_{fr.t:04d}.svg").write_text(fr.svg, encoding="utf-8")
        print(f"Wrote {len(frames)} SVGs -> {d}", file=sys.stderr)
    return 0


def cmd_schema(_: argparse.Namespace) -> int:
    from bodycause.export import trajectory_schema

    print(json.dumps(trajectory_schema(), indent=2))
    return 0


def cmd_sota(_: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "docs" / "SOTA.md"
    if path.is_file():
        print(path.read_text(encoding="utf-8"))
        return 0
    print("docs/SOTA.md not found", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bodycause", description="BodyCause Avatar SDK")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="Roll out synthetic intent → trajectory JSON/SVG")
    d.add_argument("--scenario", default="walk", help="walk|wave|think|celebrate|sad|point|idle")
    d.add_argument("--steps", type=int, default=8)
    d.add_argument("--out", default="", help="Write trajectory JSON path")
    d.add_argument("--svg-dir", default="", help="Write per-frame SVG directory")
    d.add_argument("--fps", type=float, default=30.0)
    d.add_argument("--offline", action="store_true", help="Skip NFS motion probe")
    d.set_defaults(func=cmd_demo)

    s = sub.add_parser("schema", help="Print Unity/Web trajectory JSON schema")
    s.set_defaults(func=cmd_schema)

    t = sub.add_parser("sota", help="Print SOTA research notes")
    t.set_defaults(func=cmd_sota)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
