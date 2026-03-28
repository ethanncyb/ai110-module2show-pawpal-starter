# PawPal+ Class Diagram

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +Pet pet
        +__init__(name: str, available_minutes: int)
        +set_pet(pet: Pet) None
        +get_pet() Pet
    }

    class Pet {
        +str name
        +str species
        +str special_needs
        +list~Task~ tasks
        +__init__(name: str, species: str, special_needs: str)
        +add_task(task: Task) None
        +remove_task(task_name: str) bool
        +get_tasks() list~Task~
        +get_tasks_by_category(category: str) list~Task~
    }

    class Task {
        +str name
        +str category
        +int duration_minutes
        +int priority
        +str notes
        +__init__(name: str, category: str, duration_minutes: int, priority: int, notes: str)
        +__repr__() str
    }

    class Scheduler {
        +Owner owner
        +__init__(owner: Owner)
        +generate_plan() dict
        -_sort_by_priority(tasks: list~Task~) list~Task~
        -_fit_tasks(sorted_tasks: list~Task~, available: int) tuple
    }

    Owner "1" --> "1" Pet : owns
    Pet "1" --> "*" Task : has
    Scheduler --> Owner : reads constraints from
    Scheduler ..> Task : sorts and fits
```

## Category values for Task

| Category    | Examples                        |
|-------------|---------------------------------|
| feeding     | Breakfast, dinner, treats       |
| exercise    | Morning walk, fetch, run        |
| medication  | Heartworm pill, eye drops       |
| grooming    | Brushing, nail trim, bath       |
| enrichment  | Puzzle toy, training session    |
| other       | Vet visit, travel               |

## Priority scale

| Value | Meaning       |
|-------|---------------|
| 1     | Critical      |
| 2     | High          |
| 3     | Medium        |
| 4     | Low           |
| 5     | Nice-to-have  |
