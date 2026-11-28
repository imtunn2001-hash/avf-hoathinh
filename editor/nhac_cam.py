"""Nhac nen theo TINH TIET (28/11, chu chot CCK: "them nhac nen theo dung tinh tiet cau chuyen").
Tu tao bang numpy (khong ban quyen). Moi canh co 'mood'; doi mood thi cross-fade 1,5 s.
mood: mo (bi an), dieu_tra (lan theo manh moi), cang (cang thang, truy duoi), soc (cu lat), buon (mat mat), ket (khep lai)
Dung: python3 nhac_cam.py out.wav "0:mo,12.5:cang,40:buon" 90
"""
import math
import sys
import wave

import numpy as np

SR = 44100
A_MIN = [110.0, 130.81, 164.81]          # La thu
CHORDS = {
    'mo': [[110.0, 130.81, 164.81], [98.0, 116.54, 146.83], [87.31, 110.0, 130.81], [82.41, 103.83, 123.47]],
    'buon': [[110.0, 130.81, 164.81], [87.31, 110.0, 130.81], [65.41, 98.0, 130.81], [82.41, 98.0, 123.47]],
    'ket': [[87.31, 110.0, 130.81], [98.0, 123.47, 146.83], [65.41, 82.41, 98.0], [110.0, 130.81, 164.81]],
}


def _env(n, a=.01, r=.4):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-3)) * np.exp(-t / max(r, 1e-3))


def _tone(f, n, kind='sin'):
    t = np.arange(n) / SR
    if kind == 'pluck':
        return (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t) + .15 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 6)
    if kind == 'piano':
        return (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3) + .2 * np.sin(6 * np.pi * f * t) * np.exp(-t * 5)) * np.exp(-t * 1.6)
    return np.sin(2 * np.pi * f * t)


def layer(mood, D, seed=1):
    n = int(D * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32); rng = np.random.default_rng(seed)

    def add(at, sig, g):
        a = int(at * SR)
        if a >= n: return
        b = min(n, a + len(sig)); out[a:b] += (sig[:b - a] * g).astype(np.float32)

    if mood in ('mo', 'buon', 'ket'):
        ch = CHORDS[mood]; bar = 4.0 if mood != 'buon' else 5.0
        pad = np.zeros(n)
        for i in range(int(D / bar) + 2):
            c = ch[i % 4]; a = int(i * bar * SR); L = int((bar + 1.5) * SR)
            seg = sum(_tone(f, L) + .3 * _tone(f * 2.003, L) for f in c) / 3
            e = np.minimum(1, np.arange(L) / SR / 1.2) * np.minimum(1, (L / SR - np.arange(L) / SR) / 1.5)
            b = min(n, a + L)
            if a < n: pad[a:b] += (seg * e)[:b - a]
        out += (pad * (.05 if mood != 'ket' else .06)).astype(np.float32)
        step = 1.0 if mood == 'mo' else (1.25 if mood == 'buon' else .75)
        k = 0; tt = .3
        while tt < D:
            c = ch[int(tt / bar) % 4]; f = c[k % 3] * (4 if mood != 'buon' else 2)
            if mood == 'mo' and k % 4 == 3: f *= 1.5
            add(tt, _tone(f, int(2.5 * SR), 'piano' if mood != 'mo' else 'pluck'), .05 if mood != 'mo' else .04)
            tt += step * (1.0 if mood != 'mo' else rng.choice([1.0, 1.0, 1.5])); k += 1
        if mood == 'mo':   # chuong xa
            for at in np.arange(2.0, D, 7.0): add(at, _tone(880.0, int(3 * SR)) * np.exp(-np.arange(int(3 * SR)) / SR * 1.4), .025)
    elif mood == 'dieu_tra':   # pizzicato La thu deu 100 BPM + kim dong ho
        beat = 60 / 100; seq = [110.0, 164.81, 130.81, 164.81, 98.0, 146.83, 116.54, 146.83]
        for i in range(int(D / beat) + 1):
            add(i * beat, _tone(seq[i % 8], int(.6 * SR), 'pluck'), .09)
            add(i * beat + beat / 2, _tone(2000.0, int(.03 * SR)) * _env(int(.03 * SR), .001, .01), .03)
        out += (.03 * np.sin(2 * np.pi * 55 * t)).astype(np.float32)
    elif mood == 'cang':   # nen tram + nhip tim + day cao nghich tai, tang dan
        rise = np.minimum(1, t / max(4.0, D))
        out += ((.07 * np.sin(2 * np.pi * 49 * t) + .03 * np.sin(2 * np.pi * 73.5 * t)) * (0.7 + 0.3 * rise)).astype(np.float32)
        out += (.012 * np.sin(2 * np.pi * 622 * t + 3 * np.sin(2 * np.pi * .3 * t)) * rise).astype(np.float32)
        for at in np.arange(.4, D, .82):   # thinh-thinh
            for dt, g in ((0, .22), (.22, .15)):
                L = int(.18 * SR); tk = np.arange(L) / SR
                add(at + dt, np.sin(2 * np.pi * (55 - 20 * tk) * tk) * np.exp(-tk * 22), g)
    elif mood == 'soc':   # 1 tieng dap tram + vang, roi im
        L = int(min(D, 4.0) * SR); tk = np.arange(L) / SR
        add(0, (np.sin(2 * np.pi * (60 - 30 * tk) * tk) * np.exp(-tk * 3) + .3 * rng.standard_normal(L) * np.exp(-tk * 12)), .5)
        add(0, sum(_tone(f, L) for f in (233.08, 246.94, 349.23)) * np.exp(-tk * 1.2), .02)
    return out


def build(path, marks, D):
    """marks: [(giay, mood)] tang dan. Cross-fade 1,5 s giua cac doan."""
    n = int(D * SR); out = np.zeros(n, np.float32); XF = 1.5
    marks = sorted(marks) or [(0.0, 'mo')]
    for i, (a, m) in enumerate(marks):
        b = marks[i + 1][0] if i + 1 < len(marks) else D
        a0 = max(0.0, a - XF / 2); b0 = min(D, b + XF / 2)
        seg = layer(m, b0 - a0, seed=i + 1); L = len(seg)
        e = np.ones(L, np.float32); f = int(XF * SR)
        if a0 > 0: e[:f] = np.linspace(0, 1, min(f, L))[:L] if L < f else np.linspace(0, 1, f)
        if b0 < D: e[-f:] = np.minimum(e[-f:], np.linspace(1, 0, f)) if L >= f else e[-f:]
        s0 = int(a0 * SR); out[s0:s0 + L] += (seg * e)[:n - s0]
    out = out / max(1e-6, np.abs(out).max()) * .8
    st = np.repeat(out[:, None], 2, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
    return path


if __name__ == '__main__':
    mk = [(float(x.split(':')[0]), x.split(':')[1]) for x in sys.argv[2].split(',')]
    build(sys.argv[1], mk, float(sys.argv[3]))
