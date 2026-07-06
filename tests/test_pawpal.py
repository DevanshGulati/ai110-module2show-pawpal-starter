"""Quick tests for the PawPal+ logic layer."""

from pawpal_system import Pet, Task


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
