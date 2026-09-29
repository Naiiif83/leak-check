"""موسيقى فيديو الشرح (18 ثانية): هادية ودافية، مع صوت نقطة ماء ونغمة لكل خطوة.

  0–3.4   نقطة الماء تنزل (1.1) وتموجات
  3.4–13.6 الخطوات: نغمة عند كل خطوة (3.6، 6.1، 8.6، 11.1) ونقرة خفيفة مع كل لمسة
  14–18   الدعوة: مقام كبير دافي وتلاشي

الاستخدام: python3 tutorial.py tutorial.wav
"""
import sys

import numpy as np

from sound import Mix, env, hz, tt

m = Mix(18.0, seed=5)


def pad(notes, at, d, g=0.05):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * hz(n) * t) * (1 + 0.15 * np.sin(2 * np.pi * 0.3 * t)) for n in notes)
    m.add(s * env(len(t), 0.8, 1.2), at, 0, g)


def keys(n, at, g=0.12, pan=0.0):
    t = tt(1.6)
    s = np.sin(2 * np.pi * hz(n) * t) * np.exp(-t * 2.5) + 0.25 * np.sin(2 * np.pi * hz(n) * 2 * t) * np.exp(-t * 5)
    m.add(s, at, pan, g)


def drop(at, g=0.35):
    t = tt(0.4)
    f = 900 * (1 + 1.2 * np.exp(-t * 35))
    m.add(np.sin(2 * np.pi * np.cumsum(f) / 44100) * np.exp(-t * 12), at, 0, g)


def tap(at, g=0.12):
    t = tt(0.05)
    m.add(np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 150), at, 0.2, g)


# ١: نقطة الماء
pad([50, 57, 62], 0.0, 4.0, 0.04)          # D
drop(1.1, 0.45)
for k in range(3):
    keys(74 - k * 5, 1.3 + k * 0.45, 0.06, pan=(-0.4, 0.4, 0)[k])

# ٢: الخطوات — تتابع هادي D  Bm  G  A
chords = [(50, 57, 62, 66), (47, 54, 59, 62), (43, 50, 55, 59), (45, 52, 57, 61)]
for i, at in enumerate((3.4, 5.9, 8.4, 10.9)):
    pad(chords[i], at, 3.0, 0.035)
for i, (at, n) in enumerate([(3.6, 74), (6.1, 76), (8.6, 78), (11.1, 81)]):
    keys(n, at, 0.16)
    keys(n - 12, at + 0.02, 0.06)
for at in (5.2, 7.7, 10.2):
    tap(at)
# نبض خفيف مثل عقرب ساعة في خطوة الانتظار
for at in np.arange(8.6, 11.0, 0.5):
    t = tt(0.03)
    m.add(np.sin(2 * np.pi * 1300 * t) * np.exp(-t * 200), at, -0.2, 0.05)

# ٣: الدعوة
pad([50, 57, 62, 66, 69], 13.8, 4.2, 0.05)
for k, (at, n) in enumerate([(14.0, 74), (14.5, 78), (14.9, 81), (15.4, 86)]):
    keys(n, at, 0.13, pan=(-0.3, 0.3)[k % 2])

m.echo(((0.31, 0.3), (0.53, 0.18)))
m.save(sys.argv[1] if len(sys.argv) > 1 else "tutorial.wav", fade_out=2.0)
