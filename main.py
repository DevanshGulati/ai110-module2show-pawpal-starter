"""Temporary CLI testing ground for the PawPal+ logic layer.

Run with:  python main.py

Exercises the scheduling algorithms (sorting, filtering, recurring tasks, and
conflict detection) so we can verify the backend works before wiring the UI.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # Owner with two pets.
    owner = Owner(name="Jordan", preferences={"available_minutes": 120})
    mochi = Pet(name="Mochi", species="cat")
    rex = Pet(name="Rex", species="dog")
    owner.add_pet(mochi)
    owner.add_pet(rex)

    # Tasks added deliberately OUT OF ORDER by time to prove sorting works.
    owner.add_task(rex, Task("Evening walk", duration_minutes=25, priority="medium", time="18:00"))
    owner.add_task(rex, Task("Morning walk", duration_minutes=30, priority="high", time="08:00", frequency="daily"))
    owner.add_task(mochi, Task("Play / enrichment", duration_minutes=15, priority="low", time="16:00"))
    owner.add_task(mochi, Task("Feed Mochi", duration_minutes=10, priority="high", time="07:30"))
    # A conflicting task: same 08:00 slot as Rex's morning walk.
    owner.add_task(mochi, Task("Give Mochi meds", duration_minutes=5, priority="high", time="08:00"))

    scheduler = Scheduler(available_minutes=owner.preferences["available_minutes"], start_time="07:30")

    # --- Sorting -------------------------------------------------------------
    print("Tasks sorted by time")
    print("=" * 40)
    for t in scheduler.sort_by_time(owner.all_tasks()):
        print(f"{t.time or '  —  '}  {t.description} [{t.priority}]")

    # --- Conflict detection --------------------------------------------------
    print("\nConflict check")
    print("=" * 40)
    conflicts = scheduler.detect_conflicts(owner.all_tasks())
    if conflicts:
        for warning in conflicts:
            print(f"⚠️  {warning}")
    else:
        print("No conflicts found.")

    # --- Recurring tasks -----------------------------------------------------
    print("\nRecurring task rollover")
    print("=" * 40)
    morning_walk = owner.tasks_for_pet("Rex")[1]  # the daily morning walk
    follow_up = scheduler.complete_task(rex, morning_walk)
    print(f"Completed '{morning_walk.description}' (done={morning_walk.completed}).")
    if follow_up:
        print(f"Auto-created next '{follow_up.description}' due {follow_up.due_date}.")

    # --- Filtering -----------------------------------------------------------
    print("\nOutstanding (incomplete) tasks")
    print("=" * 40)
    for t in scheduler.filter_by_status(owner.all_tasks(), completed=False):
        print(f"[ ] {t.description}")

    # --- Today's schedule ----------------------------------------------------
    print(f"\nToday's Schedule for {owner.name}")
    print("=" * 40)
    plan = scheduler.build_plan(scheduler.filter_by_status(owner.all_tasks(), completed=False))
    for item in plan:
        t = item.task
        print(f"{item.start_time}-{item.end_time}  {t.description:<20} ({t.duration_minutes:>2} min) [{t.priority}]")


if __name__ == "__main__":
    main()
