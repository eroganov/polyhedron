import unittest

from functools import reduce
from operator import add
from shadow.polyedr import Segment
from tests.matchers import SegmentApproxMatcher


def flatten(list):
    return [s for s in reduce(add, list, []) if not s.is_degenerate()]


class TestSegment(unittest.TestCase):

    # Отрезок [0,1] является невырожденным
    def test_degenerate01(self):
        self.assertFalse(Segment(0.0, 1.0).is_degenerate())

    # Отрезок [0,0] является вырожденным
    def test_degenerate02(self):
        self.assertTrue(Segment(0.0, 0.0).is_degenerate())

    # Отрезок [0,-1] является вырожденным
    def test_degenerate03(self):
        self.assertTrue(Segment(0.0, -1.0).is_degenerate())

    # Пересечение отрезка с самим собой даёт его же
    def test_intersect01(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 1.0)
        c = Segment(0.0, 1.0)
        self.assertEqual(SegmentApproxMatcher(a.intersect(b)), c)

    # Пересечение меньшего отрезка с большим даёт меньший
    def test_intersect02(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 2.0)
        c = Segment(1.0, 0.0)
        self.assertEqual(SegmentApproxMatcher(a.intersect(b)), c)

    # Пересечение коммутативно
    def test_intersect03(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 2.0)
        c = Segment(0.0, 1.0)
        d = Segment(0.0, 2.0)
        self.assertEqual(SegmentApproxMatcher(a.intersect(b)), d.intersect(c))

        a = Segment(0.0, 1.0)
        b = Segment(0.5, 1.0)
        c = Segment(0.0, 1.0)
        d = Segment(0.5, 1.0)
        self.assertEqual(SegmentApproxMatcher(a.intersect(b)), d.intersect(c))

        a = Segment(0.0, 1.0)
        b = Segment(-0.5, 0.0)
        c = Segment(0.0, 1.0)
        d = Segment(-0.5, 0.0)
        self.assertEqual(SegmentApproxMatcher(a.intersect(b)), d.intersect(c))

        a = Segment(0.0, 1.0)
        b = Segment(-0.5, -0.1)
        c = Segment(0.0, 1.0)
        d = Segment(-0.5, -0.1)
        self.assertEqual(SegmentApproxMatcher(a.intersect(b)), d.intersect(c))

    # Разность отрезка с самим собой — два вырожденных отрезка
    def test_subtraction01(self):
        a, b = Segment(0.0, 1.0), Segment(0.0, 1.0)
        self.assertTrue(all(s.is_degenerate() for s in a.subtraction(b)))

    # Для двух отрезков с совпадающим началом вычитание из большего отрезка
    # меньшего порождает один вырожденный и один невырожденный отрезок
    def test_subtraction02(self):
        a, b = Segment(0.0, 2.0), Segment(0.0, 1.0)
        self.assertTrue(any(s.is_degenerate() for s in a.subtraction(b)))
        self.assertTrue(any(not s.is_degenerate() for s in a.subtraction(b)))

    # Для двух отрезков с различными концами таких, что один из них содержится
    # внутри другого, вычитание из большего отрезка меньшего порождает два
    # невырожденных отрезка
    def test_subtraction03(self):
        a, b = Segment(-1.0, 2.0), Segment(0.0, 1.0)
        self.assertTrue(all(not s.is_degenerate() for s in a.subtraction(b)))

    # Для двух отрезков с различными концами таких, что один из них содержится
    # внутри другого, вычитание из меньшего отрезка большего порождает два
    # вырожденных отрезка
    def test_subtraction04(self):
        a, b = Segment(-1.0, 2.0), Segment(0.0, 1.0)
        self.assertTrue(all(s.is_degenerate() for s in b.subtraction(a)))

    # Если из отрезка вычесть две его половинки, то получатся только
    # вырожденные отрезки
    def test_subtraction05(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 0.5)
        c = Segment(0.5, 1.0)
        self.assertTrue(all(t.is_degenerate() for
                            t in flatten(s.subtraction(c) for
                                         s in a.subtraction(b))))

    # Если из отрезка вычесть его половинку, а затем ещё один небольшой
    # отрезочек, то невырожденным будет только один из итоговых отрезков
    def test_subtraction06(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.0, 0.5)
        c = Segment(0.6, 1.0)
        self.assertEqual(len(list(not t.is_degenerate() for
                                  t in flatten(s.subtraction(c) for
                                               s in a.subtraction(b)))), 1)

    # Если из отрезка вычесть два небольших отрезочка, то невырожденными
    # будут все три итоговых отрезка
    def test_subtraction07(self):
        a = Segment(0.0, 1.0)
        b = Segment(0.1, 0.2)
        c = Segment(0.4, 0.8)
        self.assertEqual(len(list(not t.is_degenerate() for
                                  t in flatten(s.subtraction(c) for
                                               s in a.subtraction(b)))), 3)
