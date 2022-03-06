from math import sin, cos


class R3:
    """ Вектор (точка) в R3 """

    # Конструктор
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    # Сумма векторов
    def __add__(self, other):
        return R3(self.x + other.x, self.y + other.y, self.z + other.z)

    # Разность векторов
    def __sub__(self, other):
        return R3(self.x - other.x, self.y - other.y, self.z - other.z)

    # Умножение на число
    def __mul__(self, k):
        return R3(k * self.x, k * self.y, k * self.z)

    # Поворот вокруг оси Oz
    def rz(self, fi):
        return R3(
            cos(fi) * self.x - sin(fi) * self.y,
            sin(fi) * self.x + cos(fi) * self.y, self.z)

    # Поворот вокруг оси Oy
    def ry(self, fi):
        return R3(cos(fi) * self.x + sin(fi) * self.z,
                  self.y, -sin(fi) * self.x + cos(fi) * self.z)

    # Скалярное произведение
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    # Векторное произведение
    def cross(self, other):
        return R3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x)


if __name__ == "__main__":
    x = R3(1.0, 1.0, 1.0)
    print("x", type(x), x.__dict__)
    y = x + R3(1.0, -1.0, 0.0)
    print("y", type(y), y.__dict__)
    y = y.rz(1.0)
    print("y", type(y), y.__dict__)
    u = x.dot(y)
    print("u", type(u), u)
    v = x.cross(y)
    print("v", type(v), v.__dict__)
