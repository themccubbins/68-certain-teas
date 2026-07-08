"""68 Certain Teas -- North Indian tabla tal/theka rhythm data: 38 tals, 68 theka variants.

TERMS
    tal      A rhythmic cycle: a fixed number of beats, grouped into
             sections with a fixed accent pattern (e.g. Tintal = 16 beats,
             grouped 4+4+4+4).
    theka    A specific sequence of drum strokes that realizes a tal.
             One tal can have several thekas (e.g. a standard version and
             a "Benares" version) that share the same beat count and
             accent pattern but use different strokes.
    bol      The name of a single drum stroke/syllable (Dha, Dhin, Na,
             Tin, ...). A theka is one bol per beat.
    vibhag   The accent/clap structure of a tal, one marker per beat:
                 X        sam    -- beat 1, always the strongest accent
                 2, 3, ...tali   -- a later clapped/accented beat
                 0        khali  -- a waved, deliberately unaccented beat
                 .        an ordinary unaccented beat

Bols are transliterated ASCII, diacritics dropped for portability. A "-"
bol means "no new stroke this beat" (a held/rest beat).

DATA STRUCTURES
    TALS_RAW    The source data, as transcribed from the reference site:
                one (tal_name, beats, [(variant_name, bols, vibhag), ...])
                tuple per tal. `bols` and `vibhag` are strings straight
                from the site's notation (groups separated by "|", beats
                by spaces) -- see _parse_group_string.
    THEKAS      The usable form: TALS_RAW parsed and flattened into one
                dict per theka, with bols/vibhag as lists and an `accents`
                list added (1 = sam or tali, 0 = khali or unaccented).
                This is what other files in this project import.
    NAME_MAP    Maps the smaller 9-theka set bundled with Seaside
                Modular's VCV Rack "Tala" module onto the names used here.
    THEKA_NOTES Per-theka notes where the source page's raw notation
                needed a token dropped to make bol-count, vibhag-count,
                and the stated beat count agree (see self-test below).

Run this file directly (`python tala_patterns.py`) to self-test that every
theka's bol-count, vibhag-count, and stated beat count all agree.

Source: DigiTabla.com, "Extended List of North Indian Tals and Thekas"
        https://digitabla.com/reference/tals-and-thekas/extended-list/
        (citing Chhotelal Misra, "Tal Prabandh", Kanishka Publishers, 2006)
Built by: Claude (Sonnet) & cubbs, 2026.
"""

NAME_MAP = {
    # Seaside Modular Tala name -> digitabla.com name
    "teental": "Tintal",
    "rupaktal": "Rupak",
    "jhaptal": "Jhaptal",
    "dadra": "Dadra",
    "ek tal": "Ektal",
    "tilwada": "Tilwara",
    "jhoomra": "Jhumra",
    "keherwa": "Kaharawa",
    "adachautal": "Arachartal",  # Seaside's data for this one was wrong; see module docstring
}

THEKA_NOTES = {
    "Rupak Theka": "source page's raw notation had an extra hold-mark; dropped to match the stated 7 beats",
    "Rupak 2": "source page's raw notation had an extra hold-mark; dropped to match the stated 7 beats",
    "Benares Rupak Theka": "source page's raw notation had an extra hold-mark; dropped to match the stated 7 beats",
    "Pashto Theka": "source page's raw notation had an extra hold-mark; dropped to match the stated 7 beats",
    "Jhap Sawari Theka": "vibhag had one extra trailing token vs. the bol line; dropped to match",
    "Ganesh Theka": "source page left the trailing 'ga na' beats unlabelled in the vibhag; treated as unaccented continuation",
}

