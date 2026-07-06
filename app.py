import streamlit as st

# Step 1: Bring the logic-layer classes into the UI.
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care based on time, priority, and preferences.")

# Persist the Owner in session_state so it survives every rerun.
# Streamlit re-runs this script top-to-bottom on each interaction, so we only
# create a fresh Owner the first time and reuse the stored one afterwards.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler()  # stateless helper for sorting / filtering / conflict checks

# --- Owner info --------------------------------------------------------------
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Add a pet (wired to Owner.add_pet) --------------------------------------
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

# --- Add a task to a pet (wired to Owner.add_task) ---------------------------
st.subheader("Add a task")
pet_names = [pet.name for pet in owner.pets]
with st.form("add_task_form", clear_on_submit=True):
    selected_pet_name = st.selectbox("For which pet?", pet_names)
    task_desc = st.text_input("Task description", value="Morning walk")
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col2:
        preferred_time = st.text_input("Preferred time (HH:MM)", value="08:00")
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    if st.form_submit_button("Add task"):
        pet = next(p for p in owner.pets if p.name == selected_pet_name)
        owner.add_task(
            pet,
            Task(
                description=task_desc.strip(),
                duration_minutes=int(duration),
                priority=priority,
                time=preferred_time.strip() or None,
                frequency=frequency,
            ),
        )
        st.success(f"Added '{task_desc}' ({frequency}) for {selected_pet_name}.")

# --- Conflict warnings (Scheduler.detect_conflicts) --------------------------
# Surface time clashes up front so the owner sees them before building a plan.
conflicts = scheduler.detect_conflicts(owner.all_tasks())
if conflicts:
    for warning in conflicts:
        st.warning(f"⚠️ {warning}", icon="⚠️")

# --- Show current pets and their tasks (sorted by time) ----------------------
st.subheader("Current pets & tasks")
for pet in owner.pets:
    with st.expander(f"{pet.name} ({pet.species}) — {len(pet.tasks)} task(s)", expanded=True):
        if pet.tasks:
            # Scheduler.sort_by_time() gives a clean chronological view.
            st.table(
                [
                    {
                        "Time": t.time or "—",
                        "Task": t.description,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                        "Frequency": t.frequency,
                        "Done": "✅" if t.completed else "",
                    }
                    for t in scheduler.sort_by_time(pet.tasks)
                ]
            )
        else:
            st.caption("No tasks for this pet yet.")

# --- Mark a task complete (demonstrates recurrence) --------------------------
st.subheader("Complete a task")
st.caption("Completing a daily/weekly task automatically schedules its next occurrence.")
open_pairs = [
    (pet, task)
    for pet in owner.pets
    for task in scheduler.filter_by_status(pet.tasks, completed=False)
]
if open_pairs:
    labels = [f"{pet.name}: {task.description} ({task.time or 'anytime'})" for pet, task in open_pairs]
    choice = st.selectbox("Which task did you finish?", range(len(labels)), format_func=lambda i: labels[i])
    if st.button("Mark complete"):
        pet, task = open_pairs[choice]
        follow_up = scheduler.complete_task(pet, task)
        st.success(f"Marked '{task.description}' complete for {pet.name}.")
        if follow_up is not None:
            st.info(f"🔁 Next '{follow_up.description}' auto-scheduled for {follow_up.due_date}.")
        st.rerun()
else:
    st.caption("No outstanding tasks — everything's done! 🎉")

st.divider()

# --- Build the schedule (Scheduler.build_plan) -------------------------------
st.subheader("Build schedule")
col1, col2 = st.columns(2)
with col1:
    available = st.number_input("Available minutes today", min_value=1, max_value=1440, value=120)
with col2:
    start_time = st.text_input("Start time", value="08:00")

if st.button("Generate schedule", type="primary"):
    day = Scheduler(available_minutes=int(available), start_time=start_time.strip() or "08:00")
    # Only schedule outstanding tasks (filter out completed ones).
    todo = day.filter_by_status(owner.all_tasks(), completed=False)
    plan = day.build_plan(todo)
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
        if len(plan) < len(todo):
            st.info(f"{len(todo) - len(plan)} task(s) didn't fit the {available}-minute budget and were skipped.")
        with st.expander("Why this plan?"):
            st.text(day.explain(plan))
