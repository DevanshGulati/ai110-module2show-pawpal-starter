"""PawPal+ logic layer.

Backend classes for the pet care planning assistant, generated as skeletons
from diagrams/uml.mmd. Method bodies are stubbed out and will be implemented
in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CareTask:
    """A single pet care task (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    preferred_time: str | None = None

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (higher = more urgent)."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet that has care tasks."""

    name: str
    species: str
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: CareTask) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner with one or more pets and scheduling preferences."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def add_task(self, pet: Pet, task: CareTask) -> None:
        """Add a care task to one of this owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Builds and explains a daily care plan from a set of tasks and constraints."""

    def __init__(self, available_minutes: int, start_time: str = "08:00") -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time

    def build_plan(self, tasks: list[CareTask]) -> list:
        """Choose and order tasks into a daily plan within the time budget."""
        raise NotImplementedError

    def explain(self, plan: list) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        raise NotImplementedError
