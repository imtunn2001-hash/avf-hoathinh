"""Ky Su Chien - Mo xe chien thuat: HOAT HINH CAT GHEP 2D (chu chot 20/11/2026: nhan vat co dinh, hinh dong,
cheo thuyen, danh nhau, tieng va cham vu khi, KHONG canh tinh).

Nhan vat ve bang code (khop xuong: than, dau, 2 tay 2 doan, 2 chan 2 doan) -> giong het nhau moi tap.
Moi canh (shot) la 1 mau dung san, tu chay theo thoi gian: thuyen nhap nho, mai cheo quat, giao dam, kiem do,
toe nuoc, tia lua, rung man hinh + tieng (tu tao bang numpy, khong ban quyen).

SPEC_JSON = {"branch","dir"} (spec.json trong dir) hoac spec truc tiep. spec:
{ "series": "Bãi cọc Bạch Đằng", "badge": "MỔ XẺ CHIẾN THUẬT", "ep_title": "...", "hook_text": "...", "next": "Kỳ sau: ...",
  "voice_urls": [...], "srt_urls": [...],           # tu W57 (khong co thi dung "durs")
  "cues": ["", "cum tu bat dau canh 2", ...],         # nhu series.py
  "shots": [ {"type": "fleet_arrive", "key": "CHỮ KHOÁ", ...tham so}, ... ],
  "durs": [5, 5, ...]                                 # chi dung khi khong co giong (dung thu)
}
Loai shot: fleet_arrive, prep_stakes, tide_diagram, bait_row, ambush, melee, crash_stakes, victory, narrator, general.
Bo cuc KHOA CUNG (claude/bo-cuc-khoa-cung.md): tieu de 268-400, khung hanh dong 410-1240, phu de neo day 1452.
"""
import json, math, os, random, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series import get, parse_srt, ease, wrap, wrap_bal, word_times, _norm, scene_starts, voice_part  # noqa: E402
import safezone  # noqa: E402

W, H, FPS = 1080, 1920, 30
ROOT = os.getcwd()
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
SX0, SY0, SX1, SY1 = safezone.SAFE
TW = safezone.MAXW_C540
AY0, AY1 = 410, 1250            # khung hanh dong (the gioi ve)
AW, AH = W, AY1 - AY0           # 1080 x 840
SS = 2                          # ve gap doi roi thu nho -> net muot
YEL = (255, 212, 0); WHITE = (255, 255, 255); INK = (16, 14, 20); RED1, RED2 = (70, 16, 14), (120, 34, 24)
OUTL = (22, 16, 14)

# ---------- mau nhan vat (CO DINH, khong doi giua cac tap) ----------
LOOKS = {
    'viet':    dict(skin=(214, 160, 112), top=(52, 66, 128), top2=(38, 48, 96), pants=(92, 62, 40), band=(196, 40, 36), hair=(28, 22, 20)),
    'viet2':   dict(skin=(205, 150, 104), top=(126, 84, 52), top2=(96, 62, 38), pants=(60, 52, 70), band=(196, 40, 36), hair=(28, 22, 20)),
    'han':     dict(skin=(222, 178, 130), top=(132, 118, 92), top2=(96, 84, 64), pants=(112, 42, 40), helm=(88, 78, 60), hair=(24, 20, 18)),
    'general': dict(skin=(206, 152, 106), top=(58, 58, 70), top2=(38, 38, 48), pants=(40, 36, 44), cape=(170, 30, 30), hair=(20, 16, 14), band=(212, 170, 60)),
    'scholar': dict(skin=(226, 176, 128), top=(238, 228, 204), top2=(206, 192, 164), pants=(96, 70, 50), hat=(226, 196, 122), hair=(26, 20, 18)),
}


def F(bold, size, _c={}):
    k = (bold, size)
    if k not in _c:
        for p in [os.path.join(ROOT, 'fonts', 'BeVietnamPro-ExtraBold.ttf' if bold else 'BeVietnamPro-Medium.ttf'),
                  '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf' if bold else '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf']:
            if os.path.exists(p): _c[k] = ImageFont.truetype(p, size); break
        else: sys.exit('khong co font')
    return _c[k]


def lerp(a, b, q): return a + (b - a) * q
def mix(c1, c2, q): return tuple(int(lerp(a, b, q)) for a, b in zip(c1, c2))
def osc(t, f, ph=0.0): return math.sin(2 * math.pi * (f * t + ph))


def keyf(t, keys, loop=None):
    """keys = [(t, value_or_dict), ...] noi suy muot; loop = chu ky."""
    if loop: t = t % loop
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if t < b:
            q = ease((t - a) / max(1e-6, b - a))
            if isinstance(va, dict): return {k: lerp(va[k], vb.get(k, va[k]), q) for k in va}
            return lerp(va, vb, q)
    return keys[-1][1]


# ---------- camera + but ve ----------
class Pen:
    def __init__(self, d, cam):
        self.d = d; self.cx, self.cy, self.z = cam
    def P(self, x, y): return ((x - self.cx) * self.z + AW / 2) * SS, ((y - self.cy) * self.z + AH / 2) * SS
    def S(self, v): return v * self.z * SS
    def poly(self, pts, fill, outline=OUTL, w=3):
        q = [self.P(x, y) for x, y in pts]
        self.d.polygon(q, fill=fill)
        if outline and w: self.d.line(q + [q[0]], fill=outline, width=max(1, int(self.S(w))), joint='curve')
    def seg(self, a, b, w, fill, outline=OUTL, ow=3):
        pa, pb = self.P(*a), self.P(*b); ww = self.S(w)
        if outline:
            self.d.line([pa, pb], fill=outline, width=int(ww + self.S(ow) * 2))
            for p in (pa, pb): r = (ww / 2 + self.S(ow)); self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=outline)
        self.d.line([pa, pb], fill=fill, width=int(ww))
        for p in (pa, pb): r = ww / 2; self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)
    def circ(self, c, r, fill, outline=OUTL, w=3):
        p = self.P(*c); rr = self.S(r)
        self.d.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=fill, outline=outline, width=max(1, int(self.S(w))) if outline else 0)
    def line(self, pts, fill, w):
        self.d.line([self.P(*p) for p in pts], fill=fill, width=max(1, int(self.S(w))), joint='curve')
    def rect(self, x0, y0, x1, y1, fill):
        a, b = self.P(x0, y0), self.P(x1, y1); self.d.rectangle([a[0], a[1], b[0], b[1]], fill=fill)


# ---------- nhan vat co khop ----------
L_T, L_UA, L_FA, L_TH, L_SH, R_HEAD = 58, 30, 30, 36, 36, 17


def fk(x, y, ang, ln, face):
    a = math.radians(ang); return x + face * math.sin(a) * ln, y + math.cos(a) * ln


