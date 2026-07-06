# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
$ python -m pytest -q
.......                                                                  [100%]
7 passed in 0.01s
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.build_plan()` | Sort by preferred `HH:MM` time (untimed last); the plan itself sorts by priority (high first), then shortest duration. |
| Filtering | `Scheduler.filter_by_status()`, `Owner.tasks_for_pet()` | Filter by completion status, or by pet name. `build_plan()` also drops tasks that don't fit the time budget. |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight: returns warning strings for tasks sharing the exact same start time (does not crash). |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | Completing a `daily`/`weekly` task auto-creates the next occurrence via `timedelta` (today + 1 day / 7 days). |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