# name, beats, [(variant_name, bols, vibhag), ...]
TALS_RAW = [
    ("Dadra", 6, [
        ("Dadra Theka", "dha dhi na | dha ti na", "X . . | 0 . ."),
        ("Benares Dadra Theka", "dhi dhi na | dha tu na", "X . . | 0 . ."),
    ]),
    ("Rupak", 7, [
        ("Rupak Theka", "ti ti na dhi na dhi na", "0 . . 1 . 2 ."),
        ("Rupak 2", "ti ti na dhi na dhi na", "X . . 1 . 2 ."),
        ("Benares Rupak Theka", "tin na tirakita dhin dhin dha dha", "0 . . 1 . 2 ."),
    ]),
    ("Pashto", 7, [
        ("Pashto Theka", "tin - traka dhin - dha ge", "X . . 2 . 3 ."),
    ]),
    ("Kaharawa", 8, [
        ("Kaharawa Theka", "dha ge na ti | na ke dhi na", "X . . . | 0 . . ."),
    ]),
    ("Dhumali", 8, [
        ("Dhumali Theka", "dhin dhin dha tin | traka dhin dhage traka", "X . . . | 0 . . ."),
        ("Dhumali 2", "dhin dhin dha tin | traka dhin dhage traka", "X . 2 . | 0 . 3 ."),
    ]),
    ("Basant", 9, [
        ("Basant Theka", "dha din ta dhet ta | tete kata gadi gana", "X 2 3 4 0 | 5 0 6 0"),
    ]),
    ("Jhap Sawari", 9, [
        ("Jhap Sawari Theka", "dhi na dhi dhi na | katta dhidhi nadhi dhina", "X . 2 . . | 0 . 3 ."),
    ]),
    ("Jhaptal", 10, [
        ("Jhaptal Theka", "dhi na dhi dhi na | ti na dhi dhi na", "X . 2 . . | 0 . 3 . ."),
    ]),
    ("Sultal", 10, [
        ("Sultal Theka 1", "dha dha din ta kita dha | tete kata gadi gana", "X . 0 . 2 . | 3 . 0 ."),
        ("Sultal Theka 2", "dha - din din ta - | tete kata gadi gana", "X . 0 . 2 . | 3 . 0 ."),
        ("Sultal Theka 3", "dha ghera naga di ghera naga | gad di ghera naga", "X . 0 . 2 . | 3 . 0 ."),
    ]),
    ("Rudra", 11, [
        ("Rudra Theka", "dha tet dha tirakita dhi na | tirakita tu na kat ta", "X 0 2 3 4 0 | 5 6 7 8 0"),
        ("Benares Rudra Theka", "dhi--kra dhinta dhinta kat | gheranaga takitadha -radha- kataghina | -dha-ra dha kat", "X 0 2 3 | 4 0 5 6 | 7 8 0"),
    ]),
    ("Kumbha", 11, [
        ("Kumbha Theka 1", "dha dhina taka tete dha | ghera naga tete kata gadi gana", "X 0 2 3 4 | 0 5 6 7 8 0"),
        ("Kumbha Theka 2", "dha dhin tete kata dha | dhin naka tete kata gadi gana", "X 0 2 3 4 | 0 5 6 7 8 0"),
        ("Benares Kumbha Theka", "dha dina taka tete dha | dina taka tete kata gadi gana", "X 0 2 3 4 | 0 5 6 7 8 0"),
    ]),
    ("Ashtamangal 1", 11, [
        ("Ashtamangal 1 Theka", "dhi na dhi dhi na | dhi dhi na dhage nadha traka", "X 0 2 3 0 | 4 5 0 6 7 8"),
    ]),
    ("Ektal", 12, [
        ("Ektal Theka", "dhin dhin dhage tirakita | tu na kat ta | dhage tirakita dhin na", "X . 0 . | 2 . 0 . | 3 . 4 ."),
    ]),
    ("Chautal", 12, [
        ("Chautal Theka", "dha dha din ta | kita dha din ta | tete kata gadi gana", "X . 0 . | 2 . 0 . | 3 . 4 ."),
    ]),
    ("Khemta", 12, [
        ("Khemta Theka", "dha te dhi na ti na | ta te dhi na dhi na", "X . . 2 . . | 0 . . 3 . ."),
    ]),
    ("Lilawati", 13, [
        ("Lilawati Theka", "dhin dhin dha traka | dhin - tin tin | ta traka dhin dhin -", "X . . . | 2 . . . | 3 . . 4 ."),
    ]),
    ("Arachartal", 14, [
        ("Arachartal Theka", "dhin tirakita dhi na | tu na kat ta | tirakita dhi na dhi | dhi na", "X . 2 . | 0 . 3 . | 0 . 4 . | 0 ."),
        ("Benares Arachartal Theka", "dhin tirakita dhi na | tu na kat ta | dhi dhi na dhi | dhi na", "X . 2 . | 0 . 3 . | 0 . 4 . | 0 ."),
    ]),
    ("Jhumra", 14, [
        ("Jhumra Theka", "dhin -dha tirakita | dhin dhin dhage tirakita | tin -ta tirakita | dhin dhin dhage tirakita", "X . . | 2 . . . | 0 . . | 3 . . ."),
        ("Benares Jhumra Theka", "dhin dha tirakita | dhin dhin dha dha | tin ta tirakita | dhin dhin dha dha", "X . . | 2 . . . | 0 . . | 3 . . ."),
    ]),
    ("Braha 1", 14, [
        ("Braha 1 Theka", "dha tet dhet | dhina naka dhet dhet | dhina naka dhage | tete kata gadi gana", "X 0 2 | 3 0 4 5 | 6 0 7 | 8 9 10 0"),
        ("Benares Braha 1 Theka", "dhi na tirakita | dhi na dhage tirakita | dhage tirakita tage | tirakita dhi na tet", "X 0 2 | 3 0 4 5 | 6 0 7 | 8 9 10 0"),
    ]),
    ("Pharodasta", 14, [
        ("Pharodasta Theka", "dhin dhin dhage tirakita | tu na kat ta | dhina kadha tirakita dhina | kadha tirakita", "X . 0 . | 2 . 0 . | 3 . 4 . | 5 ."),
    ]),
    ("Dipchandi", 14, [
        ("Dipchandi Theka", "dha dhin - dha dha tin - | ta tin - dha dha dhin -", "X . . 2 . . . | 0 . . 3 . . ."),
    ]),
    ("Dhamar", 14, [
        ("Dhamar Theka 1", "ka dhe te dhe te dha - | ga te te te te ta -", "X . . . . 2 . | 0 . . 3 . . ."),
        ("Dhamar Theka 2", "ka dhe te dhe te dha - | ga di na di na ta -", "X . . . . 2 . | 0 . . 3 . . ."),
    ]),
    ("Pancham Sawari", 15, [
        ("Pancham Sawari Theka", "dhi na dhidhi | kat dhidhi nadhi dhina | ti--kra tina tirakita tuna | katta dhidhi nadhi dhina", "X . . | 2 . . . | 0 . . . | 3 . . ."),
        ("Benares Pancham Sawari Theka", "dha dhin dhage | nage ti--kra tina tina | tina katta dhidhi nadhi | dhina dha--kra dhindhin dhatit", "X . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Gajajhampa", 15, [
        ("Gajajhampa Theka", "dha dhina naka taka | dha dhina naka taka | tin naka taka | tete kata gadi gana", "X . . . | 2 . . . | 0 . . | 3 . . ."),
    ]),
    ("Chhoti Sawari", 15, [
        ("Chhoti Sawari Theka", "dha - dha di | ga na dhu ma | ki ta ta ka | dhi na ta", "X . . . | 2 . . . | 3 . . . | 4 . ."),
    ]),
    ("Tintal", 16, [
        ("Tintal Theka", "dha dhin dhin dha | dha dhin dhin dha | dha tin tin ta | ta dhin dhin dha", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Tilwara", 16, [
        ("Tilwara Theka", "dha tirakita dhin dhin | dha dha tin tin | ta tirakita tin tin | dha dha dhin dhin", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
        ("Benares Tilwara Theka", "dha tirakita dhin dhin | dha dha tin tin | ta tirakita dhin dhin | dha dha dhin dhin", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Bari Sawari", 16, [
        ("Bari Sawari Theka", "dhi na dhi na | dhidhi dhina dhidhi dhina | ta-traka tuna ta-traka tuna | katta- trakadhina ginadhage nadhatraka", "X . 0 . | 2 . 0 . | 3 . 4 . | 5 . 0 ."),
        ("Bari Sawari 2", "dha - ki ta | dhu ma ki ta | ta ki ta ta | ka - ki ta", "X . . . | 2 . . . | 3 . . . | 4 . 5 ."),
    ]),
    ("Jat", 16, [
        ("Jat Theka", "dha - dhin - | dha dha tin - | ta - tin - | dha dha dhin -", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Ikwai", 16, [
        ("Ikwai Theka", "dha - ghe ghe | dha ghe - ghe | ta - ke ke | dha ghe - ghe", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Sitarkhani", 16, [
        ("Sitarkhani Theka", "dha -dhi -ka dha | dha -dhi -ka dha | dha -ti -ka ta | ta -dhi -ka dha", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Tappa", 16, [
        ("Tappa Theka 1", "dhin - dha -ga | dha dhin ta -kra | tin - ta -ga | dha dhin ta -kra", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
        ("Tappa Theka 2", "dha dhin -ta dhin | dha dhin -ta dhin | ta ka -ta kat | ta dhin -ta dhin", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
        ("Benares Tappa Theka", "dha -kra dhin - | dha -ga dha tin | ta -kra tin - | dha -ga dha dhin", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Panjabi", 16, [
        ("Panjabi Theka", "dha -dhin naka dha | dha -dhin naka dha | dha -tin naka ta | ta -dhin naka dha", "X . . . | 2 . . . | 0 . . . | 3 . . ."),
    ]),
    ("Shikhar", 17, [
        ("Shikhar Theka", "dha traka dhina naka | thun ga dhina naka | dhuma kita taka dhet dha | tete kata gadi gana", "X . . . | 2 . . . | 3 . . 4 . | 5 . . ."),
    ]),
    ("Vishnu", 17, [
        ("Vishnu Theka", "dha - ki ta ta ka | dhu ma ki ta ta ka | dhe - dhi na ta", "X . . . 2 . | 3 . . . 4 . | 5 . 6 . ."),
        ("Vishnu 2", "dha - ki ta ta ka | dhu ma ki ta ta ka | dha - dhi na ta", "X . 2 . . . | 3 . . . 4 . | 5 . 6 . ."),
        ("Vishnu 3", "dhin na dhin dhin na | dhin traka dhi na | dhin dhin na dhin | dhin na dhi na", "X . 2 . . | 3 . . . | 4 . . . | 0 . . ."),
        ("Vishnu 4", "dhin tirakita dhi na | tu na kat ta | tirakita dhi na dhage | nadha traka dhage nadha traka", "X . 0 . | 2 . 0 . | 3 . 4 . | 5 . 6 . ."),
    ]),
    ("Churamani", 17, [
        ("Churamani Theka", "dha ka ta tu nna | dhi dhi na traka | na dhi dhi na | dhi traka dhi na", "X . . 2 . | 3 . . . | 4 . . . | 5 . . ."),
    ]),
    ("Mayur", 17, [
        ("Mayur Theka", "dha dha dhina naka dhe dhe | dhina naka ki ta ta ka | ga di ga na ta", "X . 2 . . . | 3 . . . . . | 4 . . . ."),
    ]),
    ("Matta", 18, [
        ("Matta Theka 1", "dha - ghi ra na ka | ghi ra na ka te te | ka ta ga di ga na", "X . 0 . 2 . | 3 . 0 . 4 . | 5 . 6 . 0 ."),
        ("Matta Theka 2", "dhin - na - dhin tirakita | dhi na tu na kat ta | tirakita dhi na dhi dhi na", "X . 0 . 2 . | 3 . 0 . 4 . | 5 . 6 . 0 ."),
        ("Matta Theka 3", "dha - ki ta ta ka | dhin - ta - ta ka | dhi na ga di ga na", "X . 0 . 2 . | 3 . 0 . 4 . | 5 . 6 . 0 ."),
    ]),
    ("Lakshmi", 18, [
        ("Lakshmi Theka", "dhinna dhindha tirakita dhinna | dhindha tirakita dhadha tirakita | dhadha tirakita dhinna dhindha | tirakita tuna kiranaga tage | ta- tirakita", "X 2 3 0 | 4 5 6 0 | 7 8 9 10 | 11 12 13 14 | 15 0"),
        ("Benares Lakshmi Theka", "dha - dhet dhet | dha - tirakita dhet | dha - dhet dha | tirakita dhet dhedhe -dha | -na dhet", "X 2 3 0 | 4 5 6 0 | 7 8 9 10 | 11 12 13 14 | 15 0"),
    ]),
    ("Ganesh", 18, [
        ("Ganesh Theka", "dha - dhi ta | dhi ta dha - | dha - ki ta | ta ka dha di | ga na", "X . . . | 2 . . . | 3 . . . | 4 . 5 . | . ."),
    ]),
    ("Shesh", 19, [
        ("Shesh Theka", "dha - ki ta | ta ka dhu ma | ki ta ta ka | dha - ta - | dha gadi gana", "X . . . | 2 . . . | 3 . 4 . | 5 . . . | 6 7 ."),
    ]),
    ("Ashtamangal 2", 22, [
        ("Ashtamangal 2 Theka", "dha - ki ta ta ka | dhu ma ki ta ta ka | dhe - ta - ta ka | dha di ga na", "X . 0 . 2 . | 3 . 0 . 4 . | 5 . 0 . 6 . | 7 . 8 ."),
    ]),
    ("Braha 2", 28, [
        ("Braha 2 Theka", "dha - ta - dha - | di na ta - ki ta | dha - din - ta - | dha - te te ka ta | ga di ga na", "X . 0 . 2 . | 3 . 0 . 4 . | 5 . 6 . 0 . | 7 . 8 . 9 . | 10 . 0 ."),
        ("Benares Braha 2 Theka", "dhi - na - tira kita | dhi - na - dha ge | tira kita dhi - na - | tet - dha ge tira kita | ta ge tira kita", "X . 0 . 2 . | 3 . 0 . 4 . | 5 . 6 . 0 . | 7 . 8 . 9 . | 10 . 0 ."),
    ]),
]


def _parse_group_string(s):
    """'a b | c d' -> ['a', 'b', 'c', 'd']"""
    tokens = []
    for group in s.split("|"):
        tokens.extend(group.split())
    return tokens


def _accents_from_vibhag(vibhag_tokens):
    """X or a tali number -> 1 (accented). '0' (khali) or '.' -> 0."""
    accents = []
    for tok in vibhag_tokens:
        if tok == "X" or (tok.isdigit() and tok != "0"):
            accents.append(1)
        else:
            accents.append(0)
    return accents


def _build_thekas():
    thekas = []
    for tal_name, beats, variants in TALS_RAW:
        for variant_name, bols_str, vibhag_str in variants:
            bols = _parse_group_string(bols_str)
            vibhag = _parse_group_string(vibhag_str)
            thekas.append({
                "tal": tal_name,
                "variant": variant_name,
                "beats": beats,
                "bols": bols,
                "vibhag": vibhag,
                "accents": _accents_from_vibhag(vibhag),
                "note": THEKA_NOTES.get(variant_name),
            })
    return thekas


# Flat list of every theka, ready to use: each item has
# tal, variant, beats, bols (list[str]), vibhag (list[str]), accents (list[int])
THEKAS = _build_thekas()


def by_tal(name):
    """All theka variants for a given tal name (case-insensitive)."""
    name = name.lower()
    return [t for t in THEKAS if t["tal"].lower() == name]


if __name__ == "__main__":
    # Self-test: flag any entry where bol count, vibhag count, and stated
    # beat count don't all agree.
    print(f"{len(TALS_RAW)} tals, {len(THEKAS)} theka variants\n")
    problems = 0
    for t in THEKAS:
        nb, nv, beats = len(t["bols"]), len(t["vibhag"]), t["beats"]
        if not (nb == nv == beats):
            problems += 1
            print(f"[MISMATCH] {t['tal']} / {t['variant']}: "
                  f"bols={nb} vibhag={nv} stated_beats={beats}"
                  + (f"  (known: {t['note']})" if t["note"] else ""))
    if not problems:
        print("All entries consistent.")
    else:
        print(f"\n{problems} entries with token/beat-count mismatches (see above).")