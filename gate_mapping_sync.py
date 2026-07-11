"""68 Certain Teas v2 -- maps every tala (5 systems, ~170 patterns) onto
Uncertainty's 8 gate outputs with ONE FIXED SEMANTIC LAYOUT.

Why fixed: v1 assigned channels per-theka ("most-used bol first"), so
cycling patterns scrambled the patch. errorz-barz learned this lesson;
this file applies it. Every channel means the same thing in all patterns:

    1  SAM       first beat of the cycle           (reset / one-shot)
    2  TALI      clapped section markers, not sam  (accent / S&H clock)
    3  KHALI     waved beats (Carnatic: nihshabda) (anti-accent)
    4  BASS      bass-hand stroke component        (kick)
    5  TREBLE    closed treble strokes             (snare / rim)
    6  OPEN      resonant/open strokes; guru and   (open hat / ring)
                 kakapadam circular motions
    7  FLOURISH  multi-stroke runs (tirakita...);  (ratchet / hat burst)
                 Carnatic finger counts
    8  BOUNDARY  first beat of every vibhag/anga   (phrase clock)

VOICE DECOMPOSITION (default bol coding)
Tabla bols are compounds: dha = ge (bass) + na (treble); dhin = ge + tin
(ring); khali sections literally drop the bass hand. Decomposing each bol
into voice components means: patch ch4 to a kick and the bass drops out
on khali vibhags exactly like a tabla player's baya. Channels 4-7 also
form a 4-bit code -- bol identity is recoverable from the combination
(logic modules / analog switch decode it), but every bit is directly
patchable as a drum voice.

Tokens are segmented into stroke atoms by greedy longest-match, channels
are unioned, and any token that packs 3+ atoms into one beat also gets
the FLOURISH bit. Unknown atoms fail the build loudly.

BINARY CODING (alternative, BOL_CODING = "binary")
Each theka's distinct bols get index 1..15, shown as plain binary across
ch4(LSB)..ch7(MSB). Max 15 distinct bols per theka (checked). More bols
representable, but the bits mean nothing acoustically.

This file is the one-time "compile" step and never runs on the module.
Run `python3 gate_mapping.py` for the layout + channel stats;
run `python3 gate_mapping.py --write` to (re)generate realized_patterns.py.

Design: cubbs. Built by: Claude (Fable) & cubbs, 2026.
"""

import sys

from tala_patterns import TALS_RAW, _parse_group_string
from kksongs_patterns import KKSONGS_TALS
from rabindrik_patterns import RABINDRIK_TALS
from carnatic_patterns import CARNATIC_TALS
from odissi_patterns import ODISSI_TALS

BOL_CODING = "voice"  # "voice" (default) or "binary"

SAM, TALI, KHALI, BASS, TREBLE, OPEN, FLOURISH, BOUNDARY = 1, 2, 3, 4, 5, 6, 7, 8
VOICE_CHANNELS = (BASS, TREBLE, OPEN, FLOURISH)  # the 4-bit bol code, LSB first

# ---- stroke atoms -> voice channels -------------------------------------
# Greedy longest-match segmentation. Approximate by design (sources
# disagree on fine points); the goal is consistent, musical decomposition.
ATOMS = {
    # bass hand, open (baya ge / pakhawaj left / mardala low head)
    "ge": {BASS}, "ga": {BASS}, "gha": {BASS}, "ghe": {BASS}, "ghi": {BASS},
    "gi": {BASS}, "gin": {BASS}, "gad": {BASS}, "ma": {BASS}, "dhu": {BASS},
    # bass hand, closed slap
    "ka": {BASS}, "kat": {BASS}, "ke": {BASS},
    # bass + treble together
    "dha": {BASS, TREBLE}, "dhe": {BASS, TREBLE}, "dhet": {BASS, TREBLE},
    # bass + open ring
    "dhin": {BASS, OPEN}, "dhi": {BASS, OPEN}, "den": {BASS, OPEN},
    "dhei": {BASS, OPEN},
    # treble, closed
    "na": {TREBLE}, "ne": {TREBLE}, "nna": {TREBLE}, "ta": {TREBLE},
    "te": {TREBLE}, "tet": {TREBLE}, "tit": {TREBLE}, "ti": {TREBLE},
    "ki": {TREBLE}, "di": {TREBLE}, "dak": {TREBLE}, "tra": {TREBLE},
    # treble, open / resonant
    "tin": {OPEN}, "thin": {OPEN}, "tun": {OPEN}, "tu": {OPEN},
    "thun": {OPEN}, "din": {OPEN},
    # flourish glue syllables (only occur inside runs)
    "ra": {FLOURISH}, "re": {FLOURISH}, "kra": {FLOURISH},
    # combined treble+bass compounds that read as one syllable
    "nag": {BASS, TREBLE},
    # named runs that can also appear inside larger tokens
    "dhirkit": {BASS, TREBLE, FLOURISH},
    "traka": {TREBLE, FLOURISH},
}

