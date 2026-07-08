"""68 Certain Teas -- assigns each theka's bols to Uncertainty's 8 gate channels.

Channel layout, fixed regardless of how sparse a theka is:
    8       tali only (numbered clap beats -- never sam, never khali)
    1..N    bol identity, most-used bol first, one channel each
    7       sam, if <= 6 distinct bols leave it free
    6       khali, if <= 5 distinct bols leave it free
    5       "plain" (any beat that's none of sam/khali/tali), if <= 4 bols
    4       alt-voice: the busiest bol round-robins onto this channel every
            other hit instead of sitting idle, if <= 3 bols

Bol count > 7 is handled by folding the least-used bol onto its closest-
sounding survivor (difflib string similarity), repeated until 7 remain --
at that point all of channels 1-7 are bol identity, with no sam/khali/plain
room left.

GATE_PATTERNS holds the result: per theka, the channel layout plus a
realized `steps` list (one tuple of active channels per beat). This is the
one-time "compile" step; realized_patterns.py serializes just that `steps`
data into a dependency-free file for the actual firmware to import -- no
difflib or merge logic needs to run on the microcontroller.

Run this file directly to print the channel layout for every theka.

Design: cubbs. Built by: Claude (Sonnet) & cubbs, 2026.
"""

from difflib import SequenceMatcher
from tala_patterns import THEKAS

MAX_BOL_CHANNELS = 7
TALI_CHANNEL = 8
REST_TOKEN = "-"


def _first_appearance_order(bols):
    """distinct bols (excluding rests), in the order they first appear"""
    seen = []
    for b in bols:
        if b != REST_TOKEN and b not in seen:
            seen.append(b)
    return seen


def _similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def _reduce_to_seven(bols):
    """
    Merge distinct bols down to <= 7 groups by repeatedly folding the
    least-used bol onto its closest-sounding surviving bol.
    Returns (groups, merges): groups is {representative: {members}},
    merges is [(victim, absorbed_into), ...] in the order it happened.
    """
    order = _first_appearance_order(bols)
    counts = {b: bols.count(b) for b in order}
    groups = {b: {b} for b in order}
    group_counts = dict(counts)
    merges = []

    while len(groups) > MAX_BOL_CHANNELS:
        victim = min(groups.keys(), key=lambda b: (group_counts[b], -order.index(b)))
        candidates = [g for g in groups.keys() if g != victim]
        best_score = max(_similarity(victim, g) for g in candidates)
        tied = sorted(g for g in candidates if _similarity(victim, g) == best_score)
        target = tied[0]

        groups[target] |= groups[victim]
        group_counts[target] += group_counts[victim]
        del groups[victim]
        del group_counts[victim]
        merges.append((victim, target))

    return groups, merges


def build_gate_pattern(theka):
    bols = theka["bols"]
    vibhag = theka["vibhag"]
    distinct = _first_appearance_order(bols)
    n = len(distinct)

    sam_channel = None
    khali_channel = None
    plain_channel = None
    altvoice_channel = None
    altvoice_bol = None
    merges = []

    if n > MAX_BOL_CHANNELS:
        groups, merges = _reduce_to_seven(bols)
        rep_of = {m: rep for rep, members in groups.items() for m in members}
        reps_by_usage = sorted(
            groups.keys(),
            key=lambda r: (-sum(bols.count(m) for m in groups[r]), bols.index(r)),
        )
        chan_of_rep = {rep: i + 1 for i, rep in enumerate(reps_by_usage)}
        bol_to_channel = {b: chan_of_rep[rep_of[b]] for b in distinct}
    else:
        order = sorted(distinct, key=lambda b: (-bols.count(b), bols.index(b)))
        bol_to_channel = {b: i + 1 for i, b in enumerate(order)}

        if n <= 6:
            sam_channel = 7
        if n <= 5:
            khali_channel = 6
        if n <= 4:
            plain_channel = 5
        if n <= 3:
            altvoice_channel = 4
            altvoice_bol = order[0] if order else None  # most-used bol

    steps = []
    altvoice_toggle = 0
    for b, v in zip(bols, vibhag):
        active = set()
        is_sam = v == "X"
        is_khali = v == "0"
        is_tali = v.isdigit() and v != "0"
        is_plain = v == "."

        if b != REST_TOKEN:
            ch = bol_to_channel[b]
            if altvoice_bol is not None and b == altvoice_bol:
                if altvoice_toggle % 2 == 1:
                    ch = altvoice_channel
                altvoice_toggle += 1
            active.add(ch)

        if is_sam and sam_channel:
            active.add(sam_channel)
        if is_khali and khali_channel:
            active.add(khali_channel)
        if is_tali:
            active.add(TALI_CHANNEL)
        if is_plain and plain_channel:
            active.add(plain_channel)

        steps.append(tuple(sorted(active)))

    return {
        "tal": theka["tal"],
        "variant": theka["variant"],
        "beats": theka["beats"],
        "bol_to_channel": bol_to_channel,
        "sam_channel": sam_channel,
        "khali_channel": khali_channel,
        "plain_channel": plain_channel,
        "altvoice_channel": altvoice_channel,
        "altvoice_bol": altvoice_bol,
        "tali_channel": TALI_CHANNEL,
        "merges": merges,
        "steps": steps,  # list[tuple[int,...]], one tuple of active channels per beat
    }


GATE_PATTERNS = [build_gate_pattern(t) for t in THEKAS]


def get(tal, variant=None):
    matches = [g for g in GATE_PATTERNS if g["tal"].lower() == tal.lower()]
    if variant:
        matches = [g for g in matches if g["variant"].lower() == variant.lower()]
    return matches


if __name__ == "__main__":
    for g in GATE_PATTERNS:
        n_bols = len(g["bol_to_channel"])
        used = sorted(set(g["bol_to_channel"].values()))
        extras = []
        if g["sam_channel"]:
            extras.append(f"sam=ch{g['sam_channel']}")
        if g["khali_channel"]:
            extras.append(f"khali=ch{g['khali_channel']}")
        if g["plain_channel"]:
            extras.append(f"plain=ch{g['plain_channel']}")
        if g["altvoice_channel"]:
            extras.append(f"altvoice({g['altvoice_bol']})=ch{g['altvoice_channel']}")
        extras.append(f"tali=ch{g['tali_channel']}")
        line = (f"{g['tal']:16} {g['variant']:28} beats={g['beats']:2}  "
                f"bols={n_bols:2} chans={used}  " + " ".join(extras))
        if g["merges"]:
            line += "  MERGED: " + ", ".join(f"{v}->{t}" for v, t in g["merges"])
        print(line)
