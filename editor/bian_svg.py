"""Bo canh BI AN (Chuyen Chua Ke va moi kenh ke chuyen bi an) cho engine vh – dung CHUNG nhieu tap, dieu khien bang spec.
Moi hanh dong moc vao cau dang doc: V.at(sh, i, mac_dinh). Chu the gioi dat trong y 560–1300 man hinh.

Canh:
- beach     : bai bien + tuong chan song; sh.who (nhan vat ngoi tua tuong, expr), sh.people (nguoi di ngang), sh.night, sh.walk_at
- station   : nha ga: dong ho, quay gui do; vali hien o cau sh.bag_at; sh.cut=True -> nhan mac bi cat
- items     : bang vat chung tren nen giay: sh.items=[{t:'chu', icon:'shirt|suitcase|ticket|cigarette|paper|book|phone|dna|key|coin|comb|letter|map|clock|ring|car'}], hien lan luot theo cau (at = so cau)
- scrap     : manh giay cuon mo ra: sh.word (chu tren giay), sh.mean (nghia, hien o cau sh.mean_at)
- car       : xe hoi cu; nguoi mo cua sau o cau sh.open_at, cuon sach phat sang
- code      : to giay chu ma go dan tung dong sh.lines; kinh lup lia; sh.stamp (dau do) o cau cuoi
- door      : nha ve dem + so dien thoai; nhan vat sh.who mo cua o cau sh.open_at, lac dau o cau sh.shake_at
- board     : bang ghim manh moi: sh.cards=[chu], sh.links=[[i,j]], card i hien o cau i (hoac sh.at=[...])
- timeline  : truc thoi gian: sh.points=[{y:'1948', t:'chu'}] hien lan luot
- spy       : bong nguoi doi mu trong suong + chu GIA THUYET; sh.title
- lab       : phong thi nghiem: chuoi ADN xoay, kinh hien vi; sh.who (nha khoa hoc), sh.result (the ket qua o cau sh.result_at)
- tree      : cay pha he no ra, sh.count (vd '4.000 NGƯỜI'), sh.name (nhanh sang len o cau sh.name_at)
- grave     : nghia trang luc chieu, bia da sh.stone (vd 'NGƯỜI VÔ DANH'); sh.dig_at -> hoa tuoi/den
- petition  : don keu oan chat chong theo nam (sh.y0, sh.y1, sh.who, sh.title)
- stage     : san khau tu do: sh.bg (beach|station|street|room|lab|paper|night|village|village_night|riverbank|riverbank_dawn|shop|shop_day|prison|court|market|alley|hall|hall_empty|hall_dim|pagoda|lychee|lychee_dawn|lake), sh.desk (ban xu), sh.icons=[{icon,x,y,s,at}], sh.cast=[{c, x, D, expr, face, at, from}], sh.cards=[{t, x, y, at, col}]
"""
import math
import random

import vh_svg as V

GY = V.GY; INK = V.INK; FONT = V.FONT
f_ = V.f_; osc = V.osc; lerp = V.lerp; ease = V.ease; back_ease = V.back_ease; esc = V.esc
ch = V.ch


def pop(x, y, q, inner):
    if q <= 0: return ''
    sc = back_ease(min(1, q))
    return f'<g transform="translate({f_(x)} {f_(y)}) scale({f_(sc)}) translate({f_(-x)} {f_(-y)})">{inner}</g>'


def card(x, y, text, col='#f4ecd6', tc='#111', fs=40, rot=0.0, w=None):
    w = w or fs * .66 * len(text) + 60
    return (f'<g transform="rotate({f_(rot)} {f_(x)} {f_(y)})"><rect x="{f_(x - w / 2)}" y="{f_(y - fs * .95)}" width="{f_(w)}" height="{f_(fs * 1.9)}" rx="12" fill="{col}" stroke="{INK}" stroke-width="7"/>'
            f'<text x="{f_(x)}" y="{f_(y + fs * .35)}" font-family="{FONT}" font-weight="900" font-size="{fs}" fill="{tc}" text-anchor="middle">{esc(text)}</text></g>')


def paper(col='#efe6cf'):
    r = random.Random(11)
    dots = ''.join(f'<circle cx="{r.randint(-300, 1400)}" cy="{r.randint(400, 1600)}" r="{r.choice((2, 3))}" fill="#c9b88e" opacity=".5"/>' for _ in range(90))
    return f'<rect x="-900" y="-500" width="2880" height="2900" fill="{col}"/>' + dots


def night_sky():
    return V.sky('#0e1630', '#2a3458', True)


def sea_beach(t, night=False):
    o = [V.sky('#1a2340', '#3a4a6a', True) if night else V.sky('#8ec0e0', '#eaf3f6')]
    o.append(f'<rect x="-900" y="860" width="2880" height="260" fill="{"#2a4a6a" if night else "#4f8db0"}" stroke="{INK}" stroke-width="6"/>')
    for k in range(-6, 14):   # song
        x = k * 120 + (t * 40) % 120
        o.append(f'<path d="M{f_(x)},{900 + (k % 3) * 60} q30,-16 60,0" stroke="#d8eef6" stroke-width="5" fill="none" opacity=".8"/>')
    o.append(f'<path d="M-900,1110 Q-300,1080 300,1110 T1500,1100 T2000,1110 L2000,2000 L-900,2000 Z" fill="#e8d29a" stroke="{INK}" stroke-width="6"/>')
    # tuong chan song bang da
    o.append(f'<rect x="-900" y="{GY - 200}" width="2880" height="210" fill="#b8ad98" stroke="{INK}" stroke-width="7"/>')
    for r_ in range(4):
        for c_ in range(-8, 16):
            o.append(f'<rect x="{c_ * 140 + (r_ % 2) * 70}" y="{GY - 200 + r_ * 52}" width="140" height="52" fill="none" stroke="#8a806c" stroke-width="3"/>')
    o.append(f'<rect x="-900" y="{GY}" width="2880" height="900" fill="#e8d29a" stroke="{INK}" stroke-width="6"/>')
    if night: o.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#0a1030" opacity=".3"/>')
    return ''.join(o)


def station_bg(t):
    o = [f'<rect x="-900" y="-500" width="2880" height="2900" fill="#c8b48a"/>']
    for k in range(-3, 8):   # vom cua so
        x = k * 260
        o.append(f'<path d="M{x},1000 L{x},700 Q{x + 100},580 {x + 200},700 L{x + 200},1000 Z" fill="#e6dcc0" stroke="{INK}" stroke-width="7"/>'
                 f'<path d="M{x + 100},600 L{x + 100},1000 M{x},820 L{x + 200},820" stroke="{INK}" stroke-width="5"/>')
    # dong ho lon
    a = t * .4
    o.append(f'<circle cx="540" cy="640" r="90" fill="#f6f0dc" stroke="{INK}" stroke-width="9"/>'
             f'<path d="M540,640 L{f_(540 + 55 * math.sin(a))},{f_(640 - 55 * math.cos(a))}" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
             f'<path d="M540,640 L{f_(540 + 35 * math.sin(a / 12 + 1))},{f_(640 - 35 * math.cos(a / 12 + 1))}" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#8a7458" stroke="{INK}" stroke-width="6"/>')
    for k in range(-8, 14): o.append(f'<path d="M{k * 120},{GY - 40} l-40,600" stroke="#6e5a42" stroke-width="4"/>')
    return ''.join(o)


