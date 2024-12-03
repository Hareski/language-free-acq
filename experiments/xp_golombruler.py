import time

from src.languageFreeAcq import *
from src.languageFreeAcq import MaxSatAcq


def network_is_golomb(csp):
    cur_scopes, cur_relations = csp.get_scope_relation(0)
    logging.debug("g ", len(cur_scopes))
    logging.debug("cur_relations: ", len(cur_relations))

    expected_permited_tuples_1 = list(
        set([(a, b, c, d) for a in range(0, 61) for b in range(0, 61) for c in range(0, 61)
             for d in range(0, 61) if a + b == c + d]))
    expected_permited_tuples_2 = list(
        set([(a, c, b, d) for a in range(0, 61) for b in range(0, 61) for c in range(0, 61)
             for d in range(0, 61) if a + b == c + d]))
    nb_expected_permited_tuples_1 = len(set(cur_relations).intersection(expected_permited_tuples_1))
    nb_expected_permited_tuples_2 = len(set(cur_relations).intersection(expected_permited_tuples_2))
    return nb_expected_permited_tuples_1 == 0 or nb_expected_permited_tuples_2 == 0


def run_golombruler(FILE_TRAIN, NB_EXAMPLES, FILE_TEST, ORDER_KR):
    start = time.time()
    for kr in ORDER_KR:
        engine = MaxSatAcq
        delta = [kr[1] for _ in range(0, kr[0])]
        logging.debug("Curent (k, r): ", kr)
        acq = AcqSystem(ACQ_ENGINE=engine, VARIABLES_NUMBERS=10, DOMAINS=range(0, 61),
                        DELTA=delta, CROSS=True, TIMEOUT=6 * 3600 + 0 * 60 + 0, LOG=False, LOG_SOLVER=False)
        acq.add_examples(FILE_PATH=FILE_TRAIN, NB_EXAMPLES=NB_EXAMPLES)
        acq.set_objectives(SPECIFIC_SCOPES=1000, SPECIFIC_RELATIONS=1)
        terminated, _, csp = acq.run()
        logging.debug("Terminated.")
        if terminated:
            assert csp.get_delta() != [4]  # Or the following lines are not valid
            relation_found: bool = False
            network_found: bool = False
            logging.info("FILE_TRAIN: " + FILE_TRAIN, "NB_EXAMPLES: " + str(NB_EXAMPLES), "FILE_TEST: " + FILE_TEST,
                         "KR: " + str(kr), "ACCURACY: " + str(csp.check_accuracy(FILE_TEST)),
                         "RELATION: " + str(relation_found), "NETWORK: " + str(network_found),
                         "TIME: " + str(time.time() - start))
            return network_found
    logging.warning("No solution found")
    return False
