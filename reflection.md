# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My UML design includes four classes (see [pawpal_class_diagram.md](pawpal_class_diagram.md) for the full Mermaid diagram):

- **Task** — Represents a single care activity (e.g., walk, feeding, medication). Each task has a name, category, duration, priority, and optional notes. This is the core unit of work the scheduler operates on.
- **Pet** — Stores the pet's name, species, and any special needs. Holds a list of Tasks with methods to add, remove, and filter them.
- **Owner** — Stores the owner's name and total available time per day. Holds a reference to one Pet. Responsible for holding the time constraint that the scheduler uses.
- **Scheduler** — Takes an Owner (with a Pet and Tasks), sorts tasks by priority, fits them into the time budget, and returns a plan dictionary with scheduled tasks, dropped tasks, utilization, and a human-readable explanation.

Relationships: An Owner has one Pet. A Pet has many Tasks. The Scheduler reads constraints from the Owner and produces a plan.

**Core user actions:**

1. **Add a pet and owner profile** — The user enters basic information about themselves (name, time available) and their pet (name, species, any special needs). This grounds every other action in the app — tasks and schedules are meaningless without knowing *whose* pet we are planning for and how much time the owner has.

2. **Add and edit care tasks** — The user creates care tasks such as walks, feeding, medication, grooming, or enrichment. Each task has at least a duration and a priority level. The user can also edit existing tasks to adjust these values. This is the primary way the owner communicates *what* needs to happen each day.

3. **Generate a daily plan** — The user requests a schedule that fits their tasks into the available time, ordered by priority and respecting constraints. The app displays the resulting plan clearly and explains *why* it made the choices it did (e.g., why a high-priority medication task was scheduled before a lower-priority enrichment activity, or why a task was dropped if time ran out).

**b. Design changes**

Yes, the design changed during implementation. Originally I considered a fifth class, **DailyPlan**, to hold the scheduler's output (scheduled tasks, dropped tasks, utilization, and an explanation). However, I decided to keep the design simpler with only four classes. Instead of a separate DailyPlan class, the Scheduler's `generate_plan()` method returns a plain dictionary containing the scheduled tasks, dropped tasks, minutes used, utilization percentage, and a human-readable explanation string. This keeps the codebase leaner — a dedicated class was not necessary when a dictionary conveys the same information without extra overhead.

After asking AI to review my skeleton (`pawpal_system.py`), it flagged two minor points:

1. **Duplicate task names** — `Pet.remove_task()` matches by name, but nothing prevents two tasks from sharing the same name. If duplicates exist, only the first match is removed. I kept this as-is for simplicity since in practice a pet owner is unlikely to create two identically named tasks.
2. **Pet reassignment after Scheduler init** — The Scheduler checks that `owner.pet` is not `None` at construction time, but if the pet were reassigned to `None` afterwards, `generate_plan()` would crash. This is an acceptable tradeoff because the Scheduler is meant to be short-lived: create it, generate a plan, and discard it.

Neither issue warranted a code change, but documenting them shows awareness of the design's limits.

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
