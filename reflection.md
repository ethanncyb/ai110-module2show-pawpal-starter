# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My UML design includes four classes (see [pawpal_class_diagram.md](pawpal_class_diagram.md) for the full Mermaid diagram):

- **Task** — Represents a single care activity (e.g., walk, feeding, medication). Each task has a name, category, duration, priority, optional notes, and a completion status. The `mark_complete()` method lets the owner check off finished tasks.
- **Pet** — Stores the pet's name, species, and any special needs. Holds a list of Tasks with methods to add, remove, and filter them.
- **Owner** — Stores the owner's name and total available time per day. Manages **multiple pets** via `add_pet()` and `get_pets()`. Responsible for holding the time constraint that the scheduler uses.
- **Scheduler** — Takes an Owner (with one or more Pets and their Tasks), gathers tasks from all pets, sorts by priority, fits them into the time budget, and returns a plan dictionary with scheduled tasks, dropped tasks, utilization, and a human-readable explanation.

Relationships: An Owner has many Pets. A Pet has many Tasks. The Scheduler reads constraints from the Owner and produces a plan.

**Core user actions:**

1. **Add a pet and owner profile** — The user enters basic information about themselves (name, time available) and their pet (name, species, any special needs). This grounds every other action in the app — tasks and schedules are meaningless without knowing *whose* pet we are planning for and how much time the owner has.

2. **Add and edit care tasks** — The user creates care tasks such as walks, feeding, medication, grooming, or enrichment. Each task has at least a duration and a priority level. The user can also edit existing tasks to adjust these values. This is the primary way the owner communicates *what* needs to happen each day.

3. **Generate a daily plan** — The user requests a schedule that fits their tasks into the available time, ordered by priority and respecting constraints. The app displays the resulting plan clearly and explains *why* it made the choices it did (e.g., why a high-priority medication task was scheduled before a lower-priority enrichment activity, or why a task was dropped if time ran out).

**b. Design changes**

Yes, the design changed during implementation based on AI review and task requirements:

1. **DailyPlan removed** — Originally I considered a fifth class, **DailyPlan**, to hold the scheduler's output. I decided to keep the design simpler — the Scheduler's `generate_plan()` returns a plain dictionary instead. A dedicated class was not necessary when a dictionary conveys the same information without extra overhead.

2. **Multi-pet support added** — The initial design had Owner holding a single Pet (`set_pet`/`get_pet`). After reviewing task requirements, I changed Owner to manage a **list of pets** (`add_pet`/`get_pets`) and updated the Scheduler to gather tasks from all pets before scheduling. This better reflects real life — many owners have more than one pet.

3. **Task completion tracking added** — The original Task class had no way to mark a task as done. I added a `completed` attribute (defaults to `False`) and a `mark_complete()` method so the UI can track which tasks the owner has finished.

After asking AI to review the skeleton, it also flagged one minor point: `Pet.remove_task()` matches by name with no uniqueness enforcement, so if duplicates exist only the first is removed. I kept this as-is for simplicity.

See the full class diagram: [pawpal_class_diagram.md](pawpal_class_diagram.md)

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three main constraints:

1. **Available time** — The owner specifies how many minutes they have per day. The scheduler must not exceed this budget. This is the hard ceiling that determines how many tasks can fit.
2. **Task priority** — Each task has a priority level (e.g., 1 = critical, 5 = nice-to-have). The scheduler sorts tasks by priority so that the most important care activities (like medication or feeding) are scheduled first, before lower-priority ones (like enrichment or extra play).
3. **Task duration** — Each task takes a certain number of minutes. The scheduler uses duration to decide whether a task fits in the remaining time budget.

I decided priority and time mattered most because the scenario describes a *busy* pet owner — they may not have time for everything, so the app must ensure the most critical tasks always get done first. Duration is the natural complement: you cannot schedule what does not fit.

**b. Tradeoffs**

One key tradeoff is that the scheduler uses a **greedy priority-first** approach: it sorts all tasks by priority and fills the time budget from highest to lowest priority. This means a large high-priority task could consume most of the available time and push out several smaller low-priority tasks, even if fitting those smaller tasks would use the time more efficiently overall.

This tradeoff is reasonable because in pet care, skipping a critical task (like giving medication) to fit in two optional tasks (like extra grooming and a bonus walk) would be a bad outcome. The owner would rather miss a nice-to-have activity than forget something their pet genuinely needs. Safety and health come first, even if it means the schedule is not perfectly optimized for total minutes used.

