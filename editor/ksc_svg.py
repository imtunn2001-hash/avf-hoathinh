"""Ky Su Chien - hoat hinh 2D ve bang code theo skill hoat-hinh-2d-ve-bang-code (SVG -> rsvg-convert -> ffmpeg).
Nhan vat: editor/ksc_chars.py. Moi canh = beat(t, d) -> (svg_the_gioi, (zoom, cx, cy), shake, flash).
Khung 1080x1920 (Reels/TikTok/Shorts), bo cuc KHOA CUNG: chu trong SAFE (80..940, 260..1460).
spec: {series, badge, hook_text, next, voice_urls?, srt_urls?, cues?, durs?,
       shots: [{type, label, say, sfx?}]}  type: fleet_arrive | bait_row | melee | crash_stakes | victory | tide_board | prep_stakes | general
"""
import json
import doc_so, math, os, random, re, subprocess, sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ksc_chars as CH  # noqa: E402
import fx  # noqa: E402  23/11: chuyen canh whip, chu nhay theo tu, grade, ducking
from ksc_anim import mix_audio, SR  # noqa: E402  (SFX tu tao bang numpy)
from series import get, parse_srt, ease, word_times, _norm, scene_starts  # noqa: E402

W, H, FPS = 1080, 1920, 30
FMT = 'vertical'
GROUND = {'narrator': 1250, 'chase': 1150, 'ambush': 1150, 'fleet_arrive': 1000, 'prep_stakes': 1180, 'tide_board': 1250, 'bait_row': 1150, 'general': 1150, 'melee': 1060, 'crash_stakes': 1120, 'victory': 1080, 'army_march': 1100, 'crossbow_volley': 1080, 'trigger_board': 1250, 'arrow_dig': 1180, 'citadel': 1250, 'claw': 1180, 'drill': 1150}
ROOT = os.getcwd(); OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
SAFE = (80, 260, 940, 1460); TW = 780
FONT = 'Be Vietnam Pro, Inter'
INK = '#111'
WL = 900          # muc nuoc mac dinh (y)


def f_(v): return f'{v:.1f}'
def osc(t, f, ph=0.0): return math.sin(2 * math.pi * (f * t + ph))
def lerp(a, b, q): return a + (b - a) * q
def back_ease(q):  # pop-in vuot da
    q = max(0.0, min(1.0, q)); c = 1.70158; return 1 + (c + 1) * (q - 1) ** 3 + c * (q - 1) ** 2
def hold2(t, seed=0):  # run ray: giu 2 khung
    return random.Random(int(t * FPS / 2) * 7 + seed)
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------------- phong canh (ve rong x -800..1880 de zoom khong lo mep) ----------------
def sky(top, bot, y0=-400, y1=1100):
    return (f'<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient></defs>'
            f'<rect x="-800" y="{y0}" width="2680" height="{y1 - y0}" fill="url(#sk)"/>')


def karst(t, base, cols, seed=3, drift=6):
    rnd = random.Random(seed); out = []
    for k, col in enumerate(cols):
        x = -900; pts = [f'-900,{base + 600}']; off = (t * drift * (k + 1)) % 240
        while x < 2000:
            h = rnd.uniform(160, 330) * (1 - .2 * k); w = rnd.uniform(120, 220); b = base - 30 * k
            pts += [f'{f_(x - off)},{f_(b)}', f'{f_(x + w * .2 - off)},{f_(b - h)}', f'{f_(x + w * .42 - off)},{f_(b - h * .9)}', f'{f_(x + w * .7 - off)},{f_(b - 40)}']
            x += w
        pts.append(f'2000,{base + 600}')
        out.append(f'<polygon points="{" ".join(pts)}" fill="{col}"/>')
    return ''.join(out)


def water(t, lvl, c1='#3d7fae', c2='#24577e', amp=7):
    s = [f'<rect x="-800" y="{f_(lvl)}" width="2680" height="1400" fill="{c1}"/>', f'<rect x="-800" y="{f_(lvl + 140)}" width="2680" height="1400" fill="{c2}" opacity=".55"/>']
    for k in range(6):
        y = lvl + 10 + k * 34; ph = t * (.5 + k * .12)
        d = 'M' + ' L'.join(f'{x},{f_(y + math.sin(x / 42 + ph * 6.28) * amp * (1 - k * .1))}' for x in range(-800, 1900, 30))
        s.append(f'<path d="{d}" stroke="#d8ecf6" stroke-width="{3 - k * .3:.1f}" fill="none" opacity="{.7 - k * .09:.2f}"/>')
    return ''.join(s)


def reeds(t, x0, x1, y, seed=5, col='#3e6a2c'):
    rnd = random.Random(seed); s = []; x = x0
    while x < x1:
        h = rnd.uniform(60, 130); sw = osc(t, .5 + rnd.random() * .3, rnd.random()) * 10
        s.append(f'<path d="M{f_(x)},{f_(y)} Q{f_(x + sw * .4)},{f_(y - h * .5)} {f_(x + sw)},{f_(y - h)}" stroke="{col}" stroke-width="5" fill="none" stroke-linecap="round"/>')
        x += rnd.uniform(6, 13)
    return ''.join(s)


def stake(x, bed, top, lvl=None):
    return (f'<polygon points="{f_(x - 11)},{f_(bed)} {f_(x - 11)},{f_(top + 26)} {f_(x)},{f_(top)} {f_(x + 11)},{f_(top + 26)} {f_(x + 11)},{f_(bed)}" fill="#8a5e34" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<polygon points="{f_(x - 10)},{f_(top + 24)} {f_(x)},{f_(top)} {f_(x + 10)},{f_(top + 24)}" fill="#c9ccd4" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')


def light_boat(x, y, L, tilt=0.0):
    """thuyen nhe: tra ve (sau_than, truoc_than) de nhan vat ngoi giua 2 lop."""
    back = f'<path d="M{f_(x - L / 2)},{f_(y - 40)} L{f_(x + L / 2)},{f_(y - 40)} L{f_(x + L / 2 - 40)},{f_(y + 18)} L{f_(x - L / 2 + 40)},{f_(y + 18)} Z" fill="#6b4424" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    front = (f'<path d="M{f_(x - L / 2 - 30)},{f_(y - 52)} Q{f_(x)},{f_(y - 30)} {f_(x + L / 2 + 30)},{f_(y - 52)} L{f_(x + L / 2 - 30)},{f_(y + 22)} Q{f_(x)},{f_(y + 34)} {f_(x - L / 2 + 30)},{f_(y + 22)} Z" fill="#a06a38" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M{f_(x - L / 2 + 10)},{f_(y - 22)} Q{f_(x)},{f_(y - 6)} {f_(x + L / 2 - 10)},{f_(y - 22)}" stroke="#7a4e28" stroke-width="5" fill="none"/>')
    tr = f'rotate({f_(tilt)} {f_(x)} {f_(y)})'
    return f'<g transform="{tr}">{back}</g>', f'<g transform="{tr}">{front}</g>'


