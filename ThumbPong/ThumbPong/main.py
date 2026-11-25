# ThumbPong for Thumby Color (MicroPython / Tiny Game Engine)
import engine_main

import engine
import engine_io

from themes import THEMES, get_theme
from storage import SaveStore
from audio_haptics import AudioHaptics
from pong_engine import PongGame, DIFFICULTY_NAMES
from renderer import Renderer

WIN_SCORES = (5, 7, 11)


def button_pressed(name):
    button = getattr(engine_io, name, None)
    return bool(button is not None and getattr(button, "is_pressed", False))


def button_just_pressed(name):
    button = getattr(engine_io, name, None)
    return bool(button is not None and getattr(button, "is_just_pressed", False))


def button_autorepeat(name):
    button = getattr(engine_io, name, None)
    return bool(button is not None and getattr(button, "is_pressed_autorepeat", False))


def release_buttons():
    try:
        release = getattr(engine_io, "release_all_buttons", None)
        if release is not None:
            release()
    except Exception:
        pass


def read_inputs():
    return {
        "up": button_pressed("UP"),
        "down": button_pressed("DOWN"),
        "up_nav": button_autorepeat("UP"),
        "down_nav": button_autorepeat("DOWN"),
        "left_just": button_just_pressed("LEFT"),
        "right_just": button_just_pressed("RIGHT"),
        "a": button_pressed("A"),
        "b": button_pressed("B"),
        "a_just": button_just_pressed("A"),
        "b_just": button_just_pressed("B"),
        "lb_just": button_just_pressed("LB"),
        "rb_just": button_just_pressed("RB"),
        "rb": button_pressed("RB"),
        "menu_just": button_just_pressed("MENU"),
    }


def cycle_theme(game, store, ah, delta):
    game.theme_idx = (game.theme_idx + delta) % len(THEMES)
    store.set("theme_idx", game.theme_idx)
    ah.play("menu_move")


def handle_title(game, inp, store, ah):
    # Live theme cycling with LB/RB
    if inp["lb_just"]:
        cycle_theme(game, store, ah, -1)
    elif inp["rb_just"]:
        cycle_theme(game, store, ah, 1)

    if inp["up_nav"]:
        game.title_idx = (game.title_idx - 1) % 5
        ah.play("menu_move")
    elif inp["down_nav"]:
        game.title_idx = (game.title_idx + 1) % 5
        ah.play("menu_move")

    if inp["menu_just"]:
        ah.play("menu_ok")
        return False

    if inp["a_just"]:
        ah.play("menu_ok")
        release_buttons()
        if game.title_idx == 0:
            game.start_match("1p")
        elif game.title_idx == 1:
            game.start_match("2p")
        elif game.title_idx == 2:
            game.start_match("arcade")
        elif game.title_idx == 3:
            game.opt_idx = 0
            game.state = "options"
        elif game.title_idx == 4:
            return False

    return True


def handle_options(game, inp, store, ah):
    if inp["up_nav"]:
        game.opt_idx = (game.opt_idx - 1) % 6
        ah.play("menu_move")
    elif inp["down_nav"]:
        game.opt_idx = (game.opt_idx + 1) % 6
        ah.play("menu_move")

    if inp["b_just"] or inp["menu_just"]:
        ah.play("menu_ok")
        game.state = "title"
        return

    delta = 0
    if inp["right_just"] or inp["a_just"]:
        delta = 1
    elif inp["left_just"]:
        delta = -1

    if delta != 0:
        if game.opt_idx == 0:
            cycle_theme(game, store, ah, delta)
        elif game.opt_idx == 1:
            game.difficulty = (game.difficulty + delta) % len(DIFFICULTY_NAMES)
            store.set("difficulty", game.difficulty)
            ah.play("menu_move")
        elif game.opt_idx == 2:
            cur_i = 1
            for idx, ws in enumerate(WIN_SCORES):
                if ws == game.win_score:
                    cur_i = idx
                    break
            game.win_score = WIN_SCORES[(cur_i + delta) % len(WIN_SCORES)]
            store.set("win_score", game.win_score)
            ah.play("menu_move")
        elif game.opt_idx == 3:
            ah.sound_on = not ah.sound_on
            store.set("sound_on", 1 if ah.sound_on else 0)
            ah.play("menu_move")
        elif game.opt_idx == 4:
            ah.rumble_on = not ah.rumble_on
            store.set("rumble_on", 1 if ah.rumble_on else 0)
            if ah.rumble_on:
                ah.rumble(0.45, 45)
            ah.play("menu_move")
        elif game.opt_idx == 5 and inp["a_just"]:
            ah.play("menu_ok")
            game.state = "title"


