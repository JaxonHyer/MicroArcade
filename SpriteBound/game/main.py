# SpriteBound for Thumby Color.
import engine_main
import engine
import engine_io

from platform_engine import SpriteBoundGame
from renderer import Renderer


def read_inputs():
    return {
        "left": engine_io.LEFT.is_pressed,
        "right": engine_io.RIGHT.is_pressed,
        "a": engine_io.A.is_pressed,
        "b": engine_io.B.is_pressed,
        "a_just": engine_io.A.is_just_pressed,
        "b_just": engine_io.B.is_just_pressed,
        "menu_just": engine_io.MENU.is_just_pressed,
    }


def run():
    engine.fps_limit(60)
    game = SpriteBoundGame()
    renderer = Renderer()
    while True:
        if engine.tick():
            dt = engine.dt()
            if dt <= 0 or dt > 0.08:
                dt = 1.0/60.0
            inp = read_inputs()
            game.step(dt, inp)
            renderer.render(game)

run()
