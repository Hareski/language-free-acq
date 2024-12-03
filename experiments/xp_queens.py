import time

from src.languageFreeAcq import *
from src.languageFreeAcq import MaxSatAcq


def run_8queen(FILE_TRAIN, NB_EXAMPLES, FILE_TEST, ORDER_KR):
    start = time.time()
    for kr in ORDER_KR:
        engine = MaxSatAcq
        delta = [kr[1] for _ in range(0, kr[0])]
        logging.debug("Current (size, arity) = ", kr)
        acq = AcqSystem(ACQ_ENGINE=engine, VARIABLES_NUMBERS=8,
                        DOMAINS=[1, 2, 3, 4, 5, 6, 7, 8], DELTA=delta,
                        TIMEOUT=6 * 3600 + 0 * 60 + 0, CROSS=True, LOG=False, LOG_SOLVER=False)
        acq.add_examples(FILE_PATH=FILE_TRAIN, NB_EXAMPLES=NB_EXAMPLES)
        acq.set_objectives(SPECIFIC_SCOPES=1000, SPECIFIC_RELATIONS=1)
        terminated, _, csp = acq.run()
        if terminated:
            assert csp.get_delta() != [2, 2, 2, 2, 2, 2, 2, 2]  # Or the following lines are not valid
            relation_found: bool = False
            network_found: bool = False
            logging.info("FILE_TRAIN: " + FILE_TRAIN, "NB_EXAMPLES: " + str(NB_EXAMPLES), "FILE_TEST: " + FILE_TEST,
                         "KR: " + str(kr), "ACCURACY: " + str(csp.check_accuracy(FILE_TEST)),
                         "RELATION: " + str(relation_found), "NETWORK: " + str(network_found),
                         "TIME: " + str(time.time() - start))
            return network_found
    logging.warning("No model found.")
    return False
