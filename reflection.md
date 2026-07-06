# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

Based on the PawPal+ scenario, a user should be able to perform these three core actions:

1. Add a pet and owner profile: The user enters basic owner information and creates a pet (for example, name and type/breed) so the assistant knows who it is planning care for.

2. Add and edit care tasks for a pet: The user records care tasks such as walks, feeding, meds, enrichment, and grooming, giving each task at least a duration and a priority (and optionally preferences like preferred time). They can update or remove tasks as needs change.

3. Generate and view a daily care plan: The user asks PawPal+ to build a daily schedule that respects their constraints (available time, priority, preferences), then views the resulting plan clearly, ideally with an explanation of why tasks were chosen or ordered the way they were.

**a. Initial design**

My initial design used four classes, split by responsibility:

- **Owner** — holds the person's `name`, a list of their `pets`, and scheduling `preferences` (e.g. available minutes per day). It's the top-level entry point (`add_pet`, `add_task`) that ties everything together.
- **Pet** — a `Task` container with `name` and `species`; responsible for managing its own task list (`add_task`, `remove_task`).
- **Task** — a single unit of care (`description`, `duration_minutes`, `priority`, `time`, `frequency`, `completed`). It knows how urgent it is via `priority_score()` and can be marked done via `mark_complete()`.
- **Scheduler** — the behavior/logic class. It doesn't store tasks; it takes them plus constraints (`available_minutes`, `start_time`) and produces an ordered daily plan (`build_plan`) and a justification (`explain`).

I deliberately separated the *data* classes (Owner/Pet/Task, as dataclasses) from the *behavior* class (Scheduler) so the scheduling algorithm can change without touching the data model.

**b. Design changes**

Yes. When I asked my AI assistant to review the skeleton for missing relationships, it flagged that `Scheduler.build_plan()` and `explain()` both operate on a "plan," and the UML annotated the return type as `list~ScheduledItem~`, but no `ScheduledItem` class actually existed — a plan was just an untyped `list`. That left nowhere to record *when* a task was placed, which `explain()` needs.

I added a **`ScheduledItem`** dataclass that wraps a `Task` with a concrete `start_time` (plus an `end_minutes` helper), and updated both `Scheduler` method signatures and the UML to use it. This makes the plan self-describing: each item carries its task and time, so `explain()` can report the schedule without recomputing it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: a **time budget** (`available_minutes` for the day), **task priority** (high/medium/low), and each task's **duration**. When time is limited, `build_plan()` sorts by priority first (high tasks are placed before low ones) and then by shortest duration, so quick high-value tasks fit first and low-priority tasks are dropped if the budget runs out.

I decided priority mattered most because the scenario is about a busy owner staying *consistent* with essential care — feeding and meds should never be skipped in favor of enrichment. Time is the hard limit, so it acts as the gate; duration is a tie-breaker that maximizes how many tasks fit.

**b. Tradeoffs**

My conflict detection only flags tasks with the **exact same "HH:MM" start time**, not overlapping durations. Two tasks at `08:00` are caught, but a 30-minute task at `08:00` and another at `08:15` are not, even though they overlap in real time.

This is a reasonable tradeoff for this scenario: exact-match detection is trivial to reason about, runs in a single pass, and never produces false positives. A pet owner writing down preferred times will most often collide on round times ("both at 8am"), so it catches the common case cheaply. True interval-overlap detection would need parsed start/end times and pairwise comparison — worth it later, but over-engineered for a first pass where the goal is a lightweight warning rather than a hard guarantee.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI across every phase: brainstorming the initial class list, generating the UML skeleton, fleshing out method bodies, drafting tests, and polishing docs. The most effective features were **agent/edit mode** (making coordinated edits across `pawpal_system.py`, `main.py`, and the tests at once — especially for the recurrence feature that touched `Task` and `Scheduler` together) and **inline chat on a specific method** for targeted questions like "how do I sort `HH:MM` strings with a `sorted()` key?".

The most helpful prompts were **specific and scoped**: "how should the `Scheduler` retrieve all tasks from the `Owner`'s pets?" produced a clean `Owner.all_tasks()` method, and "suggest a *lightweight* conflict-detection strategy that returns a warning instead of crashing" kept the AI from over-engineering. Open-ended "make this better" prompts were the least useful.

