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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
