from typing import List

from ortools.linear_solver import pywraplp


def main():
    # Data
    routes: List[str] = [
        "San Francisco to Los Angeles",
        "San Francisco to Denver",
        "San Francisco to Seattle",
        "Los Angeles to Chicago",
        "Los Angeles to San Francisco",
        "Chicago to Denver",
        "Chicago to Seattle",
        "Denver to San Francisco",
        "Denver to Chicago",
        "Seattle to San Francisco",
        "Seattle to Los Angeles",
    ]

    sequences = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    num_routes = len(routes)
    num_sequences = len(sequences)
    costs = [2, 3, 4, 6, 7, 5, 7, 8, 9, 9, 8, 9]

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    for i in range(num_sequences):
        x[i] = solver.IntVar(0, 1, "")

    # Constraints

    # Set partitioning mode
    # 每條路線要剛好走一次
    solver.Add(solver.Sum([x[i] for i in [0, 3, 6, 9]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [1, 4, 7, 10]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [2, 5, 8, 11]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [3, 6, 8, 9, 11]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [0, 5, 9, 10]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [3, 4, 8]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [6, 7, 9, 10, 11]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [1, 3, 4, 8]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [4, 7, 10]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [2, 6, 7, 11]]) == 1)
    solver.Add(solver.Sum([x[i] for i in [5, 8, 9, 10, 11]]) == 1)

    # Set covering mode
    # 每條路線至少要走過一次
    # solver.Add(solver.Sum([x[i] for i in [0, 3, 6, 9]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [1, 4, 7, 10]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [2, 5, 8, 11]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [3, 6, 8, 9, 11]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [0, 5, 9, 10]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [3, 4, 8]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [6, 7, 9, 10, 11]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [1, 3, 4, 8]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [4, 7, 10]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [2, 6, 7, 11]]) >= 1)
    # solver.Add(solver.Sum([x[i] for i in [5, 8, 9, 10, 11]]) >= 1)

    # Assign給3個crew
    solver.Add(solver.Sum([x[i] for i in range(num_sequences)]) == 3)

    # Objective

    objective_terms = []
    for i in range(num_sequences):
        objective_terms.append(x[i] * costs[i])
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_sequences):
            if x[i].solution_value() > 0.5:
                print(f"Sequence {sequences[i]} is picked." + f" Cost: {costs[i]}")
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
