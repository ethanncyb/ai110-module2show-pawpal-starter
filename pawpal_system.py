"""PawPal+ Logic Layer — all backend classes in one module.

Classes: Task, Pet, Owner, Scheduler
Based on the PawPal+ UML class diagram.
"""

import re
from datetime import timedelta

VALID_CATEGORIES = {"feeding", "exercise", "medication", "grooming", "enrichment", "other"}
VALID_FREQUENCIES = {"once", "daily", "weekly"}


# ── Task ─────────────────────────────────────────────────────────────
class Task:
    """A single pet care activity."""

    def __init__(
        self,
        name: str,
        category: str,
        duration_minutes: int,
        priority: int = 3,
        notes: str = "",
        time: str = "",
        frequency: str = "once",
    ):
        """Create a task with validated category, duration, and priority."""
        if category not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if not 1 <= priority <= 5:
            raise ValueError("priority must be between 1 (critical) and 5 (nice-to-have)")
        if time and not re.match(r"^\d{2}:\d{2}$", time):
            raise ValueError("time must be in HH:MM format")
        if frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}")

        self.name = name
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.notes = notes
        self.time = time
        self.frequency = frequency
        self.completed = False

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed. Returns a new Task if recurring, else None."""
        self.completed = True
        if self.frequency in ("daily", "weekly"):
            delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
            return Task(
                name=self.name,
                category=self.category,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                notes=f"(auto-renewed, next in {delta.days} day{'s' if delta.days != 1 else ''})",
                time=self.time,
                frequency=self.frequency,
            )
        return None

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        status = "done" if self.completed else "pending"
        return f"Task({self.name!r}, {self.category}, {self.duration_minutes}min, p{self.priority}, {status})"


# ── Pet ──────────────────────────────────────────────────────────────
class Pet:
    """A pet with a list of care tasks."""

    def __init__(self, name: str, species: str, special_needs: str = ""):
        """Create a pet profile."""
        self.name = name
        self.species = species
        self.special_needs = special_needs
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> bool:
        """Remove the first task matching the given name; return True if found."""
        for i, t in enumerate(self.tasks):
            if t.name == task_name:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return a copy of all tasks."""
        return list(self.tasks)

    def get_tasks_by_category(self, category: str) -> list[Task]:
        """Return tasks filtered by category."""
        return [t for t in self.tasks if t.category == category]


# ── Owner ────────────────────────────────────────────────────────────
class Owner:
    """The pet owner with a daily time budget and one or more pets."""

    def __init__(self, name: str, available_minutes: int):
        """Create an owner with a daily time budget."""
        if available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return the list of pets."""
        return self.pets


# ── Scheduler ────────────────────────────────────────────────────────
class Scheduler:
    """Greedy priority-first scheduler that fits tasks into an Owner's time budget."""

    def __init__(self, owner: Owner):
        """Create a scheduler for the given owner; owner must have at least one pet."""
        if not owner.pets:
            raise ValueError("Owner must have at least one pet before scheduling")
        self.owner = owner

    def generate_plan(self) -> dict:
        """Return a plan dict with scheduled/dropped tasks and a summary."""
        # Gather tasks from ALL pets
        all_tasks: list[Task] = []
        for pet in self.owner.pets:
            all_tasks.extend(pet.get_tasks())

        sorted_tasks = self._sort_by_priority(all_tasks)
        scheduled, dropped, minutes_used = self._fit_tasks(
            sorted_tasks, self.owner.available_minutes
        )
        available = self.owner.available_minutes
        utilization = (minutes_used / available * 100) if available else 0.0

        # Build explanation
        lines = [
            f"Plan uses {minutes_used} of {available} "
            f"available minutes ({utilization:.0f}% utilization)."
        ]
        if scheduled:
            lines.append("\nScheduled tasks (highest priority first):")
            for i, t in enumerate(scheduled, 1):
                lines.append(f"  {i}. {t.name} — {t.duration_minutes} min (priority {t.priority}, {t.category})")
        if dropped:
            lines.append("\nDropped tasks (not enough time):")
            for t in dropped:
                lines.append(f"  - {t.name} — {t.duration_minutes} min (priority {t.priority}, {t.category})")
        if not scheduled:
            lines.append("\nNo tasks could be scheduled. Check your time budget or task durations.")

        return {
            "scheduled_tasks": scheduled,
            "dropped_tasks": dropped,
            "total_minutes_used": minutes_used,
            "total_minutes_available": available,
            "utilization_pct": utilization,
            "explanation": "\n".join(lines),
        }

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (1 = critical first)."""
        return sorted(tasks, key=lambda t: t.priority)

    def _fit_tasks(
        self, sorted_tasks: list[Task], available: int
    ) -> tuple[list[Task], list[Task], int]:
        """Greedily fit tasks into the time budget; return (scheduled, dropped, used)."""
        scheduled: list[Task] = []
        dropped: list[Task] = []
        minutes_used = 0
        for task in sorted_tasks:
            if minutes_used + task.duration_minutes <= available:
                scheduled.append(task)
                minutes_used += task.duration_minutes
            else:
                dropped.append(task)
        return scheduled, dropped, minutes_used

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by scheduled time (HH:MM). Tasks without a time go last."""
        return sorted(tasks, key=lambda t: (t.time == "", t.time))

    def filter_tasks(self, pet_name: str | None = None, status: str | None = None) -> list[Task]:
        """Filter tasks across all pets by pet name and/or completion status."""
        results: list[Task] = []
        for pet in self.owner.pets:
            if pet_name and pet.name != pet_name:
                continue
            for task in pet.get_tasks():
                if status == "completed" and not task.completed:
                    continue
                if status == "pending" and task.completed:
                    continue
                results.append(task)
        return results

    def detect_conflicts(self) -> list[str]:
        """Return warnings for tasks scheduled at the same time."""
        timed: dict[str, list[str]] = {}
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                if task.time:
                    timed.setdefault(task.time, []).append(task.name)
        warnings: list[str] = []
        for time_slot, names in sorted(timed.items()):
            if len(names) > 1:
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        warnings.append(
                            f"Conflict: '{names[i]}' and '{names[j]}' are both at {time_slot}"
                        )
        return warnings
