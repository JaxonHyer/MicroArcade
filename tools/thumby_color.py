"""Reusable headless Thumby Color emulator primitives.

This module models the screen, RGB565 colors, engine I/O buttons, and save/audio
interfaces used by Thumby Color Tiny Game Engine games.
"""

W = 128
H = 128


def rgb(r, g, b):
    return ((r & 0xf8) << 8) | ((g & 0xfc) << 3) | ((b >> 3) & 0x1f)


class Button:
    def __init__(self):
        self.is_pressed = False
        self.is_just_pressed = False
        self.is_just_released = False
        self.is_pressed_autorepeat = False

    def clear_edges(self):
        self.is_just_pressed = False
        self.is_just_released = False
        self.is_pressed_autorepeat = False


class FrameBuffer:
    def __init__(self, w=W, h=H):
        self.w = w
        self.h = h
        self.pixels = [0] * (w * h)
        self.draw_calls = 0

    def fill(self, color):
        self.pixels = [color] * (self.w * self.h)
        self.draw_calls += 1

    def fill_rect(self, x, y, w, h, color):
        for py in range(max(0, y), min(self.h, y + h)):
            base = py * self.w
            for px in range(max(0, x), min(self.w, x + w)):
                self.pixels[base + px] = color
        self.draw_calls += 1

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def hline(self, x, y, w, color):
        if y < 0 or y >= self.h:
            return
        for px in range(max(0, x), min(self.w, x + w)):
            self.pixels[y * self.w + px] = color
        self.draw_calls += 1

    def vline(self, x, y, h, color):
        if x < 0 or x >= self.w:
            return
        for py in range(max(0, y), min(self.h, y + h)):
            self.pixels[py * self.w + x] = color
        self.draw_calls += 1

    def pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.pixels[y * self.w + x] = color
        self.draw_calls += 1


class HeadlessThumbyColor:
    """Installable emulator context for Python unit tests and simulations."""
    def __init__(self):
        self.fb = FrameBuffer()
        self.buttons = {name: Button() for name in (
            "UP", "DOWN", "LEFT", "RIGHT", "A", "B", "LB", "RB", "MENU")}
        self.saved = {}
        self.rumble_value = 0.0
        self.indicator_value = None
        self.dt = 1.0 / 60.0
        self.fps = 60
        self.tick_count = 0

    def press(self, name):
        button = self.buttons[name]
        button.is_pressed = True
        button.is_just_pressed = True

    def release(self, name):
        button = self.buttons[name]
        button.is_pressed = False
        button.is_just_released = True

    def clear_edges(self):
        for button in self.buttons.values():
            button.clear_edges()

    def install(self, sys=None):
        if sys is None:
            import sys as sys
        import types

        engine_main = types.ModuleType("engine_main")
        engine = types.ModuleType("engine")
        engine.fps_limit = lambda fps: setattr(self, "fps", fps)
        engine.dt = lambda: self.dt
        engine.tick = self._tick

        engine_draw = types.ModuleType("engine_draw")
        engine_draw.set_background_color = lambda c: None
        engine_draw.back_fb = lambda: self.fb
        engine_draw.back_fb_data = lambda: self.fb.pixels
        engine_draw.front_fb = lambda: self.fb
        engine_draw.rect = lambda c, x, y, w, h, outline, opacity: self.fb.rect(int(x), int(y), int(w), int(h), c) if outline else self.fb.fill_rect(int(x), int(y), int(w), int(h), c)
        engine_draw.circle = lambda c, x, y, r, outline, opacity: self._circle(c, x, y, r, outline)
        engine_draw.line = lambda c, x1, y1, x2, y2, opacity: self._line(c, x1, y1, x2, y2)
        engine_draw.text = lambda font, text, c, x, y, ls, lns, opacity: self._text(text, c, x, y)

        engine_io = types.ModuleType("engine_io")
        for name, button in self.buttons.items():
            setattr(engine_io, name, button)
        engine_io.rumble = lambda value: setattr(self, "rumble_value", float(value))
        engine_io.indicator = lambda value: setattr(self, "indicator_value", value)
        engine_io.release_all_buttons = lambda: self._release_all()

        engine_save = types.ModuleType("engine_save")
        engine_save.saves_dir = lambda: "/Saves/Games/SpriteBound"
        engine_save.set_location = lambda loc: None
        engine_save.save = lambda key, value: self.saved.__setitem__(key, value)
        engine_save.load = lambda key, default=None: self.saved.get(key, default)

        engine_audio = types.ModuleType("engine_audio")
        engine_audio.play = lambda resource, channel, loop: None
        engine_audio.stop = lambda channel: None
        engine_audio.set_volume = lambda volume: None

        engine_resources = types.ModuleType("engine_resources")
        engine_resources.WaveSoundResource = lambda path, in_ram=False: type("Wave", (), {"path": path})()

        modules = {
            "engine_main": engine_main,
            "engine": engine,
            "engine_draw": engine_draw,
            "engine_io": engine_io,
            "engine_save": engine_save,
            "engine_audio": engine_audio,
            "engine_resources": engine_resources,
        }
        sys.modules.update(modules)
        return modules

    def _tick(self):
        self.tick_count += 1
        return True

    def _release_all(self):
        for button in self.buttons.values():
            button.is_pressed = False
            button.is_just_pressed = False
            button.is_just_released = False
            button.is_pressed_autorepeat = False

    def _circle(self, color, cx, cy, radius, outline):
        cx, cy, radius = int(cx), int(cy), int(radius)
        r2 = radius * radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                d = (x-cx)*(x-cx)+(y-cy)*(y-cy)
                if d <= r2:
                    if not outline or d >= (radius-1)*(radius-1):
                        self.fb.pixel(x, y, color)

    def _line(self, color, x1, y1, x2, y2):
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
        dx = abs(x2-x1); sx = 1 if x1 < x2 else -1
        dy = -abs(y2-y1); sy = 1 if y1 < y2 else -1
        err = dx+dy
        while True:
            self.fb.pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2*err
            if e2 >= dy:
                err += dy; x1 += sx
            if e2 <= dx:
                err += dx; y1 += sy

    def _text(self, text, color, x, y):
        # Approximate text with a 5x7 framebuffer region for headless tests.
        self.fb.fill_rect(int(x), int(y), max(1, len(text)*5), 7, color)
