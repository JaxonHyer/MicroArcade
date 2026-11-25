# SpriteBound

SpriteBound is a full-color vertical-scrolling platformer for the **Thumby Color** (128×128 RGB565 display, RP2350 MicroPython/Tiny Game Engine). It uses `engine_io`, `engine_draw`, and `framebuffer`-compatible APIs only and does not use the monochrome Thumby API.

## Features

- Three hand-authored stages: **Sunset Steps**, **Glass Garden**, and **Star Summit**
- Automatic upward-follow camera
- Normal, spring, disappearing, and summit platforms
- Jump timing, horizontal momentum, wall clamping, and fall counting
- Headless Thumby Color emulator primitives for local tests
- Custom 38×38 RGB565 launcher icon

## Controls

- **D-Pad Left / Right**: Move
- **A**: Jump / Start / Restart
- **B**: Back or resume from pause
- **MENU**: Pause / resume

## Install

Copy the contents of `game/` to `/Games/SpriteBound/` on the Thumby Color filesystem:

- `main.py`
- `platform_engine.py`
- `renderer.py`
- `manifest.ini`
- `icon.bmp`

Then reopen or reboot the Thumby Color launcher.

## Local Tests

Run:

```bash
python3 -m unittest discover -s SpriteBound/tests -v
```

The suite installs a generic mocked Thumby Color engine, including 128×128 framebuffer, RGB565 drawing, buttons, saves, and engine timing. Generate a launcher icon with:

```bash
python3 tools/generate_thumby_icon.py SpriteBound/game/icon.bmp
```