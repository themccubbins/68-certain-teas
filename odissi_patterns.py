"""68 Certain Teas v2 -- Odissi talas, the rhythm system of Odisha's mardala.

Two kinds of entry:
  - with ukuta (mardala bols): Rupaka, Khemta, Tripata -- transcribed from
    Odissi Darpana. Note "phank" is the Odissi equivalent of khali.
  - structure-only: matra/bibhaga/chhanda from the Mardala article; no
    per-beat ukuta source was available, so these carry claps on bibhaga
    starts only. Sparse on purpose -- they play the chhanda skeleton
    (e.g. Jhampa = pulses in 2+3+2+3), which is itself the tala's
    signature swing.

Entry format: see kksongs_patterns.py.

Sources: Odissi Darpana (nrutyayanaodissi.wordpress.com) taala posts;
         Wikipedia "Mardala" (tala table: matra/bibhaga/chhanda).
Built by: Claude (Fable) & cubbs, 2026.
"""

SYSTEM = "odissi"


def _starts(groups):
    starts, pos = [], 1
    for g in groups:
        starts.append(pos)
        pos += g
    return starts


def _with_bols(tal, bols, tali, khali, groups, note=None):
    return {
        "system": SYSTEM, "tal": tal, "variant": tal + " (Odissi)",
        "beats": len(bols), "steps_per_beat": 1, "steps": len(bols),
        "bols": list(bols), "tali": list(tali), "khali": list(khali),
        "vibhag": _starts(groups), "note": note,
    }


def _skeleton(tal, beats, groups, note=None):
    starts = _starts(groups)
    return {
        "system": SYSTEM, "tal": tal, "variant": tal + " (Odissi)",
        "beats": beats, "steps_per_beat": 1, "steps": beats,
        "bols": ["-"] * beats, "tali": starts, "khali": [],
        "vibhag": starts,
        "note": (note + "; " if note else "") + "structure-only: chhanda skeleton, no ukuta source",
    }


ODISSI_TALS = [
    _with_bols("Rupaka", ["dha", "kadataka", "dha", "kadataka", "tin", "dha"],
               tali=[1, 3], khali=[], groups=[2, 4],
               note="ukuta: (DhaS)(Kadataka) | (DhaS)(Kadataka)(Tin)(Dha)"),
    _with_bols("Khemta", ["dha", "dhi", "na", "dha", "ti", "na"],
               tali=[1], khali=[4], groups=[3, 3],
               note="aka Jhula; phank (khali) on 4"),
    _with_bols("Tripata", ["dhei", "tathin", "dak", "tathin", "dak", "tathin", "dak"],
               tali=[1, 4, 6], khali=[], groups=[3, 2, 2]),
    _skeleton("Ekatali", 4, [4], "the everyday Odissi cycle"),
    _skeleton("Jhampa", 10, [2, 3, 2, 3]),
    _skeleton("Nihsari", 10, [3, 2, 3, 2]),
    _skeleton("Adatali", 14, [4, 3, 4, 3]),
    _skeleton("Jati", 14, [3, 4, 3, 4], "Adatali's mirror"),
    _skeleton("Sarimana", 14, [4, 2, 4, 4]),
]


if __name__ == "__main__":
    for t in ODISSI_TALS:
        assert len(t["bols"]) == t["steps"], t["tal"]
        assert all(1 <= i <= t["steps"] for i in t["tali"] + t["khali"] + t["vibhag"]), t["tal"]
    print(f"{len(ODISSI_TALS)} talas ({sum(1 for t in ODISSI_TALS if any(b != '-' for b in t['bols']))} with ukuta), no problems")
