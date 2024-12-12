import logging
import sys

from experiments import xp_schurslemma, xp_sudoku, xp_subgraph_isomorphism, xp_golombruler, \
    xp_queens, xp_jigsaw, xp_custom

from src.languageFreeAcq.Common import kr_generator


def run(experiment_name: str, size_list: [int], run_list: [int]):
    """
    Simple launcher for the experiments of the paper Learning Constraint Networks over Unknown Constraint Languages
    :param experiment_name: name of the experiments {schurslemma, sudoku, subgraph_isomorphism, golombruler, queens,
                            jigsaw1, jigsaw2, jigsaw3, all}
    :param size_list: list of the size of the problem to solve
    :param run_list: list of the run to execute (1 to 5)
    :return: None
    """
    assert set(run_list).intersection(set(range(1, 6))) == set(run_list), "Run list must be between 1 and 5"
    logging.getLogger().setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    # Order for (k, r) values:
    generator_kr = kr_generator()
    order_kr = [next(generator_kr) for _ in range(1000)]

    # Experiment 1: Schur's lemma
    if experiment_name == "schurslemma" or experiment_name == "all":
        for iteration in run_list:
            schurslemma_test_file = "data/schurslemma/9_schurs_lemma_test.csv"

            for size in (size_list if size_list is not None else [10, 50, 100, 200, 400, 800]):
                schurslemma_train_file = "data/schurslemma/9_schurs_lemma_{}.csv".format(iteration)
                xp_schurslemma.run_schurslemma(FILE_TRAIN=schurslemma_train_file, NB_EXAMPLES=size,
                                               FILE_TEST=schurslemma_test_file, ORDER_KR=order_kr, N=9)

    # Experiment 2: Sudoku
    if experiment_name == "sudoku" or experiment_name == "all":
        for iteration in run_list:
            sudoku_test_file = "data/sudoku/sudoku_test.csv"
            for size in (size_list if size_list is not None else [100, 200, 400]):
                # sudoku_train_file = "data/sudoku/sudoku_{}_train.csv".format(iteration)
                sudoku_train_file = "data/sudoku/sudoku_{}_train.csv".format(iteration)
                xp_sudoku.run_sudoku_81(FILE_TRAIN=sudoku_train_file, NB_EXAMPLES=size,
                                        FILE_TEST=sudoku_test_file, ORDER_KR=order_kr)

    # Experiment 3.1: Jigsaw #1
    if experiment_name == "jigsaw1" or experiment_name == "all":
        for iteration in run_list:
            for size in (size_list if size_list is not None else [400, 600, 800, 1000, 1200, 1400]):
                jigsaw_train_file = "data/jigsaw/1_jigsaw_{}_train.csv".format(iteration)
                jigsaw_desc_file = "data/jigsaw/1_jigsaw_desc.csv".format(iteration)  # Clique of the jigsaw
                jigsaw_equiv_file = "data/jigsaw/1_jigsaw_equiv.csv".format(iteration)  # Proved redundancy
                jigsaw_test_file = "data/jigsaw/1_jigsaw_test.csv".format(iteration)
                xp_jigsaw.run_jigsaw_81(FILE_TRAIN=jigsaw_train_file, DESC_FILE=jigsaw_desc_file,
                                        EQUIV_FILE=jigsaw_equiv_file, NB_EXAMPLES=size,
                                        FILE_TEST=jigsaw_test_file, ORDER_KR=order_kr)

    # Experiment 3.2: Jigsaw #2
    if experiment_name == "jigsaw2" or experiment_name == "all":
        for iteration in run_list:
            for size in (size_list if size_list is not None else [400, 600, 800, 1000, 1200, 1400]):
                jigsaw_train_file = "data/jigsaw/2_jigsaw_{}_train.csv".format(iteration)
                jigsaw_desc_file = "data/jigsaw/2_jigsaw_desc.csv".format(iteration)  # Clique of the jigsaw
                jigsaw_equiv_file = "data/jigsaw/2_jigsaw_equiv.csv".format(iteration)  # Proved redundancy
                jigsaw_test_file = "data/jigsaw/2_jigsaw_test.csv".format(iteration)
                xp_jigsaw.run_jigsaw_81(FILE_TRAIN=jigsaw_train_file, DESC_FILE=jigsaw_desc_file,
                                        EQUIV_FILE=jigsaw_equiv_file, NB_EXAMPLES=size,
                                        FILE_TEST=jigsaw_test_file, ORDER_KR=order_kr)

    # Experiment 3.3: Jigsaw #3
    if experiment_name == "jigsaw3" or experiment_name == "all":
        for iteration in run_list:
            for size in (size_list if size_list is not None else [400, 600, 800, 1000, 1200, 1400]):
                jigsaw_train_file = "data/jigsaw/3_jigsaw_{}_train.csv".format(iteration)
                jigsaw_desc_file = "data/jigsaw/3_jigsaw_desc.csv".format(iteration)  # Clique of the jigsaw
                jigsaw_equiv_file = "data/jigsaw/3_jigsaw_equiv.csv".format(iteration)  # Proved redundancy
                jigsaw_test_file = "data/jigsaw/3_jigsaw_test.csv".format(iteration)
                xp_jigsaw.run_jigsaw_81(FILE_TRAIN=jigsaw_train_file, DESC_FILE=jigsaw_desc_file,
                                        EQUIV_FILE=jigsaw_equiv_file, NB_EXAMPLES=size,
                                        FILE_TEST=jigsaw_test_file, ORDER_KR=order_kr)

    # Experiment 4: Subgraph isomorphism
    if experiment_name == "subgraph_isomorphism" or experiment_name == "all":
        for iteration in run_list:
            for size in (size_list if size_list is not None else [100, 400, 800]):
                subgraphisomorphism_train_file = "data/subgraphisomorphism/subgraph_{}.csv".format(iteration)
                subgraphisomorphism_descH_file = "data/subgraphisomorphism/subgraph_{}_H.csv".format(iteration)
                subgraphisomorphism_descG_file = "data/subgraphisomorphism/subgraph_{}_G.csv".format(iteration)
                subgraphisomorphism_test_file = "data/subgraphisomorphism/test_subgraph_{}.csv".format(iteration)
                xp_subgraph_isomorphism.run_subgraphisomorphism(FILE_TRAIN=subgraphisomorphism_train_file,
                                                                NB_EXAMPLES=size,
                                                                FILE_TEST=subgraphisomorphism_test_file,
                                                                DESC_H=subgraphisomorphism_descH_file,
                                                                DESC_G=subgraphisomorphism_descG_file,
                                                                ORDER_KR=order_kr, IT=iteration)

    # Experiment 5: Golomb ruler
    if experiment_name == "golombruler" or experiment_name == "all":
        for iteration in run_list:
            for size in (size_list if size_list is not None else [400, 800, 1600, 3200]):
                golombruler_train_file = "data/golombruler/golombruler_{}.csv".format(iteration)
                golombruler_test_file = "data/golombruler/golomb_test.csv".format(iteration)
                xp_golombruler.run_golombruler(FILE_TRAIN=golombruler_train_file,
                                               NB_EXAMPLES=size,
                                               FILE_TEST=golombruler_test_file,
                                               ORDER_KR=order_kr)

    # Experiment 6: Queens
    if experiment_name == "queens" or experiment_name == "all":
        for iteration in run_list:
            for size in (size_list if size_list is not None else [100, 184]):
                bandwidth_train_file = "data/queens/8_queens_{}_train.csv".format(iteration)
                bandwidth_test_file = "data/queens/8_queens_{}_test.csv".format(iteration)
                xp_queens.run_8queen(FILE_TRAIN=bandwidth_train_file,
                                     NB_EXAMPLES=size,
                                     FILE_TEST=bandwidth_test_file,
                                     ORDER_KR=order_kr)

    # Experiment 7: Ratio of positive examples in sudoku
    if experiment_name == "ratio_sudoku" or experiment_name == "all":
        for OBJ_SCOPES, OBJ_RELATIONS in [(10000, 1)]:
            for iteration in run_list:
                for percents in [0, 20, 40, 50, 60, 70, 80, 90, 100]:
                    ratio: float = percents / 100
                    sudoku_train_file_positive = "data/sudoku/ratio/old/sudoku_{}_train_positive.csv".format(iteration)
                    sudoku_train_file_negative = "data/sudoku/ratio/old/sudoku_{}_train_negative.csv".format(iteration)
                    sudoku_test_file = "data/sudoku/sudoku_test.csv"
                    max_size = 2000
                    current_size = max_size + 1
                    found = True
                    while found and current_size > 1:
                        current_size -= 1
                        found = xp_sudoku.run_ratio_sudoku_81(FILE_TRAIN_POSTIVE=sudoku_train_file_positive,
                                                              FILE_TRAIN_NEGATIVE=sudoku_train_file_negative,
                                                              NB_EXAMPLES=current_size, ORDER_KR=order_kr,
                                                              RATIO=ratio, OBJ_SCOPES=OBJ_SCOPES,
                                                              OBJ_RELATIONS=OBJ_RELATIONS, FILE_TEST=sudoku_test_file)
                    if current_size == max_size or current_size == 0:
                        logging.warning("No solution found for ratio {} with OBJ_SCOPES={} and OBJ_RELATIONS={}"
                                        " and iteration {}".format(ratio, OBJ_SCOPES, OBJ_RELATIONS, iteration))
                    else:
                        logging.info("IF THE RATIO IS {}, THE MINIMUM SIZE IS {} (ITERATION {}, OBJ_SCOPES={} and "
                                     "OBJ_RELATIONS={})".format(ratio, current_size + 1,
                                                                iteration, OBJ_SCOPES, OBJ_RELATIONS))
    # Custom experiment
    elif experiment_name == "custom" or experiment_name == "all":
        xp_custom.run()
    else:
        raise ValueError("Experiment not found")


if __name__ == '__main__':
    """
    Usage: python3 main.py <experiment_name>
           python3 main.py <experiment_name> <size>
           python3 main.py <experiment_name> <size> <run {1,2,3,4,5}>
    Available experiments: schurslemma, sudoku, jigsaw1, jigsaw2, jigsaw3,
                           subgraph_isomorphism, golombruler, queens, ratio_sudoku, custom, all
     """

    if len(sys.argv) < 2:
        print("Usage: python3 main.py <experiment_name>")
        print("       python3 main.py <experiment_name> <size>")
        print("       python3 main.py <experiment_name> <size> <run {1,2,3,4,5}>")
        print("Available experiments: schurslemma, sudoku, jigsaw1, jigsaw2, jigsaw3, subgraph_isomorphism, "
              "golombruler, queens, ratio_sudoku, custom, all")
        exit(1)

    experiment_name_param = sys.argv[1]
    if len(sys.argv) > 2:
        size_list_param = [int(sys.argv[2])]
    else:
        size_list_param = None
    if len(sys.argv) > 3:
        run_list_param = [int(sys.argv[3])]
    else:
        run_list_param = [1, 2, 3, 4, 5]
    run(experiment_name_param, size_list_param, run_list_param)