def person(p, x, y, look, pose, face=1, sc=1.0, item=None, alpha_dead=0.0):
    """x,y = hong. pose: torso (nghieng ve truoc +), head, lua/lfa/rua/rfa (tay sau/truoc), lth/lsh/rth/rsh.
    Goc do tu huong thang xuong, + la ve phia mat nhin (face). item: spear|sword|oar|mallet|flag|bow|shield|board."""
    c = LOOKS[look]; s = sc
    tor = pose.get('torso', 0); rot = pose.get('rot', 0)   # rot: ca nguoi nga (do)
    def R(ang): return ang + rot
    sh = fk(x, y, 180 - R(tor) * 1.0, L_T * s, face)     # vai (di len)
    hd = fk(sh[0], sh[1], 180 - R(tor + pose.get('head', 0)), (R_HEAD + 4) * s, face)
    def limb(base, a1, a2, l1, l2):
        j = fk(base[0], base[1], R(a1), l1 * s, face); e = fk(j[0], j[1], R(a2), l2 * s, face); return j, e
    lk, lf = limb((x, y), pose.get('lth', 8), pose.get('lsh', 0), L_TH, L_SH)
    rk, rf = limb((x, y), pose.get('rth', -8), pose.get('rsh', 0), L_TH, L_SH)
    le, lh = limb(sh, pose.get('lua', 10), pose.get('lfa', 30), L_UA, L_FA)
    re_, rh = limb(sh, pose.get('rua', -10), pose.get('rfa', 20), L_UA, L_FA)
    dk = c.get('top2'); lw, aw = 15 * s, 11 * s
    # tay + chan phia sau (toi hon)
    p.seg((x, y), lk, lw, mix(c['pants'], (0, 0, 0), .25)); p.seg(lk, lf, lw * .9, mix(c['skin'], (0, 0, 0), .25))
    if look == 'general': p.poly([sh, fk(sh[0], sh[1], R(-25), 70 * s, face), fk(x, y, R(-30), 30 * s, face)], c['cape'])
    p.seg(sh, le, aw, dk); p.seg(le, lh, aw * .9, mix(c['skin'], (0, 0, 0), .2))
    # than
    nx = fk(x, y, 180 - R(tor), 4 * s, face)
    w0, w1 = 19 * s, 15 * s
    def side(pt, dist, off):
        a = math.radians(180 - R(tor) + 90 * off); return pt[0] + face * math.sin(a) * dist, pt[1] + math.cos(a) * dist
    body = [side(nx, w0, 1), side(sh, w1, 1), side(sh, w1, -1), side(nx, w0, -1)]
    hem = fk(x, y, R(tor), 14 * s, face)
    p.poly(body + [side(hem, w0 + 3 * s, -1), side(hem, w0 + 3 * s, 1)], c['top'])
    if look == 'han':   # giap vay ca
        for k in range(1, 4):
            q = k / 4.0; a_ = (lerp(body[0][0], body[1][0], q), lerp(body[0][1], body[1][1], q)); b_ = (lerp(body[3][0], body[2][0], q), lerp(body[3][1], body[2][1], q))
            p.line([a_, b_], c['top2'], 2.2 * s)
    if look in ('viet', 'viet2', 'general'):
        p.line([side(nx, w0 - 2 * s, 1), side(nx, w0 - 2 * s, -1)], c.get('band', (150, 30, 30)), 4 * s)   # dai lung
    # chan truoc
    p.seg((x, y), rk, lw, c['pants']); p.seg(rk, rf, lw * .9, c['skin'])
    # dau
    p.circ(hd, R_HEAD * s, c['skin'])
    eye = (hd[0] + face * 7 * s, hd[1] - 2 * s)
    p.circ(eye, 2.4 * s, OUTL, None)
    p.line([(hd[0] + face * 3 * s, hd[1] + 7 * s), (hd[0] + face * 11 * s, hd[1] + 6 * s)], OUTL, 1.6 * s)
    if pose.get('shout', 0) > .5: p.circ((hd[0] + face * 9 * s, hd[1] + 8 * s), 3.5 * s, (80, 20, 20), OUTL, 1.2)
    if look in ('viet', 'viet2'):
        p.poly([(hd[0] - 17 * s, hd[1] - 12 * s), (hd[0] + 17 * s, hd[1] - 12 * s), (hd[0] + 16 * s, hd[1] - 5 * s), (hd[0] - 16 * s, hd[1] - 5 * s)], c['band'], OUTL, 1.5)
        tail = (hd[0] - face * 22 * s, hd[1] - 6 * s + osc(pose.get('_t', 0), 2.2) * 3 * s)
        p.seg((hd[0] - face * 14 * s, hd[1] - 9 * s), tail, 4 * s, c['band'], OUTL, 1)
        p.poly([(hd[0] - 16 * s, hd[1] - 13 * s), (hd[0] + 15 * s, hd[1] - 13 * s), (hd[0] + 8 * s, hd[1] - 19 * s), (hd[0] - 10 * s, hd[1] - 19 * s)], c['hair'], OUTL, 1.5)
    elif look == 'han':
        p.poly([(hd[0] - 19 * s, hd[1] - 4 * s), (hd[0] - 17 * s, hd[1] - 16 * s), (hd[0], hd[1] - 24 * s), (hd[0] + 17 * s, hd[1] - 16 * s), (hd[0] + 19 * s, hd[1] - 4 * s)], c['helm'])
        p.seg((hd[0], hd[1] - 24 * s), (hd[0], hd[1] - 33 * s), 4 * s, c['helm'], OUTL, 1.5)
        p.circ((hd[0], hd[1] - 35 * s), 4 * s, (150, 30, 30), OUTL, 1.2)
    elif look == 'general':
        p.circ((hd[0] - face * 4 * s, hd[1] - 18 * s), 7 * s, c['hair'], OUTL, 1.5)
        p.line([(hd[0] - 16 * s, hd[1] - 9 * s), (hd[0] + 16 * s, hd[1] - 9 * s)], c['band'], 4 * s)
        p.line([(hd[0] + face * 4 * s, hd[1] + 12 * s), (hd[0] + face * 2 * s, hd[1] + 22 * s)], c['hair'], 3 * s)   # rau
    elif look == 'scholar':
        p.poly([(hd[0] - 34 * s, hd[1] - 6 * s), (hd[0], hd[1] - 38 * s), (hd[0] + 34 * s, hd[1] - 6 * s)], c['hat'])
        p.line([(hd[0] - 17 * s, hd[1] - 20 * s), (hd[0] + 17 * s, hd[1] - 20 * s)], mix(c['hat'], (0, 0, 0), .2), 1.5 * s)
    # vu khi / do vat o tay truoc
    tip = None
    if item:
        ia = R(pose.get('item', pose.get('rfa', 20)))
        if item in ('spear', 'flag'):
            back = fk(rh[0], rh[1], ia + 180, 50 * s, face); tip = fk(rh[0], rh[1], ia, 92 * s, face)
            p.seg(back, tip, 4.5 * s, (120, 84, 46), OUTL, 1.5)
            if item == 'spear':
                t2 = fk(tip[0], tip[1], ia, 18 * s, face); sd = fk(tip[0], tip[1], ia + 90, 6 * s, face); sd2 = fk(tip[0], tip[1], ia - 90, 6 * s, face)
                p.poly([sd, t2, sd2], (196, 200, 210), OUTL, 1.5); tip = t2
            else:
                fl = 1 + osc(pose.get('_t', 0), 1.6) * .15
                p.poly([back, fk(back[0], back[1], ia + 70, 46 * s, face), fk(back[0], back[1], ia + 70 * fl, 46 * s, face), fk(back[0], back[1], ia, -34 * s, face)], c.get('cape', (190, 30, 30)), OUTL, 1.5)
        elif item == 'sword':
            tip = fk(rh[0], rh[1], ia, 62 * s, face)
            p.seg(rh, tip, 6 * s, (206, 210, 220), OUTL, 1.5)
            g1, g2 = fk(rh[0], rh[1], ia + 90, 9 * s, face), fk(rh[0], rh[1], ia - 90, 9 * s, face); p.seg(g1, g2, 4 * s, (110, 80, 40), OUTL, 1)
        elif item == 'mallet':
            tip = fk(rh[0], rh[1], ia, 46 * s, face); p.seg(rh, tip, 5 * s, (120, 84, 46), OUTL, 1.5)
            h1, h2 = fk(tip[0], tip[1], ia + 90, 14 * s, face), fk(tip[0], tip[1], ia - 90, 14 * s, face); p.seg(h1, h2, 15 * s, (98, 66, 38), OUTL, 2)
        elif item == 'bow':
            a0 = fk(rh[0], rh[1], ia + 90, 40 * s, face); a1 = fk(rh[0], rh[1], ia - 90, 40 * s, face); mid = fk(rh[0], rh[1], ia, 14 * s, face)
            p.line([a0, mid, a1], (110, 72, 40), 4 * s); p.line([a0, a1], (230, 230, 220), 1.4 * s); tip = rh
        elif item == 'oar':
            tip = fk(rh[0], rh[1], ia, 110 * s, face); back = fk(rh[0], rh[1], ia + 180, 20 * s, face)
            p.seg(back, tip, 5 * s, (140, 98, 56), OUTL, 1.5)
            b2 = fk(tip[0], tip[1], ia, 30 * s, face); p.seg(tip, b2, 13 * s, (150, 106, 60), OUTL, 1.5); tip = b2
        elif item == 'board':
            tip = fk(rh[0], rh[1], ia, 60 * s, face)
            p.seg(rh, tip, 3.5 * s, (110, 80, 50), OUTL, 1)
    if pose.get('shield'):
        sp_ = fk(lh[0], lh[1], R(0), 4 * s, face); p.circ(sp_, 19 * s, (156, 112, 62)); p.circ(sp_, 7 * s, (120, 80, 40), OUTL, 1.5)
    # tay truoc (de len vu khi)
    p.seg(sh, re_, aw, c['top']); p.seg(re_, rh, aw * .9, c['skin'])
    p.circ(rh, 6 * s, c['skin'], OUTL, 1.5)
    return {'tip': tip, 'hand': rh, 'head': hd, 'sh': sh}


