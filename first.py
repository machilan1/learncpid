from typing import List

from ortools.linear_solver import pywraplp



def main():
    # Data

    cities : List[str] = ["LA","SF"]
    buildings : List[str] = ["factory", "warehouse"]
    capital = 10


    num_cities = len(cities)
    num_buildings = len(buildings)

    costs = [[6,5],[3,2]]
    values = [[9,6],[5,4]]



    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    for i in range(num_cities):
        for j in range(num_buildings):
            x[i, j] = solver.IntVar(0, 1, "")

    # Constraints
    # 預算要小於10

    solver.Add(solver.Sum([x[i,j]*costs[i][j] for i in range(num_cities) for j in range(num_buildings)])<=capital)

    # 公司頂多蓋一個新warehouse

    solver.Add(solver.Sum([x[i,1] for i in range(num_cities)])<=1)

    # 有蓋factory的地方才蓋warehouse
    for i in range(num_cities):
        solver.Add(x[i,1]<=x[i,0])


    # Objective
    
    objective_terms = []
    for i in range(num_cities):
        for j in range(num_buildings):
            objective_terms.append(x[i, j] * values[i][j])
    solver.Maximize(solver.Sum(objective_terms))

    # Solve
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total value = {solver.Objective().Value()}\n")
        for i in range(num_cities):
            for j in range(num_buildings):
                # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
                if x[i, j].solution_value() > 0.5:
                    print(f"City {cities[i]} build {buildings[j]}." + f" Cost: {costs[i][j]}")
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()