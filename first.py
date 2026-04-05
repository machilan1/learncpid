from typing import List

from ortools.linear_solver import pywraplp


# User decides
# 1. Minimize or Maximize 
# 2. Criteria of limit
# 3. Penalty 

def main():
    # Data

    products = ["1", "2"]
    num_products = len(products)

    cost_coeff = [[1, 0], [0, 2], [3, 2]]

    profit_coeff = [3000, 5000]

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
    for i in range(num_products):
        x[i] = solver.IntVar(0, infinity, "")

    # Constraints
    # 產品1 在工廠1的生產耗時不超過4小時
    solver.Add(x[0] * 1 <= 4)

    # 產品2 在工廠2的生產耗時不超過12小時
    solver.Add(x[1] * 2 <= 12)

    # 產品1 及 產品2 在工廠3消耗的總時間不超過18小時

    solver.Add(x[0] * 3 + x[1] * 2 <= 18)

    # Objective

    objective_terms = []

    for i in range(num_products):
        objective_terms.append(x[i] * profit_coeff[i])
    solver.Maximize(solver.Sum(objective_terms))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_products):
            if x[i].solution_value() > 0:
                print(
                    f"Product {products[i]} has been produced with  {x[i].solution_value()} units"
                )
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
