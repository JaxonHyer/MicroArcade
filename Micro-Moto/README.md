# Micro Moto

A **Thumby Color**-only, 128×128 RGB565 arcade motorcycle game inspired by side-scrolling stunt racers.

## Features

- Five complete hand-authored starter levels
- 50-level goal: first five levels are handcrafted, with 45 deterministic procedural levels in the catalog
- Hazard types: spikes, oil patches, crates
- Visible checkpoint flags and checkpoint respawning
- Press **A** to restart after a crash; the race timer continues
- Title, level select, settings, pause, crash, and finish states
- Persistent unlocked levels and best times
- Minimal two-wheel physics, jumps, ramps, and intentional lean/crash behavior

## Controls

- **D-Pad Up / A**: Accelerate
- **D-Pad Down / B**: Brake/decelerate
- **D-Pad Left / LB**: Lean backward
- **D-Pad Right / RB**: Lean forward
- **MENU**: Pause/resume
- **A**: Confirm or restart after a crash
- **B**: Back

## 50-Level Roadmap

- Levels 1–5: hand-authored and playable in this release.
- Levels 6–50: deterministic seeded procedural catalog, introduced in bounded difficulty tiers.
- Future work may replace generated stages with fully hand-authored levels while preserving the 50-level catalog API.

## Install

Copy `Micro-Moto/game/` to `/Games/Micro-Moto/` on the Thumby Color. The folder must contain:

- `main.py`
- `manifest.ini`
- `icon.bmp`
- `moto_engine.py`
- `level_catalog.py`
- `renderer.py`
- `storage.py`
- `audio_haptics.py` when audio assets are present

## Test

```bash
python3 -m unittest discover -s Micro-Moto/tests -v
python3 -m compileall -q Micro-Moto/game tools
```

## Generation

```bash
python3 tools/generate_thumby_icon.py Micro-Moto/game/icon.bmp
```