def handle_pause(game, inp, store, ah):
    if inp["menu_just"] or inp["b_just"]:
        ah.play("menu_ok")
        release_buttons()
        game.state = "playing"
        return

    if inp["up_nav"]:
        game.pause_idx = (game.pause_idx - 1) % 6
        ah.play("menu_move")
    elif inp["down_nav"]:
        game.pause_idx = (game.pause_idx + 1) % 6
        ah.play("menu_move")

    delta = 0
    if inp["right_just"] or inp["a_just"]:
        delta = 1
    elif inp["left_just"]:
        delta = -1

    if delta != 0:
        if game.pause_idx == 0 and inp["a_just"]:
            ah.play("menu_ok")
            release_buttons()
            game.state = "playing"
        elif game.pause_idx == 1 and inp["a_just"]:
            ah.play("menu_ok")
            release_buttons()
            game.start_match(game.mode)
        elif game.pause_idx == 2:
            cycle_theme(game, store, ah, delta)
        elif game.pause_idx == 3:
            ah.sound_on = not ah.sound_on
            store.set("sound_on", 1 if ah.sound_on else 0)
            ah.play("menu_move")
        elif game.pause_idx == 4:
            ah.rumble_on = not ah.rumble_on
            store.set("rumble_on", 1 if ah.rumble_on else 0)
            if ah.rumble_on:
                ah.rumble(0.45, 45)
            ah.play("menu_move")
        elif game.pause_idx == 5 and inp["a_just"]:
            ah.play("menu_ok")
            release_buttons()
            game.start_attract_demo()


def handle_gameover(game, inp, ah):
    if inp["a_just"]:
        ah.play("menu_ok")
        release_buttons()
        game.start_match(game.mode)
    elif inp["b_just"] or inp["menu_just"]:
        ah.play("menu_ok")
        release_buttons()
        game.start_attract_demo()


def run():
    engine.fps_limit(60)
    store = SaveStore()
    ah = AudioHaptics(
        sound_on=bool(store.get("sound_on")),
        rumble_on=bool(store.get("rumble_on")),
    )
    game = PongGame(store, ah)
    renderer = Renderer()

    running = True
    try:
        while running:
            if engine.tick():
                dt = engine.dt()
                if dt <= 0.0 or dt > 0.08:
                    dt = 1.0 / 60.0

                ah.update(dt * 1000.0)
                inp = read_inputs()
                theme = get_theme(game.theme_idx)

                if game.state == "title":
                    running = handle_title(game, inp, store, ah)
                    if running:
                        game.step_simulation(dt, inp, theme)
                elif game.state == "options":
                    handle_options(game, inp, store, ah)
                    game.step_simulation(dt, inp, theme)
                elif game.state == "playing":
                    if inp["menu_just"]:
                        ah.stop_rumble()
                        ah.play("menu_ok")
                        game.pause_idx = 0
                        game.state = "paused"
                    else:
                        game.step_simulation(dt, inp, theme)
                elif game.state == "paused":
                    handle_pause(game, inp, store, ah)
                elif game.state == "gameover":
                    handle_gameover(game, inp, ah)
                    game.step_simulation(dt, inp, theme)

                if running:
                    renderer.render(game)
    finally:
        store.save_all()
        ah.cleanup()


run()
