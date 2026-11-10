"""Sound design timeline for the second video (v2.html / assets/voz2.mp3).
Reuses the synth voices from sfx.py.

Usage: python3 sfx2.py assets/voz2.mp3 out.wav
"""
import numpy as np

import sfx
from sfx import whoosh, swish, click, key_tick, pop, blip, boom, shimmer, riser, hum_sweep, reverb, SR

sfx.DUR = 53.4


def build():
    n = int(sfx.DUR * SR)
    out = np.zeros(n)

    def add(sig, at, gain=1.0):
        i = int(at * SR)
        if i >= n:
            return
        L = min(len(sig), n - i)
        out[i:i + L] += sig[:L] * gain

    # A scoreboard
    add(pop(900, 450, 0.14), 0.02, 0.45)
    add(blip(1200, 2200, .2), 0.38, 0.4)
    add(pop(700, 300, 0.16), 1.2, 0.4)
    add(blip(900, 400, .25), 1.72, 0.4)
    # transitions
    for at, g, d in [(2.3, .5, .6), (6.75, .5, .7), (10.6, .55, .75), (14.1, .5, .7), (19.8, .55, .8),
                     (25.95, .55, .7), (27.65, .4, .5), (29.85, .45, .6), (32.75, .5, .7), (38.85, .5, .7),
                     (44.6, .5, .75)]:
        add(whoosh(d), at, g)
    # B seesaw band
    add(boom(1.6, 80, 38), 2.62, 0.6)
    add(shimmer(1.2), 2.65, 0.3)
    add(swish(), 4.85, 0.45)
    add(blip(1000, 1900, .2), 4.95, 0.3)
    add(swish(), 5.75, 0.45)
    add(blip(1500, 600, .25), 5.85, 0.3)
    # C radar chat
    add(hum_sweep(3.8), 7.0, 0.5)
    add(blip(1500, 1100), 7.1, 0.35)
    add(blip(1100, 1600), 9.42, 0.35)
    for at in (9.58, 9.96, 10.16):
        add(key_tick(), at, 0.5)
    # D chart
    add(pop(800, 420, 0.12), 10.95, 0.35)
    add(sfx.riser(2.1) * 0.5, 11.3, 0.5)
    add(shimmer(1.0), 13.34, 0.35)
    # E tiles filling
    for k in range(9):
        add(pop(1400, 900, 0.05), 14.45 + k * 0.06, 0.12)
    rng = np.random.default_rng(3)
    for at in np.sort(rng.uniform(15.2, 19.5, 26)):
        add(blip(rng.uniform(1300, 2200), rng.uniform(1600, 2600), .06), at, 0.13)
    for at in (16.0, 17.45, 19.3):
        add(pop(1000, 500, 0.1), at, 0.35)
    # F diagnosis
    add(pop(800, 420, 0.12), 20.15, 0.3)
    for at in (22.2, 23.34, 25.24):
        add(click(), at - 0.01, 0.55)
    add(blip(1200, 1800, .1), 22.22, 0.3)
    add(blip(1200, 1800, .1), 23.36, 0.3)
    add(blip(900, 600, .2), 25.26, 0.35)
    add(boom(0.8, 100, 55), 25.24, 0.3)
    # G globe
    add(shimmer(1.4), 26.3, 0.3)
    for k in range(3):
        add(blip(1800, 1800, .08), 26.8 + k * 0.9, 0.22)
    # H band with logo
    add(boom(1.8, 80, 38), 27.95, 0.7)
    add(shimmer(1.4), 27.98, 0.3)
    add(swish(), 28.75, 0.45)
    add(swish(.4), 29.27, 0.5)
    add(pop(500, 220, 0.25), 29.32, 0.45)
    # I form
    for i in range(11):
        add(key_tick(), 30.3 + 0.65 * i / 11, 0.9)
    for at in (31.16, 31.5, 31.75, 31.96):
        add(blip(900, 1500, .08), at, 0.28)
    add(click(), 32.31, 0.55)
    add(pop(700, 350, 0.1), 32.5, 0.35)
    add(shimmer(1.0), 32.6, 0.3)
    # J services
    for at in (33.08, 34.52, 35.72, 37.12):
        add(swish(.38), at - 0.05, 0.5)
    add(boom(0.9, 90, 50), 35.72, 0.25)
    add(boom(0.9, 90, 50), 37.12, 0.25)
    # K hub
    add(boom(0.8, 110, 60), 39.42, 0.35)
    add(shimmer(.8), 39.42, 0.25)
    add(pop(600, 250, 0.2), 40.05, 0.4)
    for at in (40.94, 42.18, 43.38):
        add(blip(1300, 2000, .1), at - 0.2, 0.3)
        add(pop(1000, 500, 0.1), at, 0.35)
    # L forgotten
    for k in range(3):
        add(blip(1200, 1600), 45.0 + k * 0.28, 0.25)
    add(pop(800, 400, 0.12), 46.5, 0.3)
    add(swish(.3), 46.95, 0.3)
    for k in range(3):
        add(blip(900, 500, .15), 47.1 + k * 0.12, 0.2)
        add(swish(.35), 47.6 + k * 0.18, 0.25)
    # M logo
    add(riser(1.6), 47.2, 0.55)
    add(boom(2.6, 70, 32), 48.8, 0.95)
    add(shimmer(2.2, 20), 48.85, 0.5)
    add(swish(.5), 49.1, 0.35)
    add(shimmer(1.4), 51.9, 0.25)
    return reverb(out, 0.9, 0.2)


if __name__ == '__main__':
    sfx.main(build=build, music_kw={'active': ((2.6, 47.0), (48.8, 52.6)), 'arp_on': (7.0, 52.6)})
