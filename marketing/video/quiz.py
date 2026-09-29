"""موسيقى فيديو «صح ولا غلط؟» (18 ثانية): جو برامج المسابقات.

  0–2      فتحة مرحة
  لكل سؤال (2، 6، 10): تكتكة ترقّب لين الكشف بعد 2.3 ثانية، وبعدها جرس (صح) أو زمّور (غلط)
  14–18    الدعوة: ختام احتفالي

الاستخدام: python3 quiz.py quiz.wav
"""
import sys

import numpy as np

from sound import Mix, env, hz, tt

m = Mix(18.0, seed=33)
B = 60 / 118


def brass(notes, at, d, g=0.1):
    t = tt(d)
    s = 0
    for n in notes:
        f = hz(n)
        s = s + sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 6))
    m.add(s * env(len(t), 0.02, 0.15), at, 0, g)


def kick(at, g=0.45):
    t = tt(0.25)
    m.add(np.sin(2 * np.pi * (50 + 80 * np.exp(-t * 30)) * t) * np.exp(-t * 12), at, 0, g)


def tick(at, g=0.12, f=1600):
    t = tt(0.035)
    m.add(np.sin(2 * np.pi * f * t) * np.exp(-t * 160), at, 0.2, g)


def ding(at, g=0.3):
    t = tt(1.2)
    s = sum(np.sin(2 * np.pi * hz(n) * t) * np.exp(-t * 3) for n in (84, 88, 91))
    m.add(s, at, 0, g)


def buzz(at, g=0.18):
    t = tt(0.5)
    s = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.6 + np.sign(np.sin(2 * np.pi * 116 * t)) * 0.4
    m.add(s * env(len(t), 0.01, 0.1), at, 0, g)


# فتحة
brass((60, 64, 67), 0.1, 0.25, 0.12)
brass((62, 65, 69), 0.4, 0.25, 0.12)
brass((64, 67, 72), 0.7, 0.9, 0.14)
kick(0.1); kick(0.7, 0.6)

# الأسئلة
for at0, true in ((2.0, False), (6.0, True), (10.0, False)):
    kick(at0, 0.5)
    k = 0
    at = at0 + 0.3
    while at < at0 + 2.3:
        tick(at, 0.1 + 0.05 * (k % 2), 1500 + 100 * (k % 2))
        at += 0.25 - min(0.12, k * 0.012)  # تتسارع
        k += 1
    if true:
        ding(at0 + 2.3)
    else:
        buzz(at0 + 2.3)
        ding(at0 + 2.35, 0.12)
    # قاعدة خفيفة وقت الشرح
    for j in range(3):
        kick(at0 + 2.6 + j * B, 0.3)

# الختام
brass((60, 64, 67), 14.1, 0.3, 0.13)
brass((65, 69, 72), 14.5, 0.3, 0.13)
brass((67, 71, 74), 14.9, 0.3, 0.13)
brass((72, 76, 79), 15.3, 1.6, 0.15)
for j in range(6):
    kick(14.1 + j * B, 0.5)
ding(15.3, 0.2)

m.echo(((0.22, 0.2),))
m.save(sys.argv[1] if len(sys.argv) > 1 else "quiz.wav", fade_out=1.5)
