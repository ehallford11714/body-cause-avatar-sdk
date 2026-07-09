"""BodyCause Avatar SDK — causal limb+face from intent/KPI streams."""

from bodycause.avatar import AvatarFrame, BodyCauseAvatar
from bodycause.export import export_trajectory_json, trajectory_schema
from bodycause.signals import IntentKPIs

__version__ = "0.1.0"

__all__ = [
    "AvatarFrame",
    "BodyCauseAvatar",
    "IntentKPIs",
    "export_trajectory_json",
    "trajectory_schema",
    "__version__",
]
