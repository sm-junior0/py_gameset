"""Future reward service boundary.

The prototype intentionally returns only virtual rewards. Real coupons, QR
codes, or sponsor prizes must be issued by a secure backend after server-side
score verification and sponsor-defined eligibility checks.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VirtualReward:
    """A local-only reward shown at the end of a prototype session."""

    label: str
    score: int


class RewardService:
    """Interface for reward decisions without real-world issuance."""

    def preview_virtual_reward(self, score: int, label: str) -> VirtualReward:
        """Return the local prototype reward preview."""
        return VirtualReward(label=label, score=score)
