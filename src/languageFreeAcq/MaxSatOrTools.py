import logging
from enum import Enum

from ortools.sat.python import cp_model


class SolverStatus(Enum):
    NOT_STARTED = 0
    OPTIMUM_FOUND = 1
    SATISFIABLE = 2
    UNSATISFIABLE = 3


class MaxSatOrTools:
    """
    MaxSat solver wrapper using the OR-Tools solver
    """

    class Clause:
        def __init__(self):
            self.literals = []

        def __add__(self, literal):
            self.literals.append(literal)
            return self

        def get_list(self):
            return self.literals

    def __init__(self, LOG: bool = False):
        """
        :param LOG:
        """
        logging.debug("Initializing the OR-Tools solver.")
        self._model = cp_model.CpModel()
        self._solver = cp_model.CpSolver()
        self._count_vars = 0
        self._vars = {}
        self._hard_clauses = []
        self._maximization_variables_and_weights = []
        self._status: SolverStatus = SolverStatus.NOT_STARTED
        self._log: bool = LOG
        self._best_objective = 0

    def add_var(self):
        self._count_vars += 1
        self._vars[self._count_vars] = self._model.NewBoolVar(f'{self._count_vars}')
        return self._count_vars

    def add_hard_literals(self, *variables):
        assert len(variables) > 0
        list_vars = []
        for var in variables:
            assert 0 < abs(var) <= self._count_vars, f"Variable {var} does not exist."
            if var < 0:
                list_vars.append(self._vars[-var].Not())
            else:
                list_vars.append(self._vars[var])
        self._model.AddBoolOr(list_vars)

    def add_hard_clause(self, clause: Clause):
        self._model.AddBoolOr([self._vars[literal] for literal in clause.get_list()])

    def add_soft_literals(self, weight, *variables):
        assert len(variables) > 0
        list_vars = []
        for var in variables:
            assert 0 < abs(var) <= self._count_vars, f"Variable {var} does not exist."
            if var < 0:
                list_vars.append(self._vars[-var].Not())
            else:
                list_vars.append(self._vars[var])
        obj_var = self._model.NewBoolVar(f'max_{self._count_vars}')
        self._maximization_variables_and_weights.append((weight, obj_var))
        self._model.AddBoolOr(list_vars + [obj_var.Not()])

    def solve(self, timeout: int = None):
        logging.debug("Setting objective.")
        self._model.Maximize(sum([weight * var for (weight, var) in self._maximization_variables_and_weights]))
        logging.debug("Solving the problem.")
        # Set time limit
        if timeout is not None:
            self._solver.parameters.max_time_in_seconds = timeout
        # Set log level to verbose
        self._solver.parameters.log_search_progress = self._log
        solver_status = self._solver.Solve(self._model)
        self._best_objective = self._solver.ObjectiveValue()
        if solver_status == cp_model.OPTIMAL:
            logging.debug("Optimal solution found.")
            self._status = SolverStatus.OPTIMUM_FOUND
        elif solver_status == cp_model.FEASIBLE:
            logging.debug("Feasible solution found.")
            self._status = SolverStatus.SATISFIABLE
        elif solver_status == cp_model.INFEASIBLE:
            logging.debug("Infeasible solution found.")
            self._status = SolverStatus.UNSATISFIABLE
        else:
            raise Exception("Unknown solver status (timeout before first solution?).")

    def solved(self):
        return self._status != SolverStatus.NOT_STARTED and self._status != SolverStatus.UNSATISFIABLE

    def optimum_found(self):
        return self._status == SolverStatus.OPTIMUM_FOUND

    def get(self, var):
        assert self.solved()
        assert 0 < var <= self._count_vars, f"Variable {var} does not exist."
        return self._solver.Value(self._vars[var]) == 1

    def get_objective(self):
        """
        Get the objective value
        """
        return self._best_objective
