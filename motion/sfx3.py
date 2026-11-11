"""Sound design for the testimonial video (v3.html / assets/depoimento_maria.m4a).
A soft, warm palette to match the light reference: gentle UI pops, check ticks,
clock ticking, airy swishes on layout changes, typing, a notification chime and
a mellow electric-piano music bed, all ducked under the voice.

Usage: python3 sfx3.py assets/depoimento_maria.m4a out.wav
"""
import sys
import wave

import numpy as np

import sfx
from sfx import SR, swish, whoosh, key_tick, pop, blip, shimmer, reverb, lp, hp, load_voice

sfx.DUR = 45.0
rng = np.random.default_rng(5)


def soft_pop(f=700, d=0.09):
    return pop(f, f * 0.55, d) * 0.8


def check_tick():
    t = np.arange(int(0.12 * SR)) / SR
    a = np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 40)
    b = np.sin(2 * np.pi * 1980 * t) * np.exp(-t * 55) * 0.5
    return (a + b) * 0.5


def clock_tick():
    n = int(0.025 * SR)
    t = np.arange(n) / SR
    s = hp(rng.standard_normal(n), 2500) * np.exp(-t * 380)
    s += np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 500) * 0.4
    return s / (np.abs(s).max() + 1e-9) * 0.4


def chime():
    t = np.arange(int(1.4 * SR)) / SR
    s = np.zeros_like(t)
    for f, d, g in [(1568, 0.0, 1), (2093, 0.09, .8)]:
        tt = np.clip(t - d, 0, None)
        s += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 4) * g * (t >= d)
        s += np.sin(2 * np.pi * f * 2.01 * tt) * np.exp(-tt * 7) * g * 0.25 * (t >= d)
    return s * 0.35


