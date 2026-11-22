"""Bo canh VAN HOC (lang que Bac Bo 1930s, gia dinh, so do quan he) cho may dung ksc_svg.
Dung: spec {"engine": "vh", ...}; ksc_svg.main() goi install(module) de thay beat()/SFX_PLAN/GROUND.
Nhan vat: ksc_chars (chipheo, chitre, bakien, baba, dan1, dan2, nongdan, bamu, phocoi, linhle, namcao, nguoike).
Moi canh: beat(sh, t, d) -> (svg_the_gioi, (zoom, cx, cy), shake, flash). Toa do the gioi: mat dat y~1250, khung nhin quanh (540, 830).
"""
import math
import random

import ksc_chars as CH

FONT = 'Be Vietnam Pro, Inter'
INK = '#111'
GY = 1250   # mat dat


def f_(v): return f'{v:.1f}'
def osc(t, f, ph=0.0): return math.sin(2 * math.pi * (f * t + ph))
def lerp(a, b, q): return a + (b - a) * q
def ease(q): q = max(0.0, min(1.0, q)); return q * q * (3 - 2 * q)
def back_ease(q): q = max(0.0, min(1.0, q)); c = 1.70158; return 1 + (c + 1) * (q - 1) ** 3 + c * (q - 1) ** 2
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def hold2(t, seed=0): return random.Random(int(t * 15) * 31 + seed)


SCALE = .8   # 22/11: nhan vat dang qua to


def ch(name, x, y, D, facing=1, expr='normal', hands=None, **kw):
    g, tips = CH.character(name, x, y, D * SCALE, facing, expr, hands, **kw); return g


def at(sh, i, default):
    """moc giay (trong canh) khi cau thu i bat dau doc; chua co moc thi dung default. Hanh dong phai khop LOI, khong chay truoc."""
    se = sh.get('_sent') or []
    if i < 0: i = len(se) + i
    return se[i] if 0 <= i < len(se) else default


# ---------------- nen ----------------
def sky(top, bot, night=False):
    s = (f'<defs><linearGradient id="vsk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient></defs>'
         f'<rect x="-900" y="-500" width="2880" height="2900" fill="url(#vsk)"/>')
    if night:
        r = random.Random(4)
        s += ''.join(f'<circle cx="{r.randint(-600, 1700)}" cy="{r.randint(-300, 700)}" r="{r.choice((2, 3, 4))}" fill="#fff" opacity=".7"/>' for _ in range(40))
        s += f'<circle cx="880" cy="180" r="70" fill="#f6efcf" stroke="{INK}" stroke-width="6"/>'
    return s


def hills(y, col='#7d9a6c', col2='#62805a'):
    return (f'<path d="M-900,{y} Q-500,{y - 160} -150,{y - 40} T600,{y - 60} T1400,{y - 30} T2000,{y} L2000,{y + 600} L-900,{y + 600} Z" fill="{col2}" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M-900,{y + 50} Q-300,{y - 60} 200,{y + 30} T1100,{y + 10} T2000,{y + 40} L2000,{y + 600} L-900,{y + 600} Z" fill="{col}" stroke="{INK}" stroke-width="6"/>')


def bamboo(x, y, s=1.0, t=0.0, col='#4f8a3a'):
    sw = osc(t, .25, x * .001) * 6 * s; o = []
    for k, dx in enumerate((-40, 0, 38)):
        h = (420 + k * 60) * s
        o.append(f'<path d="M{f_(x + dx * s)},{f_(y)} Q{f_(x + dx * s + sw)},{f_(y - h * .5)} {f_(x + dx * s * 1.6 + sw * 2)},{f_(y - h)}" stroke="{INK}" stroke-width="{f_(16 * s)}" fill="none"/>'
                 f'<path d="M{f_(x + dx * s)},{f_(y)} Q{f_(x + dx * s + sw)},{f_(y - h * .5)} {f_(x + dx * s * 1.6 + sw * 2)},{f_(y - h)}" stroke="#9cb85a" stroke-width="{f_(9 * s)}" fill="none"/>')
    for k in range(7):
        a = k / 6.0; cx = x + (-90 + 180 * a) * s + sw * 2; cy = y - (380 + 120 * math.sin(a * math.pi)) * s
        o.append(f'<ellipse cx="{f_(cx)}" cy="{f_(cy)}" rx="{f_(70 * s)}" ry="{f_(46 * s)}" fill="{col}" stroke="{INK}" stroke-width="{f_(5 * s)}"/>')
    return ''.join(o)


