# Micro Moto for Thumby Color (MicroPython / Tiny Game Engine).
import engine_main
import engine
import engine_io

from moto_engine import MotoGame
from renderer import Renderer
from storage import SaveStore


def read_inputs():
    return {
        "up": engine_io.UP.is_pressed,
        "down": engine_io.DOWN.is_pressed,
        "left": engine_io.LEFT.is_pressed,
        "right": engine_io.RIGHT.is_pressed,
        "a": engine_io.A.is_pressed,
        "b": engine_io.B.is_pressed,
        "lb": engine_io.LB.is_pressed,
        "rb": engine_io.RB.is_pressed,
        "up_nav": engine_io.UP.is_pressed_autorepeat,
        "down_nav": engine_io.DOWN.is_pressed_autorepeat,
        "left_nav": engine_io.LEFT.is_pressed_autorepeat,
        "right_nav": engine_io.RIGHT.is_pressed_autorepeat,
        "a_just": engine_io.A.is_just_pressed,
        "b_just": engine_io.B.is_just_pressed,
        "lb_just": engine_io.LB.is_just_pressed,
        "rb_just": engine_io.RB.is_just_pressed,
        "menu_just": engine_io.MENU.is_just_pressed,
    }


def run():
    engine.fps_limit(60)
    store=SaveStore()
    game=MotoGame(store)
    renderer=Renderer()
    running=True
    try:
        while running:
            if engine.tick():
                dt=engine.dt()
                if dt<=0 or dt>0.08:
                    dt=1.0/60.0
                inp=read_inputs()
                game.step(dt,inp)
                renderer.render(game)
    finally:
        store.save_all()

run()
