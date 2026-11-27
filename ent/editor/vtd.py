"""Vang & Tu duy (vtd) - video giai thich tai chinh ngang 16:9 theo mau kenh "Tien & Tu duy" (chu chot hoc 21/11/2026).
Cong thuc: 1 cau chuyen xuyen suot (anh Tin + 1 luong vang) + O DEM tien do goc phai (von / lai-lo / bai hoc x/N)
+ bang ten chuong ghim tren dau + nen den hoa tiet net xam theo chu de + nhan vat net den trang nhieu tu the
+ chu to 1-2 dong / cong thuc ngan / so lieu that + tong ket dang luoi o.
SPEC_JSON: {page, story:{who, asset}, lessons:N, beats:[{chap, theme, say, tracker?, els:[...]}],
            voice:[[url, pause], ...]  (W87, dung thu tu cau), fmt?:'h'}
Moi beat: say (1..n cau, tach dung regex cua W87) ; els xuat hien theo 'at' = chi so cau (so thuc = phan cua cau do).
"""
import json, math, os, random, re, subprocess, sys, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1920, 1080, 30
ROOT = os.getcwd(); OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
SR = 44100
BG = '#151515'; DOOD = '#2b2b2b'; INK = '#0e0e0e'
CREAM = '#f3e4b0'; GOLD = '#f2c14e'; RED = '#ff6b5b'; GREEN = '#7fd18b'; BLUE = '#6fb6ff'; ORANGE = '#f07a3c'
COL = {'y': CREAM, 'r': RED, 'g': GREEN, 'b': BLUE, 'o': ORANGE, 'gold': GOLD}
FAM = "'Be Vietnam Pro','Inter',sans-serif"
SPLIT = re.compile(r'(?<=[.!?…])\s+')
INTRO = 0.42          # pop-in moi phan tu
G = {}


def f_(v): return f'{v:.1f}'
def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def clamp(q): return max(0.0, min(1.0, q))
def ease(q): q = clamp(q); return q * q * (3 - 2 * q)
def back(q):
    q = clamp(q); c = 1.70158; return 1 + (c + 1) * (q - 1) ** 3 + c * (q - 1) ** 2


_FC = {}
def font(size):
    if size not in _FC:
        for p in [os.path.join(ROOT, 'fonts', 'BeVietnamPro-ExtraBold.ttf'), '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf',
                  '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
            if os.path.exists(p): _FC[size] = ImageFont.truetype(p, size); break
    return _FC[size]


def tw(s, size, ls=0):
    return font(size).getlength(s) + ls * max(0, len(s) - 1)


def fit(s, size, maxw, ls=1):
    while tw(s, size, ls) > maxw and size > 14: size -= 1
    return size


def text(x, y, s, size, fill, anchor='middle', ls=1, op=1.0, stroke=None):
    st = f' stroke="{stroke}" stroke-width="{size * .09:.1f}" paint-order="stroke" stroke-linejoin="round"' if stroke else ''
    return (f'<text x="{f_(x)}" y="{f_(y)}" font-family="{FAM}" font-weight="800" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op:.2f}"{st}>{esc(s)}</text>')


def pop(inner, cx, cy, q, kind='pop'):
    """bao 1 nhom: pop-in vuot da quanh (cx,cy)."""
    if q <= 0: return ''
    if q >= 1: return inner
    if kind == 'slide':
        dy = (1 - ease(q)) * 40; return f'<g transform="translate(0,{f_(dy)})" opacity="{ease(q * 1.6):.2f}">{inner}</g>'
    s = back(q)
    return f'<g opacity="{ease(q * 2):.2f}" transform="translate({f_(cx)},{f_(cy)}) scale({s:.3f}) translate({f_(-cx)},{f_(-cy)})">{inner}</g>'


# ---------------- icon net (dung cho hoa tiet nen va icon mau) ----------------
def icon(kind, x, y, s, st=DOOD, sw=3.0, fill='none', rot=0.0):
    k = s / 80.0; o = []
    def P(d, f=fill): o.append(f'<path d="{d}" fill="{f}" stroke="{st}" stroke-width="{sw / k:.2f}" stroke-linejoin="round" stroke-linecap="round"/>')
    def C(cx, cy, r, f=fill): o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{f}" stroke="{st}" stroke-width="{sw / k:.2f}"/>')
    if kind == 'bar':
        P('M-34,16 L-22,-14 L22,-14 L34,16 Z'); P('M-22,-14 L-16,-22 L28,-22 L22,-14', 'none'); P('M22,-14 L28,-22 L40,8 L34,16', 'none')
    elif kind == 'coin':
        C(0, 0, 30); C(0, 0, 20, 'none'); P('M-6,-8 L6,-8 M0,-12 L0,12 M-6,8 L6,8', 'none')
    elif kind == 'ring':
        C(0, 8, 24); C(0, 8, 15, BG if fill != 'none' else 'none'); P('M-10,-16 L0,-30 L10,-16 Z')
    elif kind == 'candle':
        for i, (xx, a, b) in enumerate([(-24, -10, 18), (0, -26, 6), (24, -4, 24)]):
            P(f'M{xx},{a - 10} L{xx},{b + 10}', 'none'); P(f'M{xx - 8},{a} L{xx + 8},{a} L{xx + 8},{b} L{xx - 8},{b} Z')
    elif kind == 'line':
        P('M-36,22 L-12,0 L4,10 L34,-22', 'none'); P('M22,-22 L34,-22 L34,-10', 'none'); P('M-38,30 L38,30 M-38,30 L-38,-30', 'none')
    elif kind == 'down':
        P('M-30,-24 L-6,0 L6,-10 L32,22', 'none'); P('M20,22 L32,22 L32,10', 'none')
    elif kind == 'pct':
        C(-16, -16, 9); C(16, 16, 9); P('M22,-26 L-22,26', 'none')
    elif kind == 'shop':
        P('M-34,-6 L34,-6 L34,30 L-34,30 Z'); P('M-38,-6 L-30,-28 L30,-28 L38,-6', 'none'); P('M-8,30 L-8,8 L8,8 L8,30', 'none')
    elif kind == 'scale':
        P('M0,-28 L0,26 M-20,26 L20,26 M-30,-18 L30,-18', 'none'); P('M-30,-18 L-40,4 L-20,4 Z'); P('M30,-18 L20,4 L40,4 Z')
    elif kind == 'tag':
        P('M-30,-10 L-10,-30 L30,-30 L30,10 L10,30 Z'); C(14, -14, 5, 'none')
    elif kind == 'globe':
        C(0, 0, 30); P('M-30,0 L30,0 M0,-30 Q-16,0 0,30 M0,-30 Q16,0 0,30', 'none')
    elif kind == 'bell':
        P('M-22,14 Q-22,-26 0,-26 Q22,-26 22,14 L28,20 L-28,20 Z'); C(0, 26, 5)
    elif kind == 'warn':
        P('M0,-30 L32,26 L-32,26 Z'); P('M0,-10 L0,8 M0,15 L0,17', 'none')
    elif kind == 'cal':
        P('M-30,-22 L30,-22 L30,28 L-30,28 Z'); P('M-30,-8 L30,-8 M-16,-30 L-16,-16 M16,-30 L16,-16', 'none')
    elif kind == 'clock':
        C(0, 0, 30); P('M0,-18 L0,0 L14,8', 'none')
    elif kind == 'bank':
        P('M-34,-12 L0,-32 L34,-12 Z'); P('M-30,26 L30,26 M-22,-8 L-22,22 M-7,-8 L-7,22 M7,-8 L7,22 M22,-8 L22,22', 'none')
    elif kind == 'pig':
        P('M-28,8 Q-30,-24 4,-24 Q30,-24 30,4 Q30,24 4,24 L-20,24 Q-30,24 -28,8 Z'); P('M-6,-24 L4,-30', 'none'); C(30, 2, 6)
    elif kind == 'wallet':
        P('M-32,-18 L28,-18 L28,24 L-32,24 Z'); P('M8,-4 L34,-4 L34,10 L8,10 Z')
    elif kind == 'bulb':
        P('M-14,12 Q-28,-4 -18,-20 Q0,-36 18,-20 Q28,-4 14,12 Z'); P('M-10,18 L10,18 M-7,24 L7,24', 'none')
    tr = f'translate({f_(x)},{f_(y)}) rotate({rot:.1f}) scale({k:.3f})'
    return f'<g transform="{tr}">{"".join(o)}</g>'


THEMES = {'gold': ['bar', 'coin', 'ring', 'pct', 'line'], 'shop': ['shop', 'scale', 'tag', 'coin', 'bar'],
          'chart': ['candle', 'line', 'down', 'globe', 'pct'], 'alarm': ['bell', 'warn', 'down', 'pct', 'candle'],
          'calendar': ['cal', 'clock', 'coin', 'pct', 'bar'], 'bank': ['bank', 'pig', 'wallet', 'pct', 'coin']}
_BGC = {}


def background(theme):
    if (theme, W) in _BGC: return _BGC[(theme, W)]
    rnd = random.Random(sum(map(ord, theme)) * 7 + W); kinds = THEMES.get(theme, THEMES['gold']); o = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    for gy in range(int(H / 165) + 1):
        for gx in range(int(W / 168) + 1):
            x = gx * 168 + 84 + (84 if gy % 2 else 0) + rnd.uniform(-30, 30); y = 150 + gy * 165 + rnd.uniform(-30, 30)
            o.append(icon(rnd.choice(kinds), x, y, rnd.uniform(70, 100), DOOD, 3.2, 'none', rnd.uniform(-22, 22)))
            if rnd.random() < .5:
                o.append(f'<circle cx="{f_(x + rnd.uniform(-80, 80))}" cy="{f_(y + rnd.uniform(-80, 80))}" r="{rnd.uniform(3, 6):.1f}" fill="none" stroke="{DOOD}" stroke-width="2.5"/>')
    _BGC[(theme, W)] = ''.join(o); return _BGC[(theme, W)]


# ---------------- nhan vat: ANH TIN (net den, toc dung, kinh tron, ao polo co huy hieu vang) ----------------
SKIN = '#f2f1ec'; SHIRT = '#e4e3dd'; PANTS = '#3e3e40'; HAIR = '#141414'; SW = 7


def ik(sx, sy, hx, hy, l1, l2, bend):
    dx, dy = hx - sx, hy - sy; d = max(1e-3, min(l1 + l2 - 1, math.hypot(dx, dy)))
    a = math.atan2(dy, dx); c = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)) if d else 1
    b = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    ang = a + bend * b
    return sx + l1 * math.cos(ang), sy + l1 * math.sin(ang)


