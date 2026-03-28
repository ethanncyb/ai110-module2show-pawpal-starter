"""PawPal+ Demo — exercises all backend features in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup ────────────────────────────────────────────────────────────
owner = Owner("Alice", available_minutes=90)

dog = Pet("Buddy", "dog", special_needs="bad knees")
dog.add_task(Task("Brushing", "grooming", 15, priority=4, time="09:00"))
dog.add_task(Task("Heartworm pill", "medication", 5, priority=1, time="07:00"))
dog.add_task(Task("Morning walk", "exercise", 20, priority=2, time="08:00"))

cat = Pet("Whiskers", "cat")
cat.add_task(Task("Breakfast", "feeding", 10, priority=1, time="08:00"))
cat.add_task(Task("Puzzle toy", "enrichment", 20, priority=5))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)

# ── 1. Sort by scheduled time ────────────────────────────────────────
all_tasks = []
for pet in owner.get_pets():
    all_tasks.extend(pet.get_tasks())

print("=" * 55)
print("  1. Tasks sorted by scheduled time")
print("=" * 55)
for t in scheduler.sort_by_time(all_tasks):
    time_str = t.time if t.time else "no time"
    print(f"  {time_str:>8}  {t.name} ({t.category}, p{t.priority})")
print()

# ── 2. Filter tasks ──────────────────────────────────────────────────
print("=" * 55)
print("  2. Filter tasks")
print("=" * 55)

print("\n  Buddy's tasks only:")
for t in scheduler.filter_tasks(pet_name="Buddy"):
    print(f"    - {t}")

# Mark one task complete for filtering demo
dog.get_tasks()[1].mark_complete()  # Heartworm pill

print("\n  Pending tasks only (after completing Heartworm pill):")
for t in scheduler.filter_tasks(status="pending"):
    print(f"    - {t}")

print("\n  Completed tasks only:")
for t in scheduler.filter_tasks(status="completed"):
    print(f"    - {t}")
print()

# ── 3. Recurring task demo ───────────────────────────────────────────
print("=" * 55)
print("  3. Recurring task (daily feeding)")
print("=" * 55)
daily_feed = Task("Evening feed", "feeding", 10, priority=1, time="18:00", frequency="daily")
cat.add_task(daily_feed)
print(f"\n  Created: {daily_feed}")
print(f"  Frequency: {daily_feed.frequency}")

next_task = daily_feed.mark_complete()
print(f"  After marking complete: {daily_feed}")
if next_task:
    print(f"  Auto-renewed task: {next_task}")
    print(f"    Notes: {next_task.notes}")
print()

# ── 4. Conflict detection ────────────────────────────────────────────
print("=" * 55)
print("  4. Conflict detection")
print("=" * 55)
conflicts = scheduler.detect_conflicts()
if conflicts:
    print()
    for warning in conflicts:
        print(f"  ⚠ {warning}")
else:
    print("\n  No conflicts found.")
print()
