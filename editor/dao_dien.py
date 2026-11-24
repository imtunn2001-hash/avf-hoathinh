"""DAO DIEN (24/11): tach moi canh thanh nhieu khung theo tung cau doc, de video khong con giong anh tinh.

Chu chot 24/11: "hinh anh con xo xai, it anh qua, giong anh tinh". Truoc day 1 canh ~10-12 giay chi 1 khung hinh dung yen.
Bay gio (spec.dao_dien = true):
- Moi cau = it nhat 1 khung; cau dai > TACH giay thi tach doi. Moi khung 1 kieu may quay khac nhau:
  toan canh / trung canh / can mat nhan vat / can vat chung (icon, the chu, vat trong bang) dung luc vat do hien ra.
- Trong moi khung: may quay day nhe vao + troi ngang (khong bao gio dung yen).
- Lop khong khi tren man hinh: bui sang troi, vien toi (vignette), tien canh mo (bokeh) troi nguoc may quay -> co chieu sau.
Chi doi MAY QUAY + them lop phu, khong dung vao noi dung canh -> ap duoc cho moi tap cu/moi dung bian_svg/vh_svg.
"""
import math
import random

GY = 1250
SCALE = .8       # = vh_svg.SCALE (nhan vat ve nho lai)
TACH = 4.2       # cau dai hon -> 2 khung
CAMDEF = (1.0, 540, 900)


def _f(v): return f'{v:.1f}'


def _ease(q): q = max(0.0, min(1.0, q)); return q * q * (3 - 2 * q)


def _at(sh, i, default):
    se = sh.get('_sent') or []
    return se[i] if 0 <= i < len(se) else default


