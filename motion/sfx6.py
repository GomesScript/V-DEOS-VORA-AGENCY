"""Audio for the conversation video (v6.html): the clip's own audio cleaned up
(high-pass, light denoise, loudness normalisation), a soft electric-piano bed
ducked under the dialogue, and the same gentle UI sound design as the reference
(pops, check ticks, clock ticks, swishes, typing, chime).

Usage: python3 sfx5.py assets/conversa_original.mp4 out.wav
"""
import subprocess
import sys
import wave

import numpy as np

import sfx
import sfx3
from sfx import SR, swish, key_tick, blip, shimmer, reverb

DUR = 36.8
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
    for at in (0.1, 13.64, 23.06, 32.2, 33.46):   # speaker tag changes
        add(blip(1000, 1500, .1), at, 0.25)
    for at in (1.22, 5.2, 6.34, 7.1, 9.5, 12.84, 13.96, 14.7, 16.32, 18.16, 18.78, 20.08, 21.86, 24.26, 29.36, 29.9, 31.54, 32.92, 33.46):
        add(pop(780, 0.1), at, 0.28)              # emphasis boxes
    for at in (2.4, 8.0, 13.55, 23.05, 25.2, 32.15, 33.4, 34.4):
        add(swish(0.45), at - 0.3, 0.3)           # layout morphs
    add(pop(600, 0.12), 2.45, 0.35)               # wear card
    add(blip(1300, 600, 2.0) * 0.5, 4.5, 0.25)
    add(shimmer(1.0), 6.3, 0.18)
    add(pop(550, 0.12), 13.45, 0.35)              # call tile
    add(pop(550, 0.12), 32.05, 0.3)
    add(pop(600, 0.12), 25.25, 0.35)              # checklist
    for at in (29.26, 30.0, 31.2):
        add(sfx3.check_tick(), at, 0.45)
    for at in (33.6, 33.8, 34.0):
        add(sfx3.check_tick(), at, 0.35)
    for at in (1.66, 2.6, 2.8, 13.8, 13.9, 25.4, 25.6, 33.6, 33.7, 33.8, 33.9):
        add(pop(1050, 0.07), at, 0.2)             # stickers
    add(pop(700), 34.45, 0.3)                     # outro
    s = 'Agendar avaliação'
    for i in range(len(s)):
        add(key_tick(), 34.8 + 0.9 * i / len(s), 0.7)
    add(sfx.click(), 35.8, 0.35)
    add(sfx3.chime(), 35.95, 0.4)
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
