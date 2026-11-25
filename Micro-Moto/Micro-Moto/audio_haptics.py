# Lightweight optional audio and rumble wrapper.
try:
    import engine_io
    import engine_audio
    from engine_resources import WaveSoundResource
except ImportError:
    engine_io = None
    engine_audio = None
    WaveSoundResource = None


class AudioHaptics:
    def __init__(self, sound=True, rumble=True):
        self.sound = sound
        self.rumble = rumble

    def rumble_pulse(self, duration=70):
        if self.rumble and engine_io:
            engine_io.rumble(0.7)

    def play(self, name):
        if not self.sound or engine_audio is None:
            return
        try:
            engine_audio.play(name, 0, False)
        except Exception:
            pass

    def cleanup(self):
        if engine_io:
            engine_io.rumble(0.0)
