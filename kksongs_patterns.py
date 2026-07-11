"""68 Certain Teas v2 -- rare Hindustani/Bengali tals transcribed from KKSongs Talamala.

23 tals not present in the digitabla.com set. Same terminology as
tala_patterns.py (tal / theka / bol / tali / khali / vibhag).

NORMALIZED ENTRY FORMAT (shared by all v2 data files)
    system          source-system tag
    tal, variant    names
    beats           musical beat count as stated by the source (may be
                    fractional, e.g. 11.5)
    steps_per_beat  1 for whole-beat tals; 2 for tals with fractional
                    (half) matras, which are laid out on a half-beat grid
                    so every step is equal -- clock these at 2x
    steps           total clock steps (= beats * steps_per_beat)
    bols            one token per step, "-" = no new stroke
    tali            1-based STEP indices of sam + clapped beats
    khali           1-based STEP indices of waved beats
    vibhag          1-based STEP indices of section starts
    note            transcription caveats, if any

TRANSCRIPTION NOTES
    KKSongs prints bols one syllable at a time, so grouping syllables
    onto beats sometimes required judgment (compound units like
    tirakita/gadigana kept whole, matra counts from the page treated as
    authoritative). Entries where the grouping or fractional-beat
    alignment is a judgment call carry a `note`. Fractional-matra tals
    (Ardha Jayatala 6.5, Upatala Jhampaka 8.5, Upadasi 10.5, Campaka
    Savari 11, Chartal Ki Savari 11, Dharami 11.5) use the half-beat
    grid; their tali/khali/vibhag indices are half-grid step indices.

Source: KKSongs Talamala, http://kksongs.org/tala/tala_list.html
        (individual tala pages, fetched July 2026)
Built by: Claude (Fable) & cubbs, 2026.
"""

SYSTEM = "hindustani-kksongs"


def _e(tal, beats, steps_per_beat, bols, tali, khali, vibhag, note=None):
    steps = len(bols)
    assert steps == int(beats * steps_per_beat), (tal, steps, beats)
    return {
        "system": SYSTEM,
        "tal": tal,
        "variant": tal + " (KKSongs)",
        "beats": beats,
        "steps_per_beat": steps_per_beat,
        "steps": steps,
        "bols": list(bols),
        "tali": list(tali),
        "khali": list(khali),
        "vibhag": list(vibhag),
        "note": note,
    }


