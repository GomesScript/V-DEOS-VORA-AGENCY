"""Audio for the edited visit video (v5.html): the clip's own audio cleaned up
(high-pass, light denoise, loudness normalisation), a soft electric-piano bed
ducked under the dialogue, and the same gentle UI sound design as the reference
(pops, check ticks, clock ticks, swishes, typing, chime).

Usage: python3 sfx5.py assets/visita_original.mp4 out.wav
"""
import subprocess
import sys
import wave

import numpy as np

import sfx
import sfx3
from sfx import SR, swish, key_tick, blip, shimmer, reverb

DUR = 20.36
sfx.DUR = DUR


def clean_voice(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-vn',
                          '-af', 'highpass=f=80,afftdn=nr=10:nf=-40,loudnorm=I=-16:TP=-1.5:LRA=9',
                          '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    v = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    out = np.zeros(int(DUR * SR))
    out[:min(len(v), len(out))] = v[:len(out)]
    return out


def build():
    n = int(DUR * SR)
    out = np.zeros(n)

    def add(sig, at, g=1.0):
        i = int(at * SR)
        if i >= n:
            return
        L = min(len(sig), n - i)
        out[i:i + L] += sig[:L] * g

    pop = sfx3.soft_pop
    add(pop(900), 0.05, 0.3)                      # top pill
    for at in (0.68, 2.22):                       # emphasis boxes on footage
        add(pop(780, 0.1), at, 0.3)
    add(blip(900, 1300, .12), 2.3, 0.22)           # smile meter
    add(shimmer(0.9), 2.9, 0.18)
    for at in (2.4, 2.94):
        add(pop(1050, 0.07), at, 0.22)
    # layout morphs
    for at in (3.55, 9.65, 13.25, 18.25):
        add(swish(0.45), at - 0.3, 0.3)
    # clock scene
    add(pop(500, 0.14), 3.6, 0.4)
    tt = 3.9
    while tt < 9.5:
        fast = 4.4 < tt < 9.2
        add(sfx3.clock_tick(), tt, 0.22 if fast else 0.4)
        tt += 0.12 if fast else 1.0
    for at in (5.4, 7.0, 8.7):                    # caption boxes
        add(pop(780, 0.1), at, 0.28)
    add(pop(900), 5.0, 0.3)
    add(pop(700), 6.6, 0.3)
    add(sfx3.chime(), 9.02, 0.3)
    for at in (3.7, 3.9, 4.3):
        add(pop(1050, 0.07), at, 0.2)
    # hug moment
    add(pop(800, 0.12), 11.0, 0.35)
    add(shimmer(1.2), 11.0, 0.18)
    for at in (10.9, 11.2):
        add(pop(1100, 0.07), at, 0.22)
    # final framed scene
    for at in (14.12, 17.36):
        add(pop(780, 0.1), at, 0.28)
    for at in (14.22, 15.6, 17.36):
        add(sfx3.check_tick(), at, 0.4)
    for at in (13.5, 13.6, 13.7, 13.8):
        add(pop(1050, 0.07), at, 0.2)
    add(pop(780, 0.1), 18.3, 0.3)
    # outro
    add(pop(700), 18.35, 0.3)
    s = 'Agendar avaliação'
    for i in range(len(s)):
        add(key_tick(), 18.7 + 0.8 * i / len(s), 0.7)
    add(sfx.click(), 19.55, 0.35)
    add(sfx3.chime(), 19.7, 0.4)
    return reverb(out, 0.7, 0.18)


def main():
    voice = clean_voice(sys.argv[1])
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.9
    mus = sfx3.epiano_music()[:len(voice)]
    e = np.convolve(np.abs(voice), np.ones(int(0.2 * SR)) / (0.2 * SR), mode='same')
    duck = 1 - 0.55 * np.clip(e / (e.max() * 0.2), 0, 1)
    mus = mus / (np.abs(mus).max() + 1e-9) * 0.16 * duck
    fx = build()
    fx = fx / (np.abs(fx).max() + 1e-9) * 0.38
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