def _items_pos(it):
    cols = 2 if len(it) > 3 else 1; o = []
    for k in range(len(it)):
        cx = (300 + 480 * (k % 2)) if cols == 2 else 540; cy = 700 + (k // cols) * 210 if cols == 2 else 700 + k * 200
        o.append((cx, cy - 10))
    return o


def targets(sh):
    """diem dang nhin trong canh: dict(x, y, z, at, kind). at = so cau ma vat/nguoi do xuat hien."""
    ty = sh.get('type'); T = []
    if ty == 'stage':
        for c in sh.get('cast', []):
            D = c.get('D', 160) * SCALE; y = c.get('y', GY + 40); x = c.get('x', 540); a = int(c.get('at', 0) or 0)
            T.append(dict(x=x, y=y - 1.45 * D, z=1.85, at=a, kind='mat'))
            T.append(dict(x=x, y=y - .95 * D, z=1.35, at=a, kind='nguoi'))
        for ic in sh.get('icons', []):
            T.append(dict(x=ic.get('x', 540), y=ic.get('y', 760), z=1.75, at=int(ic.get('at', 0)), kind='vat'))
        for k, cd in enumerate(sh.get('cards', [])):
            T.append(dict(x=cd.get('x', 540), y=cd.get('y', 760) + 40, z=1.5, at=int(cd.get('at', k)), kind='the'))
    elif ty == 'items':
        pass   # bang vat chung ve lai bang items_world(): vat moi hien TO giua man hinh, vat cu thu nho xuong hang duoi
    elif ty == 'board':
        pos = sh.get('pos') or [(270, 720), (810, 720), (540, 960), (270, 1180), (810, 1180), (540, 1200)]
        ats = sh.get('at') or list(range(len(sh.get('cards', []))))
        for k in range(len(sh.get('cards', []))):
            T.append(dict(x=pos[k][0], y=pos[k][1], z=1.3, at=int(ats[k]), kind='the'))
    elif ty == 'timeline':
        pts = sh.get('points', []); n = max(1, len(pts))
        for k, p in enumerate(pts):
            x = 160 + (760 * k / max(1, n - 1) if n > 1 else 380)
            T.append(dict(x=min(max(x, 330), 750), y=960, z=1.55, at=int(p.get('at', k)), kind='vat'))
    elif ty == 'petition':
        T.append(dict(x=640, y=GY - 260, z=1.6, at=0, kind='vat'))
        if sh.get('who'): T.append(dict(x=270, y=GY + 40 - 1.45 * sh.get('D', 165) * SCALE, z=1.8, at=0, kind='mat'))
    elif ty == 'ke':
        T.append(dict(x=360, y=860, z=1.45, at=0, kind='the'))
        T.append(dict(x=800, y=GY - 1.45 * 175 * SCALE, z=1.75, at=0, kind='mat'))
    elif ty == 'beach' and sh.get('who'):
        T.append(dict(x=560, y=GY + 40 - 1.45 * sh.get('D', 160) * SCALE, z=1.8, at=0, kind='mat'))
    return T


def plan(sh, d):
    """danh sach khung [(bat_dau, ket_thuc, (z, cx, cy) | None)] cho 1 canh. None = giu may quay goc cua canh (toan canh)."""
    key = '_dd_plan'
    if sh.get(key) and abs(sh[key][0] - d) < 1e-6: return sh[key][1]
    se = list(sh.get('_sent') or [0.0]); js = list(range(len(se)))
    if se[0] <= .6: se[0] = 0.0
    else: se = [0.0] + se; js = [-1] + js          # doan truoc cau dau: toan canh
    segs = []
    for jj, a in enumerate(se):
        b = se[jj + 1] if jj + 1 < len(se) else d; j = js[jj]
        if b - a > TACH * 1.6:
            n = 3 if b - a > TACH * 2.6 else 2
            for m in range(n): segs.append((a + (b - a) * m / n, a + (b - a) * (m + 1) / n, j, m))
        elif b - a > TACH: segs.append((a, (a + b) / 2, j, 0)); segs.append(((a + b) / 2, b, j, 1))
        else: segs.append((a, b, j, 0))
    T = targets(sh)
    r = random.Random(sum(map(ord, sh.get('say', '')[:40])) + len(T))
    out, prev, used = [], 'goc', {}
    for i, (a, b, j, m) in enumerate(segs):
        pick = None
        if i == 0 and sh.get('_first'): pick = None                 # canh hook: giu nguyen bo cuc + chu hook
        elif m == 0:
            new = [t for t in T if t['at'] == j and j > 0]          # vat/nguoi vua xuat hien o cau nay -> can no
            if new: pick = new[used.get('new', 0) % len(new)]; used['new'] = used.get('new', 0) + 1
        if pick is None and not (i == 0 and sh.get('_first')):
            pool = [t for t in T if t['at'] <= j]
            if i == 0: pool = []                                    # khung dau canh: toan canh de nguoi xem biet dang o dau
            elif prev == 'goc' and pool: pass
            elif prev != 'goc' and (i % 3 == 2 or not pool): pool = []
            if pool:
                kinds = [t for t in pool if t['kind'] != prev] or pool
                pick = kinds[(i + r.randint(0, 3)) % len(kinds)]
        if pick is None: out.append((a, b, None)); prev = 'goc'
        else: out.append((a, b, (pick['z'], pick['x'], pick['y']))); prev = pick['kind']
    sh[key] = (d, out)
    return out


def cam(sh, t, d, base):
    """may quay cho thoi diem t trong canh: khung theo cau + day/troi nhe trong khung."""
    z0, cx0, cy0 = base
    p = plan(sh, d)
    seg = p[-1]
    for s in p:
        if s[0] <= t < s[1]: seg = s; break
    a, b, tg = seg; q = _ease((t - a) / max(.5, b - a)); k = p.index(seg)
    dirn = 1 if k % 2 == 0 else -1
    if tg is None:   # toan canh: giu may goc + day vao 6% + troi ngang
        if sh.get('type') == 'stage' and sh.get('cast'):   # toan canh nhung om lay nhan vat (khong de khung trong)
            xs = [c.get('x', 540) for c in sh['cast']] + [ic.get('x', 540) for ic in sh.get('icons', [])]
            cx0 = (540 + sum(xs) / len(xs)) / 2; z0 = max(z0, 1.15); cy0 = 960
        return (z0 * (1.0 + .06 * q), cx0 + dirn * 22 * (q - .5), cy0 - 10 * q)
    z, x, y = tg
    z = max(z0, z) * (0.97 + .07 * q)
    x = x + dirn * 18 * (q - .5)
    x = min(max(x, 540 / z - 60), 1080 - 540 / z + 60)   # khong lo mep qua xa
    return (z, x, y - 8 * q)


# ---------------- lop khong khi (toa do man hinh) ----------------
NIGHT = ('village_night', 'riverbank', 'night', 'prison', 'alley', 'hall_dim')


def overlay(sh, tt, z, cx, W=1080, H=1920):
    o = []
    bg = sh.get('bg', '') if sh.get('type') == 'stage' else sh.get('type')
    night = bg in NIGHT or sh.get('night')
    # tien canh mo: 2 mang toi lon o 2 goc duoi, troi NGUOC may quay -> chieu sau (khong ap cho canh giay/bang)
    if sh.get('type') in ('stage', 'beach', 'petition', 'ke') and not sh.get('no_fg'):
        px = -(cx - 540) * .55 * z
        col = '#0b0d14' if night else '#2a2016'
        o.append('<defs><filter id="ddfg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="26"/></filter></defs>')
        o.append(f'<g filter="url(#ddfg)" opacity="{.55 if night else .32}">'
                 f'<ellipse cx="{_f(-40 + px)}" cy="{H - 300}" rx="230" ry="420" fill="{col}"/>'
                 f'<ellipse cx="{_f(W + 60 + px)}" cy="{H - 220}" rx="200" ry="360" fill="{col}"/></g>')
    # bui sang troi cham (lop rat nhe, luon chuyen dong)
    r = random.Random(7); dots = []
    for i in range(22):
        x0 = r.uniform(0, W); y0 = r.uniform(250, 1500); sp = r.uniform(6, 16); ph = r.uniform(0, 6.28); rr = r.uniform(2, 5)
        x = (x0 + math.sin(tt * .35 + ph) * 30 - (cx - 540) * .25) % W; y = (y0 - tt * sp) % 1300 + 220
        dots.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(rr)}" fill="{"#ffe9b0" if not night else "#cfe0ff"}" opacity="{_f(.18 + .14 * math.sin(tt * 1.3 + ph))}"/>')
    o.append(''.join(dots))
    # vien toi
    o.append('<defs><radialGradient id="ddvg" cx="50%" cy="46%" r="72%"><stop offset=".62" stop-color="#000" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="{.5 if night else .32}"/></radialGradient></defs>'
             f'<rect width="{W}" height="{H}" fill="url(#ddvg)"/>')
    return ''.join(o)


