from ortools.sat.python import cp_model


class ORTimetableSolver:

    def __init__(self, configs, slots, days, teachers):
        self.configs = configs
        self.slots = slots
        self.days = days
        self.teachers = teachers

        self.model = cp_model.CpModel()
        self.assignments = {}

    def build_variables(self):

        for c in self.configs:
            for d in range(len(self.days)):
                for s in range(len(self.slots)):

                    self.assignments[(c.id, d, s)] = self.model.NewBoolVar(
                        f"c{c.id}_d{d}_s{s}"
                    )

    def add_constraints(self):

        # each lesson must be scheduled exactly once
        for c in self.configs:
            self.model.Add(
                sum(
                    self.assignments[(c.id, d, s)]
                    for d in range(len(self.days))
                    for s in range(len(self.slots))
                ) == c.lessons_per_week
            )

        # no teacher overlap
        for teacher in self.teachers:
            for d in range(len(self.days)):
                for s in range(len(self.slots)):

                    self.model.Add(
                        sum(
                            self.assignments[(c.id, d, s)]
                            for c in self.configs
                            if c.teacher_assignment.teacher_id == teacher.id
                        ) <= 1
                    )

    def solve(self):

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return []

        result = []

        for (c_id, d, s), var in self.assignments.items():
            if solver.Value(var):

                config = next(c for c in self.configs if c.id == c_id)

                result.append({
                    "config": config,
                    "day": self.days[d],
                    "slot": self.slots[s]
                })

        return result