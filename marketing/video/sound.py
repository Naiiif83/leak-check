"""أدوات صوت مشتركة لموسيقى الفيديوهات، مركّبة بالكود بالكامل (بدون عينات جاهزة)."""
import wave

import numpy as np

SR = 44100


class Mix:
    def __init__(self, dur, seed=7):
        self.n = int(SR * dur)
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)
        self.rng = np.random.default_rng(seed)

    def add(self, sig, at, pan=0.0, gain=1.0):
        i = int(at * SR)
        if i >= self.n or i < 0:
            return
        j = min(self.n, i + len(sig))
        s = sig[: j - i] * gain
        self.L[i:j] += s * (1 - pan) * 0.7071
        self.R[i:j] += s * (1 + pan) * 0.7071

    def echo(self, taps=((0.23, 0.25), (0.41, 0.15))):
        for d, g in taps:
            k = int(d * SR)
            self.L[k:] += self.R[:-k] * g
            self.R[k:] += self.L[:-k] * g

    def save(self, path, fade_out=1.0):
        n = int(fade_out * SR)
        f = np.ones(self.n)
        f[-n:] = np.linspace(1, 0, n)
        L, R = self.L * f, self.R * f
        peak = max(np.abs(L).max(), np.abs(R).max()) or 1
        data = (np.stack([L, R], 1) / peak * 0.88 * 32767).astype("<i2")
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(data.tobytes())
        print("saved", path)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.01, r=0.3):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    if 0 < nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e