# ---------------- bang vat chung kieu "can tung mon" ----------------
def items_world(sh, t, d):
    """thay canh items: nhom vat vua duoc nhac hien TO o giua (can canh), cac vat da nhac thu nho thanh hang o duoi.
    Cau cuoi khong co vat moi -> toan bang nhu cu (nguoi xem nhin lai ca bo)."""
    import bian_svg as B
    import vh_svg as V
    it = sh.get('items', [])
    ats = [V.at(sh, int(x.get('at', k)), .3 + k * 1.2) for k, x in enumerate(it)]
    se = sh.get('_sent') or []
    # nhieu vat cung 1 cau -> hien LAN LUOT tung mon (moi mon ~1 giay) thay vi 3 mon nho cung luc
    g0 = sorted(set(ats)); bounds = sorted(set(se + [d]))
    for g in g0:
        ks = [k for k in range(len(it)) if ats[k] == g]
        if len(ks) < 2: continue
        nb = min([b for b in bounds if b > g + .3] + [d]); slot = max(.8, min(1.6, (nb - g) / len(ks)))
        for j, k in enumerate(ks): ats[k] = g + j * slot
    grp = sorted(set(ats))
    shown = [g for g in grp if t >= g]
    o = [B.paper()]
    if not shown: return ''.join(o)
    last_new = max(grp); tail = se[-1] if se else d
    if len(se) > 1 and tail > last_new + .3 and t >= tail:   # tong ket: ca bang
        q = _ease((t - tail) / .4)
        for k, x in enumerate(it):
            cx, cy = _items_pos(it)[k]
            inner = B.icon(x.get('icon', 'paper'), cx, cy - 10, .9) + f'<text x="{cx}" y="{cy + 85}" font-family="{V.FONT}" font-weight="900" font-size="34" fill="#5a1a14" text-anchor="middle">{V.esc(x.get("t", ""))}</text>'
            if x.get('x'): inner += f'<path d="M{cx - 80},{cy - 70} L{cx + 80},{cy + 50}" stroke="#c4281f" stroke-width="12" stroke-linecap="round"/>'
            o.append(f'<g opacity="{_f(q)}">{inner}</g>')
        return ''.join(o)
    cur = shown[-1]; old = [k for k in range(len(it)) if ats[k] < cur]; now = [k for k in range(len(it)) if ats[k] == cur]
    qn = (t - cur) / .4
    # hang vat cu (thu nho) o duoi
    n_old = len(old)
    for j, k in enumerate(old):
        x = it[k]; tx = 540 + (j - (n_old - 1) / 2) * 230; ty = 1235
        q = _ease(qn)   # vua co vat moi -> vat cu truot xuong
        sc = .55 + .35 * (1 - q)
        inner = B.icon(x.get('icon', 'paper'), tx, ty, sc)
        if x.get('x'): inner += f'<path d="M{_f(tx - 60 * sc)},{_f(ty - 60 * sc)} L{_f(tx + 60 * sc)},{_f(ty + 50 * sc)}" stroke="#c4281f" stroke-width="9" stroke-linecap="round"/>'
        o.append(f'<g opacity=".85">{inner}</g>')
    # nhom vat moi: to giua man hinh
    m = len(now); big = 1.9 if m == 1 else (1.35 if m == 2 else 1.05)
    for j, k in enumerate(now):
        x = it[k]; cx = 540 + (j - (m - 1) / 2) * (420 if m == 2 else 300); cy = 820
        lab = x.get('t', ''); fs = 54 if m == 1 else (40 if m == 2 else 32)
        inner = (f'<ellipse cx="{cx}" cy="{cy + 150 * big / 1.9}" rx="{_f(150 * big / 1.9)}" ry="{_f(26 * big / 1.9)}" fill="#000" opacity=".12"/>'
                 + B.icon(x.get('icon', 'paper'), cx, cy, big)
                 + f'<text x="{cx}" y="{_f(cy + 115 * big / 1.9 + 70)}" font-family="{V.FONT}" font-weight="900" font-size="{fs}" fill="#5a1a14" text-anchor="middle">{V.esc(lab)}</text>')
        if x.get('x'):
            qx = _ease((t - cur - .55) / .3)
            if qx > 0: inner += f'<path d="M{_f(cx - 110 * big / 1.9)},{_f(cy - 100 * big / 1.9)} L{_f(cx - 110 * big / 1.9 + 220 * big / 1.9 * qx)},{_f(cy - 100 * big / 1.9 + 180 * big / 1.9 * qx)}" stroke="#c4281f" stroke-width="16" stroke-linecap="round"/>'
        o.append(B.pop(cx, cy, qn, inner))
    return ''.join(o)


