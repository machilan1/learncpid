from typing import List

from ortools.linear_solver import pywraplp


def main():
    # Data
    chores = ["marketing", "cooking", "dishWashing", "laundry"]
    person = ["Eve", "Steven"]

    num_chores = len(chores)
    num_person = len(person)

    cost_params = [[4.5, 7.8, 3.6, 2.9], [4.9, 7.2, 4.3, 3.1]]

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.

    x = {}
    for i in range(num_person):
        for j in range(num_chores):
            x[i, j] = solver.IntVar(0, 1, "")

    # Constraints
    # 兩個人都有兩件工作
    for i in range(num_person):
        solver.Add(solver.Sum([x[i, j] for j in range(num_chores)]) == 2)

    # 每件工作都要有人完成

    for j in range(num_chores):
        solver.Add(solver.Sum([x[i, j] for i in range(num_person)]) == 1)

    # Objective

    objective_terms = []
    for i in range(num_person):
        for j in range(num_chores):
            objective_terms.append(x[i, j] * cost_params[i][j])

    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_person):
            for j in range(num_chores):
                if x[i, j].solution_value() > 0.5:
                    print(
                        f"Person {person[i]} chooses to do {chores[j]}."
                        + f" Cost: {cost_params[i][j]}"
                    )
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
