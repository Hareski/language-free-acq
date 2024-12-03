import datetime
import logging
import time

from .CspScopesRelations import CspScopesRelations
from .MaxSatAcq import MaxSatAcq
from .AcqSystem import AcqSystem

class Acquisition:
    """ This class is used to learn a CSP from examples. It is the main start point of the acquisition process.
    You can simply call the learn method with the path to the file of examples and the CSP will be learned. """

    def __init__(self):
        self.order_kr = [(1, 2), (1, 1), (2, 1), (3, 1), (4, 1), (1, 2), (5, 1), (2, 2), (6, 1), (3, 2), (7, 1), (4, 2),
                         (8, 1), (5, 2), (9, 1), (6, 2), (1, 3), (10, 1), (7, 2), (2, 3), (11, 1), (8, 2), (3, 3),
                         (12, 1), (9, 2), (4, 3), (13, 1), (10, 2), (5, 3), (14, 1), (11, 2), (6, 3), (12, 2), (7, 3),
                         (13, 2), (8, 3), (1, 4), (14, 2), (9, 3), (2, 4), (10, 3), (3, 4), (11, 3), (4, 4), (12, 3),
                         (5, 4), (13, 3), (6, 4), (14, 3), (7, 4), (8, 4), (9, 4), (10, 4), (1, 5), (11, 4), (2, 5),
                         (12, 4), (3, 5), (13, 4), (4, 5), (14, 4)]
        self.DOMAINS, self.VARIABLES_NUMBERS = None, None

    def get_domains(self):
        """
        @return: the domains of the variables inferred from the learning examples.
        """
        return self.DOMAINS

    def get_variables_numbers(self):
        """
        @return: the number of variables inferred from the learning examples.
        """
        return self.VARIABLES_NUMBERS

    def learn(self, file_train: str, max_examples: int = 0, timeout: int = None,
              verbose: bool = False) -> CspScopesRelations:
        """
        Learn the CSP from the given file of examples
        @param file_train: The path to the file of examples with the format: "var1, var2, ..., varN, weight" with var1,
        var2, ..., varN the values of the variables and weight the weight of the example (0 for a non-solution, 1 for a
        solution)
        @param max_examples: The maximum number of examples to consider in the file. If 0, all examples are considered.
        @param timeout: The maximum time (in s) to learn the CSP. If None, no timeout is set.
        @param verbose: If True, the logs of the optimization process are displayed. The other logs can be displayed by
        setting the logging level to DEBUG.
        @return: The learned CSP (a CspScopesRelations object)
        """
        csp = None
        NB_EXAMPLES, self.DOMAINS, self.VARIABLES_NUMBERS = self._params_from_file(file_train)
        logging.debug("The parameters were inferred from the file.")
        logging.debug("NB_EXAMPLES: " + str(NB_EXAMPLES))
        logging.debug("DOMAINS: " + str(self.DOMAINS))
        logging.debug("VARIABLES_NUMBERS: " + str(self.VARIABLES_NUMBERS))
        _start_time: float = time.time()
        if timeout is not None:
            _max_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        else:
            _max_time = None
        if max_examples > 0: NB_EXAMPLES = max_examples
        kr = None
        for kr in self.order_kr:
            engine = MaxSatAcq
            delta = [kr[1] for _ in range(0, kr[0])]
            logging.debug("Current (size, arity) = %s", kr)
            max_time_remaining = (_max_time - datetime.datetime.now()).total_seconds() \
                if _max_time is not None else None
            acq = AcqSystem(ACQ_ENGINE=engine, DOMAINS=self.DOMAINS,
                                            VARIABLES_NUMBERS=self.VARIABLES_NUMBERS,
                                            DELTA=delta, TIMEOUT=max_time_remaining, CROSS=True, LOG=verbose,
                                            LOG_SOLVER=verbose)
            acq.add_examples(FILE_PATH=file_train, NB_EXAMPLES=NB_EXAMPLES)
            acq.set_objectives(SPECIFIC_SCOPES=1000, SPECIFIC_RELATIONS=1)
            terminated, _, csp = acq.run()
            if terminated or _max_time is not None and datetime.datetime.now() > _max_time:
                break
        logging.debug("Final  (size, arity) = %s", kr)
        logging.debug("Total Time: %d", time.time() - _start_time)
        return csp  # type: CspScopesRelations

    def _params_from_file(self, file_path: str) -> (int, list, int):
        PARAM_NB_EXAMPLES = 0
        PARAM_DOMAINS = []
        PARAM_VARIABLES_NUMBERS = -1
        with open(file_path, 'r') as f:
            for line in f:
                if line[0] != '#':
                    PARAM_VARIABLES_NUMBERS = len(line.split(',')) - 1
                    for val in line.split(','):
                        if val != '1\n' and val != '0\n' and int(val) not in PARAM_DOMAINS:
                            PARAM_DOMAINS.append(int(val))
                    PARAM_NB_EXAMPLES += 1
                    break
            for line in f:
                if line[0] != '#':
                    assert PARAM_VARIABLES_NUMBERS == len(line.split(',')) - 1, "Inconsistent number of variables"
                    for val in line.split(','):
                        if val != '1\n' and val != '0\n' and int(val) not in PARAM_DOMAINS:
                            PARAM_DOMAINS.append(int(val))
                    PARAM_NB_EXAMPLES += 1
        if PARAM_VARIABLES_NUMBERS == -1:
            raise SyntaxError("No example found in file: " + file_path)
        return PARAM_NB_EXAMPLES, sorted(PARAM_DOMAINS), PARAM_VARIABLES_NUMBERS