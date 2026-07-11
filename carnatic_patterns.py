"""68 Certain Teas v2 -- Carnatic talas: the suladi sapta tala system (35 talas),
the 4 chapu talas, and a curated set of anga talas (melakarta talas +
Simhanandana, the 128-beat giant).

Carnatic talas have NO drum strokes in their definition -- they are pure
gesture structures. Every akshara (beat) carries one of four gestures:

    clap    sasabda (sounded)   -- anga start, or drutam beat 1
    count   finger count        -- laghu beats 2..n, virama extensions
    wave    nihshabda (waved)   -- drutam beat 2; pluta krishya/sarpini
    motion  circular/up motion  -- guru beats 2..8; kakapadam patakam

On the module: clap -> tali channel, wave -> khali channel,
count -> flourish channel, motion -> open/resonant channel. Sam and
anga boundaries come from step 1 / the vibhag list as usual.

ANGAS (with default chatusra laghu = 4):
    U  anudrutam  1 beat   [clap]
    O  drutam     2 beats  [clap, wave]
    V  druta-virama 3 beats [clap, wave, count]
    L  laghu      n beats  [clap, count*(n-1)]  n = jati (3/4/5/7/9)
    G  guru       8 beats  [clap, motion*7]
    P  plutam     12 beats [clap, count*3, wave*8]
    K  kakapadam  16 beats [clap, count*3, motion*4, wave*8]

Entry format: see kksongs_patterns.py, plus `counts` and `motions`
(step-index lists) for the gesture channels. `bols` is all "-" here.

Sources: Wikipedia "Tala (music)" (suladi system, anga definitions,
         72 melakarta tala table, Simhanandana structure);
         shadjam.wordpress.com "Classification of Talas";
         chapu clap conventions vary by school (noted per-entry).
Built by: Claude (Fable) & cubbs, 2026.
"""

SYSTEM = "carnatic"

JATI = {"tisra": 3, "chatusra": 4, "khanda": 5, "misra": 7, "sankirna": 9}

# The seven tala families as anga strings.
SAPTA = [
    ("Dhruva", "LOLL"),
    ("Matya", "LOL"),
    ("Rupaka", "OL"),
    ("Jhampa", "LUO"),
    ("Triputa", "LOO"),
    ("Ata", "LLOO"),
    ("Eka", "L"),
]


def _expand_anga(anga, laghu_len):
    """-> list of per-beat gesture tags for one anga."""
    if anga == "U":
        return ["clap"]
    if anga == "O":
        return ["clap", "wave"]
    if anga == "V":
        return ["clap", "wave", "count"]
    if anga == "L":
        return ["clap"] + ["count"] * (laghu_len - 1)
    if anga == "G":
        return ["clap"] + ["motion"] * 7
    if anga == "P":
        return ["clap"] + ["count"] * 3 + ["wave"] * 8
    if anga == "K":
        return ["clap"] + ["count"] * 3 + ["motion"] * 4 + ["wave"] * 8
    raise ValueError(anga)


def _entry(tal, variant, angas, laghu_len, note=None):
    gestures, vibhag = [], []
    for a in angas:
        vibhag.append(len(gestures) + 1)
        gestures.extend(_expand_anga(a, laghu_len))
    steps = len(gestures)
    return {
        "system": SYSTEM,
        "tal": tal,
        "variant": variant,
        "beats": steps,
        "steps_per_beat": 1,
        "steps": steps,
        "bols": ["-"] * steps,
        "tali": [i + 1 for i, g in enumerate(gestures) if g == "clap"],
        "khali": [i + 1 for i, g in enumerate(gestures) if g == "wave"],
        "counts": [i + 1 for i, g in enumerate(gestures) if g == "count"],
        "motions": [i + 1 for i, g in enumerate(gestures) if g == "motion"],
        "vibhag": vibhag,
        "note": note,
    }


def _suladi():
    out = []
    for family, angas in SAPTA:
        for jati_name, n in JATI.items():
            name = f"{jati_name.capitalize()}-jati {family}"
            out.append(_entry(family, name, angas, n))
    return out


# ---- chapu talas (clap positions; conventions vary by school) ----

