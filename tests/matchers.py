from math import isclose, sqrt


class R3ApproxMatcher:
    def __init__(self, expected):
        self.expected = expected

    def __eq__(self, other):
        return isclose(self.expected.x, other.x) and \
            isclose(self.expected.y, other.y) and \
            isclose(self.expected.z, other.z)


class R3CollinearMatcher:
    def __init__(self, expected):
        self.expected = expected

    def __eq__(self, other):
        expected_dist = sqrt(self.expected.x**2 + self.expected.y**2 +
                             self.expected.z**2)
        other_dist = sqrt(other.x**2 + other.y**2 + other.z**2)
        t = self.expected.dot(other) / expected_dist / other_dist
        return isclose(t, 1.0)


class SegmentApproxMatcher:
    def __init__(self, expected):
        self.expected = expected

    def __eq__(self, other):
        return isclose(self.expected.beg, other.beg) and \
            isclose(self.expected.fin, other.fin) or \
            isclose(self.expected.beg, other.fin) and \
            isclose(self.expected.fin, other.beg)