**Which AI features were most effective:** agent mode for multi-file changes; inline chat for one-method questions; and using the AI as a *reviewer* ("what relationships are missing from this skeleton?") which is how the `ScheduledItem` class got added.

**Using separate chat sessions** for planning vs. implementation vs. testing kept context clean — the testing session focused purely on edge cases (empty pet, duplicate times) without dragging along implementation details, and the algorithm-planning session didn't pollute the core-logic work. It made each conversation shorter and more on-topic.

**b. Judgment and verification**

- **A suggestion I modified:** when asked to simplify the `sort_by_time` key, the AI offered a terser expression, but I kept the explicit `(t.time is None, t.time or "")` tuple because it's easier for a human to read and makes the "untimed goes last" rule obvious. I chose readability over cleverness.
- **A suggestion I rejected:** I declined to build full interval-overlap conflict detection early on and kept exact-time matching instead (documented in §2b), because the extra complexity wasn't justified for a first pass.
- **How I verified:** I ran `python main.py` after each change to watch real output, and I wrote tests (11 total) that pin down the behavior — e.g. asserting a completed daily task's follow-up is due exactly `date.today() + timedelta(days=1)`. If the AI's code and my test disagreed, I traced which one was wrong rather than trusting the generated code by default.

**As the "lead architect,"** my job was to own the design decisions the AI can't make for me: which constraints matter most (priority over duration), how much complexity is warranted (lightweight conflict detection), and what "clean" means for this codebase (separating data classes from the `Scheduler`'s behavior). The AI was fast at producing options and boilerplate, but I had to be the one to reject, scope, and verify — the quality came from the combination, not from either side alone.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 11 tests in `tests/test_pawpal.py` covering both happy paths and edge cases:

- **Task basics** — `mark_complete()` flips the flag; adding a task grows the pet's list.
- **Sorting** — `sort_by_time()` returns chronological order with untimed tasks last.
- **Filtering** — `filter_by_status()` returns only matching tasks.
- **Conflict detection** — flags exact same-time clashes; returns empty when times are unique.
- **Recurrence** — a completed daily task rolls to tomorrow, a weekly task to +7 days, and a one-off task is not rescheduled.
- **Edge cases** — a pet with no tasks yields an empty plan (no crash); `build_plan()` drops tasks that exceed the time budget.

These mattered because sorting, recurrence, and conflict detection are the "smart" behaviors most likely to break silently — a wrong `timedelta` or a bad sort key wouldn't crash, it would just quietly produce a wrong plan, so tests are the only reliable guard.

**b. Confidence**

I'm about **4/5** confident. Every core behavior is exercised by a passing test, including the trickier recurrence math and the empty/over-budget edge cases. What holds me back from full confidence: conflict detection only catches exact-time matches (not overlapping durations), and I haven't tested odd inputs like malformed time strings (`"25:99"`), negative or zero durations, or recurrence across month/year boundaries. Those are what I'd test next.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the clean separation between the **data classes** (`Owner`/`Pet`/`Task` as dataclasses) and the **`Scheduler`** behavior class. It made every later feature — sorting, filtering, recurrence, conflicts — a small, self-contained method that was easy to test in isolation, and it kept the Streamlit UI thin (it just calls scheduler methods). The CLI-first workflow also paid off: having `main.py` prove the logic before touching the UI meant the UI wiring was almost trivial.

**b. What you would improve**

I'd make the `Scheduler` honor each task's **preferred `time`** when building the plan instead of packing tasks back-to-back from a single `start_time` — right now the preferred time drives sorting and conflict detection but not placement. I'd also upgrade conflict detection to true **interval-overlap** checking and add input validation for time strings and durations.

**c. Key takeaway**

The biggest lesson was that **I'm the architect and the AI is the fast builder** — the design decisions (what classes exist, which constraints win, how much complexity is worth it) have to come from me, and the AI is most valuable when I give it well-scoped problems and then verify its output with tests and real runs rather than accepting it on faith.
