"""موسيقى أصلية لفيديو فحص التسرّب (15 ثانية)، مركّبة بالكود بالكامل.

تتبع مشاهد promo.html:
  0–3.2    الخطّاف: ضربتين مع ظهور «زادت» و«بدون سبب؟»
  3.2–7.4  العدّاد: نقط ماء متكررة فوق نبض هادي
  7.4–10.6 الرقم: صعود مع العدّاد لين 100
  10.6–15  الدعوة: انفتاح لمقام كبير وتلاشي

الاستخدام: python3 music.py music.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 15.0
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    j = min(N, i + len(sig))
    if i >= N:
        return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - pan) / 2 * 2 ** 0.5 / 1.0
    R[i:j] += s * (1 + pan) / 2 * 2 ** 0.5 / 1.0


def env(n, a=0.01, r=0.3):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pad(notes, start, dur, gain=0.05):
    t = tt(dur)
    s = sum(np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(2 * np.pi * hz(m) * 2.003 * t) for m in notes)
    add(s * env(len(t), 0.4, 0.8), start, 0, gain)


def hit(at, gain=0.5):
    t = tt(0.6)
    body = np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 7)
    noise = np.random.default_rng(1).standard_normal(len(t)) * np.exp(-t * 25) * 0.25
    add(body + noise, at, 0, gain)


def drip(at, pitch=84, pan=0.0, gain=0.22):
    t = tt(0.35)
    f = hz(pitch) * (1 + 0.6 * np.exp(-t * 40))  # نقطة ماء: نغمة تنزل بسرعة
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14), at, pan, gain)


def pluck(m, at, gain=0.12, pan=0.0):
    t = tt(0.9)
    s = np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * 5) + 0.4 * np.sin(2 * np.pi * hz(m) * 3 * t) * np.exp(-t * 9)
    add(s, at, pan, gain)


# ١: الخطّاف
pad([45, 52, 60], 0.0, 3.4, 0.035)          # A صغير
hit(0.5, 0.55)
hit(1.0, 0.7)
pluck(76, 1.0, 0.10)

# ٢: العدّاد — نبض ونقط
pad([45, 52, 57, 60], 3.2, 4.4, 0.03)
for k, at in enumerate(np.arange(3.7, 7.3, 0.25)):
    drip(at, 84 + (k % 3) * 2, pan=(-0.4 if k % 2 else 0.4))
for at in np.arange(3.2, 7.4, 0.5):
    t = tt(0.25)
    add(np.sin(2 * np.pi * 50 * t) * np.exp(-t * 18), at, 0, 0.35)
hit(5.2, 0.5)

# ٣: الرقم يطلع
pad([41, 48, 57, 60], 7.4, 3.3, 0.035)       # F
for k, at in enumerate(np.linspace(8.5, 9.7, 13)):
    pluck(64 + k, at, 0.07, pan=0.3 * np.sin(k))
hit(9.7, 0.6)

# ٤: الدعوة — مقام كبير
pad([48, 55, 60, 64, 67], 10.6, 4.4, 0.045)  # C كبير
for k, (m, at) in enumerate([(72, 10.6), (76, 11.3), (79, 11.8), (84, 12.2)]):
    pluck(m, at, 0.12, pan=(-0.3, 0.3)[k % 2])

# صدى بسيط وتطبيع وتلاشي
for d, g in [(0.23, 0.25), (0.41, 0.15)]:
    k = int(d * SR)
    L[k:] += R[:-k] * g
    R[k:] += L[:-k] * g
fade = np.ones(N)
fade[-int(1.2 * SR):] = np.linspace(1, 0, int(1.2 * SR))
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.85, R / peak * 0.85

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.stack([L, R], 1) * 32767).astype("<i2").tobytes())
print("saved", out)
