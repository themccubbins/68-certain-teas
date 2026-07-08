"""68 Certain Teas -- OAM Uncertainty firmware: steps through 68 tabla theka gate patterns.

Setup: copy this file plus realized_patterns.py to the root of CIRCUITPY.

Theka order is simplest-first (beat count, then bol complexity, then name
-- see realized_patterns.py) and cycles forward each time the CV input
goes low. The module boots into THEKAS[0].

CV input (bipolar, ~-5V to +5V) drives two one-shot triggers, each firing
a fixed TRIGGER_LENGTH_S pulse on the current step's channels regardless
of how long the input stays past its threshold -- gate-length-follower
behavior made triggers wider than the source pulse on real hardware, so
this fires clean and constant-width instead:

    v > RISING_THRESHOLD_V   -> advance one step, pulse its channels
    v < FALLING_THRESHOLD_V  -> advance to the next theka, reset to step 0, pulse
    -DEAD_ZONE_V..DEAD_ZONE_V -> re-arm both triggers
    (anywhere else: undefined, hold steady -- gives hysteresis headroom)

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
pulse_off_at = None  # time.monotonic() deadline for the current trigger, or None if idle

set_outputs(ALL_OFF)  # start silent; first clock pulse lights up step 0

while True:
    now = time.monotonic()
    volts = raw_to_volts(cv_in.value)

    # end the current trigger once its fixed width has elapsed, independent
    # of whatever the input is doing at that moment
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
            set_outputs(THEKAS[theka_index]["masks"][0])
            pulse_off_at = now + TRIGGER_LENGTH_S
        armed_rising = True

    elif -DEAD_ZONE_V <= volts <= DEAD_ZONE_V:
        armed_rising = True
        armed_falling = True

    # else: between the dead zone and either trigger threshold -- no
    # defined behavior, arm state just holds steady (wide hysteresis band
    # so a slow-moving or noisy signal can't double-trigger)