# ---------------- them do dac + chuyen dong cho nen (chi khi bat dao dien) ----------------
INK = '#111'


def _swing_lamp(t, x=540, y0=380, L=340, night=False):
    a = 5 * math.sin(t * 1.1); r = math.radians(a); bx = x + L * math.sin(r); by = y0 + L * math.cos(r)
    fl = 1 + .05 * math.sin(t * 17) * (1 if night else 0)
    return (f'<path d="M{bx - 300 * math.cos(r) - 40:.1f},{GY + 20} L{bx:.1f},{by:.1f} L{bx + 300 * math.cos(r) + 40:.1f},{GY + 20} Z" fill="#fff1b8" opacity="{.16 * fl:.2f}"/>'
            f'<path d="M{x},{y0} L{bx:.1f},{by - 24:.1f}" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M{bx - 34:.1f},{by:.1f} Q{bx:.1f},{by - 50:.1f} {bx + 34:.1f},{by:.1f} Z" fill="#4a4a3a" stroke="{INK}" stroke-width="5"/>'
            f'<circle cx="{bx:.1f}" cy="{by + 10:.1f}" r="15" fill="#ffe28a" stroke="{INK}" stroke-width="4"/>')


def room_extra(t):
    o = []
    # cua so + rem lay dong
    o.append(f'<rect x="760" y="620" width="230" height="250" fill="#2a3458" stroke="{INK}" stroke-width="8"/>'
             f'<circle cx="930" cy="680" r="24" fill="#f6efd0"/><path d="M875,620 L875,870 M760,745 L990,745" stroke="{INK}" stroke-width="6"/>')
    sw = 8 * math.sin(t * .9)
    o.append(f'<path d="M740,600 Q{790 + sw:.1f},740 760,900 L800,900 Q{810 + sw:.1f},740 790,600 Z" fill="#a8563a" stroke="{INK}" stroke-width="5"/>'
             f'<path d="M1010,600 Q{960 - sw:.1f},740 990,900 L950,900 Q{940 - sw:.1f},740 960,600 Z" fill="#a8563a" stroke="{INK}" stroke-width="5"/>')
    # lich treo tuong + ke go co lo lo
    o.append(f'<rect x="110" y="640" width="130" height="160" fill="#f6f2e8" stroke="{INK}" stroke-width="6"/><rect x="110" y="640" width="130" height="44" fill="#c4281f" stroke="{INK}" stroke-width="6"/>'
             f'<text x="175" y="770" font-family="Be Vietnam Pro, Inter" font-weight="900" font-size="64" fill="#222" text-anchor="middle">1991</text>'.replace('1991', '15'))
    o.append(f'<rect x="60" y="930" width="300" height="18" fill="#8a5a2a" stroke="{INK}" stroke-width="5"/>'
             f'<rect x="85" y="870" width="46" height="60" rx="8" fill="#6a8a9a" stroke="{INK}" stroke-width="5"/><rect x="150" y="880" width="40" height="50" rx="6" fill="#d8a93a" stroke="{INK}" stroke-width="5"/>'
             f'<rect x="210" y="860" width="30" height="70" fill="#7a3a2a" stroke="{INK}" stroke-width="5"/><rect x="245" y="866" width="26" height="64" fill="#3a5a4a" stroke="{INK}" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="{GY - 70}" width="2880" height="30" fill="#7a5a3a" stroke="{INK}" stroke-width="5"/>')   # chan tuong
    o.append(_swing_lamp(t))
    return ''.join(o)


