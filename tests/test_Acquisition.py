import pathlib
from unittest import TestCase

from src.languageFreeAcq import Acquisition


class TestAcquisition(TestCase):

    def setUp(self):
        self.train_path_sudoku = pathlib.Path(__file__).parent.parent.joinpath("data/sudoku/sudoku_1_train.csv")
        self.test_path_sudoku = pathlib.Path(__file__).parent.parent.joinpath("data/sudoku/sudoku_test.csv")

    def test_learn_sudoku_200examples(self):
        # We suppose that we have 100% of accuracy on "sudoku_test.csv" with 200 examples.
        l = Acquisition()
        n = l.learn(str(self.train_path_sudoku.absolute()), max_examples=200)
        self.assertEqual(l.get_domains(), [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(l.get_variables_numbers(), 81)
        accuracy = n.check_accuracy(str(self.test_path_sudoku.absolute()))
        self.assertEqual(accuracy, 1.0)

    def test_learn_sudoku_10examples(self):
        # We suppose that the accuracy is bellow 0.5 with only 6 examples.
        l = Acquisition()
        n = l.learn(str(self.train_path_sudoku.absolute()), max_examples=6)
        self.assertEqual(l.get_domains(), [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(l.get_variables_numbers(), 81)
        accuracy = n.check_accuracy(str(self.test_path_sudoku.absolute()))
        self.assertLess(accuracy, 0.6)
        self.assertGreater(accuracy, 0.4)
