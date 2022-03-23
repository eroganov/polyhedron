#!/usr/bin/env -S python3 -B

from time import time
from common.tk_drawer import TkDrawer
from preoptimize.polyedr import Polyedr

tk = TkDrawer()

try:
    for name in ["ccc", "cube", "box", "king", "cow"]:
        print("=======================================================")
        print(f"Начало работы с полиэдром '{name}'")
        start_init_time = time()
        print("Инициализация -------------------------> ", end="", flush=True)
        poly = Polyedr(f"data/{name}.geom")
        start_shadow_time = time()
        print("%6.2f сек." % (start_shadow_time - start_init_time))
        print("Удаление невидимых линий --------------> ", end="", flush=True)
        poly.shadow()
        start_draw_time = time()
        print("%6.2f сек." % (start_draw_time - start_shadow_time))
        print("Изображение полиэдра ------------------> ", end="", flush=True)
        poly.draw(tk)
        print("%6.2f сек." % (time() - start_draw_time))
        input("Hit 'Return' to continue -> ")
except(EOFError, KeyboardInterrupt):
    print("\nStop")
    tk.close()
