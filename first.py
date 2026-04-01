from typing import List

from ortools.linear_solver import pywraplp


def main():
    # Data

    persons = ["Carl", "Chris", "David", "Tony", "Ken"]
    strokes = ["backstroke", "breaststroke", "butterfly", "freestyle"]
    num_persons = len(persons)
    num_strokes = len(strokes)

    cost_coeff = [
        [37.7, 43.4, 33.3, 29.2],
        [32.9, 33.1, 28.5, 26.4],
        [33.8, 42.2, 38.9, 29.6],
        [37.0, 34.7, 30.4, 28.5],
        [35.4, 41.8, 33.6, 31.1],
    ]

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
    for i in range(num_persons):
        for j in range(num_strokes):
            x[i, j] = solver.IntVar(0, 1, "")

    # Constraints
    # 每個式只能有一個人上場
    for j in range(num_strokes):
        solver.Add(solver.Sum([x[i, j] for i in range(num_persons)]) == 1)

    # 一個人只頂多只能游一種式
    for i in range(num_persons):
        solver.Add(solver.Sum(x[i, j] for j in range(num_strokes)) <= 1)

    # Objective

    objective_terms = []
    for i in range(num_persons):
        for j in range(num_strokes):
            objective_terms.append(x[i, j] * cost_coeff[i][j])
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        total_cost = 0
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_persons):
            for j in range(num_strokes):
                if x[i, j].solution_value() > 0.5:
                    total_cost += cost_coeff[i][j]
                    print(
                        f"Swimmer {persons[i]} is picked for {strokes[j]}"
                        + f" Cost: {cost_coeff[i][j]}"
                    )
        print(f"Total cost = {total_cost}\n")
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