def epiano_music():
    n = int(sfx.DUR * SR)
    t = np.arange(n) / SR
    bpm = 84
    beat = 60 / bpm
    m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
    # Fmaj7 - Em7 - Dm7 - Cmaj7 (each bar)
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
    roots = [41, 40, 38, 36]
    out = np.zeros(n)
    bar = beat * 4

    def note(f, start, dur, g):
        i0 = int(start * SR)
        if i0 >= n:
            return
        L = min(int((dur + 1.2) * SR), n - i0)
        tt = np.arange(L) / SR
        env = np.exp(-tt * 1.6) * np.minimum(1, tt / 0.006)
        trem = 1 + 0.15 * np.sin(2 * np.pi * 4.5 * tt)
        s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 4)
             + 0.12 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt * 8))
        out[i0:i0 + L] += s * env * trem * g

    k = 0
    tb = 0.0
    while tb < sfx.DUR:
        c = chords[k % 4]
        for j, m in enumerate(c):
            note(m2f(m), tb + j * 0.012, bar, 0.09)
            note(m2f(m), tb + beat * 2.5 + j * 0.012, bar / 2, 0.05)
        note(m2f(roots[k % 4]), tb, bar, 0.22)
        note(m2f(roots[k % 4]), tb + beat * 2, bar / 2, 0.14)
        # light melody blips
        mel = c[3] + 12
        note(m2f(mel), tb + beat * 1.5, beat, 0.04)
        note(m2f(c[2] + 12), tb + beat * 3, beat, 0.035)
        tb += bar
        k += 1
    out = lp(out, 3500)
    # soft lofi drums from 3.3s
    drums = np.zeros(n)
    kt = np.arange(int(0.3 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(110 * (50 / 110) ** np.clip(kt / 0.1, 0, 1)) / SR) * np.exp(-kt * 12)
    snare = lp(hp(rng.standard_normal(int(0.2 * SR)), 1200), 6000) * np.exp(-np.arange(int(0.2 * SR)) / SR * 22) * 0.25
    shk = hp(rng.standard_normal(int(0.06 * SR)), 6000) * np.exp(-np.arange(int(0.06 * SR)) / SR * 60) * 0.08
    for b in range(int(sfx.DUR / beat)):
        bt = b * beat
        if bt < 3.3 or bt > 43.5:
            continue
        def put(sig, at, g):
            i = int(at * SR)
            if i < n:
                L = min(len(sig), n - i)
                drums[i:i + L] += sig[:L] * g
        if b % 4 in (0, 2):
            put(kick, bt, 0.45)
        if b % 4 in (1, 3):
            put(snare, bt, 0.6)
        put(shk, bt + beat / 2, 1)
        put(shk, bt, 0.6)
    mix = out + drums
    mix *= np.minimum(1, t / 1.0) * np.minimum(1, np.maximum(0, (sfx.DUR - t) / 1.6))
    return reverb(mix, 1.4, 0.3)


def build():
    n = int(sfx.DUR * SR)
    out = np.zeros(n)

    def add(sig, at, g=1.0):
        i = int(at * SR)
        if i >= n:
            return
        L = min(len(sig), n - i)
        out[i:i + L] += sig[:L] * g

    # intro
    add(soft_pop(600), 0.0, 0.5)
    add(whoosh(0.5, 400, 3000, 900), 0.0, 0.25)
    add(soft_pop(900), 0.5, 0.4)
    add(shimmer(1.0), 1.4, 0.18)
    for at in (0.3, 0.6, 0.9, 1.2):
        add(soft_pop(1100), at, 0.25)
    # layout morphs
    for at in (3.3, 9.35, 16.6, 20.0, 24.05, 27.95, 32.9, 37.45, 41.1):
        add(swish(0.45), at - 0.3, 0.32)
    # captions: soft pop when the emphasis box lands
    import json
    words = json.load(open('words3.json'))
    emph_first = [2, 10, 13, 17, 22, 28, 32, 34, 40, 42, 46, 51, 56, 59, 62, 67, 68, 70, 73]
    # (indices of the first emphasis word of each caption chunk, see SPEC in v3.html)
    for i in emph_first:
        if i < len(words):
            add(soft_pop(780, 0.1), words[i][0] - 0.05, 0.28)
    add(soft_pop(780, 0.1), 42.2, 0.28)
    # meters
    add(blip(900, 1300, .12), 4.0, 0.2)
    add(blip(900, 1300, .12), 20.3, 0.2)
    add(shimmer(0.9), 22.0, 0.15)
    # clock scene
    add(soft_pop(500, 0.14), 9.4, 0.45)
    tt = 9.6
    while tt < 16.4:
        rate = 1.0 if not (12.9 < tt < 15.3) else 0.09
        add(clock_tick(), tt, 0.5 if rate == 1.0 else 0.3)
        tt += rate
    add(soft_pop(900), 12.8, 0.35)
    # checklist
    add(soft_pop(600, 0.12), 16.5, 0.4)
    for at in (16.88, 17.4, 19.34):
        add(check_tick(), at, 0.5)
    # pain dial
    add(soft_pop(550, 0.12), 24.05, 0.4)
    add(soft_pop(800), 25.4, 0.3)
    add(blip(1400, 600, 1.2) * 0.4, 26.3, 0.35)
    add(chime(), 27.6, 0.35)
    # stickers
    for at in (28.3, 28.6, 30.2, 32.28, 33.1, 37.6, 37.7, 37.8, 37.9, 9.6, 9.8, 16.9, 20.4, 24.3):
        add(soft_pop(1000 + rng.uniform(-150, 150), 0.07), at, 0.22)
    add(shimmer(0.8), 30.2, 0.15)
    add(shimmer(0.8), 32.28, 0.15)
    # value cards
    for i in range(4):
        add(soft_pop(650 + i * 60, 0.1), 33.0 + i * 0.12, 0.3)
    for at in (33.72, 34.02, 34.42, 35.14):
        add(check_tick(), at, 0.45)
    # final
    for at in (37.66, 38.42, 39.6):
        add(soft_pop(900, 0.09), at, 0.35)
    add(shimmer(1.2), 38.42, 0.2)
    # outro typing + send + toast
    s = 'Agende sua avaliação'
    for i in range(len(s)):
        add(key_tick(), 41.6 + 1.3 * i / len(s), 0.8)
    add(soft_pop(700), 41.15, 0.35)
    add(sfx.click(), 43.2, 0.4)
    add(chime(), 43.4, 0.45)
    return reverb(out, 0.7, 0.18)


def main():
    voice = load_voice(sys.argv[1])
    voice = hp(voice, 90)
    # gentle compression
    env = np.sqrt(np.convolve(voice ** 2, np.ones(2400) / 2400, mode='same')) + 1e-6
    target = np.percentile(env[env > env.max() * 0.05], 80)
    gain = np.clip((target / env) ** 0.4, 0.6, 2.5)
    voice = voice * gain
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.92
    mus = epiano_music()
    fx = build()
    e = np.abs(voice)
    k = int(0.2 * SR)
    e = np.convolve(e, np.ones(k) / k, mode='same')
    duck = 1 - 0.6 * np.clip(e / (e.max() * 0.2), 0, 1)
    mus = mus / (np.abs(mus).max() + 1e-9) * 0.2 * duck
    fx = fx / (np.abs(fx).max() + 1e-9) * 0.42
    mix = voice + mus + fx
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    mix /= max(1.0, np.abs(mix).max() / 0.97)
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(sys.argv[2], 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('wrote', sys.argv[2])


if __name__ == '__main__':
    main()
