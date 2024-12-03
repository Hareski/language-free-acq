import time

from src.languageFreeAcq import *
from src.languageFreeAcq import MaxSatAcq


def language_is_sudoku(csp):
    assert csp is not None
    if csp.get_delta() != [2]:
        return False
    expected_permited_tuples = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
    cur_scopes, cur_relations = csp.get_scope_relation(0)
    nb_not_expected_permited_tuples = len(set(cur_relations).difference(expected_permited_tuples))
    nb_expected_permited_tuples = len(set(cur_relations).intersection(expected_permited_tuples))
    if nb_not_expected_permited_tuples == 0 and nb_expected_permited_tuples == len(expected_permited_tuples):
        return True
    return False


def network_is_sudoku(csp):
    assert csp is not None
    if csp.get_delta() != [2]:
        return False
    expected_scopes = list(
        set([(x, y) for x in range(1, 82) for y in range(1, 82) if x < y and (x - 1) % 9 == (y - 1) % 9] + \
            [(x, y) for x in range(1, 82) for y in range(1, 82) if x < y and (x - 1) // 9 == (y - 1) // 9] + \
            [(x, y) for x in range(1, 82) for y in range(1, 82) if x < y and (
                    ((x - 1) // 9) // 3 == ((y - 1) // 9) // 3 and ((x - 1) % 9) // 3 == ((y - 1) % 9) // 3)]))
    expected_permited_tuples = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
    cur_scopes, cur_relations = csp.get_scope_relation(0)
    logging.debug(len(cur_scopes))
    for (x, y) in cur_scopes:
        logging.debug('{"from": "' + str(x) + '", "to": "' + str(y) + '"},')
    for (x, y) in cur_scopes:
        logging.debug('tuple ' + str(x - 1) + ' ' + str(y - 1))
    cur_scopes_sorted = set([(x, y) if x < y else (y, x) for (x, y) in cur_scopes])
    nb_not_expected_permited_tuples = len(set(cur_relations).difference(expected_permited_tuples))
    nb_not_expected_scopes = len(set(cur_scopes_sorted).difference(expected_scopes))
    nb_expected_permited_tuples = len(set(cur_relations).intersection(expected_permited_tuples))
    nb_expected_scopes = len(set(cur_scopes_sorted).intersection(expected_scopes))
    if nb_not_expected_permited_tuples == 0 and nb_not_expected_scopes == 0 and \
            nb_expected_permited_tuples == len(expected_permited_tuples) and \
            nb_expected_scopes == len(expected_scopes):
        return True
    else:
        return False


def run_sudoku_81(FILE_TRAIN, NB_EXAMPLES, FILE_TEST, ORDER_KR):
    start = time.time()
    for kr in ORDER_KR:
        engine = MaxSatAcq
        delta = [kr[1] for _ in range(0, kr[0])]
        logging.debug("Current (size, arity) = ", kr)
        acq = AcqSystem(ACQ_ENGINE=engine, DOMAINS=[1, 2, 3, 4, 5, 6, 7, 8, 9], VARIABLES_NUMBERS=81, DELTA=delta,
                        TIMEOUT=6 * 3600 + 0 * 60 + 0, CROSS=True, LOG=False, LOG_SOLVER=True)
        acq.add_examples(FILE_PATH=FILE_TRAIN, NB_EXAMPLES=NB_EXAMPLES)
        acq.set_objectives(SPECIFIC_SCOPES=1000, SPECIFIC_RELATIONS=1)
        terminated, _, csp = acq.run()
        if terminated:
            relation_found: bool = language_is_sudoku(csp)
            network_found: bool = network_is_sudoku(csp)
            logging.info("FILE_TRAIN: " + FILE_TRAIN, "NB_EXAMPLES: " + str(NB_EXAMPLES), "FILE_TEST: " + FILE_TEST,
                          "KR: " + str(kr), "ACCURACY: " + str(csp.check_accuracy(FILE_TEST)),
                          "RELATION: " + str(relation_found), "NETWORK: " + str(network_found),
                          "TIME: " + str(time.time() - start))
            return network_found
    logging.warning("No model found.")
    return False


def run_ratio_sudoku_81(FILE_TRAIN_POSTIVE, FILE_TRAIN_NEGATIVE, RATIO, NB_EXAMPLES, ORDER_KR, OBJ_SCOPES,
                        OBJ_RELATIONS, FILE_TEST):
    logging.debug("->> SIZE: ", NB_EXAMPLES, "RATIO: ", RATIO)
    for kr in ORDER_KR:
        engine = MaxSatAcq
        delta = [kr[1] for _ in range(0, kr[0])]
        logging.debug("Current (size, arity) = ", kr)
        acq = AcqSystem(ACQ_ENGINE=engine, DOMAINS=[1, 2, 3, 4, 5, 6, 7, 8, 9], VARIABLES_NUMBERS=81, DELTA=delta,
                        TIMEOUT=6 * 3600 + 0 * 60 + 0, CROSS=True, LOG=False, LOG_SOLVER=True)
        acq.add_examples(FILE_PATH=FILE_TRAIN_POSTIVE, NB_EXAMPLES=int(NB_EXAMPLES * RATIO))
        acq.add_examples(FILE_PATH=FILE_TRAIN_NEGATIVE, NB_EXAMPLES=int(NB_EXAMPLES * (1 - RATIO)))
        acq.set_objectives(SPECIFIC_SCOPES=OBJ_SCOPES, SPECIFIC_RELATIONS=OBJ_RELATIONS)
        terminated, _, csp = acq.run()
        if terminated:
            accuracy = csp.check_accuracy(FILE_TEST)
            network_found: bool = network_is_sudoku(csp)
            logging.info("Accuracy %s with ratio %s", accuracy, RATIO)
            return network_found
    logging.warning("No model found.")
    return False
