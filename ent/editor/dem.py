"""Chuyen Dem - dang moi 28/11 (chu chot: hoc mau "xoi 4 gio sang"): truyen ma hu cau nhe, cam dong.
Ve bang code: nhan vat khong mat (dau tron toi, nhan ra bang dang + trang phuc), moi canh 1 nguon sang,
tuong van san, toi dan ra mep, may quay day cham, chuyen canh mo dan, phu de nho chu trang khong nen.
SPEC_JSON: {"sentences":[...], "scenes":[[sent_idx, "ten_canh"], ...], "voice_urls":[...], "pauses":[...],
            "texts":[...], "sents":[...], "title":"...", "music": "..."}
Chay thu khong giong: DRY=1 (moi cau ~ so chu * 0.33s).  Soi khung: FRAMES_AT="1.0,12.5" -> out/at_NN.png
"""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safezone  # noqa: E402
from chart20 import F  # noqa: E402

W, H, FPS = 1080, 1920, 30
ROOT = os.getcwd(); OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
HEAD = (24, 21, 19); INK = (14, 12, 11)
WARM = np.array([1.0, 0.78, 0.52], np.float32); COLD = np.array([0.62, 0.72, 0.9], np.float32)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------------- ve co ban ----------------
def tex(seed, base, amp=14, blobs=60):
    """tuong van san: nen + dom loang + soc nho."""
    r = random.Random(seed); im = Image.new('RGB', (W, H), base); d = ImageDraw.Draw(im)
    for _ in range(blobs):
        x, y, rr = r.uniform(0, W), r.uniform(0, H), r.uniform(60, 260); k = r.uniform(-amp, amp)
        d.ellipse([x - rr, y - rr * .7, x + rr, y + rr * .7], fill=tuple(max(0, min(255, int(c + k))) for c in base))
    im = im.filter(ImageFilter.GaussianBlur(40))
    a = np.asarray(im).astype(np.int16) + np.random.default_rng(seed).integers(-7, 8, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def lightmap(lights, amb):
    L = np.zeros((H, W, 3), np.float32) + np.array(amb, np.float32)
    for (x, y, r, col, k) in lights:
        g = np.exp(-(((XX - x) ** 2 + ((YY - y) * 0.9) ** 2) / (2 * r * r)))[..., None]
        L += g * (np.array(col, np.float32) * k)
    return L


def vignette():
    v = 1 - 0.55 * np.clip((((XX - W / 2) / (W * .62)) ** 2 + ((YY - H * .5) / (H * .6)) ** 2), 0, 1)
    return v[..., None].astype(np.float32)


VIG = vignette()
GRAIN = [np.random.default_rng(i).normal(0, 3.5, (H // 2, W // 2, 1)).astype(np.float32) for i in range(4)]


def person(d, x, fy, h, kind, flip=1, ph=0.0, pose='down', bow=0.0):
    """nhan vat khong mat. fy = chan, h = chieu cao. kind: ba / be / me. flip 1 nhin phai, -1 nhin trai.
    ph: pha buoc di (0 = dung yen). pose: down | hold (om bat truoc nguc) | sit."""
    s = h / 100.0; bob = abs(math.sin(ph * math.pi)) * 1.2 * s if ph else 0
    sit = pose == 'sit'
    hip = fy - (30 if sit else 46) * s - bob; sh = fy - (78 if not sit else 62) * s - bob
    hx = x + flip * (bow * 18 * s + (3 * s if kind == 'ba' else 0)); hy = sh - 11 * s + bow * 10 * s
    sw, hw = (13 if kind != 'be' else 11) * s, (12 if kind != 'me' else 10) * s
    if kind == 'ba': shirt, pant = (84, 66, 54), (32, 30, 32)
    elif kind == 'be': shirt, pant = (196, 196, 190), (38, 52, 88)
    else: shirt, pant = (128, 144, 162), (62, 70, 88)
    sk = (128, 96, 76)
    # chan
    for k, sg in ((0, -1), (1, 1)):
        off = math.sin((ph + k * .5) * math.pi * 2) * 7 * s if ph else 0
        lx = x + sg * 4.5 * s
        if sit:
            d.line([(lx, hip), (lx + flip * 16 * s, hip), (lx + flip * 16 * s, fy)], fill=pant if kind != 'be' else sk, width=int(6 * s), joint='curve')
        else:
            col = sk if kind == 'be' else pant
            d.line([(lx, hip), (lx + off, fy - 2 * s)], fill=col, width=int(6.5 * s))
            if kind == 'be': d.rectangle([lx - 4 * s, hip - 2 * s, lx + 4 * s, hip + 12 * s], fill=pant)
            d.ellipse([lx + off - 4 * s, fy - 4 * s, lx + off + 5 * s, fy + 1 * s], fill=INK)
    # than (ao dai xuong qua hong)
    tl = fy - (40 if kind != 'be' else 44) * s - bob if not sit else hip + 4 * s
    tx = flip * bow * 12 * s
    d.polygon([(x - sw + tx, sh), (x + sw + tx, sh), (x + hw + 2 * s, tl), (x - hw - 2 * s, tl)], fill=shirt, outline=INK, width=2)
    if kind == 'me':
        for j in range(-2, 3):
            d.line([(x + j * 4.5 * s + tx * .6, sh + 2 * s), (x + j * 4.5 * s, tl - 2 * s)], fill=(214, 224, 236), width=max(1, int(1.6 * s)))
    if kind == 'be':
        d.polygon([(x - 4 * s + tx, sh + 1 * s), (x + 4 * s + tx, sh + 1 * s), (x + tx, sh + 11 * s)], fill=(178, 40, 36))
    if kind == 'ba':
        d.line([(x - 3 * s + tx, sh + 4 * s), (x - 3 * s, tl - 4 * s)], fill=(84, 62, 46), width=max(1, int(1.2 * s)))
    # tay
    for sg in (-1, 1):
        ax = x + sg * sw * .9 + tx
        if pose == 'hold' or (pose == 'sit' and sg == 1):
            ex = x + flip * 10 * s + tx; ey = sh + 24 * s
            d.line([(ax, sh + 3 * s), (ax + sg * 2 * s, sh + 20 * s), (ex, ey)], fill=shirt, width=int(5 * s), joint='curve')
            d.ellipse([ex - 3 * s, ey - 3 * s, ex + 3 * s, ey + 3 * s], fill=sk)
        else:
            sw_ = math.sin((ph + (sg > 0) * .5) * math.pi * 2) * 5 * s if ph else 0
            ex, ey = ax + sg * 3 * s + sw_, sh + 34 * s
            d.line([(ax, sh + 3 * s), (ex, ey)], fill=shirt, width=int(5 * s))
            d.ellipse([ex - 3 * s, ey - 2 * s, ex + 3 * s, ey + 4 * s], fill=sk)
            if kind == 'me' and sg == flip: d.rectangle([ex - 3.4 * s, ey - 3.5 * s, ex + 3.4 * s, ey - 1.8 * s], fill=(240, 240, 236))
    # dau (khong mat) + toc/khan
    r = 8.5 * s if kind != 'be' else 9.5 * s
    d.line([(x + tx, sh), (hx, hy + r * .6)], fill=HEAD, width=int(4 * s))
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=HEAD)
    if kind == 'ba':
        d.chord([hx - r * 1.12, hy - r * 1.15, hx + r * 1.12, hy + r * .9], 180, 360, fill=(70, 58, 50))
        d.polygon([(hx - flip * r, hy - r * .1), (hx - flip * (r + 7 * s), hy + r * .5), (hx - flip * (r + 2 * s), hy + r * .9)], fill=(70, 58, 50))
    elif kind == 'me':
        d.ellipse([hx - flip * (r + 3 * s) - 4 * s, hy - r * .6 - 4 * s, hx - flip * (r + 3 * s) + 4 * s, hy - r * .6 + 4 * s], fill=(12, 10, 10))
    else:
        d.chord([hx - r, hy - r * 1.05, hx + r, hy + r * .2], 180, 360, fill=(10, 9, 9))
    # vien sang mo phia nguon sang
    d.arc([hx - r, hy - r, hx + r, hy + r], 200 if flip > 0 else -20, 300 if flip > 0 else 80, fill=(70, 58, 48), width=max(1, int(1.2 * s)))


def steam(d, x, y, t, n=3, h=220, col=(190, 182, 170), w=3):
    for k in range(n):
        ph = t * .6 + k * .37; a = (ph % 1.0)
        pts = [(x + (k - 1) * 22 + math.sin((j / 10 + ph) * 6) * 12, y - j / 10 * h * (0.6 + a * .4)) for j in range(11)]
        d.line(pts, fill=col, width=w, joint='curve')


def bowl(d, x, y, s=1.0, chao=True, cover=False, spoon=0, steam_t=None):
    """bat cháo nhin nghieng. spoon: 0 khong, 1 dung trong bat, -1 up xuong canh bat."""
    w, hh = 70 * s, 34 * s
    d.chord([x - w, y - hh, x + w, y + hh], 0, 180, fill=(226, 222, 210), outline=INK, width=2)
    d.ellipse([x - w, y - 10 * s, x + w, y + 10 * s], fill=(222, 206, 160) if chao else (200, 196, 186), outline=INK, width=2)
    if chao:
        for j in range(5): d.ellipse([x - 40 * s + j * 18 * s, y - 4 * s, x - 34 * s + j * 18 * s, y + 1 * s], fill=(96, 140, 70))
    d.rectangle([x - 22 * s, y + hh - 2, x + 22 * s, y + hh + 6 * s], fill=(200, 196, 186), outline=INK, width=2)
    if cover: d.chord([x - w - 4, y - 46 * s, x + w + 4, y + 16 * s], 180, 360, fill=(120, 128, 120), outline=INK, width=2)
    if spoon == 1: d.line([(x + 18 * s, y - 2 * s), (x + 52 * s, y - 52 * s)], fill=(232, 230, 222), width=int(7 * s))
    if spoon == -1:
        d.ellipse([x + w + 10 * s, y + 18 * s, x + w + 44 * s, y + 34 * s], fill=(232, 230, 222), outline=INK, width=2)
        d.line([(x + w + 40 * s, y + 26 * s), (x + w + 100 * s, y + 30 * s)], fill=(232, 230, 222), width=int(6 * s))
    if steam_t is not None: steam(d, x, y - 20 * s, steam_t, h=200 * s, w=max(2, int(3 * s)))


def coin(d, x, y, r, wet=False):
    d.ellipse([x - r, y - r * .45, x + r, y + r * .45], fill=(168, 140, 70), outline=(90, 70, 30), width=2)
    d.ellipse([x - r * .55, y - r * .25, x + r * .55, y + r * .25], outline=(120, 96, 44), width=2)
    if wet:
        d.ellipse([x + r * .2, y - r * .3, x + r * .42, y - r * .12], fill=(236, 236, 226))


# ---------------- bo canh ----------------
class Quan:
    """quan chao truoc cong benh vien: den duong ben trai, cong sang ben phai."""
    def __init__(s, mode='dem'):
        s.mode = mode
        base = (40, 36, 34) if mode != 'sang' else (58, 64, 72)
        s.bg = tex(3, base); d = ImageDraw.Draw(s.bg)
        d.rectangle([0, 1250, W, H], fill=(26, 24, 23) if mode != 'sang' else (44, 48, 54))
        # tuong rao + cong benh vien
        d.rectangle([0, 700, W, 1250], fill=tuple(c + 6 for c in base))
        for x in range(0, W, 120): d.line([(x, 700), (x, 1250)], fill=tuple(c - 6 for c in base), width=3)
        d.rectangle([760, 620, 1080, 1250], fill=(196, 168, 120) if mode != 'sang' else (150, 166, 184))
        d.rectangle([740, 600, 1080, 640], fill=(60, 56, 54))
        with safezone.decor():
            d.rectangle([880, 470, 960, 550], fill=(236, 232, 224)); d.rectangle([908, 482, 932, 538], fill=(176, 36, 36)); d.rectangle([892, 498, 948, 522], fill=(176, 36, 36))
        # den duong
        d.rectangle([150, 380, 162, 1250], fill=(30, 28, 28)); d.line([(156, 392), (250, 392)], fill=(30, 28, 28), width=10)
        d.ellipse([228, 392, 272, 422], fill=(255, 236, 190) if mode != 'sang' else (120, 120, 118))
        # ban + noi
        s.tbl = (300, 1060, 720, 1250)
        L = [(250, 420, 330, (1.0, .8, .55), 1.5), (900, 950, 420, (1.0, .86, .62), .9), (560, 1000, 260, (1.0, .74, .5), .9)]
        if mode == 'sang': L = [(800, 700, 600, (0.7, .8, .95), 1.0), (300, 500, 500, (0.6, .7, .9), .5)]
        if mode == 'mua': L = [(250, 420, 300, (1.0, .8, .55), 1.3), (560, 1000, 240, (1.0, .74, .5), .7)]
        s.L = lightmap(L, (0.16, 0.16, 0.2) if mode != 'sang' else (0.38, 0.42, 0.5))

    def draw(s, im, t, st):
        d = ImageDraw.Draw(im)
        if st.get('ba', True): person(d, 470, 1120, 560, 'ba', 1, pose='hold' if st.get('muc') else 'down')
        x0, y0, x1, y1 = s.tbl
        d.rectangle([x0, y0, x1, y0 + 26], fill=(96, 66, 44), outline=INK, width=2)
        d.rectangle([x0 + 20, y0 + 26, x0 + 40, y1], fill=(70, 48, 32)); d.rectangle([x1 - 40, y0 + 26, x1 - 20, y1], fill=(70, 48, 32))
        d.rectangle([x0 + 10, y0 + 26, x1 - 10, y1 - 30], fill=(74, 52, 36), outline=INK, width=2)
        for yy in range(y0 + 60, y1 - 30, 34): d.line([(x0 + 12, yy), (x1 - 12, yy)], fill=(62, 44, 30), width=2)
        with safezone.decor():
            d.rectangle([x0 + 150, y0 + 100, x0 + 270, y0 + 140], fill=(214, 200, 168)); d.text((x0 + 165, y0 + 100), 'CHÁO', font=F(True, 30), fill=(150, 40, 34))
        d.rounded_rectangle([590, 900, 710, 1062], 12, fill=(150, 150, 148), outline=INK, width=2)
        d.rectangle([580, 896, 720, 914], fill=(120, 120, 118))
        if s.mode != 'sang': steam(d, 650, 890, t, h=240)
        nb = st.get('bowls', 0)
        for k in range(nb): bowl(d, 380 + k * 120, 1046, .7, steam_t=t + k if s.mode != 'sang' else None)
        if st.get('cover'): bowl(d, 420, 1046, .7, cover=True)
        be = st.get('be')
        if be:
            if be == 'vao':
                q = min(1.0, t / 3.0); x = 1000 - 220 * (q * (2 - q)); person(d, x, 1270, 380, 'be', -1, ph=t * 1.6 if q < 1 else 0)
            elif be == 'ngoi':
                d.rectangle([760, 1200, 860, 1214], fill=(120, 40, 34)); d.rectangle([772, 1214, 784, 1270], fill=(90, 30, 26)); d.rectangle([836, 1214, 848, 1270], fill=(90, 30, 26))
                person(d, 810, 1270, 380, 'be', -1, pose='sit'); bowl(d, 760, 1150, .45)
        if st.get('me'): person(d, 830, 1290, 560, 'me', -1)
        if s.mode == 'mua':
            r = random.Random(int(t * FPS) // 2)
            for _ in range(120):
                x, y = r.uniform(0, W), r.uniform(0, H); d.line([(x, y), (x - 8, y + 46)], fill=(120, 130, 140), width=2)


class Can:
    """can canh tren mat ban go (dong xu, bat chao, tay)."""
    def __init__(s, mode='dem', seed=5):
        s.mode = mode
        s.bg = tex(seed, (52, 40, 30) if mode != 'sang' else (70, 72, 76), amp=10)
        d = ImageDraw.Draw(s.bg)
        d.rectangle([0, 900, W, H], fill=(92, 64, 42) if mode != 'sang' else (88, 80, 74))
        for y in range(930, H, 70): d.line([(0, y), (W, y + 8)], fill=(76, 52, 34) if mode != 'sang' else (74, 68, 64), width=3)
        amb = (0.14, 0.13, 0.14) if mode != 'sang' else (0.42, 0.46, 0.55)
        L = [(540, 1050, 360, (1.0, .78, .52), 1.25)] if mode != 'sang' else [(700, 800, 600, (.7, .8, .95), .7)]
        s.L = lightmap(L, amb)

    def draw(s, im, t, st):
        d = ImageDraw.Draw(im); k = st.get('k')
        if k == 'hop':   # hop sat dung dong xu
            op = st.get('mo', 1.0) if not callable(st.get('mo')) else st['mo'](t)
            d.rectangle([260, 980, 820, 1210], fill=(70, 78, 84), outline=INK, width=3)
            d.rectangle([280, 1000, 800, 1190], fill=(38, 42, 46))
            r = random.Random(9)
            for j in range(26):
                x, y = r.uniform(320, 760), r.uniform(1030, 1160); coin(d, x, y, 42, wet=st.get('wet') and j % 2 == 0)
            if st.get('wet'):
                for j in range(160):
                    x, y = r.uniform(300, 780), r.uniform(1020, 1180); d.point((x, y), fill=(196, 176, 130))
                for j in range(5):
                    x = 340 + j * 100; yy = 1190 + (t * 30 + j * 13) % 60
                    d.ellipse([x - 5, yy - 8, x + 5, yy + 6], fill=(150, 170, 180))
            if op < 1: d.polygon([(260, 980 - 260 * (1 - op)), (820, 980 - 260 * (1 - op)), (820, 980), (260, 980)], fill=(84, 92, 98), outline=INK)
        elif k == 'tay2':   # tay gio 2 ngon + noi
            d.rounded_rectangle([600, 760, 900, 1000], 16, fill=(150, 150, 148), outline=INK, width=2); steam(d, 750, 750, t, h=300)
            q = min(1.0, t / .6); y = 1500 - 420 * q * (2 - q)
            d.rectangle([330, y + 120, 430, H], fill=(214, 214, 206), outline=INK, width=2)
            d.rounded_rectangle([320, y, 440, y + 150], 30, fill=(128, 96, 76), outline=INK, width=2)
            for dx in (0, 50): d.rounded_rectangle([330 + dx, y - 170, 370 + dx, y + 20], 20, fill=(128, 96, 76), outline=INK, width=2)
        elif k == 'haibat':  # hai bat chao vua muc
            d.rounded_rectangle([620, 640, 960, 940], 16, fill=(150, 150, 148), outline=INK, width=2); steam(d, 790, 630, t, h=240)
            q = min(1.0, t / .8)
            bowl(d, 330, 1090, 1.6, steam_t=t); bowl(d, 640 + 300 * (1 - q), 1130, 1.6, steam_t=t + .5)
        elif k == 'xu':     # dat tung dong xu canh noi
            d.rounded_rectangle([600, 700, 940, 1000], 16, fill=(150, 150, 148), outline=INK, width=2); steam(d, 770, 690, t, h=260)
            n = min(7, int(t / .45) + 1)
            for j in range(n): coin(d, 380, 1080 - j * 16, 70)
            if n < 7:
                q = (t / .45) % 1; coin(d, 380, 1080 - n * 16 - 200 * (1 - q), 70)
        elif k == 'bat':    # bat cháo dau ban + thia
            bowl(d, 540, 1080, 2.4, spoon=st.get('spoon', 1) if not callable(st.get('spoon')) else st['spoon'](t), steam_t=t if s.mode != 'sang' else None)
        elif k == 'anh':    # tay nguoi me cam anh con
            d.rectangle([340, 820, 740, 1240], fill=(224, 216, 196), outline=INK, width=3)
            d.rectangle([370, 850, 710, 1170], fill=(96, 104, 110))
            person(d, 540, 1200, 400, 'be', 1)
            for sg in (-1, 1):
                hx = 540 + sg * 215
                d.polygon([(hx - 40, 1300), (hx + 40, 1300), (hx + sg * 120 + 60, H), (hx + sg * 120 - 60, H)], fill=(128, 144, 162), outline=INK)
                d.rounded_rectangle([hx - 34, 1160, hx + 34, 1290], 28, fill=(128, 96, 76), outline=INK, width=2)
                d.rectangle([hx - 30, 1268, hx + 30, 1280], fill=(240, 240, 236))


class Cong:
    """cau be om bat chao di ve phia day nha benh nhan (nhin tu sau lung)."""
    def __init__(s):
        s.bg = tex(11, (34, 32, 34)); d = ImageDraw.Draw(s.bg)
        d.polygon([(0, H), (W, H), (640, 1000), (440, 1000)], fill=(30, 28, 28))
        d.rectangle([420, 640, 660, 1000], fill=(250, 232, 190))
        d.rectangle([400, 620, 680, 640], fill=(50, 46, 46))
        s.L = lightmap([(540, 840, 320, (1.0, .86, .62), 1.4), (540, 1300, 300, (1.0, .8, .6), .45)], (0.14, 0.14, 0.17))

    def draw(s, im, t, st):
        d = ImageDraw.Draw(im); q = 0.55 if st.get('bia') else min(1.0, t / max(1.0, st['dur'])); y = 1500 - 420 * q; sc = 1 - .55 * q
        person(d, 540, y, 420 * sc, 'be', 1, ph=0 if st.get('bia') else t * 1.4, pose='hold')


SCENES = {
    'bia': lambda: (Cong(), {'bia': True}),
    'xu_uot': lambda: (Can('dem', 5), {'k': 'hop', 'wet': True}),
    'quan': lambda: (Quan('dem'), {}),
    'quan_vao': lambda: (Quan('dem'), {'be': 'vao'}),
    'tay2': lambda: (Can('dem', 6), {'k': 'haibat'}),
    'quan_an': lambda: (Quan('dem'), {'be': 'ngoi', 'bowls': 1}),
    'xu_dat': lambda: (Can('dem', 7), {'k': 'xu'}),
    'di_vao': lambda: (Cong(), {}),
    'mua': lambda: (Quan('mua'), {}),
    'mua_phan': lambda: (Quan('mua'), {'cover': True, 'muc': True}),
    'sang_me': lambda: (Quan('sang'), {'me': True}),
    'anh_con': lambda: (Can('dem', 8), {'k': 'anh'}),
    'mo_hop': lambda: (Can('dem', 5), {'k': 'hop', 'wet': True, 'mo': lambda t: min(1.0, t / 1.2)}),
    'quan_hai': lambda: (Quan('dem'), {'bowls': 2, 'muc': True}),
    'bat_dem': lambda: (Can('dem', 9), {'k': 'bat', 'spoon': 1}),
    'bat_sang': lambda: (Can('sang', 9), {'k': 'bat', 'spoon': 1}),
    'bat_up': lambda: (Can('sang', 9), {'k': 'bat', 'spoon': lambda t: 1 if t < 1.4 else -1}),
}
# can canh dung gan (zoom/tam may quay)
CAM = {'quan': (1.15, 560, 1000), 'quan_vao': (1.15, 600, 1000), 'quan_hai': (1.15, 540, 1000), 'mua': (1.15, 560, 1000), 'xu_uot': (1.3, 540, 1100), 'tay2': (1.2, 600, 980), 'xu_dat': (1.2, 600, 960), 'anh_con': (1.15, 540, 1080),
       'mo_hop': (1.3, 540, 1060), 'bat_dem': (1.3, 560, 1020), 'bat_sang': (1.3, 560, 1020), 'bat_up': (1.3, 580, 1040),
       'mua_phan': (1.35, 470, 1010), 'quan_an': (1.05, 640, 1050), 'sang_me': (1.1, 640, 1000)}


def make_amb(path, D, hits, sr=44100):
    """nen am thanh dem (tu tao): u tram 2 tang song + gio nau loc thap, phong to dan; 'thinh' trầm o canh danh dau '!'."""
    import wave
    n = int(D * sr); t = np.arange(n) / sr; rng = np.random.default_rng(5)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * t / 9.0)
    drone = (np.sin(2 * np.pi * 55 * t) * .5 + np.sin(2 * np.pi * 82.4 * t + 1) * .3 + np.sin(2 * np.pi * 110.3 * t) * .12) * lfo * .16
    wn = np.cumsum(rng.normal(0, 1, n)); wn -= np.convolve(wn, np.ones(4000) / 4000, 'same'); wn /= (np.abs(wn).max() + 1e-6)
    wind = wn * (0.5 + 0.5 * np.sin(2 * np.pi * t / 13.0 + 2)) * .12
    x = drone + wind
    for h in hits:
        i0 = int(h * sr); L = int(2.2 * sr); tt = np.arange(min(L, n - i0)) / sr
        if len(tt) <= 0: continue
        x[i0:i0 + len(tt)] += np.sin(2 * np.pi * (48 - 14 * tt) * tt) * np.exp(-tt * 2.2) * .9
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (D - t) / 2.0); x = np.clip(x * fade, -1, 1)
    y = (np.stack([x, x], 1) * 32767 * .8).astype(np.int16)
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(y.tobytes())


def wrap(d, s, f, mw):
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= mw or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out


def main():
    sp = json.loads(os.environ['SPEC_JSON']) if os.environ.get('SPEC_JSON', '').strip().startswith('{') else json.load(open(os.environ['SPEC_JSON']))
    if sp.get('pack'):   # bo canh rieng tung truyen: editor/dem_<pack>.py co ham register(SCENES, CAM)
        __import__('dem_' + sp['pack']).register(SCENES, CAM)
    S = sp.get('sentences') or sp.get('texts'); DRY = os.environ.get('DRY') == '1'
    # ---- giong: moi doan W87 -> (bat dau, ket thuc, chu, cau) ----
    segs, off, parts = [], 0.3, []
    if DRY:
        for i, s in enumerate(S):
            dd = max(1.6, len(s.split()) * .36); segs.append((off, off + dd - .5, s, i)); off += dd
    else:
        from series import get, voice_part
        sents = sp.get('sents') or list(range(len(sp['voice_urls'])))
        for i, u in enumerate(sp['voice_urls']):
            pth = u if os.path.exists(u) else get(u, os.path.join(OUT, f'vp{i}.mp3'))
            wav = os.path.join(OUT, f'vp{i}.wav'); dd, _ = voice_part(pth, wav, sp, i)
            pz = float((sp.get('pauses') or [0.45] * 99)[i] or 0)
            segs.append((off, off + dd - pz, (sp.get('texts') or S)[i], sents[i])); parts.append(wav); off += dd
    TAIL = 3.2; D = off + TAIL
    st0 = {}
    for a, b, _, si in segs: st0.setdefault(si, a)
    # ---- canh ----
    sc = sp['scenes']; spans = []
    last = [0.0]

    def start_of(key):   # key: so thu tu cau, hoac cum chu DAU doan (khop texts cua W87), tim tu sau canh truoc
        if isinstance(key, int): return st0.get(key, 0)
        kk = key.lower().strip('“"')
        for test in (lambda tx: tx.startswith(kk), lambda tx: kk in tx):
            for a_, _, tx, _ in segs:
                if a_ >= last[0] - 1e-6 and test(tx.lower().strip('“"')): return a_
        raise SystemExit('khong thay cum canh: ' + key)
    for k, (si, name) in enumerate(sc):
        a = 0.0 if k == 0 else start_of(si) - 0.15
        last[0] = a + 0.2
        b = start_of(sc[k + 1][0]) - 0.15 if k + 1 < len(sc) else D
        spans.append((a, b, name))
    COVER = float(sp.get('cover_sec', 0.7)) if sp.get('cover') else 0.0
    if COVER:
        spans[0] = (COVER, spans[0][1], spans[0][2]); spans.insert(0, (0.0, COVER, sp['cover']))
    hook_end = max((b_ for a_, b_, _, si in segs if si == segs[0][3]), default=3.0) + .3
    built = {}

    def get_scene(name):
        if name not in built:
            obj, st = SCENES[name.rstrip('!')](); built[name] = (obj, st)
        return built[name]

    def render_scene(k, t):
        a, b, name = spans[k]; obj, st = get_scene(name); lt = t - a
        im = obj.bg.copy(); st = dict(st, dur=b - a); obj.draw(im, lt, st)
        arr = np.asarray(im).astype(np.float32) * obj.L * 1.3
        flick = 1 + 0.025 * math.sin(t * 9.1) * math.sin(t * 3.7)
        arr = arr * flick * VIG
        g = GRAIN[int(t * FPS / 3) % len(GRAIN)]   # hat phim doi 10 lan/giay (nhe file)
        arr += np.repeat(np.repeat(g, 2, 0), 2, 1)
        out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        if hasattr(obj, 'post'): obj.post(out, lt, st)   # bong ma / chop sang ve SAU anh sang
        z0, cx, cy = CAM.get(name.rstrip('!'), (1.0, 540, 960)); q = lt / max(1.0, b - a); z = z0 * (1 + .07 * q)
        w, h = W / z, H / z; x0 = min(max(0, cx - w / 2), W - w); y0 = min(max(0, cy - h / 2), H - h)
        return out.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))

    fS = F(True, 42)

    def frame(t):
        k = max(i for i in range(len(spans)) if spans[i][0] <= t + 1e-6)
        im = render_scene(k, t)
        if k > 0 and t - spans[k][0] < .6 and not (COVER and k == 1):
            im = Image.blend(render_scene(k - 1, t), im, (t - spans[k][0]) / .6)
        if t > D - TAIL + .4:   # ket: toi dan + ten kenh
            q = min(1.0, (t - (D - TAIL + .4)) / 1.2)
            im = Image.blend(im, Image.new('RGB', (W, H), (6, 6, 8)), .85 * q)
            d = ImageDraw.Draw(im); tt = sp.get('title', 'CHUYỆN ĐÊM'); f = F(True, 56)
            d.text(((W - d.textlength(tt, font=f)) / 2, 880), tt, font=f, fill=tuple(int(c * q) for c in (220, 200, 160)))
            return im
        hk = (sp.get('hook') or '').strip().upper()
        if hk and t < hook_end:
            a_ = 1.0 if t < hook_end - .35 else max(0.0, (hook_end - t) / .35)
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            from series import wrap_bal
            fH = F(True, 100)
            while len(wrap_bal(od, hk, fH, 780)) > 2 and fH.size > 60: fH = F(True, fH.size - 4)
            ls = wrap_bal(od, hk, fH, 780); lh = int(fH.size * 1.16); y0 = 372
            od.rectangle([0, 268, W, y0 + len(ls) * lh + 30], fill=(0, 0, 0, int(120 * a_)))
            kick = sp.get('kicker', 'CHUYỆN ĐÊM'); fK = F(True, 38); kw = od.textlength(kick, font=fK)
            od.rounded_rectangle([(W - kw) / 2 - 22, y0 - 88, (W + kw) / 2 + 22, y0 - 28], 10, fill=(150, 28, 26, int(235 * a_)))
            od.text(((W - kw) / 2, y0 - 84), kick, font=fK, fill=(250, 240, 226, int(255 * a_)))
            for j, ln in enumerate(ls):
                x = (W - od.textlength(ln, font=fH)) / 2
                od.text((x, y0 + j * lh), ln, font=fH, fill=(255, 226, 160, int(255 * a_)), stroke_width=5, stroke_fill=(0, 0, 0, int(255 * a_)))
            im.paste(ov, (0, 0), ov)
        cur = next((s_ for s_ in reversed(segs) if s_[0] - .12 <= t < s_[1] + .25), None)   # 28/11: phu de ra TRUOC loi 0,12s, khong mo dan
        if cur:
            d = ImageDraw.Draw(im); a_ = min(1.0, (cur[1] + .25 - t) / .15)
            ls = wrap(d, cur[2], fS, 760)[:3]; y = 1444 - len(ls) * 56
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            for j, ln in enumerate(ls):
                x = (W - od.textlength(ln, font=fS)) / 2
                od.text((x + 2, y + j * 56 + 3), ln, font=fS, fill=(0, 0, 0, int(200 * a_)))
                od.text((x, y + j * 56), ln, font=fS, fill=(246, 242, 232, int(255 * a_)))
            im.paste(ov, (0, 0), ov)
        return im

    at = os.environ.get('FRAMES_AT')
    if at:
        for j, x in enumerate(at.split(',')): frame(float(x)).save(os.path.join(OUT, f'at_{j:02d}.png'))
        print('spans', [(round(a, 1), n) for a, b, n in spans], 'D', round(D, 1)); return
    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    for fi in range(int(D * FPS)): p.stdin.write(frame(fi / FPS).tobytes())
    p.stdin.close(); p.wait()
    # ---- am thanh: giong + nen dem (gio + de keu nhe tu tao) ----
    amb = os.path.join(OUT, 'amb.wav'); make_amb(amb, D, [a for a, b, n in spans if n.endswith('!')])
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    if parts:
        lst = os.path.join(OUT, 'vlist.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
        voice = os.path.join(OUT, 'voice.wav')
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice])
        mus = os.path.join(ROOT, 'editor', 'story', sp.get('music', 'music_b.mp3'))
        ins = ['-i', voice, '-i', amb] + (['-stream_loop', '-1', '-i', mus] if os.path.exists(mus) else [])
        mix = '[1:a]adelay=300|300[v];[2:a]volume=0.9[n];' + ('[3:a]volume=0.05[m];[v][n][m]amix=inputs=3' if os.path.exists(mus) else '[v][n]amix=inputs=2') + \
              ':duration=longest:normalize=0,apad,loudnorm=I=-16:TP=-1.5[a]'
    else:
        ins = ['-i', amb]; mix = '[1:a]anull[a]'
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw] + ins + ['-filter_complex', mix, '-map', '0:v', '-map', '[a]',
                           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4')); print('ok', round(D, 2))


if __name__ == '__main__':
    main()
