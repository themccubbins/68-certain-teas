"""68 Certain Teas -- OAM Uncertainty firmware: steps through 68 tabla theka gate patterns.

Setup: copy this file plus realized_patterns.py to the root of CIRCUITPY.

Theka order is simplest-first (beat count, then bol complexity, then name
-- see realized_patterns.py) and cycles forward each time the CV input
goes low. The module boots into THEKAS[0].

CV input (bipolar, ~-5V to +5V) drives clock and theka-select separately:

    v > RISING_THRESHOLD_V
        Clock. Advances one step and fires a fixed TRIGGER_LENGTH_S pulse
        on that step's channels, regardless of how long the input stays
        past the threshold -- a gate-length-follower here made triggers
        wider than the source pulse on real hardware, so this fires clean
        and constant-width instead.

    v < FALLING_THRESHOLD_V
        Theka select. Advances to the next theka (reset to step 0) once
        per crossing, then shows that theka's index in binary across all
        8 outputs (channel 1 = bit 0 / LSB, channel 8 = bit 7 / MSB) for
        as long as the input stays below the threshold -- this one DOES
        follow gate length, on purpose, so the binary readout is actually
        held long enough to read off the LEDs.

    -DEAD_ZONE_V..DEAD_ZONE_V
        Off. Re-arms both triggers.

    Anywhere else (between the dead zone and either threshold): also off,
    undefined otherwise -- gives hysteresis headroom.

Each gate output's LED is hardwired to it on Uncertainty, so there's no
separate LED code needed.

Design: cubbs. Built by: Claude (Sonnet) & cubbs, 2026.
"""

import time
import board
from analogio import AnalogIn
import digitalio

from realized_patterns import REALIZED

# ---- CV input calibration ----
# Uncertainty's CV input reads roughly -5V to +5V as a 16-bit unsigned
# value (0-65535), centered at 32768 for 0V -- see OAM's own MicroPython
# examples (software/micropython/clock/boot.py etc), which use exactly
# this `(raw - 32768) / ...` centering.
ADC_CENTER = 32768
ADC_FULLSCALE_VOLTS = 5.0

def raw_to_volts(raw):
    return (raw - ADC_CENTER) / ADC_CENTER * ADC_FULLSCALE_VOLTS

RISING_THRESHOLD_V = 4.0    # "clock advance" trigger -- pulled in from the
FALLING_THRESHOLD_V = -4.0  # +/-5V ceiling/floor for reliable detection
DEAD_ZONE_V = 1.0           # -1V..+1V: re-arm triggers
TRIGGER_LENGTH_S = 0.005    # fixed output pulse width (5ms) -- tune to taste;
                             # most drum/envelope inputs are happy anywhere
                             # from ~1ms to ~10ms

# ---- hardware setup ----
cv_in = AnalogIn(board.A0)

GATE_PINS = [board.D1, board.D2, board.D3, board.D6, board.D10, board.D9, board.D8, board.D7]
outs = [digitalio.DigitalInOut(p) for p in GATE_PINS]
for out in outs:
    out.direction = digitalio.Direction.OUTPUT
    out.value = False

# ---- theka order: simplest first ----
THEKAS = sorted(
    REALIZED,
    key=lambda t: (t["beats"], t["complexity"], t["tal"], t["variant"]),
)

# Precompute a per-step boolean mask (one bool per output, in pin order) for
# every theka, once, at startup. This keeps the hot loop below to a flat,
# fixed-cost pass over 8 booleans instead of doing an "is channel N in this
# tuple" scan for each of the 8 outputs on every single loop iteration.
# That scan-per-output approach was adding avoidable per-loop latency, which
# stretches the apparent width of short input pulses on both edges.
ALL_OFF = (False,) * 8
for theka in THEKAS:
    theka["masks"] = [
        tuple((ch in active) for ch in range(1, 9))
        for active in theka["steps"]
    ]


def set_outputs(mask):
    for i in range(8):
        outs[i].value = mask[i]


# ---- state ----
theka_index = 0
step_index = 0
armed_rising = True
armed_falling = True
pulse_off_at = None  # time.monotonic() deadline for the current CLOCK trigger, or None if idle
theka_index_mask = ALL_OFF  # binary readout of theka_index, shown while v < FALLING_THRESHOLD_V

set_outputs(ALL_OFF)  # start silent; first clock pulse lights up step 0

while True:
    now = time.monotonic()
    volts = raw_to_volts(cv_in.value)

    # end the current CLOCK trigger once its fixed width has elapsed,
    # independent of whatever the input is doing at that moment. (Theka
    # select, below, isn't timed this way -- it follows the input level.)
    if pulse_off_at is not None and now >= pulse_off_at:
        set_outputs(ALL_OFF)
        pulse_off_at = None

    if volts > RISING_THRESHOLD_V:
        if armed_rising:
            armed_rising = False
            theka = THEKAS[theka_index]
            step_index = (step_index + 1) % len(theka["masks"])
            set_outputs(theka["masks"][step_index])
            pulse_off_at = now + TRIGGER_LENGTH_S
        armed_falling = True

    elif volts < FALLING_THRESHOLD_V:
        if armed_falling:
            armed_falling = False
            theka_index = (theka_index + 1) % len(THEKAS)
            step_index = 0
            theka_index_mask = tuple(((theka_index >> i) & 1) == 1 for i in range(8))
        armed_rising = True
        set_outputs(theka_index_mask)  # held for as long as v stays below threshold

    elif -DEAD_ZONE_V <= volts <= DEAD_ZONE_V:
        set_outputs(ALL_OFF)
        armed_rising = True
        armed_falling = True

    else:
        # between the dead zone and either trigger threshold -- no defined
        # behavior, stay off. Arm state holds steady (wide hysteresis band
        # so a slow-moving or noisy signal can't double-trigger).
        set_outputs(ALL_OFF)
