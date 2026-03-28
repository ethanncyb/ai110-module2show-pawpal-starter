"""PawPal+ Logic Layer — all backend classes in one module.

Classes: Task, Pet, Owner, Scheduler
Based on the PawPal+ UML class diagram.
"""

VALID_CATEGORIES = {"feeding", "exercise", "medication", "grooming", "enrichment", "other"}


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
    ):
        """Create a task with validated category, duration, and priority."""
        if category not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if not 1 <= priority <= 5:
            raise ValueError("priority must be between 1 (critical) and 5 (nice-to-have)")

        self.name = name
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.notes = notes
        self.completed = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
