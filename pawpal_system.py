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

    def __repr__(self) -> str:
        return f"Task({self.name!r}, {self.category}, {self.duration_minutes}min, p{self.priority})"


# ── Pet ──────────────────────────────────────────────────────────────
class Pet:
    """A pet with a list of care tasks."""

    def __init__(self, name: str, species: str, special_needs: str = ""):
        self.name = name
        self.species = species
        self.special_needs = special_needs
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> bool:
        for i, t in enumerate(self.tasks):
            if t.name == task_name:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        return list(self.tasks)

    def get_tasks_by_category(self, category: str) -> list[Task]:
        return [t for t in self.tasks if t.category == category]


# ── Owner ────────────────────────────────────────────────────────────
class Owner:
    """The pet owner with a daily time budget."""

    def __init__(self, name: str, available_minutes: int):
        if available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")
        self.name = name
        self.available_minutes = available_minutes
        self.pet: Pet | None = None

    def set_pet(self, pet: Pet) -> None:
        self.pet = pet

    def get_pet(self) -> Pet | None:
        return self.pet


# ── Scheduler ────────────────────────────────────────────────────────
class Scheduler:
    """Greedy priority-first scheduler that fits tasks into an Owner's time budget."""

    def __init__(self, owner: Owner):
        if owner.pet is None:
            raise ValueError("Owner must have a pet before scheduling")
        self.owner = owner

    def generate_plan(self) -> dict:
        """Return a plan dict with scheduled/dropped tasks and a summary."""
        tasks = self.owner.pet.get_tasks()
        sorted_tasks = self._sort_by_priority(tasks)
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
        return sorted(tasks, key=lambda t: t.priority)

    def _fit_tasks(
        self, sorted_tasks: list[Task], available: int
    ) -> tuple[list[Task], list[Task], int]:
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
