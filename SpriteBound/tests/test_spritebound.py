"""Headless Thumby Color tests for SpriteBound."""
import os
import struct
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game")
TOOLS = os.path.dirname(ROOT)
for path in (GAME, TOOLS):
    if path not in sys.path:
        sys.path.insert(0, path)

from tools.thumby_color import HeadlessThumbyColor


class TestSpriteBound(unittest.TestCase):
    def setUp(self):
        self.emu = HeadlessThumbyColor()
        self.emu.install(sys)
        for mod in ("main", "renderer", "platform_engine"):
            sys.modules.pop(mod, None)

    def test_manifest_and_icon(self):
        manifest = os.path.join(GAME, "manifest.ini")
        with open(manifest, "r") as f:
            text = f.read()
        self.assertIn("name = SpriteBound", text)
        self.assertIn("main = main.py", text)

        icon = os.path.join(GAME, "icon.bmp")
        self.assertTrue(os.path.isfile(icon))
        with open(icon, "rb") as f:
            data = f.read()
        self.assertEqual(data[:2], b"BM")
        bf_size, _, _, off = struct.unpack_from("<IHHI", data, 2)
        self.assertEqual(bf_size, len(data))
        self.assertEqual(off, 66)
        bi_size, width, height, planes, bpp, comp, image_size = struct.unpack_from("<IiiHHII", data, 14)
        self.assertEqual((bi_size, width, height, planes, bpp, comp), (52, 38, 38, 1, 16, 3))
        self.assertEqual(image_size, 38*38*2)

    def test_title_starts_game_on_a(self):
        from platform_engine import SpriteBoundGame
        game = SpriteBoundGame()
        self.assertEqual(game.state, "title")
        game.step(1/60, {"a_just": True})
        self.assertEqual(game.state, "playing")
        self.assertEqual(game.level, 0)

    def test_movement_jump_and_camera(self):
        from platform_engine import SpriteBoundGame
        game = SpriteBoundGame(); game.start()
        p = game.player
        p["x"] = 20
        p["y"] = 70
        p["vy"] = 0
        game.step(1/60, {"right": True, "a_just": True})
        self.assertGreater(p["vx"], 0)
        self.assertLess(p["vy"], 0)

        p["y"] = -20
        game.step(1/60, {"right": True})
        self.assertLess(game.camera, 0)

    def test_all_three_levels_and_victory(self):
        from platform_engine import SpriteBoundGame
        game = SpriteBoundGame(); game.start()
        for level in range(3):
            self.assertEqual(game.level, level)
            goal = next(p for p in game.platforms if p["kind"] == "goal")
            p = game.player
            p["x"] = goal["x"]
            p["y"] = goal["y"] - p["h"]
            p["vy"] = 0
            game.complete_timer = 0.34
            game.step(1/60, {})
        self.assertEqual(game.level, 2)

    def test_spring_and_disappearing_platforms_exist(self):
        from platform_engine import make_platforms
        for level in range(3):
            platforms = make_platforms(level)
            kinds = {p["kind"] for p in platforms}
            self.assertIn("goal", kinds)
            self.assertIn("spring", kinds)
            self.assertIn("vanish", kinds)

    def test_renderer_three_hundred_frames(self):
        from platform_engine import SpriteBoundGame
        from renderer import Renderer
        game = SpriteBoundGame(); renderer = Renderer(); game.start()
        for i in range(300):
            inp = {"right": i < 100, "left": 150 < i < 210,
                   "a_just": i in (20, 70, 120, 170, 220)}
            game.step(1/60, inp)
            renderer.render(game)
        self.assertGreater(self.emu.fb.draw_calls, 300)


if __name__ == "__main__":
    unittest.main()
