# Thumby Color persistent settings and best times.
try:
    import engine_save
except ImportError:
    engine_save = None


DEFAULT_BEST = 0
DEFAULTS = {
    "sound_on": 1,
    "rumble_on": 1,
    "assist_mode": 1,
    "theme_idx": 0,
    "show_times": 1,
    "unlocked_level": 0,
}
for i in range(50):
    DEFAULTS["best_%02d" % i] = DEFAULT_BEST


class SaveStore:
    def __init__(self):
        self.data = dict(DEFAULTS)
        self.enabled = False
        self._init()

    def _init(self):
        if engine_save is None:
            return
        try:
            if engine_save.saves_dir() is None:
                return
            engine_save.set_location("micro_moto.save")
            self.enabled = True
            for key, default in DEFAULTS.items():
                value = engine_save.load(key, default)
                if isinstance(value, int):
                    self.data[key] = value
        except Exception:
            self.enabled = False

    def get(self, key):
        return self.data.get(key, DEFAULTS.get(key, 0))

    def set(self, key, value, persist=True):
        self.data[key] = value
        if persist and self.enabled and engine_save is not None:
            try:
                engine_save.save(key, int(value))
            except Exception:
                pass

    def save_all(self):
        if not self.enabled or engine_save is None:
            return
        try:
            for key, value in self.data.items():
                engine_save.save(key, int(value))
        except Exception:
            pass
