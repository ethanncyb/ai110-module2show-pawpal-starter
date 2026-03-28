"""Tests for PawPal+ backend logic."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    """Calling mark_complete() should set completed to True."""
    task = Task("Morning walk", "exercise", 20)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task count."""
    pet = Pet("Buddy", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Breakfast", "feeding", 10))
    assert len(pet.get_tasks()) == 1


def test_sort_by_time_chronological_order():
    """sort_by_time should order tasks by HH:MM; unscheduled tasks go last."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    t1 = Task("Dinner", "feeding", 10, time="18:00")
    t2 = Task("Breakfast", "feeding", 10, time="08:00")
    t3 = Task("No time task", "other", 5)  # unscheduled
    t4 = Task("Lunch", "feeding", 10, time="12:00")

    result = scheduler.sort_by_time([t1, t2, t3, t4])

    assert result[0].name == "Breakfast"
    assert result[1].name == "Lunch"
    assert result[2].name == "Dinner"
    assert result[3].name == "No time task"  # unscheduled last


def test_recurrence_creates_new_task():
    """Marking a daily task complete should return a new pending Task."""
    task = Task("Morning walk", "exercise", 20, frequency="daily")
    new_task = task.mark_complete()

    assert task.completed is True
    assert new_task is not None
    assert new_task.completed is False
    assert new_task.name == task.name
    assert new_task.category == task.category
    assert new_task.duration_minutes == task.duration_minutes
    assert new_task.frequency == "daily"


def test_detect_conflicts():
    """Two tasks at the same time should produce a conflict warning."""
    owner = Owner("Alice", 120)
    pet1 = Pet("Buddy", "dog")
    pet2 = Pet("Whiskers", "cat")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    pet1.add_task(Task("Walk Buddy", "exercise", 30, time="09:00"))
    pet2.add_task(Task("Feed Whiskers", "feeding", 15, time="09:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) >= 1
    assert "09:00" in conflicts[0]


def test_filter_tasks_by_pet_and_status():
    """filter_tasks should narrow results by pet name and status."""
    owner = Owner("Alice", 120)
    pet1 = Pet("Buddy", "dog")
    pet2 = Pet("Whiskers", "cat")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    t1 = Task("Walk", "exercise", 30)
    t2 = Task("Feed", "feeding", 10)
    t1.mark_complete()
    pet1.add_task(t1)
    pet1.add_task(t2)
    pet2.add_task(Task("Groom", "grooming", 20))

    scheduler = Scheduler(owner)

    # Filter by pet name
    buddy_tasks = scheduler.filter_tasks(pet_name="Buddy")
    assert len(buddy_tasks) == 2

    # Filter by status
    pending = scheduler.filter_tasks(status="pending")
    assert all(not t.completed for t in pending)

    # Filter by both
    buddy_completed = scheduler.filter_tasks(pet_name="Buddy", status="completed")
    assert len(buddy_completed) == 1
    assert buddy_completed[0].name == "Walk"


# ── Edge-case tests ─────────────────────────────────────────────────


def test_pet_with_no_tasks():
    """A pet with zero tasks should return empty lists and no conflicts."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    assert pet.get_tasks() == []
    assert scheduler.filter_tasks(pet_name="Buddy") == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.sort_by_time([]) == []

    plan = scheduler.generate_plan()
    assert plan["scheduled_tasks"] == []
    assert plan["total_minutes_used"] == 0


def test_three_tasks_same_time_produces_multiple_conflicts():
    """Three tasks at the exact same time should produce three pairwise conflicts."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    pet.add_task(Task("Walk", "exercise", 20, time="09:00"))
    pet.add_task(Task("Feed", "feeding", 10, time="09:00"))
    pet.add_task(Task("Meds", "medication", 5, time="09:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()

    # 3 tasks => C(3,2) = 3 pairwise conflicts
    assert len(conflicts) == 3
    assert all("09:00" in c for c in conflicts)


def test_once_task_returns_none_on_complete():
    """A non-recurring (once) task should return None from mark_complete."""
    task = Task("Vet visit", "medication", 60, frequency="once")
    result = task.mark_complete()

    assert task.completed is True
    assert result is None


def test_sort_by_time_all_unscheduled():
    """Sorting tasks that all lack a time should preserve them without error."""
    owner = Owner("Alice", 60)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    tasks = [
        Task("Play", "enrichment", 15),
        Task("Brush", "grooming", 10),
    ]
    result = scheduler.sort_by_time(tasks)

    assert len(result) == 2  # nothing dropped or crashed


def test_remove_task_from_pet():
    """Removing a task by name should decrease count; missing name returns False."""
    pet = Pet("Buddy", "dog")
    pet.add_task(Task("Walk", "exercise", 30))
    pet.add_task(Task("Feed", "feeding", 10))

    assert pet.remove_task("Walk") is True
    assert len(pet.get_tasks()) == 1
    assert pet.remove_task("Nonexistent") is False


def test_invalid_category_raises():
    """Creating a Task with an invalid category should raise ValueError."""
    import pytest

    with pytest.raises(ValueError):
        Task("Bad task", "swimming", 10)


# ── suggest_time tests ───────────────────────────────────────────────


def _make_scheduler_with_tasks(tasks_for_pet: list[Task]) -> Scheduler:
    """Helper: create an Owner/Pet/Scheduler with the given tasks."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    for t in tasks_for_pet:
        pet.add_task(t)
    return Scheduler(owner)


def test_suggest_time_empty_schedule():
    """An empty schedule should suggest day_start as the first slot."""
    scheduler = _make_scheduler_with_tasks([])
    slots = scheduler.suggest_time(30)
    assert "06:00" in slots


def test_suggest_time_one_task():
    """One task at 08:00 (20 min) should suggest 06:00 and a slot at 08:20+."""
    scheduler = _make_scheduler_with_tasks([
        Task("Walk", "exercise", 20, time="08:00"),
    ])
    slots = scheduler.suggest_time(20)
    assert "06:00" in slots
    assert "08:20" in slots


def test_suggest_time_back_to_back_no_gap():
    """Back-to-back tasks with no gap should not suggest a slot between them."""
    scheduler = _make_scheduler_with_tasks([
        Task("Walk", "exercise", 60, time="06:00"),
        Task("Feed", "feeding", 60, time="07:00"),
    ])
    slots = scheduler.suggest_time(30)
    # No slot before 08:00 (both hours are occupied from 06:00–08:00)
    assert "06:00" not in slots
    assert "07:00" not in slots
    assert "08:00" in slots


def test_suggest_time_full_day():
    """A fully packed day should return an empty list."""
    scheduler = _make_scheduler_with_tasks([
        Task("Block", "other", 960, time="06:00"),  # 06:00–22:00 = 960 min
    ])
    slots = scheduler.suggest_time(30)
    assert slots == []


def test_suggest_time_exact_fit():
    """A task that fits exactly in a gap should be included."""
    scheduler = _make_scheduler_with_tasks([
        Task("Early", "exercise", 60, time="06:00"),   # 06:00–07:00
        Task("Late", "exercise", 60, time="07:30"),     # 07:30–08:30
    ])
    # 30-min gap from 07:00–07:30
    slots = scheduler.suggest_time(30)
    assert "07:00" in slots