# tokens whose segmentation would misread them -- assigned whole
OVERRIDES = {
    "traka": {TREBLE, FLOURISH},
    "trakra": {TREBLE, FLOURISH},
    "trakadhina": {BASS, TREBLE, OPEN, FLOURISH},
    "kadataka": {BASS, TREBLE, FLOURISH},
    "dhirkit": {BASS, TREBLE, FLOURISH},
    "tathin": {TREBLE, OPEN},
}


def segment(token):
    """token -> list of atoms (longest-match with backtracking, so
    'dhina' resolves as dhi+na instead of dying after 'dhin').
    Raises on failure."""
    t = token.replace("-", "").lower()
    if not t:
        return []
    if t in OVERRIDES:
        return [t]
    keys = sorted(ATOMS, key=len, reverse=True)
    memo = {}

    def rec(i):
        if i == len(t):
            return []
        if i in memo:
            return memo[i]
        for k in keys:
            if t.startswith(k, i):
                rest = rec(i + len(k))
                if rest is not None:
                    memo[i] = [k] + rest
                    return memo[i]
        memo[i] = None
        return None

    atoms = rec(0)
    if atoms is None:
        raise ValueError(f"cannot segment bol {token!r} ({t!r})")
    return atoms


def voice_channels(token):
    """token -> set of voice channels under the voice-decomposition coding."""
    stripped = token.replace("-", "").lower()
    if not stripped:
        return set()
    if stripped in OVERRIDES:
        return set(OVERRIDES[stripped])
    atoms = segment(token)
    chans = set()
    for a in atoms:
        chans |= ATOMS[a]
    if len(atoms) >= 3:
        chans.add(FLOURISH)
    return chans


# ---- normalize the original digitabla data ------------------------------

def _digitabla_entries():
    """TALS_RAW -> normalized v2 entries (keeps vibhag group boundaries,
    which the flattened THEKAS list discards)."""
    out = []
    for tal, beats, variants in TALS_RAW:
        for variant, bols_str, vibhag_str in variants:
            bols = _parse_group_string(bols_str)
            marks = _parse_group_string(vibhag_str)
            starts, pos = [], 1
            for group in vibhag_str.split("|"):
                starts.append(pos)
                pos += len(group.split())
            n = min(len(bols), len(marks), beats)  # v1 data self-tests clean
            out.append({
                "system": "hindustani",
                "tal": tal, "variant": variant,
                "beats": beats, "steps_per_beat": 1, "steps": n,
                "bols": bols[:n],
                "tali": [i + 1 for i, m in enumerate(marks[:n])
                         if m == "X" or (m.isdigit() and m != "0")],
                "khali": [i + 1 for i, m in enumerate(marks[:n]) if m == "0"],
                "vibhag": [s for s in starts if s <= n],
                "note": None,
            })
    return out


ALL_ENTRIES = (
    _digitabla_entries()
    + KKSONGS_TALS
    + RABINDRIK_TALS
    + ODISSI_TALS
    + CARNATIC_TALS
)

SYSTEM_ORDER = ["hindustani", "hindustani-kksongs", "rabindrik", "odissi", "carnatic"]


# ---- realize one entry into per-step channel sets ------------------------

def build_gate_pattern(entry, coding=BOL_CODING):
    n = entry["steps"]
    tali = set(entry["tali"])
    khali = set(entry["khali"])
    vibhag = set(entry["vibhag"])
    counts = set(entry.get("counts", ()))
    motions = set(entry.get("motions", ()))
    bols = entry["bols"]

    if coding == "binary":
        distinct = []
        for b in bols:
            if b != "-" and b not in distinct:
                distinct.append(b)
        if len(distinct) > 15:
            raise ValueError(f"{entry['variant']}: {len(distinct)} bols > 15 (binary coding)")
        code = {b: i + 1 for i, b in enumerate(distinct)}

    steps = []
    for i in range(1, n + 1):
        active = set()
        if i == 1:
            active.add(SAM)
        if i in tali and i != 1:
            active.add(TALI)
        if i in khali:
            active.add(KHALI)
        if i in vibhag:
            active.add(BOUNDARY)
        if i in counts:
            active.add(FLOURISH)
        if i in motions:
            active.add(OPEN)
        b = bols[i - 1]
        if b != "-" and b.replace("-", ""):
            if coding == "binary":
                bits = code[b]
                for bit, ch in enumerate(VOICE_CHANNELS):
                    if (bits >> bit) & 1:
                        active.add(ch)
            else:
                active |= voice_channels(b)
        steps.append(tuple(sorted(active)))

    return {
        "system": entry["system"],
        "tal": entry["tal"],
        "variant": entry["variant"],
        "beats": entry["beats"],
        "steps_per_beat": entry["steps_per_beat"],
        "note": entry.get("note"),
        "steps": steps,
    }


def _complexity(entry):
    distinct = len({b for b in entry["bols"] if b != "-"})
    return (entry["steps"], distinct, entry["tal"], entry["variant"])


def build_all(coding=BOL_CODING):
    """-> list of gate patterns in play order: grouped by system,
    simplest-first within each group."""
    ordered = sorted(
        ALL_ENTRIES,
        key=lambda e: (SYSTEM_ORDER.index(e["system"]), _complexity(e)),
    )
    return [build_gate_pattern(e, coding) for e in ordered]