# ---------- tu the / dong tac ----------
POSE0 = dict(torso=0, head=0, lua=12, lfa=28, rua=-12, rfa=18, lth=8, lsh=0, rth=-8, rsh=0, item=20)


def P_(**k):
    d = dict(POSE0); d.update(k); return d


def act(name, t, ph=0.0):
    """tra ve pose theo dong tac + thoi diem (giay)."""
    t = t + ph
    if name == 'idle':
        return P_(torso=2 + osc(t, .4) * 2, rua=-10 + osc(t, .4) * 3, _t=t)
    if name == 'row':   # ngoi cheo: vuoi mai cheo ra truoc cam xuong nuoc -> keo ve sau
        k = keyf(t, [(0, dict(torso=26, rua=70, rfa=40, lua=64, lfa=34, item=42)), (.5, dict(torso=-12, rua=-10, rfa=10, lua=-14, lfa=6, item=-38)),
                     (.9, dict(torso=26, rua=70, rfa=40, lua=64, lfa=34, item=42))], loop=.9)
        return P_(lth=84, lsh=-6, rth=80, rsh=-2, _t=t, **k)
    if name == 'thrust':
        k = keyf(t, [(0, dict(torso=-6, rua=-30, rfa=70, item=88, lth=18, rth=-22)), (.35, dict(torso=-12, rua=-46, rfa=60, item=86, lth=20, rth=-24)),
                     (.5, dict(torso=22, rua=70, rfa=88, item=90, lth=30, rth=-30)), (.75, dict(torso=18, rua=62, rfa=86, item=90, lth=28, rth=-28)),
                     (1.1, dict(torso=-6, rua=-30, rfa=70, item=88, lth=18, rth=-22))], loop=1.1)
        return P_(lua=30, lfa=80, _t=t, shout=1 if (t % 1.1) > .42 and (t % 1.1) < .8 else 0, **k)
    if name == 'block':
        k = keyf(t, [(0, dict(torso=-4, rua=40, rfa=150, item=150)), (.5, dict(torso=-14, rua=46, rfa=160, item=160)), (1.1, dict(torso=-4, rua=40, rfa=150, item=150))], loop=1.1)
        return P_(lth=16, rth=-20, lua=60, lfa=90, shield=1, _t=t, **k)
    if name == 'swing':
        k = keyf(t, [(0, dict(torso=-10, rua=150, rfa=170, item=175)), (.4, dict(torso=-14, rua=165, rfa=185, item=195)),
                     (.55, dict(torso=20, rua=60, rfa=70, item=80)), (1.1, dict(torso=-10, rua=150, rfa=170, item=175))], loop=1.1)
        return P_(lth=22, rth=-24, lua=40, lfa=60, shield=1, _t=t, **k)
    if name == 'hammer':
        k = keyf(t, [(0, dict(torso=-4, rua=150, rfa=200, item=200)), (.45, dict(torso=-8, rua=165, rfa=215, item=215)),
                     (.6, dict(torso=30, rua=40, rfa=60, item=95)), (1.0, dict(torso=-4, rua=150, rfa=200, item=200))], loop=1.0)
        return P_(lth=20, rth=-18, lua=40, lfa=60, _t=t, **k)
    if name == 'shoot':
        k = keyf(t, [(0, dict(rua=88, rfa=90, lua=80, lfa=60)), (.6, dict(rua=88, rfa=90, lua=86, lfa=150)), (.8, dict(rua=88, rfa=90, lua=80, lfa=60)), (1.4, dict(rua=88, rfa=90, lua=80, lfa=60))], loop=1.4)
        return P_(torso=-4, item=90, lth=14, rth=-16, _t=t, **k)
    if name == 'run':
        a = osc(t, 1.6)
        return P_(torso=14, lth=30 * a, lsh=-30 + 20 * a, rth=-30 * a, rsh=-30 - 20 * a, lua=-30 * a, lfa=40, rua=60, rfa=88, item=80, _t=t, shout=1)
    if name == 'cheer':
        a = abs(osc(t, 1.2))
        return P_(torso=-6, rua=160 + 15 * a, rfa=175 + 10 * a, lua=150 + 10 * a, lfa=165, item=175, shout=1, _t=t)
    if name == 'point':
        return P_(torso=2, rua=95 + osc(t, .5) * 6, rfa=100, lua=12, lfa=40, head=-4, _t=t, shout=1 if osc(t, 2.6) > 0 else 0, item=100)
    if name == 'command':
        a = keyf(t, [(0, 140), (.6, 160), (1.2, 140)], loop=1.2)
        return P_(torso=-4, rua=a, rfa=a + 10, item=a + 10, lua=20, lfa=50, shout=1 if (t % 1.2) < .6 else 0, _t=t)
    if name == 'fall':   # ngã ra sau
        q = ease(t / .7)
        return P_(rot=-95 * q, torso=-10, rua=150 * q, rfa=170, lua=140 * q, lfa=160, lth=30 * q, rth=-10, _t=t, shout=1)
    return P_(_t=t)


