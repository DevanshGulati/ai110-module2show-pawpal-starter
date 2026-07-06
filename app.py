import streamlit as st

# Step 1: Bring the logic-layer classes into the UI.
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care based on time, priority, and preferences.")

# Step 2: Persist the Owner in session_state so it survives every rerun.
# Streamlit re-runs this script top-to-bottom on each interaction, so we only
# create a fresh Owner the first time and reuse the stored one afterwards.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

# --- Owner info --------------------------------------------------------------
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Add a pet (Step 3: wire the form to Owner.add_pet) ----------------------
st.subheader("Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name} the {species}.")
        else:
            st.warning("Please enter a pet name.")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")
    st.stop()

# --- Add a task to a pet (Step 3: wire the form to Owner.add_task) -----------
st.subheader("Add a task")
pet_names = [pet.name for pet in owner.pets]
with st.form("add_task_form", clear_on_submit=True):
    selected_pet_name = st.selectbox("For which pet?", pet_names)
    task_desc = st.text_input("Task description", value="Morning walk")
    col1, col2, col3 = st.columns(3)
    with col1:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col3:
        preferred_time = st.text_input("Preferred time", value="08:00")
    if st.form_submit_button("Add task"):
        pet = next(p for p in owner.pets if p.name == selected_pet_name)
        owner.add_task(
            pet,
            Task(
                description=task_desc.strip(),
                duration_minutes=int(duration),
                priority=priority,
                time=preferred_time.strip() or None,
            ),
        )
        st.success(f"Added '{task_desc}' for {selected_pet_name}.")

# --- Show current pets and their tasks ---------------------------------------
st.subheader("Current pets & tasks")
for pet in owner.pets:
    with st.expander(f"{pet.name} ({pet.species}) — {len(pet.tasks)} task(s)", expanded=True):
        if pet.tasks:
            st.table(
                [
                    {
                        "Task": t.description,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                        "Preferred time": t.time or "—",
                        "Done": "✅" if t.completed else "",
                    }
                    for t in pet.tasks
                ]
            )
        else:
            st.caption("No tasks for this pet yet.")

st.divider()

# --- Build the schedule (Step 3: call the Scheduler) -------------------------
st.subheader("Build schedule")
col1, col2 = st.columns(2)
with col1:
    available = st.number_input("Available minutes today", min_value=1, max_value=1440, value=120)
with col2:
    start_time = st.text_input("Start time", value="08:00")

if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(available_minutes=int(available), start_time=start_time.strip() or "08:00")
    plan = scheduler.build_plan(owner.all_tasks())
    if not plan:
        st.warning("No tasks could be scheduled within the available time.")
    else:
        st.markdown(f"### Today's plan for {owner.name}")
        st.table(
            [
                {
                    "Start": item.start_time,
                    "End": item.end_time,
                    "Task": item.task.description,
                    "Duration (min)": item.task.duration_minutes,
                    "Priority": item.task.priority,
                }
                for item in plan
            ]
        )
        with st.expander("Why this plan?"):
            st.text(scheduler.explain(plan))
