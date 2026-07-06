"""Quick tests for the PawPal+ logic layer."""

from datetime import date, timedelta

from pawpal_system import Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task's completed flag to True."""
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet(name="Rex", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feed Rex", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1


def test_sort_by_time_orders_chronologically_untimed_last():
    """sort_by_time() orders by HH:MM and pushes untimed tasks to the end."""
    tasks = [
        Task("Evening", time="18:00"),
        Task("Anytime", time=None),
        Task("Morning", time="08:00"),
    ]
    ordered = [t.description for t in Scheduler.sort_by_time(tasks)]
    assert ordered == ["Morning", "Evening", "Anytime"]


def test_filter_by_status_returns_matching_tasks():
    """filter_by_status() keeps only tasks whose completed flag matches."""
    done = Task("Done", completed=True)
    todo = Task("Todo", completed=False)
    assert Scheduler.filter_by_status([done, todo], completed=False) == [todo]
    assert Scheduler.filter_by_status([done, todo], completed=True) == [done]


def test_detect_conflicts_flags_same_time_only():
    """detect_conflicts() warns on exact time clashes and ignores unique times."""
    scheduler = Scheduler()
    tasks = [
        Task("Walk", time="08:00"),
        Task("Meds", time="08:00"),
        Task("Feed", time="09:00"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_complete_task_reschedules_recurring():
    """complete_task() marks a daily task done and creates tomorrow's occurrence."""
    scheduler = Scheduler()
    pet = Pet(name="Rex", species="dog")
    walk = Task("Walk", frequency="daily", due_date=date.today())
    pet.add_task(walk)

    follow_up = scheduler.complete_task(pet, walk)

    assert walk.completed is True
    assert follow_up is not None
    assert follow_up.completed is False
    assert follow_up.due_date == date.today() + timedelta(days=1)
    assert len(pet.tasks) == 2


def test_complete_task_does_not_reschedule_one_off():
    """complete_task() returns None and adds nothing for a non-recurring task."""
    scheduler = Scheduler()
    pet = Pet(name="Rex", species="dog")
    task = Task("One-off vet visit", frequency="once")
    pet.add_task(task)

    follow_up = scheduler.complete_task(pet, task)

    assert follow_up is None
    assert len(pet.tasks) == 1
