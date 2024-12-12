from unittest import TestCase

from src.languageFreeAcq import kr_generator


class TestAcquisition(TestCase):

    def test_kr_generator(self):
        order_kr = [(1, 1), (2, 1), (3, 1), (4, 1), (1, 2), (5, 1), (2, 2), (6, 1), (3, 2), (7, 1), (4, 2),
                    (8, 1), (5, 2), (9, 1), (6, 2), (1, 3), (10, 1), (7, 2), (2, 3), (11, 1), (8, 2), (3, 3),
                    (12, 1), (9, 2), (4, 3), (13, 1), (10, 2), (5, 3), (14, 1), (11, 2), (6, 3), (15, 1), (12, 2),
                    (7, 3), (16, 1), (13, 2), (8, 3), (1, 4), (17, 1), (14, 2), (9, 3), (2, 4), (18, 1), (15, 2)]
        gen = kr_generator()
        self.assertEqual([next(gen) for _ in range(len(order_kr))], order_kr)
        gen2 = kr_generator()
        self.assertEqual([next(gen2) for _ in range(1000)][-1], (37, 10))
