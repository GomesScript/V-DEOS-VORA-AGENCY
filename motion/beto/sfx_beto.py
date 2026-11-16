"""Cartoon sound design + bouncy music bed for 'A Vida do Beto' EP1.
Run from motion/:  PYTHONPATH=. python3 beto/sfx_beto.py beto/narracao.mp3 out.wav
"""
import sys
import wave

import numpy as np

import sfx
from sfx import SR, whoosh, swish, click, key_tick, pop, blip, shimmer, reverb, lp, hp, load_voice

DUR = 51.2
sfx.DUR = DUR
rng = np.random.default_rng(8)


def tone(f, d, decay=6.0, harm=(1, .4, .2)):
    t = np.arange(int(d * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm))
    return s * np.exp(-t * decay) * np.minimum(1, t / .004)


def boing(f0=180, f1=520, d=.35):
    t = np.arange(int(d * SR)) / SR
    f = f0 + (f1 - f0) * (1 - np.exp(-t * 18)) + 40 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * .8


def coin():
    a = tone(988, .09, 30, (1, .3))
    b = tone(1319, .45, 7, (1, .3, .1))
    out = np.zeros(int(.55 * SR))
    out[:len(a)] += a
    i = int(.07 * SR)
    out[i:i + len(b)] += b[:len(out) - i]
    return out * .6


def cha_ching():
    out = np.zeros(int(1.0 * SR))
    for k, f in enumerate((1568, 2093, 2637)):
        s = tone(f, .7, 5, (1, .25))
        i = int(k * .06 * SR)
        out[i:i + len(s)] += s[:len(out) - i] * .5
    n = hp(rng.standard_normal(int(.12 * SR)), 3000) * np.exp(-np.arange(int(.12 * SR)) / SR * 40) * .4
    out[:len(n)] += n
    return out


def plim():
    return (tone(1760, .5, 8, (1, .2)) + np.pad(tone(2349, .45, 9, (1, .2)), (int(.08 * SR), 0))[:int(.5 * SR)]) * .45


def harp():
    out = np.zeros(int(1.4 * SR))
    for k, m in enumerate((72, 76, 79, 84, 88)):
        f = 440 * 2 ** ((m - 69) / 12)
        s = tone(f, 1.0, 4, (1, .3, .1))
        i = int(k * .07 * SR)
        out[i:i + len(s)] += s[:len(out) - i] * .3
    return out


def devil():
    out = np.zeros(int(1.2 * SR))
    for k, m in enumerate((45, 44)):
        f = 440 * 2 ** ((m - 69) / 12)
        t = np.arange(int(.55 * SR)) / SR
        s = np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 3) * .25
        s = lp(s, 1200)
        i = int(k * .5 * SR)
        out[i:i + len(s)] += s
    return out


def drumroll(d=1.0):
    t = np.arange(int(d * SR)) / SR
    n = lp(hp(rng.standard_normal(len(t)), 300), 4000)
    am = .5 + .5 * np.sign(np.sin(2 * np.pi * 22 * t))
    return n * am * np.minimum(1, t / d) ** 1.5 * .35


def music():
    n = int(DUR * SR)
    out = np.zeros(n)
    bpm = 112
    beat = 60 / bpm
    m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
    chords = [[60, 64, 67], [57, 60, 64], [65, 69, 72], [67, 71, 74]]  # C Am F G
    roots = [48, 45, 41, 43]
    patt = [0, 2, 1, 2, 0, 2, 1, 2]
    for b in range(int(DUR / beat) * 2):
        tb = b * beat / 2
        bar = int(b // 8)
        c = chords[bar % 4]
        f = m2f(c[patt[b % 8]] + 12)
        s = tone(f, .35, 9, (1, .5, .15)) * .16
        i = int(tb * SR)
        if i >= n:
            break
        L = min(len(s), n - i)
        out[i:i + L] += s[:L]
        if b % 2 == 0:
            bs = tone(m2f(roots[bar % 4]), beat * .9, 5, (1, .3)) * (.3 if b % 4 == 0 else .18)
            L = min(len(bs), n - i)
            out[i:i + L] += bs[:L]
        if b % 4 == 2:  # clap
            cl = hp(rng.standard_normal(int(.08 * SR)), 1500) * np.exp(-np.arange(int(.08 * SR)) / SR * 45) * .18
            L = min(len(cl), n - i)
            out[i:i + L] += cl[:L]
    # duck the music a lot during the 'choice' tension (37.4-38.3) for the drumroll
    t = np.arange(n) / SR
    out *= np.where((t > 37.3) & (t < 38.3), .3, 1.0)
    out *= np.minimum(1, t / .8) * np.minimum(1, np.maximum(0, (DUR - t) / 1.2))
    return reverb(out, .8, .15)


def build():
    n = int(DUR * SR)
    out = np.zeros(n)

    def add(sig, at, g=1.0):
        i = int(at * SR)
        if i >= n:
            return
        L = min(len(sig), n - i)
        out[i:i + L] += sig[:L] * g

    for at in (2.55, 9.45, 17.85, 29.05, 37.45):  # scene changes
        add(whoosh(.5, 500, 4000, 1200), at - .25, .35)
    add(pop(900, 400, .12), 0.05, .4)
    add(boing(), 0.7, .5)
    add(shimmer(.9), 0.9, .2)
    add(pop(800, 380, .12), 2.6, .4)
    add(boing(220, 640, .3), 3.7, .4)
    add(blip(700, 400, .2), 7.1, .3)
    add(pop(700, 350, .12), 9.55, .35)
    for at in (11.6, 13.05, 15.39):
        add(plim(), at - .05, .5)
    add(blip(600, 300, .25), 11.65, .25)
    add(boing(160, 420, .35), 17.95, .4)
    for k in range(5):
        add(coin(), 19.0 + k * .12, .35)
    add(cha_ching(), 21.8, .6)
    add(shimmer(1.0), 21.9, .25)
    add(swish(.3), 24.6, .35)
    add(blip(800, 500, .2), 24.73, .3)
    add(pop(1000, 600, .1), 27.9, .35)
    add(sfx.boom(.9, 90, 50), 30.0, .5)
    add(harp(), 32.5, .6)
    add(pop(900, 450, .1), 33.6, .3)
    add(devil(), 35.2, .6)
    add(pop(900, 450, .1), 36.1, .3)
    add(drumroll(.9), 36.6, .7)
    add(sfx.boom(.6, 120, 60), 37.5, .45)
    add(boing(260, 700, .3), 38.3, .45)
    add(boing(200, 560, .3), 41.35, .45)
    add(plim(), 45.65, .5)
    t = 46.5
    while t < DUR - .5:
        add(key_tick(), t, .25)
        t += .5
    return reverb(out, .6, .12)


def main():
    v = load_voice(sys.argv[1])
    v = v / (np.abs(v).max() + 1e-9) * .9
    mus = music()
    e = np.convolve(np.abs(v), np.ones(int(.2 * SR)) / (.2 * SR), mode='same')
    duck = 1 - .5 * np.clip(e / (e.max() * .2), 0, 1)
    mus = mus / (np.abs(mus).max() + 1e-9) * .18 * duck
    fx = build()
    fx = fx / (np.abs(fx).max() + 1e-9) * .5
    mix = v + mus + fx
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    mix /= max(1.0, np.abs(mix).max() / .97)
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(sys.argv[2], 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('wrote', sys.argv[2])


if __name__ == '__main__':
    main()
