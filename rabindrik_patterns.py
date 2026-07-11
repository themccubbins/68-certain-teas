"""68 Certain Teas v2 -- Rabindrik taals: meters Rabindranath Tagore created
(or repurposed) for Rabindra Sangeet, transcribed from Geetabitan.com.

Defining feature: NO KHALI anywhere. Tagore's taals mark structure with
claps only -- every `khali` list here is empty, which on the module means
channel 3 stays silent for this whole group (authentic, not a bug).

Entry format: see kksongs_patterns.py. All taals here are whole-beat
(steps_per_beat = 1). `tali` includes the sam (step 1).

Source: Geetabitan.com taal index, https://www.geetabitan.com/taal/index.html
        (individual taal pages, fetched July 2026)
Built by: Claude (Fable) & cubbs, 2026.
"""

SYSTEM = "rabindrik"


def _e(tal, beats, bols_str, tali, vibhag_div, note=None):
    bols = []
    for group in bols_str.split("|"):
        bols.extend(group.split())
    assert len(bols) == beats, (tal, len(bols), beats)
    # vibhag starts from the division sizes
    starts, pos = [], 1
    for d in vibhag_div:
        starts.append(pos)
        pos += d
    assert pos - 1 == beats, (tal, vibhag_div, beats)
    return {
        "system": SYSTEM,
        "tal": tal,
        "variant": tal,
        "beats": beats,
        "steps_per_beat": 1,
        "steps": beats,
        "bols": bols,
        "tali": list(tali),
        "khali": [],
        "vibhag": starts,
        "note": note,
    }


RABINDRIK_TALS = [
    _e("Ardha Jhaptaal", 5, "dhi na | dhi dhi na",
       tali=[1, 3], vibhag_div=[2, 3],
       note="first half of Jhaptaal; cousin of Carnatic Khanda Chapu"),

    _e("Jhampak", 5, "dhi dhi na | dhi na",
       tali=[1, 4], vibhag_div=[3, 2],
       note="Tagore's 3+2 answer to Jhaptaal"),

    _e("Sasthi", 6, "dhi na | dha dhi dhi na",
       tali=[1, 3], vibhag_div=[2, 4],
       note="6 beats as 2+4 (vs Dadra's 3+3)"),

    _e("Sasthi (4|2)", 6, "dha dhi na dhi | dha dhi",
       tali=[1, 5], vibhag_div=[4, 2]),

    _e("Teyora", 7, "dha dhi na | dhi na | dhi na",
       tali=[1, 4, 6], vibhag_div=[3, 2, 2],
       note="traditional 7-beat meter as used in Rabindra Sangeet"),

    _e("Rupakra", 8, "dha dhi na | dhi na | dhi dhi na",
       tali=[1, 4, 6], vibhag_div=[3, 2, 3],
       note="Tagore's asymmetric 3+2+3 eight"),

    _e("Nabataal (3|2|2|2)", 9, "dha den ta | tete kata | gadi ghene | dhage tete",
       tali=[1, 4, 6, 8], vibhag_div=[3, 2, 2, 2]),

    _e("Nabataal (3|6)", 9, "dha dhi na | dha dhi dhi na dhi na",
       tali=[1, 4], vibhag_div=[3, 6]),

    _e("Nabataal (5|4)", 9, "dha dhi na dhi na | dha dhi dhi na",
       tali=[1, 6], vibhag_div=[5, 4]),

    _e("Nabataal (3|3|3)", 9, "dhin dhin na | nag thun na | tete dhin tete",
       tali=[1, 4, 7], vibhag_div=[3, 3, 3]),

    _e("Nabataal (9)", 9, "dhi dhi na dha dhi na dha dhi na",
       tali=[1], vibhag_div=[9],
       note="nine beats in a single undivided sweep"),

    _e("Ekadoshi (3|2|2|4)", 11, "dha den ta | tete kata | gadi ghene | dhage tete tage tete",
       tali=[1, 4, 6, 8], vibhag_div=[3, 2, 2, 4]),

    _e("Ekadoshi (3|4|4)", 11, "dha dhi na | dha dhi dhi na | dha dhi tere kete",
       tali=[1, 4, 8], vibhag_div=[3, 4, 4]),

    _e("Nabapancha", 18, "dha dha | dhage tete den ta | tage tete den ta | tete kata gadi ghene | dhage tete tage tete",
       tali=[1, 3, 7, 11, 15], vibhag_div=[2, 4, 4, 4, 4],
       note="Tagore's 18-beat cycle, 2+4+4+4+4"),
]


if __name__ == "__main__":
    for t in RABINDRIK_TALS:
        assert len(t["bols"]) == t["steps"]
        assert all(1 <= i <= t["steps"] for i in t["tali"] + t["vibhag"])
        assert t["khali"] == []
    print(f"{len(RABINDRIK_TALS)} taals, all khali-less, no problems")
