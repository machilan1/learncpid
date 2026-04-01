from typing import List

from ortools.linear_solver import pywraplp


def main():
    # Data

    machines = ["1", "2"]
    products = ["tow", "stabilizer"]
    num_machines = len(machines)
    num_products = len(products)

    cost_coeff = [
        [3.2, 2.4],
        [2, 3],
    ]

    profit_coeff = [130, 150]

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    infinity = solver.infinity()
    for i in range(num_machines):
        for j in range(num_products):
            x[i, j] = solver.IntVar(0, infinity, "")

    # Constraints
    # Machine 1 will be available for 16 hours over the next two days

    solver.Add(sum(x[0, j] * cost_coeff[0][j] for j in range(num_products)) <= 16)

    # Machine 2 will be available for 15 hours
    solver.Add(sum(x[1, j] * cost_coeff[1][j] for j in range(num_products)) <= 15)

    # Objective

    objective_terms = []
    for i in range(num_machines):
        for j in range(num_products):
            objective_terms.append(x[i, j] * profit_coeff[j])
    solver.Maximize(solver.Sum(objective_terms))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_machines):
            for j in range(num_products):
                if x[i, j].solution_value() > 0:
                    print(
                        f"Machine {machines[i]} is picked for producing {x[i,j].solution_value()} units of product {products[j]}"
                        + f" Cost: {x[i,j].solution_value()*cost_coeff[i][j]}"
                    )
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
