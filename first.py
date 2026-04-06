from typing import List

from ortools.linear_solver import pywraplp


# User decides
# 1. Minimize or Maximize
# 2. Criteria of limit
# 3. Penalty


def main():
    # Data

    nurses = ["A", "B", "C", "D"]
    shifts = ["早", "中", "晚"]
    days = ["1", "2", "3"]

    num_nurses = len(nurses)
    num_shifts = len(shifts)
    num_days = len(days)

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i,j,d] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j in day d.
    infinity = solver.infinity()
    x = {}
    for i in range(num_nurses):
        for j in range(num_shifts):
            for d in range(num_days):
                x[i, j, d] = solver.IntVar(0, 1, "")
    # y[i] is the surplus variable of total work shift person i takes.
    y = {}
    for i in range(num_nurses):
        y[i] = solver.IntVar(0, infinity, "")

    # z[i] is the deficit variable of total work shift person i takes.
    z = {}
    for i in range(num_nurses):
        z[i] = solver.IntVar(0, infinity, "")

    # Constraints
    # Each shift is assigned to a single nurse per day.
    for j in range(num_shifts):
        for d in range(num_days):
            solver.Add(sum([x[i, j, d] for i in range(num_nurses)]) == 1)

    # Each nurse works at most one shift per day.
    for i in range(num_nurses):
        for d in range(num_days):
            solver.Add(sum([x[i, j, d] for j in range(num_shifts)]) <= 1)

    # 每個護士平均上班
    for i in range(num_nurses):
        solver.Add(
            sum([x[i, j, d] for j in range(num_shifts) for d in range(num_days)])
            - y[i]
            + z[i]
            == (num_days * num_shifts) // num_nurses
        )

    # Objective

    objective_terms = [x[0, 0, 0]]

    # for i in range(num):
    # objective_terms.append(x[i] * profit_coeff[i])
    solver.Minimize(solver.Sum([y[i] * 3 + z[i] * 10 for i in range(num_nurses)]))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for d in range(num_days):
            print(f"Day {days[d]} : ")
            for j in range(num_shifts):
                for i in range(num_nurses):
                    if x[i, j, d].solution_value() > 0:
                        print(f"Employee {nurses[i]} take shift {shifts[j]}")
            print("\n")
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
