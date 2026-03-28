# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

PawPal+ includes an algorithmic scheduling layer with four features:

- **Sort by scheduled time** — Tasks can have an optional `time` (HH:MM format). The scheduler sorts tasks chronologically, placing unscheduled tasks at the end.
- **Filter by pet or status** — Retrieve tasks filtered by pet name, completion status (`"pending"` / `"completed"`), or both.
- **Recurring task auto-renewal** — Tasks can have a `frequency` of `"daily"` or `"weekly"`. When a recurring task is marked complete, a new pending copy is automatically created for the next occurrence.
- **Time conflict detection** — The scheduler scans all tasks and warns when two or more tasks are scheduled at the exact same time.

## Testing PawPal+

### Run the tests

```bash
python -m pytest
```

### Run the demo

```bash
python main.py
```

### What the tests cover

- **Mark complete** — verifies `mark_complete()` flips status to completed
- **Add task** — confirms adding a task increases the pet's task count
- **Sort by time** — checks chronological ordering with unscheduled tasks last
- **Recurrence** — ensures a daily task produces a new pending copy on completion
- **Conflict detection** — validates warnings when two tasks share the same time
- **Filtering** — tests filtering by pet name, by status, and by both combined
- **Pet with no tasks** — edge case: empty pet produces no conflicts and an empty plan
- **Three-way time conflict** — edge case: three tasks at the exact same time yield three pairwise warnings
- **Once-task returns None** — non-recurring task returns `None` from `mark_complete()`
- **All unscheduled sort** — sorting tasks that all lack a time works without error
- **Remove task** — removing by name decreases count; missing name returns `False`
- **Invalid category** — creating a Task with a bad category raises `ValueError`

**Confidence:** The test suite covers core scheduling behaviors (sorting, filtering, recurrence, conflicts), basic CRUD operations, and edge cases (empty inputs, invalid data, multi-way conflicts).

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
