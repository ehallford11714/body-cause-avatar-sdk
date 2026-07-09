<p align="center">
  <img src="assets/logo.svg" alt="BodyCause Avatar SDK" width="96" height="96" />
</p>

# BodyCause Avatar SDK

**Game/avatar SDK: causal limb + face from intent/KPI streams to joints, face aspects, and Unity/Web trajectory JSON.**

Package: `bodycause` - Product **P13** in the causal research suite.

## Install

```bash
cd BodyCauseAvatarSDK
pip install -e ".[dev]"
```

## Quick start

```bash
bodycause demo --scenario wave --steps 12 --out examples/out/wave.json --svg-dir examples/out/svg --offline
bodycause schema
python examples/run_wave_demo.py
```

## Docs

- [docs/SOTA.md](docs/SOTA.md) — state of the art notes for this product

## Suite

Part of the research product suite. Index: [PRODUCTS.md](../PRODUCTS.md) · GitHub: [body-cause-avatar-sdk](https://github.com/ehallford11714/body-cause-avatar-sdk)

## License

MIT