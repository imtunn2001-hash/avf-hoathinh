"""Bo canh CUNG DINH / BI AN LICH SU (Ly – Tran...) cho engine vh. vh_svg.beat() chuyen cac type trong CUNG sang day.
Moi hanh dong moc vao cau dang doc: V.at(sh, i, mac_dinh). Chu the gioi dat trong y 560–1300 man hinh.
"""
import math
import random

import vh_svg as V

GY = V.GY; INK = V.INK; FONT = V.FONT
f_ = V.f_; osc = V.osc; lerp = V.lerp; ease = V.ease; back_ease = V.back_ease; esc = V.esc
ch = V.ch

SIL = ('<defs><filter id="sil" x="-50%" y="-50%" width="200%" height="200%"><feColorMatrix type="matrix" '
       'values="0 0 0 0 0.06  0 0 0 0 0.03  0 0 0 0 0.03  0 0 0 0.88 0"/></filter></defs>')


def hall(t, dim=0.0, throne=True):
    """dien rong: tuong son do, dai vang, cot son, den long, bac the, ngai vang."""
    o = [f'<rect x="-900" y="-500" width="2880" height="2900" fill="#5a1a14"/>']
    for k in range(-4, 8):   # o vuong chim tren tuong
        x = k * 220
        o.append(f'<rect x="{x}" y="620" width="180" height="300" rx="10" fill="#6e241c" stroke="#3a0e0a" stroke-width="6"/>'
                 f'<rect x="{x + 30}" y="650" width="120" height="240" rx="6" fill="none" stroke="#b8862e" stroke-width="3" opacity=".6"/>')
    o.append(f'<rect x="-900" y="560" width="2880" height="36" fill="#c9962e" stroke="{INK}" stroke-width="5"/>')
    for k in range(-6, 12):
        o.append(f'<path d="M{k * 120},{578} q30,-14 60,0 t60,0" stroke="#7a1f1a" stroke-width="4" fill="none"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#b8925a" stroke="{INK}" stroke-width="6"/>')
    for k in range(-8, 14): o.append(f'<path d="M{k * 140},{GY - 40} l-60,600" stroke="#9a7848" stroke-width="4"/>')
    for x in (-90, 1170):   # cot son
        o.append(f'<rect x="{x - 55}" y="500" width="110" height="{GY - 460}" fill="#a8261c" stroke="{INK}" stroke-width="8"/>'
                 f'<rect x="{x - 62}" y="{GY - 120}" width="124" height="40" fill="#c9962e" stroke="{INK}" stroke-width="6"/>'
                 f'<path d="M{x - 30},700 q30,40 0,80 q-30,40 0,80" stroke="#d8a93a" stroke-width="7" fill="none"/>')
    for x in (180, 900):   # den long
        sw = osc(t, .35, x * .01) * 4
        o.append(f'<g transform="rotate({f_(sw)} {x} 520)"><line x1="{x}" y1="520" x2="{x}" y2="610" stroke="{INK}" stroke-width="4"/>'
                 f'<ellipse cx="{x}" cy="660" rx="44" ry="56" fill="#e0402a" stroke="{INK}" stroke-width="6"/>'
                 f'<rect x="{x - 22}" y="600" width="44" height="12" fill="#c9962e" stroke="{INK}" stroke-width="4"/><rect x="{x - 22}" y="708" width="44" height="12" fill="#c9962e" stroke="{INK}" stroke-width="4"/>'
                 f'<ellipse cx="{x}" cy="660" rx="60" ry="72" fill="#ffcf6a" opacity=".18"/></g>')
    if throne:
        o.append(dais())
        o.append(throne_svg(540, 1100))
    if dim > 0: o.append(f'<rect x="-900" y="-500" width="2880" height="2900" fill="#0a0608" opacity="{f_(dim)}"/>')
    return ''.join(o)


def dais():
    return ''.join(f'<rect x="{300 - k * 40}" y="{1100 + k * 50}" width="{480 + k * 80}" height="50" fill="{("#c9a46a", "#b8925a", "#a8824a")[k]}" stroke="{INK}" stroke-width="6"/>' for k in range(3))


def throne_svg(x, y, s=1.0):
    """ngai vang (chan ngai cham y)."""
    return (f'<path d="M{f_(x - 150 * s)},{f_(y)} L{f_(x - 150 * s)},{f_(y - 300 * s)} Q{f_(x - 150 * s)},{f_(y - 380 * s)} {f_(x - 80 * s)},{f_(y - 380 * s)} L{f_(x + 80 * s)},{f_(y - 380 * s)} Q{f_(x + 150 * s)},{f_(y - 380 * s)} {f_(x + 150 * s)},{f_(y - 300 * s)} L{f_(x + 150 * s)},{f_(y)} Z" fill="#d8a93a" stroke="{INK}" stroke-width="{f_(8 * s)}"/>'
            f'<path d="M{f_(x - 110 * s)},{f_(y - 120 * s)} L{f_(x - 110 * s)},{f_(y - 320 * s)} L{f_(x + 110 * s)},{f_(y - 320 * s)} L{f_(x + 110 * s)},{f_(y - 120 * s)} Z" fill="#a8261c" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
            f'<circle cx="{f_(x)}" cy="{f_(y - 250 * s)}" r="{f_(34 * s)}" fill="none" stroke="#d8a93a" stroke-width="{f_(7 * s)}"/>'
            f'<path d="M{f_(x - 180 * s)},{f_(y - 120 * s)} L{f_(x + 180 * s)},{f_(y - 120 * s)} L{f_(x + 170 * s)},{f_(y - 80 * s)} L{f_(x - 170 * s)},{f_(y - 80 * s)} Z" fill="#c9962e" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
            f'<circle cx="{f_(x - 180 * s)}" cy="{f_(y - 130 * s)}" r="{f_(20 * s)}" fill="#d8a93a" stroke="{INK}" stroke-width="{f_(5 * s)}"/><circle cx="{f_(x + 180 * s)}" cy="{f_(y - 130 * s)}" r="{f_(20 * s)}" fill="#d8a93a" stroke="{INK}" stroke-width="{f_(5 * s)}"/>')


