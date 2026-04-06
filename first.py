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
    x = {}
    for i in range(num_nurses):
        for j in range(num_shifts):
            for d in range(num_days):
                x[i, j, d] = solver.IntVar(0, 1, "")

    # Constraints
    # Each shift is assigned to a single nurse per day.
    for j in range(num_shifts):
        for d in range(num_days):
            solver.Add(sum([x[i, j, d] for i in range(num_nurses)]) == 1)

    # Each nurse works at most one shift per day.
    for i in range(num_nurses):
        for d in range(num_days):
            solver.Add(sum([x[i, j, d] for j in range(num_shifts)]) == 1)

    # 每個護士平均上班
    least_level = (num_shifts * num_days) // num_nurses

    for i in range(num_nurses):
        solver.Add(
            sum([x[i, j, d] for j in range(num_shifts) for d in range(num_days)])
            >= least_level
        )

    # Objective

    objective_terms = [x[0, 0, 0]]

    # for i in range(num):
    #     objective_terms.append(x[i] * profit_coeff[i])
    solver.Maximize(x[0, 0, 0] * 6)

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for d in range(num_days):
            for j in range(num_shifts):
                for i in range(num_nurses):
                    if x[i].solution_value() > 0:
                        print(
                            f"Days {days[d]} has been produced with  {x[i].solution_value()} units"
                        )
    else:
        print(x)
        print("No solution found.")


if __name__ == "__main__":
    main()
