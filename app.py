import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, VALID_CATEGORIES

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant that schedules your day.")

# ── Session state: persist Owner across reruns ───────────────────────
if "owner" not in st.session_state:
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
            st.rerun()
else:
    owner = st.session_state.owner
    st.success(f"Owner: **{owner.name}** — {owner.available_minutes} min/day")

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
            with col2:
                duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
                priority = st.slider("Priority (1=critical, 5=nice-to-have)", 1, 5, 3)
            notes = st.text_input("Notes (optional)", value="")
            add_task = st.form_submit_button("Add task")
            if add_task and task_name:
                selected_pet.add_task(
                    Task(task_name, category, int(duration), priority, notes)
                )
                st.rerun()

        # Show current tasks for selected pet
        tasks = selected_pet.get_tasks()
        if tasks:
            st.write(f"**{selected_pet.name}'s tasks:**")
            for t in tasks:
                status = "✅" if t.completed else "⬜"
                st.write(f"{status} {t.name} — {t.duration_minutes} min, "
                         f"priority {t.priority}, {t.category}")
        else:
            st.info(f"No tasks for {selected_pet.name} yet.")

        # ── Step 4: Generate schedule ────────────────────────────────
        st.divider()
        st.subheader("Daily Schedule")

        if st.button("Generate schedule"):
            try:
                scheduler = Scheduler(owner)
                plan = scheduler.generate_plan()
                st.text(plan["explanation"])
            except ValueError as e:
                st.error(str(e))