def beach_extra(t):
    o = []
    for k, (x0, y, sp) in enumerate([(100, 430, 14), (700, 520, 9), (1300, 380, 11)]):   # may troi
        x = (x0 + t * sp) % 2200 - 500
        o.append(f'<g opacity=".9"><ellipse cx="{x:.1f}" cy="{y}" rx="90" ry="30" fill="#fff"/><ellipse cx="{x + 50:.1f}" cy="{y - 18}" rx="60" ry="30" fill="#fff"/><ellipse cx="{x - 50:.1f}" cy="{y - 8}" rx="50" ry="24" fill="#fff"/></g>')
    for k in range(3):   # chim hai au vo canh
        x = (200 + k * 260 + t * (40 + k * 8)) % 1700 - 300; y = 560 + k * 40 + 10 * math.sin(t * 1.5 + k)
        w = 18 * math.sin(t * 9 + k * 2)
        o.append(f'<path d="M{x - 26:.1f},{y - w:.1f} Q{x - 12:.1f},{y - 6:.1f} {x:.1f},{y:.1f} Q{x + 12:.1f},{y - 6:.1f} {x + 26:.1f},{y - w:.1f}" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    for x, s_ in ((-60, 1.0), (1140, .9)):   # cay bang dua nhe
        a = 2.5 * math.sin(t * .8 + x)
        o.append(f'<g transform="rotate({a:.2f} {x} {GY})"><path d="M{x - 18},{GY} L{x - 10},{GY - 420 * s_:.0f} L{x + 10},{GY - 420 * s_:.0f} L{x + 18},{GY} Z" fill="#6a4a2a" stroke="{INK}" stroke-width="6"/>'
                 f'<ellipse cx="{x}" cy="{GY - 470 * s_:.0f}" rx="{170 * s_:.0f}" ry="{90 * s_:.0f}" fill="#4f8a3a" stroke="{INK}" stroke-width="6"/>'
                 f'<ellipse cx="{x + 60}" cy="{GY - 520 * s_:.0f}" rx="{110 * s_:.0f}" ry="{60 * s_:.0f}" fill="#5f9a46" stroke="{INK}" stroke-width="5"/></g>')
    return ''.join(o)


def village_extra(t):
    o = []
    for k in range(6):   # khoi bep bay len tu mai nha
        q = ((t * .35 + k / 6) % 1.0); x = 980 + 30 * math.sin(q * 6 + k) + q * 40; y = 900 - q * 380
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{14 + q * 46:.1f}" fill="#e8e4da" opacity="{.6 * (1 - q):.2f}"/>')
    for k in range(4):
        x = (t * (55 + k * 9) + k * 300) % 1700 - 300; y = 500 + k * 30 + 8 * math.sin(t * 2 + k); w = 14 * math.sin(t * 10 + k)
        o.append(f'<path d="M{x - 20:.1f},{y - w:.1f} Q{x - 9:.1f},{y - 4:.1f} {x:.1f},{y:.1f} Q{x + 9:.1f},{y - 4:.1f} {x + 20:.1f},{y - w:.1f}" stroke="{INK}" stroke-width="4" fill="none"/>')
    return ''.join(o)


def street_extra(t):
    fl = .12 if int(t * 9) % 23 == 0 else (.2 + .04 * math.sin(t * 13))
    o = [f'<circle cx="980" cy="810" r="120" fill="#ffd98a" opacity="{fl:.2f}"/>']
    for k in range(5):   # thieu than quanh den
        a = t * (2 + k * .4) + k; o.append(f'<circle cx="{980 + 50 * math.cos(a):.1f}" cy="{810 + 30 * math.sin(a * 1.3):.1f}" r="4" fill="#fff6c8"/>')
    return ''.join(o)


def install_bg():
    """boc BG cua bian_svg: ve them do dac/chuyen dong NGAY SAU nen (duoi nhan vat)."""
    import bian_svg as B
    if getattr(B, '_dd_bg', False): return
    B._dd_bg = True
    ex = {'room': room_extra, 'beach': beach_extra, 'village': village_extra, 'street': street_extra}
    for k, fn in ex.items():
        if k in B.BG:
            base = B.BG[k]
            B.BG[k] = (lambda b, f: (lambda t: b(t) + f(t)))(base, fn)
    sb = B.sea_beach
    B.sea_beach = lambda t, night=False: sb(t, night) + beach_extra(t)
