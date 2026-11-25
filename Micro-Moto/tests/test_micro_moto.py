"""Headless Thumby Color tests for Micro Moto."""
import os
import struct
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game")
REPO = os.path.dirname(ROOT)
for path in (GAME, REPO):
    if path not in sys.path:
        sys.path.insert(0, path)

from tools.thumby_color import HeadlessThumbyColor


class TestMicroMoto(unittest.TestCase):
    def setUp(self):
        self.emu = HeadlessThumbyColor()
        self.emu.install(sys)
        for mod in ("main", "moto_engine", "level_catalog", "renderer", "storage", "audio_haptics"):
            sys.modules.pop(mod, None)

    def test_manifest_icon_and_readme_50_level_goal(self):
        manifest = os.path.join(GAME, "manifest.ini")
        with open(manifest, "r") as f:
            text = f.read()
        self.assertIn("name = Micro Moto", text)
        icon = os.path.join(GAME, "icon.bmp")
        self.assertTrue(os.path.isfile(icon))
        with open(icon, "rb") as f:
            data = f.read()
        self.assertEqual(data[:2], b"BM")
        bf_size, _, _, off = struct.unpack_from("<IHHI", data, 2)
        self.assertEqual(bf_size, len(data))
        self.assertEqual(off, 66)
        bi_size, width, height, planes, bpp, comp = struct.unpack_from("<IiiHHH", data, 14)
        self.assertEqual((bi_size, width, height, planes, bpp, comp), (52, 38, 38, 1, 16, 3))
        with open(os.path.join(ROOT, "README.md"), "r") as f:
            readme = f.read()
        self.assertIn("50-level", readme)

    def test_catalog_has_exactly_fifty_deterministic_levels(self):
        from level_catalog import get_level, LEVEL_COUNT
        self.assertEqual(LEVEL_COUNT, 50)
        names = set()
        for i in range(50):
            level = get_level(i)
            again = get_level(i)
            self.assertEqual(level["terrain"], again["terrain"])
            self.assertGreater(level["length"], 500)
            self.assertGreater(len(level["terrain"]), 50)
            self.assertTrue(level["checkpoints"] == sorted(level["checkpoints"]))
            names.add(level["name"])
        self.assertGreaterEqual(len(names), 50)

    def test_first_five_are_hand_authored_and_have_hazards_checkpoints(self):
        from level_catalog import get_level
        for i in range(5):
            level = get_level(i)
            self.assertTrue(level["checkpoints"])
            self.assertTrue(level["hazards"])
            self.assertIn(level["name"], ("GREEN START","SUNRUN","GLASS RIDGE","CHECKPOINT CLIMB","FIRE SUMMIT"))

    def test_title_menu_level_select_settings_and_pause(self):
        from moto_engine import MotoGame
        game = MotoGame()
        self.assertEqual(game.state, "title")
        game.step(1/60, {"down_nav": True})
        self.assertEqual(game.title_option, 1)
        game.step(1/60, {"a_just": True})
        self.assertEqual(game.state, "level_select")
        game.step(1/60, {"a_just": True})
        self.assertEqual(game.state, "playing")
        game.step(1/60, {"menu_just": True})
        self.assertEqual(game.state, "paused")
        game.step(1/60, {"menu_just": True})
        self.assertEqual(game.state, "playing")

    def test_accelerate_brake_and_lean_are_applied(self):
        from moto_engine import MotoGame
        game = MotoGame(); game.start_level(0)
        p = game.player
        p["ground"] = True
        game.step(1/60, {"up": True, "right": True})
        self.assertGreater(p["vx"], 0)
        vx = p["vx"]
        game.step(1/60, {"down": True})
        self.assertLess(p["vx"], vx)
        av = p["av"]
        game.step(1/60, {"left": True})
        self.assertLess(p["av"], av)

    def test_checkpoint_respawn_keeps_timer_and_requires_a(self):
        from moto_engine import MotoGame
        import math
        game = MotoGame(); game.start_level(0)
        game.player["x"] = 380
        game.elapsed = 12.5
        game.step(1/60, {})
        self.assertGreaterEqual(game.checkpoint, 1)
        game.player["y"] = 200
        game.player["angle"] = math.pi
        game.step(1/60, {})
        self.assertEqual(game.state, "crashed")
        elapsed = game.elapsed
        game.step(1/60, {})
        self.assertEqual(game.state, "crashed")
        game.step(1/60, {"a_just": True})
        self.assertEqual(game.state, "playing")
        self.assertEqual(game.elapsed, elapsed)
        self.assertGreater(game.player["x"], 300)

    def test_finish_records_best_and_unlocks_next_level(self):
        from moto_engine import MotoGame
        game = MotoGame(); game.start_level(0)
        game.elapsed = 30.0
        game.player["x"] = game.level["finish"]
        game.step(1/60, {})
        self.assertEqual(game.state, "complete")
        self.assertGreater(game.best_times[0], 0)
        self.assertEqual(game.unlocked_level, 1)

    def test_settings_persist_to_store_and_reset(self):
        from storage import SaveStore
        from moto_engine import MotoGame
        store = SaveStore(); game = MotoGame(store)
        game.state = "settings"
        game.setting_index = 0
        game.step(1/60, {"a_just": True})
        self.assertFalse(game.sound_on)
        game.setting_index = 2
        game.step(1/60, {"left_nav": True})
        self.assertEqual(game.assist_mode, 0)
        game.step(1/60, {"b_just": True})
        self.assertEqual(store.get("assist_mode"), 0)

    def test_renderer_300_frames_across_menu_and_riding(self):
        from moto_engine import MotoGame
        from renderer import Renderer
        game = MotoGame(); renderer = Renderer()
        for i in range(300):
            inp = {"up": i < 220, "right": 40 < i < 120,
                   "left": 180 < i < 220}
            if i == 0:
                inp["a_just"] = True
                game.step(1/60, inp)
            else:
                game.step(1/60, inp)
            renderer.render(game)
        self.assertGreater(self.emu.fb.draw_calls, 300)


if __name__ == "__main__":
    unittest.main()