def garden(t, dusk=0.0):
    """vuon chua: troi chieu, mai chua cong, cay bo de, co."""
    o = [V.sky('#e8a060', '#f6dcaa')]
    o.append(V.hills(900, '#7d9a6c', '#62805a'))
    # chua: mai cong 2 tang
    x0 = 820
    o.append(f'<rect x="{x0 - 200}" y="900" width="400" height="{GY - 900}" fill="#e8d8b0" stroke="{INK}" stroke-width="7"/>')
    for k, (w, y) in enumerate(((560, 900), (400, 760))):
        o.append(f'<path d="M{x0 - w / 2 - 40},{y - 10} Q{x0 - w / 2},{y} {x0 - w / 2 + 30},{y - 30} L{x0 - w / 2 + 80},{y - 120} L{x0 + w / 2 - 80},{y - 120} L{x0 + w / 2 - 30},{y - 30} Q{x0 + w / 2},{y} {x0 + w / 2 + 40},{y - 10} L{x0 + w / 2 - 20},{y + 10} L{x0 - w / 2 + 20},{y + 10} Z" fill="#8a4a2a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    o.append(f'<rect x="{x0 - 60}" y="{GY - 200}" width="120" height="200" fill="#5a3a22" stroke="{INK}" stroke-width="6"/>')
    # cay bo de
    o.append(f'<path d="M150,{GY} Q170,1000 130,860" stroke="{INK}" stroke-width="40" fill="none"/><path d="M150,{GY} Q170,1000 130,860" stroke="#6b4a2a" stroke-width="26" fill="none"/>')
    sw = osc(t, .2) * 6
    for k in range(6):
        a = k / 5; cx = -40 + a * 340 + sw; cy = 760 + 90 * math.sin(a * math.pi * 1.3)
        o.append(f'<ellipse cx="{f_(cx)}" cy="{f_(cy)}" rx="120" ry="80" fill="#4f7a3a" stroke="{INK}" stroke-width="6"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#7fa257" stroke="{INK}" stroke-width="6"/>')
    r = random.Random(7)
    for _ in range(26):
        gx = r.randint(-300, 1400); gy = GY - 30 + r.randint(0, 160)
        o.append(f'<path d="M{gx},{gy} q-6,-26 -18,-36 M{gx},{gy} q2,-30 8,-42 M{gx},{gy} q10,-22 22,-30" stroke="#3e6a2c" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if dusk > 0: o.append(f'<rect x="-900" y="-500" width="2880" height="2900" fill="#2a1030" opacity="{f_(dusk)}"/>')
    return ''.join(o)


def lychee(t, dawn=0.0):
    """vuon vai Le Chi ve dem: cay vai trai do, trai vua vang, den long; dawn>0 -> troi hung sang."""
    o = [V.sky('#0e1630', '#2a3460', True) if dawn <= 0 else V.sky('#5a6a9a', '#f2b98a')]
    o.append(V.hills(900, '#2e3e4a', '#24323e'))
    for k, (x, sc) in enumerate(((60, 1.0), (330, .8), (1020, .9))):   # cay vai
        sw = osc(t, .18, k) * 5
        o.append(f'<path d="M{x},{GY} Q{x + 14},{GY - 160} {x - 6},{GY - 300 * sc}" stroke="{INK}" stroke-width="{f_(46 * sc)}" fill="none"/><path d="M{x},{GY} Q{x + 14},{GY - 160} {x - 6},{GY - 300 * sc}" stroke="#4a3220" stroke-width="{f_(30 * sc)}" fill="none"/>')
        r = random.Random(11 + k)
        for j in range(5):
            cx = x + sw + (j - 2) * 80 * sc; cy = GY - 330 * sc - (60 if j % 2 else 0) * sc
            o.append(f'<ellipse cx="{f_(cx)}" cy="{f_(cy)}" rx="{f_(110 * sc)}" ry="{f_(80 * sc)}" fill="#24502e" stroke="{INK}" stroke-width="6"/>')
        for j in range(12):
            fx = x + sw + r.uniform(-200, 200) * sc; fy = GY - 330 * sc + r.uniform(-90, 60) * sc
            o.append(f'<circle cx="{f_(fx)}" cy="{f_(fy)}" r="{f_(11 * sc)}" fill="#d8402a" stroke="{INK}" stroke-width="3"/>')
    # trai vua (man vang) + den long
    x0 = 690
    o.append(f'<path d="M{x0 - 190},{GY - 20} L{x0 - 150},{GY - 250} L{x0},{GY - 340} L{x0 + 150},{GY - 250} L{x0 + 190},{GY - 20} Z" fill="#d8a93a" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
             f'<path d="M{x0 - 150},{GY - 250} L{x0 + 150},{GY - 250}" stroke="#7a1f1a" stroke-width="10"/>'
             f'<path d="M{x0 - 60},{GY - 20} L{x0},{GY - 230} L{x0 + 60},{GY - 20} Z" fill="#7a1f1a" stroke="{INK}" stroke-width="6"/>')
    gl = .25 + .08 * osc(t, 1.3)
    o.append(f'<circle cx="{x0}" cy="{GY - 140}" r="120" fill="#ffcf6a" opacity="{f_(gl * (1 - dawn))}"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#2c3a24" stroke="{INK}" stroke-width="6"/>')
    r = random.Random(9)
    for k in range(10):   # dom dom
        fx = r.randint(-100, 1180) + osc(t, .3, k) * 40; fy = r.randint(700, 1200) + osc(t, .25, k * 2) * 30
        o.append(f'<circle cx="{f_(fx)}" cy="{f_(fy)}" r="5" fill="#f6f08a" opacity="{f_(.4 + .4 * abs(osc(t, .9, k)))}"/>')
    if dawn > 0: o.append(f'<rect x="-900" y="-500" width="2880" height="2900" fill="#f2b98a" opacity="{f_(.12 * dawn)}"/>')
    return ''.join(o)


def boat(x, y, w=300, col='#8a5a2a'):
    return (f'<path d="M{f_(x - w / 2)},{f_(y - 30)} Q{f_(x)},{f_(y + 50)} {f_(x + w / 2)},{f_(y - 30)} L{f_(x + w / 2 - 20)},{f_(y - 10)} Q{f_(x)},{f_(y + 30)} {f_(x - w / 2 + 20)},{f_(y - 10)} Z" fill="{col}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M{f_(x - w / 2 + 10)},{f_(y - 28)} Q{f_(x)},{f_(y + 30)} {f_(x + w / 2 - 10)},{f_(y - 28)}" fill="{col}" stroke="{INK}" stroke-width="7"/>')


def tiger(x, y, s, t):
    """con ho kieu roi: than cam soc den, dau tron, tai, mat du."""
    b = osc(t, 1.4) * 4 * s
    o = [f'<g transform="translate({f_(x)} {f_(y + b)}) scale({f_(s)})">']
    o.append(f'<path d="M80,-40 q60,-30 70,-90" stroke="{INK}" stroke-width="22" fill="none" stroke-linecap="round"/><path d="M80,-40 q60,-30 70,-90" stroke="#e8902a" stroke-width="12" fill="none" stroke-linecap="round"/>')
    o.append(f'<ellipse cx="20" cy="-60" rx="110" ry="62" fill="#e8902a" stroke="{INK}" stroke-width="8"/>')
    for k in range(4): o.append(f'<path d="M{-40 + k * 40},-118 q10,30 -4,56" stroke="{INK}" stroke-width="9" fill="none" stroke-linecap="round"/>')
    o.append(f'<circle cx="-90" cy="-120" r="66" fill="#e8902a" stroke="{INK}" stroke-width="8"/>')
    o.append(f'<path d="M-140,-170 l-6,-40 l38,22 Z M-40,-170 l6,-40 l-38,22 Z" fill="#e8902a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    o.append(f'<ellipse cx="-90" cy="-96" rx="34" ry="24" fill="#f6eedd" stroke="{INK}" stroke-width="5"/>')
    o.append(f'<path d="M-122,-138 l18,8 M-58,-138 l-18,8" stroke="{INK}" stroke-width="8" stroke-linecap="round"/><circle cx="-110" cy="-124" r="7" fill="{INK}"/><circle cx="-70" cy="-124" r="7" fill="{INK}"/>')
    o.append(f'<path d="M-90,-104 l-8,-8 l16,0 Z" fill="{INK}"/><path d="M-104,-86 q14,10 28,0" stroke="{INK}" stroke-width="5" fill="none"/>')
    o.append(f'<path d="M-150,-150 q20,6 26,22 M-30,-150 q-20,6 -26,22" stroke="{INK}" stroke-width="7" fill="none"/>')
    o.append('</g>')
    return ''.join(o)


def lake(t):
    o = [V.sky('#b8c8cc', '#e8ece6')]
    o.append(V.hills(960, '#8aa294', '#6e8a7c'))
    o.append(f'<rect x="-900" y="1000" width="2880" height="1400" fill="#4a7a8a" stroke="{INK}" stroke-width="6"/>')
    for k in range(9):
        y = 1040 + k * 45; ph = (t * 40 + k * 70) % 160
        o.append(f'<path d="M{-200 + ph},{y} q40,-12 80,0 t80,0 t80,0 M{500 + ph},{y + 18} q40,-12 80,0 t80,0" stroke="#8ab4c2" stroke-width="5" fill="none"/>')
    return ''.join(o)


def net(x, y, w, h, q):
    if q <= 0: return ''
    k = min(1, q); yy = lerp(y - 500, y, ease(k))
    o = [f'<g opacity=".95">']
    for j in range(9):
        xx = x - w / 2 + j * w / 8
        o.append(f'<path d="M{f_(xx)},{f_(yy - h)} Q{f_(xx + 10)},{f_(yy - h / 2)} {f_(xx)},{f_(yy)}" stroke="#3a2a1a" stroke-width="4" fill="none"/>')
    for j in range(7):
        y2 = yy - h + j * h / 6
        o.append(f'<path d="M{f_(x - w / 2)},{f_(y2)} Q{f_(x)},{f_(y2 + 14)} {f_(x + w / 2)},{f_(y2)}" stroke="#3a2a1a" stroke-width="4" fill="none"/>')
    o.append('</g>')
    return ''.join(o)


def paper():
    return '<rect x="-900" y="-500" width="2880" height="2900" fill="#f2ead6"/>'


def stamp(x, y, text, q, col='#c4281f', rot=-12):
    if q <= 0: return ''
    sc = 1 + 1.2 * (1 - back_ease(min(1, q))); fs = 64; w = fs * .7 * len(text) + 60
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({f_(sc)})" opacity="{f_(min(1, q * 2))}">'
            f'<rect x="{f_(-w / 2)}" y="-56" width="{f_(w)}" height="112" rx="10" fill="none" stroke="{col}" stroke-width="10"/>'
            f'<text x="0" y="22" font-family="{FONT}" font-weight="900" font-size="{fs}" fill="{col}" text-anchor="middle">{esc(text)}</text></g>')


def tag_card(x, y, text, q, col='#d8a93a', tc='#111', fs=44):
    if q <= 0: return ''
    sc = back_ease(min(1, q)); w = fs * .68 * len(text) + 60
    return (f'<g transform="translate({x} {y}) scale({f_(sc)})"><rect x="{f_(-w / 2)}" y="-46" width="{f_(w)}" height="92" rx="14" fill="{col}" stroke="{INK}" stroke-width="7"/>'
            f'<text x="0" y="16" font-family="{FONT}" font-weight="900" font-size="{fs}" fill="{tc}" text-anchor="middle">{esc(text)}</text></g>')


def dust(x, y, t, q, n=7):
    if q <= 0 or q > 1.6: return ''
    o = []; r = random.Random(int(x))
    for k in range(n):
        a = r.uniform(-math.pi, 0); d = 60 + 220 * min(1, q) * r.uniform(.6, 1.1)
        cx, cy = x + math.cos(a) * d, y + math.sin(a) * d * .6
        o.append(f'<circle cx="{f_(cx)}" cy="{f_(cy)}" r="{f_(50 + 40 * q)}" fill="#d8ccb4" stroke="#8a7a64" stroke-width="5" opacity="{f_(max(0, .9 - q * .5))}"/>')
    return ''.join(o)


CUNG = ('child_throne', 'sick_king', 'pages', 'towel', 'whisper', 'wedding', 'swap', 'pagoda', 'empty_garden',
        'collapse', 'doubt', 'mongol', 'scales', 'damdam')


def beat(sh, t, d):
    ty = sh['type']; s = []; cam = (1.0, 540, 830); shake = 0.0; flash = 0.0
    if ty == 'child_throne':   # nu vuong be xiu tren ngai to; bong nguoi lon hien sau ngai
        s.append(SIL); s.append(hall(t, throne=False)); s.append(dais())
        qa = sh.get('shadow', True)
        if qa:
            q = ease((t - V.at(sh, int(sh.get('shadow_at', 1)), d * .5)) / .9)
            if q > 0:
                s.append(f'<g filter="url(#sil)" opacity="{f_(q)}">' + ch('thudo', 540, 1130 + (1 - q) * 160, 330, 1, 'angry', [(.7, -.6, None), (-.7, -.6, None)], t=t, tag=False) + '</g>')
        s.append(throne_svg(540, 1100))
        s.append(ch('chieuhoang', 540, 1000, 95, 1, sh.get('expr', 'normal'), t=t, tag=not qa or t < d * .45))
        if sh.get('ask'):
            tq = V.at(sh, -1, d * .6)
            if t >= tq: s.append(V.bigq(860, 1000, t - tq))
        cam = (lerp(1.0, 1.15, ease(t / max(1, d))), 540, 880)
    elif ty == 'sick_king':    # vua Ly Hue Tong om, lac lu; quyen than buoc vao
        s.append(hall(t))
        sw = osc(t, .45) * 7
        s.append(ch('huetong', 540, 1000, 120, 1, 'sad' if int(t) % 4 < 2 else 'scared', t=t, lean=sw))
        for k in range(3):   # vong choang vang
            a = t * 3 + k * 2.1
            s.append(V.star(540 + math.cos(a) * 80, 640 + math.sin(a) * 20, 16, t * 200))
        ta = V.at(sh, int(sh.get('enter', 1)), d * .45)
        if t >= ta:
            q = ease((t - ta) / 1.4); x = lerp(1300, 860, q); bob = V.walk(t) if q < 1 else 0
            s.append(ch('linhle', x + 200, GY + 40 - bob, 150, -1, 'normal', [(.6, -.1, 'spear', -70)], t=t, tag=False))
            s.append(ch('thudo', x, GY + 40 - bob, 190, -1, 'normal', [(.5, .1, None)], t=t))
        cam = (1.0, 600, 880)
    elif ty == 'pages':        # nguoi hau quanh nu vuong toan nguoi ho Tran; Tran Canh xuat hien
        s.append(hall(t))
        s.append(ch('chieuhoang', 540, 1000, 95, 1, 'happy', t=t, tag=False))
        for k, x in enumerate((140, 940)):
            q = back_ease(min(1, (t - V.at(sh, 0, .2) - .2 - k * .3) / .35))
            if q > 0: s.append(f'<g transform="translate({x} {GY + 40}) scale({f_(q)}) translate({-x} {-GY - 40})">' + ch('thitu', x, GY + 40, 130, 1 if x < 540 else -1, 'normal', t=t, tag=False) + '</g>')
        tc = V.at(sh, 1, d * .5)
        if t >= tc:
            q = back_ease(min(1, (t - tc) / .4)); x = 340
            s.append(f'<g transform="translate({x} {GY + 40}) scale({f_(q)}) translate({-x} {-GY - 40})">' + ch('trancanh', x, GY + 40, 115, 1, 'happy', t=t) + '</g>')
            s.append(V.star(x + 100, 960, 22 * q, t * 120))
        s.append(f'<g opacity=".9">' + ch('thudo', 1000, GY + 60, 150, -1, 'normal', t=t, tag=t > d * .5) + '</g>')
        cam = (1.0, 560, 900)
    elif ty == 'towel':        # nu vuong nem khan trau cho Tran Canh
        s.append(hall(t, throne=False)); s.append(dais())
        tt = V.at(sh, int(sh.get('throw_at', 1)), d * .35)
        q = (t - tt) / .8
        s.append(ch('chieuhoang', 740, GY + 40, 115, -1, 'happy', [(.5, -.4 if 0 <= q < .4 else .1, None)], t=t))
        caught = q >= 1
        s.append(ch('trancanh', 320, GY + 40, 110, 1, 'surprised' if caught else 'normal', [(.6, -.2, 'towel')] if caught else None, t=t))
        if 0 <= q < 1:
            x = lerp(680, 400, q); y = lerp(1010, 1040, q) - math.sin(q * math.pi) * 260
            s.append(f'<g transform="rotate({f_(q * 540)} {f_(x)} {f_(y)})"><path d="M{f_(x - 30)},{f_(y - 10)} q30,-30 60,-6 l-8,40 q-26,-14 -52,8 Z" fill="#c4281f" stroke="{INK}" stroke-width="5"/></g>')
        if caught and q < 2.2:
            s.append(f'<text x="330" y="{f_(820 - 30 * min(1, q - 1))}" font-family="{FONT}" font-weight="900" font-size="90" fill="#ffd400" stroke="{INK}" stroke-width="7" paint-order="stroke" text-anchor="middle">!</text>')
        cam = (1.0, 540, 900)
    elif ty == 'whisper':      # Tran Canh chay ve mach chu; Thu Do noi cau "lam vua hay chet ca ho"
        s.append(hall(t, dim=.35, throne=False))
        q = ease(t / 1.4); x = lerp(-80, 420, q); bob = V.walk(t, 1.4) if q < 1 else 0
        s.append(ch('trancanh', x, GY + 40 - bob, 110, 1, 'scared' if sh.get('fork') else 'surprised', [(.6, -.2, 'towel')], t=t, tag=False))
        s.append(ch('thudo', 720, GY + 40, 200, -1, 'angry' if sh.get('fork') else 'normal', [(.55, -.25, None)], t=t))
        if sh.get('fork'):
            qa = (t - V.at(sh, 0, .3) - .3) / .4; qb = (t - V.at(sh, 1, d * .5)) / .4
            s.append(tag_card(300, 760, 'HỌ NHÀ VUA', qa, '#d8a93a'))
            s.append(tag_card(780, 760, 'CHẾT CẢ HỌ', qb, '#c4281f', '#fff'))
            if qb > 0: s.append(f'<text x="540" y="780" font-family="{FONT}" font-weight="900" font-size="60" fill="#fff" text-anchor="middle" opacity="{f_(min(1, qb))}">/</text>')
            cam = (lerp(1.0, 1.12, ease(t / max(1, d))), 600, 900)
        else:
            cam = (1.0, 560, 900)
    elif ty == 'wedding':      # "be ha co chong": 2 dua tre, quan trieu cui lay
        s.append(hall(t, throne=False)); s.append(dais())
        r = random.Random(3)
        for k in range(18):   # hoa roi
            x0 = r.randint(-100, 1180); y = (r.randint(0, 900) + t * 160) % 900 + 520
            s.append(f'<circle cx="{f_(x0 + osc(t, .5, k * .1) * 20)}" cy="{f_(y)}" r="10" fill="#f08a8a" stroke="{INK}" stroke-width="3"/>')
        s.append(ch('trancanh', 470, GY - 40, 105, 1, 'surprised', t=t, tag=False))
        s.append(ch('chieuhoang', 620, GY - 40, 105, -1, 'happy', t=t, tag=False))
        bow = 14 + 10 * abs(osc(t, .8))
        for k, x in enumerate((60, 220, 860, 1020)):
            s.append(ch('quan', x, GY + 120, 140, 1 if x < 540 else -1, 'surprised' if k == 1 else 'normal', lean=bow, t=t, tag=False))
        s.append(ch('thudo', 900, GY - 60, 150, -1, 'happy', t=t, tag=False))
        cam = (1.0, 540, 900)
    elif ty == 'swap':         # Chieu Hoang buoc xuong, Tran Canh buoc len; bang "NHA LY" roi xuong
        s.append(hall(t))
        tsw = V.at(sh, 0, .3) + .4; q = ease((t - tsw) / 1.4)
        s.append(ch('chieuhoang', lerp(540, 280, q), lerp(1000, GY + 40, q), lerp(95, 105, q), -1, 'sad' if q > .5 else 'normal', t=t, tag=q > .9))
        s.append(ch('trancanh', lerp(860, 540, q), lerp(GY + 40, 1000, q), lerp(105, 95, q), -1 if q < .5 else 1, 'surprised', t=t, tag=q > .9))
        tb = V.at(sh, 1, d * .55); qb = (t - tb) / 1.1
        by = 740 if qb <= 0 else 740 + 480 * min(1, qb) ** 2
        rot = 0 if qb <= 0 else min(1, qb) * 28
        s.append(f'<g transform="rotate({f_(rot)} 540 {f_(by)})"><rect x="250" y="{f_(by - 60)}" width="580" height="120" rx="10" fill="#2a4a7a" stroke="{INK}" stroke-width="8"/>'
                 f'<text x="540" y="{f_(by + 20)}" font-family="{FONT}" font-weight="900" font-size="54" fill="#ffd400" text-anchor="middle">NHÀ LÝ 1009 – 1225</text></g>')
        if 0 < qb < 1.4 and qb > .95: shake = 10
        cam = (1.0, 540, 880)
    elif ty == 'pagoda':       # su Hue Quang (vua cu) nho co sau chua; Thu Do di toi
        s.append(garden(t))
        pull = abs(osc(t, .7)) ; hy = .1 + .25 * pull
        s.append(f'<rect x="380" y="{GY - 70}" width="360" height="90" rx="40" fill="#5e8a46" stroke="{INK}" stroke-width="6"/>')
        s.append(ch('huequang', 560, GY + 70, 140, -1, sh.get('expr', 'normal'), [(.75, hy + .3, 'weed' if pull > .6 else None)], t=t, hidden_below=GY - 40))
        s.append(f'<path d="M370,{GY - 30} q190,-50 380,0 L750,{GY + 20} L370,{GY + 20} Z" fill="#5e8a46" stroke="{INK}" stroke-width="6"/>')
        ta = V.at(sh, int(sh.get('arrive', 9)), 1e9) if sh.get('arrive') is not None else 1e9
        if sh.get('present'): ta = -9
        if t >= ta:
            q = ease((t - ta) / 1.3); x = lerp(-150, 230, q); bob = V.walk(t) if q < 1 else 0
            s.append(ch('thudo', x, GY + 40 - bob, 180, 1, 'normal', [(.6, -.15, None)], t=t))
        tr = V.at(sh, int(sh['root']), 1e9) if sh.get('root') is not None else 1e9
        if t >= tr:   # bui co bi nho ca re: phong to giua khung
            q = back_ease(min(1, (t - tr) / .5))
            s.append(f'<g transform="translate(540 760) scale({f_(2.2 * q)}) translate(-540 -760)">'
                     f'<path d="M540,700 q-12,60 8,120 q-28,40 -8,92 M544,780 q32,24 40,68 M540,700 q-40,20 -60,70" stroke="#8a6a3a" stroke-width="8" fill="none" stroke-linecap="round"/>'
                     + ''.join(f'<path d="M540,700 q{dx},-60 {dx * 2},-120" stroke="#3e7a2c" stroke-width="14" fill="none" stroke-linecap="round"/>' for dx in (-28, -8, 16, 32)) + '</g>')
        cam = (1.0, 520, 900)
    elif ty == 'empty_garden':   # vuon chua vang: chuoi tran hat, chiec non tren co, la roi
        s.append(garden(t, .35))
        s.append(f'<ellipse cx="560" cy="{GY + 40}" rx="120" ry="26" fill="#d8bc78" stroke="{INK}" stroke-width="6"/><path d="M450,{GY + 40} L560,{GY - 20} L670,{GY + 40}" fill="#e2c47a" stroke="{INK}" stroke-width="6"/>')
        s.append(''.join(f'<circle cx="{f_(380 + 40 * math.cos(k / 14 * 6.28))}" cy="{f_(GY + 60 + 16 * math.sin(k / 14 * 6.28))}" r="9" fill="#6b3a1a" stroke="{INK}" stroke-width="3"/>' for k in range(14)))
        r = random.Random(5)
        for k in range(9):
            x0 = r.randint(-100, 1100); y = (r.randint(0, 700) + t * 90) % 700 + 600
            s.append(f'<ellipse cx="{f_(x0 + osc(t, .4, k * .2) * 40)}" cy="{f_(y)}" rx="16" ry="8" fill="#c9962e" stroke="{INK}" stroke-width="3" transform="rotate({f_(t * 90 + k * 40)} {f_(x0)} {f_(y)})"/>')
        cam = (lerp(1.0, 1.2, ease(t / max(1, d))), 520, 980)
    elif ty == 'collapse':     # Thai Duong: ton that ho Ly vao cung, nha sap
        s.append(V.sky('#d88a52', '#f2cc98')); s.append(V.hills(900))
        s.append(V.road(GY))
        tc = V.at(sh, 1, d * .55); q = (t - tc) / .7
        hx = 640
        if q <= 0:
            s.append(V.house(hx, GY - 40, 460, 260, '#e8d8b0', '#8a2a1e'))
        else:
            k = min(1, q)
            s.append(f'<rect x="{hx - 230}" y="{f_(GY - 40 - 260 * (1 - .75 * k))}" width="460" height="{f_(260 * (1 - .75 * k))}" fill="#e8d8b0" stroke="{INK}" stroke-width="7"/>')
            s.append(f'<g transform="translate(0 {f_(200 * k)}) rotate({f_(14 * k)} {hx} {GY - 300})"><path d="M{hx - 285},{GY - 300} L{hx},{GY - 534} L{hx + 285},{GY - 300} Z" fill="#8a2a1e" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/></g>')
            s.append(dust(hx, GY - 60, t, q * 1.2, 9))
            if q < .5: shake = 16 * (1 - q * 2)
            if q < .15: flash = .35
        n_in = 3
        for k in range(n_in):
            t0 = V.at(sh, 0, .2) + k * .6; qq = ease((t - t0) / 2.0)
            if qq <= 0 or (q > 0 and qq >= .99): continue
            x = lerp(-120, hx - 60 + k * 30, qq); bob = V.walk(t)
            vis = 1 if qq < .95 else max(0, (1 - qq) * 20)
            s.append(f'<g opacity="{f_(vis)}">' + ch('tonthat', x, GY + 60 - bob, 140, 1, 'normal', t=t, tag=k == 0) + '</g>')
        cam = (1.0, 560, 900)
    elif ty == 'doubt':        # Ngo Si Lien nghi: so chep vs con nguoi ho Ly
        s.append(paper())
        s.append(f'<rect x="120" y="640" width="520" height="560" rx="10" fill="#f6e8b8" stroke="{INK}" stroke-width="8"/>'
                 f'<rect x="100" y="620" width="560" height="30" rx="15" fill="#7a1f1a" stroke="{INK}" stroke-width="6"/><rect x="100" y="1190" width="560" height="30" rx="15" fill="#7a1f1a" stroke="{INK}" stroke-width="6"/>'
                 f'<text x="380" y="730" font-family="{FONT}" font-weight="900" font-size="48" fill="#5a1a14" text-anchor="middle">SỬ CHÉP</text>'
                 f'<text x="380" y="800" font-family="{FONT}" font-weight="700" font-size="38" fill="#5a1a14" text-anchor="middle">THÁI ĐƯỜNG, 1232</text>')
        s.append(f'<path d="M230,1120 L380,960 L530,1120 Z" fill="#8a2a1e" stroke="{INK}" stroke-width="6" transform="rotate(12 380 1040)"/>' + dust(380, 1110, t, .5, 5))
        s.append(ch('ngosilien', 840, GY + 40, 170, -1, 'normal' if t < V.at(sh, 1, d * .5) else 'surprised', [(.6, -.3, 'pen')], t=t))
        s.append(stamp(380, 960, 'NGHI VẤN', (t - V.at(sh, 0, .3) - .6) / .4))
        cam = (1.0, 540, 900)
    elif ty == 'mongol':       # 1258: quan Mong Co toi, Thu Do gia: "dau than chua roi xuong dat"
        s.append(hall(t))
        s.append(f'<rect x="-60" y="640" width="300" height="300" fill="#e8a060" stroke="{INK}" stroke-width="10"/>')
        for k in range(5):
            x = -40 + ((t * 40 + k * 70) % 300)
            s.append(f'<circle cx="{f_(x)}" cy="{860 + (k % 2) * 20}" r="14" fill="#3a2a1a"/><path d="M{f_(x - 4)},{850 + (k % 2) * 20} l0,-40" stroke="#3a2a1a" stroke-width="4"/>')
        s.append(f'<rect x="-60" y="640" width="300" height="300" fill="none" stroke="#6b4a2a" stroke-width="16"/><path d="M90,640 L90,940 M-60,790 L240,790" stroke="#6b4a2a" stroke-width="10"/>')
        s.append(ch('thaitong', 540, 1000, 115, 1, 'scared' if t < V.at(sh, int(sh.get('lift', 1)), d * .5) else 'surprised', t=t))
        lift = ease((t - V.at(sh, int(sh.get('lift', 1)), d * .5)) / .5)
        s.append(ch('thudogia', 820, GY + 40, 190, -1, 'angry', [(.55, lerp(.1, -.75, lift), None)], t=t))
        cam = (1.0, 600, 900)
    elif ty == 'scales':       # can: ac hay cong
        s.append(paper())
        tilt = osc(t, .35) * 12
        s.append(f'<path d="M540,1180 L540,720" stroke="{INK}" stroke-width="22"/><path d="M540,1180 L540,720" stroke="#8a6a3a" stroke-width="12"/><path d="M420,1190 L660,1190 L600,1150 L480,1150 Z" fill="#8a6a3a" stroke="{INK}" stroke-width="6"/>')
        s.append(f'<g transform="rotate({f_(tilt)} 540 720)"><path d="M200,720 L880,720" stroke="{INK}" stroke-width="16"/><path d="M200,720 L880,720" stroke="#c9962e" stroke-width="8"/></g>')
        for side, txt, col in ((-1, sh.get('left', 'BỨC TỬ VUA LÝ'), '#c4281f'), (1, sh.get('right', 'GIỮ NƯỚC 1258'), '#2a4a7a')):
            a = math.radians(tilt); px = 540 + side * 340 * math.cos(a); py = 720 + side * 340 * math.sin(a)
            s.append(f'<path d="M{f_(px)},{f_(py)} L{f_(px - 110)},{f_(py + 160)} M{f_(px)},{f_(py)} L{f_(px + 110)},{f_(py + 160)}" stroke="{INK}" stroke-width="4"/>'
                     f'<path d="M{f_(px - 140)},{f_(py + 160)} Q{f_(px)},{f_(py + 240)} {f_(px + 140)},{f_(py + 160)} Z" fill="#c9962e" stroke="{INK}" stroke-width="6"/>')
            qq = (t - V.at(sh, 0 if side < 0 else 1, .3 if side < 0 else d * .45)) / .35
            s.append(tag_card(px, py + 110, txt, qq, col, '#fff', 34))
        if sh.get('ask'):
            tq = V.at(sh, -1, d * .7)
            if t >= tq: s.append(V.bigq(900, 1150, t - tq))
        cam = (1.0, 540, 950)
    elif ty == 'damdam':       # ho Dam Dam 1096: suong mu, thuyen lao toi, vua phong giao, ho trong thuyen, luoi trum, go luoi ra la Le Van Thinh
        s.append(lake(t))
        ph = sh.get('phase', 'fog')
        # thuyen vua ben trai
        tj = V.at(sh, int(sh['spear_at']), d * .1) if sh.get('spear_at') is not None else 1e9
        s.append(ch('nhantong', 290, 1110, 125, 1, 'surprised' if t >= tj or ph != 'calm' else 'normal', [(.7, -.55 if t >= tj else -.1, 'spear', -40 if t >= tj else -70)] if ph != 'calm' else None, t=t))
        s.append(boat(290, 1140, 340, '#a8261c'))
        # thuyen la ben phai
        if ph != 'calm':
            ta = V.at(sh, int(sh.get('boat_at', 0)), .3); q = ease((t - ta) / 2.2) if ph == 'fog' else 1
            bx = lerp(1250, 790, q)
            tt = (V.at(sh, int(sh['tiger_at']), d * .3) if sh.get('tiger_at') is not None else 1e9) if ph == 'fog' else -9
            tn = (V.at(sh, int(sh['net_at']), d * .6) if sh.get('net_at') is not None else 1e9) if ph != 'reveal' else -9
            tr = V.at(sh, int(sh.get('reveal_at', 0)), d * .4) if ph == 'reveal' else 1e9
            if t >= tr:
                q2 = ease((t - tr) / .8)
                s.append(ch('levanthinh', bx, 1110, 130, -1, 'scared', t=t))
                s.append(f'<g opacity="{f_(1 - q2)}">' + net(bx, 1100, 360, 380, 1) + '</g>')
            elif t >= tt:
                s.append(tiger(bx + 30, 1100, .9, t))
                s.append(net(bx + 10, 1110, 380, 360, (t - tn) / .7))
            s.append(boat(bx, 1140, 320))
            if ph == 'reveal' and t < tr: s.append(net(bx + 10, 1110, 380, 360, 1))
            if t >= tn and ph != 'reveal': s.append(ch('mucthan', 1010, 1240, 130, -1, 'angry', [(.7, -.6, None), (-.6, -.5, None)], t=t)); s.append(boat(1010, 1270, 240, '#6b4a2a'))
            if t >= tj and t < tj + .9:   # ngon giao bay
                qq = (t - tj) / .9; x = lerp(380, bx, qq); y = lerp(900, 1000, qq) - math.sin(qq * 3.14) * 120
                s.append(f'<path d="M{f_(x - 70)},{f_(y + 10)} L{f_(x + 60)},{f_(y)}" stroke="{INK}" stroke-width="12" stroke-linecap="round"/><path d="M{f_(x + 50)},{f_(y - 12)} l40,12 l-40,12 Z" fill="#c8ccd2" stroke="{INK}" stroke-width="5"/>')
            # suong mu: day dac khi ph=fog cho toi luc ho hien
            fog = 0.0
            if ph == 'fog':
                fog = min(1, max(0, (t - .2) / 1.5)) * (1 - min(1, max(0, (t - tt) / .8)))
            for k in range(7):
                fx = (k * 260 + t * 30) % 1600 - 300; fy = 860 + (k % 3) * 120
                s.append(f'<ellipse cx="{f_(fx)}" cy="{fy}" rx="300" ry="90" fill="#f4f4f0" opacity="{f_(.75 * fog)}"/>')
        cam = (1.0, 600, 950)
    return ''.join(s), cam, shake, flash


SFX = {
    'child_throne': [('f0.5', 'sting', .6)],
    'sick_king': [('f0.5', 'thud', .5), ('f0.6', 'thud', .5)],
    'pages': [('f0.2', 'pop', .5), ('f0.5', 'pop', .8), ('f0.52', 'ding', .5)],
    'towel': [('f0.35', 'whoosh', .7), ('f0.6', 'pop', .7)],
    'whisper': [('f0.1', 'whoosh', .4), ('f0.55', 'sting', .6)],
    'wedding': [('f0.1', 'ding', .5), ('f0.5', 'ding', .4)],
    'swap': [('f0.55', 'boom', .7)],
    'pagoda': [('every:1.4@0.5', 'tick', .25), ('f0.6', 'sting', .6)],
    'empty_garden': [],
    'collapse': [('f0.55', 'boom', 1.0), ('f0.58', 'thud', .9)],
    'doubt': [('f0.2', 'thud', .8)],
    'mongol': [('every:1.2', 'drum', .6)],
    'scales': [('f0.1', 'pop', .6), ('f0.5', 'pop', .6)],
    'damdam': [('f0.15', 'whoosh', .5), ('f0.6', 'sting', .6)],
}
