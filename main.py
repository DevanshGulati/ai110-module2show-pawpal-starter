"""Temporary CLI testing ground for the PawPal+ logic layer.

Run with:  python main.py

Builds a small owner/pet/task setup and prints today's schedule so we can verify
the backend works before wiring it into the Streamlit UI.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # Owner with two pets.
    owner = Owner(name="Jordan", preferences={"available_minutes": 120})
    mochi = Pet(name="Mochi", species="cat")
    rex = Pet(name="Rex", species="dog")
    owner.add_pet(mochi)
    owner.add_pet(rex)

    # At least three tasks with different preferred times and priorities.
    owner.add_task(rex, Task("Morning walk", duration_minutes=30, priority="high", time="08:00"))
    owner.add_task(rex, Task("Evening walk", duration_minutes=25, priority="medium", time="18:00"))
    owner.add_task(mochi, Task("Feed Mochi", duration_minutes=10, priority="high", time="07:30"))
    owner.add_task(mochi, Task("Play / enrichment", duration_minutes=15, priority="low", time="16:00"))

    # Build and print today's schedule.
    scheduler = Scheduler(available_minutes=owner.preferences["available_minutes"], start_time="07:30")
    plan = scheduler.build_plan(owner.all_tasks())

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for item in plan:
        t = item.task
        print(f"{item.start_time}-{item.end_time}  {t.description:<20} ({t.duration_minutes:>2} min) [{t.priority}]")
    print("=" * 40)
    print(scheduler.explain(plan))


if __name__ == "__main__":
    main()
