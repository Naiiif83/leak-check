"""موسيقى فيديو «٣ علامات» (16 ثانية، 85 نبضة): لو-فاي دافي مع خشخشة أسطوانة.

  0–2.2    العنوان
  2.3/5.7/9.1  جرس مع كل رقم (٣، ٢، ١)
  12.6–16  الدعوة: انفتاح وتلاشي

الاستخدام: python3 signs.py signs.wav
"""
import sys

import numpy as np

from sound import Mix, env, hz, tt

BPM = 85
B = 60 / BPM
m = Mix(16.0, seed=85)


def kick(at, g=0.55):
    t = tt(0.3)
    m.add(np.sin(2 * np.pi * (48 + 60 * np.exp(-t * 25)) * t) * np.exp(-t * 10), at, 0, g)


def snap(at, g=0.12):
    t = tt(0.12)
    s = m.rng.standard_normal(len(t)) * np.exp(-t * 40)
    m.add(np.convolve(s, np.ones(12) / 12, "same"), at, 0.15, g)


def rhodes(notes, at, d, g=0.05):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * hz(n) * t + 0.6 * np.sin(2 * np.pi * hz(n) * t) * np.exp(-t * 3)) for n in notes)
    m.add(s * env(len(t), 0.01, 0.6) * np.exp(-t * 0.6), at, 0, g)


def bass(n, at, d, g=0.2):
    t = tt(d)
    m.add(np.sin(2 * np.pi * hz(n) * t) * env(len(t), 0.01, 0.1), at, 0, g)


def bell(n, at, g=0.16):
    t = tt(1.5)
    s = np.sin(2 * np.pi * hz(n) * t) * np.exp(-t * 3) + 0.4 * np.sin(2 * np.pi * hz(n) * 2.76 * t) * np.exp(-t * 6)
    m.add(s, at, 0, g)


# خشخشة أسطوانة على طول الفيديو
crackle = np.zeros(m.n)
idx = m.rng.integers(0, m.n, 900)
crackle[idx] = m.rng.uniform(-1, 1, len(idx))
m.L += crackle * 0.05
m.R += np.roll(crackle, 37) * 0.05

# Am7  Dm7  G7  Cmaj7
chords = [(57, 60, 64, 67), (50, 57, 60, 65), (55, 59, 62, 65), (48, 55, 59, 64)]
roots = [45, 38, 43, 36]
bar = 4 * B
for i in range(5):
    at = i * bar * 0.75
    if at > 15:
        break
    c = i % 4
    rhodes(chords[c], at, bar * 0.8)
    bass(roots[c], at, B * 1.5)
    bass(roots[c] + 7, at + B * 2, B)

beat = 0.0
while beat < 15.2:
    kick(beat)
    snap(beat + B)
    kick(beat + B * 2.5, 0.35)
    snap(beat + B * 3)
    beat += 4 * B

for at, n in [(2.3, 76), (5.7, 74), (9.1, 72)]:
    bell(n, at)
    bell(n + 12, at + 0.02, 0.05)

rhodes((60, 64, 67, 71), 12.6, 3.4, 0.07)
for k, (at, n) in enumerate([(12.6, 72), (13.1, 76), (13.5, 79), (13.9, 83)]):
    bell(n, at, 0.1)

m.echo(((0.35, 0.22),))
m.save(sys.argv[1] if len(sys.argv) > 1 else "signs.wav", fade_out=1.5)