# ---------- tieng (tu tao) ----------
SR = 44100


def _env(n, a, dcy):
    t = np.arange(n) / SR; return np.minimum(1, t / max(1e-4, a)) * np.exp(-t / dcy)


def synth(kind, rnd):
    if kind == 'clash':      # kim loai va nhau
        n = int(SR * .9); t = np.arange(n) / SR; y = np.zeros(n)
        for f, g, dcy in [(1180, 1, .32), (2310, .7, .22), (3790, .5, .15), (5210, .35, .1), (6850, .25, .07)]:
            y += g * np.sin(2 * np.pi * f * (1 + rnd.uniform(-.03, .03)) * t) * np.exp(-t / dcy)
        y += rnd.standard_normal(n) * np.exp(-t / .012) * 1.5
        return y * .45
    if kind == 'thud':       # go dap / bua
        n = int(SR * .5); t = np.arange(n) / SR
        y = np.sin(2 * np.pi * (70 + 60 * np.exp(-t / .03)) * t) * np.exp(-t / .12) + rnd.standard_normal(n) * np.exp(-t / .02) * .5
        return y * .8
    if kind == 'crack':      # go vo
        n = int(SR * .8); t = np.arange(n) / SR
        y = rnd.standard_normal(n) * (np.exp(-t / .05) + .4 * np.exp(-((t - .12) ** 2) / .0004)) + np.sin(2 * np.pi * 55 * t) * np.exp(-t / .3) * .8
        return y * .6
    if kind == 'splash':
        n = int(SR * .9); t = np.arange(n) / SR
        x = rnd.standard_normal(n); x = np.convolve(x, np.ones(6) / 6, 'same')
        return x * (np.minimum(1, t / .02) * np.exp(-t / .22)) * .9
    if kind == 'oar':        # mai cheo vuc nuoc
        n = int(SR * .5); t = np.arange(n) / SR
        x = rnd.standard_normal(n); x = np.convolve(x, np.ones(14) / 14, 'same')
        return x * np.sin(np.pi * np.minimum(1, t / .45)) * .55
    if kind == 'drum':       # trong tran
        n = int(SR * .7); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * (58 + 30 * np.exp(-t / .05)) * t) * np.exp(-t / .25) + rnd.standard_normal(n) * np.exp(-t / .01) * .3) * 1.0
    if kind == 'whoosh':     # ten bay / vung vu khi
        n = int(SR * .45); t = np.arange(n) / SR
        x = rnd.standard_normal(n); x = x - np.convolve(x, np.ones(30) / 30, 'same')
        return x * np.sin(np.pi * t / .45) ** 2 * .35
    if kind == 'shout':      # tieng ho (tong hop, khong phai giong nguoi that)
        n = int(SR * .6); t = np.arange(n) / SR; f0 = 160 + 40 * np.sin(np.pi * t / .6)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        y = sum(np.sin(k * ph) / k for k in range(1, 9)) * np.sin(np.pi * t / .6) ** .5
        return y * .18
    return np.zeros(10)


def mix_audio(events, dur, voice_wav=None, path=None, lead=0.0):
    rnd = np.random.default_rng(7); n = int(SR * dur) + SR
    out = np.zeros(n)
    # nen: song nuoc + gio (rat nho)
    amb = rnd.standard_normal(n); amb = np.convolve(amb, np.ones(40) / 40, 'same'); out += amb * .05 * (1 + .3 * np.sin(2 * np.pi * .2 * np.arange(n) / SR))
    for t0, kind, vol in events:
        y = synth(kind, rnd) * vol; i = int(t0 * SR)
        if i >= n: continue
        m = min(len(y), n - i); out[i:i + m] += y[:m]
    pk = np.max(np.abs(out)) or 1; out = out / max(1.0, pk / .9)
    data = (np.stack([out, out], 1) * 32767 * .8).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
    return path


# ---------- phong canh ----------
def sky(p, top, bot):
    a = Image.new('RGB', (1, 64)); ad = ImageDraw.Draw(a)
    for y in range(64): ad.point((0, y), fill=mix(top, bot, y / 63))
    return a.resize((AW * SS, AH * SS))


SKIES = {'dawn': ((58, 66, 110), (236, 160, 110)), 'day': ((96, 150, 206), (196, 222, 236)), 'dusk': ((44, 36, 70), (210, 110, 80)),
         'storm': ((40, 46, 58), (112, 120, 128))}


def hills(p, t, base, cols, seed=3):
    rnd = random.Random(seed)
    for k, col in enumerate(cols):
        pts = [(-200, AH + 50)]; x = -200; sp = 0.6 + k * .4
        off = (t * 6 * sp) % 260
        while x < AW + 300:
            h = rnd.uniform(120, 260) * (1 - k * .22); w = rnd.uniform(110, 200)
            pts += [(x - off, base - 20 * k), (x + w * .25 - off, base - h - 20 * k), (x + w * .45 - off, base - h * .92 - 20 * k), (x + w * .7 - off, base - 30 - 20 * k)]
            x += w
        pts += [(AW + 300, AH + 50)]
        p.poly(pts, col, None, 0)


def reeds(p, t, x0, x1, y, col=(58, 92, 44), dens=9, wind=1.0, seed=5):
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        h = rnd.uniform(40, 90); sw = osc(t, .5 + rnd.random() * .3, rnd.random()) * 8 * wind
        p.line([(x, y), (x + sw * .5, y - h * .5), (x + sw, y - h)], col, 4)
        x += rnd.uniform(4, dens)


def water(p, t, lvl, col1=(52, 108, 150), col2=(34, 74, 112), wave_amp=6):
    p.rect(-400, lvl, AW + 400, AH + 400, col1)
    p.rect(-400, lvl + 60, AW + 400, AH + 400, mix(col1, col2, .5))
    p.rect(-400, lvl + 160, AW + 400, AH + 400, col2)
    for k in range(5):
        y = lvl + 6 + k * 26; ph = t * (.6 + k * .15)
        pts = [(x, y + math.sin(x / 38 + ph * 2 * math.pi) * wave_amp * (1 - k * .12)) for x in range(-60, AW + 80, 24)]
        p.line(pts, mix(col1, (220, 236, 246), .45 - k * .07), 2.5)


def stakes(p, xs, bed, tip_y, lvl, shown=1.0):
    for i, x in enumerate(xs):
        top = lerp(bed, tip_y, shown) + (i % 3) * 6
        p.poly([(x - 7, bed), (x - 7, top + 18), (x, top), (x + 7, top + 18), (x + 7, bed)], (120, 84, 50))
        p.poly([(x - 6, top + 16), (x, top), (x + 6, top + 16)], (176, 180, 188), OUTL, 1.5)


