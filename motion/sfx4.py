"""Audio for the calm/static testimonial (v4.html): the voice (delayed 0.8 s to match
the fade-in), a soft electric-piano bed ducked under it, and a gentle chime at the
start and end. Usage: python3 sfx4.py assets/depoimento_maria.m4a out.wav
"""
import sys
import wave

import numpy as np

import sfx
import sfx3
from sfx import SR, hp, load_voice

DUR = 43.8
T0 = 0.8
sfx.DUR = DUR


def main():
    v = load_voice(sys.argv[1])
    v = hp(v, 90)
    env = np.sqrt(np.convolve(v ** 2, np.ones(2400) / 2400, mode='same')) + 1e-6
    target = np.percentile(env[env > env.max() * 0.05], 80)
    v = v * np.clip((target / env) ** 0.4, 0.6, 2.5)
    v = v / (np.abs(v).max() + 1e-9) * 0.92
    n = int(DUR * SR)
    voice = np.zeros(n)
    i0 = int(T0 * SR)
    voice[i0:] = v[: n - i0]

    mus = sfx3.epiano_music()[:n]
    e = np.convolve(np.abs(voice), np.ones(int(0.2 * SR)) / (0.2 * SR), mode='same')
    duck = 1 - 0.55 * np.clip(e / (e.max() * 0.2), 0, 1)
    mus = mus / (np.abs(mus).max() + 1e-9) * 0.17 * duck

    fx = np.zeros(n)
    for at, g in ((0.15, 0.5), (DUR - 1.4, 0.4)):
        c = sfx3.chime()
        j = int(at * SR)
        L = min(len(c), n - j)
        fx[j:j + L] += c[:L] * g

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
