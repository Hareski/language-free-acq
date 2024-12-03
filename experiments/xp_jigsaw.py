import time

from src.languageFreeAcq import *
from src.languageFreeAcq import MaxSatAcq


def language_is_jigsaw(csp):
    assert csp is not None
    cur_scopes, cur_relations = csp.get_scope_relation(0)
    expected_permited_tuples = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
    nb_not_expected_permited_tuples = len(set(cur_relations).difference(expected_permited_tuples))
    same_size_permited_tuples = len(set(cur_relations)) == len(expected_permited_tuples)
    if nb_not_expected_permited_tuples == 0 and same_size_permited_tuples:
        return True
    return False


def network_is_jigsaw(csp, DESC_FILE, EQUIV_FILE):
    assert csp is not None
    cliques = []
    with open(DESC_FILE, 'r') as f:
        for line in f:
            cliques.append([int(x) for x in line.split(',')])
    cur_scopes, cur_relations = csp.get_scope_relation(0)
    expected_scopes = list(
        set([(x, y) for x in range(1, 82) for y in range(1, 82) if x < y and (x - 1) % 9 == (y - 1) % 9] + \
            [(x, y) for x in range(1, 82) for y in range(1, 82) if x < y and (x - 1) // 9 == (y - 1) // 9] + \
            [(x, y) for x in range(1, 82) for y in range(1, 82) for clique in cliques
             if x < y and x in clique and y in clique])
    )
    with open(EQUIV_FILE, 'r') as f:
        for line in f:
            expected_scopes.append(tuple([int(x) for x in line.split(',')]))
    expected_permited_tuples = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
    cur_scopes_sorted = set([(x, y) if x < y else (y, x) for (x, y) in cur_scopes])
    nb_not_expected_permited_tuples = len(set(cur_relations).difference(expected_permited_tuples))
    nb_not_expected_scopes = len(set(cur_scopes_sorted).difference(expected_scopes))
    same_size_permited_tuples = len(set(cur_relations)) == len(expected_permited_tuples)
    same_size_scopes = len(set(cur_scopes_sorted)) == len(expected_scopes)
    if nb_not_expected_permited_tuples == 0 and nb_not_expected_scopes == 0 and same_size_permited_tuples \
            and same_size_scopes:
        return True
    return False


def run_jigsaw_81(FILE_TRAIN, DESC_FILE, EQUIV_FILE, NB_EXAMPLES, FILE_TEST, ORDER_KR):
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
            relation_found: bool = language_is_jigsaw(csp)
            network_found: bool = network_is_jigsaw(csp, DESC_FILE, EQUIV_FILE)
            logging.info("FILE_TRAIN: " + FILE_TRAIN, "NB_EXAMPLES: " + str(NB_EXAMPLES), "FILE_TEST: " + FILE_TEST,
                  "KR: " + str(kr), "ACCURACY: " + str(csp.check_accuracy(FILE_TEST)),
                  "RELATION: " + str(relation_found), "NETWORK: " + str(network_found),
                  "TIME: " + str(time.time() - start))
            return
    raise ValueError("No model found")
