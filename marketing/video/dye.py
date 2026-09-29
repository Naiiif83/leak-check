"""موسيقى فيديو «تجربة الصبغة» (17 ثانية، 100 نبضة): ماريمبا ونقر مرح مثل فيديوهات الحِيَل.

  3.6/4.2/4.8  نقط الصبغة
  6.6–8.8      تكتكة ساعة سريعة
  10.7         ختم «سيفونك يسرّب!»
  12.6–17      الدعوة

الاستخدام: python3 dye.py dye.wav
"""
import sys

import numpy as np

from sound import Mix, hz, tt

B = 0.6
m = Mix(17.0, seed=100)


def marimba(n, at, g=0.14, pan=0.0):
    t = tt(0.5)
    f = hz(n)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)
    m.add(s, at, pan, g)


def pluck(n, at, g=0.1):
    t = tt(0.3)
    m.add(np.sin(2 * np.pi * hz(n) * t) * np.exp(-t * 16), at, 0.3, g)


def thump(at, g=0.35):
    t = tt(0.2)
    m.add(np.sin(2 * np.pi * (60 + 50 * np.exp(-t * 30)) * t) * np.exp(-t * 14), at, 0, g)


def drip(at, g=0.3):
    t = tt(0.3)
    f = 700 * (1 + 1.4 * np.exp(-t * 40))
    m.add(np.sin(2 * np.pi * np.cumsum(f) / 44100) * np.exp(-t * 14), at, 0, g)


def tick(at, g=0.1):
    t = tt(0.03)
    m.add(np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 180), at, -0.2, g)


# لحن مرح بسلم كبير: يتكرر ويتنوع
melody = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 76, 74]
basses = [48, 53, 55, 48]
i = 0
at = 0.0
while at < 12.4:
    if not (6.4 < at < 9.2):  # الساعة لحالها في النص
        marimba(melody[i % len(melody)], at, 0.12, pan=(-0.3, 0.3)[i % 2])
        if i % 2 == 0:
            pluck(basses[(i // 4) % 4] + 12, at)
            thump(at, 0.25)
    at += B / 2
    i += 1

for d in (3.6, 4.2, 4.8):
    drip(d + 0.35)
for k in range(int((8.8 - 6.6) / 0.11)):
    tick(6.6 + k * 0.11)

# الختم
thump(10.7, 0.6)
for k, n in enumerate((72, 76, 79, 84)):
    marimba(n, 10.7 + k * 0.07, 0.16)

# الدعوة
at = 12.6
for k, n in enumerate([79, 81, 84, 88, 84, 81, 79, 76, 79, 84]):
    marimba(n, at + k * B / 2, 0.11, pan=(-0.3, 0.3)[k % 2])
    if k % 2 == 0:
        pluck(48 + (0, 5, 7, 0, 0)[k // 2] + 12, at + k * B / 2)

m.echo(((0.3, 0.2),))
m.save(sys.argv[1] if len(sys.argv) > 1 else "dye.wav", fade_out=1.5)