A second tradeoff involves the **conflict detection** algorithm. The current implementation only flags tasks with an **exact time match** — for example, two tasks both scheduled at "08:00". It does *not* consider task duration or overlapping time windows. This means a 20-minute task at "08:00" and a 15-minute task at "08:10" would **not** be flagged as conflicting, even though they overlap. I chose exact-match detection because it is simple and avoids requiring an end-time or duration-based interval calculation. For a pet-care app where most tasks are short and owners schedule them at round times, exact-match catches the most common mistake (double-booking a time slot). A future iteration could add duration-aware overlap detection for more precision.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools throughout every phase of this project:

- **Design brainstorming** — I started by describing the PawPal+ scenario to AI and asked it to suggest classes, attributes, and relationships. This helped me quickly draft the initial UML diagram with Owner, Pet, Task, and Scheduler classes. The most helpful prompts were specific ones like *"What attributes should a Task class have for a pet care scheduling app?"* rather than vague ones like *"Help me design an app."*
- **Code generation** — After finalizing the UML, I used AI to generate Python class stubs and then iteratively fill in the logic. Asking the AI to implement one method at a time (e.g., *"Write the `_fit_tasks` method that greedily fills a time budget"*) kept changes small and reviewable.
- **Debugging** — When tests failed, I pasted the error traceback and asked AI to diagnose the issue. It was especially helpful for catching off-by-one errors in the conflict detection loop and for identifying missing edge-case handling.
- **Refactoring** — After the initial implementation worked, I asked AI to review the code for simplification opportunities. It suggested combining redundant loops and improving method signatures.

**b. Judgment and verification**

One moment where I did not accept an AI suggestion was when it proposed adding a **DailyPlan** class to wrap the scheduler output. The AI generated a full class with attributes like `scheduled_tasks`, `dropped_tasks`, and `utilization_pct`, along with a `to_dict()` method. I evaluated this by considering whether the extra class added meaningful behavior or just wrapped a dictionary. Since the dictionary already conveyed all the needed information and the DailyPlan class had no real logic beyond getters, I rejected the suggestion and kept the simpler dictionary return. I verified this decision by confirming that all tests and the UI worked perfectly with the dictionary approach.

I also questioned an AI suggestion to add type-checking `isinstance()` guards in every method. After reviewing Python best practices (duck typing, EAFP), I decided explicit type checks were unnecessary overhead for this project and kept the code clean.

---

## 4. Testing and Verification

**a. What you tested**

The test suite includes 18 automated tests covering:

- **Core scheduling** — `generate_plan()` correctly sorts by priority, fits tasks into the time budget, and reports utilization. Tasks that exceed the budget are dropped.
- **Sorting** — `sort_by_time()` orders tasks chronologically by their HH:MM time, with unscheduled tasks placed last. Also tested with all-unscheduled tasks to ensure no errors.
- **Filtering** — `filter_tasks()` correctly filters by pet name, by status (pending/completed), and by both criteria combined. Returns empty lists when no matches exist.
- **Recurrence** — Marking a daily task complete returns a new pending copy with auto-renewal notes. Marking a once-only task complete returns `None`.
- **Conflict detection** — Two tasks at the same time produce one warning. Three tasks at the same time produce three pairwise warnings. A pet with no tasks produces zero conflicts.
- **CRUD operations** — Adding a task increases the pet's task count. Removing by name decreases it; removing a nonexistent name returns `False`.
- **Validation** — Creating a Task with an invalid category raises `ValueError`.

These tests are important because they verify the algorithmic correctness of the scheduling logic (the core value of the app) and guard against regressions when adding new features like recurring tasks or conflict detection.

**b. Confidence**

I am highly confident that the scheduler works correctly for the supported scenarios. The tests cover the happy path, boundary conditions (zero tasks, budget exactly filled), and error cases (invalid input). The greedy algorithm is deterministic, so the same inputs always produce the same output.

Edge cases I would test next with more time:
- Tasks with identical priority *and* identical duration (tie-breaking behavior)
- Very large numbers of tasks (performance)
- Duration-aware overlap detection (e.g., a 30-min task at 08:00 overlapping a task at 08:15)
- Concurrent mark-complete calls on the same recurring task

---

## 5. Reflection

**a. What went well**

I am most satisfied with the **greedy scheduling algorithm and conflict detection system**. The priority-based greedy approach is simple enough to understand and explain, yet powerful enough to make genuinely useful scheduling decisions. Seeing the scheduler correctly drop low-priority tasks when time runs out — while always keeping critical medication tasks — was a satisfying confirmation that the algorithm matches real-world pet care priorities. The conflict detection, while simple (exact time match), adds a practical safety layer that catches the most common scheduling mistake.

**b. What you would improve**

If I had another iteration, I would improve two things:

