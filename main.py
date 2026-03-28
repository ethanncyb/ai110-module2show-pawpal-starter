"""PawPal+ Demo — verifies the backend logic in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup ────────────────────────────────────────────────────────────
owner = Owner("Alice", available_minutes=60)

# Pet 1: a dog
dog = Pet("Buddy", "dog", special_needs="bad knees")
dog.add_task(Task("Morning walk", "exercise", 20, priority=2))
dog.add_task(Task("Heartworm pill", "medication", 5, priority=1))
dog.add_task(Task("Brushing", "grooming", 15, priority=4))

# Pet 2: a cat
cat = Pet("Whiskers", "cat")
cat.add_task(Task("Breakfast", "feeding", 10, priority=1))
cat.add_task(Task("Puzzle toy", "enrichment", 20, priority=5))

owner.add_pet(dog)
owner.add_pet(cat)

# ── Generate and display the daily plan ──────────────────────────────
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

print("=" * 50)
print(f"  Today's Schedule for {owner.name}")
print(f"  Pets: {', '.join(p.name for p in owner.get_pets())}")
print("=" * 50)
print(plan["explanation"])
print()

# ── Demo: mark a task complete ───────────────────────────────────────
first_task = plan["scheduled_tasks"][0]
print(f"Marking '{first_task.name}' as complete...")
first_task.mark_complete()
print(f"  {first_task}")
