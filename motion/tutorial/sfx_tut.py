"""Sound design + music bed for the Claude Code tutorial (tutorial/index.html),
mixed under the ElevenLabs narration (tutorial/narracao.mp3).

Run from motion/:  python3 tutorial/sfx_tut.py tutorial/narracao.mp3 out.wav
"""
import sys
import wave

import numpy as np

import sfx
from sfx import SR, whoosh, swish, click, key_tick, pop, blip, boom, shimmer, riser, reverb, load_voice

DUR = 75.2
sfx.DUR = DUR


def typing(add, s, t0, t1, g=0.6):
    n = max(1, len(s))
    for i in range(n):
        add(key_tick(), t0 + (t1 - t0) * i / n, g)


def build():
    n = int(DUR * SR)
    out = np.zeros(n)

    def add(sig, at, g=1.0):
        i = int(at * SR)
        if i >= n:
            return
        L = min(len(sig), n - i)
        out[i:i + L] += sig[:L] * g

    # scene transitions
    for at in (8.1, 15.6, 25.55, 34.0, 42.55, 51.55, 59.5, 67.55):
        add(whoosh(0.6), at, 0.4)
    # headline swaps
    for at in (3.9, 22.4, 30.2):
        add(swish(0.35), at - 0.15, 0.3)
    # S1
    add(boom(1.4, 80, 40), 0.05, 0.5)
    add(pop(800, 400, 0.12), 0.1, 0.35)
    add(pop(900, 450, 0.12), 0.45, 0.35)
    typing(add, 'instala o Claude Code', 1.2, 2.9, 0.45)
    add(blip(1000, 1600, .12), 6.64, 0.3)
    add(blip(1200, 1900, .12), 7.66, 0.3)
    # S2 plans
    add(pop(700, 350, 0.12), 9.6, 0.35)
    add(pop(900, 500, 0.1), 11.83, 0.35)
    add(shimmer(0.8), 12.03, 0.2)
    add(pop(900, 500, 0.1), 12.55, 0.35)
    add(shimmer(0.8), 12.75, 0.2)
    add(pop(500, 250, 0.15), 13.27, 0.35)
    add(blip(700, 300, .25), 14.5, 0.3)
    # S3 install
    add(pop(800, 400, 0.1), 16.4, 0.3)
    typing(add, 'curl -fsSL https://claude.ai/install.sh | bash', 19.9, 21.5)
    add(click(), 21.72, 0.5)
    add(blip(1300, 2000, .15), 22.0, 0.35)
    add(click(), 22.44, 0.4)
    typing(add, 'irm https://claude.ai/install.ps1 | iex', 24.6, 25.6)
    # S4 claude + login
    typing(add, 'claude', 28.6, 29.3, 0.7)
    add(click(), 29.5, 0.45)
    add(shimmer(1.0), 29.6, 0.25)
    add(pop(700, 350, 0.12), 31.6, 0.35)
    add(click(), 33.1, 0.5)
    add(blip(1300, 2000, .15), 33.5, 0.35)
    # S5 demo
    add(pop(600, 300, 0.1), 37.4, 0.25)
    typing(add, 'organiza as notas fiscais desta pasta numa planilha', 38.3, 41.1)
    add(click(), 41.3, 0.45)
    add(riser(0.6), 41.3, 0.25)
    add(pop(800, 400, 0.15), 42.1, 0.45)
    add(shimmer(1.0), 42.2, 0.25)
    # S6 desktop
    add(pop(700, 350, 0.12), 44.3, 0.35)
    add(blip(1000, 1500, .12), 45.6, 0.3)
    add(blip(1300, 2000, .15), 49.0, 0.3)
    add(click(), 50.97, 0.5)
    # S7 phone
    add(pop(700, 350, 0.12), 52.0, 0.35)
    add(pop(1000, 600, 0.08), 54.25, 0.3)
    add(pop(1000, 600, 0.08), 55.6, 0.3)
    add(riser(0.8), 55.8, 0.2)
    add(blip(1300, 2000, .15), 56.7, 0.3)
    add(click(), 59.1, 0.5)
    # S8 remote control
    typing(add, '/remote-control', 61.5, 62.6, 0.6)
    add(click(), 62.8, 0.45)
    add(pop(900, 450, 0.1), 63.0, 0.35)
    add(pop(700, 350, 0.12), 63.6, 0.35)
    add(swish(0.4), 64.0, 0.3)
    add(blip(1100, 1700, .12), 65.6, 0.3)
    # S9 CTA
    add(boom(1.2, 90, 45), 68.0, 0.45)
    add(pop(800, 400, 0.12), 68.0, 0.35)
    add(click(), 69.33, 0.55)
    add(shimmer(1.4), 69.4, 0.3)
    add(pop(900, 450, 0.1), 72.5, 0.3)
    return reverb(out, 0.8, 0.18)


def main():
    v = load_voice(sys.argv[1])
    v = v / (np.abs(v).max() + 1e-9) * 0.9
    mus = sfx.music(active=((3.9, 67.5), (68.0, 74.0)), arp_on=(0.0, 74.5))
    e = np.convolve(np.abs(v), np.ones(int(0.2 * SR)) / (0.2 * SR), mode='same')
    duck = 1 - 0.55 * np.clip(e / (e.max() * 0.2), 0, 1)
    mus = mus / (np.abs(mus).max() + 1e-9) * 0.17 * duck
    fx = build()
    fx = fx / (np.abs(fx).max() + 1e-9) * 0.45
    mix = v + mus + fx
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
