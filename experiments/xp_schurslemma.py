import time

from src.languageFreeAcq import *
from src.languageFreeAcq import MaxSatAcq


def relation_is_schurslemma(csp, n):
    cur_scopes, cur_relations = csp.get_scope_relation(0)
    expected_permited_tuples = [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    nb_not_expected_permited_tuples = len(set(cur_relations).difference(expected_permited_tuples))
    same_size_permited_tuples = len(set(cur_relations)) == len(expected_permited_tuples)
    if nb_not_expected_permited_tuples == 0 and same_size_permited_tuples:
        return True
    return False


def network_is_schurslemma(csp, n):
    cur_scopes, cur_relations = csp.get_scope_relation(0)
    expected_scopes = list(
        set([(x, y, z) for x in range(1, n + 1) for y in range(1, n + 1) for z in range(1, n + 1)
             if (x + y == z) or (x + z == y) or (y + z == x)
             or (x + x == y or x + x == z or y + y == x or y + y == z or z + z == x or z + z == y)]))

    expected_permited_tuples = [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    nb_not_expected_permited_tuples = len(set(cur_relations).difference(expected_permited_tuples))
    nb_not_expected_scopes = len(set(cur_scopes).difference(expected_scopes))
    same_size_permited_tuples = len(set(cur_relations)) == len(expected_permited_tuples)
    same_size_scopes = len(set(cur_scopes)) == len(expected_scopes)
    if nb_not_expected_permited_tuples == 0 and nb_not_expected_scopes == 0 and \
            same_size_permited_tuples and same_size_scopes:
        return True
    return False


def run_schurslemma(FILE_TRAIN, NB_EXAMPLES, FILE_TEST, ORDER_KR, N):
    start = time.time()
    for kr in ORDER_KR:
        engine = MaxSatAcq
        delta = [kr[1] for _ in range(0, kr[0])]
        acq = AcqSystem(ACQ_ENGINE=engine, VARIABLES_NUMBERS=9, DOMAINS=[1, 2, 3],
                        DELTA=delta, CROSS=True, TIMEOUT=6 * 3600 + 0 * 60 + 0, LOG=False, LOG_SOLVER=False)
        acq.add_examples(FILE_PATH=FILE_TRAIN, NB_EXAMPLES=NB_EXAMPLES)
        acq.set_objectives(SPECIFIC_SCOPES=1000, SPECIFIC_RELATIONS=1)
        terminated, _, csp = acq.run()
        if terminated:
            relation_found: bool = relation_is_schurslemma(csp, N)
            network_found: bool = network_is_schurslemma(csp, N)
            logging.info(f"FILE_TRAIN: {FILE_TRAIN} NB_EXAMPLES: {NB_EXAMPLES} FILE_TEST: {FILE_TEST} KR: {kr} "
                         f"ACCURACY: {csp.check_accuracy(FILE_TEST)} RELATION: {relation_found} NETWORK: {network_found} "
                         f"TIME: {time.time() - start}")
            return
    raise ValueError("No model found")
