# -*- coding: utf-8 -*-
"""Reels quang cao Nhip 1080x1920: mockup chat + chu dong + giong doc + nhac nen tu tong hop.
Dung: python3 nhip_reel.py <thu_muc_giong v1..v6.wav> <out.mp4>
"""
import sys, os, json, math, wave, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
TEAL = (14, 107, 92); TEAL_D = (8, 70, 60); MINT = (227, 241, 238); OFF = (245, 246, 244)
INK = (22, 24, 29); GREY = (120, 128, 136); ORANGE = (255, 138, 61); RED = (226, 64, 64)
NAVY = (14, 20, 38); NAVY2 = (28, 36, 64); WHITE = (255, 255, 255)

FD = os.environ.get('FONT_DIR', '')
S = {'shop': 'Shop Thời Trang Mây', 'avatar': 'M', 's1_time': '23:47', 's1_sub': 'Hôm nay đăng gì đây?',
     's2_title': '3 ngày không đăng', 's2_stamp': 'KHÁCH QUÊN SHOP',
     's3_req': 'Viết bài giới thiệu váy linen màu kem, giọng vui tươi',
     's3_body': ['Nắng lên rồi, diện váy linen màu kem', 'đi cà phê là chuẩn bài luôn nè!', 'Chất mát, dáng suông, mặc cả ngày', 'vẫn thoải mái...'],
     's3_tags': '#vaylinen #thoitrangnu #outfitdicafe', 'product': 'dress', 'pcolor': [214, 182, 140], 'pbg': [250, 232, 214],
     's4_req': 'Làm Reels 15 giây khoe mẫu váy mới cho kênh thời trang'}
def font(w, size):
    cands = []
    if FD:
        cands.append(os.path.join(FD, 'BeVietnamPro-%s.ttf' % w))
    cands.append('/usr/share/fonts/opentype/inter/Inter-%s.otf' % w)
    cands.append('fonts/BeVietnamPro-%s.ttf' % w)
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

_fc = {}
def F(w, s):
    k = (w, s)
    if k not in _fc: _fc[k] = font(w, s)
    return _fc[k]

EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
_ec = {}
def emoji(ch, size):
    k = (ch, size)
    if k in _ec: return _ec[k]
    try:
        f = ImageFont.truetype(EMO, 109)
        im = Image.new('RGBA', (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
        bb = im.getbbox() or (0, 0, 1, 1)
        im = im.crop(bb).resize((size, size), Image.LANCZOS)
    except Exception:
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    _ec[k] = im
    return im

def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def back(t):
    t = max(0.0, min(1.0, t)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def clamp01(x): return max(0.0, min(1.0, x))

def wrap(d, text, f, maxw):
    words = text.split(' '); lines = []; cur = ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def rrect(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def shadow_layer(size, box, r, blur=24, alpha=70, off=(0, 14)):
    sh = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0] + off[0], box[1] + off[1], box[2] + off[0], box[3] + off[1]), radius=r, fill=(0, 0, 0, alpha))
    return sh.filter(ImageFilter.GaussianBlur(blur))

# ---------- phone mockup ----------
PX0, PY0, PW, PH = 150, 470, 780, 1180   # khung dien thoai (o giua)

def phone(base, dark, msgs, t, header=None, status_time='02:13', typing=None):
    """msgs: list of dict(side='l'|'r', text, at, tag(optional)) ; t: giay trong canh"""
    im = base
    header = header or S['shop']
    sh = shadow_layer((W, H), (PX0, PY0, PX0 + PW, PY0 + PH), 70, blur=30, alpha=110 if dark else 60)
    im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    bg = (22, 27, 44) if dark else WHITE
    rrect(d, (PX0, PY0, PX0 + PW, PY0 + PH), 70, (10, 10, 14))
    rrect(d, (PX0 + 14, PY0 + 14, PX0 + PW - 14, PY0 + PH - 14), 58, bg)
    # status bar
    fc = (230, 232, 240) if dark else INK
    d.text((PX0 + 70, PY0 + 40), status_time, font=F('SemiBold', 30), fill=fc)
    rrect(d, (PX0 + PW // 2 - 90, PY0 + 34, PX0 + PW // 2 + 90, PY0 + 74), 20, (10, 10, 14))
    d.rectangle((PX0 + PW - 140, PY0 + 48, PX0 + PW - 90, PY0 + 66), outline=fc, width=3)
    d.rectangle((PX0 + PW - 136, PY0 + 52, PX0 + PW - 104, PY0 + 62), fill=fc)
    # header
    hy = PY0 + 100
    d.line((PX0 + 14, hy + 96, PX0 + PW - 14, hy + 96), fill=(50, 56, 80) if dark else (232, 234, 238), width=2)
    d.ellipse((PX0 + 50, hy + 14, PX0 + 120, hy + 84), fill=(255, 196, 140))
    d.text((PX0 + 85, hy + 49), S['avatar'], font=F('Bold', 34), fill=(120, 60, 20), anchor='mm')
    d.text((PX0 + 140, hy + 18), header, font=F('Bold', 32), fill=fc)
    d.text((PX0 + 140, hy + 56), 'Messenger', font=F('Regular', 24), fill=GREY)
    # messages
    y = hy + 130
    fm = F('Medium', 34)
    maxw = PW - 260
    for m in msgs:
        if t < m['at']: continue
        k = back((t - m['at']) / 0.35)
        lines = []
        for para in m['text'].split('\n'):
            lines += wrap(d, para, fm, maxw)
        lh = 46
        bw = max(d.textlength(l, font=fm) for l in lines) + 56
        bh = len(lines) * lh + 34
        if m['side'] == 'l':
            x0 = PX0 + 44; col = (44, 52, 80) if dark else (240, 241, 244); tc = (240, 242, 248) if dark else INK
        else:
            x0 = PX0 + PW - 44 - bw; col = TEAL if m.get('ai') else (0, 132, 255); tc = WHITE
        sc = 0.6 + 0.4 * k
        alpha = clamp01(k * 1.4)
        bub = Image.new('RGBA', (int(bw) + 4, int(bh) + 4), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bub)
        rrect(bd, (0, 0, bw, bh), 30, col)
        yy = 17
        for l in lines:
            bd.text((28, yy), l, font=fm, fill=tc); yy += lh
        if alpha < 1:
            a = bub.split()[3].point(lambda p: int(p * alpha)); bub.putalpha(a)
        bub2 = bub.resize((max(1, int(bub.width * sc)), max(1, int(bub.height * sc))), Image.LANCZOS)
        ox = x0 if m['side'] == 'l' else x0 + bw - bub2.width
        im.alpha_composite(bub2, (int(ox), int(y + (bh - bub2.height) * 0.5)))
        if m.get('tag') and t > m['at'] + 0.4:
            ka = clamp01((t - m['at'] - 0.4) / 0.3)
            tg = m['tag']; ft = F('SemiBold', 24)
            tw = d.textlength(tg, font=ft)
            tx = PX0 + PW - 50 - tw if m['side'] == 'r' else PX0 + 50
            d.text((tx, y + bh + 6), tg, font=ft, fill=tuple(int(c * ka + (bg[i]) * (1 - ka)) for i, c in enumerate(TEAL if not dark else (120, 220, 200))))
            y += 36
        y += bh + 24
    if typing is not None and typing[0] <= t < typing[1]:
        x0 = PX0 + PW - 44 - 150; col = TEAL
        rrect(d, (x0, y, x0 + 150, y + 76), 30, col)
        for i in range(3):
            ph = math.sin((t * 8) - i * 0.9) * 0.5 + 0.5
            r = 9 + 3 * ph
            cx = x0 + 42 + i * 33; cy = y + 38 - 6 * ph
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255))
    return im

# ---------- chu lon ----------
def title(im, text, y, size, color, t, at=0.0, w='ExtraBold', anchor='mm', maxw=940, shadow=None, lh=1.12):
    if t < at: return
    k = back((t - at) / 0.4)
    d0 = ImageDraw.Draw(im)
    f = F(w, size)
    lines = wrap(d0, text, f, maxw)
    hh = int(size * lh)
    lay = Image.new('RGBA', (W, hh * len(lines) + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i, l in enumerate(lines):
        if shadow: ld.text((W // 2 + 4, 20 + i * hh + hh // 2 + 5), l, font=f, fill=shadow, anchor='mm')
        ld.text((W // 2, 20 + i * hh + hh // 2), l, font=f, fill=color, anchor='mm')
    sc = 0.7 + 0.3 * k
    a = clamp01((t - at) / 0.2)
    if a < 1: lay.putalpha(lay.split()[3].point(lambda p: int(p * a)))
    l2 = lay.resize((int(W * sc), int(lay.height * sc)), Image.LANCZOS)
    im.alpha_composite(l2, ((W - l2.width) // 2, int(y - l2.height / 2)))

def caption(im, text, t, dur):
    """phu de giong doc o duoi, chia cum 5-7 tu"""
    words = text.split(' ')
    chunks = []; cur = []
    for w_ in words:
        cur.append(w_)
        if len(cur) >= 6 or w_.endswith(('.', ',', '?')):
            chunks.append(' '.join(cur)); cur = []
    if cur: chunks.append(' '.join(cur))
    n = sum(len(c) for c in chunks); acc = 0; idx = 0
    for i, c in enumerate(chunks):
        if t * n / max(dur, 0.1) >= acc: idx = i
        acc += len(c)
    c = chunks[idx]
    d = ImageDraw.Draw(im); f = F('Bold', 44)
    lines = wrap(d, c, f, 900)
    y0 = 1735 - (len(lines) - 1) * 30
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f)
        rrect(d, (W / 2 - tw / 2 - 22, y0 + i * 60 - 34, W / 2 + tw / 2 + 22, y0 + i * 60 + 30), 18, (0, 0, 0, 170))
        d.text((W / 2, y0 + i * 60), l, font=f, fill=(255, 255, 255), anchor='mm')

def bg_night(t):
    im = Image.new('RGBA', (W, H), NAVY + (255,))
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(NAVY)[None, None, :] * (1 - g[..., None]) + np.array(NAVY2)[None, None, :] * g[..., None])
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    im = Image.fromarray(arr, 'RGB').convert('RGBA')
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for i in range(70):
        x = rnd.randint(0, W); y = rnd.randint(0, 900); r = rnd.choice([1, 2, 2, 3])
        tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        c = int(120 + 120 * tw)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(c, c, min(255, c + 20)))
    # trang
    d.ellipse((935, 50, 1035, 150), fill=(250, 236, 190))
    d.ellipse((910, 38, 1010, 138), fill=NAVY)
    return im

def bg_light(t, col=OFF):
    im = Image.new('RGBA', (W, H), col + (255,))
    d = ImageDraw.Draw(im)
    # hinh tron trang tri troi nhe
    for i, (cx, cy, r, c) in enumerate([(120, 300, 220, MINT), (980, 1500, 260, MINT), (90, 1660, 90, (255, 226, 204))]):
        dy = 14 * math.sin(t * 1.2 + i)
        d.ellipse((cx - r, cy - r + dy, cx + r, cy + r + dy), fill=c)
    return im

def brand_tag(im, dark=False):
    d = ImageDraw.Draw(im)
    f = F('ExtraBold', 34)
    tx = 'Nhịp'
    tw = d.textlength(tx, font=f)
    x = W - 60 - tw - 56
    rrect(d, (x, 60, W - 60, 120), 30, TEAL)
    d.ellipse((x + 18, 80, x + 38, 100), fill=ORANGE)
    d.text((x + 48, 90), tx, font=f, fill=WHITE, anchor='lm')

def product(d, cx, cy, k, kind, col):
    col = tuple(col); dark = tuple(max(0, c - 40) for c in col)
    if kind == 'cup':
        d.polygon([(cx - 90 * k, cy - 80 * k), (cx + 90 * k, cy - 80 * k), (cx + 65 * k, cy + 110 * k), (cx - 65 * k, cy + 110 * k)], fill=col)
        d.ellipse((cx - 90 * k, cy - 100 * k, cx + 90 * k, cy - 60 * k), fill=dark)
        d.arc((cx + 60 * k, cy - 40 * k, cx + 140 * k, cy + 40 * k), -90, 90, fill=col, width=int(16 * k))
        for i in range(3): d.arc((cx - 40 * k + i * 30 * k, cy - 190 * k, cx - 10 * k + i * 30 * k, cy - 110 * k), 90, 270, fill=(200, 200, 200), width=int(6 * k))
    elif kind == 'bottle':
        d.rounded_rectangle((cx - 60 * k, cy - 60 * k, cx + 60 * k, cy + 130 * k), radius=int(30 * k), fill=col)
        d.rectangle((cx - 25 * k, cy - 120 * k, cx + 25 * k, cy - 60 * k), fill=dark)
        d.rounded_rectangle((cx - 35 * k, cy - 150 * k, cx + 35 * k, cy - 115 * k), radius=int(8 * k), fill=(90, 90, 100))
        d.rounded_rectangle((cx - 45 * k, cy, cx + 45 * k, cy + 70 * k), radius=int(10 * k), fill=(255, 255, 255))
    elif kind == 'cake':
        d.rounded_rectangle((cx - 130 * k, cy - 20 * k, cx + 130 * k, cy + 110 * k), radius=int(20 * k), fill=col)
        d.rounded_rectangle((cx - 100 * k, cy - 110 * k, cx + 100 * k, cy - 10 * k), radius=int(20 * k), fill=dark)
        d.rectangle((cx - 6 * k, cy - 170 * k, cx + 6 * k, cy - 110 * k), fill=(255, 220, 120))
        d.ellipse((cx - 12 * k, cy - 200 * k, cx + 12 * k, cy - 165 * k), fill=(255, 150, 60))
    elif kind == 'bag':
        d.rounded_rectangle((cx - 120 * k, cy - 60 * k, cx + 120 * k, cy + 120 * k), radius=int(24 * k), fill=col)
        d.arc((cx - 70 * k, cy - 150 * k, cx + 70 * k, cy - 10 * k), 180, 360, fill=dark, width=int(14 * k))
        d.rectangle((cx - 120 * k, cy - 10 * k, cx + 120 * k, cy + 10 * k), fill=dark)
    elif kind == 'shoe':
        d.polygon([(cx - 140 * k, cy + 60 * k), (cx - 130 * k, cy - 60 * k), (cx - 40 * k, cy - 70 * k), (cx + 20 * k, cy - 10 * k), (cx + 140 * k, cy + 20 * k), (cx + 150 * k, cy + 70 * k)], fill=col)
        d.rectangle((cx - 145 * k, cy + 60 * k, cx + 152 * k, cy + 90 * k), fill=(250, 250, 250))
        for i in range(3): d.line((cx - 80 * k + i * 30 * k, cy - 50 * k, cx - 50 * k + i * 30 * k, cy - 20 * k), fill=(255, 255, 255), width=int(5 * k))
    else:
        d.polygon([(cx - 50 * k, cy - 120 * k), (cx + 50 * k, cy - 120 * k), (cx + 70 * k, cy - 40 * k), (cx + 150 * k, cy + 140 * k), (cx - 150 * k, cy + 140 * k), (cx - 70 * k, cy - 40 * k)], fill=col)
        d.line([(cx - 70 * k, cy - 40 * k), (cx + 70 * k, cy - 40 * k)], fill=dark, width=int(6 * k))
        d.line([(cx - 30 * k, cy - 150 * k), (cx - 50 * k, cy - 120 * k)], fill=(150, 130, 110), width=int(5 * k))
        d.line([(cx + 30 * k, cy - 150 * k), (cx + 50 * k, cy - 120 * k)], fill=(150, 130, 110), width=int(5 * k))

# ---------- canh ----------
def card(im, box, r=36, fill=WHITE, alpha=50, blur=20):
    im.alpha_composite(shadow_layer((W, H), box, r, blur=blur, alpha=alpha))
    d = ImageDraw.Draw(im); rrect(d, box, r, fill); return d

def typed(text, t, at, cps=22):
    if t < at: return ''
    n = int((t - at) * cps); return text[:n]

def scene1(t, dur, line):
    im = bg_night(t)
    title(im, S['s1_time'], 210, 150, (255, 214, 102), t, 0.0, w='Black', shadow=(0, 0, 0, 160))
    title(im, S['s1_sub'], 360, 60, (230, 234, 245), t, 0.5, w='Bold')
    if t > 0.7:
        k = ease((t - 0.7) / 0.5)
        y = int(600 + 80 * (1 - k))
        d = card(im, (90, y, 990, y + 520), 40, (30, 37, 62), alpha=120)
        d.ellipse((140, y + 50, 230, y + 140), fill=(255, 196, 140))
        d.text((185, y + 95), S['avatar'], font=F('Bold', 44), fill=(120, 60, 20), anchor='mm')
        d.text((260, y + 60), S['shop'], font=F('Bold', 40), fill=(235, 238, 248))
        d.text((260, y + 110), 'Tạo bài viết', font=F('Regular', 30), fill=(150, 160, 190))
        rrect(d, (140, y + 180, 940, y + 380), 26, (22, 27, 46))
        d.text((180, y + 220), 'Bạn đang nghĩ gì?', font=F('Medium', 42), fill=(110, 118, 150))
        if int(t * 2) % 2 == 0: d.rectangle((180, y + 280, 184, y + 330), fill=(230, 234, 245))
        d.text((140, y + 420), 'Bài gần nhất: 3 ngày trước', font=F('SemiBold', 34), fill=(255, 140, 140))
    caption(im, line, t, dur)
    return im

def scene2(t, dur, line):
    im = bg_night(t + 3)
    title(im, S['s2_title'], 220, 84, (255, 214, 102), t, 0.0, shadow=(0, 0, 0, 160))
    d = card(im, (90, 470, 990, 1250), 40, (30, 37, 62), alpha=120)
    d.text((140, 520), 'Tương tác của page', font=F('Bold', 40), fill=(235, 238, 248))
    xs = [150, 270, 390, 510, 630, 750, 870, 930]
    ys = [760, 720, 740, 700, 860, 980, 1080, 1120]
    k = clamp01(t / 1.6)
    npts = 1 + k * (len(xs) - 1)
    pts = []
    for i in range(len(xs)):
        if i <= npts: pts.append((xs[i], ys[i]))
        else:
            f = npts - int(npts); j = int(npts)
            if j + 1 < len(xs): pts.append((xs[j] + (xs[j + 1] - xs[j]) * f, ys[j] + (ys[j + 1] - ys[j]) * f))
            break
    for gy in (700, 850, 1000, 1150): d.line((140, gy, 940, gy), fill=(50, 58, 90), width=2)
    if len(pts) > 1:
        for i in range(len(pts) - 1):
            c = (120, 220, 200) if pts[i + 1][0] <= 630 else RED
            d.line((pts[i], pts[i + 1]), fill=c, width=10)
        x, y = pts[-1]; d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=RED if x > 630 else (120, 220, 200))
    if t > 1.4:
        kk = back((t - 1.4) / 0.35)
        st = Image.new('RGBA', (700, 170), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((8, 8, 692, 162), radius=24, outline=RED, width=10)
        sd.text((350, 85), S['s2_stamp'], font=F('Black', 58 if len(S['s2_stamp']) <= 16 else 48), fill=RED, anchor='mm')
        st = st.rotate(-8, expand=True, resample=Image.BICUBIC)
        sc = 1.8 - 0.8 * kk
        st2 = st.resize((max(1, int(st.width * sc)), max(1, int(st.height * sc))), Image.LANCZOS)
        im.alpha_composite(st2, ((W - st2.width) // 2, 1400 - st2.height // 2))
    caption(im, line, t, dur)
    return im

def app_frame(im, t, label):
    """khung app Nhip trong dien thoai"""
    sh = shadow_layer((W, H), (PX0, PY0, PX0 + PW, PY0 + PH), 70, blur=30, alpha=60)
    im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    rrect(d, (PX0, PY0, PX0 + PW, PY0 + PH), 70, (10, 10, 14))
    rrect(d, (PX0 + 14, PY0 + 14, PX0 + PW - 14, PY0 + PH - 14), 58, OFF)
    d.text((PX0 + 70, PY0 + 40), '09:00', font=F('SemiBold', 30), fill=INK)
    rrect(d, (PX0 + PW // 2 - 90, PY0 + 34, PX0 + PW // 2 + 90, PY0 + 74), 20, (10, 10, 14))
    hy = PY0 + 100
    d.ellipse((PX0 + 50, hy + 30, PX0 + 74, hy + 54), fill=ORANGE)
    d.text((PX0 + 86, hy + 42), 'Nhịp', font=F('ExtraBold', 40), fill=TEAL, anchor='lm')
    d.text((PX0 + PW - 50, hy + 42), label, font=F('SemiBold', 28), fill=GREY, anchor='rm')
    return d

def prompt_box(im, d, y, text, t, at, done_at):
    rrect(d, (PX0 + 44, y, PX0 + PW - 44, y + 150), 30, WHITE, outline=(214, 222, 220), width=3)
    tx = typed(text, t, at, 26)
    f = F('Medium', 32)
    ls = wrap(d, tx, f, PW - 230)
    for i, l in enumerate(ls[:3]): d.text((PX0 + 74, y + 26 + i * 42), l, font=f, fill=INK)
    if t < done_at and int(t * 3) % 2 == 0 and ls:
        lx = PX0 + 74 + d.textlength(ls[-1], font=f); ly = y + 26 + (len(ls) - 1) * 42
        d.rectangle((lx + 3, ly + 2, lx + 6, ly + 38), fill=TEAL)
    bx = PX0 + PW - 120
    col = ORANGE if t >= done_at else TEAL
    d.ellipse((bx, y + 40, bx + 70, y + 110), fill=col)
    d.polygon([(bx + 24, y + 58), (bx + 52, y + 75), (bx + 24, y + 92)], fill=WHITE)

def scene3(t, dur, line):
    im = bg_light(t)
    brand_tag(im)
    title(im, 'Chỉ cần nói yêu cầu', 210, 76, TEAL, t, 0.0)
    title(im, 'AI tự viết bài + ảnh + hashtag', 310, 44, INK, t, 0.4, w='SemiBold')
    d = app_frame(im, t, 'Viết bài')
    req = S['s3_req']
    prompt_box(im, d, PY0 + 190, req, t, 0.5, 0.5 + len(req) / 26 + 0.2)
    at = 0.5 + len(req) / 26 + 0.6
    if t > at:
        k = back((t - at) / 0.45)
        y0 = int(PY0 + 380 + 60 * (1 - k))
        d = card(im, (PX0 + 44, y0, PX0 + PW - 44, y0 + 740), 30, WHITE, alpha=40)
        # anh san pham ve tay
        ix0, iy0, ix1, iy1 = PX0 + 74, y0 + 30, PX0 + PW - 74, y0 + 380
        rrect(d, (ix0, iy0, ix1, iy1), 22, tuple(S['pbg']))
        cx = (ix0 + ix1) // 2
        d.ellipse((cx - 160, iy0 + 25, cx + 160, iy1 - 15), fill=(255, 250, 244))
        product(d, cx, (iy0 + iy1) // 2 + 10, 0.85, S['product'], S['pcolor'])
        body = []
        for para in S['s3_body']: body += wrap(d, para, F('Medium', 30), PW - 160)
        body = body[:5]
        tt = t - at - 0.3
        shown = int(max(0, tt) * 40)
        acc = 0; yy = y0 + 410
        for l in body:
            part = l[:max(0, shown - acc)]; acc += len(l)
            d.text((PX0 + 74, yy), part, font=F('Medium', 30), fill=INK); yy += 44
        if tt > 2.2:
            d.text((PX0 + 74, yy + 14), S['s3_tags'], font=F('SemiBold', 28), fill=(0, 110, 220))
            kk = clamp01((tt - 2.4) / 0.3)
            if kk > 0:
                d.text((PX0 + PW - 74, y0 + 700), 'AI viết xong · 10 giây', font=F('SemiBold', 26), fill=TEAL, anchor='rm')
    caption(im, line, t, dur)
    return im

def scene4(t, dur, line):
    im = bg_light(t, MINT)
    brand_tag(im)
    title(im, 'Tự làm video Reels', 210, 78, TEAL_D, t, 0.0)
    title(im, 'đúng chủ đề, đúng kênh của bạn', 310, 44, INK, t, 0.4, w='SemiBold')
    d = app_frame(im, t, 'Video')
    req = S['s4_req']
    prompt_box(im, d, PY0 + 190, req, t, 0.4, 0.4 + len(req) / 30 + 0.1)
    at = 0.4 + len(req) / 30 + 0.4
    if t > at:
        k = back((t - at) / 0.4)
        vw, vh = 330, 586
        x0 = PX0 + (PW - vw) // 2; y0 = int(PY0 + 380 + 50 * (1 - k))
        d = card(im, (x0, y0, x0 + vw, y0 + vh), 26, (30, 36, 50), alpha=70)
        prog = clamp01((t - at - 0.3) / 1.6)
        # khung hinh doi mau theo tien do (gia lap cac canh)
        cols = [(250, 226, 200), (226, 214, 240), (206, 236, 226)]
        ci = min(2, int((t - at) * 2) % 3)
        rrect(d, (x0 + 14, y0 + 14, x0 + vw - 14, y0 + vh - 90), 18, cols[ci])
        cx, cy = x0 + vw // 2, y0 + (vh - 90) // 2
        product(d, cx, cy + 20, 0.75, S['product'], S['pcolor'])
        rrect(d, (x0 + 30, y0 + vh - 60, x0 + vw - 30, y0 + vh - 44), 8, (70, 80, 100))
        rrect(d, (x0 + 30, y0 + vh - 60, x0 + 30 + int((vw - 60) * prog), y0 + vh - 44), 8, ORANGE)
        if prog < 1:
            d.text((cx, y0 + vh - 100), 'Đang dựng... %d%%' % int(prog * 100), font=F('Bold', 26), fill=INK, anchor='mm')
        else:
            kk = back((t - at - 1.9) / 0.35)
            r = int(56 * kk)
            if r > 2:
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255))
                d.polygon([(cx - r * 0.3, cy - r * 0.45), (cx + r * 0.5, cy), (cx - r * 0.3, cy + r * 0.45)], fill=TEAL)
            d.text((PX0 + PW // 2, y0 + vh + 50), 'Video xong · có giọng đọc, phụ đề, nhạc', font=F('SemiBold', 28), fill=TEAL, anchor='mm')
    caption(im, line, t, dur)
    return im

def chip(d, x, y, text, bg, fg, f):
    tw = d.textlength(text, font=f)
    rrect(d, (x, y, x + tw + 60, y + 72), 36, bg)
    d.text((x + 30 + tw / 2, y + 36), text, font=f, fill=fg, anchor='mm')
    return x + tw + 60

def scene5(t, dur, line):
    im = bg_light(t)
    brand_tag(im)
    title(im, 'Tự đăng đúng giờ', 210, 80, TEAL, t, 0.0)
    title(im, 'đều đặn mỗi ngày', 310, 46, INK, t, 0.35, w='SemiBold')
    days = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    kinds = ['Bài viết', 'Reels', 'Bài viết', 'Reels', 'Bài viết', 'Reels', 'Bài viết']
    d = card(im, (70, 420, 1010, 1260), 40, WHITE, alpha=45)
    d.text((120, 470), 'Lịch đăng tuần này', font=F('Bold', 40), fill=INK)
    for i, dd in enumerate(days):
        y = 550 + i * 95
        d.text((130, y + 40), dd, font=F('Bold', 36), fill=GREY, anchor='lm')
        at = 0.5 + i * 0.28
        if t < at:
            rrect(d, (220, y + 8, 960, y + 72), 18, (240, 242, 241)); continue
        k = ease((t - at) / 0.3)
        xw = int(220 + 740 * k)
        rrect(d, (220, y + 8, xw, y + 72), 18, MINT)
        if k > 0.7:
            d.text((250, y + 40), '%s  ·  19:30' % kinds[i], font=F('SemiBold', 32), fill=TEAL_D, anchor='lm')
            d.text((900, y + 40), 'Đã đăng', font=F('SemiBold', 26), fill=(46, 150, 110), anchor='rm')
            d.ellipse((912, y + 24, 944, y + 56), fill=(46, 170, 120))
    at = 0.5 + 7 * 0.28 + 0.2
    if t > at:
        d = ImageDraw.Draw(im); f = F('Bold', 32)
        x = 110
        for j, (txt, bg) in enumerate([('Facebook', (24, 119, 242)), ('Instagram', (214, 41, 118)), ('TikTok', (20, 20, 24)), ('Zalo OA', (0, 104, 255))]):
            if t > at + j * 0.15: x = chip(d, x, 1310, txt, bg, WHITE, f) + 16
    at2 = at + 1.2
    if t > at2:
        k = back((t - at2) / 0.35)
        d = ImageDraw.Draw(im)
        f = F('SemiBold', 32)
        txt = '+ AI trả lời bình luận & tin nhắn'
        tw = d.textlength(txt, font=f)
        a = clamp01(k)
        rrect(d, (W / 2 - tw / 2 - 30, 1440, W / 2 + tw / 2 + 30, 1510), 35, (255, 236, 222))
        d.text((W / 2, 1475), txt, font=f, fill=(190, 90, 30), anchor='mm')
    caption(im, line, t, dur)
    return im

def scene6(t, dur, line):
    im = Image.new('RGBA', (W, H), TEAL + (255,))
    d = ImageDraw.Draw(im)
    for i in range(6):
        r = 300 + i * 180 + (t * 60) % 180
        a = max(0, 60 - i * 10)
        d.ellipse((W / 2 - r, 820 - r, W / 2 + r, 820 + r), outline=(255, 255, 255, a), width=3)
    im2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    k = back(t / 0.5)
    lf = F('Black', int(200 * (0.6 + 0.4 * k)))
    dd = ImageDraw.Draw(im2)
    dd.ellipse((W / 2 + 225, 815, W / 2 + 275, 865), fill=ORANGE)
    dd.text((W / 2, 780), 'Nhịp', font=lf, fill=WHITE, anchor='mm')
    im.alpha_composite(im2)
    title(im, 'Viết bài · Làm video · Tự đăng', 990, 50, (255, 214, 170), t, 0.4, w='Bold')
    title(im, 'Bạn lo bán hàng.', 1090, 64, WHITE, t, 0.8)
    title(im, 'Nhịp lo nội dung mỗi ngày.', 1175, 64, WHITE, t, 1.1)
    at = 1.7
    if t > at:
        kk = back((t - at) / 0.4)
        pulse = 1 + 0.04 * math.sin((t - at) * 6)
        bw = int(780 * kk * pulse); bh = int(140 * kk * pulse)
        cx, cy = W // 2, 1390
        d = ImageDraw.Draw(im)
        if bw > 10:
            rrect(d, (cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2), bh // 2, WHITE)
            d.text((cx, cy), 'Nhắn tin cho page Nhịp', font=F('ExtraBold', max(10, int(52 * kk * pulse))), fill=TEAL_D, anchor='mm')
        d.text((cx, cy + 125), 'để được tư vấn', font=F('SemiBold', 40), fill=(220, 240, 235), anchor='mm')
    caption(im, line, t, dur)
    return im

SCENES = [scene1, scene2, scene3, scene4, scene5, scene6]
MIN = [3.6, 3.0, 7.5, 5.6, 5.5, 4.6]  # do dai toi thieu moi canh (giay)

def wav_dur(p):
    with wave.open(p) as w_:
        return w_.getnframes() / w_.getframerate()

def render_scene(i, dur, line, out):
    tmp = out + '.part.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        im = SCENES[i](t, dur, line).convert('RGB')
        # chuyen canh: 6 frame dau mo tu trang/den nhe
        if i > 0 and f < 5:
            a = 1 - f / 5
            im = Image.blend(im, Image.new('RGB', (W, H), (255, 255, 255)), a * 0.85)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)
    else: raise SystemExit('ffmpeg loi canh %d' % i)

def synth_music(dur, path, sr=44100):
    """nhac nen nhe nhang tu tong hop: hop am + nhip go nhe, 100 bpm"""
    n = int(dur * sr); t = np.arange(n) / sr
    bpm = 100; beat = 60 / bpm
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    out = np.zeros(n)
    bar = beat * 4
    for ci in range(int(dur / bar) + 1):
        ch = chords[ci % 4]
        s0 = int(ci * bar * sr); s1 = min(n, int((ci + 1) * bar * sr))
        if s0 >= n: break
        tt = t[s0:s1] - ci * bar
        env = np.minimum(1, tt / 0.3) * np.exp(-tt * 0.25)
        for m in ch:
            f = 440 * 2 ** ((m - 69) / 12)
            out[s0:s1] += 0.12 * env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt))
        # arpeggio 8 not
        for k in range(8):
            a0 = s0 + int(k * beat / 2 * sr); a1 = min(s1, a0 + int(0.4 * sr))
            if a0 >= s1: break
            m = ch[k % 3] + 12
            f = 440 * 2 ** ((m - 69) / 12)
            ta = t[a0:a1] - t[a0]
            out[a0:a1] += 0.07 * np.exp(-ta * 7) * np.sin(2 * np.pi * f * ta)
        # bass
        f = 440 * 2 ** ((ch[0] - 12 - 69) / 12)
        for k in range(4):
            b0 = s0 + int(k * beat * sr); b1 = min(s1, b0 + int(0.35 * sr))
            if b0 >= s1: break
            tb = t[b0:b1] - t[b0]
            out[b0:b1] += 0.16 * np.exp(-tb * 6) * np.sin(2 * np.pi * f * tb)
    # go nhe (hi-hat noise) moi phach roi
    rng = np.random.default_rng(1)
    for k in range(int(dur / (beat / 2))):
        h0 = int(k * beat / 2 * sr); h1 = min(n, h0 + int(0.05 * sr))
        if h0 >= n: break
        out[h0:h1] += 0.03 * rng.standard_normal(h1 - h0) * np.exp(-np.arange(h1 - h0) / sr * 80)
    fade = int(1.5 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out /= max(1e-6, np.abs(out).max()); out *= 0.8
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'w') as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes(pcm.tobytes())

def sfx_pop(path, sr=44100):
    n = int(0.12 * sr); t = np.arange(n) / sr
    f = 900 * np.exp(-t * 18) + 300
    y = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 35) * 0.6
    with wave.open(path, 'w') as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes((y * 32767).astype(np.int16).tobytes())

def main():
    vdir, out = sys.argv[1], sys.argv[2]
    lines = json.load(open(os.path.join(vdir, 'lines.json'), encoding='utf-8'))
    sp = os.path.join(vdir, 'scene.json')
    if os.path.exists(sp): S.update(json.load(open(sp, encoding='utf-8')))
    wd = os.path.join(os.path.dirname(os.path.abspath(out)), 'work'); os.makedirs(wd, exist_ok=True)
    durs, starts = [], []
    acc = 0.0
    for i in range(6):
        vd = wav_dur(os.path.join(vdir, 'v%d.wav' % (i + 1)))
        d = max(MIN[i], vd + 0.55)
        if i == 5: d = max(d, vd + 1.6)
        durs.append(d); starts.append(acc); acc += d
    only = os.environ.get('ONLY')
    for i in range(6):
        if only is not None and str(i) not in only.split(','): continue
        render_scene(i, durs[i], lines[i], os.path.join(wd, 's%d.mp4' % i))
    with open(os.path.join(wd, 'list.txt'), 'w') as f:
        for i in range(6): f.write("file 's%d.mp4'\n" % i)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(wd, 'list.txt'), '-c', 'copy', os.path.join(wd, 'video.mp4')], check=True)
    total = acc
    synth_music(total, os.path.join(wd, 'music.wav'))
    sfx_pop(os.path.join(wd, 'pop.wav'))
    # giong: moi doan vao dau canh + 0.25s
    inputs = ['-i', os.path.join(wd, 'video.mp4'), '-i', os.path.join(wd, 'music.wav')]
    flt = []; mix = []
    for i in range(6):
        inputs += ['-i', os.path.join(vdir, 'v%d.wav' % (i + 1))]
        ms = int((starts[i] + 0.25) * 1000)
        flt.append('[%d:a]aresample=44100,adelay=%d|%d,volume=1.0[v%d]' % (i + 2, ms, ms, i)); mix.append('[v%d]' % i)
    pops = [0.7, starts[1] + 1.4, starts[2] + 2.9, starts[3] + 2.5, starts[3] + 4.3] + [starts[4] + 0.5 + i * 0.28 for i in range(7)] + [starts[5] + 1.7]
    pi = 8
    for j, p_ in enumerate(pops):
        inputs += ['-i', os.path.join(wd, 'pop.wav')]
        ms = int(p_ * 1000)
        flt.append('[%d:a]aresample=44100,adelay=%d|%d,volume=0.35[p%d]' % (pi + j, ms, ms, j)); mix.append('[p%d]' % j)
    flt.append('[1:a]aresample=44100,volume=0.16[m]')
    flt.append('%s[m]amix=inputs=%d:normalize=0:duration=longest,loudnorm=I=-15:TP=-1.5:LRA=11[a]' % (''.join(mix), len(mix) + 1))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', '%.2f' % total, '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    print(json.dumps({'durs': durs, 'total': total}))

if __name__ == '__main__':
    main()