GATE_PATTERNS = build_all()


# ---- realized_patterns.py generator --------------------------------------

HEADER = "\x22\x22\x2268 Certain Teas v2 -- precomputed step data. GENERATED by gate_mapping.py\n" \
    "-- do not edit by hand; edit the *_patterns.py data files and regenerate.\n" \
    "\n" \
    "One flat `bytes` blob, one byte per step; bit (channel-1) set = channel\n" \
    "fires on that step (ch1 = bit 0 ... ch8 = bit 7). LENGTHS holds each\n" \
    "pattern's step count; patterns are stored back to back in play order\n" \
    "(grouped by system, simplest first). This shape is the errorz-barz\n" \
    "MemoryError fix: no tuples, no dicts, nothing for the GC to chew on.\nStored as adjacent b-string literals because a bytes([...]) list\nliteral this long exhausts the RP2040 parser's pystack (RuntimeError).\n" \
    "\n" \
    "Bol coding: {coding}. Patterns: {count}. Total steps: {total}.\n" \
    "\x22\x22\x22\n" \
    "\n" \
    "PATTERN_COUNT = {count}\n" \
    "\n" \
    "# step count per pattern, in play order\n" \
    "LENGTHS = (\n" \
    "{lengths}\n" \
    ")\n" \
    "\n" \
    "# names, one per pattern, in play order (comment only -- costs flash,\n" \
    "# zero RAM):\n" \
    "{names}\n" \
    "\n" \
    "STEP_DATA = (\n" \
    "{data}\n" \
    ")\n"


def write_realized(path="realized_patterns.py", coding=BOL_CODING):
    pats = build_all(coding)
    if len(pats) > 256:
        raise ValueError(f"{len(pats)} patterns > 256 (binary index readout limit)")
    lengths, blob, names = [], [], []
    for p in pats:
        lengths.append(len(p["steps"]))
        for active in p["steps"]:
            byte = 0
            for ch in active:
                byte |= 1 << (ch - 1)
            blob.append(byte)
        half = " [half-beat grid: clock at 2x]" if p["steps_per_beat"] == 2 else ""
        names.append(f"#   {len(names):3d}  {p['system']:22s} {p['variant']}{half}")

    def chunk(vals, per):
        # adjacent b"" literals: constant-folded at parse time, so the
        # CircuitPython compiler never builds a 2000-element list literal
        # (bytes([...]) exhausted its pystack -- RuntimeError on import)
        lines = []
        for i in range(0, len(vals), per):
            hexes = "".join("\\x%02x" % v for v in vals[i:i + per])
            lines.append('    b"' + hexes + '"')
        return "\n".join(lines)

    src = HEADER.format(
        coding=coding,
        count=len(pats),
        total=len(blob),
        lengths=chunk(lengths, 16),
        names="\n".join(names),
        data=chunk(blob, 16),
    )
    with open(path, "w") as f:
        f.write(src)
    return len(pats), len(blob)


# ---- self-test / report ---------------------------------------------------

if __name__ == "__main__":
    problems = []

    all_tokens = sorted({b for e in ALL_ENTRIES for b in e["bols"] if b != "-"})
    for tok in all_tokens:
        try:
            if not voice_channels(tok):
                problems.append(f"bol {tok!r} maps to NO channels")
        except ValueError as err:
            problems.append(str(err))

    pats = GATE_PATTERNS
    if len(pats) > 256:
        problems.append(f"{len(pats)} patterns exceeds 256")

    hits = {ch: 0 for ch in range(1, 9)}
    total_steps = 0
    for p in pats:
        total_steps += len(p["steps"])
        for active in p["steps"]:
            for ch in active:
                hits[ch] += 1
    per_system = {}
    for p in pats:
        per_system[p["system"]] = per_system.get(p["system"], 0) + 1

    if "-v" in sys.argv or "--verbose" in sys.argv:
        for p in pats:
            print(f"{p['system']:22s} {p['variant']:42s} steps={len(p['steps']):3d}")
        print()

    print(f"{len(pats)} patterns, {total_steps} total steps "
          f"({total_steps} bytes of step data)")
    for s in SYSTEM_ORDER:
        print(f"  {s:22s} {per_system.get(s, 0):3d}")
    print(f"distinct bol tokens: {len(all_tokens)}")
    labels = ["sam", "tali", "khali", "bass", "treble", "open", "flourish", "boundary"]
    for ch in range(1, 9):
        pct = 100.0 * hits[ch] / total_steps
        print(f"  ch{ch} {labels[ch-1]:9s} fires on {hits[ch]:4d} steps ({pct:4.1f}%)")

    if problems:
        print(f"\n{len(problems)} PROBLEMS:")
        for p in problems:
            print(" ", p)
        sys.exit(1)
    print("no problems")

    if "--write" in sys.argv:
        n, b = write_realized()
        print(f"wrote realized_patterns.py: {n} patterns, {b} step bytes")
