# BodyCause Avatar SDK — SOTA notes

Research framing for **P13 BodyCause Avatar SDK**: causal limb + face control from intent/KPI streams for games and avatars.

**Related:** [MotionCause Engine](../../MotionCauseEngine/), [NextFrameSeq](../../NextFrameSeq/) `motion/`, FaceCause Studio.

---

## 1. Avatar animation landscape

| Lineage | Idea | Relevance |
|---------|------|-----------|
| Keyframe / state machines | Discrete clips + blends | Baseline; BodyCause replaces teleporting poses with damped drift |
| Motion matching / Motion Fields | Query database of poses by trajectory features | Later retrieval backend for `intent` |
| Learned locomotion (PFNN, AMP, control nets) | Policy → joints | Optional learned head over same `step` API |
| Procedural IK / FABRIK | Goal-driven limbs | Point/wave intents in MVP |
| Face blendshapes / ARKit | Expression channels | `face_aspects` map cleanly |

MVP ships a **damped joint integrator + face aspects + SVG/JSON** — portable control signals for Unity/Web, not a full renderer.

---

## 2. Causal / world-model driven characters

NextFrameSeq / MotionCause treat motion as a causal loop:

\[
\text{signals }(v,a,\text{emotion},\text{intent}) \rightarrow H\cdot V \text{ drift} \rightarrow \text{pixels / joints}
\]

BodyCause specializes the **character control** side:

\[
(\text{intent}, \text{KPIs}) \xrightarrow{\text{step}} (\text{joints}, \text{face\_aspects}, \text{skeleton frame})
\]

Identification intuition: intent/text acts as instrument \(Z\); body KPIs are observations \(X\); confounders \(U\) (style, morphometry) are absorbed into damping / later style latents.

Optional path: when `nextframeseq.motion` is importable, treat it as the upstream world-model for face H·V; BodyCause remains the **avatar SDK façade**.

---

## 3. MeshGraphNets & graph dynamics

MeshGraphNets (and related GNN simulators) learn dynamics on mesh/graph nodes — a natural fit for:

- Cloth / soft-body secondary motion on top of joints
- Contact-aware foot plants
- Learned residual \(\Delta\) joints conditioned on intent

BodyCause MVP keeps an analytic graph (bones as edges, joints as nodes). A MeshGraphNet residual head can later predict \(\Delta\) angles without changing the export schema.

---

## 4. Export contract (Unity / Web)

See `bodycause.export.trajectory_schema()` and CLI `bodycause schema`.

- **Unity:** map `joints` → Humanoid muscles / local Euler offsets; `face_aspects` → blendshapes.
- **Web:** `positions_2d` + `bones` for Canvas/SVG; `joints` for Three.js rigs.

Schema id: `bodycause.trajectory.v1`.

---

## 5. Roadmap

| Phase | Deliverable |
|-------|-------------|
| **MVP** | `BodyCauseAvatar.step`, SVG/JSON, trajectory export, offline tests |
| P13.1 | Motion-matching clip library keyed by intent |
| P13.2 | Thin adapter to NextFrameSeq `CausalMotionLoop` |
| P13.3 | MeshGraphNet residual dynamics |
| P13.4 | Unity package sample importer |

---

## 6. Hygiene

- Library-first — **no default demo port** (does not touch **8765**).
- Optional NFS motion probe is import-only; never required for tests.
