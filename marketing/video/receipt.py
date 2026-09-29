"""موسيقى فيديو «الفاتورة» (16 ثانية، 96 نبضة): إلكتروني خفيف وجاد، مع صوت طابعة وكاشير.

  0–2.3    العنوان: نبض منخفض
  3.2–8.6  صوت طابعة مع كل سطر
  7.6      صوت كاشير مع المجموع
  9.6      ختم «وأنت ما تدري»
  12.4–16  الدعوة

الاستخدام: python3 receipt.py receipt.wav
"""
import sys

import numpy as np

from sound import Mix, env, hz, tt

m = Mix(16.0, seed=96)
B = 60 / 96


def kick(at, g=0.5):
    t = tt(0.3)
    m.add(np.sin(2 * np.pi * (42 + 70 * np.exp(-t * 26)) * t) * np.exp(-t * 9), at, 0, g)


def hat(at, g=0.05):
    t = tt(0.05)
    m.add(np.diff(m.rng.standard_normal(len(t)), prepend=0) * np.exp(-t * 90), at, -0.25, g)


def bass(n, at, d, g=0.22):
    t = tt(d)
    f = hz(n)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    m.add(s * env(len(t), 0.005, 0.1), at, 0, g)


def printer(at, d=0.35, g=0.1):
    t = tt(d)
    s = m.rng.standard_normal(len(t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 38 * t)))
    s = np.convolve(s, np.ones(8) / 8, "same") + 0.4 * np.sin(2 * np.pi * 180 * t)
    m.add(s * env(len(t), 0.01, 0.05), at, 0.3, g)


def kaching(at, g=0.3):
    t = tt(1.0)
    bell = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 4) for f in (2093, 2637, 3136))
    drawer = m.rng.standard_normal(int(0.08 * 44100)) * np.exp(-tt(0.08) * 40)
    m.add(drawer, at, 0, g * 0.8)
    m.add(bell, at + 0.06, 0, g * 0.5)


def pad(notes, at, d, g=0.04):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * hz(n) * t) + 0.2 * np.sin(2 * np.pi * hz(n) * 2.004 * t) for n in notes)
    m.add(s * env(len(t), 0.3, 0.8), at, 0, g)


# العنوان: نبض منخفض
pad((45, 52, 57), 0.0, 2.6, 0.05)
for k in range(4):
    kick(k * B, 0.4)

# الطباعة: إيقاع خفيف
seq = [45, 45, 48, 43]
k = 0
at = 2.3
while at < 12.0:
    kick(at, 0.45)
    hat(at + B / 2)
    bass(seq[(k // 2) % 4], at, B * 0.8)
    at += B
    k += 1
pad((45, 52, 57, 60), 2.3, 5.0, 0.03)
pad((41, 48, 57, 60), 7.3, 4.8, 0.03)
for at in (2.4, 3.2, 4.2, 5.2, 6.3):
    printer(at)
printer(7.6, 0.45)
kaching(7.95)
printer(8.6, 0.3, 0.07)

# الختم
kick(9.6, 0.8)
t = tt(0.4)
m.add(m.rng.standard_normal(len(t)) * np.exp(-t * 20), 9.6, 0, 0.12)

# الدعوة: تنفرج لمقام كبير
pad((48, 55, 60, 64, 67), 12.3, 3.7, 0.06)
for j, n in enumerate((72, 76, 79, 84)):
    t = tt(1.0)
    m.add(np.sin(2 * np.pi * hz(n) * t) * np.exp(-t * 4), 12.4 + j * 0.4, (-0.3, 0.3)[j % 2], 0.12)
for j in range(5):
    kick(12.4 + j * B, 0.35)

m.echo(((0.31, 0.2),))
m.save(sys.argv[1] if len(sys.argv) > 1 else "receipt.wav", fade_out=1.5)