POSES = {  # (khuyu trai, tay trai, khuyu phai, tay phai) - toa do cuc bo, goc chan (0,0), len tren am; nhin sang phai
    'idle': ((-128, -290), (-132, -200), (128, -290), (132, -200)),
    'hold': ((-140, -300), (-58, -292), (140, -300), (58, -292)),
    'point': ((-128, -290), (-132, -200), (195, -400), (282, -418)),
    'point_up': ((-128, -290), (-132, -200), (180, -470), (168, -612)),
    'think': ((-120, -282), (24, -268), (158, -300), (62, -428)),
    'shock': ((-190, -468), (-108, -566), (190, -468), (108, -566)),
    'facepalm': ((-128, -290), (-132, -200), (172, -432), (42, -566)),
    'wave': ((-128, -290), (-132, -200), (205, -470), (236, -622))}


def face(expr, talk, cx, cy):
    o = []; ey = cy - 4
    def L(d, w=5.5): o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    # kinh tron
    for ex in (-34, 34):
        o.append(f'<circle cx="{cx + ex}" cy="{ey}" r="25" fill="#ffffff" fill-opacity=".35" stroke="{INK}" stroke-width="5"/>')
    L(f'M{cx - 9},{ey} Q{cx},{ey - 6} {cx + 9},{ey}', 4.5)
    if expr == 'happy':
        for ex in (-34, 34): L(f'M{cx + ex - 11},{ey + 4} Q{cx + ex},{ey - 9} {cx + ex + 11},{ey + 4}', 5)
    elif expr == 'shock':
        for ex in (-34, 34): o.append(f'<circle cx="{cx + ex}" cy="{ey}" r="12" fill="#fff" stroke="{INK}" stroke-width="4"/><circle cx="{cx + ex}" cy="{ey}" r="4.5" fill="{INK}"/>')
    elif expr == 'think':
        for ex in (-34, 34): o.append(f'<circle cx="{cx + ex + 7}" cy="{ey - 7}" r="7" fill="{INK}"/>')
    else:
        for ex in (-34, 34): o.append(f'<ellipse cx="{cx + ex}" cy="{ey + 1}" rx="6.5" ry="8.5" fill="{INK}"/>')
    # long may
    if expr in ('sad', 'worry'):
        L(f'M{cx - 52},{ey - 30} L{cx - 18},{ey - 40}'); L(f'M{cx + 18},{ey - 40} L{cx + 52},{ey - 30}')
    elif expr == 'think':
        L(f'M{cx - 52},{ey - 36} L{cx - 18},{ey - 36}'); L(f'M{cx + 18},{ey - 44} Q{cx + 36},{ey - 54} {cx + 52},{ey - 42}')
    elif expr == 'shock':
        L(f'M{cx - 50},{ey - 46} Q{cx - 34},{ey - 56} {cx - 18},{ey - 46}'); L(f'M{cx + 18},{ey - 46} Q{cx + 34},{ey - 56} {cx + 50},{ey - 46}')
    else:
        L(f'M{cx - 50},{ey - 38} Q{cx - 34},{ey - 46} {cx - 18},{ey - 38}'); L(f'M{cx + 18},{ey - 38} Q{cx + 34},{ey - 46} {cx + 50},{ey - 38}')
    my = cy + 50
    if expr == 'shock':
        o.append(f'<ellipse cx="{cx}" cy="{my + 4}" rx="{14 if not talk else 17}" ry="{18 if not talk else 22}" fill="#5a1f1f" stroke="{INK}" stroke-width="5"/>')
    elif talk:
        if expr in ('happy',):
            o.append(f'<path d="M{cx - 30},{my - 6} Q{cx},{my - 2} {cx + 30},{my - 6} Q{cx + 24},{my + 26} {cx},{my + 26} Q{cx - 24},{my + 26} {cx - 30},{my - 6} Z" fill="#5a1f1f" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
        else:
            o.append(f'<ellipse cx="{cx}" cy="{my + 4}" rx="17" ry="13" fill="#5a1f1f" stroke="{INK}" stroke-width="5"/>')
    elif expr == 'happy': L(f'M{cx - 28},{my - 4} Q{cx},{my + 22} {cx + 28},{my - 4}', 6)
    elif expr in ('sad', 'worry'): L(f'M{cx - 22},{my + 10} Q{cx},{my - 8} {cx + 22},{my + 10}', 6)
    elif expr == 'think': L(f'M{cx - 6},{my + 4} L{cx + 22},{my}', 6)
    else: L(f'M{cx - 20},{my} Q{cx},{my + 10} {cx + 20},{my}', 6)
    if expr in ('worry', 'shock'):
        o.append(f'<path d="M{cx + 92},{cy - 46} q8,14 0,22 q-8,-8 0,-22 Z" fill="#9fd3ff" stroke="{INK}" stroke-width="3.5"/>')
    return ''.join(o)


def arm(sx, sy, ex, ey, hx, hy):
    d = f'M{f_(sx)},{f_(sy)} L{f_(ex)},{f_(ey)} L{f_(hx)},{f_(hy)}'
    o = [f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{42 + 2 * SW}" stroke-linecap="round" stroke-linejoin="round"/>',
         f'<path d="{d}" fill="none" stroke="{SKIN}" stroke-width="42" stroke-linecap="round" stroke-linejoin="round"/>']
    mx, my = sx + (ex - sx) * .45, sy + (ey - sy) * .45
    o.append(f'<path d="M{f_(sx)},{f_(sy)} L{f_(mx)},{f_(my)}" stroke="{INK}" stroke-width="{60 + 2 * SW}" stroke-linecap="round"/>'
             f'<path d="M{f_(sx)},{f_(sy)} L{f_(mx)},{f_(my)}" stroke="{SHIRT}" stroke-width="60" stroke-linecap="round"/>')
    o.append(f'<circle cx="{f_(hx)}" cy="{f_(hy)}" r="27" fill="{SKIN}" stroke="{INK}" stroke-width="{SW}"/>')
    return ''.join(o)


def man(pose='idle', expr='normal', talk=False, x=1400, y=1000, s=1.0, face_dir=1, t=0.0):
    le, la, re_, ra = POSES.get(pose, POSES['idle'])
    o = []
    # chan + quan
    for lx in (-44, 44):
        o.append(f'<path d="M{lx - 36},-215 L{lx + 36},-215 L{lx + 30},-16 L{lx - 30},-16 Z" fill="{PANTS}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')
        o.append(f'<ellipse cx="{lx + 10}" cy="-10" rx="46" ry="18" fill="{SKIN}" stroke="{INK}" stroke-width="{SW}"/>')
    # than ao polo
    o.append(f'<path d="M-112,-392 Q-126,-300 -104,-200 L104,-200 Q126,-300 112,-392 Q0,-422 -112,-392 Z" fill="{SHIRT}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')
    o.append(f'<path d="M-34,-404 L0,-360 L34,-404" fill="#ffffff" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
             f'<path d="M0,-360 L0,-318" stroke="{INK}" stroke-width="4"/><circle cx="0" cy="-340" r="3.5" fill="{INK}"/><circle cx="0" cy="-326" r="3.5" fill="{INK}"/>')
    o.append(f'<circle cx="-50" cy="-336" r="13" fill="{GOLD}" stroke="{INK}" stroke-width="4"/>')
    o.append(f'<path d="M-104,-214 L104,-214" stroke="{INK}" stroke-width="4" opacity=".5"/>')
    # dau
    hx, hy = 0, -520
    o.append(f'<circle cx="{hx - 96}" cy="{hy + 8}" r="20" fill="{SKIN}" stroke="{INK}" stroke-width="{SW}"/><circle cx="{hx + 96}" cy="{hy + 8}" r="20" fill="{SKIN}" stroke="{INK}" stroke-width="{SW}"/>')
    o.append(f'<circle cx="{hx}" cy="{hy}" r="100" fill="{SKIN}" stroke="{INK}" stroke-width="{SW}"/>')
    spikes = ' '.join(f'L{f_(hx + math.cos(a) * r)},{f_(hy + math.sin(a) * r)}' for a, r in
                      [(math.radians(d), rr) for d, rr in [(-178, 98), (-170, 128), (-155, 108), (-140, 140), (-125, 116), (-108, 146), (-92, 118), (-76, 146), (-60, 114), (-44, 136), (-28, 104), (-14, 118), (-4, 96)]])
    o.append(f'<path d="M{hx - 98},{hy - 2} {spikes} Q{hx + 40},{hy - 40} {hx - 10},{hy - 54} Q{hx - 60},{hy - 52} {hx - 98},{hy - 2} Z" fill="{HAIR}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')
    o.append(face(expr, talk, hx, hy + 14))
    # tay (tay sau ve truoc than neu ve phia trong)
    o.append(arm(-100, -378, le[0], le[1], la[0], la[1])); o.append(arm(100, -378, re_[0], re_[1], ra[0], ra[1]))
    # do cam
    if pose == 'hold':
        o.append(icon('bar', 0, -318, 170, INK, 6, GOLD))
    if pose in ('point', 'point_up', 'wave'):
        tx, ty = ra
        if pose == 'point': o.append(f'<path d="M{tx + 18},{ty - 4} L{tx + 60},{ty - 10}" stroke="{INK}" stroke-width="{16 + 2 * SW}" stroke-linecap="round"/><path d="M{tx + 14},{ty - 4} L{tx + 60},{ty - 10}" stroke="{SKIN}" stroke-width="16" stroke-linecap="round"/>')
        elif pose == 'point_up':
            o.append(f'<path d="M{tx + 2},{ty - 14} L{tx + 6},{ty - 52}" stroke="{INK}" stroke-width="{16 + 2 * SW}" stroke-linecap="round"/><path d="M{tx + 2},{ty - 14} L{tx + 6},{ty - 52}" stroke="{SKIN}" stroke-width="16" stroke-linecap="round"/>')
            o.append(icon('bulb', tx - 120, ty - 20, 90, INK, 5, '#ffe27a'))
    tr = f'translate({f_(x)},{f_(y)}) scale({s * face_dir:.3f},{s:.3f})'
    return f'<g transform="{tr}">{"".join(o)}</g>'


# ---------------- khung co dinh ----------------
def topbar(chap, q):
    o = [f'<rect width="{W}" height="118" fill="#060606"/>']
    sz = 54
    while tw(chap, sz) > W - 80 and sz > 30: sz -= 2
    o.append(f'<g opacity="{ease(q * 1.5):.2f}" transform="translate(0,{f_((1 - ease(q)) * -18)})">{text(W / 2, 59 + sz * .38, chap, sz, "#ffffff", ls=0)}</g>')
    return ''.join(o)


def tracker_svg(st, pulse, lessons, who, asset):
    w, h = 420, 152; x, y = W - w - 40, (134 if W > H else 122)
    col = RED if st.get('c') == 'r' else (GREEN if st.get('c') == 'g' else ORANGE)
    sc = 1 + .08 * math.sin(math.pi * clamp(pulse)) if pulse < 1 else 1
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#1c1c1c" stroke="{col}" stroke-width="5"/>',
         icon('bar', x + 34, y + 34, 44, INK, 4, GOLD), text(x + 66, y + 44, f'{who} · {asset}', fit(f'{who} · {asset}', 27, w - 86, 1), '#bdb7a6', 'start', 1),
         text(x + 26, y + 98, st.get('v', ''), 46, RED if st.get('c') == 'r' else CREAM, 'start', 1),
         text(x + 26, y + 136, f'BÀI HỌC: {st.get("n", 0)} / {lessons}', 30, GREEN if st.get('n', 0) >= lessons else '#c9c3b0', 'start', 1)]
    cx, cy = x + w / 2, y + h / 2
    flash = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#fff" opacity="{.35 * (1 - clamp(pulse)):.2f}"/>' if pulse < 1 else ''
    return f'<g transform="translate({f_(cx)},{f_(cy)}) scale({sc:.3f}) translate({f_(-cx)},{f_(-cy)})">{"".join(o)}{flash}</g>'


