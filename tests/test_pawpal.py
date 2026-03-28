"""Tests for PawPal+ backend logic."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