def house(x, y, w=360, h=200, wall='#e8d8b0', roof='#a07a44', door=True, shut=False):
    rp = f'M{f_(x - w * .62)},{f_(y - h)} L{f_(x)},{f_(y - h - h * .9)} L{f_(x + w * .62)},{f_(y - h)} Z'
    o = [f'<rect x="{f_(x - w / 2)}" y="{f_(y - h)}" width="{f_(w)}" height="{f_(h)}" fill="{wall}" stroke="{INK}" stroke-width="7"/>',
         f'<path d="{rp}" fill="{roof}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>']
    for k in range(5): o.append(f'<path d="M{f_(x - w * .55 + k * w * .27)},{f_(y - h)} l{f_(w * .12)},{f_(-h * .5)}" stroke="#7a5a2e" stroke-width="5"/>')
    if door:
        o.append(f'<rect x="{f_(x - 45)}" y="{f_(y - 130)}" width="90" height="130" fill="{"#6b4524" if shut else "#2a1a10"}" stroke="{INK}" stroke-width="6"/>')
        if shut: o.append(f'<line x1="{f_(x)}" y1="{f_(y - 130)}" x2="{f_(x)}" y2="{f_(y)}" stroke="{INK}" stroke-width="5"/>')
    return ''.join(o)


def fence(x0, x1, y, col='#b8945a'):
    o = [f'<rect x="{x0}" y="{y - 70}" width="{x1 - x0}" height="14" fill="{col}" stroke="{INK}" stroke-width="4"/>']
    for x in range(int(x0), int(x1), 46):
        o.append(f'<path d="M{x},{y} L{x},{y - 110} L{x + 14},{y - 126} L{x + 28},{y - 110} L{x + 28},{y} Z" fill="{col}" stroke="{INK}" stroke-width="5"/>')
    return ''.join(o)


def road(y=GY, col='#c9a46a'):
    return (f'<rect x="-900" y="{y - 40}" width="2880" height="1200" fill="#7fa257" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M-900,{y - 20} L1980,{y - 20} L1980,{y + 170} L-900,{y + 170} Z" fill="{col}" stroke="{INK}" stroke-width="6"/>')


def village(t, night=False, dusk=False, shut=False):
    if night: s = [sky('#0e1630', '#2a3458', True)]
    elif dusk: s = [sky('#e98a52', '#f6d49a')]
    else: s = [sky('#8ec0e0', '#e8f2f4')]
    s.append(hills(860, '#5e7a5a' if night else '#7d9a6c', '#46604a' if night else '#62805a'))
    for x in (-420, 1280): s.append(bamboo(x, GY - 60, 1.0, t))
    s.append(house(120, GY - 40, shut=shut)); s.append(house(960, GY - 60, 380, 220, shut=shut))
    s.append(road(GY, '#8a7450' if night else '#c9a46a'))
    s.append(fence(-200, 330, GY - 20)); s.append(fence(760, 1300, GY - 20))
    if night: s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#0a1030" opacity=".35"/>')
    return ''.join(s)


def kiln(x, y, s=1.0):
    o = [f'<path d="M{f_(x - 230 * s)},{f_(y)} L{f_(x - 170 * s)},{f_(y - 330 * s)} Q{f_(x)},{f_(y - 420 * s)} {f_(x + 170 * s)},{f_(y - 330 * s)} L{f_(x + 230 * s)},{f_(y)} Z" fill="#a8563a" stroke="{INK}" stroke-width="{f_(8 * s)}"/>',
         f'<path d="M{f_(x - 80 * s)},{f_(y)} L{f_(x - 80 * s)},{f_(y - 120 * s)} Q{f_(x)},{f_(y - 190 * s)} {f_(x + 80 * s)},{f_(y - 120 * s)} L{f_(x + 80 * s)},{f_(y)} Z" fill="#2a160e" stroke="{INK}" stroke-width="{f_(6 * s)}"/>']
    for r_ in range(5):
        yy = y - (60 + r_ * 55) * s
        for c_ in range(-3, 4):
            xx = x + c_ * 60 * s + (r_ % 2) * 30 * s
            if abs(xx - x) < (220 - r_ * 25) * s and not (abs(xx - x) < 90 * s and yy > y - 170 * s):
                o.append(f'<rect x="{f_(xx - 26 * s)}" y="{f_(yy - 22 * s)}" width="{f_(52 * s)}" height="{f_(22 * s)}" fill="none" stroke="#6e2e1c" stroke-width="{f_(3 * s)}"/>')
    for k in range(6):   # co dai
        gx = x - 260 * s + k * 100 * s
        o.append(f'<path d="M{f_(gx)},{f_(y)} q{f_(10 * s)},{f_(-60 * s)} {f_(30 * s)},{f_(-80 * s)} M{f_(gx + 20 * s)},{f_(y)} q{f_(-5 * s)},{f_(-50 * s)} {f_(-25 * s)},{f_(-70 * s)}" stroke="#3e6a2c" stroke-width="{f_(7 * s)}" fill="none"/>')
    return ''.join(o)