def street_night(t):
    o = [night_sky()]
    for k, (x, w, h) in enumerate([(-200, 300, 420), (160, 260, 520), (460, 300, 380), (800, 280, 480), (1120, 300, 420)]):
        o.append(f'<rect x="{x}" y="{GY - 40 - h}" width="{w}" height="{h}" fill="#2e3448" stroke="{INK}" stroke-width="6"/>')
        for r_ in range(int(h // 90)):
            for c_ in range(int(w // 80)):
                lit = (k * 7 + r_ * 3 + c_) % 4 == 0
                o.append(f'<rect x="{x + 20 + c_ * 80}" y="{GY - 20 - h + 30 + r_ * 90}" width="44" height="50" fill="{"#ffd98a" if lit else "#1e2232"}"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#3a3a44" stroke="{INK}" stroke-width="6"/>')
    o.append(f'<path d="M980,{GY - 40} L980,820" stroke="{INK}" stroke-width="14"/><circle cx="980" cy="810" r="26" fill="#ffd98a" stroke="{INK}" stroke-width="6"/><path d="M880,{GY - 40} L980,840 L1080,{GY - 40} Z" fill="#ffd98a" opacity=".12"/>')
    return ''.join(o)


def room_bg(t, col='#d8c8a8'):
    o = [f'<rect x="-900" y="-500" width="2880" height="2900" fill="{col}"/>']
    for k in range(-10, 20): o.append(f'<path d="M{k * 90},500 L{k * 90},{GY - 40}" stroke="#c4b292" stroke-width="4"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#8a6a46" stroke="{INK}" stroke-width="6"/>')
    return ''.join(o)


def lab_bg(t):
    o = [f'<rect x="-900" y="-500" width="2880" height="2900" fill="#dfe8ee"/>']
    o.append(f'<rect x="-900" y="{GY - 200}" width="2880" height="40" fill="#9aaab6" stroke="{INK}" stroke-width="6"/>')
    for x in (60, 980):   # ong nghiem
        for k in range(3):
            o.append(f'<rect x="{x + k * 40}" y="{GY - 300}" width="24" height="100" rx="12" fill="{("#7ac4f0", "#f08a8a", "#9ad88a")[k]}" stroke="{INK}" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#b8c4cc" stroke="{INK}" stroke-width="6"/>')
    return ''.join(o)


def shop_bg(t, night=True):
    """quan tap hoa nong thon: mai ngoi, tu kinh, den vang"""
    o = [V.village(t, night=night)]
    o.append(f'<rect x="250" y="{GY - 420}" width="580" height="380" fill="#c9a46a" stroke="{INK}" stroke-width="8"/>'
             f'<path d="M210,{GY - 420} L540,{GY - 560} L870,{GY - 420} Z" fill="#a8563a" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
             f'<rect x="300" y="{GY - 340}" width="300" height="300" fill="#2a1e14" stroke="{INK}" stroke-width="7"/>'
             f'<rect x="630" y="{GY - 230}" width="170" height="190" fill="#bfe0ec" fill-opacity=".7" stroke="{INK}" stroke-width="7"/>')
    for j in range(3):
        o.append(f'<path d="M635,{GY - 180 + j * 50} l160,0" stroke="{INK}" stroke-width="4"/>'
                 + ''.join(f'<rect x="{645 + k * 38}" y="{GY - 212 + j * 50}" width="24" height="30" fill="{("#e8822a", "#3a7ac4", "#9ad88a", "#f08a8a")[(j + k) % 4]}" stroke="{INK}" stroke-width="3"/>' for k in range(4)))
    gl = .55 + .15 * osc(t, .7)
    o.append(f'<circle cx="450" cy="{GY - 300}" r="22" fill="#ffd98a" stroke="{INK}" stroke-width="5"/><circle cx="450" cy="{GY - 300}" r="120" fill="#ffd98a" opacity="{f_(gl * .35)}"/>'
             f'<rect x="330" y="{GY - 405}" width="240" height="56" rx="8" fill="#f4ecd6" stroke="{INK}" stroke-width="6"/>'
             f'<text x="450" y="{GY - 365}" font-family="{FONT}" font-weight="900" font-size="32" fill="#7a1f1a" text-anchor="middle">TẠP HOÁ</text>')
    return ''.join(o)


def prison_bg(t):
    """trai giam: tuong gach, o cua song sat"""
    o = [f'<rect x="-900" y="-500" width="2880" height="2900" fill="#8a8a86"/>']
    for r_ in range(14):
        for c_ in range(-8, 16):
            o.append(f'<rect x="{c_ * 150 + (r_ % 2) * 75}" y="{400 + r_ * 60}" width="150" height="60" fill="none" stroke="#6e6e6a" stroke-width="3"/>')
    o.append(f'<rect x="340" y="600" width="400" height="240" fill="#3a4458" stroke="{INK}" stroke-width="8"/>')
    for k in range(7): o.append(f'<path d="M{370 + k * 56},600 L{370 + k * 56},840" stroke="{INK}" stroke-width="12"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#5e5e5a" stroke="{INK}" stroke-width="6"/>')
    return ''.join(o)


def court_bg(t):
    """phong xu: tuong go, ban dai mau do"""
    o = [f'<rect x="-900" y="-500" width="2880" height="2900" fill="#c9a87a"/>']
    for k in range(-10, 20): o.append(f'<path d="M{k * 110},400 L{k * 110},{GY - 40}" stroke="#b08e60" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#7a5a3a" stroke="{INK}" stroke-width="6"/>')
    return ''.join(o)


def court_desk():
    """ban xu dat TRUOC nhan vat (che than duoi)"""
    return (f'<rect x="40" y="{GY - 150}" width="1000" height="190" fill="#8a2a1e" stroke="{INK}" stroke-width="8"/>'
            f'<rect x="20" y="{GY - 170}" width="1040" height="28" fill="#6e4a2e" stroke="{INK}" stroke-width="6"/>')


def market_bg(t):
    """cho do cu ban ngay: mai bat, sap go bay phu tung (den xe, banh, oc vit)"""
    o = [f'<rect x="-900" y="-500" width="2880" height="2900" fill="#e8d8b0"/>']
    for k, (x, col) in enumerate([(-260, '#3a6aa4'), (80, '#c4281f'), (420, '#3a7a4a'), (760, '#d8a93a'), (1100, '#3a6aa4')]):
        o.append(f'<path d="M{x},{GY - 470} L{x + 330},{GY - 470} L{x + 360},{GY - 380} L{x - 30},{GY - 380} Z" fill="{col}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
                 f'<path d="M{x + 10},{GY - 380} L{x + 10},{GY - 40} M{x + 320},{GY - 380} L{x + 320},{GY - 40}" stroke="#6e4a2e" stroke-width="10"/>'
                 f'<rect x="{x - 10}" y="{GY - 200}" width="350" height="40" fill="#8a6a46" stroke="{INK}" stroke-width="6"/>')
        for j in range(4):
            cx = x + 40 + j * 80; cy = GY - 230
            o.append(f'<circle cx="{cx}" cy="{cy}" r="24" fill="#f6f0c8" stroke="{INK}" stroke-width="5"/>' if (j + k) % 2 == 0 else
                     f'<rect x="{cx - 26}" y="{cy - 20}" width="52" height="40" rx="6" fill="#9aa0aa" stroke="{INK}" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#a89a80" stroke="{INK}" stroke-width="6"/>')
    return ''.join(o)


def alley_bg(t):
    """hem tro thanh pho luc chieu: hai day nha ong, day dien"""
    o = [V.sky('#e9a86a', '#f6dcaa')]
    for x, h, col in [(-300, 700, '#c9b48a'), (40, 640, '#d8c49a'), (720, 660, '#c4ae86'), (1000, 720, '#d2bc92')]:
        o.append(f'<rect x="{x}" y="{GY - 40 - h}" width="340" height="{h}" fill="{col}" stroke="{INK}" stroke-width="7"/>')
        for r_ in range(int(h // 160)):
            o.append(f'<rect x="{x + 110}" y="{GY - h + 20 + r_ * 160}" width="120" height="100" fill="#4a5a6a" stroke="{INK}" stroke-width="5"/>')
    o.append(f'<path d="M-100,560 Q540,660 1180,540 M-100,600 Q540,700 1180,590" stroke="{INK}" stroke-width="4" fill="none"/>')
    o.append(f'<path d="M380,{GY - 40} L700,{GY - 40} L1300,2000 L-200,2000 Z" fill="#9a9488"/>')
    o.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#8a847a" stroke="{INK}" stroke-width="6"/>')
    o.append(f'<rect x="420" y="{GY - 640}" width="240" height="60" rx="6" fill="#f4ecd6" stroke="{INK}" stroke-width="5"/>'
             f'<text x="540" y="{GY - 598}" font-family="{FONT}" font-weight="900" font-size="34" fill="#7a1f1a" text-anchor="middle">HẺM 404</text>')
    return ''.join(o)


BG = {'shop': lambda t: shop_bg(t), 'shop_day': lambda t: shop_bg(t, False), 'prison': prison_bg, 'court': court_bg,
      'beach': lambda t: sea_beach(t), 'beach_night': lambda t: sea_beach(t, True), 'station': station_bg, 'street': street_night,
      'room': room_bg, 'lab': lab_bg, 'paper': lambda t: paper(), 'night': lambda t: night_sky() + f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#2a3428" stroke="{INK}" stroke-width="6"/>',
      'market': market_bg, 'alley': alley_bg,
      'hall': lambda t: __import__('cung_svg').hall(t), 'hall_empty': lambda t: __import__('cung_svg').hall(t, throne=False), 'hall_dim': lambda t: __import__('cung_svg').hall(t, .45, throne=False),
      'pagoda': lambda t: __import__('cung_svg').garden(t), 'lychee': lambda t: __import__('cung_svg').lychee(t), 'lychee_dawn': lambda t: __import__('cung_svg').lychee(t, 1.0), 'lake': lambda t: __import__('cung_svg').lake(t), 'village': lambda t: V.village(t), 'village_night': lambda t: V.village(t, night=True), 'riverbank': lambda t: V.riverbank(t), 'riverbank_dawn': lambda t: V.riverbank(t, False)}


# ---------------- icon vat chung ----------------
def icon(kind, x, y, s=1.0):
    k = kind
    if k == 'suitcase':
        return (f'<rect x="{f_(x - 70 * s)}" y="{f_(y - 40 * s)}" width="{f_(140 * s)}" height="{f_(90 * s)}" rx="{f_(10 * s)}" fill="#8a5a2a" stroke="{INK}" stroke-width="{f_(7 * s)}"/>'
                f'<path d="M{f_(x - 25 * s)},{f_(y - 40 * s)} l0,{f_(-20 * s)} l{f_(50 * s)},0 l0,{f_(20 * s)}" stroke="{INK}" stroke-width="{f_(7 * s)}" fill="none"/>'
                f'<path d="M{f_(x - 70 * s)},{f_(y)} L{f_(x + 70 * s)},{f_(y)}" stroke="#d8a93a" stroke-width="{f_(6 * s)}"/>')
    if k == 'shirt':
        return (f'<path d="M{f_(x - 60 * s)},{f_(y - 40 * s)} L{f_(x - 25 * s)},{f_(y - 60 * s)} Q{f_(x)},{f_(y - 45 * s)} {f_(x + 25 * s)},{f_(y - 60 * s)} L{f_(x + 60 * s)},{f_(y - 40 * s)} L{f_(x + 45 * s)},{f_(y - 15 * s)} L{f_(x + 35 * s)},{f_(y - 20 * s)} L{f_(x + 35 * s)},{f_(y + 50 * s)} L{f_(x - 35 * s)},{f_(y + 50 * s)} L{f_(x - 35 * s)},{f_(y - 20 * s)} L{f_(x - 45 * s)},{f_(y - 15 * s)} Z" fill="#e8e2d2" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{f_(x - 18 * s)},{f_(y - 48 * s)} l{f_(36 * s)},0" stroke="#c4281f" stroke-width="{f_(6 * s)}" stroke-dasharray="{f_(6 * s)} {f_(4 * s)}"/>')
    if k == 'ticket':
        return (f'<rect x="{f_(x - 60 * s)}" y="{f_(y - 30 * s)}" width="{f_(120 * s)}" height="{f_(60 * s)}" rx="{f_(6 * s)}" fill="#f2dc8a" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
                f'<path d="M{f_(x + 20 * s)},{f_(y - 30 * s)} l0,{f_(60 * s)}" stroke="{INK}" stroke-width="{f_(3 * s)}" stroke-dasharray="{f_(6 * s)} {f_(5 * s)}"/>')
    if k == 'cigarette':
        return (f'<rect x="{f_(x - 70 * s)}" y="{f_(y - 10 * s)}" width="{f_(140 * s)}" height="{f_(20 * s)}" rx="{f_(4 * s)}" fill="#f6f2e8" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
                f'<rect x="{f_(x + 30 * s)}" y="{f_(y - 10 * s)}" width="{f_(40 * s)}" height="{f_(20 * s)}" fill="#d8a060" stroke="{INK}" stroke-width="{f_(5 * s)}"/>')
    if k in ('paper', 'letter'):
        return (f'<rect x="{f_(x - 50 * s)}" y="{f_(y - 60 * s)}" width="{f_(100 * s)}" height="{f_(120 * s)}" fill="#fbf6e6" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
                + ''.join(f'<path d="M{f_(x - 34 * s)},{f_(y - (38 - j * 20) * s)} l{f_(68 * s)},0" stroke="#8a8270" stroke-width="{f_(4 * s)}"/>' for j in range(5)))
    if k == 'book':
        return (f'<rect x="{f_(x - 50 * s)}" y="{f_(y - 65 * s)}" width="{f_(100 * s)}" height="{f_(130 * s)}" rx="{f_(6 * s)}" fill="#3a5a3a" stroke="{INK}" stroke-width="{f_(7 * s)}"/>'
                f'<rect x="{f_(x - 30 * s)}" y="{f_(y - 40 * s)}" width="{f_(60 * s)}" height="{f_(30 * s)}" fill="none" stroke="#d8a93a" stroke-width="{f_(4 * s)}"/>')
    if k == 'phone':
        return (f'<path d="M{f_(x - 60 * s)},{f_(y + 40 * s)} L{f_(x - 50 * s)},{f_(y - 10 * s)} L{f_(x + 50 * s)},{f_(y - 10 * s)} L{f_(x + 60 * s)},{f_(y + 40 * s)} Z" fill="#2a2a2a" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
                f'<path d="M{f_(x - 65 * s)},{f_(y - 25 * s)} Q{f_(x)},{f_(y - 70 * s)} {f_(x + 65 * s)},{f_(y - 25 * s)}" stroke="#2a2a2a" stroke-width="{f_(22 * s)}" fill="none" stroke-linecap="round"/>'
                f'<circle cx="{f_(x)}" cy="{f_(y + 15 * s)}" r="{f_(16 * s)}" fill="#e8e2d2"/>')
    if k == 'dna':
        o = []
        for j in range(9):
            yy = y - 70 * s + j * 18 * s; a = j * .7
            x1, x2 = x + math.sin(a) * 40 * s, x - math.sin(a) * 40 * s
            o.append(f'<path d="M{f_(x1)},{f_(yy)} L{f_(x2)},{f_(yy)}" stroke="#8a8270" stroke-width="{f_(4 * s)}"/><circle cx="{f_(x1)}" cy="{f_(yy)}" r="{f_(8 * s)}" fill="#3a7ac4" stroke="{INK}" stroke-width="{f_(3 * s)}"/><circle cx="{f_(x2)}" cy="{f_(yy)}" r="{f_(8 * s)}" fill="#c4281f" stroke="{INK}" stroke-width="{f_(3 * s)}"/>')
        return ''.join(o)
    if k == 'key':
        return (f'<circle cx="{f_(x - 40 * s)}" cy="{f_(y)}" r="{f_(26 * s)}" fill="none" stroke="#c9962e" stroke-width="{f_(12 * s)}"/>'
                f'<path d="M{f_(x - 14 * s)},{f_(y)} L{f_(x + 60 * s)},{f_(y)} M{f_(x + 40 * s)},{f_(y)} l0,{f_(20 * s)} M{f_(x + 56 * s)},{f_(y)} l0,{f_(16 * s)}" stroke="#c9962e" stroke-width="{f_(12 * s)}"/>')
    if k == 'screwdriver':
        return (f'<rect x="{f_(x - 70 * s)}" y="{f_(y - 16 * s)}" width="{f_(60 * s)}" height="{f_(32 * s)}" rx="{f_(10 * s)}" fill="#c4281f" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
                f'<path d="M{f_(x - 10 * s)},{f_(y)} L{f_(x + 70 * s)},{f_(y)}" stroke="{INK}" stroke-width="{f_(12 * s)}"/><path d="M{f_(x - 10 * s)},{f_(y)} L{f_(x + 70 * s)},{f_(y)}" stroke="#c9ccd4" stroke-width="{f_(6 * s)}"/>')
    if k == 'thread':
        return f'<rect x="{f_(x - 30 * s)}" y="{f_(y - 45 * s)}" width="{f_(60 * s)}" height="{f_(90 * s)}" rx="{f_(8 * s)}" fill="#e8822a" stroke="{INK}" stroke-width="{f_(6 * s)}"/>' + ''.join(f'<path d="M{f_(x - 30 * s)},{f_(y - 30 * s + j * 14 * s)} l{f_(60 * s)},0" stroke="#b85e1a" stroke-width="{f_(3 * s)}"/>' for j in range(5))
    if k == 'coin':
        return f'<circle cx="{f_(x)}" cy="{f_(y)}" r="{f_(45 * s)}" fill="#d8a93a" stroke="{INK}" stroke-width="{f_(7 * s)}"/><circle cx="{f_(x)}" cy="{f_(y)}" r="{f_(30 * s)}" fill="none" stroke="#8a6a2a" stroke-width="{f_(4 * s)}"/>'
    if k == 'comb':
        return (f'<rect x="{f_(x - 70 * s)}" y="{f_(y - 20 * s)}" width="{f_(140 * s)}" height="{f_(22 * s)}" rx="{f_(6 * s)}" fill="#6a4a2a" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
                + ''.join(f'<path d="M{f_(x - 62 * s + j * 12 * s)},{f_(y)} l0,{f_(26 * s)}" stroke="#6a4a2a" stroke-width="{f_(5 * s)}"/>' for j in range(11)))
    if k == 'map':
        return (f'<path d="M{f_(x - 70 * s)},{f_(y - 50 * s)} L{f_(x - 20 * s)},{f_(y - 60 * s)} L{f_(x + 25 * s)},{f_(y - 50 * s)} L{f_(x + 70 * s)},{f_(y - 60 * s)} L{f_(x + 70 * s)},{f_(y + 50 * s)} L{f_(x + 25 * s)},{f_(y + 60 * s)} L{f_(x - 20 * s)},{f_(y + 50 * s)} L{f_(x - 70 * s)},{f_(y + 60 * s)} Z" fill="#e8dcb0" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
                f'<circle cx="{f_(x + 10 * s)}" cy="{f_(y)}" r="{f_(12 * s)}" fill="#c4281f" stroke="{INK}" stroke-width="{f_(4 * s)}"/>')
    if k == 'clock':
        return f'<circle cx="{f_(x)}" cy="{f_(y)}" r="{f_(55 * s)}" fill="#f6f0dc" stroke="{INK}" stroke-width="{f_(7 * s)}"/><path d="M{f_(x)},{f_(y)} l0,{f_(-36 * s)} M{f_(x)},{f_(y)} l{f_(26 * s)},{f_(10 * s)}" stroke="{INK}" stroke-width="{f_(7 * s)}" stroke-linecap="round"/>'
    if k == 'ring':
        return f'<circle cx="{f_(x)}" cy="{f_(y + 10 * s)}" r="{f_(38 * s)}" fill="none" stroke="#d8a93a" stroke-width="{f_(12 * s)}"/><path d="M{f_(x - 16 * s)},{f_(y - 34 * s)} l{f_(16 * s)},{f_(-20 * s)} l{f_(16 * s)},{f_(20 * s)} Z" fill="#9fd8f5" stroke="{INK}" stroke-width="{f_(4 * s)}"/>'
    if k == 'car':
        return (f'<path d="M{f_(x - 90 * s)},{f_(y + 20 * s)} L{f_(x - 80 * s)},{f_(y - 20 * s)} L{f_(x - 40 * s)},{f_(y - 25 * s)} L{f_(x - 20 * s)},{f_(y - 60 * s)} L{f_(x + 40 * s)},{f_(y - 60 * s)} L{f_(x + 60 * s)},{f_(y - 25 * s)} L{f_(x + 90 * s)},{f_(y - 15 * s)} L{f_(x + 90 * s)},{f_(y + 20 * s)} Z" fill="#3a4a5a" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<circle cx="{f_(x - 50 * s)}" cy="{f_(y + 22 * s)}" r="{f_(18 * s)}" fill="#222" stroke="{INK}" stroke-width="{f_(4 * s)}"/><circle cx="{f_(x + 55 * s)}" cy="{f_(y + 22 * s)}" r="{f_(18 * s)}" fill="#222" stroke="{INK}" stroke-width="{f_(4 * s)}"/>')
    if k == 'footprint':
        return ''.join(f'<g transform="translate({f_(x + dx * s)} {f_(y + dy * s)}) rotate({rt})"><ellipse cx="0" cy="0" rx="{f_(20 * s)}" ry="{f_(42 * s)}" fill="#6e5a42" stroke="{INK}" stroke-width="{f_(4 * s)}"/>'
                       + ''.join(f'<circle cx="{f_((j - 2) * 9 * s)}" cy="{f_(-52 * s - abs(j - 2) * -3 * s)}" r="{f_(6 * s)}" fill="#6e5a42" stroke="{INK}" stroke-width="{f_(2 * s)}"/>' for j in range(5)) + '</g>'
                       for dx, dy, rt in ((-30, 20, -8), (30, -30, 8)))
    if k == 'fingerprint':
        return ''.join(f'<ellipse cx="{f_(x)}" cy="{f_(y)}" rx="{f_((14 + j * 10) * s)}" ry="{f_((20 + j * 12) * s)}" fill="none" stroke="#3a5a8a" stroke-width="{f_(5 * s)}" stroke-dasharray="{f_(18 * s)} {f_(6 * s)}"/>' for j in range(4))
    if k == 'bottle':
        return (f'<path d="M{f_(x - 18 * s)},{f_(y - 70 * s)} l{f_(36 * s)},0 l0,{f_(30 * s)} q{f_(22 * s)},{f_(14 * s)} {f_(22 * s)},{f_(40 * s)} l0,{f_(70 * s)} l{f_(-80 * s)},0 l0,{f_(-70 * s)} q0,{f_(-26 * s)} {f_(22 * s)},{f_(-40 * s)} Z" fill="#4a8a4a" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<rect x="{f_(x - 30 * s)}" y="{f_(y + 10 * s)}" width="{f_(60 * s)}" height="{f_(36 * s)}" fill="#f2dc8a" stroke="{INK}" stroke-width="{f_(3 * s)}"/>')
    if k == 'recorder':
        return (f'<rect x="{f_(x - 55 * s)}" y="{f_(y - 75 * s)}" width="{f_(110 * s)}" height="{f_(150 * s)}" rx="{f_(12 * s)}" fill="#3a3a44" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
                f'<rect x="{f_(x - 38 * s)}" y="{f_(y - 58 * s)}" width="{f_(76 * s)}" height="{f_(40 * s)}" fill="#9fd8a0" stroke="{INK}" stroke-width="{f_(4 * s)}"/>'
                f'<circle cx="{f_(x)}" cy="{f_(y + 30 * s)}" r="{f_(24 * s)}" fill="#c4281f" stroke="{INK}" stroke-width="{f_(4 * s)}"/>')
    if k == 'redbook':
        return (f'<rect x="{f_(x - 55 * s)}" y="{f_(y - 70 * s)}" width="{f_(110 * s)}" height="{f_(140 * s)}" rx="{f_(5 * s)}" fill="#c4281f" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
                f'<circle cx="{f_(x)}" cy="{f_(y - 15 * s)}" r="{f_(22 * s)}" fill="none" stroke="#f2dc8a" stroke-width="{f_(5 * s)}"/>'
                f'<path d="M{f_(x - 30 * s)},{f_(y + 30 * s)} l{f_(60 * s)},0" stroke="#f2dc8a" stroke-width="{f_(5 * s)}"/>')
    if k == 'bike':
        return (f'<circle cx="{f_(x - 55 * s)}" cy="{f_(y + 25 * s)}" r="{f_(38 * s)}" fill="none" stroke="{INK}" stroke-width="{f_(7 * s)}"/><circle cx="{f_(x + 55 * s)}" cy="{f_(y + 25 * s)}" r="{f_(38 * s)}" fill="none" stroke="{INK}" stroke-width="{f_(7 * s)}"/>'
                f'<path d="M{f_(x - 55 * s)},{f_(y + 25 * s)} L{f_(x - 10 * s)},{f_(y - 25 * s)} L{f_(x + 40 * s)},{f_(y - 25 * s)} L{f_(x + 55 * s)},{f_(y + 25 * s)} M{f_(x - 10 * s)},{f_(y - 25 * s)} L{f_(x)},{f_(y + 25 * s)} L{f_(x + 40 * s)},{f_(y - 25 * s)}" stroke="#2e5a8a" stroke-width="{f_(7 * s)}" fill="none"/>'
                f'<rect x="{f_(x + 30 * s)}" y="{f_(y - 80 * s)}" width="{f_(46 * s)}" height="{f_(54 * s)}" rx="{f_(6 * s)}" fill="#f6f2e8" stroke="{INK}" stroke-width="{f_(4 * s)}"/>'
                f'<rect x="{f_(x - 80 * s)}" y="{f_(y - 80 * s)}" width="{f_(46 * s)}" height="{f_(54 * s)}" rx="{f_(6 * s)}" fill="#f6f2e8" stroke="{INK}" stroke-width="{f_(4 * s)}"/>')
    if k == 'scale':
        return (f'<path d="M{f_(x)},{f_(y - 70 * s)} L{f_(x)},{f_(y + 60 * s)} M{f_(x - 40 * s)},{f_(y + 60 * s)} l{f_(80 * s)},0 M{f_(x - 70 * s)},{f_(y - 50 * s)} L{f_(x + 70 * s)},{f_(y - 50 * s)}" stroke="#8a6a2a" stroke-width="{f_(8 * s)}"/>'
                f'<path d="M{f_(x - 95 * s)},{f_(y)} q{f_(25 * s)},{f_(30 * s)} {f_(50 * s)},0 Z M{f_(x + 45 * s)},{f_(y)} q{f_(25 * s)},{f_(30 * s)} {f_(50 * s)},0 Z" fill="#d8a93a" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
                f'<path d="M{f_(x - 70 * s)},{f_(y - 50 * s)} L{f_(x - 95 * s)},{f_(y)} M{f_(x - 70 * s)},{f_(y - 50 * s)} L{f_(x - 45 * s)},{f_(y)} M{f_(x + 70 * s)},{f_(y - 50 * s)} L{f_(x + 45 * s)},{f_(y)} M{f_(x + 70 * s)},{f_(y - 50 * s)} L{f_(x + 95 * s)},{f_(y)}" stroke="#8a6a2a" stroke-width="{f_(3 * s)}"/>')
    if k in ('headlight', 'headlight_crack'):   # den pha xe may tron; ban 'crack' co vet ran o goc phai
        o = (f'<circle cx="{f_(x)}" cy="{f_(y)}" r="{f_(62 * s)}" fill="#9aa0aa" stroke="{INK}" stroke-width="{f_(7 * s)}"/>'
             f'<circle cx="{f_(x)}" cy="{f_(y)}" r="{f_(46 * s)}" fill="#f6f0c8" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
             f'<path d="M{f_(x - 30 * s)},{f_(y - 10 * s)} l{f_(60 * s)},0 M{f_(x - 26 * s)},{f_(y + 12 * s)} l{f_(52 * s)},0" stroke="#d8cf9a" stroke-width="{f_(4 * s)}"/>'
             f'<circle cx="{f_(x - 14 * s)}" cy="{f_(y - 22 * s)}" r="{f_(9 * s)}" fill="#fff"/>')
        if k == 'headlight_crack':
            o += (f'<path d="M{f_(x + 44 * s)},{f_(y - 14 * s)} L{f_(x + 22 * s)},{f_(y - 4 * s)} L{f_(x + 30 * s)},{f_(y + 10 * s)} L{f_(x + 10 * s)},{f_(y + 22 * s)} '
                  f'M{f_(x + 22 * s)},{f_(y - 4 * s)} L{f_(x + 8 * s)},{f_(y - 22 * s)} M{f_(x + 30 * s)},{f_(y + 10 * s)} L{f_(x + 42 * s)},{f_(y + 24 * s)}" stroke="#c4281f" stroke-width="{f_(5 * s)}" fill="none" stroke-linecap="round"/>')
        return o
    if k == 'motorbike':   # xe may do (Win) nhin ngang, den tron phia truoc
        return (f'<circle cx="{f_(x - 70 * s)}" cy="{f_(y + 40 * s)}" r="{f_(36 * s)}" fill="#2a2a2a" stroke="{INK}" stroke-width="{f_(6 * s)}"/><circle cx="{f_(x - 70 * s)}" cy="{f_(y + 40 * s)}" r="{f_(14 * s)}" fill="#bbb"/>'
                f'<circle cx="{f_(x + 75 * s)}" cy="{f_(y + 40 * s)}" r="{f_(36 * s)}" fill="#2a2a2a" stroke="{INK}" stroke-width="{f_(6 * s)}"/><circle cx="{f_(x + 75 * s)}" cy="{f_(y + 40 * s)}" r="{f_(14 * s)}" fill="#bbb"/>'
                f'<path d="M{f_(x - 95 * s)},{f_(y + 5 * s)} L{f_(x - 40 * s)},{f_(y - 30 * s)} L{f_(x + 20 * s)},{f_(y - 30 * s)} L{f_(x + 40 * s)},{f_(y + 10 * s)} L{f_(x - 20 * s)},{f_(y + 20 * s)} Z" fill="#c4281f" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<rect x="{f_(x - 75 * s)}" y="{f_(y - 48 * s)}" width="{f_(70 * s)}" height="{f_(18 * s)}" rx="{f_(8 * s)}" fill="#2a2a2a" stroke="{INK}" stroke-width="{f_(4 * s)}"/>'
                f'<path d="M{f_(x + 40 * s)},{f_(y + 10 * s)} L{f_(x + 60 * s)},{f_(y - 60 * s)} M{f_(x + 60 * s)},{f_(y - 60 * s)} l{f_(-26 * s)},{f_(-6 * s)} M{f_(x + 62 * s)},{f_(y - 40 * s)} L{f_(x + 75 * s)},{f_(y + 40 * s)}" stroke="{INK}" stroke-width="{f_(8 * s)}" stroke-linecap="round"/>'
                f'<circle cx="{f_(x + 80 * s)}" cy="{f_(y - 48 * s)}" r="{f_(18 * s)}" fill="#f6f0c8" stroke="{INK}" stroke-width="{f_(5 * s)}"/>')
    if k == 'watch':
        return (f'<rect x="{f_(x - 20 * s)}" y="{f_(y - 80 * s)}" width="{f_(40 * s)}" height="{f_(160 * s)}" rx="{f_(8 * s)}" fill="#b8b8c0" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
                f'<circle cx="{f_(x)}" cy="{f_(y)}" r="{f_(42 * s)}" fill="#f6f6f0" stroke="{INK}" stroke-width="{f_(7 * s)}"/>'
                f'<path d="M{f_(x)},{f_(y)} l0,{f_(-26 * s)} M{f_(x)},{f_(y)} l{f_(18 * s)},{f_(8 * s)}" stroke="{INK}" stroke-width="{f_(5 * s)}" stroke-linecap="round"/>')
    if k == 'gold':
        return (f'<path d="M{f_(x - 70 * s)},{f_(y + 30 * s)} L{f_(x - 45 * s)},{f_(y - 30 * s)} L{f_(x + 45 * s)},{f_(y - 30 * s)} L{f_(x + 70 * s)},{f_(y + 30 * s)} Z" fill="#e8b830" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{f_(x - 30 * s)},{f_(y - 14 * s)} l{f_(40 * s)},0" stroke="#fff3b0" stroke-width="{f_(6 * s)}" stroke-linecap="round"/>')
    if k == 'cap':   # mu luoi trai mau den nhin nghieng
        return (f'<path d="M{f_(x - 60 * s)},{f_(y + 10 * s)} Q{f_(x - 58 * s)},{f_(y - 62 * s)} {f_(x + 5 * s)},{f_(y - 62 * s)} Q{f_(x + 62 * s)},{f_(y - 58 * s)} {f_(x + 60 * s)},{f_(y + 10 * s)} Z" fill="#232326" stroke="{INK}" stroke-width="{f_(7 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{f_(x + 40 * s)},{f_(y + 10 * s)} Q{f_(x + 100 * s)},{f_(y + 4 * s)} {f_(x + 125 * s)},{f_(y + 26 * s)} Q{f_(x + 80 * s)},{f_(y + 34 * s)} {f_(x + 40 * s)},{f_(y + 24 * s)} Z" fill="#1a1a1c" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{f_(x - 60 * s)},{f_(y + 10 * s)} L{f_(x + 60 * s)},{f_(y + 10 * s)}" stroke="#55555c" stroke-width="{f_(6 * s)}"/>'
                f'<circle cx="{f_(x + 2 * s)}" cy="{f_(y - 62 * s)}" r="{f_(7 * s)}" fill="#55555c" stroke="{INK}" stroke-width="{f_(3 * s)}"/>'
                f'<path d="M{f_(x - 30 * s)},{f_(y - 40 * s)} Q{f_(x - 20 * s)},{f_(y - 52 * s)} {f_(x)},{f_(y - 54 * s)}" stroke="#4a4a52" stroke-width="{f_(5 * s)}" fill="none" stroke-linecap="round"/>')
    if k == 'helmet':   # mu bao hiem nua dau
        return (f'<path d="M{f_(x - 70 * s)},{f_(y + 20 * s)} Q{f_(x - 70 * s)},{f_(y - 70 * s)} {f_(x)},{f_(y - 70 * s)} Q{f_(x + 70 * s)},{f_(y - 70 * s)} {f_(x + 70 * s)},{f_(y + 20 * s)} Z" fill="#2e6ab0" stroke="{INK}" stroke-width="{f_(7 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{f_(x - 74 * s)},{f_(y + 20 * s)} L{f_(x + 74 * s)},{f_(y + 20 * s)}" stroke="{INK}" stroke-width="{f_(12 * s)}" stroke-linecap="round"/>'
                f'<path d="M{f_(x - 40 * s)},{f_(y - 40 * s)} Q{f_(x - 20 * s)},{f_(y - 58 * s)} {f_(x + 10 * s)},{f_(y - 58 * s)}" stroke="#a8c8f0" stroke-width="{f_(8 * s)}" fill="none" stroke-linecap="round"/>'
                f'<path d="M{f_(x - 50 * s)},{f_(y + 26 * s)} Q{f_(x)},{f_(y + 70 * s)} {f_(x + 50 * s)},{f_(y + 26 * s)}" stroke="#5a4a3a" stroke-width="{f_(5 * s)}" fill="none"/>')
    if k == 'mask':   # khau trang
        return (f'<path d="M{f_(x - 60 * s)},{f_(y - 30 * s)} Q{f_(x)},{f_(y - 46 * s)} {f_(x + 60 * s)},{f_(y - 30 * s)} L{f_(x + 56 * s)},{f_(y + 30 * s)} Q{f_(x)},{f_(y + 56 * s)} {f_(x - 56 * s)},{f_(y + 30 * s)} Z" fill="#5a6a7a" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{f_(x - 60 * s)},{f_(y - 24 * s)} q{f_(-40 * s)},{f_(20 * s)} 0,{f_(44 * s)} M{f_(x + 60 * s)},{f_(y - 24 * s)} q{f_(40 * s)},{f_(20 * s)} 0,{f_(44 * s)}" stroke="#e8e2d2" stroke-width="{f_(5 * s)}" fill="none"/>'
                + ''.join(f'<path d="M{f_(x - 44 * s)},{f_(y + (j * 16 - 12) * s)} l{f_(88 * s)},0" stroke="#46525e" stroke-width="{f_(3 * s)}"/>' for j in range(3)))
    if k == 'cards':   # bo bai (co bac)
        return ''.join(f'<g transform="rotate({r} {f_(x)} {f_(y + 60 * s)})"><rect x="{f_(x - 36 * s)}" y="{f_(y - 52 * s)}" width="{f_(72 * s)}" height="{f_(104 * s)}" rx="{f_(8 * s)}" fill="#fbf6e6" stroke="{INK}" stroke-width="{f_(5 * s)}"/>'
                       f'<text x="{f_(x)}" y="{f_(y + 16 * s)}" font-family="{FONT}" font-weight="900" font-size="{f_(46 * s)}" fill="{c}" text-anchor="middle">{g}</text></g>'
                       for r, c, g in ((-18, '#111', '♠'), (0, '#c4281f', '♥'), (18, '#111', '♣')))
    if k in ('dog', 'dog_sad', 'dog_tied'):   # cau Vang (Lao Hac): cho vang ngoi nhin phai; sad = tai cup, mat nguoc len; tied = nam, day trung chan
        return dog_svg(x, y, s, k)
    if k == 'bowl':   # bat com sanh
        return (f'<path d="M{f_(x - 60 * s)},{f_(y - 20 * s)} Q{f_(x)},{f_(y + 60 * s)} {f_(x + 60 * s)},{f_(y - 20 * s)} Z" fill="#f4f0e6" stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{f_(x - 48 * s)},{f_(y - 4 * s)} Q{f_(x)},{f_(y + 22 * s)} {f_(x + 48 * s)},{f_(y - 4 * s)}" stroke="#3a6ab0" stroke-width="{f_(5 * s)}" fill="none"/>'
                f'<ellipse cx="{f_(x)}" cy="{f_(y - 22 * s)}" rx="{f_(52 * s)}" ry="{f_(14 * s)}" fill="#fbfaf4" stroke="{INK}" stroke-width="{f_(5 * s)}"/>')
    if k == 'plate':   # bien so xe
        return (f'<rect x="{f_(x - 70 * s)}" y="{f_(y - 36 * s)}" width="{f_(140 * s)}" height="{f_(72 * s)}" rx="{f_(6 * s)}" fill="#f6f6f0" stroke="{INK}" stroke-width="{f_(6 * s)}"/>'
                f'<text x="{f_(x)}" y="{f_(y + 14 * s)}" font-family="{FONT}" font-weight="900" font-size="{f_(40 * s)}" fill="#111" text-anchor="middle">79-?</text>')
    return f'<circle cx="{f_(x)}" cy="{f_(y)}" r="{f_(40 * s)}" fill="#ddd" stroke="{INK}" stroke-width="6"/>'


def dog_svg(x, y, s=1.0, k='dog'):
    """Cau Vang: cho vang viền muc dam, vong co do (dau rieng). (x, y) = giua than; chan cham y + 75*s."""
    P = lambda dx, dy: f'{f_(x + dx * s)},{f_(y + dy * s)}'
    W = f'stroke="{INK}" stroke-width="{f_(6 * s)}" stroke-linejoin="round" stroke-linecap="round"'
    FUR, FUR2 = '#d9a441', '#b8822a'
    o = []
    if k == 'dog_tied':   # nam nghieng, 4 chan bi trói
        o.append(f'<path d="M{P(-95, 40)} Q{P(-130, 10)} {P(-150, 30)}" fill="none" {W}/>')
        o.append(f'<ellipse cx="{f_(x - 10 * s)}" cy="{f_(y + 40 * s)}" rx="{f_(95 * s)}" ry="{f_(38 * s)}" fill="{FUR}" {W}/>')
        for dx in (-50, -25, 35, 60):
            o.append(f'<path d="M{P(dx, 65)} L{P(dx + 18, 92)}" {W} fill="none"/>')
        o.append(f'<path d="M{P(-60, 88)} Q{P(0, 104)} {P(85, 88)}" stroke="#8a6a3a" stroke-width="{f_(9 * s)}" fill="none"/>')
        hx, hy = 95, 20
        o.append(f'<circle cx="{f_(x + hx * s)}" cy="{f_(y + hy * s)}" r="{f_(40 * s)}" fill="{FUR}" {W}/>')
        o.append(f'<ellipse cx="{f_(x + (hx + 38) * s)}" cy="{f_(y + (hy + 14) * s)}" rx="{f_(26 * s)}" ry="{f_(17 * s)}" fill="#e8bd66" {W}/>')
        o.append(f'<circle cx="{f_(x + (hx + 60) * s)}" cy="{f_(y + (hy + 8) * s)}" r="{f_(8 * s)}" fill="{INK}"/>')
        o.append(f'<path d="M{P(hx - 25, hy - 30)} Q{P(hx - 50, hy - 5)} {P(hx - 35, hy + 25)}" fill="{FUR2}" {W}/>')
        o.append(f'<circle cx="{f_(x + (hx + 12) * s)}" cy="{f_(y + (hy - 10) * s)}" r="{f_(7 * s)}" fill="{INK}"/><circle cx="{f_(x + (hx + 14) * s)}" cy="{f_(y + (hy - 13) * s)}" r="{f_(2.5 * s)}" fill="#fff"/>')
        o.append(f'<path d="M{P(hx + 2, hy - 24)} L{P(hx + 22, hy - 18)}" {W} fill="none"/>')
        o.append(f'<path d="M{P(hx - 30, hy + 10)} Q{P(hx - 20, hy + 30)} {P(hx - 5, hy + 38)}" stroke="#c4281f" stroke-width="{f_(9 * s)}" fill="none"/>')
        return ''.join(o)
    sad = k == 'dog_sad'
    tail = f'M{P(-70, 30)} Q{P(-120, 40)} {P(-125, 70)}' if sad else f'M{P(-70, 10)} Q{P(-120, -10)} {P(-110, -60)}'
    o.append(f'<path d="{tail}" fill="none" stroke="{INK}" stroke-width="{f_(16 * s)}" stroke-linecap="round"/><path d="{tail}" fill="none" stroke="{FUR}" stroke-width="{f_(8 * s)}" stroke-linecap="round"/>')
    o.append(f'<path d="M{P(-75, 70)} Q{P(-90, -10)} {P(-10, -45)} Q{P(50, -55)} {P(55, 10)} L{P(50, 75)} Z" fill="{FUR}" {W}/>')
    o.append(f'<ellipse cx="{f_(x - 40 * s)}" cy="{f_(y + 40 * s)}" rx="{f_(42 * s)}" ry="{f_(36 * s)}" fill="{FUR}" {W}/>')
    o.append(f'<path d="M{P(-70, 75)} L{P(-25, 75)}" {W} fill="none"/>')
    for dx in (18, 42):
        o.append(f'<path d="M{P(dx, 0)} L{P(dx, 75)}" stroke="{INK}" stroke-width="{f_(22 * s)}" stroke-linecap="round"/><path d="M{P(dx, 0)} L{P(dx, 75)}" stroke="{FUR}" stroke-width="{f_(11 * s)}" stroke-linecap="round"/>')
    hx, hy = (45, -60) if sad else (45, -85)
    o.append(f'<circle cx="{f_(x + hx * s)}" cy="{f_(y + hy * s)}" r="{f_(44 * s)}" fill="{FUR}" {W}/>')
    o.append(f'<ellipse cx="{f_(x + (hx + 42) * s)}" cy="{f_(y + (hy + 16) * s)}" rx="{f_(28 * s)}" ry="{f_(19 * s)}" fill="#e8bd66" {W}/>')
    o.append(f'<circle cx="{f_(x + (hx + 66) * s)}" cy="{f_(y + (hy + 9) * s)}" r="{f_(9 * s)}" fill="{INK}"/>')
    o.append(f'<path d="M{P(hx + 42, hy + 30)} Q{P(hx + 52, hy + 36)} {P(hx + 60, hy + 30)}" {W} fill="none"/>' if not sad else
             f'<path d="M{P(hx + 40, hy + 36)} Q{P(hx + 50, hy + 28)} {P(hx + 60, hy + 34)}" {W} fill="none"/>')
    if sad:   # tai cup sat dau, mat nguoc len, may chau
        o.append(f'<path d="M{P(hx - 30, hy - 25)} Q{P(hx - 55, hy + 5)} {P(hx - 38, hy + 40)} Q{P(hx - 20, hy + 10)} {P(hx - 12, hy - 30)} Z" fill="{FUR2}" {W}/>')
        o.append(f'<circle cx="{f_(x + (hx + 14) * s)}" cy="{f_(y + (hy - 8) * s)}" r="{f_(8 * s)}" fill="{INK}"/><circle cx="{f_(x + (hx + 16) * s)}" cy="{f_(y + (hy - 12) * s)}" r="{f_(3 * s)}" fill="#fff"/>')
        o.append(f'<path d="M{P(hx + 2, hy - 20)} L{P(hx + 24, hy - 28)}" {W} fill="none"/>')
        o.append(f'<path d="M{P(hx + 20, hy + 2)} q{f_(-3 * s)},{f_(12 * s)} 0,{f_(16 * s)} q{f_(3 * s)},{f_(-4 * s)} 0,{f_(-16 * s)}" fill="#7fc3f0" stroke="{INK}" stroke-width="{f_(2.5 * s)}"/>')
    else:     # tai vềnh, mat tron vui
        o.append(f'<path d="M{P(hx - 32, hy - 20)} L{P(hx - 30, hy - 72)} L{P(hx - 2, hy - 38)} Z" fill="{FUR2}" {W}/>')
        o.append(f'<circle cx="{f_(x + (hx + 16) * s)}" cy="{f_(y + (hy - 10) * s)}" r="{f_(8 * s)}" fill="{INK}"/><circle cx="{f_(x + (hx + 18) * s)}" cy="{f_(y + (hy - 13) * s)}" r="{f_(3 * s)}" fill="#fff"/>')
    o.append(f'<path d="M{P(hx - 34, hy + 22)} Q{P(hx - 10, hy + 46)} {P(hx + 22, hy + 38)}" stroke="#c4281f" stroke-width="{f_(10 * s)}" fill="none" stroke-linecap="round"/>')
    return ''.join(o)


def suitcase_open(x, y, q):
    lid = -100 * q
    return (f'<rect x="{x - 150}" y="{y - 60}" width="300" height="120" rx="12" fill="#8a5a2a" stroke="{INK}" stroke-width="8"/>'
            f'<g transform="rotate({f_(lid)} {x - 150} {y - 60})"><rect x="{x - 150}" y="{y - 120}" width="300" height="60" rx="12" fill="#9a6a34" stroke="{INK}" stroke-width="8"/></g>')


CUNG = ('beach', 'station', 'items', 'scrap', 'car', 'code', 'door', 'board', 'timeline', 'spy', 'lab', 'tree', 'grave', 'stage', 'petition')


def beat(sh, t, d):
    ty = sh['type']; s = []; cam = (1.0, 540, 830); shake = 0.0; flash = 0.0
    if ty == 'beach':
        s.append(sea_beach(t, sh.get('night', False)))
        who = sh.get('who')
        if who:   # nguoi ngoi tua tuong (an duoi tuong: chi thay than tren)
            s.append(ch(who, 560, GY + 40, sh.get('D', 160), -1, sh.get('expr', 'sleep'), [(.55, .05, sh.get('prop'))] if sh.get('prop') else None, t=0, tag=sh.get('tag', True), lean=-6))
        for k, p in enumerate(sh.get('people', [])):
            ta = V.at(sh, int(p.get('at', 0)), 0.2)
            if t < ta: continue
            q = (t - ta) / max(1.0, d - ta); x = lerp(p.get('x0', -150), p.get('x1', 300), ease(q)); bob = V.walk(t)
            s.append(ch(p['c'], x, GY + 120 - bob, p.get('D', 150), 1 if p.get('x1', 300) > p.get('x0', -150) else -1, p.get('expr', 'normal'), t=t, tag=p.get('tag', False)))
        cam = (lerp(1.0, 1.12, ease(t / max(1, d))), 560, 980)
    elif ty == 'station':
        s.append(station_bg(t))
        s.append(f'<rect x="300" y="{GY - 260}" width="480" height="220" fill="#6b4a2a" stroke="{INK}" stroke-width="8"/><rect x="280" y="{GY - 280}" width="520" height="30" fill="#8a6a46" stroke="{INK}" stroke-width="7"/>')
        tb = V.at(sh, int(sh.get('bag_at', 1)), d * .4)
        if t >= tb:
            s.append(pop(540, GY - 330, (t - tb) / .4, icon('suitcase', 540, GY - 330, 1.4)))
            if sh.get('cut') and t >= tb + .8:
                s.append(f'<g transform="translate(640 {GY - 380}) rotate(14)"><rect x="-50" y="-22" width="100" height="44" fill="#f6f2e8" stroke="{INK}" stroke-width="5" stroke-dasharray="8 6"/><path d="M-60,-30 L60,30" stroke="#c4281f" stroke-width="8"/></g>')
        if sh.get('who'): s.append(ch(sh['who'], 880, GY + 40, 160, -1, sh.get('expr', 'surprised') if t >= tb else 'normal', t=t))
        cam = (1.0, 560, 900)
    elif ty == 'items':
        s.append(paper())
        it = sh.get('items', [])
        cols = 2 if len(it) > 3 else 1
        for k, x in enumerate(it):
            ta = V.at(sh, int(x.get('at', k)), .3 + k * 1.2)
            if t < ta: continue
            cx = (300 + 480 * (k % 2)) if cols == 2 else 540; cy = 700 + (k // cols) * 210 if cols == 2 else 700 + k * 200
            inner = icon(x.get('icon', 'paper'), cx, cy - 20, .9) + f'<text x="{cx}" y="{cy + 75}" font-family="{FONT}" font-weight="900" font-size="34" fill="#5a1a14" text-anchor="middle">{esc(x.get("t", ""))}</text>'
            s.append(pop(cx, cy, (t - ta) / .35, inner))
            if x.get('x'):   # gach cheo: thieu / bi cat
                q = ease((t - ta - .5) / .3)
                if q > 0: s.append(f'<path d="M{cx - 80},{cy - 80} L{f_(cx - 80 + 160 * q)},{f_(cy - 80 + 120 * q)}" stroke="#c4281f" stroke-width="12" stroke-linecap="round"/>')
        cam = (1.0, 540, 900)
    elif ty == 'scrap':
        s.append(paper('#e6dcc0'))
        q = ease((t - .3) / 1.2)
        w = 80 + 520 * q
        s.append(f'<rect x="{f_(540 - w / 2)}" y="760" width="{f_(w)}" height="180" fill="#fbf6e6" stroke="{INK}" stroke-width="7"/>'
                 f'<ellipse cx="{f_(540 - w / 2)}" cy="850" rx="22" ry="92" fill="#e8dcc0" stroke="{INK}" stroke-width="6"/><ellipse cx="{f_(540 + w / 2)}" cy="850" rx="22" ry="92" fill="#e8dcc0" stroke="{INK}" stroke-width="6"/>')
        if q > .8:
            s.append(f'<text x="540" y="880" font-family="Georgia, serif" font-style="italic" font-weight="700" font-size="84" fill="#2a1a10" text-anchor="middle" opacity="{f_(min(1, (q - .8) * 5))}">{esc(sh.get("word", ""))}</text>')
        tm = V.at(sh, int(sh.get('mean_at', 1)), d * .5)
        if t >= tm and sh.get('mean'):
            s.append(pop(540, 1110, (t - tm) / .35, card(540, 1110, sh['mean'], '#c4281f', '#fff', 46)))
        cam = (lerp(1.0, 1.1, ease(t / max(1, d))), 540, 940)
    elif ty == 'car':
        s.append(street_night(t))
        s.append(icon('car', 540, GY - 90, 3.2))
        to = V.at(sh, int(sh.get('open_at', 1)), d * .45)
        if t >= to:
            q = ease((t - to) / .5)
            s.append(f'<path d="M560,{GY - 260} L{f_(560 + 150 * q)},{GY - 300} L{f_(560 + 150 * q)},{GY - 120} L560,{GY - 100} Z" fill="#4a5a6a" stroke="{INK}" stroke-width="7"/>')
            gl = .5 + .5 * abs(osc(t, .8))
            s.append(f'<circle cx="460" cy="{GY - 190}" r="{f_(110 * gl)}" fill="#fff6c8" opacity=".35"/>' + icon('book', 460, GY - 190, .8))
        if sh.get('who'):
            s.append(ch(sh['who'], 860, GY + 60, 170, -1, 'surprised' if t >= to else 'normal', t=t))
        cam = (1.0, 560, 920)
    elif ty == 'code':
        s.append(paper('#e6dcc0'))
        s.append(f'<rect x="150" y="640" width="780" height="620" fill="#fbf6e6" stroke="{INK}" stroke-width="8"/>')
        lines = sh.get('lines', [])
        n = sum(len(l) for l in lines); shown = int(n * min(1, t / max(1.0, d * .6)))
        cnt = 0
        for j, ln in enumerate(lines):
            vis = ln[:max(0, shown - cnt)]; cnt += len(ln)
            s.append(f'<text x="200" y="{740 + j * 95}" font-family="Courier New, monospace" font-weight="700" font-size="64" fill="#2a1a10" xml:space="preserve">{esc(vis)}</text>')
        mx = 300 + 400 * (.5 + .5 * osc(t, .25)); my = 760 + 160 * (.5 + .5 * osc(t, .17))
        s.append(f'<circle cx="{f_(mx)}" cy="{f_(my)}" r="90" fill="#cfe8f4" fill-opacity=".35" stroke="{INK}" stroke-width="12"/><path d="M{f_(mx + 64)},{f_(my + 64)} l90,90" stroke="{INK}" stroke-width="24" stroke-linecap="round"/>')
        if sh.get('stamp'):
            tq = V.at(sh, -1, d * .7)
            from cung_svg import stamp
            s.append(stamp(540, 1180, sh['stamp'], (t - tq) / .4))
        cam = (1.0, 540, 940)
    elif ty == 'door':
        s.append(street_night(t))
        s.append(f'<rect x="420" y="{GY - 360}" width="240" height="320" fill="#6b4524" stroke="{INK}" stroke-width="8"/>')
        to = V.at(sh, int(sh.get('open_at', 1)), d * .4); q = ease((t - to) / .5)
        if q > 0:
            s.append(f'<rect x="420" y="{GY - 360}" width="{f_(240 * (1 - .8 * q))}" height="320" fill="#5a3a1e" stroke="{INK}" stroke-width="8"/><rect x="{f_(420 + 240 * (1 - .8 * q))}" y="{GY - 360}" width="{f_(240 * .8 * q)}" height="320" fill="#ffd98a" opacity=".55"/>')
            tk = V.at(sh, int(sh.get('shake_at', 99)), 1e9)
            hr = 10 * osc(t, 2.2) if t >= tk else 0
            s.append(ch(sh.get('who', 'yta'), 560, GY - 40, 140, -1, 'scared' if t >= tk else 'surprised', t=t, head_rot=hr))
        if sh.get('number'):
            s.append(card(540, 700, sh['number'], '#f2dc8a', '#111', 52))
        if sh.get('caller'): s.append(ch(sh['caller'], 900, GY + 60, 170, -1, 'normal', [(.6, -.2, 'magnifier')], t=t))
        cam = (1.0, 560, 900)
    elif ty == 'board':
        s.append(f'<rect x="-900" y="-500" width="2880" height="2900" fill="#6e4a2e"/><rect x="80" y="600" width="920" height="720" fill="#c8a06a" stroke="{INK}" stroke-width="10"/>')
        cards = sh.get('cards', []); pos = sh.get('pos') or [(270, 720), (810, 720), (540, 960), (270, 1180), (810, 1180), (540, 1200)]
        ats = sh.get('at') or list(range(len(cards)))
        shown = [k for k in range(len(cards)) if t >= V.at(sh, int(ats[k]), .3 + k * 1.1)]
        for a, b in sh.get('links', []):
            if a in shown and b in shown:
                (x1, y1), (x2, y2) = pos[a], pos[b]
                s.append(f'<path d="M{x1},{y1} Q{(x1 + x2) / 2},{(y1 + y2) / 2 + 40} {x2},{y2}" stroke="#c4281f" stroke-width="6" fill="none"/>')
        for k in shown:
            x, y = pos[k]; ta = V.at(sh, int(ats[k]), .3 + k * 1.1)
            s.append(pop(x, y, (t - ta) / .35, card(x, y, cards[k], '#fbf6e6', '#111', 34, rot=(-4, 3, -2, 4, -3, 2)[k % 6]) + f'<circle cx="{x}" cy="{y - 36}" r="10" fill="#c4281f" stroke="{INK}" stroke-width="3"/>'))
        cam = (1.0, 540, 950)
    elif ty == 'timeline':
        s.append(paper())
        pts = sh.get('points', []); n = max(1, len(pts))
        s.append(f'<path d="M120,960 L960,960" stroke="{INK}" stroke-width="10"/>')
        for k, p in enumerate(pts):
            ta = V.at(sh, int(p.get('at', k)), .3 + k * 1.2)
            if t < ta: continue
            x = 160 + (760 * k / max(1, n - 1) if n > 1 else 380); up = k % 2 == 0
            inner = (f'<circle cx="{f_(x)}" cy="960" r="22" fill="#c4281f" stroke="{INK}" stroke-width="6"/>'
                     f'<text x="{f_(x)}" y="{900 if up else 1050}" font-family="{FONT}" font-weight="900" font-size="48" fill="#5a1a14" text-anchor="middle">{esc(p.get("y", ""))}</text>'
                     f'<text x="{f_(x)}" y="{840 if up else 1110}" font-family="{FONT}" font-weight="700" font-size="32" fill="#333" text-anchor="middle">{esc(p.get("t", ""))}</text>')
            s.append(pop(x, 960, (t - ta) / .35, inner))
        cam = (1.0, 540, 960)
    elif ty == 'spy':
        s.append(street_night(t)); s.append('<rect x="-900" y="-500" width="2880" height="2900" fill="#9aa4b8" opacity=".35"/>')
        from cung_svg import SIL
        s.append(SIL + '<g filter="url(#sil)">' + ch(sh.get('who', 'dan_tay'), 560, GY + 40, 260, -1, 'normal', [(.6, -.1, 'phone')] if sh.get('phone') else None, t=t, tag=False) + '</g>')
        s.append(pop(540, 760, (t - V.at(sh, 0, .3) - .4) / .35, card(540, 760, sh.get('title', 'GIẢ THUYẾT: ĐIỆP VIÊN?'), '#c4281f', '#fff', 46)))
        cam = (lerp(1.08, 1.0, ease(t / max(1, d))), 560, 900)
    elif ty == 'lab':
        s.append(lab_bg(t))
        s.append(f'<g transform="translate(540 760)">' + ''.join(
            f'<circle cx="{f_(math.sin(t * 2 + j * .6) * 70)}" cy="{-160 + j * 40}" r="14" fill="#3a7ac4" stroke="{INK}" stroke-width="4"/><circle cx="{f_(-math.sin(t * 2 + j * .6) * 70)}" cy="{-160 + j * 40}" r="14" fill="#c4281f" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M{f_(math.sin(t * 2 + j * .6) * 70)},{-160 + j * 40} L{f_(-math.sin(t * 2 + j * .6) * 70)},{-160 + j * 40}" stroke="#8a8270" stroke-width="4"/>' for j in range(9)) + '</g>')
        if sh.get('who'): s.append(ch(sh['who'], 300, GY + 40, 170, 1, 'normal', [(.6, -.3, 'magnifier')], t=t))
        if sh.get('who2'): s.append(ch(sh['who2'], 820, GY + 40, 160, -1, 'happy', t=t))
        tr = V.at(sh, int(sh.get('result_at', 99)), 1e9)
        if t >= tr and sh.get('result'):
            s.append(pop(540, 1120, (t - tr) / .35, card(540, 1120, sh['result'], '#2a7a4a', '#fff', 46)))
        cam = (1.0, 540, 900)
    elif ty == 'tree':
        s.append(paper())
        r = random.Random(4); q = ease(t / max(1.0, d * .6))
        nodes = [(540, 700)]; edges = []
        for lvl in range(1, 5):
            for j in range(2 ** lvl):
                x = 540 + (j - (2 ** lvl - 1) / 2) * (900 / 2 ** lvl) + r.uniform(-8, 8); y = 700 + lvl * 130
                nodes.append((x, y)); edges.append((len(nodes) - 1, (len(nodes) - 2) // 2 if lvl > 0 else 0))
        nv = int(len(nodes) * q) + 1
        for a, b in edges:
            if a < nv: s.append(f'<path d="M{f_(nodes[b][0])},{f_(nodes[b][1])} L{f_(nodes[a][0])},{f_(nodes[a][1])}" stroke="#8a6a3a" stroke-width="4"/>')
        hi = len(nodes) - 5
        tn = V.at(sh, int(sh.get('name_at', 99)), 1e9)
        for k, (x, y) in enumerate(nodes[:nv]):
            on = t >= tn and k == hi
            s.append(f'<circle cx="{f_(x)}" cy="{f_(y)}" r="{18 if on else 12}" fill="{"#ffd400" if on else "#d8c9a4"}" stroke="{INK}" stroke-width="4"/>')
        if sh.get('count'): s.append(pop(540, 620, (t - .5) / .35, card(540, 620, sh['count'], '#f2dc8a', '#111', 44)))
        if t >= tn and sh.get('name'):
            x, y = nodes[hi]
            s.append(pop(x, y + 120, (t - tn) / .35, card(x, y + 120, sh['name'], '#c4281f', '#fff', 40)))
        cam = (1.0, 540, 960)
    elif ty == 'grave':
        s.append(V.sky('#e98a52', '#f6d49a')); s.append(V.hills(900))
        s.append(f'<rect x="-900" y="{GY - 40}" width="2880" height="1000" fill="#6e8a4e" stroke="{INK}" stroke-width="6"/>')
        for x in (-60, 140, 940, 1140): s.append(f'<path d="M{x - 50},{GY - 30} L{x - 50},{GY - 150} Q{x},{GY - 200} {x + 50},{GY - 150} L{x + 50},{GY - 30} Z" fill="#a8a49a" stroke="{INK}" stroke-width="6"/>')
        s.append(f'<path d="M380,{GY - 20} L380,{GY - 300} Q540,{GY - 400} 700,{GY - 300} L700,{GY - 20} Z" fill="#c8c4b8" stroke="{INK}" stroke-width="8"/>')
        st = sh.get('stone', '').split('|')
        for j, ln in enumerate(st): s.append(f'<text x="540" y="{GY - 220 + j * 60}" font-family="{FONT}" font-weight="800" font-size="{34 if len(ln) > 10 else 40}" fill="#3a3a3a" text-anchor="middle">{esc(ln)}</text>')
        td = V.at(sh, int(sh.get('dig_at', 99)), 1e9)
        if t >= td:
            s.append(pop(540, GY + 20, (t - td) / .4, ''.join(f'<circle cx="{500 + k * 26}" cy="{GY + 10 - (k % 2) * 16}" r="16" fill="{("#f08a8a", "#ffd400", "#f6f2e8")[k % 3]}" stroke="{INK}" stroke-width="4"/>' for k in range(4))))
        cam = (lerp(1.0, 1.1, ease(t / max(1, d))), 540, 980)
    elif ty == 'petition':   # don keu oan chat chong theo nam: sh.y0..sh.y1, sh.who (nguoi dung canh), sh.title
        s.append(room_bg(t, '#d8c8a8'))
        y0, y1 = sh.get('y0', 2004), sh.get('y1', 2013)
        q = ease(min(1, t / max(1.0, d * .75))); yr = int(round(lerp(y0, y1, q)))
        n = 3 + int(q * 18)
        for j in range(n):
            r_ = random.Random(j); xx = 640 + r_.uniform(-14, 14); yy = GY - 50 - j * 15
            s.append(f'<g transform="rotate({f_(r_.uniform(-5, 5))} {f_(xx)} {f_(yy)})"><rect x="{f_(xx - 120)}" y="{f_(yy - 14)}" width="240" height="20" fill="#fbf6e6" stroke="{INK}" stroke-width="4"/></g>')
        s.append(card(640, GY - 110 - n * 15, f'ĐƠN NĂM {yr}', '#f2dc8a', '#111', 40))
        if sh.get('title'): s.append(card(540, 600, sh['title'], '#c4281f', '#fff', 44))
        if sh.get('who'): s.append(ch(sh['who'], 270, GY + 40, sh.get('D', 165), 1, sh.get('expr', 'sad'), [(.6, -.25, 'scroll')], t=t))
        cam = (1.0, 540, 900)
    elif ty == 'stage':
        s.append(BG.get(sh.get('bg', 'paper'), BG['paper'])(t))
        for k, c in enumerate(sh.get('cast', [])):
            ta = V.at(sh, int(c.get('at', 0)), 0) if c.get('at') else -1
            if t < ta: continue
            x = c.get('x', 540); fx = c.get('from')
            if fx is not None:
                q = ease((t - max(0, ta)) / 1.3); x = lerp(fx, c.get('x', 540), q); bob = V.walk(t) if q < 1 else 0
            else: bob = 0
            g = ch(c['c'], x, c.get('y', GY + 40) - bob, c.get('D', 160), c.get('face', 1), c.get('expr', 'normal'), c.get('hands'), t=t, tag=c.get('tag', True))
            s.append(pop(x, c.get('y', GY + 40) - 100, (t - ta) / .35, g) if (c.get('at') and fx is None) else g)
        if sh.get('desk'): s.append(court_desk())
        for k, ic in enumerate(sh.get('icons', [])):   # vat chung dat trong canh: {icon, x, y, s, at}
            ta = V.at(sh, int(ic.get('at', 0)), .3)
            if t >= ta: s.append(pop(ic.get('x', 540), ic.get('y', 760), (t - ta) / .35, icon(ic['icon'], ic.get('x', 540), ic.get('y', 760), ic.get('s', 1.0))))
        for k, cd in enumerate(sh.get('cards', [])):
            ta = V.at(sh, int(cd.get('at', k)), .3 + k)
            if t >= ta: s.append(pop(cd.get('x', 540), cd.get('y', 760), (t - ta) / .35, card(cd.get('x', 540), cd.get('y', 760), cd['t'], cd.get('col', '#f2dc8a'), cd.get('tc', '#111'), cd.get('fs', 44))))
        if sh.get('ask'):
            tq = V.at(sh, -1, d * .6)
            if t >= tq: s.append(V.bigq(sh.get('qx', 880), 1000, t - tq))
        cam = (lerp(1.0, sh.get('zoom', 1.0), ease(t / max(1, d))), 540, 900)
    return ''.join(s), cam, shake, flash


SFX = {
    'beach': [], 'station': [('f0.4', 'pop', .7), ('f0.5', 'sting', .5)], 'items': [('every:1.5@0.3', 'pop', .5)],
    'scrap': [('f0.1', 'whoosh', .5), ('f0.5', 'sting', .7)], 'car': [('f0.45', 'thud', .6), ('f0.5', 'ding', .5)],
    'code': [('every:0.25@0.2', 'tick', .15)], 'door': [('f0.1', 'thud', .5), ('f0.15', 'thud', .5), ('f0.4', 'pop', .5)],
    'board': [('every:1.4@0.3', 'pop', .5)], 'timeline': [('every:1.4@0.3', 'pop', .5)], 'spy': [('f0.1', 'sting', .6)],
    'lab': [('f0.6', 'ding', .6)], 'tree': [('every:0.6', 'tick', .2), ('f0.7', 'ding', .6)], 'grave': [], 'stage': [], 'petition': [('every:0.8@0.2', 'tick', .2)],
}
