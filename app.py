import os
import streamlit as st
import pandas as pd
from pawpal_system import Owner, Pet, Task, Scheduler, VALID_CATEGORIES, VALID_FREQUENCIES

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant that schedules your day.")

# ── Session state: persist Owner across reruns ───────────────────────
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    else:
        st.session_state.owner = None

# ── Step 1: Owner profile ───────────────────────────────────────────
st.subheader("Owner Profile")

if st.session_state.owner is None:
    with st.form("owner_form"):
        owner_name = st.text_input("Your name", value="Jordan")
        available = st.number_input(
            "Available minutes per day", min_value=1, max_value=480, value=60
        )
        submitted = st.form_submit_button("Create profile")
        if submitted:
            st.session_state.owner = Owner(owner_name, int(available))
            st.session_state.owner.save_to_json(DATA_FILE)
            st.rerun()
else:
    owner = st.session_state.owner
    st.success(f"Owner: **{owner.name}** — {owner.available_minutes} min/day")

    if st.button("Reset data"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.session_state.owner = None
        st.rerun()

    # ── Step 2: Add pets ─────────────────────────────────────────────
    st.divider()
    st.subheader("Pets")

    with st.form("pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Pet name", value="Mochi")
        with col2:
            species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
        special_needs = st.text_input("Special needs (optional)", value="")
        add_pet = st.form_submit_button("Add pet")
        if add_pet and pet_name:
            owner.add_pet(Pet(pet_name, species, special_needs))
            owner.save_to_json(DATA_FILE)
            st.rerun()

    if owner.get_pets():
        for pet in owner.get_pets():
            st.write(f"**{pet.name}** ({pet.species})"
                     + (f" — {pet.special_needs}" if pet.special_needs else ""))
    else:
        st.info("No pets yet. Add one above.")

    # ── Step 3: Add tasks to a pet ───────────────────────────────────
    if owner.get_pets():
        st.divider()
        st.subheader("Tasks")

        pet_names = [p.name for p in owner.get_pets()]
        selected_pet_name = st.selectbox("Select pet", pet_names)
        selected_pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)

        with st.form("task_form"):
            col1, col2 = st.columns(2)
            with col1:
                task_name = st.text_input("Task name", value="Morning walk")
                category = st.selectbox("Category", sorted(VALID_CATEGORIES))
                time_input = st.text_input("Time (HH:MM, optional)", value="")
            with col2:
                duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
                priority = st.slider("Priority (1=critical, 5=nice-to-have)", 1, 5, 3)
                frequency = st.selectbox("Frequency", sorted(VALID_FREQUENCIES))
            notes = st.text_input("Notes (optional)", value="")
            add_task = st.form_submit_button("Add task")
            if add_task and task_name:
                try:
                    selected_pet.add_task(
                        Task(task_name, category, int(duration), priority, notes,
                             time=time_input, frequency=frequency)
                    )
                    owner.save_to_json(DATA_FILE)
                    st.rerun()
                except ValueError:
                    st.error("Invalid time format. Please use HH:MM (e.g. 08:30).")

        # Show current tasks in a table
        tasks = selected_pet.get_tasks()
        if tasks:
            st.write(f"**{selected_pet.name}'s tasks:**")
            task_rows = []
            for idx, t in enumerate(tasks):
                task_rows.append({
                    "Status": "✅" if t.completed else "⬜",
                    "Name": t.name,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                    "Category": t.category,
                    "Time": t.time or "—",
                    "Frequency": t.frequency,
                })
            st.table(pd.DataFrame(task_rows))

            # Mark complete buttons
            st.write("**Mark tasks complete:**")
            for idx, t in enumerate(tasks):
                if not t.completed:
                    if st.button(f"Complete: {t.name}", key=f"complete_{selected_pet.name}_{idx}"):
                        renewal = t.mark_complete()
                        if renewal:
                            selected_pet.add_task(renewal)
                            st.toast(f"Recurring task '{t.name}' renewed!")
                        else:
                            st.toast(f"'{t.name}' marked complete!")
                        owner.save_to_json(DATA_FILE)
                        st.rerun()
        else:
            st.info(f"No tasks for {selected_pet.name} yet.")

        # ── Step 4: Filter tasks ───────────────────────────────────────
        st.divider()
        st.subheader("Filter Tasks")

        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names, key="filter_pet")
        with filter_col2:
            filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"], key="filter_status")

        try:
            scheduler = Scheduler(owner)
            pet_filter = None if filter_pet == "All" else filter_pet
            status_filter = None if filter_status == "All" else filter_status.lower()
            filtered = scheduler.filter_tasks(pet_name=pet_filter, status=status_filter)

            if filtered:
                filter_rows = []
                for t in filtered:
                    filter_rows.append({
                        "Status": "✅" if t.completed else "⬜",
                        "Name": t.name,
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": t.priority,
                        "Category": t.category,
                        "Time": t.time or "—",
                        "Frequency": t.frequency,
                    })
                st.table(pd.DataFrame(filter_rows))
            else:
                st.info("No tasks match the current filters.")
        except ValueError:
            st.info("Add at least one pet to use filters.")

        # ── Step 5: Suggest available time slots ─────────────────────────
        st.divider()
        st.subheader("Suggest Time")

        suggest_col1, suggest_col2 = st.columns(2)
        with suggest_col1:
            suggest_duration = st.number_input(
                "Task duration (min)", min_value=1, max_value=240, value=20, key="suggest_dur"
            )
        with suggest_col2:
            suggest_start = st.text_input("Day start (HH:MM)", value="06:00", key="suggest_start")
            suggest_end = st.text_input("Day end (HH:MM)", value="22:00", key="suggest_end")

        if st.button("Find available slots"):
            try:
                scheduler = Scheduler(owner)
                slots = scheduler.suggest_time(int(suggest_duration), suggest_start, suggest_end)
                if slots:
                    st.info("Available slots for a **{} min** task:".format(suggest_duration))
                    for slot in slots:
                        st.write(f"  - {slot}")
                else:
                    st.warning("No available slots found for that duration.")
            except ValueError as e:
                st.error(str(e))

        # ── Step 6: Generate schedule ──────────────────────────────────
        st.divider()
        st.subheader("Daily Schedule")

        if st.button("Generate schedule"):
            try:
                scheduler = Scheduler(owner)
                plan = scheduler.generate_plan()

                # Utilization metric
                st.metric(
                    "Time Utilization",
                    f"{plan['utilization_pct']:.0f}%",
                    f"{plan['total_minutes_used']} of {plan['total_minutes_available']} min used",
                )

                # Scheduled tasks table
                if plan["scheduled_tasks"]:
                    st.subheader("Scheduled Tasks")
                    sched_rows = []
                    for i, t in enumerate(plan["scheduled_tasks"], 1):
                        sched_rows.append({
                            "#": i,
                            "Name": t.name,
                            "Duration": f"{t.duration_minutes} min",
                            "Priority": t.priority,
                            "Category": t.category,
                            "Time": t.time or "—",
                        })
                    st.table(pd.DataFrame(sched_rows))

                # Dropped tasks warning
                if plan["dropped_tasks"]:
                    st.warning("**Dropped tasks** (not enough time):")
                    for t in plan["dropped_tasks"]:
                        st.warning(f"  ↳ {t.name} — {t.duration_minutes} min (priority {t.priority})")

                # Sorted by time
                all_scheduled = plan["scheduled_tasks"]
                if all_scheduled:
                    sorted_tasks = scheduler.sort_by_time(all_scheduled)
                    st.subheader("Sorted by Time")
                    time_rows = []
                    for t in sorted_tasks:
                        time_rows.append({
                            "Time": t.time or "—",
                            "Name": t.name,
                            "Duration": f"{t.duration_minutes} min",
                            "Priority": t.priority,
                            "Category": t.category,
                        })
                    st.table(pd.DataFrame(time_rows))

                # Conflict detection
                conflicts = scheduler.detect_conflicts()
                if conflicts:
                    st.subheader("Scheduling Conflicts")
                    for c in conflicts:
                        st.warning(c)
                else:
                    st.success("No scheduling conflicts detected!")

                st.success("Schedule generated successfully!")

            except ValueError as e:
                st.error(str(e))