# ---------------- phan tu noi dung ----------------
def el_svg(e, tl, ta, ctx):
    """tl: thoi gian trong beat; ta: moc xuat hien cua phan tu. tra ve svg."""
    q = (tl - ta) / INTRO; k = e['k']
    if q <= 0: return ''
    if k == 'man':
        if e.get('_hide'): return ''
        return pop(man(e.get('pose', 'idle'), e.get('expr', 'normal'), ctx['talk'], e.get('x', 1420), e.get('y', 1055), e.get('s', 1.12), e.get('face', 1)),
                   e.get('x', 1420), e.get('y', 1055) - 350, q, 'slide')
    if k in ('title', 'big', 'line'):
        size = e.get('size') or {'title': 86, 'big': 104, 'line': 58}[k]; s = e['t']
        while tw(s, size, 2) > e.get('maxw', 1000) and size > 36: size -= 2
        col = COL.get(e.get('col', 'y'), CREAM)
        inner = text(e['x'], e['y'], s, size, col, ls=2)
        if e.get('icon'):
            ix = e['x'] + tw(s, size, 2) / 2 + 74
            inner += icon(e['icon'], ix, e['y'] - size * .34, size * 1.25, INK, 5, GOLD if e['icon'] in ('bar', 'coin', 'ring') else ('#9fd3ff' if e['icon'] == 'globe' else '#e9e4d4'))
        return pop(inner, e['x'], e['y'] - size * .35, q)
    if k == 'chip':
        size = e.get('size', 44); s = e['t']; wd = tw(s, size, 1) + 64; hh = size + 34
        bgc = COL.get(e.get('bg', 'gold'), GOLD) if e.get('bg') != 'o' else ORANGE
        inner = (f'<rect x="{f_(e["x"] - wd / 2 + 8)}" y="{f_(e["y"] - hh / 2 + 8)}" width="{f_(wd)}" height="{hh}" rx="6" fill="#000" opacity=".45"/>'
                 f'<rect x="{f_(e["x"] - wd / 2)}" y="{f_(e["y"] - hh / 2)}" width="{f_(wd)}" height="{hh}" rx="6" fill="{bgc}" stroke="{INK}" stroke-width="4"/>'
                 + text(e['x'], e['y'] + size * .36, s, size, '#1a1408', ls=1))
        return pop(inner, e['x'], e['y'], q)
    if k == 'board':
        wd = e.get('w', 1120); x0, y0 = e['x'] - wd / 2, e['y'] - 150; rows = e['rows']; o = []
        o.append(f'<rect x="{x0}" y="{y0}" width="{wd}" height="300" rx="12" fill="#1f1d18" stroke="{GOLD}" stroke-width="5"/>')
        o.append(text(x0 + 40, y0 + 72, rows[0][0], 40, GOLD, 'start'))
        for i, (_, sub, val) in enumerate(rows):
            yy = y0 + 150 + i * 96
            o.append(text(x0 + 40, yy, sub, 46, '#d8d2bf', 'start')); o.append(text(x0 + wd - 40, yy, f'{val} TRIỆU', 62, CREAM if i == 0 else RED, 'end'))
        try:
            dv = float(rows[0][2].replace(',', '.')) - float(rows[1][2].replace(',', '.'))
            ch = dict(k='chip', t=f'CHÊNH {dv:.1f} TRIỆU / LƯỢNG'.replace('.', ','), x=e['x'], y=y0 + 360, bg='o', size=46)
            o.append(el_svg(ch, tl, ta + .9, ctx))
        except Exception: pass
        return pop(''.join(o), e['x'], e['y'], q)
    if k == 'cards':
        it = e['items']; n = len(it); cw = e.get('cw', 340 if n <= 3 else 330); gap = e.get('gap', 46); tot = n * cw + (n - 1) * gap; x0 = (W - tot) / 2; o = []; kk = cw / 340
        for i, (a, b, c) in enumerate(it):
            ti = ta + (i * ctx['spread'] / n if e.get('at_each') else i * .12); qi = (tl - ti) / INTRO
            if qi <= 0: continue
            xx = x0 + i * (cw + gap); col = COL.get(c, CREAM)
            card = (f'<rect x="{f_(xx)}" y="{e["y"] - 130}" width="{cw}" height="250" rx="12" fill="#222" stroke="{col}" stroke-width="5"/>'
                    + text(xx + cw / 2, e['y'] - 60, a, fit(a, int(40 * max(kk, .8)), cw - 28), '#d8d2bf') + text(xx + cw / 2, e['y'] + 62, b, fit(b, int(82 * max(kk, .85)), cw - 30, 2), col))
            o.append(pop(card, xx + cw / 2, e['y'], qi))
        return ''.join(o)
    if k == 'grid':
        it = e['items']; cw, chh, gap = 540, 300, 44; o = []
        pos = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
        x0 = (W - 3 * cw - 2 * gap) / 2; y0 = 160
        sq = W <= H
        if sq: cw, chh, gap = 470, 236, 26; x0 = (W - 2 * cw - gap) / 2; rows = (len(it) + 1) // 2; y0 = max(150, 120 + (H - 120 - rows * (chh + gap)) / 2)
        for i, s in enumerate(it):
            ti = ta + (i * ctx['spread'] / len(it) if e.get('at_each') else i * .12); qi = (tl - ti) / INTRO
            gx, gy = pos[i]; xx = x0 + gx * (cw + gap) + (cw / 2 + gap / 2 if gy == 1 else 0); yy = y0 + gy * (chh + gap)
            if sq: xx = x0 + (i % 2) * (cw + gap) + ((cw + gap) / 2 if i == len(it) - 1 and len(it) % 2 else 0); yy = y0 + (i // 2) * (chh + gap)
            if qi <= 0:
                o.append(f'<rect x="{f_(xx)}" y="{yy}" width="{cw}" height="{chh}" rx="12" fill="#1d1d1d" stroke="#2d2d2d" stroke-width="4"/>'); continue
            lines = s.split('\n')
            cell = (f'<rect x="{f_(xx)}" y="{yy}" width="{cw}" height="{chh}" rx="12" fill="#252525" stroke="{GOLD if i == len(it) - 1 else "#8a8577"}" stroke-width="5"/>'
                    + text(xx + 36, yy + (70 if sq else 84), str(i + 1), 56 if sq else 66, BLUE, 'start')
                    + ''.join(text(xx + 36, yy + (140 if sq else 176) + j * (56 if sq else 70), ln, fit(ln, 46 if sq else 56, cw - 60), CREAM, 'start') for j, ln in enumerate(lines)))
            o.append(pop(cell, xx + cw / 2, yy + chh / 2, qi))
        return ''.join(o)
    if k == 'flow':
        it = e['items']; n = len(it); bw = e.get('bw', 430); gap = e.get('gap', 130); tot = n * bw + (n - 1) * gap; x0 = (W - tot) / 2; o = []; fs = int(50 * bw / 430)
        for i, s in enumerate(it):
            ti = ta + i * .55; qi = (tl - ti) / INTRO; xx = x0 + i * (bw + gap)
            if qi <= 0: continue
            col = RED if '↓' in s else CREAM
            box = (f'<rect x="{f_(xx)}" y="{e["y"] - 70}" width="{bw}" height="140" rx="10" fill="#222" stroke="{col}" stroke-width="5"/>' + text(xx + bw / 2, e['y'] + fs * .4, s, fs, col))
            if i: box += f'<path d="M{f_(xx - gap + 10)},{e["y"]} L{f_(xx - 10)},{e["y"]} M{f_(xx - 28)},{e["y"] - 16} L{f_(xx - 10)},{e["y"]} L{f_(xx - 28)},{e["y"] + 16}" stroke="{GOLD}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            o.append(pop(box, xx + bw / 2, e['y'], qi))
        return ''.join(o)
    if k == 'bars':
        it = e['items']; mx = max(v for _, v, _ in it); o = []; bw, gap, hmax = e.get('bw', 190), e.get('gap', 120), e.get('hmax', 460)
        for i, (lab, v, c) in enumerate(it):
            ti = ta + (i * ctx['spread'] / len(it) if e.get('at_each') else i * .3); qi = clamp((tl - ti) / .8)
            if qi <= 0: continue
            xx = e['x'] + i * (bw + gap); hh = hmax * v / mx * ease(qi); col = COL.get(c, CREAM)
            o.append(f'<rect x="{xx}" y="{f_(e["y"] - hh)}" width="{bw}" height="{f_(hh)}" fill="{col}" stroke="{INK}" stroke-width="5"/>')
            o.append(text(xx + bw / 2, e['y'] + 60, lab, 44, '#d8d2bf'))
            if qi > .6: o.append(text(xx + bw / 2, e['y'] - hh - 26, f'{v:.1f}'.replace('.', ','), 64, col))
        o.append(f'<path d="M{e["x"] - 40},{e["y"]} L{e["x"] + len(it) * (bw + gap)},{e["y"]}" stroke="#8a8577" stroke-width="4"/>')
        o.append(text(e['x'] - 40, e['y'] - hmax - 80, e.get('label') or ('CHÊNH LỆCH MUA–BÁN SJC (' + e.get('unit', '') + ')'), 34, '#a8a292', 'start'))
        return ''.join(o)
    if k == 'chart':
        ser = e['series']; n = len(ser); x0, y0, wd, hh = e['x'], e['y'], e['w'], e['h']; lo, hi = min(ser), max(ser); pad = (hi - lo) * .15
        lo -= pad; hi += pad
        pts = [(x0 + 70 + i * (wd - 140) / (n - 1), y0 + 40 + (hh - 110) * (1 - (v - lo) / (hi - lo))) for i, v in enumerate(ser)]
        qd = clamp((tl - ta) / 1.6); o = [f'<rect x="{x0}" y="{y0}" width="{wd}" height="{hh}" rx="12" fill="#1b1b1b" stroke="#3a3a3a" stroke-width="4" opacity="{ease(q):.2f}"/>']
        for gy in range(4):
            yy = y0 + 40 + gy * (hh - 110) / 3; o.append(f'<path d="M{x0 + 40},{f_(yy)} L{x0 + wd - 40},{f_(yy)}" stroke="#2c2c2c" stroke-width="3" stroke-dasharray="10 10"/>')
        for i, lab in enumerate(e.get('labels', [])):
            if lab: o.append(text(pts[i][0], y0 + hh - 22, lab, 32, '#a8a292'))
        m = max(1, int(qd * (n - 1) * 20)); path = []
        for j in range(m + 1):
            u = j / 20; i0 = min(n - 2, int(u)); fr = u - i0
            path.append((pts[i0][0] + (pts[i0 + 1][0] - pts[i0][0]) * fr, pts[i0][1] + (pts[i0 + 1][1] - pts[i0][1]) * fr))
        d = 'M' + ' L'.join(f'{f_(a)},{f_(b)}' for a, b in path)
        o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><path d="{d}" fill="none" stroke="{GOLD}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
        ex, ey = path[-1]; o.append(f'<circle cx="{f_(ex)}" cy="{f_(ey)}" r="13" fill="{RED if qd > .5 else GOLD}" stroke="{INK}" stroke-width="5"/>')
        o.append(text(pts[0][0] + 10, pts[0][1] - 30, f'{ser[0]:,.0f}'.replace(',', '.'), 44, CREAM, 'start'))
        if qd >= 1:
            o.append(text(pts[-1][0] - 10, pts[-1][1] + 70, f'{ser[-1]:,.0f}'.replace(',', '.'), 44, RED, 'end'))
            o.append(pop(el_svg(dict(k='chip', t=e.get('tag', ''), x=x0 + wd - 190, y=y0 + 95, bg='o', size=56), 1, 0, ctx), x0 + wd - 190, y0 + 95, clamp((tl - ta - 1.6) / INTRO)))
        o.append(text(x0 + 40, y0 - 22, e.get('head', 'VÀNG THẾ GIỚI') + ' · ' + e.get('unit', ''), 34, '#a8a292', 'start'))
        return ''.join(o)
    if k == 'cta':
        pg = ctx['page']; o = []; cx = e.get('x', 640); mw = e.get('maxw', 1050); y0 = e.get('y', 420)
        o.append(icon('bar', cx, y0, 190 * min(1, mw / 1050 + .2), INK, 6, GOLD))
        o.append(text(cx, y0 + 180, 'THEO DÕI', 64, '#d8d2bf'))
        size = 92
        while tw(pg, size, 2) > mw and size > 40: size -= 2
        o.append(text(cx, y0 + 300, pg, size, GOLD, ls=2))
        ss = 'Mỗi ngày hiểu thêm 1 điều về vàng'; s2 = 46
        while tw(ss, s2) > mw and s2 > 26: s2 -= 2
        o.append(text(cx, y0 + 380, ss, s2, CREAM, ls=0))
        dz = 30
        while tw('Thông tin tham khảo, không phải khuyến nghị đầu tư.', dz) > (mw if W <= H else W) and dz > 18: dz -= 1
        if W > H: o.append(text(W / 2, H - 40, 'Thông tin tham khảo, không phải khuyến nghị đầu tư.', dz, '#8f8a7c', ls=0))
        return pop(''.join(o), cx, y0 + 180, q)
    return ''


# ---------------- bo cuc tu dong cho khung vuong ----------------
WIDE = ('board', 'cards', 'bars', 'chart', 'flow')
HGT = {'title': 104, 'big': 124, 'line': 76, 'chip': 92, 'board': 430, 'cards': 270, 'bars': 470, 'chart': 520, 'flow': 160}


def autolayout(b):
    els = b['els']; ks = [e['k'] for e in els]
    if 'grid' in ks:
        for e in els:
            if e['k'] == 'man': e['_hide'] = True
        return
    hasman = 'man' in ks; wide = any(k in WIDE for k in ks)
    for e in els:
        if e['k'] == 'man':
            if wide: e['_hide'] = True
            else: e.update(x=870, y=1066, s=.70, face=-1)
    cx, mw = (320, 560) if (hasman and not wide) else (540, 980)
    if 'cta' in ks:
        for e in els:
            if e['k'] == 'cta': e.update(x=cx, maxw=min(mw, 540), y=330)
        return
    body = [e for e in els if e['k'] in HGT]
    top, bot, gap = 300, 1046, 26
    tot = sum(HGT[e['k']] for e in body) + gap * max(0, len(body) - 1)
    y = max(top, top + (bot - top - tot) / 2)
    for e in body:
        k = e['k']; h = HGT[k]
        if k in ('title', 'big', 'line'):
            e.update(x=cx, y=y + h * .74, maxw=mw, size={'title': 70, 'big': 88, 'line': 48}[k])
        elif k == 'chip':
            e.update(x=cx, y=y + h / 2, size=38)
            while tw(e['t'], e['size'], 1) + 64 > mw and e['size'] > 32: e['size'] -= 2  # 22/11: chip >= 32px
        elif k == 'board': e.update(x=540, y=y + 150, w=980)
        elif k == 'cards':
            n = len(e['items']); e.update(y=y + 130, cw=(300 if n <= 3 else 225), gap=(30 if n <= 3 else 20))
        elif k == 'bars':
            n = len(e['items']); e.update(bw=170, gap=110, hmax=290); e['x'] = 540 - (n * 280 - 110) / 2; e['y'] = y + 290 + 110
        elif k == 'chart': e.update(x=60, y=y + 50, w=960, h=460)
        elif k == 'flow': e.update(y=y + 75, bw=300, gap=50)
        y += h + gap


W87 = os.environ.get('AVF_TTS_URL', '')   # 27/11: repo cong khai -> cong W97 (X-AVF-Key), khong ghi dia chi trong code


def tts(sp):
    import urllib.request
    text_ = '\n\n'.join(b['say'].strip() for b in sp['beats'])
    body = json.dumps({'text': text_, 'speed': sp.get('speed', 1.05), 'tag': sp.get('tag', 'vtd')}).encode()
    for k in range(2):
        try:
            req = urllib.request.Request(W87, data=body, headers={'Content-Type': 'application/json', 'X-AVF-Key': os.environ.get('AVF_KEY', '')})
            with urllib.request.urlopen(req, timeout=1200) as r: j = json.loads(r.read())
            if j.get('ok'): return [[u, p] for u, p in zip(j['voice_urls'], j['pauses'])]
            print('W87 loi', str(j)[:300])
        except Exception as ex: print('W87 that bai', k, ex)
    sys.exit('khong co giong')


# ---------------- dong thoi gian ----------------
def at_time(b, a):
    """a = chi so cau (so thuc) -> giay trong beat."""
    ss = b['_sent']; i = min(int(a), len(ss) - 1); fr = a - int(a)
    return ss[i][0] + fr * (ss[i][1] - ss[i][0])


def plan(sp):
    beats = sp['beats']; trk = dict(v='', c='y', n=0)
    for b in beats:
        b['_trk0'] = dict(trk)
        if b.get('tracker'):
            nt = dict(trk); nt.update({k: v for k, v in b['tracker'].items() if k != 'at'}); b['_trk1'] = nt; b['_trk_at'] = at_time(b, b['tracker'].get('at', 0)) + .15; trk = nt
        else:
            b['_trk1'] = dict(trk); b['_trk_at'] = None
        for i, e in enumerate(b['els']):
            e['_ta'] = at_time(b, e['at']) if 'at' in e else i * .1
        b['_spread'] = max(1.0, min(2.4, b['_dur'] * .5))
        ev = sorted([e['_ta'] for e in b['els']] + ([b['_trk_at']] if b['_trk_at'] is not None else []))
        sub = []
        for e in b['els']:
            if e.get('at_each'):
                n = len(e['items']); sub += [e['_ta'] + i * b['_spread'] / n for i in range(n)]
            if e['k'] == 'chart': sub += [e['_ta'] + x * .1 for x in range(26)]
            if e['k'] == 'board': sub += [e['_ta'] + .9]
            if e['k'] == 'flow': sub += [e['_ta'] + i * .55 for i in range(len(e['items']))]
            if e['k'] == 'bars': sub += [e['_ta'] + i * b['_spread'] / len(e['items']) + x * .2 for i in range(len(e['items'])) for x in range(5)]
        b['_events'] = sorted(ev + sub)


def anim_active(b, tl):
    for t0 in b['_events']:
        if t0 - .02 <= tl <= t0 + INTRO + .05: return True
    if tl < .5: return True          # doi chuong / thanh tren
    return False


def settle(b, tl):
    """moc thoi gian tinh: moi chuyen dong da xong, trang thai giong tl."""
    done = [t0 for t0 in b['_events'] if t0 <= tl]
    return round(max([.5] + [t0 + INTRO + .06 for t0 in done]), 3)


def frame_svg(key):
    bi, tl, talk = key; sp = G['sp']; b = sp['beats'][bi]
    prev = sp['beats'][bi - 1] if bi else None
    chap_q = 1.0 if (prev and prev['chap'] == b['chap']) else clamp(tl / .45)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', background(b.get('theme', 'gold'))]
    ctx = dict(talk=talk, spread=b['_spread'], page=sp.get('page', ''))
    for e in b['els']:
        if e['k'] != 'man': o.append(el_svg(e, tl, e['_ta'], ctx))
    for e in b['els']:
        if e['k'] == 'man': o.append(el_svg(e, tl, e['_ta'], ctx))
    if not any(e['k'] in ('cta', 'grid') for e in b['els']):
        ta = b['_trk_at']; st = b['_trk1'] if (ta is not None and tl >= ta) else b['_trk0']
        pulse = (tl - ta) / .5 if (ta is not None and tl >= ta) else 1.0
        if st.get('v'): o.append(tracker_svg(st, pulse, sp.get('lessons', 5), sp['story']['who'], sp['story']['asset']))
    o.append(topbar(b['chap'], chap_q))
    o.append('</svg>')
    return ''.join(o)


def render(key):
    png = subprocess.run(['rsvg-convert', '-f', 'png', '-w', str(W), '-h', str(H)], input=frame_svg(key).encode(), capture_output=True, check=True).stdout
    from io import BytesIO
    return key, Image.open(BytesIO(png)).convert('RGB').tobytes()


def _init(g):
    global W, H
    G.update(g)
    if 'WH' in g: W, H = g['WH']


# ---------------- am thanh ----------------
TRIM = ('silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.04,areverse,'
        'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,areverse')


def get(url, path):
    import urllib.request
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f: f.write(r.read())
    return path


def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())


