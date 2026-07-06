# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

- **Owner & pet management** — create an owner and add multiple pets, each with their own care tasks.
- **Rich tasks** — every task has a description, duration, priority, preferred time, and frequency.
- **Priority-aware daily planning** — `Scheduler.build_plan()` orders tasks by priority (high first), then shortest duration, and packs them into a time budget, skipping what doesn't fit.
- **Sorting by time** — `Scheduler.sort_by_time()` presents tasks chronologically by their `HH:MM` time (untimed tasks last).
- **Filtering** — filter tasks by completion status (`Scheduler.filter_by_status()`) or by pet (`Owner.tasks_for_pet()`).
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags tasks scheduled at the same time and returns friendly warnings instead of crashing.
- **Daily & weekly recurrence** — completing a recurring task auto-schedules its next occurrence (`Scheduler.complete_task()` + `Task.next_occurrence()`, using `timedelta`).
- **Plan explanations** — `Scheduler.explain()` describes why the plan looks the way it does.
- **Interactive Streamlit UI** — add pets/tasks, see conflict warnings, mark tasks complete, and generate a schedule, with all state persisted in `st.session_state`.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running `python main.py`:

```
Tasks sorted by time
========================================
07:30  Feed Mochi [high]
08:00  Give Mochi meds [high]
08:00  Morning walk [high]
16:00  Play / enrichment [low]
18:00  Evening walk [medium]

Conflict check
========================================
⚠️  Conflict at 08:00: Give Mochi meds, Morning walk

Recurring task rollover
========================================
Completed 'Morning walk' (done=True).
Auto-created next 'Morning walk' due 2026-07-06.

Outstanding (incomplete) tasks
========================================
[ ] Play / enrichment
[ ] Feed Mochi
[ ] Give Mochi meds
[ ] Evening walk
[ ] Morning walk

Today's Schedule for Jordan
========================================
07:30-07:35  Give Mochi meds      ( 5 min) [high]
07:35-07:45  Feed Mochi           (10 min) [high]
07:45-08:15  Morning walk         (30 min) [high]
08:15-08:40  Evening walk         (25 min) [medium]
08:40-08:55  Play / enrichment    (15 min) [low]
```

## 🧪 Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest

# Or, with coverage:
pytest --cov
```

**What the tests cover** ([`tests/test_pawpal.py`](tests/test_pawpal.py)) — 11 tests spanning happy paths and edge cases:

- **Task basics** — `mark_complete()` flips the completion flag; adding a task increases a pet's task count.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological `HH:MM` order, with untimed tasks placed last.
- **Filtering** — `filter_by_status()` returns only tasks matching a completion status.
- **Conflict detection** — flags two tasks sharing the exact same time, and returns an empty list when all times are unique.
- **Recurrence logic** — completing a `daily` task creates a new occurrence due the next day; a `weekly` task rolls forward 7 days; a one-off task is not rescheduled.
- **Edge cases** — a pet with no tasks yields an empty plan (no crash); `build_plan()` drops tasks that exceed the available time budget.

Successful test run:

```
$ python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0
collected 11 items

tests/test_pawpal.py ...........                                         [100%]

============================== 11 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5).** All core scheduling behaviors — sorting, filtering, recurrence, conflict detection, and time-budget handling — are covered by passing tests, including the key edge cases. It's held back from 5 stars because conflict detection only catches exact-time matches (not overlapping durations), and the recurrence tests are date-relative rather than covering month/year boundaries in depth.

## 📐 Smarter Scheduling

PawPal+ goes beyond a flat task list with four scheduling behaviors. Each is
implemented in the logic layer ([`pawpal_system.py`](pawpal_system.py)):

### Sorting — `Scheduler.sort_by_time()`

Orders tasks by their preferred `HH:MM` start time. Because `HH:MM` strings are
zero-padded, a plain string sort is already chronological; a `sorted()` key of
`(t.time is None, t.time or "")` pushes untimed tasks to the end. The daily plan
builder (`Scheduler.build_plan()`) additionally sorts by priority (high first),
then shortest duration, so the most important quick wins are placed first.

### Filtering — `Scheduler.filter_by_status()` and `Owner.tasks_for_pet()`

- `Scheduler.filter_by_status(tasks, completed=...)` returns only the tasks whose
  completion flag matches, e.g. to show just the outstanding to-dos.
