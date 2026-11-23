"""Hieu ung dung chung (23/11, chu chot "lam tat"): chuyen canh whip/zoom co nhoe chuyen dong, tieng whoosh,
grade mau theo kenh (ffmpeg -vf), ha nhac khi co loi (ducking), chu nhay theo tung tu (moc tu theo am tiet)."""
import numpy as np
from PIL import Image

SR = 44100

# ---------- grade mau theo kenh: chuoi -vf cho ffmpeg (giu trang o 1.0 de chu trang khong bi ngam mau) ----------
GRADE = {
    # Moi Ngay Mot Buoc: am, toi sau, bong hoi xanh (teal & orange nhe), hat phim mong
    'mnmb': "curves=r='0/0 0.25/0.24 0.75/0.79 1/1':g='0/0 0.5/0.5 1/1':b='0/0.03 0.25/0.25 0.75/0.70 1/1',"
            "colorbalance=rs=-0.03:bs=0.05:rh=0.05:bh=-0.04,eq=contrast=1.06:saturation=1.05,noise=alls=5:allf=t",
    # roi nuoc / ky su / lien thien: trong, tuoi, hoi am nhu giay do; khong hat
    'rn': "eq=contrast=1.04:saturation=1.08,colorbalance=rh=0.03:bh=-0.02,vignette=angle=PI/6",
    # Chien Su Ky ban do: tong phim tai lieu – giay cu am, bot bao hoa, toi vien
    'war': "eq=contrast=1.04:saturation=0.96,vignette=angle=PI/7",   # 23/11: ban dau ngam vang lam ban do duc -> chi giu tuong phan + toi vien nhe
    # Chuyen Dem: da co VHS trong code; chi ep den sau them + lanh nhe
    'cd': "curves=all='0/0 0.15/0.10 0.6/0.6 1/1',colorbalance=bs=0.04:gs=0.02",
}


def grade_vf(name):
    return GRADE.get(name or '', '')


# ---------- chuyen canh ----------
def hblur(img, k):
    """nhoe ngang nhanh: thu nho chieu ngang roi phong lai (k = do nhoe, 1 = khong)"""
    if k <= 1.05: return img
    w, h = img.size
    return img.resize((max(8, int(w / k)), h), Image.BILINEAR).resize((w, h), Image.BILINEAR)


def vblur(img, k):
    if k <= 1.05: return img
    w, h = img.size
    return img.resize((w, max(8, int(h / k))), Image.BILINEAR).resize((w, h), Image.BILINEAR)


def _ease_io(q):
    q = min(1.0, max(0.0, q)); return q * q * (3 - 2 * q)


def whip(a, b, p, kind='left'):
    """p 0..1: khung a lao ra, khung b lao vao, nhoe theo huong chuyen dong (manh nhat o giua)."""
    w, h = a.size; e = _ease_io(p); bl = 1 + 34 * (1 - abs(2 * p - 1)) ** 1.5
    out = Image.new('RGB', (w, h))
    if kind in ('left', 'right'):
        s = -1 if kind == 'left' else 1; off = int(e * w)
        out.paste(hblur(a, bl), (s * off, 0)); out.paste(hblur(b, bl), (s * off - s * w, 0))
    elif kind in ('up', 'down'):
        s = -1 if kind == 'up' else 1; off = int(e * h)
        out.paste(vblur(a, bl), (0, s * off)); out.paste(vblur(b, bl), (0, s * off - s * h))
    else:   # 'zoom': a phong to + mo dan, b tu to ve 1
        za = 1 + 0.35 * e; zb = 1.25 - 0.25 * e
        A = a.resize((int(w * za), int(h * za)), Image.BILINEAR).crop((int((w * za - w) / 2), int((h * za - h) / 2), int((w * za - w) / 2) + w, int((h * za - h) / 2) + h))
        B = b.resize((int(w * zb), int(h * zb)), Image.BILINEAR).crop((int((w * zb - w) / 2), int((h * zb - h) / 2), int((w * zb - w) / 2) + w, int((h * zb - h) / 2) + h))
        out = Image.blend(A, B, e)
    return out


KINDS = ['left', 'zoom', 'up', 'left', 'right', 'zoom']


def kind_for(k):
    return KINDS[k % len(KINDS)]


# ---------- am thanh ----------
def whoosh(d=0.45, vol=0.22, up=True, seed=0):
    """tieng vut: nhieu trang loc bang thong quet tan so + bao canh len/xuong."""
    n = int(d * SR); rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n)
    fc = (300 + 3200 * t) if up else (3500 - 3200 * t)
    # loc thong thap thay doi theo thoi gian (1 cuc) + thong cao don gian
    y = np.zeros(n, np.float32); lp = 0.0; prev = 0.0
    for i in range(n):
        a = min(1.0, 2 * np.pi * fc[i] / SR); lp += a * (x[i] - lp); y[i] = lp - 0.92 * prev; prev = lp
    env = np.sin(np.pi * t) ** 1.6
    y = y * env; y /= (np.abs(y).max() + 1e-6)
    return (y * vol).astype(np.float32)


def duck(music, voice, depth=0.6, att=0.06, rel=0.45):
    """ha nhac khi co giong: bao am cua giong -> giam nhac toi depth (0.6 = con 40%)."""
    n = min(len(music), len(voice))
    e = np.abs(voice[:n]); blk = int(SR * 0.02)
    m = e[: n // blk * blk].reshape(-1, blk).max(1)
    on = (m > 0.02).astype(np.float32)
    g = np.zeros_like(on); ka, kr = 0.02 / att, 0.02 / rel; cur = 0.0
    for i, v in enumerate(on):
        cur += (v - cur) * (ka if v > cur else kr); g[i] = cur
    gain = 1 - depth * np.repeat(g, blk)
    out = music.copy(); out[: len(gain)] *= gain
    return out


# ---------- chu nhay theo tu ----------
def word_times(words, t0, t1):
    """moc bat dau tung tu trong 1 cau: chia theo do dai (am tiet tieng Viet ~ 1 tu), them nghi o dau phay."""
    wts = []
    for w in words:
        wt = 1.0 + 0.12 * max(0, len(w) - 4)
        if w.endswith((',', ';', ':')): wt += 0.9
        if w.endswith(('.', '!', '?', '…')): wt += 0.6
        wts.append(wt)
    tot = sum(wts) or 1; t = t0; out = []
    for wt in wts:
        out.append(t); t += (t1 - t0) * wt / tot
    return out
