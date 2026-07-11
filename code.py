"""68 Certain Teas v2 -- OAM Uncertainty firmware: steps through ~170 tala
gate patterns from five Indian rhythm systems (Hindustani, KKSongs
rarities, Rabindrik, Odissi, Carnatic).

Setup: copy this file plus realized_patterns.py to the root of CIRCUITPY.

CHANNEL LAYOUT -- fixed for every pattern (see gate_mapping.py):
    1  Sam (cycle start)      5  Treble voice (closed)
    2  Tali (section claps)   6  Open/resonant voice
    3  Khali (waved beats)    7  Flourish / finger counts
    4  Bass voice             8  Vibhag/anga boundary

Patterns have VARIABLE lengths (3 to 128 steps) -- LENGTHS gives each
pattern's step count and OFFSETS (computed once at boot) indexes into the
flat STEP_DATA bytes blob, one byte per step, bit (channel-1) = channel
fires. A handful of patterns are on a half-beat grid (fractional-matra
tals like Dharami 11.5) -- clock those at 2x; they're flagged in the
realized_patterns.py name list.

Pattern order is grouped by system (Hindustani core, KKSongs rarities,
Rabindrik, Odissi, Carnatic), simplest-first within each group, baked
into realized_patterns.py at generation time -- nothing is sorted at boot.

CV input (bipolar, ~-5V to +5V), same shape as v1 / errorz-barz:

    v > RISING_THRESHOLD_V
        Clock. Advances one step and fires a fixed TRIGGER_LENGTH_S pulse
        on that step's channels, regardless of how long the input stays
        past the threshold.

    v < FALLING_THRESHOLD_V
        Pattern select. Advances to the next pattern (reset to step 0)
        once per crossing, then shows that pattern's index in binary
        across all 8 outputs (ch1 = bit 0 / LSB) for as long as the input
        stays below the threshold.

    -DEAD_ZONE_V..DEAD_ZONE_V
        Off. Re-arms both triggers.

    Anywhere else: off; hysteresis headroom.

BOOT LOG (ported from errorz-barz -- see that repo for the full story):
a one-line breadcrumb in NVM says how far the last boot got, and a
separate 4-byte counter bumps unconditionally every boot so a crash loop
that dies before any checkpoint is still visible. Read it over serial:
    import microcontroller
    bytes(microcontroller.nvm[0:64]).split(b'\x00')[0]   # last outcome
    int.from_bytes(microcontroller.nvm[64:68], "little")  # boot attempts

Design: cubbs. Built by: Claude (Fable) & cubbs, 2026.
"""

import time
import board
from analogio import AnalogIn
import digitalio
import gc
import microcontroller

_LOG_SIZE = 64        # bytes reserved for the last-real-outcome message
_COUNTER_OFFSET = 64  # 4 bytes: boot-attempt counter, bumped every boot


def _log(status):
    """Best-effort NVM breadcrumb; never raises."""
    try:
        data = status.encode("ascii")[:_LOG_SIZE]
        data += b"\x00" * (_LOG_SIZE - len(data))
        microcontroller.nvm[0:_LOG_SIZE] = data
    except Exception:
        pass


def _bump_boot_counter():
    try:
        n = int.from_bytes(
            bytes(microcontroller.nvm[_COUNTER_OFFSET:_COUNTER_OFFSET + 4]), "little"
        )
        n = (n + 1) % (2 ** 32)
        microcontroller.nvm[_COUNTER_OFFSET:_COUNTER_OFFSET + 4] = n.to_bytes(4, "little")
    except Exception:
        pass


_bump_boot_counter()

try:
    from realized_patterns import STEP_DATA, LENGTHS, PATTERN_COUNT
except Exception as e:
    _log("FAIL import {} free={}".format(type(e).__name__, gc.mem_free()))
    raise

# per-pattern start offsets into STEP_DATA, computed once (a few hundred
# bytes of RAM -- cheap, and keeps the hot loop to one add + one index)
try:
    OFFSETS = []
    _off = 0
    for _n in LENGTHS:
        OFFSETS.append(_off)
        _off += _n