- `Owner.tasks_for_pet(pet_name)` returns the tasks belonging to a single pet.
- `Scheduler.build_plan()` also implicitly filters out tasks that don't fit the
  remaining time budget.

### Conflict detection — `Scheduler.detect_conflicts()`

A lightweight check that groups tasks by their exact start time and returns a
list of human-readable warning strings (e.g. `"Conflict at 08:00: Meds, Walk"`)
when two or more tasks share the same slot. It returns warnings rather than
raising, so the program never crashes. (It flags exact-time matches only, not
overlapping durations — see the tradeoff noted in [`reflection.md`](reflection.md).)

### Recurring tasks — `Task.next_occurrence()` and `Scheduler.complete_task()`

When a `daily` or `weekly` task is completed via `Scheduler.complete_task(pet, task)`,
the scheduler marks it done and calls `Task.next_occurrence()`, which uses
Python's `timedelta` to build a fresh, uncompleted copy due on the next date
(today + 1 day for daily, + 7 days for weekly) and adds it to the pet. One-off
tasks (`frequency="once"`) return `None` and are not rescheduled.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.build_plan()` | Sort by preferred `HH:MM` time (untimed last); the plan itself sorts by priority (high first), then shortest duration. |
| Filtering | `Scheduler.filter_by_status()`, `Owner.tasks_for_pet()` | Filter by completion status, or by pet name. `build_plan()` also drops tasks that don't fit the time budget. |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight: returns warning strings for tasks sharing the exact same start time (does not crash). |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | Completing a `daily`/`weekly` task auto-creates the next occurrence via `timedelta` (today + 1 day / 7 days). |

## 📸 Demo Walkthrough

### Main UI features

Launch the app with `streamlit run app.py`. From top to bottom you can:

- **Set the owner name** and **add pets** (name + species).
- **Add tasks** to any pet — description, duration, priority, preferred time, and frequency (once / daily / weekly).
- See **conflict warnings** appear automatically when two tasks share a start time.
- Browse **each pet's tasks in a time-sorted table**.
- **Mark a task complete** — recurring tasks instantly show their next scheduled date.
- **Generate a daily schedule** for a given time budget and start time, with an explanation of the ordering.

### Example workflow

1. Enter the owner name (e.g. *Jordan*).
2. **Add a pet:** "Rex", species *dog* → click **Add pet**.
3. **Add a task:** for Rex, "Morning walk", 30 min, priority *high*, time `08:00`, frequency *daily* → **Add task**.
4. **Add another task** at the same time (e.g. "Give meds" at `08:00`) → a **⚠️ conflict warning** appears for the 08:00 slot.
5. **Mark "Morning walk" complete** → PawPal+ confirms completion and reports that the next daily occurrence is auto-scheduled for tomorrow.
6. Set **Available minutes** (e.g. 120) and **Start time** (`08:00`), then click **Generate schedule** to see **Today's plan** as a table, plus a "Why this plan?" explanation.

### Key Scheduler behaviors shown

- **Sorting:** tasks display and schedule in chronological / priority order rather than insertion order.
- **Conflict warnings:** exact same-time tasks are flagged before you build the plan.
- **Recurrence:** completing a daily/weekly task rolls it forward automatically.
- **Time-budget filtering:** tasks that don't fit the available minutes are skipped, and the UI notes how many were dropped.

### Sample CLI output (`python main.py`)

```
Tasks sorted by time
========================================
07:30  Feed Mochi [high]
08:00  Give Mochi meds [high]
08:00  Morning walk [high]
16:00  Play / enrichment [low]
18:00  Evening walk [medium]

Conflict check
========================================
⚠️  Conflict at 08:00: Give Mochi meds, Morning walk

Recurring task rollover
========================================
Completed 'Morning walk' (done=True).
Auto-created next 'Morning walk' due 2026-07-06.

Outstanding (incomplete) tasks
========================================
[ ] Play / enrichment
[ ] Feed Mochi
[ ] Give Mochi meds
[ ] Evening walk
[ ] Morning walk

Today's Schedule for Jordan
========================================
07:30-07:35  Give Mochi meds      ( 5 min) [high]
07:35-07:45  Feed Mochi           (10 min) [high]
07:45-08:15  Morning walk         (30 min) [high]
08:15-08:40  Evening walk         (25 min) [medium]
08:40-08:55  Play / enrichment    (15 min) [low]
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
