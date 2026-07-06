"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. This is the "brain" of the
app: it models owners, pets, and their care tasks, and builds an ordered daily
plan that respects a time budget and task priorities.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Higher number = more urgent. Used to sort tasks when time is limited.
_PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}


def _to_minutes(clock: str) -> int:
    """Convert an "HH:MM" clock string into minutes past midnight."""
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def _to_clock(minutes: int) -> str:
    """Convert minutes past midnight into an "HH:MM" clock string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    description: str
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    time: str | None = None  # preferred start time, "HH:MM"
    frequency: str = "daily"  # e.g. "daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (higher = more urgent)."""
        return _PRIORITY_WEIGHTS.get(self.priority.lower(), 0)


@dataclass
class ScheduledItem:
    """A Task placed at a concrete time in the daily plan."""

    task: Task
    start_time: str  # "HH:MM"

    @property
    def end_minutes(self) -> int:
        """Return the item's end time in minutes past midnight."""
        return _to_minutes(self.start_time) + self.task.duration_minutes

    @property
    def end_time(self) -> str:
        """Return the item's end time as an "HH:MM" clock string."""
        return _to_clock(self.end_minutes)


@dataclass
class Pet:
    """A pet that has care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet, if present."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    """A pet owner with one or more pets and scheduling preferences."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a care task to one of this owner's pets."""
        pet.add_task(task)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily care plan from a set of tasks and constraints."""

    def __init__(self, available_minutes: int = 240, start_time: str = "08:00") -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time

    def build_plan(self, tasks: list[Task]) -> list[ScheduledItem]:
        """Choose and order tasks into a daily plan within the time budget.

        Tasks are sorted by priority (high first), then by shorter duration so
        quick wins fit early. Tasks that don't fit the remaining budget are
        skipped. Chosen tasks are placed back-to-back starting at ``start_time``.
        """
        ordered = sorted(
            tasks,
            key=lambda t: (-t.priority_score(), t.duration_minutes),
        )

        plan: list[ScheduledItem] = []
        cursor = _to_minutes(self.start_time)
        remaining = self.available_minutes

        for task in ordered:
            if task.duration_minutes > remaining:
                continue  # not enough time left in the day's budget
            plan.append(ScheduledItem(task=task, start_time=_to_clock(cursor)))
            cursor += task.duration_minutes
            remaining -= task.duration_minutes

        return plan

    def explain(self, plan: list[ScheduledItem]) -> str:
        """Return a human-readable explanation of the plan and its ordering."""
        if not plan:
            return "No tasks could be scheduled within the available time."

        used = sum(item.task.duration_minutes for item in plan)
        lines = [
            f"Scheduled {len(plan)} task(s) using {used} of "
            f"{self.available_minutes} available minutes, "
            "ordered by priority (high first), then shortest duration:",
        ]
        for item in plan:
            t = item.task
            lines.append(
                f"  {item.start_time}-{item.end_time}  {t.description} "
                f"({t.duration_minutes} min) [priority: {t.priority}]"
            )
        return "\n".join(lines)