def sfx(kind, rnd):
    if kind == 'whoosh':
        n = int(SR * .4); t = np.arange(n) / SR; x = rnd.standard_normal(n); x = x - np.convolve(x, np.ones(30) / 30, 'same'); return x * np.sin(np.pi * t / .4) ** 2 * .22
    if kind == 'pop':
        n = int(SR * .12); t = np.arange(n) / SR; return np.sin(2 * np.pi * (520 + 900 * np.exp(-t / .02)) * t) * np.exp(-t / .035) * .22
    if kind == 'ding':
        n = int(SR * 1.0); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1318 * t) + .5 * np.sin(2 * np.pi * 1976 * t) + .25 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t / .28) * .2
    return np.zeros(10)


def bands_svg(sp):
    """khung doc 1080x1920: bang tren 420 (cau mo), giua de trong cho video vuong, bang duoi 420 (ten page)."""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">',
         '<rect width="1080" height="420" fill="#0b0b0b"/><rect y="1500" width="1080" height="420" fill="#0b0b0b"/>',
         f'<rect y="412" width="1080" height="8" fill="{GOLD}"/><rect y="1500" width="1080" height="8" fill="{GOLD}"/>']
    lab = sp.get('label') or (sp.get('page', '') + ' · GIẢI THÍCH VÀNG')
    o.append(text(540, 150, lab, fit(lab, 34, 980), '#bdb7a6', ls=2))
    hk = sp.get('hook') or ['', '']
    cols = [CREAM, RED]
    for i, ln in enumerate(hk[:2]):
        o.append(text(540, 250 + i * 98, ln, fit(ln, 84, 1000, 2), cols[i % 2], ls=2))
    pg = sp.get('page', '')
    o.append(icon('bar', 540, 1590, 80, INK, 5, GOLD))
    o.append(text(540, 1700, pg, fit(pg, 64, 1000, 2), GOLD, ls=2))
    # QC 23-24/11: footer ~1,5% khung, mien tru ~1% -> phong to cho doc duoc tren dien thoai
    o.append(text(540, 1768, 'Theo dõi để hiểu vàng mỗi ngày', 46, CREAM, ls=0))
    dz = fit('Thông tin tham khảo, không phải khuyến nghị đầu tư.', 38, 1000)
    o.append(text(540, 1846, 'Thông tin tham khảo, không phải khuyến nghị đầu tư.', dz, '#c9c2ae', ls=0))
    o.append('</svg>')
    return ''.join(o)


