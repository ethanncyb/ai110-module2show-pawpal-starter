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




---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
