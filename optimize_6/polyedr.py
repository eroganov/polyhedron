from math import pi
from time import time
from functools import reduce
from operator import add
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Segment:
    """ Одномерный отрезок """
    # Параметры конструктора: начало и конец отрезка (числа)

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    # Отрезок вырожден?
    def is_degenerate(self):
        return self.beg >= self.fin

    # Пересечение с отрезком
    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    # Разность отрезков
    # Разность двух отрезков всегда является списком из двух отрезков!
    def subtraction(self, other):
        return [Segment(
            self.beg, self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)]


class Edge:
    """ Ребро полиэдра """
    # Начало и конец стандартного одномерного отрезка
    SBEG, SFIN = 0.0, 1.0

    # Параметры конструктора: начало и конец ребра (точки в R3)
    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        # Список «просветов»
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    # Учёт тени от одной грани
    def shadow(self, facet):
        # Не надо ничего делать, если «просветов» на ребере не осталось
        if len(self.gaps) == 0:
            return

        # xy-прямоугольник грани должен пересекать xy-прямоугольник ребра
        if (min([self.beg.x, self.fin.x]) > facet.xmax or
            max([self.beg.x, self.fin.x]) < facet.xmin or
            min([self.beg.y, self.fin.y]) > facet.ymax or
                max([self.beg.y, self.fin.y]) < facet.ymin):
            return

        # «Низкие» и «вертикальные» грани не могут затенить ребро
        if ((self.beg.z >= facet.zmax and self.fin.z >= facet.zmax) or
                facet.is_vertical()):
            return

        # Нахождение одномерной тени на ребре
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(
                facet.vertexes[0], facet.h_normal()))
        if shade.is_degenerate():
            return
        # Преобразование списка «просветов», если тень невырождена
        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [
            s for s in reduce(add, gaps, []) if not s.is_degenerate()]

    # Преобразование одномерных координат в трёхмерные
    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    # Пересечение ребра с полупространством, задаваемым точкой (a)
    # на плоскости и вектором внешней нормали (n) к ней
    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = - f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)


class Facet:
    """ Грань полиэдра """
    # Параметры конструктора: список вершин

    def __init__(self, vertexes):
        self.vertexes = vertexes

    # «Вертикальна» ли грань?
    def is_vertical(self):
        return self._is_vertical

    # Нормаль к «горизонтальному» полупространству
    def h_normal(self):
        return self._h_normal

    # Нормали к «вертикальным» полупространствам, причём k-я из них
    # является нормалью к грани, которая содержит ребро, соединяющее
    # вершины с индексами k-1 и k
    def v_normals(self):
        return self._v_normals

    # Центр грани
    def center(self):
        return self._center

    # Предкомпиляция грани
    def precompile(self):
        self._center = sum(self.vertexes, R3(0.0, 0.0, 0.0)
                           ) * (1.0 / len(self.vertexes))
        n = (
            self.vertexes[1] - self.vertexes[0]).cross(
            self.vertexes[2] - self.vertexes[0])
        self._h_normal = n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n
        self._v_normals = [self._vert(x) for x in range(len(self.vertexes))]
        self._is_vertical = self.h_normal().dot(Polyedr.V) == 0.0
        self.zmax = max(v.z for v in self.vertexes)
        self.xmin = min(v.x for v in self.vertexes)
        self.ymin = min(v.y for v in self.vertexes)
        self.xmax = max(v.x for v in self.vertexes)
        self.ymax = max(v.y for v in self.vertexes)

    # Вспомогательный метод
    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * \
            (-1.0) if n.dot(self.vertexes[k - 1] - self.center()) < 0.0 else n


class Polyedr:
    """ Полиэдр """
    # вектор проектирования
    V = R3(0.0, 0.0, 1.0)

    # Параметры конструктора: файл, задающий полиэдр
    def __init__(self, file):

        # списки вершин, рёбер и граней полиэдра
        self.vertexes, self.edges, self.facets = [], [], []

        # список строк файла
        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    # обрабатываем первую строку; buf - вспомогательный массив
                    buf = line.split()
                    # коэффициент гомотетии
                    c = float(buf.pop(0))
                    # углы Эйлера, определяющие вращение
                    alpha, beta, gamma = (float(x) * pi / 180.0 for x in buf)
                elif i == 1:
                    # во второй строке число вершин, граней и рёбер полиэдра
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    # задание всех вершин полиэдра
                    x, y, z = (float(x) for x in line.split())
                    self.vertexes.append(R3(x, y, z).rz(
                        alpha).ry(beta).rz(gamma) * c)
                else:
                    # вспомогательный массив
                    buf = line.split()
                    # количество вершин очередной грани
                    size = int(buf.pop(0))
                    # массив вершин этой грани
                    vertexes = list(self.vertexes[int(n) - 1] for n in buf)
                    # задание рёбер грани
                    for n in range(size):
                        self.edges.append(Edge(vertexes[n - 1], vertexes[n]))
                    # задание самой грани
                    self.facets.append(Facet(vertexes))

    # Удаление дубликатов рёбер
    def edges_uniq(self):
        edges = {}
        for e in self.edges:
            if (e.beg, e.fin) not in edges and (e.fin, e.beg) not in edges:
                edges[(e.beg, e.fin)] = e
        self.edges = list(edges.values())

    # Оптимизация
    def optimize(self):
        stage_time = time()
        result = "   Удаление дубликатов рёбер\n" + \
            "     Рёбер до    : %6d\n" % len(self.edges)
        self.edges_uniq()
        result += "     Рёбер после : %6d\n" % len(self.edges) + \
            "     Время       : %6.2f сек.\n" % (time() - stage_time)
        stage_time = time()
        for f in self.facets:
            f.precompile()
        result += "   Предкомпиляция граней\n" + \
            "     Время       : %6.2f сек." % (time() - stage_time)
        return result

    # Нахождение «просветов»
    def shadow(self):
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
        return self

    # Метод изображения полиэдра
    def draw(self, tk):
        tk.clean()
        for e in self.edges:
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))
