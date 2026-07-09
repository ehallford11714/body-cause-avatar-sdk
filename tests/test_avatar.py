"""Offline tests for BodyCause Avatar SDK."""

from __future__ import annotations

import json
from pathlib import Path

from bodycause.avatar import BodyCauseAvatar
from bodycause.export import export_trajectory_json, trajectory_schema
from bodycause.signals import IntentKPIs, synthetic_intent
from bodycause.skeleton import JOINTS


def test_synthetic_intent():
    sig = synthetic_intent("walk")
    assert sig.intent == "walk"
    assert sig.motion > 0.2


def test_step_returns_joints_and_face():
    avatar = BodyCauseAvatar(prefer_nfs_motion=False)
    fr = avatar.step("wave", {"valence": 0.5, "arousal": 0.4, "emotion": "happy"})
    assert fr.t == 1
    assert set(JOINTS).issubset(set(fr.joints))
    assert "mouth_curve" in fr.face_aspects
    assert fr.svg and "<svg" in fr.svg
    assert fr.skeleton_json is not None


def test_intent_kpis_mapping():
    sig = IntentKPIs.from_mapping({"intent": "point", "motion": 0.3, "custom_x": 1.5})
    assert sig.intent == "point"
    assert sig.extras.get("custom_x") == 1.5


def test_rollout_changes_phase():
    avatar = BodyCauseAvatar(prefer_nfs_motion=False)
    sig = synthetic_intent("walk")
    a = avatar.step(sig)
    b = avatar.step(sig)
    assert b.t == a.t + 1
    assert b.phase != a.phase or b.joints != a.joints


def test_export_trajectory(tmp_path: Path):
    avatar = BodyCauseAvatar(prefer_nfs_motion=False)
    frames = [avatar.step(synthetic_intent("think")) for _ in range(3)]
    path = export_trajectory_json(frames, tmp_path / "traj.json", fps=24)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "bodycause.trajectory.v1"
    assert data["fps"] == 24
    assert len(data["frames"]) == 3
    assert "joints_order" in data


def test_schema_documents_unity():
    sch = trajectory_schema()
    assert "unity_notes" in sch
    assert "joints_order" in sch
    assert len(sch["bones"]) > 0