def junk(x, y, s=1.0, face=-1, tilt=0.0, sail=True):
    """tau chien lon Nam Han (khong chu tren co). face=-1: mui ben trai."""
    g = []
    if sail:
        g.append(f'<line x1="0" y1="-60" x2="0" y2="-430" stroke="{INK}" stroke-width="18"/><line x1="0" y1="-60" x2="0" y2="-430" stroke="#6b4424" stroke-width="10"/>')
        g.append(f'<path d="M-10,-420 L150,-405 L165,-120 L-10,-110 Z" fill="#d9bc86" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
        for k in range(1, 6): g.append(f'<line x1="-8" y1="{-420 + k * 52}" x2="{150 + k * 2.5:.0f}" y2="{-405 + k * 50}" stroke="#8a6a3e" stroke-width="5"/>')
        g.append(f'<path d="M-4,-430 L-80,-415 L-4,-398 Z" fill="#b8241e" stroke="{INK}" stroke-width="5"/>')
    g.append(f'<path d="M-330,-90 L-250,-50 L250,-50 L360,-150 L380,-80 L300,40 L-250,40 L-350,-30 Z" fill="#8a5630" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>')
    g.append('<path d="M-280,-20 L320,-20 M-260,12 L300,12" stroke="#5e3a1e" stroke-width="6"/>')
    for k in range(6): g.append(f'<circle cx="{-200 + k * 85}" cy="-2" r="9" fill="#3a2414" stroke="{INK}" stroke-width="4"/>')
    g.append(f'<path d="M180,-50 L360,-150 L360,-200 L190,-125 Z" fill="#9c6438" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    return f'<g transform="translate({f_(x)},{f_(y)}) rotate({f_(tilt)}) scale({f_(s * -face)},{f_(s)})">{"".join(g)}</g>'


def _rot(px, py, cx, cy, a):
    r = math.radians(a); dx, dy = px - cx, py - cy
    return cx + dx * math.cos(r) - dy * math.sin(r), cy + dx * math.sin(r) + dy * math.cos(r)


def junk_wreck(x, y, q, t, tau):
    """tau giac bi coc xuyen: q=0 nguyen -> q=1 gay doi (2 nua chuc dau xuong), coc dam xuyen qua san.
    tra ve (svg_than, svg_truoc, diem_nguoi) ; toa do cuc bo giong junk(face=-1, s=1)."""
    PX, PY = -20, 40                     # diem gay (ngay dinh coc chinh)
    ang = 17 * q; gap = 34 * q
    crack = 'L-10,-50 L-42,-24 L-6,-2 L-36,18 L-30,40'
    L = f'M-330,-90 L-250,-50 {crack} L-250,40 L-350,-30 Z'
    R = 'M-10,-50 L250,-50 L360,-150 L380,-80 L300,40 L-30,40 L-36,18 L-6,-2 L-42,-24 Z'
    def half(path, extra, a, dx):
        return (f'<g transform="translate({f_(dx)},0) rotate({f_(a)} {PX} {PY})"><path d="{path}" fill="#8a5630" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>{extra}</g>')
    holes = ''
    if q > 0:
        for hx in (-200, 190):  # lo thung quanh coc phu
            r = 26 * min(1, q * 2)
            pts = ' '.join(f'{f_(hx + math.cos(k * .785) * r * (1 if k % 2 else .55))},{f_(14 + math.sin(k * .785) * r * (1 if k % 2 else .55))}' for k in range(8))
            holes += f'<polygon points="{pts}" fill="#1a0f08" stroke="{INK}" stroke-width="4"/>'
    lp = '<path d="M-280,-20 L-40,-20 M-260,12 L-20,12" stroke="#5e3a1e" stroke-width="6"/>' + ''.join(f'<circle cx="{-200 + k * 85}" cy="-2" r="9" fill="#3a2414" stroke="{INK}" stroke-width="4"/>' for k in range(2))
    rp = ('<path d="M-10,-20 L320,-20 M-10,12 L300,12" stroke="#5e3a1e" stroke-width="6"/>' + ''.join(f'<circle cx="{-30 + k * 85}" cy="-2" r="9" fill="#3a2414" stroke="{INK}" stroke-width="4"/>' for k in range(1, 4))
          + f'<path d="M180,-50 L360,-150 L360,-200 L190,-125 Z" fill="#9c6438" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    # mat buom do theo nua phai, nga them
    ma = 40 * ease(min(1, q * 1.3))
    mast = (f'<g transform="rotate({f_(ma)} 40 -50)"><line x1="40" y1="-60" x2="40" y2="-430" stroke="{INK}" stroke-width="18"/><line x1="40" y1="-60" x2="40" y2="-430" stroke="#6b4424" stroke-width="10"/>'
            f'<path d="M30,-420 L190,-405 L{f_(205 - 40 * q)},-120 L{f_(110 + 30 * q)},-150 L30,-110 Z" fill="#d9bc86" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M36,-430 L-40,-415 L36,-398 Z" fill="#b8241e" stroke="{INK}" stroke-width="5"/></g>')
    body = half(L, lp + (holes if q > 0 else ''), -ang, -gap) + half(R, mast + rp, ang, gap)
    # coc: chinh xuyen qua cho gay, 2 coc phu xuyen day (ve truoc than)
    tipy = lerp(60, -175, ease(min(1, q * 2.5)))
    front = (f'<g transform="translate({PX},0) scale(1.6,1) translate({-PX},0)">' + stake(PX, 420, tipy) + '</g>'
             + ''.join(f'<polygon points="{f_(PX + dx)},-52 {f_(PX + dx * 2.2)},{f_(-52 - 46 * q)} {f_(PX + dx * 1.3)},-50" fill="#c08850" stroke="{INK}" stroke-width="4"/>' for dx in (-22, -12, 14, 24) if q > .2))
    front += stake(-200, 420, lerp(60, -30, ease(min(1, q * 3)))) + stake(190, 420, lerp(60, -20, ease(min(1, q * 3))))
    if tau > 0:
        rnd = random.Random(11)
        for k in range(12):  # van go vang ra
            vx = rnd.uniform(-420, 420); vy = rnd.uniform(-720, -420); rr = rnd.uniform(-900, 900)
            tt = tau - k * .03
            if tt <= 0: continue
            px = PX + vx * tt; py = -40 + vy * tt + 1100 * tt * tt
            if py > 200: continue
            w = rnd.choice((60, 46, 34))
            front += f'<rect x="{f_(px - w / 2)}" y="{f_(py - 7)}" width="{w}" height="14" rx="3" fill="#a06a38" stroke="{INK}" stroke-width="4" transform="rotate({f_(rr * tt)} {f_(px)} {f_(py)})"/>'
        for hx in (PX, -200, 190):  # nuoc phut len qua lo thung
            for k in range(5):
                a = ((tau * 1.6 + k * .2) % 1.0); dx = (k - 2) * 14 * a
                front += f'<circle cx="{f_(hx + dx)}" cy="{f_(-10 - 190 * a + 260 * a * a)}" r="{f_(11 - 7 * a)}" fill="#e6f4fb" stroke="{INK}" stroke-width="3"/>'
    spots = [_rot(-200, -50, PX, PY, -ang), _rot(170, -50, PX, PY, ang)]
    spots = [(x + (sx - gap if i == 0 else sx + gap), y + sy) for i, (sx, sy) in enumerate(spots)]
    tr = f'translate({f_(x)},{f_(y)})'
    return f'<g transform="{tr}">{body}</g>', f'<g transform="{tr}">{front}</g>', spots, (-ang, ang)


def star(x, y, r, rot=0.0):
    pts = []
    for k in range(16):
        a = math.radians(rot + k * 22.5); rr = r if k % 2 == 0 else r * .45
        pts.append(f'{f_(x + math.cos(a) * rr)},{f_(y + math.sin(a) * rr)}')
    return f'<polygon points="{" ".join(pts)}" fill="#fff6b0" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'


def splash(x, y, q, s=1.0):
    if q <= 0 or q >= 1: return ''
    out = []
    for k in range(7):
        a = math.radians(-160 + k * 23); d = (40 + 120 * q) * s
        px, py = x + math.cos(a) * d, y + math.sin(a) * d * 1.3 + 260 * q * q * s
        out.append(f'<circle cx="{f_(px)}" cy="{f_(py)}" r="{f_((14 - 10 * q) * s)}" fill="#e6f4fb" stroke="{INK}" stroke-width="4"/>')
    return ''.join(out)


def smoke(x, y, t, s=1.0):
    k = int(t * FPS / 2) % 4; out = []
    for j in range(3):
        r = (34 + 10 * ((j + k) % 3)) * s; ox = (j - 1) * 40 * s + k * 3; oy = -j * 26 * s - k * 6
        out.append(f'<circle cx="{f_(x + ox)}" cy="{f_(y + oy)}" r="{f_(r + 6)}" fill="#7a7a7a" stroke="{INK}" stroke-width="5"/><circle cx="{f_(x + ox - 4)}" cy="{f_(y + oy - 4)}" r="{f_(r)}" fill="#c8c8c8"/>')
    return ''.join(out)


# ---------------- cac canh ----------------
def beat(sh, t, d):
    """tra ve (svg, (zoom, cx, cy), shake, flash)."""
    ty = sh['type']; s = []; cam = (1.0, 540, 830); shake = 0.0; flash = 0.0
    if ty == 'fleet_arrive':
        s.append(sky('#5a7fb0', '#d8e6ee')); s.append(karst(t, 860, ['#7c95a3', '#5f7a86']))
        s.append(water(t, WL)); s.append(reeds(t, -300, 160, WL + 20))
        for k in (2, 1, 0):
            sc = .55 + k * .22; x = lerp(1500 + k * 260, 380 + k * 300, ease(t / max(2.5, d * .9))); y = WL + 70 + k * 120 + osc(t, .35, k * .3) * 6
            for j in range(3):
                cx_ = x - 120 * sc + j * 120 * sc
                g, _ = CH.character('linhhan', cx_, y - 48 * sc, 62 * sc, -1, 'angry', [(.55, -.1, 'spear', -70)], tag=False, t=t); s.append(g)
            if k == 0:
                g, _ = CH.character('hoangthao', x + 210 * sc, y - 70 * sc, 82 * sc, -1, 'happy', [(.6, 0, 'sword', -60)], tag=(t > max(2.5, d * .9) * .6), t=t); s.append(g)
            s.append(junk(x, y, sc, -1, osc(t, .35, k) * 1.2))
        cam = (lerp(1.0, 1.08, ease(t / d)), 540 + 40 * ease(t / d), 860)
    elif ty == 'bait_row':
        s.append(sky('#5a7fb0', '#d8e6ee')); s.append(karst(t, 820, ['#7c95a3', '#5f7a86'], drift=40)); s.append(water(t, 860))
        jx = lerp(1350, 1020, ease(t / d)); s.append(junk(jx, 1000 + osc(t, .35) * 5, .75, -1))
        g, _ = CH.character('linhhan', jx - 60, 950, 56, -1, 'angry', [(.6, -.2, 'spear', -40)], tag=False, t=t); s.append(g)
        for k in range(10):   # vet nuoc troi -> cam giac lao nhanh
            x = (k * 230 - t * 420) % 1900 - 400; y = 1180 + (k % 3) * 50
            s.append(f'<path d="M{f_(x)},{f_(y)} l110,0" stroke="#e6f4fb" stroke-width="6" stroke-linecap="round" opacity=".8"/>')
        bx, by = 470, 1150 + osc(t, .55) * 6; tilt = osc(t, .55, .25) * 1.5
        bk, fr = light_boat(bx, by, 520, tilt); s.append(bk)
        for k, nm in enumerate(['linhviet2', 'linhviet', 'linhviet2']):
            ph = (t * 1.25 + k * .08) % 1.0; a = -70 + 110 * (ph if ph < .55 else (1 - ph) / .45 * .55 * 0 + (1 - (ph - .55) / .45)) if True else 0
            a = lerp(-75, 40, ph / .55) if ph < .55 else lerp(40, -75, (ph - .55) / .45)
            hx = .45 + .25 * (1 - ph if ph < .55 else ph)
            g, _ = CH.character(nm, bx - 170 + k * 170, by - 28, 96, -1, 'surprised' if k == 1 else 'happy', [(hx, .05, 'oar', 180 - a if False else a + 90)], tag=(k == 1), t=t, hidden_below=by - 40)
            s.append(g)
            if abs(ph - .02) < 1.5 / FPS * 1.25: pass
            s.append(splash(bx - 170 + k * 170 - 150, by + 30, ((t * 1.25 + k * .08) % 1.0) / .5))
        s.append(fr)
        cam = (1.05, 540, 900)
    elif ty == 'melee':
        s.append(sky('#4d6a94', '#c4d4de')); s.append(karst(t, 760, ['#6f8592'])); s.append(water(t, 1080, amp=10))
        deck = 1060
        s.append(f'<path d="M-800,{deck} L1880,{deck} L1880,{deck + 70} L-800,{deck + 70} Z" fill="#9a6232" stroke="{INK}" stroke-width="8"/>')
        s.append(f'<path d="M-800,{deck + 26} L1880,{deck + 26}" stroke="#6b4022" stroke-width="6"/>')
        cyc = 1.1; fall_at = float(sh.get('fall_at', max(3.0, d - 2.2))); fallen = t > fall_at
        # cap danh nhau nho phia sau
        for k, (x1, x2) in enumerate([(-60, 110), (900, 1070)]):
            q = (t + k * .37) % cyc; hit = q > .45 and q < .7
            g, _ = CH.character('linhviet2', x1, deck - 150, 70, 1, 'angry', [(.55 + (.45 if hit else 0), -.05, 'spear', -10)], tag=False, t=t); s.append(g)
            g, _ = CH.character('linhhan', x2, deck - 150, 70, -1, 'angry', [(.6, -.2, 'sword', -100)], tag=False, t=t); s.append(g)
        q = t % cyc; lunge = ease((q - .3) / .2) * (1 - ease((q - .7) / .35)) if not fallen else 0
        vx = 250 + 40 * lunge
        g, tips = CH.character('linhviet', vx, deck, 170, 1, 'angry', [(.45 + .25 * lunge, -.05, 'spear', -6 + 4 * lunge), (.2, .05)], t=t); s.append(g)
        if not fallen:
            shiv = hold2(t, 3).uniform(-3, 3) if (q > .5 and q < .8) else 0
            g, _ = CH.character('linhhan', 800 + shiv, deck, 170, -1, 'angry' if q < .5 else 'scared', [(.55, -.25, 'sword', -95), (.45, .05, 'shield', 0)], t=t); s.append(g)
            if .5 <= q < .62:
                tip = tips[0]; s.append(star(tip[0] + 30, tip[1], 70 * back_ease((q - .5) / .12), q * 300)); shake = 12; flash = .45
        else:
            ft = t - fall_at; rot = -80 * ease(ft / .5); hx = 800 + 240 * ease(ft / .8); hy = deck + max(0, ft - .35) ** 2 * 1800
            s.append(f'<g transform="rotate({f_(rot)} {f_(hx)} {f_(hy)})">')
            g, _ = CH.character('linhhan', hx, hy, 170, -1, 'scared', [(.3, -1.0), (-.2, -1.0)], tag=False, t=t); s.append(g); s.append('</g>')
            s.append(splash(1040, 1100, (ft - .55) / .9, 1.6))
            if ft < .2: s.append(star(800, deck - 230, 90, 20)); shake = 14; flash = .5
        cam = (1.1 + .05 * lunge, 560, 820)
    elif ty == 'crash_stakes':
        en = sh.get('enemy', 'linhhan'); hero = sh.get('hero'); phase = sh.get('phase', 'crash')
        s.append(sky('#3e5478', '#a9bccb')); s.append(karst(t, 740, ['#62788a', '#4d6474']))
        if phase == 'retreat':     # nuoc rut dan, coc nho dan, tau giac quay dau thao chay ve phia coc
            lvl = lerp(800, 960, ease(t / d)); s.append(water(t, lvl))
            jx = lerp(380, 620, ease(t / d)); jy = lvl + 120
            for j in range(3):
                g, _ = CH.character(en, jx - 140 + j * 130, jy - 70, 78, 1, 'scared', [(.3, -1.1), (-.3, -1.1)], tag=(j == 1), t=t); s.append(g)
            s.append(junk(jx, jy, 1.0, 1, osc(t, .4) * 2))
            for k in range(6):
                x = 820 + k * 110; s.append(stake(x, 1500, lerp(1020, 900, ease(t / d)) - (k % 2) * 16))
            cam = (1.0, 600, 930)
            return ''.join(s), cam, 0.0, 0.0
        hit = .05 if sh.get('late') else d * .45; lvl = lerp(800, 960, ease(min(1, t / max(.1, hit)))) if not sh.get('late') else 960
        s.append(water(t, lvl)); tau = max(0.0, t - hit)
        q = ease(min(1, tau / .45)); sink = .85 * ease(max(0.0, min(1, (tau - 1.1) / max(.6, d - hit - 1.1))))
        jx = (620 - min(t, hit) * 60 + (200 if hero else 0)) if not sh.get('late') else 560 + (200 if hero else 0)
        jolt = hold2(t, 9).uniform(-8, 8) if hit < t < hit + .5 else 0
        jy = lvl + 120 + sink * 130 + jolt
        if tau <= 0:   # dang lao toi: tau nguyen ven
            for j in range(3):
                g, _ = CH.character(en, jx - 140 + j * 130, jy - 70, 78, -1, 'angry', [(.55, -.2, 'spear', -70)], tag=(j == 1), t=t); s.append(g)
            s.append(junk(jx, jy, 1.0, -1, 0))   # coc con chim duoi nuoc: khong thay
        else:
            body, front, spots, angs = junk_wreck(jx, jy, q, t, tau)
            for i, (sx, sy) in enumerate(spots):   # 2 linh bam tren 2 nua tau
                g, _ = CH.character(en, sx, sy - 20, 78, -1, 'scared', [(.3, -1.1), (-.3, -1.1)], tag=False, t=t)
                s.append(f'<g transform="rotate({f_(angs[i] * 1.3)} {f_(sx)} {f_(sy)})">{g}</g>')
            # linh thu 3 bi hat xuong nuoc
            fx = jx - 60 - 330 * min(tau, .9); fy = jy - 120 - 620 * tau + 900 * tau * tau
            surf = lvl + 70
            if fy < surf:
                g, _ = CH.character(en, fx, fy, 78, -1, 'scared', [(.4, -1.2), (-.4, -1.2)], tag=False, lean=-30 * tau, t=t); s.append(g)
            else:
                bob = osc(t, 1.4) * 8
                g, _ = CH.character(en, fx, surf + 95 + bob, 78, -1, 'scared', [(.45, -1.4 + .2 * osc(t, 2)), (-.45, -1.4 - .2 * osc(t, 2))], tag=False, hidden_below=surf + 10, t=t); s.append(g)
            s.append(body)
            for k in range(9):
                if abs(60 + k * 120 - jx) > 280: s.append(stake(60 + k * 120, 1500, 980 - (k % 3) * 18))
            s.append(front)
            # mat nuoc phia truoc che phan than da chim
            s.append(f'<rect x="-800" y="{f_(lvl + 150)}" width="2680" height="1400" fill="#2e6894" opacity=".72"/>')
            s.append(f'<path d="M-800,{f_(lvl + 150)} ' + ' '.join(f'L{x},{f_(lvl + 150 + math.sin(x / 40 + t * 6) * 6)}' for x in range(-800, 1900, 40)) + '" stroke="#d8ecf6" stroke-width="5" fill="none"/>')
            if tau < .22: s.append(star(jx - 20, jy + 30, 85 * back_ease(tau / .15))); shake = 22; flash = .5
            elif tau < .55: shake = 10
            s.append(splash(jx + 300, lvl + 90, ((tau + .5) % 1.3) / 1.3, .8))
            if tau > .75: s.append(splash(fx, surf + 20, min(.99, (tau - .75) / .8), .9))
        if hero:
            s.append(f'<path d="M-800,1120 Q-200,1060 380,1120 L380,2000 L-800,2000 Z" fill="#6f9a52" stroke="{INK}" stroke-width="7"/>')
            jump = abs(osc(t, 1.2)) * 30
            g, _ = CH.character(hero, 230, 1120 - jump, 140, 1, 'happy', [(.7, -.35, 'sword', -35), (-.4, -.3)], t=t); s.append(g)
        cam = (lerp(1.0, 1.1, ease(t / d)), 560, 930)
    elif ty == 'victory':
        s.append(sky('#4b3f7a', '#f2b27c')); sy = 760 - 30 * ease(t / d)
        s.append(f'<circle cx="820" cy="{f_(sy)}" r="110" fill="#ffd68a" stroke="{INK}" stroke-width="6"/>')
        s.append(karst(t, 860, ['#7a6a8a', '#5e5170'])); s.append(water(t, 940))
        if not sh.get('no_junk'): s.append(junk(900, 1060, .6, -1, -20))
        s.append(f'<path d="M-800,1080 Q200,1010 700,1080 L700,2000 L-800,2000 Z" fill="#6f9a52" stroke="{INK}" stroke-width="7"/>')
        for k, (nm, x, D) in enumerate([(sh.get('side', 'linhviet2'), 120, 120), (sh.get('hero', 'ngoquyen'), 330, 150), (sh.get('side', 'linhviet'), 540, 120)]):
            jump = abs(osc(t, 1.3, k * .2)) * 40
            hands = [(.55, -.9, 'flag' if k == 1 else ('crossbow' if nm == 'linhaulac' else 'spear'), -80), (-.45, -.9)]
            g, _ = CH.character(nm, x, 1080 - jump, D, 1, 'happy', hands, t=t); s.append(g)
        cam = (1.04, 480, 900)
    elif ty == 'tide_board':      # hoc tro giang bang: muc nuoc len xuong, coc chim/nho
        s.append('<rect x="-800" y="-400" width="2680" height="2800" fill="#efe7d2"/>')
        s.append(f'<rect x="70" y="740" width="640" height="500" rx="18" fill="#2e4a40" stroke="{INK}" stroke-width="10"/>')
        cyc = float(sh.get('cycle', 5.0)); mode = sh.get('mode', 'cycle')
        if mode == 'high': hi = lerp(.35, 1.0, ease(t / 1.2)) + osc(t, .5) * .03
        elif mode == 'low': hi = lerp(.65, 0.0, ease(t / 1.2)) + osc(t, .5) * .03
        else: hi = .5 + .5 * math.cos(2 * math.pi * t / cyc)
        lvl = lerp(1150, 860, hi)
        s.append(f'<rect x="80" y="{f_(lvl)}" width="620" height="{f_(1230 - lvl)}" fill="#4b8fc4" opacity=".65"/>')
        for k in range(5): s.append(stake(150 + k * 120, 1230, 1010))
        s.append(f'<path d="M80,{f_(lvl)} L700,{f_(lvl)}" stroke="#bfe3ff" stroke-width="6"/>')
        if t > 2.4: s.append(f'<text x="390" y="800" font-family="{FONT}" font-weight="800" font-size="36" fill="#ffd400" text-anchor="middle">{"TRIỀU LÊN: CỌC CHÌM" if (mode == 'high' or (mode != 'low' and hi > .5)) else "TRIỀU XUỐNG: CỌC NHÔ"}</text>')
        g, _ = CH.character('hoctro', 880, 1250, 180, -1, 'happy' if hi > .5 else 'surprised', [(.85, .05, 'board', 35)], t=t); s.append(g)
        cam = (1.0, 540, 900)
    elif ty == 'narrator':        # hoc tro noi voi nguoi xem: gat dau giu 3 khung, tay chi
        s.append('<rect x="-800" y="-400" width="2680" height="2800" fill="#efe7d2"/>')
        s.append(f'<rect x="-800" y="1250" width="2680" height="900" fill="#d8c9a4"/>')
        for k in range(7): s.append(f'<rect x="{-640 + k * 360}" y="560" width="250" height="330" rx="12" fill="#e4d8bb" stroke="#c9b98f" stroke-width="6"/>')
        nod = (int(t * FPS / 3) % 4 in (1, 2)) * 3
        ex = sh.get('expr', 'happy'); bob = abs(osc(t, 1.6)) * 10
        g, _ = CH.character('hoctro', 640, 1250 - bob, 175, -1, ex, [(.85, .0 + .06 * abs(osc(t, .9)), 'board', 30 + 12 * osc(t, .9)), (-.55, .05)], head_rot=nod, t=t); s.append(g)
        if sh.get('ask'):
            q = back_ease(min(1, t / .4)); s.append(f'<text x="300" y="1060" font-family="{FONT}" font-weight="800" font-size="{f_(260 * q)}" fill="#c4281f" stroke="{INK}" stroke-width="8" paint-order="stroke" text-anchor="middle">?</text>')
            cam = (lerp(1.0, 1.14, ease(min(1, t / max(.5, d)))), 560, 900)   # bat nghi: day may cham
        else:
            cam = (1.0, 540, 900)
    elif ty == 'chase':           # tau giac duoi theo, luot qua bai coc dang chim
        s.append(sky('#5a7fb0', '#d8e6ee')); s.append(karst(t, 800, ['#7c95a3', '#5f7a86'], drift=30)); s.append(water(t, 860))
        for k in range(8): s.append(f'<g opacity=".35">{stake(-200 + k * 190, 1500, 1060 + (k % 2) * 20)}</g>')
        jx = lerp(1250, 520, ease(t / d)); jy = 1060 + osc(t, .35) * 5
        for j in range(3):
            g, _ = CH.character('linhhan', jx - 140 + j * 130, jy - 70, 80, -1, 'angry', [(.6, -.25, 'spear', -30)], tag=(j == 1), t=t); s.append(g)
        s.append(junk(jx, jy, 1.0, -1))
        for k in range(8):
            x = (k * 250 - t * 380) % 2000 - 500; s.append(f'<path d="M{f_(x)},{1200 + (k % 3) * 45} l130,0" stroke="#e6f4fb" stroke-width="6" stroke-linecap="round" opacity=".8"/>')
        cam = (1.0, 520, 930)
    elif ty == 'ambush':          # quan ta tu lau say hai bo xong ra, tau giac quay dau
        s.append(sky('#4d6a94', '#c4d4de')); s.append(karst(t, 780, ['#6f8592', '#596f7c'])); s.append(water(t, 900))
        turn = ease((t - d * .5) / .6); jf = -1 if turn < .5 else 1
        s.append(junk(540, 1060 + osc(t, .35) * 5, .8, jf, osc(t, .6) * 2))
        g, _ = CH.character('linhhan', 520, 990, 80, jf, 'scared', [(.3, -1.1), (-.3, -1.1)], t=t); s.append(g)
        for side, x0 in ((1, 60), (-1, 1020)):
            s.append(f'<path d="M{x0 - 400 * side},1160 L{x0 + 330 * side},1150 L{x0 + 330 * side},2000 L{x0 - 400 * side},2000 Z" fill="#6f9a52" stroke="{INK}" stroke-width="7"/>')
            for j in range(2):
                q = back_ease(min(1, max(0, (t - .2 - j * .35) / .45))); x = x0 + side * (70 + j * 125)
                lunge = abs(osc(t, .9, j * .3))
                g, _ = CH.character('linhviet' if j == 0 else 'linhviet2', x, 1150 + (1 - q) * 220, 120, side, 'angry', [(.5 + .3 * lunge, -.1, 'spear', -15), (.15, .1)], tag=(j == 0), t=t); s.append(g)
            s.append(reeds(t, x0 - 400 * side if side > 0 else x0 - 30, x0 + 30 if side > 0 else x0 + 400, 1170, seed=7 + side))
        for k in range(4):
            a = ((t * 1.2 + k * .25) % 1.0); side = 1 if k % 2 == 0 else -1
            x = lerp(80 if side > 0 else 1000, 540, a); y = 1000 - 260 * math.sin(math.pi * a)
            s.append(f'<line x1="{f_(x)}" y1="{f_(y)}" x2="{f_(x - side * 46)}" y2="{f_(y + 8)}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><line x1="{f_(x)}" y1="{f_(y)}" x2="{f_(x - side * 46)}" y2="{f_(y + 8)}" stroke="#8a5e34" stroke-width="3"/>')
        cam = (1.0, 540, 930)
    elif ty == 'prep_stakes':
        s.append(sky('#5a7fb0', '#d8e6ee')); s.append(karst(t, 800, ['#7f9a86', '#62806a'])); s.append(water(t, 860, amp=3))
        s.append(f'<path d="M-800,940 L1880,960 L1880,2000 L-800,2000 Z" fill="#8c6e48" stroke="{INK}" stroke-width="7"/>')
        for k in range(8): s.append(stake(-120 + k * 190, 1100, 860 + (k % 2) * 30))
        for k, (nm, x, fc) in enumerate([('linhviet', 260, 1), ('linhviet2', 820, -1)]):
            q = (t + k * .45) % 1.0; up = q < .55; a = lerp(-100, -80, q / .55) if up else lerp(-80, 25, ease((q - .55) / .15))
            sx = x + fc * 200
            s.append(stake(sx, 1180, 990 + (12 if q > .7 else 0)))
            g, _ = CH.character(nm, x, 1180, 150, fc, 'angry' if q > .6 else 'normal', [(.9, -.55 if up else -.15, 'mallet', a)], t=t); s.append(g)
            if .7 <= q < .8: s.append(star(sx, 990, 50, q * 200))
        cam = (1.02, 540, 960)
    elif ty == 'general':
        s.append(sky('#5a7fb0', '#d8e6ee')); s.append(karst(t, 820, ['#7c95a3', '#5f7a86'])); s.append(water(t, 880))
        bx, by = 520, 1150 + osc(t, .5) * 6; bk, fr = light_boat(bx, by, 560); s.append(bk)
        for k, nm in enumerate(['linhviet2', 'linhviet2']):
            ph = (t * 1.25 + k * .1) % 1.0; a = lerp(-75, 40, ph / .55) if ph < .55 else lerp(40, -75, (ph - .55) / .45)
            g, _ = CH.character(nm, bx - 200 + k * 400, by - 28, 90, 1, 'normal', [(.5, .05, 'oar', a + 90)], tag=False, t=t, hidden_below=by - 40); s.append(g)
        cmd = abs(osc(t, .8))
        g, _ = CH.character('ngoquyen', bx, by - 30 - 8 * cmd, 160, 1, 'angry', [(.75, -.3 - .15 * cmd, 'sword', -30 - 15 * cmd), (-.4, .1)], t=t, hidden_below=by - 40); s.append(g)
        s.append(fr); cam = (1.0, 540, 760)
    elif ty == 'army_march':      # dao quan dich tien tu phai sang trai, co, trong
        s.append(sky('#7a8aa8', '#e2d6c0')); s.append(karst(t, 900, ['#8a9a8a', '#6f826e'], seed=9, drift=0))
        s.append(f'<path d="M-800,1000 Q500,960 1880,1010 L1880,2000 L-800,2000 Z" fill="#a8925e" stroke="{INK}" stroke-width="7"/>')
        en = sh.get('enemy', 'linhtrieu'); lead = sh.get('leader', 'trieuda')
        adv = 260 * ease(min(1, t / max(2.0, d)))
        for row in (2, 1, 0):
            sc = .55 + row * .22; y = 1010 + row * 70
            for j in range(7):
                x = 1000 + j * 150 * sc - adv * (1 + row * .3) - row * 60; bob = abs(osc(t, 1.6, j * .13)) * 8
                if x < 520 or x > 1900: continue
                g, _ = CH.character(en, x, y - bob, 70 * sc, -1, 'angry', [(.55, -.15, 'spear', -75)], tag=False, t=t); s.append(g)
                if j % 3 == 1:
                    fx_ = x + 40 * sc; s.append(f'<line x1="{f_(fx_)}" y1="{f_(y - 160 * sc)}" x2="{f_(fx_)}" y2="{f_(y - 330 * sc)}" stroke="{INK}" stroke-width="{f_(8 * sc)}"/><path d="M{f_(fx_)},{f_(y - 330 * sc)} l{f_(-70 * sc)},{f_(14 * sc + osc(t, 1.2, j) * 8 * sc)} l{f_(70 * sc)},{f_(30 * sc)} Z" fill="#3a3a48" stroke="{INK}" stroke-width="{f_(4 * sc)}"/>')
        s.append(f'<ellipse cx="{f_(1100 - adv)}" cy="1240" rx="560" ry="36" fill="#d8c79a" opacity=".45"/>')
        g, _ = CH.character(lead, 380 - adv * .4, 1170, 150, -1, 'angry', [(.75, -.25, 'sword', -30)], t=t); s.append(g)
        cam = (lerp(1.0, 1.06, ease(t / d)), 600, 920)
    elif ty == 'crossbow_volley':  # quan Au Lac tren tuong dat ban no tung loat, dich lui
        s.append(sky('#6a86b0', '#e6dcc4')); s.append(karst(t, 900, ['#8a9a8a', '#6f826e'], seed=9, drift=0))
        s.append(f'<path d="M-800,1040 Q600,1000 1880,1050 L1880,2000 L-800,2000 Z" fill="#a8925e" stroke="{INK}" stroke-width="7"/>')
        cyc = float(sh.get('cycle', 1.8)); k = int(t / cyc); q = (t % cyc) / cyc
        en = sh.get('enemy', 'linhtrieu'); back = 120 * ease(min(1, t / max(2.0, d)))
        for j in range(6):   # dich: giơ khien, lui dan
            x = 800 + j * 95 + back + (j % 2) * 30; y = 1110 + (j % 2) * 50; sh_ = hold2(t, j).uniform(-3, 3) if q < .35 else 0
            g, _ = CH.character(en, x + sh_, y, 82, -1, 'scared', [(.5, -.35, 'shield', 0)], tag=(j == 2), t=t); s.append(g)
        for n in range(2):   # 2 loat ten dang bay
            tf = (q - .12) * cyc + n * cyc
            if 0 < tf < 1.1:
                for j in range(9):
                    x0, y0 = 330 + (j % 3) * 170, 870 - (j // 3) * 14; x1 = 820 + (j * 97) % 420; u = tf / 1.1
                    x = lerp(x0, x1, u); y = lerp(y0, 1050, u) - 360 * u * (1 - u) * 1.0
                    ang = math.degrees(math.atan2((1050 - y0) - 360 * (1 - 2 * u), x1 - x0))
                    s.append(f'<g transform="translate({f_(x)} {f_(y)}) rotate({f_(ang)})"><line x1="-46" y1="0" x2="20" y2="0" stroke="{INK}" stroke-width="7"/><line x1="-44" y1="0" x2="18" y2="0" stroke="#c9a35a" stroke-width="3"/><polygon points="20,-7 36,0 20,7" fill="#b07a3a" stroke="{INK}" stroke-width="3"/></g>')
        s.append(f'<path d="M-800,1000 L560,1000 L600,1180 L-800,1180 Z" fill="#8a6a40" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>')   # tuong dat
        for x in range(-760, 560, 90): s.append(f'<rect x="{x}" y="976" width="54" height="30" fill="#8a6a40" stroke="{INK}" stroke-width="6"/>')
        fired = q < .25
        for j, x in enumerate((170, 365, 560)):
            g, _ = CH.character('linhaulac', x, 1000, 115, 1, 'angry', [(.55, -.25, 'crossbow_r' if fired else 'crossbow', -14), (.15, -.15)], tag=(j == 1), t=t, hidden_below=1010); s.append(g)
        if sh.get('hero'):
            g, _ = CH.character(sh['hero'], 40, 1000, 150, 1, 'angry', [(.75, -.3, 'sword', -25)], t=t, hidden_below=1010); s.append(g)
        if q < .08: shake = 6
        cam = (1.0, 600, 930)
    elif ty == 'drill':           # Cao Lo luyen quan ban no vao bia rom
        s.append(sky('#6a9ad0', '#eee2c4')); s.append(karst(t, 900, ['#8aa08a', '#6f866e'], seed=4, drift=0))
        s.append(f'<path d="M-800,1060 Q600,1030 1880,1070 L1880,2000 L-800,2000 Z" fill="#9ab060" stroke="{INK}" stroke-width="7"/>')
        cyc = float(sh.get('cycle', 2.0)); k = int(t / cyc); q = (t % cyc) / cyc
        for i, (bx, by) in enumerate(((930, 1010), (1060, 1040))):
            s.append(f'<line x1="{bx}" y1="{by}" x2="{bx}" y2="{by + 120}" stroke="{INK}" stroke-width="10"/><circle cx="{bx}" cy="{by - 30}" r="62" fill="#e8c86a" stroke="{INK}" stroke-width="7"/><circle cx="{bx}" cy="{by - 30}" r="36" fill="none" stroke="#c4281f" stroke-width="8"/><circle cx="{bx}" cy="{by - 30}" r="10" fill="#c4281f"/>')
            for a in range(min(6, k + (1 if q > .35 else 0))):
                rr = random.Random(a * 7 + i); ax = bx + rr.uniform(-30, 30); ay = by - 30 + rr.uniform(-30, 30)
                s.append(f'<line x1="{f_(ax - 50)}" y1="{f_(ay - 4)}" x2="{f_(ax)}" y2="{f_(ay)}" stroke="{INK}" stroke-width="6"/><line x1="{f_(ax - 48)}" y1="{f_(ay - 4)}" x2="{f_(ax)}" y2="{f_(ay)}" stroke="#c9a35a" stroke-width="3"/>')
        if .15 < q < .35:
            u = (q - .15) / .2
            for j in range(3): s.append(f'<line x1="{f_(lerp(420 + j * 140, 900, u) - 40)}" y1="{f_(lerp(1000, 980, u))}" x2="{f_(lerp(420 + j * 140, 900, u))}" y2="{f_(lerp(1000, 980, u))}" stroke="#c9a35a" stroke-width="5"/>')
        fired = .15 < q < .6
        for j, x in enumerate((310, 500, 690)):
            g, _ = CH.character('linhaulac', x, 1140, 110, 1, 'angry', [(.55, -.25, 'crossbow_r' if fired else 'crossbow', -4), (.15, -.15)], tag=(j == 1), t=t); s.append(g)
        cmd = abs(osc(t, .5))
        g, _ = CH.character('caolo', 130, 1150, 150, 1, 'angry' if cmd > .5 else 'normal', [(.35, -1.15 - .15 * cmd), (-.4, .05)], t=t); s.append(g)
        if q < .15 and q > .1: shake = 3
        cam = (1.0, 580, 960)
    elif ty == 'trigger_board':   # hoc tro giang lay no tren bang
        s.append('<rect x="-800" y="-400" width="2680" height="2800" fill="#efe7d2"/>')
        s.append(f'<rect x="70" y="740" width="640" height="500" rx="18" fill="#2e4a40" stroke="{INK}" stroke-width="10"/>')
        cyc = float(sh.get('cycle', 3.2)); q = (t % cyc) / cyc; fire = q > .5
        pull = ease(min(1, max(0, (q - .42) / .08))) if q < .85 else 0
        sy = 1010; nx = 300 if not fire else 590
        s.append(f'<rect x="120" y="{sy - 16}" width="520" height="32" rx="10" fill="#a8743f" stroke="{INK}" stroke-width="7"/>')
        s.append(f'<path d="M600,{sy - 170} Q660,{sy} 600,{sy + 170}" stroke="{INK}" stroke-width="22" fill="none" stroke-linecap="round"/><path d="M600,{sy - 170} Q660,{sy} 600,{sy + 170}" stroke="#7a5230" stroke-width="12" fill="none" stroke-linecap="round"/>')
        s.append(f'<path d="M600,{sy - 170} L{nx},{sy - 18} L600,{sy + 170}" stroke="#f2ead2" stroke-width="5" fill="none"/>')
        if not fire: s.append(f'<line x1="{nx}" y1="{sy - 26}" x2="640" y2="{sy - 26}" stroke="{INK}" stroke-width="9"/><line x1="{nx}" y1="{sy - 26}" x2="640" y2="{sy - 26}" stroke="#c9a35a" stroke-width="5"/><polygon points="640,{sy - 36} 670,{sy - 26} 640,{sy - 16}" fill="#b07a3a" stroke="{INK}" stroke-width="4"/>')
        else:
            ax = 640 + (q - .5) / .5 * 900
            if ax < 760: s.append(f'<line x1="{f_(ax - 340)}" y1="{sy - 26}" x2="{f_(ax)}" y2="{sy - 26}" stroke="#c9a35a" stroke-width="6" opacity=".8"/>')
        rot = -28 * pull
        hi = (t > 2.4) and abs(osc(t, 1.2)) > .3
        s.append(f'<g transform="rotate({f_(rot)} 300 {sy + 10})"><path d="M284,{sy - 34} L316,{sy - 34} L322,{sy + 90} Q300,{sy + 110} 278,{sy + 90} Z" fill="{"#ffd400" if hi else "#d4aa3c"}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/></g>')
        if t > 2.4: s.append(f'<text x="300" y="{sy + 170}" font-family="{FONT}" font-weight="800" font-size="38" fill="#ffd400" text-anchor="middle">LẪY ĐỒNG</text>')
        if .5 <= q < .56: s.append(star(600, sy, 60, q * 300)); shake = 5
        g, _ = CH.character('hoctro', 880, 1250, 180, -1, 'surprised' if fire else 'happy', [(.85, .05, 'board', 35)], t=t); s.append(g)
        cam = (1.0, 540, 900)
    elif ty == 'arrow_dig':       # khao co: dao ho, mui ten dong lo ra cang luc cang nhieu
        s.append(sky('#8ab0d0', '#eee2c4', y1=900)); s.append(f'<rect x="-800" y="880" width="2680" height="1400" fill="#b08a58"/>')
        s.append(f'<path d="M-800,880 L1880,880" stroke="{INK}" stroke-width="7"/><ellipse cx="520" cy="1120" rx="380" ry="120" fill="#6e5232" stroke="{INK}" stroke-width="8"/>')
        nshow = int(70 * ease(min(1, t / max(1.5, d * .8)))); rnd = random.Random(11)
        for i in range(70):
            x = 520 + rnd.uniform(-300, 300); y = 1120 + rnd.uniform(-70, 70); a = rnd.uniform(0, 360)
            if i < nshow: s.append(f'<polygon points="{f_(x - 12)},{f_(y + 8)} {f_(x)},{f_(y - 16)} {f_(x + 12)},{f_(y + 8)}" fill="#c9a35a" stroke="{INK}" stroke-width="3" transform="rotate({f_(a)} {f_(x)} {f_(y)})"/>')
        for i in range(3):
            if (t * 2 + i) % 3 < .4: s.append(star(380 + i * 140, 1090 + (i % 2) * 40, 30, t * 200))
        dig = abs(osc(t, .9))
        g, _ = CH.character('hoctro', 940, 1180, 170, -1, 'surprised' if t > d * .5 else 'happy', [(.8, -.2 + .3 * dig, 'shovel', 60 + 30 * dig)], t=t); s.append(g)
        cam = (1.0, 560, 960)
    elif ty == 'citadel':         # thanh Co Loa nhin tu tren: 3 vong thanh xoay, hao nuoc
        s.append('<rect x="-800" y="-400" width="2680" height="2800" fill="#7ea05a"/>')
        for k, (rx, ry) in enumerate(((620, 430), (420, 300), (190, 140))):
            w = 'M' + ' L'.join(f'{f_(540 + rx * math.cos(a / 30 * math.pi) * (1 + .06 * math.sin(a / 5 + k)))},{f_(960 + ry * math.sin(a / 30 * math.pi) * (1 + .06 * math.cos(a / 4 + k)))}' for a in range(61)) + ' Z'
            s.append(f'<path d="{w}" fill="none" stroke="#4b8fc4" stroke-width="44" opacity=".9"/>')
            s.append(f'<path d="{w}" fill="none" stroke="{INK}" stroke-width="30"/><path d="{w}" fill="none" stroke="#a8743f" stroke-width="22"/>')
            for j in range(10):
                a = (j / 10 + t * .02 * (1 if k % 2 else -1)) * 2 * math.pi
                s.append(f'<circle cx="{f_(540 + rx * math.cos(a))}" cy="{f_(960 + ry * math.sin(a))}" r="9" fill="#c4281f" stroke="{INK}" stroke-width="3"/>')
        s.append(f'<rect x="500" y="930" width="80" height="60" fill="#d4aa3c" stroke="{INK}" stroke-width="6"/><path d="M490,930 L540,895 L590,930 Z" fill="#7a1c1a" stroke="{INK}" stroke-width="6"/>')
        cam = (lerp(.92, 1.12, ease(t / d)), 540, 960)
    elif ty == 'claw':            # truyen thuyet: mong rua vang, bi tráo
        s.append('<rect x="-800" y="-400" width="2680" height="2800" fill="#2a2140"/>')
        swap = float(sh.get('swap', 0)) and t > d * float(sh.get('swap'))
        glow = 0 if swap else .5 + .5 * abs(osc(t, .8))
        s.append(f'<circle cx="540" cy="930" r="{f_(260 + 30 * glow)}" fill="#ffd68a" opacity="{f_(.18 * glow)}"/>')
        s.append(f'<ellipse cx="540" cy="1110" rx="220" ry="46" fill="#7a1c1a" stroke="{INK}" stroke-width="7"/>')
        col = '#8a8a90' if swap else '#e8b830'
        s.append(f'<path d="M430,1080 Q440,860 600,800 Q560,900 580,1080 Z" fill="{col}" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/><path d="M470,1060 Q480,920 560,860" stroke="{"#6a6a70" if swap else "#fff3b0"}" stroke-width="8" fill="none"/>')
        if swap: s.append(f'<path d="M520,860 L500,930 L530,960 L505,1040" stroke="{INK}" stroke-width="6" fill="none"/>')
        if sh.get('swap') and abs(t - d * float(sh['swap'])) < .25: flash = .5; shake = 8
        cam = (lerp(1.0, 1.1, ease(t / d)), 540, 960)
    return ''.join(s), cam, shake, flash


SFX_PLAN = {   # (moc giay hoac 'f0.4' = 40% canh, ten, am luong); 'every:x' = lap moi x giay
    'fleet_arrive': [('every:1.5', 'drum', .9)],
    'bait_row': [('every:0.8', 'oar', .6), ('f0.3', 'splash', .5)],
    'melee': [('every:1.1@0.5', 'clash', 1.0), ('every:1.1@0.87', 'clash', .4), ('fall', 'shout', .7), ('fall+0.6', 'splash', 1.0)],
    'crash_stakes': [('f0.45', 'crack', 1.0), ('f0.46', 'thud', 1.0), ('f0.5', 'crack', .9), ('f0.55', 'crack', .7), ('f0.58', 'shout', .7), ('f0.62', 'splash', 1.0), ('f0.75', 'splash', .8), ('f0.9', 'splash', .6)],
    'victory': [(0.05, 'shout', .9), ('every:1.0', 'drum', .8)],
    'tide_board': [],
    'narrator': [],
    'chase': [('every:1.5', 'drum', .7), ('f0.1', 'splash', .5)],
    'ambush': [(0.2, 'shout', .9), ('every:0.5@0.3', 'whoosh', .6), ('every:1.2', 'drum', .8)],
    'prep_stakes': [('every:1.0@0.72', 'thud', .8), ('every:1.0@0.27', 'thud', .7)],
    'general': [('every:0.8', 'oar', .5), ('every:1.4', 'drum', .7)],
    'army_march': [('every:1.2', 'drum', .9)],
    'crossbow_volley': [('every:1.8@0.2', 'whoosh', .9), ('every:1.8@0.25', 'whoosh', .7), ('every:1.8@1.3', 'thud', .6), ('f0.05', 'shout', .7)],
    'trigger_board': [('every:3.2@1.6', 'whoosh', .8), ('every:3.2@1.62', 'thud', .5)],
    'arrow_dig': [('every:1.1@0.3', 'thud', .5)],
    'citadel': [('every:2.0', 'drum', .5)],
    'drill': [('every:2.0@0.3', 'whoosh', .8), ('every:2.0@0.7', 'thud', .7)],
    'claw': [],
}


def sfx_events(sh, t0, d):
    ev = [(t0, 'whoosh', .3)]
    fall_at = float(sh.get('fall_at', max(3.0, d - 2.2)))
    for when, kind, vol in SFX_PLAN.get(sh['type'], []) + [tuple(x) for x in sh.get('sfx', [])]:
        if isinstance(when, (int, float)): ev.append((t0 + when, kind, vol)); continue
        if when.startswith('fall'):
            if sh['type'] == 'melee': ev.append((t0 + fall_at + (float(when[5:]) if '+' in when else 0), kind, vol))
            continue
        if when.startswith('f'): ev.append((t0 + float(when[1:]) * d, kind, vol)); continue
        if when.startswith('every:'):
            per, _, ph = when[6:].partition('@'); per = float(per); ph = float(ph or 0); x = ph
            lim = fall_at if sh['type'] == 'melee' and kind == 'clash' else d
            while x < lim: ev.append((t0 + x, kind, vol)); x += per
    return ev


# ---------------- lop chu (overlay, khong bi camera zoom) ----------------
def header_svg(sp):
    if FMT == 'square': return header_sq(sp)
    ser = esc(sp.get('series', '')); fs = 56 if len(ser) <= 22 else max(40, int(56 * 22 / len(ser)))
    b = esc(sp.get('badge', 'MỔ XẺ CHIẾN THUẬT')); bw = 30 * .72 * len(b) + 50
    return (f'<defs><linearGradient id="hd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#46100e"/><stop offset="1" stop-color="#781f16"/></linearGradient></defs>'
            f'<rect x="0" y="256" width="{W}" height="148" fill="url(#hd)"/><rect x="0" y="404" width="{W}" height="6" fill="#ffd400"/>'
            f'<text x="540" y="{276 + fs}" font-family="{FONT}" font-weight="800" font-size="{fs}" fill="#ffd400" text-anchor="middle" stroke="#111" stroke-width="3" paint-order="stroke">{ser}</text>'
            f'<rect x="{f_(540 - bw / 2)}" y="350" width="{f_(bw)}" height="44" rx="12" fill="#111"/>'
            f'<text x="540" y="383" font-family="{FONT}" font-weight="800" font-size="30" fill="#fff" text-anchor="middle">{b}</text>')


def header_sq(sp):
    """khung vuong theo skill: bang tren cao 120, ten series vang #FFD400 tren nen xanh #0d2a6b, nhan do goc phai."""
    ser = esc(sp.get('series', '')); b = esc(sp.get('badge', 'MỔ XẺ CHIẾN THUẬT'))
    bfs = 26; bw = bfs * .72 * len(b) + 40
    fs = 46
    while fs * .62 * len(ser) > 1080 - bw - 90 and fs > 30: fs -= 2
    return (f'<rect x="0" y="0" width="{W}" height="120" fill="#0d2a6b"/><rect x="0" y="116" width="{W}" height="4" fill="#ffd400"/>'
            f'<text x="40" y="{f_(60 + fs * .36)}" font-family="{FONT}" font-weight="800" font-size="{fs}" fill="#ffd400" stroke="#111" stroke-width="3" paint-order="stroke">{ser}</text>'
            f'<rect x="{f_(1040 - bw)}" y="38" width="{f_(bw)}" height="46" rx="12" fill="#c4281f" stroke="#111" stroke-width="3"/>'
            f'<text x="{f_(1040 - bw / 2)}" y="70" font-family="{FONT}" font-weight="800" font-size="{bfs}" fill="#fff" text-anchor="middle">{b}</text>')


def label_sq(txt, q):
    t = esc(txt.upper()); fs = 56
    while fs * .72 * len(t) + 50 > 960 and fs > 32: fs -= 2
    bw = fs * .72 * len(t) + 50; sc = 1.15 - .15 * min(1, q / .18)
    return (f'<g transform="translate(540 190) scale({f_(sc)}) translate(-540 -190)">'
            f'<rect x="{f_(540 - bw / 2)}" y="142" width="{f_(bw)}" height="{fs + 28}" rx="18" fill="#111" opacity=".85"/>'
            f'<text x="540" y="{f_(142 + fs + 5)}" font-family="{FONT}" font-weight="800" font-size="{fs}" fill="#ffd400" text-anchor="middle">{t}</text></g>')


def label_svg(txt, q):
    if not txt or q <= 0: return ''
    if FMT == 'square': return label_sq(txt, q)
    t = esc(txt.upper()); fs = 62
    while fs * .72 * len(t) + 50 > TW and fs > 36: fs -= 2
    bw = fs * .72 * len(t) + 50; sc = 1.15 - .15 * min(1, q / .18 * 1.0) if q < .18 else 1.0
    return (f'<g transform="translate(540 {f_(470)}) scale({f_(sc)}) translate(-540 -470)">'
            f'<rect x="{f_(540 - bw / 2)}" y="430" width="{f_(bw)}" height="{fs + 30}" rx="18" fill="#111" opacity=".85"/>'
            f'<text x="540" y="{f_(430 + fs + 6)}" font-family="{FONT}" font-weight="800" font-size="{fs}" fill="#ffd400" text-anchor="middle">{t}</text></g>')


JN = '~'   # noi tam cac tu khong duoc tach (ten rieng, so + don vi)


def protect(txt):
    ws = txt.split(); out = []
    for w in ws:
        if out:
            p = out[-1]; last = p.split(JN)[-1]
            cap = lambda x: x[:1].isupper() or x[:1].isdigit()
            name = cap(last) and w[:1].isupper() and not last.endswith(('.', ',', '!', '?', ':', ';', '"', '”'))
            num = re.fullmatch(r'[\d.,%]+', last) is not None and w[:1].islower()
            if (name or num) and len(p) + 1 + len(w) <= 20: out[-1] = p + JN + w; continue
        out.append(w)
    return ' '.join(out)


def chunks(txt, maxc=28):
    """chia cau thanh doan vua 2 dong x 28 ky tu, uu tien cat o dau cau/dau phay; khong tach ten rieng, khong de 1 tu le."""
    txt = protect(txt)
    def fits(t): ls = split_lines(t, maxc); return len(ls) <= 2 and max(len(l) for l in ls) <= maxc + 2
    clauses = [c.strip() for c in re.findall(r'(?:[^.,!?:;]|(?<=\d)[.,:](?=\d))+[.,!?:;]?', txt) if c.strip()]   # 25/11: khong cat trong so (2.000, 7,2, 15:30)
    out, cur = [], ''
    for c in clauses:
        t = (cur + ' ' + c).strip()
        if fits(t): cur = t; continue
        if cur: out.append(cur); cur = ''
        if fits(c): cur = c; continue
        ws = c.split(); piece = []
        for w in ws:
            if fits(' '.join(piece + [w])): piece.append(w)
            else: out.append(' '.join(piece)); piece = [w]
        cur = ' '.join(piece)
    if cur: out.append(cur)
    res = []   # doan chi 1 tu -> gop vao doan truoc (cho phep vuot nhe)
    for c in out:
        if res and len(c.split()) == 1 and len(split_lines(res[-1] + ' ' + c, maxc + 4)) <= 2: res[-1] += ' ' + c
        else: res.append(c)
    return res


def timed_chunks(a, b, txt):
    cs = chunks(txt); tot = sum(len(c) + 4 for c in cs) or 1; t = a; res = []
    for c in cs:
        e = t + (b - a) * (len(c) + 4) / tot; res.append((t, e, c)); t = e
    return res


def split_lines(txt, maxc=28):
    ws = txt.split(); lines, cur = [], ''
    for w in ws:
        if len((cur + ' ' + w).strip()) <= maxc: cur = (cur + ' ' + w).strip()
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    if len(lines) > 2:   # can bang 2 dong
        n = len(ws); best = None
        for k in range(1, n):
            a, b = ' '.join(ws[:k]), ' '.join(ws[k:]); m = max(len(a), len(b))
            if best is None or m < best[0]: best = (m, [a, b])
        lines = best[1]
    if len(lines) == 2:   # uu tien xuong dong ngay sau dau cau/dau phay neu ca 2 dong vua
        best = None
        for k in range(1, len(ws)):
            if ws[k - 1].endswith(('.', ',', '!', '?', ':', ';')):
                a, b = ' '.join(ws[:k]), ' '.join(ws[k:])
                if len(a) <= maxc + 2 and len(b) <= maxc + 2 and (best is None or max(len(a), len(b)) < best[0]): best = (max(len(a), len(b)), [a, b])
        if best: lines = best[1]
    if len(lines) == 2 and len(lines[1].split()) == 1 and len(lines[0].split()) >= 3:   # khong de 1 tu mo coi o dong 2
        a = lines[0].split(); cand = [' '.join(a[:-1]), a[-1] + ' ' + lines[1]]
        if len(cand[1]) <= maxc + 2: lines = cand
    return lines


def sub_top(txt):
    if not txt: return H
    lines = split_lines(txt, 28); fs = 44 if FMT == 'square' else 50
    while max(len(l) for l in lines) * fs * .56 > (900 if FMT == 'square' else TW) and fs > 40: fs -= 2
    bot = 1052 if FMT == 'square' else SAFE[3] - 12
    return bot - fs * 1.3 * len(lines) - 16


def sub_svg(txt, cur=None, tv=None):
    """cur=(a,b,txt), tv: 23/11 chu nhay theo tu: tu da doc sang ro, tu dang doc nhac len + vang, tu chua doc mo 45%."""
    if not txt: return ''
    lines = split_lines(txt, 28); fs = 44 if FMT == 'square' else 50
    while max(len(l) for l in lines) * fs * .56 > (900 if FMT == 'square' else TW) and fs > 40: fs -= 2
    lh = fs * 1.3; bot = 1052 if FMT == 'square' else SAFE[3] - 12; x0, x1 = (60, 1020) if FMT == 'square' else (SAFE[0], SAFE[2]); y0 = bot - lh * len(lines)
    out = [f'<rect x="{x0}" y="{f_(y0 - 16)}" width="{x1 - x0}" height="{f_(lh * len(lines) + 24)}" rx="22" fill="#000" opacity=".62"/>']
    allw = txt.split(); yel_set = set(); start = True
    for i, w in enumerate(allw):
        core = w.strip('.,!?…:;"“”()')
        nxt_cap = i + 1 < len(allw) and allw[i + 1][:1].isupper()
        if re.search(r'\d', core) or (core.isupper() and len(core) > 1) or (core[:1].isupper() and (not start or nxt_cap)): yel_set.add(i)
        start = w.endswith(('.', '!', '?', ':'))
    wt = None; ci = -1
    if cur is not None and tv is not None:
        wt = fx.word_times(allw, cur[0], cur[1]); ci = max([i for i, t0 in enumerate(wt) if t0 <= tv] or [-1])
    wi = 0
    for j, ln in enumerate(lines):
        spans = []
        for k, w in enumerate(ln.split(' ')):
            yel = wi in yel_set; i_ = wi; wi += 1
            if wt is None: spans.append(f'<tspan fill="{"#ffd400" if yel else "#fff"}">{esc(w.replace(JN, " "))}</tspan>'); continue
            if i_ == ci:
                q = max(0.0, min(1.0, (tv - wt[i_]) / .16)); lift = 7 * (1 - q * q)
                spans.append(f'<tspan fill="#ffd400" dy="{f_(-lift)}">{esc(w.replace(JN, " "))}</tspan><tspan dy="{f_(lift)}"></tspan>')
            else:
                op = '1' if i_ < ci else '.45'
                spans.append(f'<tspan fill="{"#ffd400" if yel else "#fff"}" fill-opacity="{op}">{esc(w.replace(JN, " "))}</tspan>')
        out.append(f'<text xml:space="preserve" x="540" y="{f_(y0 + fs + j * lh)}" font-family="{FONT}" font-weight="800" font-size="{fs}" text-anchor="middle" stroke="#111" stroke-width="5" paint-order="stroke">{" ".join(spans)}</text>')
    return ''.join(out)


def hook_svg(txt, q):
    """hook nam o dai tren (thay cho nhan canh), khong de len nhan vat; tu thu nho chu cho vua 2 dong."""
    if not txt or q <= 0: return ''
    hx0, hx1 = (60, 1020) if FMT == 'square' else (SAFE[0] - 30, SAFE[2] + 30)
    top = 138 if FMT == 'square' else 428
    fs = 78
    while True:
        maxc = max(8, int((hx1 - hx0 - 60) / (fs * .66)))
        lines = split_lines(txt.upper(), maxc)
        if (len(lines) <= 2 and max(len(l) for l in lines) <= maxc) or fs <= 44: break
        fs -= 2
    lh = fs * 1.2; hh = lh * len(lines) + 40
    o = [f'<g opacity="{f_(q)}"><rect x="{hx0}" y="{top}" width="{hx1 - hx0}" height="{f_(hh)}" rx="26" fill="#140808" opacity=".92" stroke="#ffd400" stroke-width="6"/>']
    for j_, ln in enumerate(lines): o.append(f'<text x="540" y="{f_(top + 18 + fs + j_ * lh)}" font-family="{FONT}" font-weight="800" font-size="{fs}" fill="#ffd400" text-anchor="middle" stroke="#111" stroke-width="5" paint-order="stroke">{esc(ln)}</text>')
    return ''.join(o) + '</g>'


def tags_svg(tags, z, cx, cy, X0, Y0, top, bot):
    """nhan ten ve tren cung: bo nhan nghieng/nga, nhan vat nho, ngoai khung, trung ten, de len nhau."""
    items = []
    for tg in tags:
        Ds = tg['D'] * z
        if tg['tilt'] > 12 or Ds < 85: continue
        txt = tg['text']; fs = max(22, min(34, Ds * .2)); tw = fs * .68 * len(txt) + 28; th = fs + 14
        sx = X0 + z * (tg['x'] - cx); sy = Y0 + z * (tg['y'] - cy)
        sx = min(max(sx, tw / 2 + 16), W - tw / 2 - 16)
        b = (sx - tw / 2, sy - th, sx + tw / 2, sy)
        if b[1] < top or b[3] > bot: continue
        items.append((Ds, b, txt, fs))
    items.sort(key=lambda it: -it[0]); placed, seen, o = [], set(), []
    for Ds, b, txt, fs in items:
        if txt in seen or any(not (b[2] + 10 < p[0] or p[2] + 10 < b[0] or b[3] + 8 < p[1] or p[3] + 8 < b[1]) for p in placed): continue
        seen.add(txt); placed.append(b); x = (b[0] + b[2]) / 2
        if TAG_STYLE == 'go':
            import rn_chars; o.append(rn_chars.plaque(esc(txt), x, b[3], fs)); continue
        o.append(f'<rect x="{f_(b[0])}" y="{f_(b[1])}" width="{f_(b[2] - b[0])}" height="{f_(b[3] - b[1])}" rx="{f_(fs * .4)}" fill="#111" opacity=".85"/>'
                 f'<text x="{f_(x)}" y="{f_(b[3] - 9)}" font-family="{FONT}" font-weight="800" font-size="{f_(fs)}" fill="#ffd400" text-anchor="middle">{esc(txt)}</text>')
    return ''.join(o)


def end_svg(sp, q):
    if q <= 0: return ''
    nx = split_lines(sp.get('next', ''), 22); o = [f'<rect width="{W}" height="{H}" fill="#120606" opacity="{f_(.88 * q)}"/>']
    if q > .5:
        y = 380 if FMT == 'square' else 700
        for ln in nx: o.append(f'<text x="540" y="{y}" font-family="{FONT}" font-weight="800" font-size="62" fill="#fff" text-anchor="middle">{esc(ln)}</text>'); y += 84
        o.append(f'<rect x="200" y="{y + 30}" width="680" height="100" rx="34" fill="#ffd400"/><text x="540" y="{y + 98}" font-family="{FONT}" font-weight="800" font-size="48" fill="#111" text-anchor="middle">{esc(sp.get("cta", "THEO DÕI KÝ SỬ CHIẾN"))}</text>')
        o.append(f'<text x="540" y="{y + 200}" font-family="{FONT}" font-weight="600" font-size="34" fill="#e6dcd0" text-anchor="middle">Hoạt hình minh hoạ, giản lược</text>')
    return ''.join(o)


# ---------------- dung ----------------
G = {}
TAG_STYLE = 'den'   # 'go' = bien go treo day (nhan vat roi nuoc)


def frame_svg(fi):
    sp, st, ends, D, LEAD, TAIL, subs = G['sp'], G['st'], G['ends'], G['D'], G['LEAD'], G['TAIL'], G['subs']
    tt = fi / FPS; tv = tt - LEAD; n = len(sp['shots'])
    k = max(i for i in range(n) if st[i] <= max(0.0, tv)); sh = sp['shots'][k]; ts = max(0.0, tv - st[k]); dk = ends[k] - st[k]
    CH.TAGS = []
    world, (z, cx, cy), shake, flash = beat(sh, ts, dk)
    if DD:   # 24/11 dao dien: nhieu khung theo tung cau
        if sh['type'] == 'items': world = DD.items_world(sh, ts, dk)
        z, cx, cy = DD.cam(sh, ts, dk, (z, cx, cy))
    tags = CH.TAGS; CH.TAGS = None
    r = random.Random(fi); ox = r.uniform(-shake, shake); oy = r.uniform(-shake, shake)
    Y0 = 600 if FMT == 'square' else 830
    if FMT == 'square': cy = GROUND.get(sh['type'], cy) - 170 / z
    cam = f'translate({f_(540 + ox)} {f_(Y0 + oy)}) scale({f_(z)}) translate({f_(-cx)} {f_(-cy)})'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#2a2a30"/>']
    # 23/11 chuyen canh whip (chi khi doi boi canh): 0.12s cuoi canh cu + 0.16s dau canh moi, nhoe ngang theo huong lao
    TA, TB = .12, .16; wp = None
    if not sp.get('no_whip'):
        nxt = sp['shots'][k + 1] if k + 1 < n else None
        if nxt is not None and nxt['type'] != sh['type'] and st[k + 1] - tv < TA and tt < D - TAIL:
            wp = (k, k + 1, (tv - (st[k + 1] - TA)) / (TA + TB))
        elif k > 0 and sp['shots'][k - 1]['type'] != sh['type'] and ts < TB:
            wp = (k - 1, k, (ts + TA) / (TA + TB))
    if wp is None:
        sc_, sat_ = DD.lat_fx(sh, ts) if DD else (1.0, 1.0)
        if sc_ != 1.0 or sat_ < 1.0:   # 25/11 cu lat: the dap + mat mau roi hoi lai
            o.append(f'<defs><filter id="mono"><feColorMatrix type="saturate" values="{f_(sat_)}"/></filter></defs>'
                     f'<g filter="url(#mono)"><g transform="translate(540 960) scale({f_(sc_)}) translate(-540 -960)"><g transform="{cam}">{world}</g></g></g>')
        else:
            o.append(f'<g transform="{cam}">{world}</g>')
    else:
        a_, b_, p = wp; p = max(0.0, min(1.0, p)); e = p * p * (3 - 2 * p); bl = 2 + 46 * (1 - abs(2 * p - 1)) ** 1.5
        dirn = -1 if (b_ % 2) else 1
        o.append(f'<defs><filter id="mb" x="-20%" y="0" width="140%" height="100%"><feGaussianBlur stdDeviation="{f_(bl)} 0"/></filter>'
                 f'<clipPath id="cw"><rect x="0" y="0" width="{W}" height="{H}"/></clipPath></defs>')
        for kk, off in ((a_, dirn * e * W), (b_, dirn * (e - 1) * W)):
            shk = sp['shots'][kk]; dk_ = ends[kk] - st[kk]; tk = max(0.0, min(dk_, tv - st[kk]))
            CH.TAGS = []; wk, (zk, cxk, cyk), _, _ = beat(shk, tk, dk_); CH.TAGS = None
            if DD:
                if shk['type'] == 'items': wk = DD.items_world(shk, tk, dk_)
                zk, cxk, cyk = DD.cam(shk, tk, dk_, (zk, cxk, cyk))
            if FMT == 'square': cyk = GROUND.get(shk['type'], cyk) - 170 / zk
            camk = f'translate(540 {f_(Y0)}) scale({f_(zk)}) translate({f_(-cxk)} {f_(-cyk)})'   # moi canh bi cat dung khung roi moi truot
            o.append(f'<g filter="url(#mb)"><g transform="translate({f_(off)} 0)"><g clip-path="url(#cw)"><g transform="{camk}">{wk}</g></g></g></g>')
        tags = []
    if DD: o.append(DD.overlay(sh, tt, z, cx, W, H)); o.append(DD.so_svg(sh, ts, W))
    if flash > 0: o.append(f'<rect width="{W}" height="{H}" fill="#fff" opacity="{f_(min(.6, flash))}"/>')   # loe trang DUOI lop chu
    o.append(header_svg(sp))
    hooking = bool(sp.get('hook_text')) and tv < 2.6
    lab_on = (not hooking) and bool(sh.get('label')) and ts < 2.4
    if lab_on: o.append(label_svg(sh.get('label', ''), ts))
    cur = next((s for s in subs if s[0] - .05 <= tv < s[1] + .1), None)
    cur = cur if (cur and tt < D - TAIL) else None
    if not hooking and tt < D - TAIL:
        top = (250 if lab_on else 132) if FMT == 'square' else (540 if lab_on else 420)
        bot = (sub_top(cur[2]) - 8) if cur else H - 20
        o.append(tags_svg(tags, z, cx, cy, 540 + ox, Y0 + oy, top, bot))
    if cur: o.append(sub_svg(cur[2], cur, tv))
    if hooking: o.append(hook_svg(sp.get('hook_text', ''), 1.0 if tv < 2.3 else max(0, 1 - (tv - 2.3) / .3)))
    if tt >= D - TAIL: o.append(end_svg(sp, ease((tt - (D - TAIL)) / .35)))
    o.append('</svg>')
    return ''.join(o)


def render_png(fi):
    svg = frame_svg(fi)
    return subprocess.run(['rsvg-convert', '-f', 'png', '-w', str(W), '-h', str(H)], input=svg.encode(), capture_output=True, check=True).stdout


DD = None   # 24/11 dao dien (editor/dao_dien.py) khi spec.dao_dien = true


def _init(g):
    global FMT, W, H, DD
    G.update(g); FMT = g.get('fmt', 'vertical'); W, H = (1080, 1080) if FMT == 'square' else (1080, 1920)
    if g.get('sp', {}).get('dao_dien', True):   # 25/11 chu chot: dung kieu moi cho moi kenh hoat hinh (CCK, KSC, LT); spec.dao_dien=false de tat
        import dao_dien as DD
        DD.install_bg()
        if g['sp'].get('shots'): g['sp']['shots'][0]['_first'] = True
        if g.get('st'): DD.chuan_bi(g['sp']['shots'], g['st'])
    if g.get('sp', {}).get('engine') == 'vh':   # tien trinh con (forkserver/spawn) khong giu ban va tu main -> nap lai
        import vh_svg; vh_svg.install(sys.modules[__name__])
    if g.get('sp', {}).get('chars') == 'roinuoc':
        import rn_chars; rn_chars.install(sys.modules[__name__], g['sp'].get('cast'))


TRIM = ('silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.04,areverse,'
        'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,areverse')


def pause_after(sh):
    """nghi sau moi cau: ~0.35s; sau cau hoi ~0.6s; + gap rieng cua canh (nhip bat nghi)."""
    # quy tac ngat nghi v2 (chu chot 21/11, giong W87): cau hoi 0.85, bo lung 0.35, cau ngan <=6 tu 0.6, con lai 0.45
    say = (sh.get('say') or '').strip().rstrip('"”\'')
    if say.endswith('?'): d = 0.85
    elif say.endswith('...') or say.endswith('…'): d = 0.35
    elif len(say.split()) <= 6: d = 0.6
    else: d = 0.45
    base = float(sh.get('pause', d))
    return base + float(sh.get('gap', 0))


SENT = {}   # moc tung cau trong canh: {canh: [(bat_dau, ket_thuc, chu)]}
W87 = os.environ.get('AVF_TTS_URL', '')   # dia chi that nam trong GitHub Secrets, khong ghi vao code


def bo_ky_hieu(s):
    """bo ky hieu ngat nghi khoi phu de: ' / ', ' // ', ' /// ', [nghỉ x], {chậm: ...} -> chi giu chu."""
    s = re.sub(r'\[nghỉ\s*[\d.,]+\s*\]', ' ', s)
    s = re.sub(r'\{(?:chậm|rất chậm|nhấn|hạ|nhanh|cao)\s*:\s*', '', s, flags=re.I).replace('}', '')
    s = re.sub(r'(^|\s)/{1,3}(?=\s|$)', ' ', s)
    return re.sub(r'\s+', ' ', s).replace(' ,', ',').replace(' .', '.').strip()


def tts_shots(sp):
    import urllib.request
    from multiprocessing.pool import ThreadPool
    def one(i):
        sh = sp['shots'][i]; src = sh.get('tts') or sh['say']
        # 24/11: ky hieu ngat nghi (skill giong-doc-ngat-nghi) -> W87 v3. Giu nguyen [nghỉ x] khi doi so -> chu.
        txt = ''.join(x if re.fullmatch(r'\[nghỉ\s*[\d.,]+\s*\]', x) else doc_so.doc_tts(x) for x in re.split(r'(\[nghỉ\s*[\d.,]+\s*\])', src))
        body = json.dumps({'text': txt, 'speed': sp.get('speed', 1.0), 'tag': f"{sp.get('tag', 'ksc')}-{i}"}).encode()
        for k in range(3):
            try:
                req = urllib.request.Request(W87, data=body, headers={'Content-Type': 'application/json', 'X-AVF-Key': os.environ.get('AVF_KEY', '')})
                with urllib.request.urlopen(req, timeout=900) as r: j = json.loads(r.read())
                if j.get('ok'):
                    for u in j['voice_urls']: print('::add-mask::' + u, flush=True)   # che link file giong khoi nhat ky
                    tx = j.get('texts') or [''] * len(j['voice_urls'])
                    se_ = j.get('sents') or list(range(len(j['voice_urls'])))   # cau cua tung cum (W87 v3)
                    return [[u, p, t_, s_] for u, p, t_, s_ in zip(j['voice_urls'], j['pauses'], tx, se_)]
                print('giong loi canh', i)
            except Exception as ex: print('giong that bai canh', i, k, type(ex).__name__)
        sys.exit(f'khong co giong canh {i}')
    with ThreadPool(4) as tp: return tp.map(one, range(len(sp['shots'])))


def main():
    inp = json.loads(os.environ['SPEC_JSON'])
    if 'shots' in inp: sp = inp
    else:
        br, dd = inp['branch'], inp['dir'].strip('/')
        subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
        subprocess.run(['git', 'checkout', 'FETCH_HEAD', '--', dd], check=True)
        sp = json.load(open(os.path.join(ROOT, dd, 'spec.json'), encoding='utf-8'))
    if sp.get('engine') == 'vh':   # bo canh van hoc (lang que, gia dinh, so do) – editor/vh_svg.py
        import vh_svg; vh_svg.install(sys.modules[__name__])
    if sp.get('chars') == 'roinuoc':   # nhan vat roi nuoc son son (dau an AVF tu 22/11) – editor/rn_chars.py
        import rn_chars; rn_chars.install(sys.modules[__name__], sp.get('cast'))
    def _cd(o):   # chuan chinh ta moi chu hien tren hinh (hòa, tòa, thủy...)
        if isinstance(o, dict): return {k: (v if 'url' in k else _cd(v)) for k, v in o.items()}
        if isinstance(o, list): return [_cd(x) for x in o]
        return doc_so.chuan_dau(o) if isinstance(o, str) else o
    sp['shots'] = _cd(sp['shots'])
    for sh_ in sp['shots']:   # 23/11: giong doc dung ban chu (tts), phu de dung ban SO (2026, 59.000, 19:20)
        if sh_.get('say'):
            if not sh_.get('tts'): sh_['tts'] = sh_['say']
            sh_['say'] = doc_so.chu_so(bo_ky_hieu(sh_['say']))
    for k_ in ('series', 'badge', 'hook_text', 'next', 'cta'):
        if isinstance(sp.get(k_), str): sp[k_] = doc_so.chuan_dau(sp[k_])
    shots = sp['shots']; n = len(shots); voice = None; srt = []
    if not sp.get('voice_urls') and sp.get('tts'):   # tu goi W87 cho tung canh (giong Nhat Khoa, ngat nghi theo cau)
        sp['voice_urls'] = tts_shots(sp)
    urls = sp.get('voice_urls') or []
    if urls:
        parts, off = [], 0.0
        for i, u in enumerate(urls):
            wv = os.path.join(OUT, f'vp{i}.wav'); pa = pause_after(shots[i] if len(urls) == n else {})
            if isinstance(u, (list, tuple)):
                # canh nhieu cau (W87): [[url, pause], ...] -> moi cau doc lien, nghi dung pause giua cau (chu chot 21/11)
                subs_ = []; cur = 0.0; sent = []
                for k, it in enumerate(u):
                    uu, pz = it[0], it[1]; tx = it[2] if len(it) > 2 else ''; sx = it[3] if len(it) > 3 else k
                    pk = get(uu, os.path.join(OUT, f'vp{i}_{k}.mp3')); wk = os.path.join(OUT, f'vp{i}_{k}.wav')
                    pad = pa if k == len(u) - 1 else max(0.0, float(pz or .45) - 0.1)
                    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', pk, '-ar', str(SR), '-ac', '2', '-af', TRIM + ',apad=pad_dur=%.2f' % pad, wk]); subs_.append(wk)
                    dk = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wk]).decode().strip())
                    sent.append((cur, cur + max(.2, dk - pad), tx, sx)); cur += dk   # moc noi that cua tung cum (khong tinh khoang nghi)
                g_ = {}   # gop cac cum cung 1 cau -> 1 moc cau (phu de / dao dien theo cau)
                for a_, b_, t_, s_ in sent:
                    if s_ in g_: g_[s_] = (g_[s_][0], b_, g_[s_][2] + ' ' + t_)
                    else: g_[s_] = (a_, b_, t_)
                SENT[i] = [g_[k_] for k_ in sorted(g_)]
                l2 = os.path.join(OUT, f'vl{i}.txt'); open(l2, 'w').write(''.join(f"file '{x}'\n" for x in subs_))
                subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', l2, '-c', 'copy', wv])
            else:
                pth = u if os.path.exists(u) else get(u, os.path.join(OUT, f'vp{i}.mp3'))
                subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', pth, '-ar', str(SR), '-ac', '2', '-af', TRIM + ',apad=pad_dur=%.2f' % pa, wv])
            dd_ = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wv]).decode().strip())
            su = (sp.get('srt_urls') or [''] * len(urls))[i]
            if su:
                txt = open(su if os.path.exists(su) else get(su, os.path.join(OUT, f'vp{i}.srt')), encoding='utf-8').read()
                srt += [(a + off, b + off, tx) for a, b, tx in parse_srt(txt)]
            parts.append(wv); off += dd_
        lst = os.path.join(OUT, 'vl.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
        voice = os.path.join(OUT, 'voice.wav'); subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice]); dur = off
        if len(urls) == n:   # 1 cau = 1 canh = 1 file giong (skill: mot cau thoai mot canh)
            st = []; acc = 0.0
            for wv in parts:
                st.append(acc); acc += float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wv]).decode().strip())
            subs = []
            for k in range(n):
                se = SENT.get(k) or []
                txts = [x[2] for x in se]
                if se:   # 23/11: phu de LUON lay chu tu 'say' (so viet bang chu so, ten goc), KHONG lay chu W87 tra ve (da doi so -> chu, phien am)
                    say_k = re.sub(r'\[\[(.+?)\]\]', r'\1', shots[k].get('say', ''))
                    parts_ = [x.strip() for x in re.findall(r'.+?(?:[.!?…]+(?=\s|$)|$)', say_k) if x.strip()]
                    if len(parts_) == len(se): se = [(a, b, t_) for (a, b, _), t_ in zip(se, parts_)]
                    else: se = [(se[0][0], se[-1][1], say_k)]   # lech so cau: ca canh 1 khoi, van dung chu 'say'
                if se:   # phu de theo DUNG tung cau: chu hien khi cau bat dau, het khi cau doc xong (22/11: anh/chu chay truoc loi)
                    shots[k]['_sent'] = [a for a, b, t_ in se]
                    for a, b, t_ in se: subs += timed_chunks(st[k] + a, st[k] + b, t_)
                else:
                    subs += timed_chunks(st[k], (st[k + 1] if k + 1 < n else dur) - .08, shots[k].get('say', ''))
            subs.sort(key=lambda c: c[0])
            for j in range(len(subs) - 1):   # giu chu qua khoang nghi ngan giua 2 cau, tranh nhap nhay
                if subs[j + 1][0] - subs[j][1] < .7: subs[j] = (subs[j][0], subs[j + 1][0] - .02, subs[j][2])
        else:
            st = scene_starts(sp, srt, n, dur); subs = srt
    else:
        durs = sp.get('durs') or [5.0] * n; st = [sum(durs[:k]) for k in range(n)]; dur = sum(durs)
        subs = [c for k in range(n) for c in timed_chunks(st[k], st[k] + durs[k] - .15, shots[k].get('say', ''))]
    LEAD, TAIL = .1, 2.6; D = dur + LEAD + TAIL; ends = st[1:] + [dur + TAIL]
    g = dict(sp=sp, st=st, ends=ends, D=D, LEAD=LEAD, TAIL=TAIL, subs=subs, fmt=sp.get('format', 'square'))
    _init(g)
    nfr = int(D * FPS)
    if os.environ.get('FRAMES_AT'):   # 23/11: ve dung cac moc giay (vd "10.8,10.9") de soat chuyen canh
        for j, x in enumerate(os.environ['FRAMES_AT'].split(',')):
            open(os.path.join(OUT, f'at_{j:02d}.png'), 'wb').write(render_png(min(int(float(x) * FPS), nfr - 1)))
        print('frames ok'); return
    if os.environ.get('BOARD'):   # bang khung hinh: moi canh 1 khung o moc 75%
        for k in range(n):
            fi = int((LEAD + st[k] + float(os.environ.get('BOARD_AT', '.75')) * (ends[k] - st[k])) * FPS)
            open(os.path.join(OUT, f'board_{k}.png'), 'wb').write(render_png(min(fi, nfr - 1)))
        print('board ok'); return
    raw = os.path.join(OUT, 'v_tmp.mp4')
    pr = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-'] + (['-vf', fx.grade_vf(sp.get('grade', 'rn'))] if fx.grade_vf(sp.get('grade', 'rn')) else []) + ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    import multiprocessing as _mp
    ctx = _mp.get_context('fork') if 'fork' in _mp.get_all_start_methods() else _mp   # Python 3.14 mac dinh forkserver -> mat ban va beat()
    with ctx.Pool(int(os.environ.get('NPROC', '2')), initializer=_init, initargs=(g,)) as pool:
        for png in pool.imap(render_png, range(nfr), chunksize=8): pr.stdin.write(png)
    pr.stdin.close(); pr.wait()
    if pr.returncode != 0: sys.exit('ffmpeg loi')
    ev = []
    for k, sh in enumerate(shots): ev += sfx_events(sh, LEAD + st[k], ends[k] - st[k])
    sw = mix_audio(ev, D, path=os.path.join(OUT, 'sfx.wav'))
    mus = os.path.join(ROOT, 'editor', 'story', sp.get('music', 'music_b.mp3')); tmp = os.path.join(OUT, 'out.tmp.mp4')
    if voice:
        fc = (f'[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2[vx];'
              '[vx]asplit=2[v][vk];[2:a]volume=0.6[s];[3:a]volume=0.13[m0];[m0][vk]sidechaincompress=threshold=0.03:ratio=8:attack=25:release=450[m];'   # 23/11: nhac tu ha khi co loi, len lai khi nghi
              '[v][s][m]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5[a]')
        ins = ['-i', voice, '-i', sw, '-stream_loop', '-1', '-i', mus]
    else:
        fc = '[1:a]volume=1.0[s];[2:a]volume=0.10[m];[s][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
        ins = ['-i', sw, '-stream_loop', '-1', '-i', mus]
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw] + ins + ['-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    print('ok', round(D, 2), 'frames', nfr, 'sfx', len(ev))


if __name__ == '__main__':
    main()
