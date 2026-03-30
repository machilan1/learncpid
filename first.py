from ortools.sat.python import cp_model

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__solutions = []

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        for v in self.__variables:
            ans = f"{v}={self.value(v)}"
            self.__solutions.append(ans)
            print(ans, end=" ")
        print()

    @property
    def solution_count(self) -> int:
        return self.__solution_count
    
    @property
    def solutions(self) -> list[str]:
        return self.__solutions

def main():
    """Showcases calling the solver to search for all solutions."""
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    num_vals = 3
    x = model.new_int_var(0, num_vals - 1, "x")
    y = model.new_int_var(0, num_vals - 1, "y")
    z = model.new_int_var(0, num_vals - 1, "z")

    # Create the constraints.
    model.add(x != y)
    model.add(x != z)
    model.add(y != z)
    model.add(x>z)

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([x, y, z])
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)

    print(solution_printer.solutions)

    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")

if __name__ == "__main__":
    main()