KKSONGS_TALS = [
    _e("Adi (Hindustani)", 8, 1,
       ["dha", "kita", "takita", "dhatita", "ka", "titata", "tirakita", "gadigana"],
       tali=[1], khali=[5, 7], vibhag=[1, 5, 7],
       note="syllable-to-beat grouping approximate (source prints 21 syllables over 8 matras)"),

    _e("Ank", 9, 1,
       ["dha", "dhin", "na", "-", "na", "ka", "dhet", "-", "ta"],
       tali=[1, 3], khali=[7], vibhag=[1, 3, 7],
       note="rest placement approximate (7 syllables over 9 matras)"),

    _e("Ardha Jayatala", 6.5, 2,
       # half-grid: 1 1.5 2 2.5 3 3.5 4 4.5 5 5.5 6 6.5 7
       ["tin", "-", "ta", "-", "tirakita", "-", "dhin", "-", "na", "-", "dha", "ge", "na"],
       tali=[7, 11], khali=[1], vibhag=[1, 7, 11],
       note="khali falls on beat 1 (khali-sam tal, like Rupak); 6.5 beats on half-grid"),

    _e("Arjuna", 20, 1,
       ["dha", "-", "dhi", "na", "na", "ka", "dhet", "-",
        "dhi", "na", "na", "ka", "dhet", "-", "dha", "ge",
        "tira", "kita", "gadi", "gana"],
       tali=[1, 5, 7, 11, 13, 19], khali=[9, 15],
       vibhag=[1, 5, 7, 9, 11, 13, 15, 19]),

    _e("Basanta Sikhira", 26, 1,
       ["dha", "trakra", "dhe", "na", "naka", "tuge",
        "dhe", "na", "naka", "tirakita", "dha", "dhage",
        "tira", "kita", "gadi", "gana", "dhage", "tira",
        "kita", "gadi", "gana", "dhage", "tira", "kita",
        "gadi", "gana"],
       tali=[1, 5, 11, 12, 17, 22], khali=[14, 19, 24],
       vibhag=[1, 5, 11, 12, 14, 17, 19, 22, 24],
       note="syllable-to-beat grouping approximate"),

    _e("Bengali Ektal", 12, 1,
       ["ghatira", "ghati", "tata", "ghatira", "ghati", "tata",
        "ghatira", "kiti", "tata", "kitira", "kiti", "tata"],
       tali=[1, 4], khali=[7], vibhag=[1, 4, 7]),

    _e("Bhajani", 8, 1,
       ["dhin", "ta", "dhin", "dhinta", "tin", "ta", "tin", "tinta"],
       tali=[1], khali=[5], vibhag=[1, 5],
       note="off-beat feel on matras 2,3,6,7 per source"),

    _e("Brahma", 14, 1,
       ["dha", "tita", "dhet", "dhinna", "dhage", "dhet", "dhet",
        "dhinna", "naga", "dhage", "tita", "kata", "gadi", "gana"],
       tali=[1, 3, 4, 6, 7, 8, 13], khali=[10],
       vibhag=[1, 3, 4, 6, 7, 8, 10, 13]),

    _e("Campaka Savari", 11, 2,
       # half-grid, 22 slots; savari-style compressed tail
       ["dhin", "-", "na", "-", "dha", "-", "na", "-",
        "kat", "-", "dhin", "-", "tira", "-", "dhinna", "-",
        "tin", "na", "katta", "tiradhin", "na", "dhindhinte"],
       tali=[1, 9, 20], khali=[17], vibhag=[1, 9, 17, 20],
       note="fractional-beat alignment approximate (savari tail 1.5+1.5)"),

    _e("Chartal Ki Savari", 11, 2,
       ["dhin", "-", "tirakita", "-", "dhin", "-", "na", "-",
        "tu", "-", "na", "-", "kat", "-", "ta", "-",
        "dhin", "-", "na", "dhin", "na", "-"],
       tali=[1, 5, 13, 17, 20], khali=[9], vibhag=[1, 5, 9, 13, 17, 20]),

    _e("Choti Dasakusi", 7, 1,
       ["dhadhina", "gadhina", "dhadhina", "gadhina",
        "dhadhirkit", "dhadhirkit", "ghagha"],
       tali=[1, 3, 5, 6], khali=[7], vibhag=[1, 3, 5, 6, 7],
       note="Bengali tal; source notes tali/khali structure is not very clear"),

    _e("Dharami", 11.5, 2,
       # dhamar with the final three matras compressed into 1.5
       ["ka", "-", "dhi", "-", "ta", "-", "dhi", "-", "ta", "-",
        "dha", "-", "-", "-", "ga", "-", "ti", "-", "ta", "-",
        "ti", "ta", "ka"],
       tali=[1, 11, 21], khali=[15], vibhag=[1, 11, 15, 21],
       note="11.5 beats on half-grid; matra 7 is a true rest (as in Dhamar)"),

    _e("Krsna", 20, 1,
       ["dhin", "dhita", "dhita", "dha", "dhin", "dhita", "dhita", "dha",
        "dhita", "dhita", "dhita", "ta", "ka", "tita", "tita", "ta",
        "tira", "kita", "gadi", "gana"],
       tali=[1, 5, 9, 17], khali=[13], vibhag=[1, 5, 9, 13, 17],
       note="matra 5 bol illegible in source, restored as dhin (tintal-extension reading)"),

    _e("Lofa", 12, 1,
       ["dha", "ge", "dhin", "na", "ge", "dhin", "na", "-",
        "ti", "ta", "keke", "ti"],
       tali=[1, 4, 9], khali=[7, 11], vibhag=[1, 4, 7, 9, 11],
       note="source notes some render this 2+2+2+2+2+2 instead"),

    _e("Magdha", 23, 1,
       ["dha", "-", "dhi", "na", "na", "ka", "dhet", "-",
        "dhi", "na", "na", "ka", "dhet", "-", "dhet", "-",
        "dhita", "dha", "-", "tira", "kita", "gadi", "gana"],
       tali=[1, 5, 9, 13, 17, 20, 22], khali=[],
       vibhag=[1, 5, 9, 13, 17, 20, 22],
       note="no khali; rest placement approximate"),

    _e("Prabhupada", 16, 1,
       ["dha", "tira", "kita", "ta", "ta", "tira", "kita", "ta",
        "ka", "tira", "kita", "dha", "dhin", "dha", "dhin", "dha"],
       tali=[1, 13], khali=[7], vibhag=[1, 9, 13],
       note="khali at 7 (mid-vibhag) as stated by source; khol tal by Gour Mohan Dey"),

    _e("Sravana Nila", 21, 1,
       ["dha", "gadi", "gana", "dha", "gadi", "gana", "dhage",
        "tita", "gadi", "gana", "naga", "tira", "kita", "naga",
        "tira", "kita", "dhage", "tita", "kata", "gadi", "gana"],
       tali=[1, 4, 7, 11, 14, 17], khali=[],
       vibhag=[1, 4, 7, 11, 14, 17],
       note="no khali"),

    _e("Tivra", 7, 1,
       ["dha", "dhin", "ta", "tira", "kita", "gadi", "gana"],
       tali=[1, 4, 6], khali=[], vibhag=[1, 4, 6],
       note="source text says tali 1,4,7 but its own chart marks 1,4,6; chart used"),

    _e("Upadasi", 10.5, 2,
       ["tin", "-", "ta", "-", "tirakita", "-", "tin", "-", "ta",
        "tira", "-", "kita", "dhin", "-", "-", "dhage", "na", "-",
        "dhin", "dhage", "na"],
       tali=[1, 7, 13, 16, 19], khali=[10], vibhag=[1, 7, 10, 16, 19],
       note="10.5 beats, the most fraction-heavy tal in the set; alignment reconstructed on half-grid"),

    _e("Upatala Jhampaka", 8.5, 2,
       # jhaptal with matras 8-10 compressed into 1.5
       ["dhin", "-", "na", "-", "dhin", "-", "dhin", "-", "na", "-",
        "tin", "-", "na", "-", "dhin", "dhin", "na"],
       tali=[1, 5, 15], khali=[11], vibhag=[1, 5, 11, 15],
       note="aka Rupam tala; jhaptal with a compressed tail"),

    _e("Vikram", 6, 1,
       ["dha", "dhetta", "ta", "dinta", "tirakita", "gadigana"],
       tali=[1, 2, 5], khali=[3], vibhag=[1, 2, 3, 5]),

    _e("Visva", 13, 1,
       ["dha", "dhin", "dhina", "naka", "dhet", "dhet", "dhina",
        "naka", "dhet", "tita", "kata", "gadi", "gana"],
       tali=[1, 3, 5, 7, 9, 12], khali=[6, 10],
       vibhag=[1, 3, 5, 6, 7, 9, 10, 12]),

    _e("Visva Vandita", 8, 1,
       ["dhatita", "dinta", "tita", "dinta", "tita", "dinta",
        "tirakita", "gadigana"],
       tali=[1, 7], khali=[5], vibhag=[1, 5, 7],
       note="syllable-to-beat grouping approximate"),
]


if __name__ == "__main__":
    problems = 0
    for t in KKSONGS_TALS:
        n = t["steps"]
        for field in ("tali", "khali", "vibhag"):
            bad = [i for i in t[field] if not (1 <= i <= n)]
            if bad:
                problems += 1
                print(f"[RANGE] {t['tal']}: {field} {bad} outside 1..{n}")
        if len(t["bols"]) != n:
            problems += 1
            print(f"[LEN] {t['tal']}: {len(t['bols'])} bols != {n} steps")
        if 1 not in t["vibhag"]:
            problems += 1
            print(f"[VIBHAG] {t['tal']}: no section start at step 1")
    print(f"{len(KKSONGS_TALS)} tals, {'no problems' if not problems else str(problems) + ' problems'}")