def small_boat(p, x, y, t, crew, face=-1, rowing=True, bob=1.0, ph=0.0, sfx=None, now=0, s=1.0, item='spear'):
    """thuyen nhe; y = mat nuoc. Nguoi ngoi cheo, mai cheo cam xuong nuoc."""
    yy = y + osc(t, .55, ph) * 4 * bob; tilt = osc(t, .55, ph + .25) * 1.5 * bob
    L = (110 + 62 * len(crew)) * s
    hull = [(x - L / 2 - 16 * s, yy - 26 * s - tilt), (x + L / 2 + 16 * s, yy - 26 * s + tilt), (x + L / 2 - 20 * s, yy + 14 * s), (x - L / 2 + 20 * s, yy + 14 * s)]
    p.poly(hull, (124, 80, 44))
    for k, who in enumerate(crew):
        cx = x - L / 2 + 55 * s + k * 62 * s
        if rowing:
            pose = act('row', t, ph + k * .07)
            person(p, cx, yy - 30 * s, who, pose, face, .9 * s, 'oar')
            ph_ = ((t + ph + k * .07) % .9)
            if sfx is not None and k == 0 and abs(ph_ - .02) < .5 / FPS: sfx.append((now, 'oar', .55))
        else:
            person(p, cx, yy - 30 * s, who, act('idle', t, k * .3), face, .9 * s, item)
    p.poly([hull[0], hull[1], (x + L / 2 + 4 * s, yy - 12 * s), (x - L / 2 - 4 * s, yy - 12 * s)], (146, 96, 54), OUTL, 2)
    p.line([(x - L / 2, yy - 2 * s), (x + L / 2, yy - 2 * s)], (90, 56, 30), 3)


def junk(p, x, y, t, face=1, crew=3, sink=0.0, tilt=0.0, ph=0.0, scale=1.0):
    s = scale; yy = y + osc(t, .35, ph) * 5 + sink * 120 * s; tl = tilt + osc(t, .35, ph + .3) * 1.2
    def R(px, py):
        a = math.radians(tl); dx, dy = px * s * face, py * s
        return x + dx * math.cos(a) - dy * math.sin(a), yy + dx * math.sin(a) + dy * math.cos(a)
    # buom vuong
    p.seg(R(0, -40), R(0, -330), 9 * s, (96, 66, 40))
    sail = [R(-10, -320), R(120, -310), R(130, -90), R(-10, -80)]
    p.poly(sail, (196, 164, 118))
    for k in range(1, 6): p.line([R(-10, -320 + k * 40), R(124, -310 + k * 40)], (120, 92, 62), 3 * s)
    p.poly([R(-6, -330), R(-60, -318), R(-6, -306)], (150, 36, 30))     # co tron, khong chu
    # than tau
    hull = [R(-260, -70), R(-200, -40), R(220, -40), R(300, -110), R(310, -60), R(250, 30), R(-210, 30), R(-280, -20)]
    p.poly(hull, (110, 70, 40))
    p.line([R(-230, -20), R(270, -20)], (78, 48, 26), 4 * s); p.line([R(-220, 5), R(255, 5)], (78, 48, 26), 3 * s)
    for k in range(5): p.circ(R(-150 + k * 80, -6), 7 * s, (60, 36, 20), OUTL, 1)
    p.poly([R(150, -40), R(300, -110), R(300, -150), R(160, -110)], (126, 84, 48))   # lau duoi
    for k in range(crew):
        person(p, R(-150 + k * 90, -44)[0], R(-150 + k * 90, -44)[1], 'han', act('idle', t, k * .4 + ph), face, .7 * s, 'spear')
    return R


class FX:
    def __init__(self): self.parts = []
    def burst(self, kind, x, y, n, t, rnd):
        for _ in range(n):
            if kind == 'spark': v = (rnd.uniform(-260, 260), rnd.uniform(-300, 60)); life = rnd.uniform(.2, .45); col = (255, rnd.randint(200, 250), 120)
            elif kind == 'splash': v = (rnd.uniform(-160, 160), rnd.uniform(-420, -160)); life = rnd.uniform(.5, .9); col = (214, 232, 244)
            elif kind == 'wood': v = (rnd.uniform(-220, 220), rnd.uniform(-380, -80)); life = rnd.uniform(.6, 1.1); col = (130, 90, 50)
            else: v = (rnd.uniform(-80, 80), rnd.uniform(-120, -40)); life = 1.0; col = (200, 200, 200)
            self.parts.append([x, y, v[0], v[1], t, life, col, kind])
    def draw(self, p, t):
        keep = []
        for pt in self.parts:
            x, y, vx, vy, t0, life, col, kind = pt; a = t - t0
            if a < 0 or a > life: continue
            keep.append(pt); px, py = x + vx * a, y + vy * a + 600 * a * a
            if kind == 'spark': p.line([(px, py), (px - vx * .03, py - vy * .03)], col, 3)
            elif kind == 'wood': p.seg((px, py), (px + 8, py + 3), 4, col, OUTL, 1)
            else: p.circ((px, py), 4 * (1 - a / life) + 2, col, None)
        self.parts = keep


# ---------- cac mau canh (shot) ----------
def foot(g, s): return g - (L_TH + L_SH) * s * .97     # hong dat sao cho ban chan cham mat dat g


