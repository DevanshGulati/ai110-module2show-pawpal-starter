"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. This is the "brain" of the
app: it models owners, pets, and their care tasks, and builds an ordered daily
plan that respects a time budget and task priorities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# How far ahead the next occurrence of a recurring task should be scheduled.
_FREQUENCY_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

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
    frequency: str = "once"  # "once", "daily", or "weekly"
    completed: bool = False
    due_date: date | None = None  # the day this occurrence is due

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (higher = more urgent)."""
        return _PRIORITY_WEIGHTS.get(self.priority.lower(), 0)

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy due on the next date, or None if not recurring."""
        delta = _FREQUENCY_DELTAS.get(self.frequency.lower())
        if delta is None:
            return None  # one-off task: nothing to reschedule
        base = self.due_date or date.today()
        return Task(
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time=self.time,
            frequency=self.frequency,
            completed=False,
            due_date=base + delta,
        )


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

    def tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return the tasks belonging to the pet with the given name."""
        return [task for pet in self.pets if pet.name == pet_name for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily care plan from a set of tasks and constraints."""

    def __init__(self, available_minutes: int = 240, start_time: str = "08:00") -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by preferred "HH:MM" time; untimed tasks go last.

        "HH:MM" strings are zero-padded, so plain string comparison already
        orders them chronologically. The ``key`` sorts untimed tasks (time is
        None) after timed ones by giving them a truthy first element.
        """
        return sorted(tasks, key=lambda t: (t.time is None, t.time or ""))

    @staticmethod
    def filter_by_status(tasks: list[Task], completed: bool = False) -> list[Task]:
        """Return only the tasks whose completed flag matches ``completed``."""
        return [t for t in tasks if t.completed == completed]

    def complete_task(self, pet: Pet, task: Task) -> Task | None:
        """Mark a task complete and, if recurring, add its next occurrence to the pet.

        Returns the newly created follow-up Task, or None for a one-off task.
        """
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            pet.add_task(follow_up)
        return follow_up

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warnings for tasks sharing the same preferred time.

        Lightweight strategy: only flags exact "HH:MM" matches (not overlapping
        durations) and returns human-readable warnings instead of raising.
        """
        by_time: dict[str, list[Task]] = {}
        for task in tasks:
            if task.time:  # ignore untimed tasks
                by_time.setdefault(task.time, []).append(task)

        warnings = []
        for time, clashing in by_time.items():
            if len(clashing) > 1:
                names = ", ".join(t.description for t in clashing)
                warnings.append(f"Conflict at {time}: {names}")
        return warnings

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
