# 68 Certain Teas (v2)

Indian tala rhythms from **five systems**, played back as gate/trigger
patterns on [OAM Uncertainty](https://oamodular.org/products/uncertainty),
a 2HP Eurorack module built around an RP2040. Now **168 patterns**
(the name is sentimental): the original 68 Hindustani thekas plus rare
tals, Tagore's invented meters, Odissi talas, and the Carnatic tala
systems -- including the 128-beat Simhanandana.

| System | Patterns | What it is |
| --- | --- | --- |
| Hindustani (digitabla) | 68 | the original v1 set: 38 tals, 68 thekas |
| Hindustani (KKSongs) | 23 | rare/pakhawaj/Bengali tals, incl. fractional-beat tals like 11.5-beat Dharami |
| Rabindrik | 14 | meters Tagore created for Rabindra Sangeet; all khali-less |
| Odissi | 9 | mardala talas of Odisha |
| Carnatic | 54 | all 35 suladi sapta talas, 4 chapu talas, 14 melakarta anga talas, Simhanandana (128 beats) |

## Channel layout (fixed, all patterns)

v1 reassigned channels per-theka; v2 uses one semantic layout so a patch
stays meaningful while you cycle patterns (a lesson from sibling project
[Errorz Barz](https://github.com/themccubbins/errorz-barz)):

| Ch | Meaning | Patch idea |
| --- | --- | --- |
| 1 | **Sam** -- first beat of the cycle | sequencer reset, one-shot |
| 2 | **Tali** -- clapped section markers | accents, S&H clock |
| 3 | **Khali** -- waved beats | anything "anti-accent" |
| 4 | **Bass voice** (baya / left hand) | kick |
| 5 | **Treble voice**, closed (na/ta/tin family) | snare, rim |
| 6 | **Open/resonant** (tun/din rings; Carnatic guru motions) | open hat |
| 7 | **Flourish** (tirakita runs; Carnatic finger counts) | ratchet, hat burst |
| 8 | **Vibhag/anga boundary** -- every section start | phrase clock, chord change |

Bols are decomposed into voice components (dha = bass + treble,
dhin = bass + ring, ...), so ch4 patched to a kick **drops out on khali
sections exactly like a tabla player's baya**. Channels 4-7 double as a
4-bit code: bol identity is recoverable from the combination. A pure
binary bol coding (index across ch4-7) is available as a build-time
flag (`BOL_CODING` in `gate_mapping.py`).

Carnatic talas have no strokes -- they are clap/wave/count gesture
structures and live on channels 1/2/3/6/7. Rabindrik taals never fire
ch3 (Tagore wrote no khali). Six structure-only Odissi talas play their
chhanda skeleton on the structural channels.

## What's here

| File | Purpose |
| --- | --- |
| `tala_patterns.py` | v1 Hindustani data (digitabla), unchanged |
| `kksongs_patterns.py` | rare Hindustani/Bengali tals (KKSongs Talamala) |
| `rabindrik_patterns.py` | Tagore taals (Geetabitan) |
| `odissi_patterns.py` | Odissi talas (Odissi Darpana, Wikipedia Mardala) |
| `carnatic_patterns.py` | suladi 35 + chapu + anga talas (generated from anga formulas) |
| `gate_mapping.py` | dev-time compiler: fixed channel layout, voice decomposition, self-tests; `--write` regenerates `realized_patterns.py` |
| `realized_patterns.py` | GENERATED flat bytes blob -- ships to the device |
| `code.py` | Uncertainty firmware -- ships to the device |

Only `code.py` and `realized_patterns.py` go on the CIRCUITPY drive.
The loader is the errorz-barz shape: one `bytes` blob, one byte per step
(bit = channel), per-pattern length table, offsets computed once at
boot, order baked at build time, NVM boot log + boot-attempt counter
for post-mortem debugging (see `code.py`'s docstring for how to read it).

## How it works

Same CV scheme as v1: a pulse above ~+4V clocks one step and fires a
5ms trigger on that step's channels; a pulse below ~-4V advances to the
next pattern and holds the pattern's index in binary on the LEDs (168 <=
256, so the index always fits). Patterns are 3 to 128 steps long. A few
fractional-matra tals (e.g. Dharami, 11.5 beats) are stored on a
half-beat grid -- clock them at 2x; they're flagged in
`realized_patterns.py`'s name list.

## Transcription honesty

Some sources print bols one syllable at a time with ambiguous
beat-grouping, and fractional-beat alignment occasionally required
judgment; entries carry a `note` where that happened. Chapu clap
conventions vary by school. The voice decomposition is deliberately
approximate -- it optimizes for consistent, musical gates, not
scholarship. Corrections welcome.

## Credits & thanks

**Rhythm data:**
[DigiTabla.com](https://digitabla.com/reference/tals-and-thekas/extended-list/)
(Chhotelal Misra, *Tal Prabandh*, Kanishka 2006) for the core 68;
[KKSongs Talamala](http://kksongs.org/talamala.html) for the rare tals;
[Geetabitan.com](https://www.geetabitan.com/taal/index.html) for the
Rabindrik taals; [Odissi Darpana](https://nrutyayanaodissi.wordpress.com/)
and Wikipedia's [Mardala](https://en.wikipedia.org/wiki/Mardala) article
for Odissi; Wikipedia's [Tala (music)](https://en.wikipedia.org/wiki/Tala_(music))
for the suladi system, anga definitions, melakarta tala table and
Simhanandana. All credit for the musical content belongs to those
sources and traditions.

**The idea** started from [Seaside Modular's Tala](https://github.com/abluenautilus/SeasideModularVCV)
for VCV Rack; the firmware shape and diagnostics come from
[Errorz Barz](https://github.com/themccubbins/errorz-barz).

**The hardware/platform** is [OAM Uncertainty](https://oamodular.org/products/uncertainty)
by Olivia Artz Modular (hardware/firmware CC BY-SA 4.0; logo/branding
reserved, not used here). This project targets Uncertainty's documented
pinout and I/O behavior and is original code, not a derivative of OAM's
firmware.

**Built by** Claude (Sonnet & Fable), AI models by Anthropic, working
with cubbs.

## License

MIT for the code and data structures (see `LICENSE`). The tala data
itself is transcription of traditional/reference material and isn't
original creative work. On Uncertainty's CC BY-SA firmware: this
project's code was written from scratch against OAM's public
documentation -- read their license and draw your own conclusions before
wide redistribution. Not legal advice.