def shot_render(sh, p, t, D, sfx, now, fx, rnd):
    """ve 1 khung cua canh sh tai t (giay ke tu dau canh), D = do dai canh. Tra ve do rung."""
    typ = sh.get('type', 'narrator'); shake = 0
    def every(f, ph=0.0): return int((t + ph) * f) != int((t + ph - 1 / FPS) * f)
    def at(x): return abs(t - x) < .5 / FPS
    if typ == 'fleet_arrive':        # doan tau chien dich keo vao cua song
        hills(p, t, 360, [(96, 112, 124), (74, 92, 98)]); lvl = 420
        water(p, t, lvl); reeds(p, t, -40, 220, lvl + 8, wind=1.2)
        for k in range(int(sh.get('ships', 3)) - 1, -1, -1):
            sc = .75 + k * .22; x = lerp(1300 + k * 200, 300 + k * 330, ease(t / max(2.5, D * .95)))
            junk(p, x, lvl + 120 + k * 120, t, face=-1, crew=3, ph=k * .3, scale=sc)
        if every(1.5): sfx.append((now, 'drum', .9))
    elif typ == 'prep_stakes':       # dan lang dong coc xuong long song luc trieu xuong
        hills(p, t, 300, [(98, 120, 104), (78, 100, 86)]); g = 720
        water(p, t, 470, wave_amp=3)
        p.poly([(-60, 520), (AW + 60, 540), (AW + 60, AH + 60), (-60, AH + 60)], (112, 92, 66))
        stakes(p, [60 + k * 150 for k in range(8)], g - 40, 470, 0)
        for k, (x, who) in enumerate([(250, 'viet'), (560, 'viet2'), (860, 'viet')]):
            s = 1.45; face = 1 if k != 1 else -1
            pose = act('hammer', t, k * .33)
            stake_x = x + face * 112 * s * .62
            stakes(p, [stake_x], g + 6, g - 150 + 26 * ((t + k * .33) % 1.0 > .6), 0)
            r = person(p, x, foot(g, s), who, pose, face, s, 'mallet')
            if at(((t + k * .33) // 1.0) * 1.0 + .6 - k * .33): sfx.append((now, 'thud', .8)); fx.burst('wood', stake_x, g - 150, 7, t, rnd)
        fx.draw(p, t)
    elif typ == 'tide_diagram':      # mat cat: trieu len coc chim, trieu xuong coc nho
        p.rect(-400, -400, AW + 400, AH + 400, (230, 236, 240))
        bed = 720; p.poly([(-50, bed), (AW + 50, bed), (AW + 50, AH + 50), (-50, AH + 50)], (150, 120, 84))
        cyc = float(sh.get('cycle', 6.0)); hi = .5 + .5 * math.cos(2 * math.pi * t / cyc)
        lvl = lerp(500, 200, hi)
        stakes(p, [150 + k * 130 for k in range(7)], bed, 420, lvl)
        wl = Image.new('RGBA', (AW * SS, AH * SS), (0, 0, 0, 0)); wd = ImageDraw.Draw(wl)
        y0 = p.P(0, lvl)[1]; wd.rectangle([0, y0, AW * SS, p.P(0, bed)[1]], fill=(60, 130, 190, 140)); p.extra = wl
        p.line([(30, lvl), (AW - 30, lvl)], (30, 90, 150), 5)
        up = math.sin(2 * math.pi * t / cyc) < 0; ax = 980
        p.poly([(ax - 26, lvl - 40 + (30 if up else 0)), (ax, lvl - 40 + (0 if up else 30)), (ax + 26, lvl - 40 + (30 if up else 0))], (30, 90, 150), None, 0)
        bx = 540 + osc(t, .07) * 200
        small_boat(p, bx, lvl, t, ['viet', 'viet2'], face=1 if osc(t, .07, .25) > 0 else -1, s=1.0)
        if lvl > 400 and rnd.random() < .05: fx.burst('splash', bx, lvl, 4, t, rnd)
        fx.draw(p, t)
    elif typ == 'bait_row':          # thuyen nhe gia thua, tau giac duoi theo
        hills(p, t, 300, [(92, 110, 120), (70, 90, 96)]); lvl = 400; water(p, t, lvl)
        junk(p, 1280 - ease(t / D) * 360, lvl + 110, t, face=-1, crew=3, scale=.85)
        sp = t * 220
        for k in range(8):
            x = (k * 180 - sp) % (AW + 300) - 150; y_ = lvl + 300 + (k % 3) * 40
            p.line([(x, y_ + osc(t, .3, k) * 3), (x + 80, y_)], (210, 230, 244), 3)
        small_boat(p, 470, lvl + 330, t, ['viet', 'viet2', 'viet'], face=-1, sfx=sfx, now=now, s=1.35)
        if rnd.random() < .12: fx.burst('splash', 470 + rnd.uniform(-180, 180), lvl + 345, 4, t, rnd)
        fx.draw(p, t)
    elif typ == 'ambush':            # quan ta tu lau say hai bo xong ra
        hills(p, t, 280, [(80, 100, 90), (62, 82, 72)]); lvl = 430; water(p, t, lvl)
        junk(p, 560, lvl + 120, t, face=-1, crew=3, scale=.8, tilt=osc(t, .7) * 2)
        g = 820; p.poly([(-80, g - 40), (330, g - 10), (330, AH + 60), (-80, AH + 60)], (86, 108, 60)); p.poly([(750, g - 10), (AW + 80, g - 40), (AW + 80, AH + 60), (750, AH + 60)], (86, 108, 60))
        q = ease(t / 1.0)
        for k, (x, face, it) in enumerate([(110, 1, 'bow'), (250, 1, 'spear'), (830, -1, 'spear'), (970, -1, 'bow')]):
            s = 1.3; pose = act('shoot', t, k * .3) if it == 'bow' else act('thrust', t, k * .2)
            person(p, x, lerp(foot(g, s) + 220, foot(g, s), q), 'viet' if k % 2 else 'viet2', pose, face, s, it)
            if it == 'bow' and abs(((t + k * .3) % 1.4) - .62) < .5 / FPS:
                sfx.append((now, 'whoosh', .7)); fx.parts.append([x + face * 60, foot(g, s) - 40, 900 * face, -160, t, 1.0, (60, 40, 20), 'arrow'])
        reeds(p, t, -40, 340, g - 30, (52, 86, 40), 6, 1.6); reeds(p, t, 740, 1120, g - 30, (52, 86, 40), 6, 1.6, seed=9)
        for pt in fx.parts:
            a = t - pt[4]
            if pt[7] == 'arrow' and 0 <= a < pt[5]:
                x_, y_ = pt[0] + pt[2] * a, pt[1] + pt[3] * a + 260 * a * a; dx = 46 * (1 if pt[2] > 0 else -1)
                p.seg((x_ - dx, y_ + 6), (x_, y_), 3, (90, 60, 30), OUTL, 1)
        fx.parts = [pt for pt in fx.parts if t - pt[4] < pt[5]]
        if at(0.05): sfx.append((now, 'shout', .9))
    elif typ == 'melee':             # giap la ca tren ban tau
        hills(p, t, 240, [(90, 96, 100)]); lvl = 700; water(p, t, lvl, wave_amp=8)
        g = 640; p.poly([(-60, g - 10), (AW + 60, g - 10), (AW + 40, g + 60), (-40, g + 60)], (124, 82, 46)); p.line([(-60, g + 4), (AW + 60, g + 4)], (92, 58, 30), 4)
        cyc = 1.1; fall_at = float(sh.get('fall_at', max(3.0, D - 2.0)))
        for k, (x1, x2) in enumerate([(90, 230), (850, 990)]):     # cap danh nhau phia sau
            person(p, x1, foot(g - 70, .85), 'viet2', act('swing', t, k * .4 + .2), 1, .85, 'sword')
            person(p, x2, foot(g - 70, .85), 'han', act('block', t, k * .4), -1, .85, 'spear')
            if abs(((t + k * .4 + .2) % 1.1) - .55) < .5 / FPS: sfx.append((now, 'clash', .4)); fx.burst('spark', (x1 + x2) / 2, g - 200, 8, t, rnd)
        s = 1.9; v = act('thrust', t); fallen = t > fall_at
        h = act('block', t, .05) if not fallen else act('fall', t - fall_at)
        hx = 700 + (min(240, (t - fall_at) * 300) if fallen else 0)
        hy = foot(g, s) + (max(0, (t - fall_at - .35)) ** 2 * 1400 if fallen else 0)
        rv = person(p, 330 + keyf(t, [(0, 0), (.5, 50), (1.1, 0)], loop=cyc), foot(g, s), 'viet', v, 1, s, 'spear')
        rh = person(p, hx, hy, 'han', h, -1, s, 'sword')
        if not fallen and abs((t % cyc) - .5) < .5 / FPS:
            cx_, cy_ = (rv['tip'][0] + rh['hand'][0]) / 2, (rv['tip'][1] + rh['hand'][1]) / 2
            sfx.append((now, 'clash', 1.0)); fx.burst('spark', cx_, cy_, 24, t, rnd); shake = 12
        if at(fall_at): sfx.append((now, 'shout', .7))
        if at(fall_at + .6): sfx.append((now, 'splash', 1.0)); fx.burst('splash', hx + 80, lvl, 28, t, rnd); shake = 6
        fx.draw(p, t)
    elif typ == 'crash_stakes':      # trieu rut, tau dam vao bai coc
        hills(p, t, 260, [(84, 96, 104), (66, 78, 86)])
        hit = D * .45; q = ease(min(1, t / max(1.5, hit))); lvl = lerp(360, 470, q)
        sink = max(0, (t - hit) / max(.1, D - hit)) if t > hit else 0
        water(p, t, lvl)
        jx = 640 - min(t, hit) * 60; jolt = osc(t, 9) * 4 if hit < t < hit + .6 else 0
        junk(p, jx, lvl + 150, t, face=-1, crew=3, scale=1.05, sink=sink * .45, tilt=-16 * ease(sink * 2) + jolt)
        xs = [70 + k * 120 for k in range(9)]
        stakes(p, xs, AH + 40, 470, lvl)
        if at(hit):
            sfx.append((now, 'crack', 1.0)); sfx.append((now + .18, 'crack', .7)); sfx.append((now + .05, 'thud', .9)); shake = 18
            for x in xs[2:6]: fx.burst('wood', x, 500, 9, t, rnd)
        if hit < t < hit + 1.6 and rnd.random() < .3: fx.burst('splash', jx + rnd.uniform(-260, 260), lvl, 6, t, rnd)
        if at(hit + .7): sfx.append((now, 'splash', .9)); sfx.append((now, 'shout', .5))
        if t > hit: shake = max(shake, 5 * (1 - min(1, (t - hit) / .8)))
        fx.draw(p, t)
    elif typ == 'victory':
        hills(p, t, 380, [(110, 104, 120), (86, 82, 96)]); lvl = 520
        p.circ((820, 260), 80 + osc(t, .2) * 3, (255, 214, 140), None)
        water(p, t, lvl); junk(p, 800, lvl + 90, t, face=-1, crew=0, scale=.65, tilt=-18, sink=.35)
        g = 800; p.poly([(-80, g - 60), (600, g - 10), (600, AH + 60), (-80, AH + 60)], (96, 120, 70))
        for k, x in enumerate([100, 240, 380, 520]):
            s = 1.35 - k * .06; person(p, x, foot(g - 40 + k * 10, s), 'viet' if k % 2 else 'viet2', act('cheer', t, k * .25), 1, s, 'spear' if k != 1 else 'flag')
        if every(1.0): sfx.append((now, 'drum', .8))
        if at(0.05): sfx.append((now, 'shout', .9))
    elif typ == 'general':           # tuong chi huy tren thuyen
        hills(p, t, 300, [(88, 100, 110), (70, 82, 92)]); lvl = 470; water(p, t, lvl)
        bx = 520; small_boat(p, bx, lvl + 260, t, ['viet', 'viet2', 'viet'], face=1, sfx=sfx, now=now, s=1.2)
        person(p, bx + 40, foot(lvl + 260 - 26 * 1.2, 1.7) + osc(t, .55) * 4, 'general', act('command', t), 1, 1.7, 'sword')
        if every(1.4): sfx.append((now, 'drum', .7))
    else:                            # narrator: cau hoc tro doi non la chi bang
        p.rect(-400, -400, AW + 400, AH + 400, (240, 232, 214))
        p.poly([(60, 110), (720, 110), (720, 600), (60, 600)], (44, 70, 62))
        p.line([(120, 500), (660, 500)], (210, 220, 210), 6)
        for k in range(5): p.line([(160 + k * 115, 500), (160 + k * 115, 400 + (k % 2) * 30)], (226, 196, 140), 8)
        lv = 440 + osc(t, .25) * 50; p.line([(90, lv), (690, lv)], (120, 180, 230), 5)
        s = 2.0; person(p, 880, foot(800, s), 'scholar', act('point', t), -1, s, 'board')
    return shake


# ---------- chu: tieu de, phu de, chu khoa, hook, ket ----------
def text_c(d, y, s, f, fill, stroke=3):
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def header(im, sp):
    d = ImageDraw.Draw(im)
    for y in range(256, 404):
        a = (y - 256) / 148; d.line([(0, y), (W, y)], fill=mix(RED1, RED2, a))
    d.rectangle([0, 404, W, 409], fill=YEL)
    s = sp.get('series', ''); fS = F(True, 60)
    while d.textlength(s, font=fS) > TW and fS.size > 40: fS = F(True, fS.size - 2)
    text_c(d, 276, s, fS, YEL)
    b = sp.get('badge', 'MỔ XẺ CHIẾN THUẬT'); fB = F(True, 30); bw = d.textlength(b, font=fB)
    d.rounded_rectangle([(W - bw) / 2 - 20, 350, (W + bw) / 2 + 20, 396], 12, fill=INK); text_c(d, 354, b, fB, WHITE, 0)


def main():
    inp = json.loads(os.environ['SPEC_JSON'])
    if 'shots' in inp: sp = inp
    else:
        br, dd = inp['branch'], inp['dir'].strip('/')
        subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
        __import__('gitlay').lay(dd)
        sp = json.load(open(os.path.join(ROOT, dd, 'spec.json'), encoding='utf-8'))
    shots = sp['shots']; n = len(shots)
    # giong
    srt, voice, dur = [], None, None
    urls = sp.get('voice_urls') or []
    if urls:
        parts, off = [], 0.0
        for i, u in enumerate(urls):
            pth = u if os.path.exists(u) else get(u, os.path.join(OUT, f'vp{i}.mp3')); wav_ = os.path.join(OUT, f'vp{i}.wav')
            dd_, lead = voice_part(pth, wav_, sp, i, sr=SR)
            su = (sp.get('srt_urls') or [''] * len(urls))[i]
            if su:
                try:
                    txt = open(su if os.path.exists(su) else get(su, os.path.join(OUT, f'vp{i}.srt')), encoding='utf-8').read()
                    srt += [(max(0, a - lead) + off, max(0, b - lead) + off, tx) for a, b, tx in parse_srt(txt)]
                except Exception as e: print('srt', e)
            parts.append(wav_); off += dd_
        lst = os.path.join(OUT, 'vl.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
        voice = os.path.join(OUT, 'voice.wav'); subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice]); dur = off
        from series import fix_cues
        srt = fix_cues(srt); st = scene_starts(sp, srt, n, dur)
    else:
        durs = sp.get('durs') or [5.0] * n; st = [sum(durs[:k]) for k in range(n)]; dur = sum(durs)
        srt = [(st[k], st[k] + durs[k] - .2, shots[k].get('say', '')) for k in range(n) if shots[k].get('say')]
    LEAD, TAIL = .1, 2.6; D = dur + LEAD + TAIL
    ends = st[1:] + [dur + TAIL]
    wts = word_times(srt)
    base = Image.new('RGB', (W, H), (14, 10, 10)); header(base, sp)
    sfx = []; rnd = random.Random(11); fxs = [FX() for _ in shots]
    raw = os.path.join(OUT, 'v_tmp.mp4')
    pr = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    hook = (sp.get('hook_text') or '').strip().upper(); prev_k = -1
    for fi in range(int(D * FPS)):
        tt = fi / FPS; tv = tt - LEAD
        k = max(0, max(i for i in range(n) if st[i] <= max(0, tv)))
        sh = shots[k]; ts = max(0.0, tv - st[k]); Dk = ends[k] - st[k]
        if k != prev_k: sfx.append((tt, 'whoosh', .35)); prev_k = k
        # camera: dong cham + rung
        z0, z1 = sh.get('zoom', [1.0, 1.08]); cam = [AW / 2 + sh.get('pan', 0) * ease(ts / Dk), AH / 2, lerp(z0, z1, ease(ts / max(1, Dk)))]
        canvas = Image.new('RGB', (AW * SS, AH * SS), SKIES.get(sh.get('sky', 'day'), SKIES['day'])[1])
        canvas.paste(sky(None, *SKIES.get(sh.get('sky', 'day'), SKIES['day'])))
        cd = ImageDraw.Draw(canvas); pen = Pen(cd, cam); pen.extra = None
        shake = shot_render(sh, pen, ts, Dk, sfx, tt, fxs[k], rnd)
        if pen.extra is not None: canvas.paste(pen.extra, (0, 0), pen.extra)
        act_img = canvas.resize((AW, AH), Image.LANCZOS)
        # nen toan khung = chinh canh do, phong to + mo + toi (khong de vien den)
        bg = act_img.resize((27, 48), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        im = Image.blend(bg, Image.new('RGB', (W, H), (10, 6, 6)), .45)
        im.paste(base.crop((0, 250, W, 410)), (0, 250))
        ox = int(rnd.uniform(-shake, shake)) if shake else 0; oy = int(rnd.uniform(-shake, shake)) if shake else 0
        im.paste(act_img, (ox, AY0 + oy))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 404, W, 409], fill=YEL)
        # chu khoa cua canh (1.8s dau canh)
        key = (sh.get('key') or '').upper()
        if key and ts < 2.2:
            q = ease(ts / .2) * (1 - ease(max(0, ts - 1.9) / .3)); fK = F(True, 64)
            while d.textlength(key, font=fK) > TW - 40 and fK.size > 36: fK = F(True, fK.size - 2)
            kw = d.textlength(key, font=fK); y = 440
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([(W - kw) / 2 - 26, y - 12, (W + kw) / 2 + 26, y + fK.size + 22], 18, fill=(10, 8, 8, int(200 * q)))
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            if q > .1: text_c(d, y, key, fK, YEL, 4)
        # hook 0-2.6s
        if hook and tv < 2.6:
            q = ease(min(1, (tv + LEAD) / .25)) * (1 - ease(max(0, tv - 2.3) / .3)); fH = F(True, 84)
            while len(wrap_bal(d, hook, fH, TW - 40)) > 3 and fH.size > 52: fH = F(True, fH.size - 4)
            hl = wrap_bal(d, hook, fH, TW - 40)[:3]; lh = int(fH.size * 1.2); hh = lh * len(hl) + 50; y0 = 760 - hh / 2
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([SX0, y0, SX1, y0 + hh], 28, fill=(16, 8, 8, int(225 * q))); od.rounded_rectangle([SX0, y0, SX1, y0 + hh], 28, outline=(*YEL, int(255 * q)), width=5)
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            if q > .05:
                for j, ln in enumerate(hl): text_c(d, y0 + 25 + j * lh, ln, fH, YEL, 5)
        # nen toi cho phu de + phu de karaoke neo day
        cur = next((s_ for s_ in wts if s_[0] - .05 <= tv < s_[1] + .1), None)
        if cur and tt < D - TAIL:
            ws = cur[2]; txt = ' '.join(w_ for _, _, w_ in ws); fC = F(True, 56)
            while len(wrap_bal(d, txt, fC, TW)) > 3 and fC.size > 40: fC = F(True, fC.size - 4)
            lines = wrap_bal(d, txt, fC, TW)[:3]; LH = int(fC.size * 1.32); y = SY1 - 8 - len(lines) * LH
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([SX0 - 4, y - 14, SX1 + 4, SY1 + 2], 22, fill=(8, 6, 6, 170)); im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            wi = 0
            for j, ln in enumerate(lines):
                x = (W - d.textlength(ln, font=fC)) / 2
                for wd in ln.split(' '):
                    a_, b_, _ = ws[wi] if wi < len(ws) else (0, 0, wd); wi += 1
                    s_ = wd.strip('.,!?…:;"“”'); keyw = s_.isupper() and len(s_) > 1
                    wl = d.textlength(wd, font=fC)
                    if a_ <= tv < b_ + .02:
                        d.rounded_rectangle([x - 8, y + j * LH - 4, x + wl + 8, y + j * LH + LH - 6], 12, fill=YEL); d.text((x, y + j * LH), wd, font=fC, fill=INK)
                    else:
                        d.text((x, y + j * LH), wd, font=fC, fill=(YEL if keyw else WHITE), stroke_width=4, stroke_fill=(0, 0, 0))
                    x += d.textlength(wd + ' ', font=fC)
        # ket
        if tt >= D - TAIL:
            q = ease((tt - (D - TAIL)) / .35)
            ov = Image.new('RGBA', (W, H), (12, 6, 6, int(215 * q))); im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            if q > .5:
                y = 600; fO = F(True, 64); nx = sp.get('next', '')
                for ln in wrap_bal(d, nx, fO, TW)[:3]: text_c(d, y, ln, fO, WHITE, 4); y += int(fO.size * 1.35)
                lab = 'THEO DÕI KÝ SỬ CHIẾN'; fB = F(True, 50); bw_ = d.textlength(lab, font=fB)
                d.rounded_rectangle([(W - bw_) / 2 - 40, y + 50, (W + bw_) / 2 + 40, y + 146], 34, fill=YEL); d.text(((W - bw_) / 2, y + 68), lab, font=fB, fill=INK)
                text_c(d, y + 190, 'Hoạt hình minh hoạ, giản lược', F(False, 34), (220, 210, 200), 0)
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); pr.wait()
    sw = mix_audio(sfx, D, path=os.path.join(OUT, 'sfx.wav'))
    mus = os.path.join(ROOT, 'editor', 'story', sp.get('music', 'music_b.mp3'))
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    if voice:
        fc = f'[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)}[v];[2:a]volume=0.55[s];[3:a]volume=0.08[m];[v][s][m]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-15:TP=-1.5[a]'
        ins = ['-i', voice, '-i', sw, '-stream_loop', '-1', '-i', mus]
    else:
        fc = '[1:a]volume=0.9[s];[2:a]volume=0.10[m];[s][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-15:TP=-1.5[a]'
        ins = ['-i', sw, '-stream_loop', '-1', '-i', mus]
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw] + ins + ['-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    print('ok', round(D, 2), 'sfx', len(sfx))


if __name__ == '__main__':
    main()
