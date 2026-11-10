"""Synthesizes the sound design (whooshes, clicks, typing, pops, risers, impacts,
shimmer) plus an ambient tech music bed, then mixes it under the voice-over.
Everything is generated procedurally, so there are no third-party audio assets.

Usage: python3 sfx.py assets/voz.mp3 out.wav
"""
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 49.4
rng = np.random.default_rng(42)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def env_ad(n, a, d_curve=4.0):
    x = np.linspace(0, 1, n)
    ai = max(1, int(n * a))
    e = np.ones(n)
    e[:ai] = np.linspace(0, 1, ai) ** 2
    e[ai:] = np.exp(-d_curve * np.linspace(0, 1, n - ai))
    return e


def bp(sig, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, sig)


def lp(sig, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), sig)


def hp(sig, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), sig)


def swept_noise(d, f0, f1, f2=None, q=0.9):
    """Noise through a band-pass whose centre sweeps f0->f1(->f2), block-wise."""
    n = int(d * SR)
    noise = rng.standard_normal(n + 4096)
    out = np.zeros(n)
    blk = 512
    for i in range(0, n, blk):
        x = i / n
        if f2 is None:
            fc = f0 * (f1 / f0) ** x
        else:
            fc = f0 * (f1 / f0) ** (x * 2) if x < .5 else f1 * (f2 / f1) ** ((x - .5) * 2)
        lo, hi = fc * (1 - q / 2), min(fc * (1 + q / 2), SR / 2 - 100)
        seg = bp(noise[i:i + blk + 2048], max(lo, 30), hi)[2048:2048 + blk]
        out[i:i + blk] = seg[: len(out[i:i + blk])]
    return out


def whoosh(d=0.7, f0=250, f1=3800, f2=700):
    s = swept_noise(d, f0, f1, f2, q=1.1)
    n = len(s)
    x = np.linspace(0, 1, n)
    e = np.sin(np.pi * x ** 0.8) ** 2
    return s * e / (np.abs(s).max() + 1e-9)


def swish(d=0.32):
    return whoosh(d, 1500, 7000, 3000) * 0.7


def click():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 180)
    body = np.sin(2 * np.pi * 900 * t) * np.exp(-t * 90) * 0.5
    nz = hp(rng.standard_normal(n), 3000) * np.exp(-t * 600) * 0.6
    return (tone + body + nz) * 0.8


def key_tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    f = rng.uniform(1800, 3200)
    s = bp(rng.standard_normal(n), f * .7, f * 1.3) * np.exp(-t * 260)
    s += np.sin(2 * np.pi * f * .5 * t) * np.exp(-t * 300) * 0.3
    return s / (np.abs(s).max() + 1e-9) * 0.35


def pop(f0=900, f1=420, d=0.12):
    t = t_axis(d)
    f = f0 * (f1 / f0) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 28) * 0.7


def blip(f0=1200, f1=1900, d=0.09):
    t = t_axis(d)
    f = f0 + (f1 - f0) * t / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.sin(np.pi * t / d) * 0.5


def boom(d=2.2, f0=70, f1=34):
    t = t_axis(d)
    f = f0 * (f1 / f0) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 2.2)
    thump = lp(rng.standard_normal(len(t)), 180) * np.exp(-t * 14) * 3
    s = sub + thump
    return np.tanh(s * 1.4) * 0.9


def shimmer(d=1.8, n_part=14):
    t = t_axis(d)
    s = np.zeros_like(t)
    for _ in range(n_part):
        f = rng.uniform(2500, 9000)
        trem = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(5, 14) * t + rng.uniform(0, 6))
        s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * trem
    s *= np.exp(-t * 2.2) * np.minimum(1, t / 0.02)
    return s / (np.abs(s).max() + 1e-9) * 0.35


def riser(d=1.4):
    t = t_axis(d)
    nz = swept_noise(d, 300, 6000, q=0.8)
    nz /= np.abs(nz).max() + 1e-9
    f = 180 * (1400 / 180) ** (t / d)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
    tone += np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.15
    e = (t / d) ** 2.2
    return (nz * .8 + tone) * e


def hum_sweep(d=2.5):
    t = t_axis(d)
    s = np.sin(2 * np.pi * 110 * t) * 0.4 + np.sin(2 * np.pi * 165 * t) * 0.2
    s *= np.sin(np.pi * t / d) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 2.3 * t))
    return s * 0.4


