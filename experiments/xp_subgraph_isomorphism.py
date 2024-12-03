import time

from src.languageFreeAcq import *
from src.languageFreeAcq import MaxSatAcq


def describe_H(csp, DESC_H, DOM):
    assert csp is not None
    if csp.get_delta() != [2, 2]:
        return False
    cur_scopes_1, _ = csp.get_scope_relation(0)
    cur_scopes_2, _ = csp.get_scope_relation(1)
    file = open(DESC_H, "r")
    expected_permited_tuples_1 = []
    for line in file:
        edge = line.split(",")
        expected_permited_tuples_1.append((int(edge[0]) + 1, int(edge[1]) + 1))
    expected_permited_tuples_2 = []
    for i in DOM:
        for j in DOM:
            if i != j and (i, j) not in expected_permited_tuples_1:
                expected_permited_tuples_2.append((i, j))
    bool1 = len(set(expected_permited_tuples_1).difference(cur_scopes_1)) == 0 and len(
        set(expected_permited_tuples_2).difference(cur_scopes_2)) == 0
    bool2 = len(set(cur_scopes_1).difference(expected_permited_tuples_2)) == 0 and len(
        set(cur_scopes_2).difference(expected_permited_tuples_1)) == 0
    if bool1 or bool2:
        return True
    return False


def language_is_subgraphisomorphism(csp, DESC_G, DOM, IT):
    assert csp is not None
    if csp.get_delta() != [2, 2]:
        return False

    cur_scopes_1, cur_rel_1 = csp.get_scope_relation(0)
    cur_scopes_2, cur_rel_2 = csp.get_scope_relation(1)

    # Open the file
    file = open(DESC_G, "r")
    edges = []
    for line in file:
        edge = line.split(",")
        edges.append((int(edge[0]) + 1, int(edge[1]) + 1))

    rel_1 = []
    # Add all the other edges
    for i in DOM:
        for j in DOM:
            if (i, j) not in edges:
                rel_1.append((i, j))

    rel_2 = edges

    bool1 = len(set(rel_1).difference(cur_rel_1)) == 0 and len(set(rel_2).difference(cur_rel_2)) == 0
    bool2 = len(set(rel_1).difference(cur_rel_2)) == 0 and len(set(rel_2).difference(cur_rel_1)) == 0
    if bool1 or bool2:
        return True
    return False


def run_subgraphisomorphism(FILE_TRAIN, NB_EXAMPLES, FILE_TEST, DESC_H, DESC_G, ORDER_KR, IT):
    start = time.time()
    for kr in ORDER_KR:
        engine = MaxSatAcq
        delta = [kr[1] for _ in range(0, kr[0])]
        logging.debug("Current (size, arity) = ", kr)
        acq = AcqSystem(ACQ_ENGINE=engine, DOMAINS=range(1, 20 + 1), VARIABLES_NUMBERS=5, DELTA=delta,
                        TIMEOUT=5 * 3600 + 0 * 60 + 0, CROSS=True, LOG=False, LOG_SOLVER=False)
        acq.add_examples(FILE_PATH=FILE_TRAIN, NB_EXAMPLES=NB_EXAMPLES)
        acq.set_objectives(SPECIFIC_SCOPES=1000, SPECIFIC_RELATIONS=1)
        terminated, _, csp = acq.run()
        if terminated:
            describe_h = describe_H(csp, DESC_H=DESC_H, DOM=[1, 2, 3, 4, 5])
            relation_found: bool = language_is_subgraphisomorphism(csp, DESC_G=DESC_G, DOM=[1, 2, 3, 4, 5], IT=IT)
            logging.info("FILE_TRAIN: " + FILE_TRAIN, "NB_EXAMPLES: " + str(NB_EXAMPLES), "FILE_TEST: " + FILE_TEST,
                         "KR: " + str(kr), "ACCURACY: " + str(csp.check_accuracy(FILE_TEST)),
                         "DESCRIBE_H: " + str(describe_h), "RELATION: " + str(relation_found),
                         "TIME: " + str(time.time() - start))
            return
    raise ValueError("No model found")