def _chapu(name, beats, claps, groups, note):
    starts, pos = [], 1
    for g in groups:
        starts.append(pos)
        pos += g
    return {
        "system": SYSTEM,
        "tal": name,
        "variant": name,
        "beats": beats,
        "steps_per_beat": 1,
        "steps": beats,
        "bols": ["-"] * beats,
        "tali": list(claps),
        "khali": [],
        "counts": [],
        "motions": [],
        "vibhag": starts,
        "note": note,
    }


CHAPU = [
    _chapu("Tisra Chapu", 3, [1, 2], [1, 2],
           "1+2; clap conventions vary"),
    _chapu("Khanda Chapu", 5, [1, 3], [2, 3],
           "2+3; the 10-count feel at double speed; clap conventions vary"),
    _chapu("Misra Chapu", 7, [1, 4, 6], [3, 2, 2],
           "3+2+2; many padams are set to this"),
    _chapu("Sankirna Chapu", 9, [1, 5, 7], [4, 5],
           "4+5; rare; clap conventions vary"),
]


# ---- curated anga talas: melakarta talas + Simhanandana ----
# Anga strings use: U O V(=druta-virama) L G P K. Chatusra laghu.

MELAKARTA_PICKS = [
    ("Paavani", "VLUU", 9, None),
    ("Natakapriya", "OOOLO", 12, None),
    ("Soolini", "LVLU", 12, None),
    ("Yagapriya", "VLLO", 13, None),
    ("Raghupriya", "VLULO", 14, None),
    ("Kanakaangi", "UOGL", 15, "first melakarta; has a guru"),
    ("Chala Naata", "LVLOO", 15, None),
    ("Dhenuka", "PUUO", 16, "opens with a 12-beat plutam"),
    ("Bhavapriya", "LULULO", 16, None),
    ("Rathnaangi", "GULVL", 20, None),
    ("Charukesi", "GVLULO", 22, None),
    ("Hanumathodi", "GUULOPOL", 34, "guru and plutam in one cycle"),
    ("Jankaradhwani", "PVVVPOU", 36, "two plutams: wave-heavy"),
    ("Suryakantham", "GVOGP", 33, "two gurus and a plutam"),
]

ANGA_TALAS = [
    _entry(name, f"{name} (melakarta tala)", angas, 4, note)
    for name, angas, expected, note in MELAKARTA_PICKS
] + [
    _entry("Simhanandana", "Simhanandana (128 beats)",
           "GGLPLGOOGGLPLPGLLK", 4,
           "the longest tala in the 108-tala scheme: 6 gurus, 6 laghus, "
           "3 plutams, 2 drutams, 1 kakapadam = 128 aksharas"),
]

# expected-length check data for the self-test
_EXPECTED = {name: exp for name, _, exp, _ in MELAKARTA_PICKS}
_EXPECTED["Simhanandana"] = 128

CARNATIC_TALS = _suladi() + CHAPU + ANGA_TALAS


if __name__ == "__main__":
    problems = 0
    for t in CARNATIC_TALS:
        exp = _EXPECTED.get(t["tal"])
        if exp is not None and t["steps"] != exp:
            problems += 1
            print(f"[LEN] {t['variant']}: {t['steps']} != expected {exp}")
    # spot-check famous suladi lengths
    known = {"Chatusra-jati Triputa": 8,   # Adi tala
             "Chatusra-jati Dhruva": 14,
             "Misra-jati Jhampa": 10,
             "Khanda-jati Ata": 14,
             "Tisra-jati Eka": 3,
             "Sankirna-jati Dhruva": 29}
    for name, exp in known.items():
        got = [t for t in CARNATIC_TALS if t["variant"] == name]
        if not got or got[0]["steps"] != exp:
            problems += 1
            print(f"[SULADI] {name}: got {got[0]['steps'] if got else '??'}, expected {exp}")
    print(f"{len(CARNATIC_TALS)} talas "
          f"({sum(1 for t in CARNATIC_TALS if 'jati' in t['variant'])} suladi, "
          f"{len(CHAPU)} chapu, {len(ANGA_TALAS)} anga), "
          f"{'no problems' if not problems else str(problems) + ' problems'}")