def bottle(x, y, s=1.0, ang=0):
    return (f'<g transform="rotate({ang} {f_(x)} {f_(y)})"><path d="M{f_(x - 20 * s)},{f_(y)} L{f_(x - 20 * s)},{f_(y - 60 * s)} Q{f_(x - 20 * s)},{f_(y - 80 * s)} {f_(x - 8 * s)},{f_(y - 90 * s)} L{f_(x - 8 * s)},{f_(y - 115 * s)} L{f_(x + 8 * s)},{f_(y - 115 * s)} L{f_(x + 8 * s)},{f_(y - 90 * s)} Q{f_(x + 20 * s)},{f_(y - 80 * s)} {f_(x + 20 * s)},{f_(y - 60 * s)} L{f_(x + 20 * s)},{f_(y)} Z" fill="#cfe6e0" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
            f'<rect x="{f_(x - 18 * s)}" y="{f_(y - 40 * s)}" width="{f_(36 * s)}" height="{f_(38 * s)}" fill="#e8d8a0" opacity=".8"/></g>')


def waves(x, y, t, n=3, col='#ffd400', back=False):
    o = []
    for k in range(n):
        q = ((t * .9 + k / n) % 1.0); r = 60 + q * 380 if not back else 440 - q * 380
        o.append(f'<path d="M{f_(x + r * .5)},{f_(y - r * .6)} A{f_(r)},{f_(r)} 0 0 1 {f_(x + r * .5)},{f_(y + r * .6)}" stroke="{col}" stroke-width="12" fill="none" opacity="{f_(1 - q)}" stroke-linecap="round"/>')
    return ''.join(o)


def bigq(x, y, t, col='#c4281f'):
    q = back_ease(min(1, t / .4))
    return f'<text x="{f_(x)}" y="{f_(y)}" font-family="{FONT}" font-weight="800" font-size="{f_(240 * q)}" fill="{col}" stroke="{INK}" stroke-width="8" paint-order="stroke" text-anchor="middle">?</text>'


def card(x, y, w, h, title, sub='', col='#f4ecd6', rot=0.0, tc='#111'):
    return (f'<g transform="rotate({f_(rot)} {f_(x)} {f_(y)})"><rect x="{f_(x - w / 2)}" y="{f_(y - h / 2)}" width="{f_(w)}" height="{f_(h)}" rx="14" fill="{col}" stroke="{INK}" stroke-width="8"/>'
            f'<text x="{f_(x)}" y="{f_(y - h / 2 + 70)}" font-family="{FONT}" font-weight="800" font-size="40" fill="{tc}" text-anchor="middle">{esc(title)}</text>'
            + (f'<text x="{f_(x)}" y="{f_(y - h / 2 + 118)}" font-family="{FONT}" font-weight="600" font-size="30" fill="{tc}" text-anchor="middle">{esc(sub)}</text>' if sub else '') + '</g>')


def star(x, y, r, rot=0.0):
    pts = []
    for k in range(10):
        a = math.radians(rot + k * 36); rr = r if k % 2 == 0 else r * .45
        pts.append(f'{f_(x + rr * math.cos(a))},{f_(y + rr * math.sin(a))}')
    return f'<polygon points="{" ".join(pts)}" fill="#ffd400" stroke="{INK}" stroke-width="6"/>'


def walk(t, speed=1.0):   # nhun 2 nhip / chu ky 20 khung (skill)
    ph = (t * 1.5 * speed) % 1.0
    return abs(math.sin(ph * 2 * math.pi)) * 14


