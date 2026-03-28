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

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
