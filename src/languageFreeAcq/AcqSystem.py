import datetime
import itertools
import logging
import random
import time
import warnings

from .Common import progress_bar
from .CspScopesRelations import CspScopesRelations


class AcqSystem:
    """
    ACQ system
    """

    def __init__(self, ACQ_ENGINE, DOMAINS: [int], VARIABLES_NUMBERS: int, DELTA: [int], TIMEOUT: int = None,
                 CROSS=False, SCOPES=None, LOG: bool = True, LOG_SOLVER: bool = True):
        """
        Initialisation of the ACQ system.
        :param ACQ_ENGINE: ACQ engine to use (MaxSAT, Linear (first draft used Gurobi as a solver), ...)
        :param DOMAINS: The domains of the variables, the domains is the same for all variables (e.g. [0,1] for boolean)
        :param VARIABLES_NUMBERS: The number of variables in the example (e.g. 81 for a sudoku)
        :param DELTA: The delta of the variables (e.g. [3, 2, 2] to find one ternary and two binary relation)
        :param TIMEOUT: Timeout of the complete process (in seconds), None if no timeout
        :param CROSS: True if we want to use scopes with repetitions (e.g. (1,1,2))
        :param SCOPES: The scopes to use (if None, all possible scopes are used)
        :param LOG: True to log the progress of the optimisation
        """
        # Parameters initialization
        self.start_time = time.time()
        self.DOMAINS = DOMAINS
        self.VARIABLES = range(0, VARIABLES_NUMBERS)
        self.DELTA = DELTA
        self._timeout = datetime.datetime.now() + datetime.timedelta(seconds=TIMEOUT) if TIMEOUT is not None else None
        self.CROSS = CROSS
        self.SCOPES = []
        self._log = LOG
        if SCOPES is None:
            self.CUSTOM_SCOPES = False
            for arity in self.DELTA:
                self.SCOPES.append(list(itertools.product(self.VARIABLES, repeat=arity)) if CROSS
                                   else list(itertools.permutations(self.VARIABLES, arity)))
        else:
            self.CUSTOM_SCOPES = True
            assert len(SCOPES) == len(DELTA)
            for i in range(0, len(self.DELTA)):
                assert len(SCOPES[i][0]) == self.DELTA[i], "Scope {} has not the right arity".format(SCOPES[i])
            self.SCOPES = SCOPES

        self.variables_relations = {}
        self.variables_scopes = {}
        self.is_forced_true = {}
        self.can_be_used = None
        self.positive_examples_used: int = 0
        self.negative_examples_used: int = 0
        self.examples_explored: int = 0

        # Engine initialization
        self.acq_engine = ACQ_ENGINE(self.VARIABLES, self.DOMAINS, self.DELTA, self.SCOPES, LOG_SOLVER)

        # Callback
        self.CALLBACK: callable = None

    def run(self, max_examples: int = 0, FILE_PATH: str = None, SKIP_EXAMPLES: int = 0, BATCH_SIZE: int = 1) \
            -> (bool, float, CspScopesRelations):
        """
        Run the optimization process.
        :param max_examples: Maximum number of examples to read.
        :param FILE_PATH: Path to the file containing the examples.
        :param SKIP_EXAMPLES: Number of examples to skip at the beginning of the file.
        :param BATCH_SIZE: Number of counterexamples to read before doing a new optimization.
        :return: (True, objective value, CSP) if a solution has been found, (False, 0, None) otherwise.
        """
        # Solving a first time with current examples
        if self._timeout is not None and datetime.datetime.now() > self._timeout:
            raise TimeoutError("Timeout reached before the first optimisation.")
        max_time_remaining = (self._timeout - datetime.datetime.now()).total_seconds() \
            if self._timeout is not None else None
        self.acq_engine.solve(max_time_remaining)
        if not self.acq_engine.solved():
            logging.debug("No solution found.")
            return False, 0, None
        current_csp: CspScopesRelations = self.acq_engine.to_csp()
        self.__callback_call(current_csp)
        logging.debug("{} examples read for coherence.".format(self.examples_explored))
        if not self.acq_engine.solved():
            return False, 0, None
        logging.debug("--- {} seconds ---".format(time.time() - self.start_time))
        return self.acq_engine.solved(), self.acq_engine.get_objective(), current_csp

    def set_objectives(self, SPECIFIC_SCOPES: float = 0, SPECIFIC_RELATIONS: float = 0, TRIANGLE: float = 0,
                       DEGREE: float = 0) -> None:
        """
        Set the objectives of the optimization.
        :param SPECIFIC_SCOPES: 1 if we want to maximise the number of scopes, -1 otherwise.
        :param SPECIFIC_RELATIONS: 1 if we want to maximise the number of forbidden tuples, -1 otherwise.
        :param TRIANGLE: 1 if we want to maximise the number of complete triangles, -1 otherwise.
        :param DEGREE: 1 if we want to minimise the sum of difference of degree in the primal, -1 otherwise.
        """
        if SPECIFIC_SCOPES != 0:
            logging.debug("Apply specific scope objective with weight {}.".format(SPECIFIC_SCOPES))
            self.acq_engine.objective_scope(SPECIFIC_SCOPES)
        if SPECIFIC_RELATIONS != 0:
            logging.debug("Apply specific relation objective with weight {}.".format(SPECIFIC_RELATIONS))
            self.acq_engine.objective_relation(SPECIFIC_RELATIONS)
        if TRIANGLE != 0:
            logging.warning("Old implementation of triangle objective, use with precaution.")
            logging.debug("Apply triangle objective with weight {}.".format(TRIANGLE))
            self.acq_engine.objective_triangle(TRIANGLE)
        if DEGREE != 0:
            logging.warning("Old implementation of degree objective, use with precaution.")
            logging.debug("Apply degree objective with weight {}.".format(DEGREE))
            self.acq_engine.objective_degree_regularity(DEGREE)

    def add_examples(self, FILE_PATH: str, NB_EXAMPLES: int = -1, ratio_ejected: float = 0,
                     SKIP_EXAMPLES: int = 0) -> int:
        """
        Add examples from a file to the system.
        :param FILE_PATH: path to the file containing the examples
        :param NB_EXAMPLES: maximum number of examples to add from the file
        :param ratio_ejected: ratio of examples to eject from the file
        :return: number of examples added (maybe less than max_examples if the file contains fewer examples)
                 if -1, there is an negative example that don't have any applied constraints
        """
        if not self.__examples_files_well_formed(FILE_PATH):
            logging.error("Examples file {} not well formed.".format(FILE_PATH))
            return 0
        if NB_EXAMPLES == -1:
            NB_EXAMPLES = sum(1 for _ in open(FILE_PATH))
        with progress_bar(NB_EXAMPLES, title="Read examples", active=self._log) as progress:
            examples_number: int = 0
            positive_examples: int = 0
            negatives_examples: int = 0
            sudoku_file = open(FILE_PATH, "r")
            if SKIP_EXAMPLES > 0:
                for i in range(SKIP_EXAMPLES):
                    sudoku_file.readline()
            for line in sudoku_file:
                if examples_number >= NB_EXAMPLES:
                    break
                random_value = random.random()
                if random_value >= ratio_ejected:
                    example = line.split(",")
                    weight = int(example[-1])
                    example = [int(x) for x in example[:-1]]
                    if weight == 1:
                        self.__positive_example_to_clauses(example)
                        positive_examples += 1
                        examples_number += 1
                    elif weight == 0:
                        if not self.__negative_example_to_clauses(example, PASSIF=False):
                            return -1
                        negatives_examples += 1
                        examples_number += 1
                    elif weight != 0 and weight != 1:
                        raise warnings.warn("Weight must be 0 or 1. Discarded example {}".format(examples_number))
                progress.update()
            if not examples_number >= NB_EXAMPLES:
                logging.warning("There are only {} examples in the file.".format(examples_number))
        logging.debug("There are {} examples with {} positives and {} negatives."
                      .format(examples_number, positive_examples, negatives_examples))
        sudoku_file.close()
        return examples_number

    def callback_config(self, CALLABLE: callable):
        """
        Configure the callback function.
        :param CALLABLE: function to call after each optimisation. The function must take 5 arguments:
            - the current CSP
            - the number of positive examples used
            - the number of negative examples used
            - the number of examples read
            - the time elapsed since the beginning of the algorithm
            - the objective value of the current CSP
        :return:
        """
        self.CALLBACK = CALLABLE

    def __get_kappa(self, assignment: [int], u: int) -> list:
        kappa = []
        for var in self.SCOPES[u]:
            for v in var:
                assert 0 <= v < len(assignment), "Variable {} not in assignment (scope {}).".format(v, var)
            values = [assignment[v] for v in var]
            if self.is_forced_true is None or not self.is_forced_true.get((var, tuple(values)), False):
                kappa.append((var, tuple(values)))
        return kappa

    def __positive_example_to_clauses(self, assignment: [int]):
        self.positive_examples_used += 1
        if self.CUSTOM_SCOPES is False:
            for arity in set(self.DELTA):
                kappa = self.__get_kappa(assignment, self.DELTA.index(arity))
                for u in range(1, len(self.DELTA) + 1):
                    if self.DELTA[u - 1] == arity:
                        for (scope, relation) in kappa:
                            self.acq_engine.positive_constraint(u, scope, relation)
                            self.is_forced_true[scope, relation] = True
        else:
            for u in range(1, len(self.DELTA) + 1):
                for (scope, relation) in self.__get_kappa(assignment, u - 1):
                    self.acq_engine.positive_constraint(u, scope, relation)
                    self.is_forced_true[scope, relation] = True

    def __negative_example_to_clauses(self, example: [int], PASSIF=False):
        self.negative_examples_used += 1
        u_scopes_relations = []
        for u in range(1, len(self.DELTA) + 1):
            for (scope, relation) in self.__get_kappa(example, u - 1):
                if not PASSIF or self.can_be_used.get((scope, relation), False):
                    u_scopes_relations.append((u, scope, relation))
        if len(u_scopes_relations) == 0:
            logging.debug("No negative constraint to add for example {}.".format(example))
            return False
        else:
            self.acq_engine.negative_constraint(u_scopes_relations)
            return True

    def __callback_call(self, csp: CspScopesRelations):
        if self.CALLBACK is not None:
            self.CALLBACK(csp, self.positive_examples_used, self.negative_examples_used, self.examples_explored,
                          (time.time() - self.start_time), self.acq_engine.get_objective())

    @staticmethod
    def __read_line(line, line_number):
        try:
            example = line.split(",")
            weight, assignment = int(example[-1]), [int(x) for x in example[:-1]]
            if weight not in {0, 1}:
                warnings.warn("Weight must be 0 or 1. Discarded line {}: ".format(line_number, line))
                return None, None
            return assignment, weight
        except Exception as e:
            warnings.warn("Error while reading example {}: {} ({})".format(line_number, line, e))
            return None, None

    def __find_counter_example(self, SKIP_EXAMPLES, current_csp, examples_file, max_examples):
        # Skip SKIP_EXAMPLES lines
        for i in range(SKIP_EXAMPLES):
            examples_file.readline()
        line_number = SKIP_EXAMPLES
        current_batch_size = 0
        for line in examples_file:
            line_number += 1
            assignment, weight = self.__read_line(line, line_number)
            if assignment is None:
                continue
            is_solution: bool = current_csp.is_solution(assignment)
            if weight == 1 and not is_solution:
                logging.debug("Positive example {} miss classified by the current model."
                              .format(line_number, weight))
                self.__positive_example_to_clauses(assignment)
                current_batch_size += 1
                self.examples_explored = max(line_number, self.examples_explored)
                return line_number, True
            elif weight == 0 and is_solution:
                logging.debug("Negative example {} miss classified by the current model."
                              .format(line_number + 1, weight))
                self.__negative_example_to_clauses(assignment)
                current_batch_size += 1
                self.examples_explored = max(line_number, self.examples_explored)
                return line_number, True
        return line_number, False

    def __examples_files_well_formed(self, FILE_PATH: str) -> bool:
        """
        Check if the file is well-formed.
        :param FILE_PATH: path to the file
        :return: True if the file is well-formed, False otherwise
        """
        with open(FILE_PATH, "r") as examples_file:
            line_number = 0
            for line in examples_file:
                line_number += 1
                assignment, weight = self.__read_line(line, line_number)
                if assignment is None:
                    return False
                # Check if the size is correct and if all the values are in the domain
                if len(assignment) != len(self.VARIABLES):
                    logging.error("The size of the assignment is incorrect. Line {}".format(line_number))
                    return False
                for v in assignment:
                    if v not in self.DOMAINS:
                        logging.error("The value {} is not in the domain. Line {}".format(v, line_number))
                        return False
        return True