# ---------------- canh ----------------
def beat(sh, t, d):
    ty = sh['type']; s = []; cam = (1.0, 540, 830); shake = 0.0; flash = 0.0
    if ty == 'chui_road':       # Chi Pheo vua di vua chui, dan lang nup sau rao
        s.append(village(t, dusk=True))
        for k, (nm, x) in enumerate([('dan1', 40), ('dan2', 900), ('dan1', 1060)]):
            peek = ease(min(1, (t - .4 - k * .5) / .4)) * (1 - ease((t - d + .8) / .4))
            s.append(ch(nm, x, GY - 20 + (1 - peek) * 90, 92, 1 if x < 540 else -1, 'scared', tag=False, t=t, hidden_below=GY - 90))
        x = lerp(-120, 640, ease(t / max(1, d))); bob = walk(t)
        sway = osc(t, .7) * 7
        s.append(ch('chipheo', x, GY + 60 - bob, 190, 1, 'angry', [(.7, -.35 + .1 * osc(t, 1.1), None)], lean=sway, t=t, tag=t > 1.0))
        s.append(bottle(x - 150, GY - 70 - bob, 1.1, -25 + sway))
        if int(t * 2) % 2 == 0: s.append(waves(x + 120, GY - 330, t))
        cam = (lerp(1.12, 1.0, ease(t / 1.2)), x + 60, 880)
    elif ty == 'chui_steps':    # so do leo thang: troi -> doi -> ca lang
        s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#f2ead6"/>')
        steps = [('TRỜI', '#8ec0e0', 'Trời có của riêng ai'), ('ĐỜI', '#e9b25a', 'Đời là tất cả'), ('CẢ LÀNG', '#c4281f', 'Làng Vũ Đại')]
        for k, (tt, col, sub) in enumerate(steps):
            t0 = at(sh, (1, 3, 5)[k], .3 + k * d * .25); q = back_ease(min(1, (t - t0) / .35)); x = 260 + k * 280; y = 1180 - k * 190
            if q > 0:
                s.append(f'<g transform="translate({x} {y}) scale({f_(q)}) translate({-x} {-y})">{card(x, y, 250, 170, tt, "", col, 0, "#fff" if k == 2 else "#111")}</g>')
                if k: s.append(f'<path d="M{x - 200},{y + 150} Q{x - 140},{y + 40} {x - 120},{y + 70}" stroke="{INK}" stroke-width="10" fill="none" marker-end=""/><polygon points="{x - 128},{y + 40} {x - 100},{y + 86} {x - 150},{y + 84}" fill="{INK}"/>')
        s.append(ch('chipheo', 200, 1450, 150, 1, 'angry', [(.75, -.45, None)], t=t, tag=False))
        cam = (1.0, 540, 1000)
    elif ty == 'ke':            # nguoi ke noi voi nguoi xem (canh co dinh cua kenh)
        s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#efe7d2"/>')
        s.append(f'<rect x="-900" y="{GY}" width="2880" height="900" fill="#d8c9a4" stroke="{INK}" stroke-width="6"/>')
        s.append(f'<rect x="80" y="660" width="560" height="380" rx="16" fill="#2f4a3a" stroke="#6b4a2a" stroke-width="16"/>')
        txt = sh.get('board', '')
        if txt:
            for j, ln in enumerate(txt.split('|')): s.append(f'<text x="360" y="{780 + j * 80}" font-family="{FONT}" font-weight="700" font-size="56" fill="#f4f0e0" text-anchor="middle">{esc(ln)}</text>')
        nod = (int(t * 30 / 3) % 4 in (1, 2)) * 3; bob = abs(osc(t, 1.6)) * 10
        s.append(ch('nguoike', 800, GY - bob, 175, -1, sh.get('expr', 'happy'), [(.85, .05 * abs(osc(t, .9)), 'board', 200 + 12 * osc(t, .9)), (-.55, .05)], head_rot=nod, t=t))
        if sh.get('ask'):
            s.append(bigq(360, 1150, t)); cam = (lerp(1.0, 1.12, ease(t / max(.5, d))), 560, 900)
        else: cam = (1.0, 540, 900)
    elif ty == 'writer':        # Nam Cao viet duoi den dau
        s.append(sky('#1e1a2a', '#3a2e3e'))
        s.append(f'<rect x="-900" y="1120" width="2880" height="1000" fill="#5a3a22" stroke="{INK}" stroke-width="7"/>')
        fl = 1 + .06 * hold2(t, 2).uniform(-1, 1)
        s.append(f'<circle cx="760" cy="880" r="{f_(420 * fl)}" fill="#ffd98a" opacity=".22"/>')
        s.append(f'<rect x="720" y="930" width="80" height="190" rx="10" fill="#b8963e" stroke="{INK}" stroke-width="6"/><ellipse cx="760" cy="{f_(905 - 10 * fl)}" rx="22" ry="{f_(42 * fl)}" fill="#ffb03a" stroke="{INK}" stroke-width="4"/>')
        for k in range(4): s.append(f'<rect x="{180 + k * 14}" y="{1080 - k * 12}" width="300" height="40" fill="#f4ecd6" stroke="{INK}" stroke-width="4"/>')
        wr = osc(t, 3) * 6
        s.append(ch('namcao', 420, 1120, 170, 1, 'normal', [(.7, .25 + wr * .01, 'board', 35)], head_rot=-6, t=t))
        cam = (lerp(1.0, 1.1, ease(t / d)), 560, 900)
    elif ty == 'book_swap':     # nha xuat ban doi ten sach
        s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#e9dcc0"/>')
        t1 = at(sh, 1, d * .4); sw = ease((t - t1) / .5)
        s.append(card(lerp(320, 250, sw), 1000, 340, 470, 'CÁI LÒ', 'GẠCH CŨ', '#a8563a', lerp(0, -12, sw), '#fff'))
        if sw > 0:
            q = back_ease(min(1, (t - t1) / .4))
            s.append(f'<g transform="translate(800 1000) scale({f_(q)}) translate(-800 -1000)">{card(800, 1000, 340, 470, "ĐÔI LỨA", "XỨNG ĐÔI", "#e8607a", 8, "#fff")}<text x="800" y="1180" font-size="120" text-anchor="middle">❤</text></g>')
            if t - t1 < .2: flash = .4
        s.append(ch('namcao', 560, 1420, 150, 1, 'sad' if sw > .5 else 'surprised', [(.2, -1.05, None)], t=t))
        cam = (1.0, 540, 1000)
    elif ty == 'kiln':          # cai lo gach bo hoang luc hoang hon
        s.append(sky('#c86a42', '#f2c27a')); s.append(hills(900, '#8a8a5a', '#6e6e46'))
        s.append(f'<rect x="-900" y="1180" width="2880" height="1000" fill="#7a8a4a" stroke="{INK}" stroke-width="6"/>')
        s.append(kiln(560, 1200, 1.4))
        for k in range(3):
            bx = (k * 420 + t * 60) % 1700 - 300
            s.append(f'<path d="M{f_(bx)},{f_(300 + k * 60)} q20,-18 40,0 q20,-18 40,0" stroke="{INK}" stroke-width="5" fill="none"/>')
        cam = (lerp(1.0, 1.15, ease(t / d)), 560, lerp(860, 900, ease(t / d)))
    elif ty == 'found_baby':    # anh tha ong luon thay dua be canh lo
        s.append(sky('#b8c8d0', '#eef0e6'))
        s.append(f'<rect x="-900" y="1180" width="2880" height="1000" fill="#7a8a4a" stroke="{INK}" stroke-width="6"/>')
        s.append(kiln(300, 1200, 1.1))
        wig = osc(t, 2.2) * 4
        s.append(f'<ellipse cx="{f_(560 + wig)}" cy="1170" rx="70" ry="38" fill="#c8b48a" stroke="{INK}" stroke-width="6"/><circle cx="{f_(612 + wig)}" cy="1150" r="30" fill="#f0c49c" stroke="{INK}" stroke-width="6"/>')
        tb = at(sh, 1, 1.4); x = lerp(1250, 860, ease(t / max(.6, tb))); stop = t > tb
        s.append(ch('nongdan', x, GY + 20 - (0 if stop else walk(t)), 170, -1, 'surprised' if stop else 'normal', [(.6, .1, 'oar', 70)], t=t, tag=stop))
        for k in range(3): s.append(f'<ellipse cx="{f_(x + 60 + k * 30)}" cy="{GY - 10}" rx="16" ry="42" fill="#9a7a44" stroke="{INK}" stroke-width="5"/>')
        if stop and t < tb + .4: shake = 6
        cam = (1.08, 640, 900)
    elif ty == 'passed':        # dua be bi chuyen tay
        s.append(village(t))
        who = ['bamu', 'phocoi', 'dan1', 'dan2']; seg = max(.8, d / len(who)); k = min(len(who) - 1, int(t / seg)); q = (t - k * seg) / seg
        for j, nm in enumerate(who):
            x = 160 + j * 260 - k * 260 + (1 - ease(q * 3)) * 260 * (k > 0)
            if -200 < x < 1300: s.append(ch(nm, x, GY + 40, 130, 1, 'sad' if nm == 'bamu' else 'normal', [(.7, -.1, None)], t=t, tag=(j == k)))
        boy = min(1.0, .4 + t / d * .6)
        bx = 160 + 260 * .55 + 30; s.append(ch('chitre', bx, GY + 40, 130 * boy, 1, 'sad', t=t, tag=False))
        cam = (1.0, 560, 900)
    elif ty == 'farmhand':      # anh canh dien hien lanh lam ruong nha ly Kien
        s.append(sky('#8ec0e0', '#e8f2f4')); s.append(hills(880))
        s.append(f'<rect x="-900" y="1100" width="2880" height="1100" fill="#6aa0b8" stroke="{INK}" stroke-width="6"/>')
        for r_ in range(6):
            for c_ in range(12):
                x = -500 + c_ * 180 + (r_ % 2) * 90; y = 1130 + r_ * 70
                s.append(f'<path d="M{x},{y} l-10,-34 M{x},{y} l0,-40 M{x},{y} l10,-34" stroke="#3e7a2c" stroke-width="6"/>')
        s.append(house(1050, 1080, 420, 240, '#efe2c0', '#8a3a2a'))
        q = (t * .9) % 1.0; a = lerp(-110, 20, ease(q / .5)) if q < .5 else lerp(20, -110, (q - .5) / .5)
        s.append(ch('chitre', 520, 1230, 190, 1, 'happy', [(.85, -.45 if q < .5 else -.1, 'shovel', a)], t=t))
        cam = (1.0, 560, 900)
    elif ty == 'jealous':       # ba Ba goi len, ong Ly ghen sau binh phong
        s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#6b3a22"/>')
        s.append(f'<rect x="-900" y="{GY}" width="2880" height="900" fill="#8a5a34" stroke="{INK}" stroke-width="6"/>')
        for k in range(6): s.append(f'<rect x="{-500 + k * 300}" y="300" width="60" height="{GY - 300}" fill="#4a2a16" stroke="{INK}" stroke-width="6"/>')
        s.append(f'<rect x="760" y="700" width="420" height="{GY - 700}" fill="#b8863e" stroke="{INK}" stroke-width="8"/>')
        for k in range(3): s.append(f'<rect x="{790 + k * 130}" y="730" width="110" height="{GY - 760}" fill="#d4a85a" stroke="{INK}" stroke-width="5"/>')
        s.append(ch('baba', 200, GY + 20, 160, 1, 'happy', [(.8, -.2, None)], t=t))
        s.append(ch('chitre', 520, GY + 30, 170, -1, 'scared', [(.4, .1, None)], t=t, tag=False))
        peek = ease((t - at(sh, 2, d * .35)) / .5)
        if peek > 0:
            s.append(ch('bakien', lerp(1100, 980, peek), GY + 20, 190, -1, 'angry', t=t, tag=peek > .8))
        cam = (1.0, 560, 900)
    elif ty == 'arrest':        # linh le giai di
        s.append(village(t))
        t0 = at(sh, 3, .6); x = lerp(380, 1250, ease((t - t0) / max(.8, d - t0))); bob = walk(t) if t > t0 else 0
        s.append(ch('bakien', 120, GY + 40, 190, 1, 'normal', t=t, tag=t < d * .6))
        s.append(ch('linhle', x - 210, GY + 50 - bob, 160, 1, 'angry', [(.6, -.1, 'spear', -60)], t=t, tag=False))
        s.append(ch('chitre', x, GY + 50 - bob, 165, 1, 'scared', [(-.3, .1, None)], t=t, tag=False))
        s.append(ch('linhle', x + 210, GY + 50 - bob, 160, 1, 'normal', [(.6, -.1, 'spear', -60)], t=t))
        cam = (1.0, lerp(540, 680, ease(t / d)), 880)
    elif ty == 'return':        # nguoi la tro ve: dau troc, rang cao trang, ngu xam
        s.append(village(t, dusk=True))
        ta = at(sh, 1, 1.2); x = lerp(1300, 620, ease(t / max(.6, ta))); arr = t > ta
        for k, (nm, xx) in enumerate([('dan1', 150), ('dan2', 330)]):
            jump = back_ease(min(1, (t - ta) / .3)) if arr else 0
            s.append(ch(nm, xx - 60 * jump, GY + 40 - 40 * max(0, 1 - abs((t - ta - .15) / .15)), 130, 1, 'surprised' if arr else 'normal', t=t, tag=False))
        s.append(ch('chipheo', x, GY + 60 - (0 if arr else walk(t)), 220, -1, 'normal', [(.5, .2, None)], t=t, tag=arr))
        if arr and t < ta + .25: flash = .45; shake = 10; s.append(star(x - 150, GY - 380, 60, t * 300))
        cam = (lerp(1.0, 1.15, ease((t - ta) / .6)), lerp(700, 560, ease(t / (ta + .2))), 820)
    elif ty == 'drunk':         # quan ruou, dan lang tranh xa
        s.append(village(t, dusk=True))
        s.append(f'<rect x="380" y="1060" width="420" height="180" fill="#8a5a34" stroke="{INK}" stroke-width="7"/><path d="M340,1060 L840,1060 L780,960 L400,960 Z" fill="#c9a46a" stroke="{INK}" stroke-width="7"/>')
        for k in range(5): s.append(bottle(420 + k * 80, 1060, .8, (k - 2) * 8))
        sway = osc(t, .6) * 9
        s.append(ch('chipheo', 600, GY + 60, 200, 1, 'sad' if int(t) % 3 == 2 else 'angry', [(.6, -.3, None)], lean=sway, t=t))
        s.append(bottle(700, GY - 120, 1.0, 40 + sway))
        for k, (nm, xx) in enumerate([('dan1', 60), ('dan2', 1080)]):
            s.append(ch(nm, xx + (k * 2 - 1) * t * 40, GY + 40, 110, -1 if k == 0 else 1, 'scared', t=t, tag=False))
        cam = (1.05, 600, 880)
    elif ty == 'alone':         # bat nghi: duong lang vang, cua dong, dau hoi
        s.append(village(t, dusk=True, shut=True))
        s.append(ch('chipheo', 560, GY + 60, 180, 1, 'sad', t=t, tag=False))
        tq = at(sh, -1, 0.0)
        if t >= tq: s.append(bigq(820, 900, t - tq))
        cam = (lerp(1.0, 1.18, ease(t / max(.5, d))), 600, 900)
    elif ty == 'echo':          # tieng chui di ra, khong co tieng nao quay ve
        s.append(sky('#2a3458', '#5a5a7a')); s.append(hills(900, '#4e6250', '#3a4e3e'))
        s.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#5a6a46" stroke="{INK}" stroke-width="6"/>')
        s.append(ch('chipheo', 320, GY + 40, 200, 1, 'sad', [(.6, -.4, None)], t=t, tag=False))
        s.append(waves(470, GY - 340, t, 4, '#ffd400'))
        for k in range(3):   # o tim tieng dap: rong
            x = 900 + k * 120; q = ((t * .6 + k * .3) % 1.0)
            s.append(f'<circle cx="{x}" cy="{GY - 380 - k * 60}" r="{f_(30 + 10 * q)}" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="10 10" opacity="{f_(.6 - .5 * q)}"/>')
        cam = (1.0, 560, 880)
    elif ty == 'silence':       # ca lang im, mat nhin qua khe cua
        s.append(village(t, night=True, shut=True))
        for k, (x, y) in enumerate([(120, 1090), (960, 1070), (1180, 1150), (-80, 1150)]):
            bl = 0 if (int(t * 30) + k * 7) % 70 < 4 else 1
            s.append(f'<ellipse cx="{x - 14}" cy="{y}" rx="9" ry="{f_(9 * bl + 1)}" fill="#ffe98a"/><ellipse cx="{x + 14}" cy="{y}" rx="9" ry="{f_(9 * bl + 1)}" fill="#ffe98a"/>')
        s.append(ch('chipheo', lerp(560, 600, t / d), GY + 60, 110, 1, 'sad', t=t, tag=False))
        cam = (lerp(1.1, 1.0, ease(t / d)), 560, 860)
    elif ty == 'web':           # so do quan he: 3 nguoi that o lang Dai Hoang -> 1 nhan vat
        s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#f2ead6"/>')
        s.append(f'<text x="540" y="820" font-family="{FONT}" font-weight="800" font-size="54" fill="#6b4a2a" text-anchor="middle">LÀNG ĐẠI HOÀNG</text>')
        pos = [(220, 1010), (540, 960), (860, 1010)]
        for k, (x, y) in enumerate(pos):
            q = back_ease(min(1, (t - at(sh, 1, .2) - k * .35) / .35))
            if q > 0:
                s.append(f'<g transform="translate({x} {y}) scale({f_(q)}) translate({-x} {-y})"><circle cx="{x}" cy="{y}" r="95" fill="#d8c9a4" stroke="{INK}" stroke-width="7"/>'
                         f'<circle cx="{x}" cy="{y - 25}" r="32" fill="#6e5a4a"/><path d="M{x - 55},{y + 60} Q{x},{y - 10} {x + 55},{y + 60} Z" fill="#6e5a4a"/>'
                         f'<text x="{x}" y="{y + 140}" font-family="{FONT}" font-weight="800" font-size="40" fill="#111" text-anchor="middle">NGƯỜI THẬT {k + 1}</text></g>')
        m = ease((t - at(sh, 2, 1.4)) / .6)
        if m > 0:
            for x, y in pos: s.append(f'<path d="M{x},{y + 160} L{f_(lerp(x, 540, m))},{f_(lerp(y + 160, 1300, m))}" stroke="#c4281f" stroke-width="10" stroke-dasharray="20 12"/>')
            s.append(f'<g opacity="{f_(m)}">' + ch('chipheo', 540, 1480, 160, 1, 'normal', t=t, tag=False) + '</g>')
        cam = (1.0, 540, 1000)
    elif ty == 'night_gate':    # dem, Chi cam dao den cong nha cu Ba
        s.append(sky('#0e1630', '#2a3458', True))
        s.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#3a4430" stroke="{INK}" stroke-width="6"/>')
        s.append(f'<rect x="660" y="640" width="70" height="{GY - 600}" fill="#5a3a22" stroke="{INK}" stroke-width="7"/><rect x="1160" y="640" width="70" height="{GY - 600}" fill="#5a3a22" stroke="{INK}" stroke-width="7"/>')
        s.append(f'<path d="M600,660 L945,520 L1290,660 Z" fill="#7a2a1e" stroke="{INK}" stroke-width="8"/><rect x="730" y="760" width="430" height="{GY - 720}" fill="#4a2a16" stroke="{INK}" stroke-width="7"/>')
        sw = osc(t, .5) * 10
        s.append(f'<line x1="700" y1="700" x2="{f_(700 + sw)}" y2="800" stroke="{INK}" stroke-width="4"/><ellipse cx="{f_(700 + sw)}" cy="840" rx="34" ry="44" fill="#ff8a3a" stroke="{INK}" stroke-width="5"/><circle cx="{f_(700 + sw)}" cy="840" r="120" fill="#ffb03a" opacity=".18"/>')
        x = lerp(-150, 420, ease(t / d)); bob = walk(t, .7)
        s.append(ch('chipheo', x, GY + 60 - bob, 200, 1, 'angry', [(.7, -.1, 'sword', 20)], lean=osc(t, .5) * 6, t=t))
        s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#0a1030" opacity=".25"/>')
        cam = (lerp(1.0, 1.12, ease(t / d)), lerp(400, 600, ease(t / d)), 860)
    else:
        s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#efe7d2"/>')
    return ''.join(s), cam, shake, flash


