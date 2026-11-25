# Hardware-independent Micro Moto physics and race state.
import math
from level_catalog import get_level, LEVEL_COUNT

W = 128
H = 128


class MotoGame:
    def __init__(self, storage=None):
        self.storage = storage
        self.state = "title"
        self.level_index = 0
        self.title_option = 0
        self.level_page = 0
        self.setting_index = 0
        self.assist_mode = 1
        self.theme_idx = 0
        self.sound_on = True
        self.rumble_on = True
        self.show_times = True
        self.elapsed = 0.0
        self.best_times = [0] * LEVEL_COUNT
        self.unlocked_level = 0
        if storage:
            self.assist_mode = storage.get("assist_mode")
            self.theme_idx = storage.get("theme_idx")
            self.sound_on = bool(storage.get("sound_on"))
            self.rumble_on = bool(storage.get("rumble_on"))
            self.show_times = bool(storage.get("show_times"))
            self.unlocked_level = storage.get("unlocked_level")
            self.best_times = [storage.get("best_%02d" % i) for i in range(LEVEL_COUNT)]
        self.level = None
        self.reset_level()

    def reset_level(self):
        self.level = get_level(self.level_index)
        sx, _ = self.level["spawn"]
        self.player = {
            "x": float(sx), "y": 82.0, "vx": 0.0, "vy": 0.0,
            "angle": 0.0, "av": 0.0, "ground": False,
            "wheel_spin": 0.0, "lean": 0.0,
        }
        self.camera = 0.0
        self.checkpoint = 0
        self.checkpoint_x = float(sx)
        self.checkpoint_y = 82.0
        self.elapsed = 0.0
        self.finish_time = 0.0
        self.shake = 0.0
        self.crash = False

    def restart_checkpoint(self):
        p = self.player
        p["x"] = self.checkpoint_x
        p["y"] = self.checkpoint_y
        p["vx"] = 0.0
        p["vy"] = 0.0
        p["angle"] = 0.0
        p["av"] = 0.0
        p["ground"] = False
        p["lean"] = 0.0
        self.crash = False
        self.state = "playing"

    def start_level(self, index):
        index = max(0, min(LEVEL_COUNT - 1, int(index)))
        self.level_index = index
        self.reset_level()
        self.state = "playing"

    def terrain_height(self, x):
        terrain = self.level["terrain"]
        spacing = self.level["spacing"]
        if x <= 0:
            return terrain[0]
        pos = x / spacing
        i = int(pos)
        if i >= len(terrain)-1:
            return terrain[-1]
        frac = pos-i
        return terrain[i]*(1-frac)+terrain[i+1]*frac

    def hazard_contact(self, p):
        px = p["x"]
        py = p["y"]
        for hazard in self.level["hazards"]:
            hx = hazard["x"]
            hw = hazard["w"]
            ground = self.terrain_height(hx+hw*0.5)
            if px+9 >= hx and px-9 <= hx+hw:
                if py+12 >= ground-8 and py < ground:
                    if hazard["kind"] in ("spikes", "crate"):
                        return True
                    if hazard["kind"] == "oil":
                        p["vx"] *= 0.96
        return False

    def step(self, dt, inp):
        dt = min(0.033, max(0.0, dt))

        if self.state == "title":
            if inp.get("up_nav"):
                self.title_option = (self.title_option-1)%3
            elif inp.get("down_nav"):
                self.title_option = (self.title_option+1)%3
            if inp.get("a_just"):
                if self.title_option == 0:
                    self.start_level(self.level_index)
                elif self.title_option == 1:
                    self.state = "level_select"
                else:
                    self.setting_index = 0
                    self.state = "settings"
            return

        if self.state == "level_select":
            if inp.get("left_nav"):
                self.level_index = max(0, self.level_index-1)
            elif inp.get("right_nav"):
                self.level_index = min(self.unlocked_level, self.level_index+1)
            elif inp.get("up_nav"):
                self.level_index = max(0, self.level_index-5)
            elif inp.get("down_nav"):
                self.level_index = min(self.unlocked_level, self.level_index+5)
            if inp.get("a_just"):
                self.start_level(self.level_index)
            elif inp.get("b_just"):
                self.state = "title"
            return

        if self.state == "settings":
            if inp.get("up_nav"):
                self.setting_index = (self.setting_index-1)%5
            elif inp.get("down_nav"):
                self.setting_index = (self.setting_index+1)%5
            delta = 1 if inp.get("right_nav") or inp.get("a_just") else -1 if inp.get("left_nav") else 0
            if delta:
                if self.setting_index == 0:
                    self.sound_on = not self.sound_on
                elif self.setting_index == 1:
                    self.rumble_on = not self.rumble_on
                elif self.setting_index == 2:
                    self.assist_mode = (self.assist_mode+delta)%3
                elif self.setting_index == 3:
                    self.theme_idx = (self.theme_idx+delta)%3
                elif self.setting_index == 4:
                    self.show_times = not self.show_times
            if inp.get("b_just"):
                self.save_settings()
                self.state = "title"
            return

        if self.state == "paused":
            if inp.get("menu_just") or inp.get("b_just"):
                self.state = "playing"
            elif inp.get("a_just"):
                self.reset_level()
                self.state = "playing"
            return

        if self.state == "crashed":
            if inp.get("a_just"):
                self.restart_checkpoint()
            elif inp.get("b_just"):
                self.reset_level()
                self.state = "playing"
            return

        if self.state == "complete":
            if inp.get("a_just"):
                self.level_index = min(LEVEL_COUNT-1, self.level_index+1)
                self.start_level(self.level_index)
            elif inp.get("b_just"):
                self.state = "title"
            return

        if inp.get("menu_just"):
            self.state = "paused"
            return

        self.elapsed += dt
        p = self.player
        ground = self.terrain_height(p["x"])

        # Throttle/brake and lean controls.
        accelerate = inp.get("up") or inp.get("a")
        brake = inp.get("down") or inp.get("b")
        lean_backward = inp.get("left") or inp.get("lb")
        lean_forward = inp.get("right") or inp.get("rb")

        if ground-p["y"] > 18:
            p["ground"] = False
        else:
            p["ground"] = True

        if accelerate:
            p["vx"] += (62.0 if p["ground"] else 20.0)*dt
        if brake:
            p["vx"] -= 72.0*dt
        p["vx"] *= 0.997 if p["ground"] else 0.999

        # Mild automatic balance assist; Normal and Easy reduce crash sensitivity.
        target_av = 0.0
        if lean_backward:
            target_av -= 2.5
        if lean_forward:
            target_av += 2.5
        if self.assist_mode == 2:
            target_av *= 0.55
        elif self.assist_mode == 0:
            target_av *= 1.35
        p["av"] += (target_av-p["av"])*min(1.0, dt*8.0)

        p["vy"] += 210.0*dt
        p["angle"] += p["av"]*dt
        p["x"] += p["vx"]*dt
        p["y"] += p["vy"]*dt

        if p["x"] < 8:
            p["x"] = 8
            p["vx"] = 0.0

        ground = self.terrain_height(p["x"])
        surface_y = ground-11
        if p["y"]+12 >= surface_y and p["vy"] >= -155:
            left_h = self.terrain_height(p["x"]-7)
            right_h = self.terrain_height(p["x"]+7)
            slope = math.atan2(left_h-right_h, 14.0)
            p["y"] = surface_y-12
            p["vy"] = 0.0
            p["ground"] = True
            p["angle"] += (slope-p["angle"])*min(1.0, dt*10.0)

        # Crashes for spikes/crates, extreme angle, deep falls, or high reverse speed.
        if abs(p["angle"] % (2*math.pi)) > 2.20:
            self.crash = True
        if p["y"] > H+35 or p["y"] < -75:
            self.crash = True
        if self.hazard_contact(p):
            self.crash = True
        if abs(p["vx"]-0) > 155:
            self.crash = True

        if self.crash:
            self.state = "crashed"
            self.shake = 0.18
            p["vx"] = 0.0
            p["vy"] = 0.0
            return

        # Checkpoints are ordered and crossed left-to-right.
        if self.checkpoint < len(self.level["checkpoints"]):
            cp = self.level["checkpoints"][self.checkpoint]
            if p["x"] >= cp:
                self.checkpoint += 1
                self.checkpoint_x = float(cp-18)
                self.checkpoint_y = float(self.terrain_height(cp-18)-23)

        if p["x"] >= self.level["finish"]:
            self.finish_time = self.elapsed
            self._record_finish()
            self.state = "complete"

        if self.shake > 0:
            self.shake -= dt

    def _record_finish(self):
        key = "best_%02d" % self.level_index
        old = self.best_times[self.level_index]
        milliseconds = int(self.elapsed*1000)
        if old == 0 or milliseconds < old:
            self.best_times[self.level_index] = milliseconds
            if self.storage:
                self.storage.set(key, milliseconds)
        next_level = min(LEVEL_COUNT-1, self.level_index+1)
        if next_level > self.unlocked_level:
            self.unlocked_level = next_level
            if self.storage:
                self.storage.set("unlocked_level", next_level)

    def save_settings(self):
        if not self.storage:
            return
        self.storage.set("sound_on", int(self.sound_on))
        self.storage.set("rumble_on", int(self.rumble_on))
        self.storage.set("assist_mode", self.assist_mode)
        self.storage.set("theme_idx", self.theme_idx)
        self.storage.set("show_times", int(self.show_times))
