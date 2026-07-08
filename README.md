# 68 Certain Teas

North Indian tabla theka rhythms, played back as gate/trigger patterns on
[OAM Uncertainty](https://oamodular.org/products/uncertainty), a 2HP
Eurorack module built around an RP2040. 68 thekas across 38 tals, each
mapped onto Uncertainty's 8 gate outputs and stepped by an external clock.

## What's here

| File | Purpose |
|---|---|
| `tala_patterns.py` | Raw tal/theka rhythm data (bols + accent structure) |
| `gate_mapping.py` | Dev-time tool: assigns each theka's bols to gate channels |
| `realized_patterns.py` | Precomputed patterns -- ships to the device |
| `code.py` | Uncertainty firmware -- ships to the device |

`tala_patterns.py` and `gate_mapping.py` are the "build" side and never
run on the module itself; `realized_patterns.py` and `code.py` are the
only two files that need to be copied onto Uncertainty's CIRCUITPY drive.
See the docstrings in each file for the details of the data model and
channel-assignment rules.

## How it works, briefly

The module boots into the simplest theka (fewest beats, then fewest
distinct bols). A clock/gate above roughly +4V fires a short fixed-width
trigger on the current step's outputs and advances to the next step. A
pulse below roughly -4V advances to the next theka (simplest to most
complex, wrapping around), resets to its first step, and -- as long as
the input stays below that threshold -- displays the new theka's index
in binary across all 8 outputs (channel 1 = least significant bit,
channel 8 = most significant), so the LEDs count up as you cycle
through thekas. Since these are the same 8 gate outputs the drums are
patched into, the binary countup doubles as a bonus rhythmic pattern in
its own right.

## License

This project -- `tala_patterns.py`, `gate_mapping.py`,
`realized_patterns.py`, and `code.py` -- is released under the MIT
License (see `LICENSE`). The tabla rhythm data itself is a transcription
of reference material and isn't original creative work, but the code,
data structures, and the specific arrangement/mapping onto Uncertainty's
hardware are.

## Credits & thanks

**Rhythm data** is transcribed from [DigiTabla.com](https://digitabla.com/reference/tals-and-thekas/extended-list/),
"Extended List of North Indian Tals and Thekas," which in turn cites
Chhotelal Misra's *Tal Prabandh* (Kanishka Publishers, 2006). All credit
for the actual musical content belongs there -- go read the site, it's a
genuinely good resource on tabla.

**The idea** started from poking around [Seaside Modular's Tala](https://github.com/abluenautilus/SeasideModularVCV)
module for VCV Rack, an MIT-licensed sample-based tabla machine. Its
bundled 9-theka set was the seed for this project before it grew into the
full 68-theka version above. Tala's own tabla samples are credited there
to the [Naad project](https://github.com/oormicreations/naad) (also
MIT) -- not used here, since this project only borrows rhythm data, never
audio.

**The hardware/platform** is [OAM Uncertainty](https://oamodular.org/products/uncertainty)
by Olivia Artz Modular, an open-source gate-processor/scripting platform
for Eurorack. Uncertainty's hardware and official firmware are licensed
CC BY-SA 4.0; its logo and branding are copyrighted separately and
reserved (not used here). This project targets Uncertainty's documented
pinout and I/O behavior but is original code written for it, not a
derivative of OAM's own firmware.

**Built by** Claude (Sonnet), an AI model by Anthropic, working with
cubbs.

## A note on licensing, for what it's worth

I'm not a lawyer, and this isn't legal advice. Uncertainty's own firmware
is CC BY-SA, a share-alike license that can carry expectations for
derivative works. This project's code was written from scratch against
Uncertainty's public pinout/I/O documentation rather than by copying or
modifying OAM's firmware, which is the basis for releasing it separately
under MIT -- but if you plan to distribute this widely, it's worth
reading OAM's license yourself and drawing your own conclusion.