SFX = {
    'chui_road': [('every:1.3@0.4', 'shout', .5)],
    'chui_steps': [('f0.1', 'pop', .7), ('f0.35', 'pop', .7), ('f0.6', 'pop', .8)],
    'ke': [],
    'writer': [],
    'book_swap': [('f0.4', 'pop', .9), ('f0.42', 'ding', .5)],
    'kiln': [],
    'found_baby': [('f0.4', 'sting', .6)],
    'passed': [('every:1.5', 'pop', .4)],
    'farmhand': [('every:1.1@0.5', 'thud', .5)],
    'jealous': [('f0.4', 'sting', .6)],
    'arrest': [('every:0.7@0.6', 'thud', .3), (0.2, 'shout', .5)],
    'return': [(1.2, 'boom', .8), (1.25, 'sting', .7)],
    'drunk': [('every:2.5', 'shout', .4)],
    'alone': [('f0.1', 'tick', .5)],
    'echo': [('every:1.1', 'shout', .3)],
    'silence': [],
    'web': [('f0.05', 'pop', .6), ('f0.2', 'pop', .6), ('f0.35', 'pop', .6), ('f0.55', 'whoosh', .6)],
    'night_gate': [('every:1.4', 'thud', .3), ('f0.8', 'sting', .7)],
}


def install(M):
    """thay beat/SFX/GROUND cua module may dung (ksc_svg dang chay)."""
    M.beat = beat
    M.SFX_PLAN.update(SFX)
    for k in SFX: M.GROUND[k] = GY
