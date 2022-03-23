#!/usr/bin/env -S python3 -B

from time import time
from common.tk_drawer import TkDrawer, x, y
import sys
try:
    exec(f'from optimize_{sys.argv[1]}.polyedr import Polyedr')
except(IndexError, ModuleNotFoundError):
    print("\nНеобходимо указание варианта оптимизации от 1 до 7, например,\n"
          "    ./run_optimize 1\n"
          "или\n"
          "    python run_optimize 1\n")
    exit(1)


def draw_line(self, p, q):
    self.canvas.create_line(x(p), y(p), x(q), y(q), fill="black", width=1)


setattr(TkDrawer, 'draw_line', draw_line)

tk = TkDrawer()

try:
    for name in ["ccc", "cube", "box", "king", "cow"]:
        print("=======================================================")
        print(f"Начало работы с полиэдром '{name}'")
        start_init_time = time()
        print("Инициализация -------------------------> ", end="", flush=True)
        poly = Polyedr(f"data/{name}.geom")
        start_optimize_time = time()
        print("%6.2f сек." % (start_optimize_time - start_init_time))
        print("Оптимизация ---------------------------> ", end="", flush=True)
        optimize_statistics = poly.optimize()
        start_shadow_time = time()
        print("%6.2f сек.\n%s" % (start_shadow_time -
                                  start_optimize_time, optimize_statistics))
        print("Удаление невидимых линий --------------> ", end="", flush=True)
        poly.shadow()
        start_draw_time = time()
        print("%6.2f сек." % (start_draw_time - start_shadow_time))
        print("Изображение полиэдра ------------------> ", end="", flush=True)
        poly.draw(tk)
        tk.root.update()
        print("%6.2f сек." % (time() - start_draw_time))
        input("Hit 'Return' to continue -> ")
except(EOFError, KeyboardInterrupt):
    print("\nStop")
    tk.close()
