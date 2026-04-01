from typing import List

from ortools.linear_solver import pywraplp


def main():
    # Data
    projects = [1, 2, 3, 4, 5, 6]
    num_projects = len(projects)

    cost_coeff = [38, 33, 39, 45, 23, 27]
    profit_coeff = [15, 12, 16, 18, 9, 11]

    quota = 100

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
    # 不要花超過quota

    solver.Add(solver.Sum([x[i] * cost_coeff[i] for i in range(num_projects)]) <= quota)

    # Investment opportunities 1 and 2 are mutually exclusive, and so are 3 and 4.
    solver.Add(x[0] + x[1] <= 1)
    solver.Add(x[2] + x[3] <= 1)

    # neither 3 nor 4 can be undertaken unless one of the first two opportunities is undertaken.
    solver.Add(x[0] + x[1] >= x[2])
    solver.Add(x[0] + x[1] >= x[3])

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
        total_cost = 0
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_projects):
            if x[i].solution_value() > 0.5:
                total_cost += cost_coeff[i]
                print(f"Project {projects[i]} is picked." + f" Cost: {cost_coeff[i]}")
        print(f"Total cost = {total_cost}\n")
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
