from typing import List

from ortools.linear_solver import pywraplp


def main():
    # Data
    projects = [1, 2, 3, 4, 5]
    num_projects = len(projects)

    cost_coeff = [6, 12, 10, 4, 8]
    profit_coeff = [1, 1.8, 1.6, 0.8, 1.4]

    quota = 20

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    for i in range(num_projects):
        x[i] = solver.IntVar(0, 1, "")

    # Constraints
    # 不要花超過quota就好

    solver.Add(solver.Sum([x[i] * cost_coeff[i] for i in range(num_projects)]) <= quota)

    # Objective

    objective_terms = []
    for i in range(num_projects):
        objective_terms.append(x[i] * profit_coeff[i])
    solver.Maximize(solver.Sum(objective_terms))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_projects):
            if x[i].solution_value() > 0.5:
                print(f"Project {projects[i]} is picked." + f" Cost: {cost_coeff[i]}")
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
