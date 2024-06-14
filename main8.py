from constraint import Problem, AllDifferentConstraint
import pandas as pd

problem = Problem()

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
time_slots = ["Slot1", "Slot2", "Slot3", "Slot4", "Slot5"]
time_slots_tuesday = ["Slot1", "Slot2", "Slot3"]
groups = ["Group1", "Group2", "Group3", "Group4", "Group5", "Group6"]
courses = ["MF", "SEC", "ANUM", "RO", "ENT", "ARCHI", "AI", "RX"]
sessions = ["LEC", "TD", "TP"]

teachers = {
    "MF": ["T1"],
    "SEC": ["T3"],
    "ANUM": ["T4"],
    "RO": ["T5"],
    "ENT": ["T6"],
    "ARCHI": ["T7"],
    "AI": {
        "LEC": ["T8"],
        "TD": ["T8"],
        "TP": ["T9", "T10", "T11"]
    },
    "RX": {
        "LEC": ["T12"],
        "TD": ["T12", "T13"],
        "TP": ["T14"]
    }
}

# Adding variables and their domains
for day in days:
    for slot in (time_slots if day != 'Tuesday' else time_slots_tuesday):
        for group in groups:
            for course in courses:
                for session in sessions:
                    if isinstance(teachers[course], list):
                        problem.addVariable((day, slot, group, course, session), teachers[course])
                    else:
                        problem.addVariable((day, slot, group, course, session), teachers[course][session])

# Adding constraints
# 1. All different constraint for courses in the same slot
for day in days:
    for slot in (time_slots if day != "Tuesday" else time_slots_tuesday):
        for group in groups:
            for course in courses:
                for session in sessions:
                    problem.addConstraint(AllDifferentConstraint(), [(day, slot, group, course, session)])

# 2. Constraint: Lectures of the same course should not be scheduled in the same slot
for day in days:
    for slot in (time_slots if day != "Tuesday" else time_slots_tuesday):
        for course in ["MF", "SEC", "ANUM", "RO", "ENT", "ARCHI"]:
            lec_teacher_variants = [(day, slot, group, course, "LEC", teacher) for group in groups for teacher in teachers[course]]
            problem.addConstraint(AllDifferentConstraint(), lec_teacher_variants)

# 3. Constraint: Different courses for the same group should have different slot allocations
for day in days:
    for group in groups:
        for course1 in courses:
            for course2 in courses:
                if course1 != course2:
                    for session in sessions:
                        problem.addConstraint(AllDifferentConstraint(), [(day, slot, group, course1, session) for slot in (time_slots if day != "Tuesday" else time_slots_tuesday) for session in sessions] + [(day, slot, group, course2, session) for slot in (time_slots if day != "Tuesday" else time_slots_tuesday) for session in sessions])

# 4. Constraint: No more than three successive slots of work
for day in days:
    slots = time_slots if day != "Tuesday" else time_slots_tuesday
    for i in range(len(slots) - 2):
        problem.addConstraint(AllDifferentConstraint(), [(day, slots[i+j], group, course, session) for j in range(3) for group in groups for course in courses for session in sessions])

solutions = problem.getSolutions()

print(f"Number of solutions found: {len(solutions)}")

if solutions:
    timetable_list = [[key[0], key[1], key[2], key[3], key[4], value] for solution in solutions for key, value in solution.items()]
    df = pd.DataFrame(timetable_list, columns=["Day", "Time Slot", "Group", "Course", "Session", "Teacher"])
    timetable_df = df.pivot_table(index=["Day", "Time Slot"], columns=["Group", "Course", "Session"], values="Teacher", aggfunc='first')
    print(timetable_df)

    # Save to CSV file
    timetable_df.to_csv('timetable.csv')
    print("Timetable saved to timetable.csv")
else:
    print("No solution found.")
