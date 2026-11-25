# Micro Moto level catalog: 5 hand-authored levels + 45 deterministic stages.

SPACING = 8
LEVEL_COUNT = 50


def _terrain(seed, length, band):
    # Deterministic linear-congruential generator. No random/time state.
    state = (0x4D4F5440 ^ ((seed * 0x9E3779) & 0xFFFFFFFF)) & 0xFFFFFFFF
    out = []
    y = 96
    count = (length + SPACING - 1) // SPACING
    step_limit = (8 + band * 2)
    for i in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        change = (state % (step_limit * 2 + 1)) - step_limit
        if i < 8:
            change = 0
        y += change
        y = max(58, min(108, y))
        out.append(y)
    return out


def _generated(seed, band):
    length = 1120 + band * 45 + (seed % 4) * 80
    terrain = _terrain(seed, length, band)
    checkpoints = [length // 3, 2 * length // 3]
    hazards = []
    for i in range(3 + band // 2):
        x = 180 + i * max(110, (length - 280) // (4 + band // 2))
        if x > length - 150:
            break
        kind = ("spikes" if i % 3 == 0 else "oil" if i % 3 == 1 else "crate")
        hazards.append({"kind": kind, "x": x, "w": 14 if kind != "oil" else 22})
    return {
        "name": "SECTOR " + str(seed - 4).zfill(2),
        "length": length,
        "spacing": SPACING,
        "terrain": terrain,
        "checkpoints": checkpoints,
        "hazards": hazards,
        "finish": length - 40,
        "spawn": (24, 70),
        "band": band,
    }


def _hand_level(name, terrain, checkpoints, hazards, finish=1120):
    # Normalize a compact hand-authored heightfield to 8px spacing.
    return {
        "name": name,
        "length": finish,
        "spacing": SPACING,
        "terrain": list(terrain),
        "checkpoints": checkpoints,
        "hazards": hazards,
        "finish": finish,
        "spawn": (24, 70),
        "band": 0,
    }


def build_hand_levels():
    flat = tuple(96 for _ in range(141))
    level1 = list(flat)

    level2 = list(flat)
    for i in range(22, 45): level2[i] = 96 - (i - 22) * 2
    for i in range(45, 58): level2[i] = 50
    for i in range(58, 76): level2[i] = 50 + (i - 58) * 3

    level3 = list(flat)
    for i in range(18, 32): level3[i] = 96 - (i - 18) * 2
    for i in range(32, 48): level3[i] = 68 + ((i - 32) % 4) * 3
    for i in range(48, 64): level3[i] = 82 + (i - 48) * 1

    level4 = list(flat)
    for i in range(20, 38): level4[i] = 96 - ((i - 20) // 2) * 3
    for i in range(38, 53): level4[i] = 68 + ((i - 38) % 3) * 4
    for i in range(53, 72): level4[i] = 88 - (i - 53) * 2

    level5 = list(flat)
    for i in range(12, 125):
        level5[i] = 96 - (int((i % 11) * 3)) + ((i // 11) % 2) * 5

    return (
        _hand_level("GREEN START", level1, [360, 720], [{"kind":"spikes","x":210,"w":18},{"kind":"crate","x":520,"w":14}], 1120),
        _hand_level("SUNRUN", level2, [380, 760], [{"kind":"oil","x":260,"w":24},{"kind":"spikes","x":620,"w":20},{"kind":"crate","x":890,"w":16}], 1120),
        _hand_level("GLASS RIDGE", level3, [400, 800], [{"kind":"spikes","x":180,"w":18},{"kind":"crate","x":390,"w":14},{"kind":"oil","x":690,"w":28},{"kind":"spikes","x":920,"w":22}], 1120),
        _hand_level("CHECKPOINT CLIMB", level4, [300, 620, 920], [{"kind":"crate","x":240,"w":16},{"kind":"oil","x":480,"w":24},{"kind":"spikes","x":760,"w":20},{"kind":"crate","x":980,"w":16}], 1120),
        _hand_level("FIRE SUMMIT", level5, [260, 560, 860], [{"kind":"spikes","x":150,"w":18},{"kind":"oil","x":430,"w":28},{"kind":"crate","x":650,"w":16},{"kind":"spikes","x":850,"w":24},{"kind":"oil","x":1010,"w":22}], 1120),
    )


HAND_LEVELS = build_hand_levels()


def get_level(index):
    index = max(0, min(LEVEL_COUNT - 1, int(index)))
    if index < len(HAND_LEVELS):
        return HAND_LEVELS[index]
    catalog_id = index + 1
    band = min(5, (index - 5) // 9)
    return _generated(catalog_id, band)


def level_name(index):
    return get_level(index)["name"]
