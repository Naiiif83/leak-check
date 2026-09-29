"""موسيقى الفيديو السريع (15 ثانية، 120 نبضة بالدقيقة): إيقاع حماسي يضرب مع النصوص.

  0–3.5   الفاتورة: كيك وضربات مع ظهور المبلغ
  3.5–8   الأسباب: إيقاع كامل، وضربة مع كل سبب (5، 6، 7)
  8–11    الحل: ضربات على «ساعة وحدة» و«قراءتين» و«بدون فني»، وصعود قبل الدعوة
  11–15   الدعوة: انفتاح لمقام كبير

الاستخدام: python3 fast.py fast.wav
"""
import sys

import numpy as np

from sound import Mix, env, hz, tt

B = 0.5  # نبضة
m = Mix(15.0, seed=21)
noise = lambda d: m.rng.standard_normal(int(d * 44100))


def kick(at, g=0.9):
    t = tt(0.35)
    m.add(np.sin(2 * np.pi * (45 + 110 * np.exp(-t * 28)) * t) * np.exp(-t * 9), at, 0, g)


def clap(at, g=0.35):
    t = tt(0.25)
    s = noise(0.25) * np.exp(-t * 22)
    s = np.convolve(s, np.ones(6) / 6, "same")  # يخفف الحدة
    m.add(s, at, 0.1, g)


def hat(at, g=0.08, pan=-0.3):
    t = tt(0.06)
    m.add(np.diff(noise(0.06), prepend=0) * np.exp(-t * 80), at, pan, g)


def bass(note, at, d, g=0.28):
    t = tt(d)
    f = hz(note)
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + np.sin(2 * np.pi * f * t)
    m.add(s * env(len(t), 0.005, 0.08), at, 0, g)


def stab(notes, at, g=0.18):
    t = tt(0.4)
    s = sum(np.sin(2 * np.pi * hz(n) * t) + 0.5 * np.sin(2 * np.pi * hz(n) * 2 * t) for n in notes)
    m.add(s * np.exp(-t * 7), at, 0, g)


def riser(a, b, g=0.25):
    t = tt(b - a)
    x = t / (b - a)
    s = noise(b - a) * x ** 2 + np.sin(2 * np.pi * np.cumsum(200 + 1400 * x ** 2) / 44100) * 0.3 * x
    m.add(s, a, 0, g)


# ١: الفاتورة
kick(0.0, 1.0); stab([57, 60, 64], 0.0, 0.22)
for k in range(12):  # عدّاد المبلغ: تكّات تتسارع
    m.add(np.sin(2 * np.pi * 1800 * tt(0.03)) * np.exp(-tt(0.03) * 120), 0.6 + k * 0.075, 0.2, 0.12)
kick(1.5); kick(2.0, 1.0); clap(2.0, 0.5); stab([56, 60, 63], 2.0, 0.22)
for at in np.arange(2.0, 3.5, B):
    kick(at, 0.7)

# ٢: الأسباب — الإيقاع الكامل
prog_ = [45, 45, 41, 43]  # A F G
for bar in range(9):
    at0 = 3.5 + bar * B
    if at0 >= 8.0:
        break
    kick(at0)
    if bar % 2:
        clap(at0)
    hat(at0 + B / 2, 0.09)
    bass(prog_[(bar // 2) % 4], at0, B * 0.9)
for at, notes in [(5.0, [69, 72, 76]), (6.0, [65, 69, 72]), (7.0, [67, 71, 74])]:
    stab(notes, at, 0.25)

# ٣: الحل
for at in np.arange(8.0, 11.0, B):
    kick(at, 0.8); hat(at + B / 2, 0.1, 0.3)
for at in (8.0, 8.8, 9.6, 10.2):
    stab([72, 76, 79], at, 0.22)
riser(9.8, 11.0, 0.3)

# ٤: الدعوة — مقام كبير
kick(11.0, 1.0); clap(11.0, 0.5)
t = tt(4.0)
pad = sum(np.sin(2 * np.pi * hz(n) * t) + 0.3 * np.sin(2 * np.pi * hz(n) * 2.002 * t) for n in (48, 55, 60, 64, 67))
m.add(pad * env(len(t), 0.05, 1.5), 11.0, 0, 0.07)
for k, at in enumerate(np.arange(11.0, 14.5, B)):
    kick(at, 0.6); hat(at + B / 2, 0.07)
    bass((48, 48, 53, 55)[(k // 2) % 4], at, B * 0.9, 0.22)
for at, n in [(11.4, 72), (11.9, 76), (12.3, 79), (12.7, 84)]:
    stab([n], at, 0.2)

m.echo(((0.25, 0.18),))
m.save(sys.argv[1] if len(sys.argv) > 1 else "fast.wav", fade_out=1.2)
