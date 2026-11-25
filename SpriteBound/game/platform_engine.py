# SpriteBound core platformer simulation (headless-testable).

W = 128
H = 128

LEVELS = (
    ("SUNSET STEPS", (250, 86, 45), 470),
    ("GLASS GARDEN", (50, 170, 230), 540),
    ("STAR SUMMIT", (120, 75, 210), 610),
)


def make_platforms(index):
    if index == 0:
        rows = [(8,96,28),(8,72,32),(58,48,34),(16,25,30),(78,8,30),(38,-18,36),(100,-43,20),(52,-68,32),(8,-94,34),(72,-118,26),(36,-145,36),(94,-170,24),(48,-198,34),(5,-224,28),(62,-250,32)]
        kinds = ["normal","normal","normal","spring","normal","normal","vanish","normal","normal","spring","normal","vanish","normal","normal","goal"]
    elif index == 1:
        rows = [(24,96,32),(82,68,28),(40,42,26),(4,16,34),(70,-10,32),(24,-38,24),(92,-66,28),(52,-94,30),(8,-122,24),(66,-150,36),(24,-180,30),(88,-208,28),(42,-238,34),(4,-268,25),(58,-300,38)]
        kinds = ["normal","spring","normal","vanish","normal","normal","spring","normal","vanish","normal","normal","vanish","spring","normal","goal"]
    else:
        rows = [(48,96,34),(8,68,28),(76,40,28),(38,12,30),(96,-16,24),(52,-44,34),(10,-74,24),(68,-104,30),(28,-134,34),(88,-164,24),(44,-194,30),(4,-224,28),(64,-254,34),(24,-284,28),(82,-314,32),(44,-344,36)]
        kinds = ["normal","normal","spring","vanish","normal","normal","spring","vanish","normal","normal","spring","normal","vanish","normal","spring","goal"]
    return [{"x":x,"y":y,"w":w,"h":5,"kind":k,"vanish":0.0,"gone":False,"used":False} for (x,y,w),k in zip(rows,kinds)]


class SpriteBoundGame:
    def __init__(self):
        self.state = "title"
        self.level = 0
        self.elapsed = 0.0
        self.falls = 0
        self.best_level = 0
        self.shake = 0.0
        self.reset_level()

    def reset_level(self):
        self.player = {"x":52.0,"y":82.0,"vx":0.0,"vy":0.0,"w":10,"h":12,"ground":False}
        self.platforms = make_platforms(self.level)
        self.camera = 0.0
        self.elapsed = 0.0
        self.complete_timer = 0.0
        self.message = ""

    def start(self):
        self.level = 0
        self.falls = 0
        self.state = "playing"
        self.reset_level()

    def next_level(self):
        if self.level < 2:
            self.level += 1
            self.best_level = max(self.best_level, self.level)
            self.state = "playing"
            self.reset_level()
        else:
            self.state = "victory"

    def step(self, dt, inp):
        dt = min(dt, 0.033)
        self.elapsed += dt

        if self.state == "title":
            if inp.get("a_just"):
                self.start()
            return
        if self.state == "victory":
            if inp.get("a_just") or inp.get("b_just"):
                self.state = "title"
            return
        if self.state == "paused":
            if inp.get("menu_just") or inp.get("b_just"):
                self.state = "playing"
            elif inp.get("a_just"):
                self.reset_level(); self.state = "playing"
            return
        if self.state == "gameover":
            if inp.get("a_just"):
                self.start()
            elif inp.get("b_just"):
                self.state = "title"
            return
        if inp.get("menu_just"):
            self.state = "paused"; return

        p = self.player
        p["ground"] = False
        move = 0
        if inp.get("left"):
            move -= 1
        if inp.get("right"):
            move += 1
        if move:
            p["vx"] += move * 170.0 * dt
        else:
            p["vx"] *= 0.78
        p["vx"] = max(-85.0, min(85.0, p["vx"]))

        if inp.get("a_just") and p["vy"] >= -20.0:
            # Coyote/jump feel: A always jumps if recently or currently on a support.
            p["vy"] = -112.0

        p["vy"] += 255.0 * dt
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt

        if p["x"] < 2:
            p["x"] = 2; p["vx"] = 0
        if p["x"] + p["w"] > 126:
            p["x"] = 126-p["w"]; p["vx"] = 0

        # Landing only while moving downward.
        if p["vy"] >= 0:
            old_bottom = p["y"] + p["h"] - p["vy"] * dt
            new_bottom = p["y"] + p["h"]
            for plat in self.platforms:
                if plat["gone"]:
                    continue
                if old_bottom <= plat["y"] + 2 and new_bottom >= plat["y"]:
                    if p["x"] + p["w"] > plat["x"] and p["x"] < plat["x"] + plat["w"]:
                        p["y"] = plat["y"] - p["h"]
                        if plat["kind"] == "spring":
                            p["vy"] = -155.0
                            plat["used"] = True
                            self.message = "BOING!"
                        else:
                            p["vy"] = 0.0
                        p["ground"] = True
                        if plat["kind"] == "vanish":
                            plat["vanish"] += dt
                            if plat["vanish"] > 0.55:
                                plat["gone"] = True
                        break

        for plat in self.platforms:
            if plat["kind"] == "goal" and not plat["gone"]:
                if p["x"] + p["w"] > plat["x"] and p["x"] < plat["x"] + plat["w"]:
                    if p["y"] + p["h"] >= plat["y"] and p["y"] < plat["y"] + 10:
                        self.complete_timer += dt
                        if self.complete_timer > 0.35:
                            self.next_level()
                        return

        # Camera follows upward motion; positive world-to-screen offset lowers y.
        target = p["y"] - 62.0
        if target < self.camera:
            self.camera += (target - self.camera) * min(1.0, dt * 5.0)

        if p["y"] - self.camera > 150:
            self.falls += 1
            self.shake = 0.18
            self.reset_level()

        if self.shake > 0:
            self.shake -= dt
