import logging

from tqdm import tqdm


def kr_generator():
    """
    Generator that yields kr values in ascending order based on k + r^2.
    If there is a tie, it yields the value with the smallest r first.
    """
    to_yield = [(1, 1)]
    yielded = set()
    while True:
        to_yield.sort(key=lambda x: x[0] + x[1] ** 2 + 0.1 * x[1])
        yield to_yield[0]
        yielded.add(to_yield.pop(0))
        for (k, r) in yielded:
            if (k+1, r) not in yielded and (k+1, r) not in to_yield:
                to_yield.append((k+1, r))
            if (k, r+1) not in yielded and (k, r+1) not in to_yield:
                to_yield.append((k, r+1))


def progress_bar(maxi: int, title: str = "", active: bool = True):
    """
    Create a progress bar using TQDM, this wrapper allow to simply change progress bar settings
    """
    return tqdm(total=maxi, desc=title, disable=not active)


def common_lines(file1, file2):
    """
    Count the number of common lines between two files
    :param file1: the first file
    :param file2: the second file
    :return: None
    """
    with open(file1, 'r') as f1:
        lines1 = f1.readlines()
    with open(file2, 'r') as f2:
        lines2 = f2.readlines()
    lines2_set = set(lines2)
    common_lines_file = 0
    for line in lines1:
        if line in lines2_set:
            common_lines_file += 1
    repeated_lines = len(lines2) - len(lines2_set)
    logging.debug(f'Number of repeated lines: {repeated_lines}')
    logging.debug(f'Number of common lines: {common_lines_file}')


def paradox_free(file: str):
    """
    Check if the given file is paradox-free, i.e. it does not contain two line with the same values but one
    finishing with 0 and the other with 1.
    :param file: the file to check
    :return: True if the file is paradox-free, False otherwise
    """
    with open(file, 'r') as f:
        lines = f.readlines()
        examples_dict = {}
        line_nb = 0
        for line in lines:
            line_nb += 1
            example = line.split(",")
            weight = int(example[-1])
            example = tuple([int(x) for x in example[:-1]])
            if example not in examples_dict:
                examples_dict[example] = (weight, line_nb)
            else:
                if examples_dict[example][0] != weight:
                    logging.info("Paradox found between line {} and line {} on the file {}."
                                 .format(examples_dict[example][1], line_nb, file))
                    return False
    logging.debug("No paradox found")
    return True
