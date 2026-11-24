# SpriteBound
A **Thumby Color** (128×128, Tiny Game Engine / MicroPython) vertical-scrolling platformer. Three hand-built stages, spring and disappearing platforms, automatic upward camera, fall counter, and a summit finish. This does **not** use the monochrome Thumby API.

## Install / play

Copy `SpriteBound/game.py` and `SpriteBound/main.py` to `/Games/SpriteBound/` on the Thumby Color using the [Color code editor](https://color.thumby.us/code/). Launch `main.py`. Left/right moves, A or B jumps; press A on the title/win screen to start. Spring platforms (cyan) bounce automatically, pink platforms crumble, gold is the exit. Missing a jump resets the stage.

## Headless testing

Run `python3 -m unittest discover -s tests -v` or `python3 -m SpriteBound.headless.runner` on a desktop. The lightweight headless engine adapter models the **Color Tiny Game Engine** modules and 128×128 coordinate system, not the B&W Thumby emulator. It runs the actual entry point for a fixed number of frames and validates node positions and UI. Physics is tested separately without a display. This is an API-level simulation, **not** the official Color IDE's WASM firmware: the public `TinyCircuits-Thumby-Code-Editor` repository is for the original monochrome Thumby and cannot accurately emulate Color hardware. For hardware/firmware validation use the [Tiny Game Engine Linux build instructions](https://github.com/TinyCircuits/TinyCircuits-Tiny-Game-Engine#building-on-linux-for-linux).