def reverb(sig, secs=1.1, wet=0.25):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = lp(ir, 6000)
    ir /= np.sqrt((ir ** 2).sum())
    w = fftconvolve(sig, ir)[: len(sig)]
    return sig * (1 - wet) + w * wet * 2.2


# ---------------------------------------------------------------- music bed
def music():
    n = int(DUR * SR)
    t = np.arange(n) / SR
    bpm = 100
    beat = 60 / bpm
    bar = beat * 4
    # Am - F - C - G (each 2 bars)
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
    roots = [45, 41, 48, 43]
    m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
    pad = np.zeros(n)
    bass = np.zeros(n)
    arp = np.zeros(n)
    seg = bar * 2
    for ci in range(int(DUR / seg) + 1):
        c = chords[ci % 4]
        t0 = ci * seg
        i0, i1 = int(t0 * SR), min(n, int((t0 + seg + 0.6) * SR))
        if i0 >= n:
            break
        tt = t[i0:i1] - t0
        e = np.minimum(1, tt / 0.8) * np.minimum(1, np.maximum(0, (seg + 0.6 - tt) / 0.8))
        chunk = np.zeros(i1 - i0)
        for m in c:
            for det in (-0.08, 0.0, 0.08):
                f = m2f(m + det)
                chunk += ((tt * f) % 1.0 * 2 - 1) * 0.06
        pad[i0:i1] += chunk * e
        f = m2f(roots[ci % 4] - 12)
        bass[i0:i1] += np.sin(2 * np.pi * f * tt) * e * 0.5
        # 16th arpeggio
        for k in range(int(seg / (beat / 2))):
            nt = t0 + k * beat / 2
            j0 = int(nt * SR)
            if j0 >= n:
                break
            note = c[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
            L = min(int(0.35 * SR), n - j0)
            tl = np.arange(L) / SR
            fr = m2f(note)
            arp[j0:j0 + L] += (np.sin(2 * np.pi * fr * tl) + 0.3 * np.sin(4 * np.pi * fr * tl)) * np.exp(-tl * 11) * 0.18
    pad = lp(pad, 1400)
    # drums: soft kick + hats, with breaks
    drums = np.zeros(n)
    kick_t = t_axis(0.35)
    kick = np.sin(2 * np.pi * np.cumsum(150 * (45 / 150) ** (kick_t / 0.12).clip(0, 1)) / SR) * np.exp(-kick_t * 9)
    hat = hp(rng.standard_normal(int(0.05 * SR)), 7000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90) * 0.18
    for k in range(int(DUR / beat)):
        bt = k * beat
        active = (3.3 <= bt < 38.9) or (42.28 <= bt < 48.2)
        if not active:
            continue
        j = int(bt * SR)
        L = min(len(kick), n - j)
        drums[j:j + L] += kick[:L] * 0.55
        jh = int((bt + beat / 2) * SR)
        if jh < n:
            L = min(len(hat), n - jh)
            drums[jh:jh + L] += hat[:L]
    arp_gate = np.where((t > 10.5) & (t < 48.5), 1.0, 0.25)
    mix = pad * 0.9 + bass * 0.35 + arp * arp_gate + drums
    mix *= np.minimum(1, t / 1.2) * np.minimum(1, np.maximum(0, (DUR - t) / 1.5))
    return reverb(mix, 1.6, 0.25)


# ---------------------------------------------------------------- timeline
def build_sfx():
    n = int(DUR * SR)
    out = np.zeros(n)

    def add(sig, at, gain=1.0):
        i = int(at * SR)
        if i >= n or i + len(sig) <= 0:
            return
        j0 = max(0, -i)
        L = min(len(sig) - j0, n - max(i, 0))
        out[max(i, 0):max(i, 0) + L] += sig[j0:j0 + L] * gain

    # S1 tiles pop in
    for k, d in enumerate([0, 1, 1, 1, 1, 1.41, 1.41, 1.41, 1.41]):
        add(pop(1100 + k * 40, 600, 0.08), 0.05 + d * 0.12 + k * 0.004, 0.18)
    add(blip(1300, 2100), 2.36, 0.35)          # likes badge
    # transitions
    for at, g, d in [(3.05, .55, .75), (10.05, .5, .6), (13.0, .5, .7), (16.8, .55, .75), (23.1, .55, .8),
                     (25.75, .4, .6), (30.25, .5, .7), (34.75, .5, .75), (38.75, .55, .8), (44.75, .35, .6)]:
        add(whoosh(d), at, g)
    # S2 typing
    f1s, f2s = 'Sua Empresa', 'www.suaempresa.com.br'
    for i in range(len(f1s)):
        add(key_tick(), 3.55 + 0.8 * i / len(f1s), 0.9)
    for i in range(len(f2s)):
        add(key_tick(), 4.5 + 0.95 * i / len(f2s), 0.9)
    add(pop(700, 350, 0.1), 9.95, 0.35)
    add(shimmer(1.0), 10.0, 0.35)
    # clicks
    for at in [2.02, 6.04, 7.6, 9.08, 9.72, 45.66]:
        add(click(), at - 0.01, 0.55)
    for at in [6.06, 7.62, 9.1]:
        add(blip(900, 1500, .08), at, 0.25)
    # S3 light band
    add(boom(1.8, 80, 38), 10.5, 0.75)
    add(shimmer(1.4), 10.52, 0.35)
    for at in [11.0, 11.62]:
        add(swish(), at - 0.05, 0.45)
    add(swish(.4), 12.38, 0.5)
    add(pop(500, 220, 0.25), 12.45, 0.4)
    # S4 radar + chat
    add(hum_sweep(3.6), 13.3, 0.5)
    add(blip(1500, 1100), 13.5, 0.35)
    add(blip(1100, 1600), 14.25, 0.35)
    for i in range(7):
        add(key_tick(), 14.4 + i * 0.22, 0.4)
    # S5 big text swaps
    for at in [17.6, 18.28, 20.8]:
        add(swish(.38), at - 0.05, 0.5)
    add(boom(0.9, 90, 50), 20.82, 0.3)
    # S6a calendar cards
    for i in range(10):
        add(pop(1200 + (i % 3) * 120, 700, 0.07), 23.75 + i * 0.13, 0.17)
    add(blip(1000, 1700), 25.25, 0.35)
    # S6b
    add(pop(800, 400, 0.12), 26.2, 0.3)
    add(swish(.45), 27.4, 0.35)
    add(blip(1400, 2200, .14), 28.15, 0.3)
    add(pop(900, 450, 0.14), 28.7, 0.35)
    add(shimmer(1.2), 29.68, 0.3)
    # S7 connections
    add(boom(0.8, 110, 60), 30.86, 0.35)
    add(shimmer(.8), 30.86, 0.25)
    add(pop(600, 250, 0.2), 31.6, 0.4)
    for at in [32.0, 33.14, 34.22]:
        add(blip(1300, 2000, .1), at - 0.2, 0.3)
        add(pop(1000, 500, 0.1), at, 0.35)
    # S8a tiles
    for k in range(9):
        add(pop(1400, 900, 0.05), 35.1 + k * 0.08, 0.12)
    for k in range(6):
        add(key_tick(), 37.25 + k * 0.14, 0.5)
    add(shimmer(1.5), 38.2, 0.4)
    add(boom(1.0, 95, 50), 38.22, 0.35)
    # S8b list
    add(blip(1200, 1600), 39.12, 0.28)
    add(blip(1200, 1600), 39.5, 0.28)
    add(pop(800, 420, 0.13), 40.3, 0.4)
    add(swish(.3), 40.8, 0.25)
    add(swish(.3), 41.0, 0.25)
    # logo
    add(riser(1.5), 40.8, 0.55)
    add(boom(2.6, 70, 32), 42.26, 0.95)
    add(shimmer(2.2, 20), 42.3, 0.5)
    add(swish(.5), 42.65, 0.35)
    add(shimmer(1.4), 46.2, 0.22)
    # CTA
    add(pop(700, 380, 0.15), 45.15, 0.4)
    return reverb(out, 0.9, 0.2)


def load_voice(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    v = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    out = np.zeros(int(DUR * SR))
    out[: min(len(v), len(out))] = v[: len(out)]
    return out


def main():
    voice = load_voice(sys.argv[1])
    mus = music()
    fx = build_sfx()
    # sidechain duck music under the voice
    env = np.abs(voice)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode='same')
    duck = 1 - 0.55 * np.clip(env / (env.max() * 0.25), 0, 1)
    mus = mus / (np.abs(mus).max() + 1e-9) * 0.22 * duck
    fx = fx / (np.abs(fx).max() + 1e-9) * 0.55
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.9
    mix = voice + mus + fx
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    mix /= max(1.0, np.abs(mix).max() / 0.97)
    stereo = np.stack([mix, mix], 1)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(sys.argv[2], 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('wrote', sys.argv[2])


if __name__ == '__main__':
    main()