except Exception as e:
    _log("FAIL offsets {} free={}".format(type(e).__name__, gc.mem_free()))
    raise

# ---- CV input calibration ----
# Uncertainty reads ~-5V..+5V as 0..65535 centered at 32768 (see OAM's
# own MicroPython examples).
ADC_CENTER = 32768
ADC_FULLSCALE_VOLTS = 5.0

def raw_to_volts(raw):
    return (raw - ADC_CENTER) / ADC_CENTER * ADC_FULLSCALE_VOLTS

RISING_THRESHOLD_V = 4.0
FALLING_THRESHOLD_V = -2.0  # tuned to this rig: the select pulse is a
                            # PNW clock inverted through an attenuverter
                            # and lands around -2.4V at the jack. Narrower
                            # hysteresis band than the +4V side, fine as
                            # long as nothing else in the patch swings
                            # negative; raise magnitude if you ever get
                            # phantom pattern advances
DEAD_ZONE_V = 1.0
TRIGGER_LENGTH_S = 0.005

# CV meter mode: normal operation is suspended and the LEDs show what the
# firmware is reading -- ch8 on = input is negative, ch1..ch7 are a
# thermometer bar, one LED per volt of magnitude. Send your select pulse
# and count LEDs: if a "-5V" pulse only lights 3, you've found the
# problem (and can trim FALLING_THRESHOLD_V / ADC_CENTER to match).
DEBUG_CV = False

# ---- hardware setup ----
try:
    cv_in = AnalogIn(board.A0)
    GATE_PINS = [board.D1, board.D2, board.D3, board.D6, board.D10, board.D9, board.D8, board.D7]
    outs = [digitalio.DigitalInOut(p) for p in GATE_PINS]
    for out in outs:
        out.direction = digitalio.Direction.OUTPUT
        out.value = False
except Exception as e:
    _log("FAIL hw_setup {} free={}".format(type(e).__name__, gc.mem_free()))
    raise

ALL_OFF = 0

_log("boot OK n={} free={}".format(PATTERN_COUNT, gc.mem_free()))


def set_outputs(step_byte):
    """bit (channel-1) set -> that channel on."""
    for i in range(8):
        outs[i].value = bool((step_byte >> i) & 1)


# ---- state ----
pattern_index = 0
step_index = 0
armed_rising = True
armed_falling = True
pulse_off_at = None
pattern_index_mask = ALL_OFF

set_outputs(ALL_OFF)  # start silent; first clock pulse lights up step 0

try:
    while True:
        now = time.monotonic()
        volts = raw_to_volts(cv_in.value)

        if DEBUG_CV:
            mag = min(7, int(abs(volts) + 0.5))
            mask = (1 << mag) - 1          # thermometer on ch1..ch7
            if volts < 0:
                mask |= 0x80               # ch8 = negative sign
            set_outputs(mask)
            continue

        if pulse_off_at is not None and now >= pulse_off_at:
            set_outputs(ALL_OFF)
            pulse_off_at = None

        if volts > RISING_THRESHOLD_V:
            if armed_rising:
                armed_rising = False
                step_index = (step_index + 1) % LENGTHS[pattern_index]
                set_outputs(STEP_DATA[OFFSETS[pattern_index] + step_index])
                pulse_off_at = now + TRIGGER_LENGTH_S
            armed_falling = True

        elif volts < FALLING_THRESHOLD_V:
            if armed_falling:
                armed_falling = False
                pattern_index = (pattern_index + 1) % PATTERN_COUNT
                step_index = 0
                # the index in binary IS a valid channel bitmask while
                # PATTERN_COUNT <= 256 (ch1 = bit 0 = LSB)
                pattern_index_mask = pattern_index
            armed_rising = True
            set_outputs(pattern_index_mask)

        elif -DEAD_ZONE_V <= volts <= DEAD_ZONE_V:
            set_outputs(ALL_OFF)
            armed_rising = True
            armed_falling = True

        else:
            set_outputs(ALL_OFF)
except Exception as e:
    _log(
        "FAIL loop {} p={} s={} free={}".format(
            type(e).__name__, pattern_index, step_index, gc.mem_free()
        )
    )
    raise