def reel_wrap(sp, sqf, D):
    bp = os.path.join(OUT, 'bands.png')
    open(bp, 'wb').write(subprocess.run(['rsvg-convert', '-f', 'png'], input=bands_svg(sp).encode(), capture_output=True, check=True).stdout)
    fc = (f'[1:v]format=rgba[b];[0:v]pad=1080:1920:0:420:color=black[p];[p][b]overlay=0:0[v1];'
          f'color=c=0x2a2a2a:s=1080x14:r=30[bgbar];color=c=0xf2c14e:s=1080x14:r=30[bar];'
          f'[v1][bgbar]overlay=0:1890:shortest=1[v2];[v2][bar]overlay=x=\'-1080+1080*t/{D:.2f}\':y=1890:shortest=1,format=yuv420p[v]')
    tmp = os.path.join(OUT, 'reel.tmp.mp4')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', sqf, '-loop', '1', '-i', bp, '-filter_complex', fc, '-map', '[v]', '-map', '0:a',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', '30', '-c:a', 'copy', '-t', f'{D:.2f}', '-movflags', '+faststart', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))


def main():
    sp = json.loads(os.environ['SPEC_JSON']) if 'SPEC_JSON' in os.environ else json.load(open(sys.argv[1], encoding='utf-8'))
    if sp.get('file'):   # spec dai (nhieu link giong) -> luu trong repo, chi gui duong dan
        sp = json.load(open(os.path.join(ROOT, sp['file']), encoding='utf-8'))
    global W, H
    if sp.get('fmt', 'sq') == 'sq': W, H = 1080, 1080
    G['WH'] = (W, H)
    beats = sp['beats']; sents = []
    if W == H:
        for b in beats: autolayout(b)
    if not sp.get('voice') and not os.environ.get('NOVOICE') and not os.environ.get('BOARD'): sp['voice'] = tts(sp)
    for bi, b in enumerate(beats):
        ss = [s for s in SPLIT.split(b['say'].strip()) if s.strip()]; b['_ns'] = len(ss); sents += [(bi, s) for s in ss]
    voice = sp.get('voice') or []
    parts = []; starts = []; acc = 0.0
    if voice:
        if len(voice) != len(sents): sys.exit(f'so cau giong {len(voice)} != so cau kich ban {len(sents)}')
        for i, (u, pz) in enumerate(voice):
            p = get(u, os.path.join(OUT, f's{i}.mp3')) if str(u).startswith('http') else u; wv = os.path.join(OUT, f's{i}.wav')
            last_in_beat = (i + 1 == len(sents)) or sents[i + 1][0] != sents[i][0]
            pad = max(0.0, float(pz if pz is not None else .45) - .1)
            if last_in_beat: pad = max(pad, .55)
            if i + 1 == len(sents): pad = 0.2
            subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', p, '-ar', str(SR), '-ac', '1', '-af', TRIM + ',apad=pad_dur=%.2f' % pad, wv])
            d = dur(wv); starts.append((acc, acc + d)); acc += d; parts.append(wv)
    else:   # ban xem truoc khong giong: uoc luong 0.36 s/tu
        for bi, s in sents:
            d = .36 * len(s.split()) + .5; starts.append((acc, acc + d)); acc += d
    # gan cau vao beat
    k = 0; t0 = 0.0
    for b in beats:
        ss = starts[k:k + b['_ns']]; b['_t0'] = ss[0][0]; b['_sent'] = [(a - b['_t0'], c - b['_t0']) for a, c in ss]; k += b['_ns']
    for i, b in enumerate(beats):
        b['_dur'] = (beats[i + 1]['_t0'] if i + 1 < len(beats) else acc + 2.6) - b['_t0']
    plan(sp); D = acc + 2.6
    # bao am giong -> khau hinh (mo/khep mieng)
    env = None
    if parts:
        lst = os.path.join(OUT, 'vl.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
        vw = os.path.join(OUT, 'voice.wav'); subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vw])
        with wave.open(vw) as w: a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        hop = SR // FPS; env = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2) + 1e-9) for i in range(len(a) // hop + 1)])
    nfr = int(D * FPS); keys = []
    for fi in range(nfr):
        t = fi / FPS; bi = max(i for i, b in enumerate(beats) if b['_t0'] <= t + 1e-6); b = beats[bi]; tl = t - b['_t0']
        has_man = any(e['k'] == 'man' for e in b['els'])
        talk = bool(has_man and env is not None and fi < len(env) and env[fi] > .035 and (fi // 3) % 2 == 0)
        if env is None and has_man: talk = (fi // 4) % 2 == 0 and tl < b['_sent'][-1][1]
        tk = round(tl, 3) if anim_active(b, tl) else settle(b, tl)
        keys.append((bi, tk, talk))
    if os.environ.get('BOARD'):
        g = dict(sp=sp, WH=(W, H)); _init(g); idx = [int((b['_t0'] + b['_dur'] * .8) * FPS) for b in beats]
        for n_, fi in enumerate(idx):
            k_, raw = render(keys[min(fi, nfr - 1)]); Image.frombytes('RGB', (W, H), raw).save(os.path.join(OUT, f'board_{n_:02d}.png'))
        print('board', len(idx)); return
    uniq = list(dict.fromkeys(keys)); print('khung', nfr, 'khac nhau', len(uniq), 'dai', round(D, 1), flush=True)
    cache = {}
    raw_mp4 = os.path.join(OUT, 'v_tmp.mp4')
    pr = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-framerate', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', raw_mp4], stdin=subprocess.PIPE)
    # render theo lo de giu RAM thap: moi lo 300 khung
    with Pool(int(os.environ.get('NPROC', '4')), initializer=_init, initargs=(dict(sp=sp, WH=(W, H)),)) as pool:
        pos = 0
        while pos < nfr:
            chunk = keys[pos:pos + 300]; need = [k_ for k_ in dict.fromkeys(chunk) if k_ not in cache]
            for k_, raw in pool.imap(render, need, chunksize=4): cache[k_] = raw
            for k_ in chunk: pr.stdin.write(cache[k_])
            keep = set(keys[pos + 300:pos + 900]); cache = {k_: v for k_, v in cache.items() if k_ in keep}
            pos += 300
    pr.stdin.close(); pr.wait()
    if pr.returncode: sys.exit('ffmpeg loi')
    # sfx
    rnd = np.random.default_rng(3); n = int(SR * D) + SR; mix = np.zeros(n)
    def add(t, kind, v=1.0):
        y = sfx(kind, rnd) * v; i = int(t * SR); m = min(len(y), n - i)
        if m > 0: mix[i:i + m] += y[:m]
    for i, b in enumerate(beats):
        if i: add(b['_t0'], 'whoosh', .9 if b['chap'] != beats[i - 1]['chap'] else .5)
        for e in b['els']:
            if e['k'] in ('chip', 'big') and e['_ta'] > .2: add(b['_t0'] + e['_ta'], 'pop', .8)
        if b['_trk_at'] is not None: add(b['_t0'] + b['_trk_at'], 'ding', .9)
    sw = os.path.join(OUT, 'sfx.wav')
    with wave.open(sw, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767 * .9).astype(np.int16).tobytes())
    mus = os.path.join(ROOT, 'editor', 'story', sp.get('music', 'music_a.mp3')); tmp = os.path.join(OUT, 'out.tmp.mp4')
    if parts:
        fc = '[1:a]aresample=44100[v];[2:a]volume=0.7[s];[3:a]volume=0.05,afade=t=out:st=%.2f:d=2[m];[v][s][m]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5[a]' % max(0, D - 2)
        ins = ['-i', os.path.join(OUT, 'voice.wav'), '-i', sw, '-stream_loop', '-1', '-i', mus]
    else:
        fc = '[1:a]volume=0.7[s];[2:a]volume=0.08[m];[s][m]amix=inputs=2:duration=first:normalize=0[a]'; ins = ['-i', sw, '-stream_loop', '-1', '-i', mus]
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw_mp4] + ins + ['-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    if sp.get('out', 'reel') == 'reel' and W == H:
        sqf = os.path.join(OUT, 'sq.mp4'); os.replace(tmp, sqf); reel_wrap(sp, sqf, D)
    else:
        os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    json.dump({'beats': [dict(chap=b['chap'], t0=round(b['_t0'], 2)) for b in beats], 'dur': round(D, 2)}, open(os.path.join(OUT, 'timing.json'), 'w'), ensure_ascii=False)
    print('ok', round(D, 2))


if __name__ == '__main__':
    main()