1. **Duration-aware overlap detection** — The current conflict detection only flags exact time matches. A smarter version would calculate time windows (start time + duration) and detect any overlapping intervals. This would catch cases like a 30-minute walk at 08:00 conflicting with grooming at 08:15.
2. **Interactive UI for task editing** — Currently tasks can only be added and marked complete. I would add inline editing (change duration, priority, or time) and drag-and-drop reordering so owners can manually adjust the schedule after the algorithm generates it.

**c. Key takeaway**

The most important thing I learned is that **AI collaboration works best when you maintain clear ownership of design decisions**. AI is excellent at generating code, suggesting patterns, and catching bugs — but the human must decide *what* to build and *why*. When I let AI drive the architecture (like the DailyPlan class suggestion), it added unnecessary complexity. When I used AI as a tool within my own design framework — asking it to implement specific methods or review specific choices — the results were consistently better. The key is to treat AI as a skilled pair programmer, not an architect: give it clear specifications and evaluate its output critically.

---

## 6. Prompt Comparison — Multi-Model (Challenge 5)

**Algorithmic task chosen:** Recurring task auto-renewal logic (`mark_complete()` method).

When a daily or weekly task is marked complete, the system must automatically create a fresh pending copy so it reappears on the next schedule. This involves cloning the task with the same attributes, resetting completion status, and attaching a descriptive note about the renewal interval.

### The Prompt (identical for both models)

> I have a `Task` class in a pet-care scheduling app. Each task has: `name`, `category`, `duration_minutes`, `priority`, `notes`, `time` (HH:MM or None), `frequency` ("once", "daily", "weekly"), and `completed` (bool).
>
> Write a `mark_complete(self)` method that:
> 1. Sets `self.completed = True`
> 2. If the task is recurring (daily or weekly), returns a **new** Task clone with the same attributes but `completed=False` and an updated note indicating when it renews (e.g., "next in 1 day" or "next in 7 days")
> 3. If the task is non-recurring ("once"), returns `None`
>
> Use Python type hints. Keep it concise and Pythonic.

---

### Claude's Response

```python
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
```

**Observations:**
- Uses `timedelta` to compute the interval, making it easy to extend to other frequencies later.
- Handles plural ("days" vs "day") in the note string.
- Single exit point for `None` at the bottom — clean flow.
- Concise: the entire method is ~12 lines.

---

### GPT-4's Response

```python
FREQUENCY_DAYS = {"daily": 1, "weekly": 7}

def mark_complete(self) -> "Task | None":
    """Mark complete and return a renewed copy for recurring tasks."""
    self.completed = True
    days = FREQUENCY_DAYS.get(self.frequency)
    if days is None:
        return None
    return Task(
        name=self.name,
        category=self.category,
        duration_minutes=self.duration_minutes,
        priority=self.priority,
        notes=f"(auto-renewed, next in {days} day{'s' if days != 1 else ''})",
        time=self.time,
        frequency=self.frequency,
    )
```

**Observations:**
- Extracts frequency-to-days mapping into a module-level constant (`FREQUENCY_DAYS`), which is more data-driven and extensible (adding "biweekly" = 14 is trivial).
- Uses `dict.get()` to handle the non-recurring case — idiomatic Python, avoids an explicit `if/in` check.
- Slightly more modular but introduces a module-level constant, which adds a small coupling concern.

---

### Comparison and Verdict

| Criterion | Claude | GPT-4 |
|-----------|--------|-------|
| Correctness | ✅ Fully correct | ✅ Fully correct |
| Readability | Clear `if/in` guard is easy to follow | `dict.get()` pattern is compact but slightly less obvious to beginners |
| Extensibility | Would need another `elif` for new frequencies | Just add a key to the dictionary — more scalable |
| Dependencies | Uses `timedelta` (standard library) | Uses a plain dict — no extra imports |
| Pythonic style | Good — uses f-strings, type hints | Slightly more Pythonic — data-driven design |
| Modularity | Self-contained method | Separates data (mapping) from logic (method) |

**Winner: GPT-4 (by a narrow margin).** Both solutions are correct, concise, and well-typed. GPT-4's version is slightly more Pythonic because it separates the frequency-to-days mapping into data rather than branching logic. This makes it easier to extend (e.g., adding a "biweekly" frequency requires zero logic changes). However, Claude's version is arguably more readable for someone unfamiliar with the `dict.get()` pattern, and the `timedelta` usage makes the intent (a time interval) more explicit than a raw integer.

In the final codebase, we used **Claude's approach** because the `timedelta` usage communicates intent clearly and our frequency options are unlikely to grow beyond two or three values, so the extensibility advantage is minimal in practice.
