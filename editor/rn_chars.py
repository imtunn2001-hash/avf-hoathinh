"""Nhan vat RỐI NƯỚC (con roi go son son) – dau an rieng cua AVF (chu chot 22/11/2026).
Thay ksc_chars.character bang ban roi, giu nguyen chu ky ham va cau hinh CHARS -> moi canh cu (vh, CSK...) tu doi sang roi.
Dung: spec {"chars": "roinuoc"}; ksc_svg.main() goi rn_chars.install(module).

Dac diem nhan dien (khong doi giua cac kenh):
- Be vay go son DO loe xuong + 2 vien vang + hoa van may: chan de cua roi (cung la "bong" cua nhan vat).
- Than + dau go co VET BONG SON (lang son mai), chot co go nau, khop tay CHOT VANG.
- Mat ve son: may cong manh, mat hanh nhan, MA DO tron, moi son do nho (doi hinh theo bieu cam).
- Cu dong kieu roi: nhap nho tren mat nuoc, lac quanh de, tay giat theo nhip 12 hinh/giay (khong muot).
- Bang ten = BIEN GO treo day vang (ksc_svg.tags_svg ve khi TAG_STYLE == 'go').
Don vi D giu nhu cu (cao toan than ~2,3D, cham dat tai y).
"""
import math
import random

import ksc_chars as CH

INK = '#1a1410'
LAC = '#8e1f17'; LAC2 = '#6a150f'; GOLD = '#d8a93a'; WOOD = '#6b4a2a'
def _f(v): return f'{v:.1f}'

# them nhan vat van hoc / dau an rieng tung nguoi (mark)
EXTRA = {
    'thino': dict(tag='THỊ NỞ', skin='#d9a77a', hair='#140f0c', hair_style='bun', outfit='#6c5a8a', outfit2='#4c3e66', trim='#c8a24a', mark='bigface'),
    'thinoa': dict(tag='THỊ NỞ', skin='#d9a77a', hair='#140f0c', hair_style='bun', outfit='#6c5a8a', outfit2='#4c3e66', trim='#c8a24a', mark='bigface', prop='bowl'),
}
EXTRA.update({
    'chieuhoang': dict(tag='LÝ CHIÊU HOÀNG', skin='#f0c49c', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f', mark='bangs'),
    'trancanh': dict(tag='TRẦN CẢNH', skin='#ecb88a', hair='#140f0c', hair_style='topknot', outfit='#2e5a8a', outfit2='#22436a', trim='#d8a93a'),
    'thaitong': dict(tag='TRẦN THÁI TÔNG', skin='#e6b48a', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f', beard=True),
    'thudo': dict(tag='TRẦN THỦ ĐỘ', skin='#d9a070', hair='#140f0c', hair_style='khan', hat='#111', outfit='#7a1f1a', outfit2='#561410', trim='#d8a93a', w=1.12, beard=True, mark='brow'),
    'thudogia': dict(tag='TRẦN THỦ ĐỘ', skin='#d9a070', hair='#e8e4da', hair_style='khan', hat='#111', outfit='#7a1f1a', outfit2='#561410', trim='#d8a93a', w=1.12, beard=True, mark='brow'),
    'huetong': dict(tag='LÝ HUỆ TÔNG', skin='#e2b48a', hair='#140f0c', hair_style='mien', outfit='#c99a2a', outfit2='#9a7418', trim='#7a1f1a', mark='pale'),
    'huequang': dict(tag='SƯ HUỆ QUANG', skin='#e2b48a', hair='#cfa078', hair_style='bald', outfit='#8a5a2a', outfit2='#6a4420', trim='#d8a93a', mark='pale'),
    'tonthat': dict(tag='TÔN THẤT HỌ LÝ', skin='#e0aa7c', hair='#140f0c', hair_style='khan', hat='#2a2a3a', outfit='#5a6a8a', outfit2='#44506a', trim='#d8a93a'),
    'quan': dict(tag='QUAN TRIỀU', skin='#dca476', hair='#140f0c', hair_style='khan', hat='#1a1a1a', outfit='#2e5a46', outfit2='#224436', trim='#d8a93a', beard=True),
    'ngosilien': dict(tag='NGÔ SĨ LIÊN', skin='#e2ae80', hair='#d8d4ca', hair_style='khan', hat='#2a2a2a', outfit='#efe6cf', outfit2='#cfc3a3', trim='#7a5a2a', beard=True, mark='glasses'),
    'thitu': dict(tag='NGƯỜI HẦU', skin='#ecb88a', hair='#140f0c', hair_style='bun', outfit='#8a3a5a', outfit2='#6a2a44', trim='#d8a93a'),
})
EXTRA.update({
    'canhsat': dict(tag='CẢNH SÁT', skin='#e8b890', hair='#3a2a1a', hair_style='cap', hat='#1e2a44', outfit='#2a3a5e', outfit2='#1e2a44', trim='#d8a93a'),
    'thamtu': dict(tag='THÁM TỬ', skin='#e8b890', hair='#3a2a1a', hair_style='fedora', hat='#5a4a3a', outfit='#7a6a52', outfit2='#5a4e3c', trim='#3a2a1a', mark='mustache'),
    'bacsi': dict(tag='BÁC SĨ', skin='#ecc09a', hair='#8a8a8a', hair_style='side', outfit='#f2f2ee', outfit2='#cfcfc8', trim='#5a8aa8', mark='glasses'),
    'yta': dict(tag='Y TÁ', skin='#f0c8a0', hair='#5a3a22', hair_style='nurse', outfit='#e8eef2', outfit2='#c8d2da', trim='#5a8aa8'),
    'nguoila': dict(tag='NGƯỜI LẠ', skin='#ecc4a0', hair='#6a4a2a', hair_style='side', outfit='#5a5a62', outfit2='#3e3e46', trim='#7a1f1a'),
    'nhakhoahoc': dict(tag='NHÀ KHOA HỌC', skin='#ecc4a0', hair='#d8d4ca', hair_style='side', outfit='#3a5a7a', outfit2='#2a4460', trim='#d8a93a', mark='glasses'),
    'dan_tay': dict(tag='NGƯỜI DÂN', skin='#ecc4a0', hair='#7a5a3a', hair_style='fedora', hat='#4a4a52', outfit='#6a5a4a', outfit2='#4e4236', trim='#3a2a1a'),
})
MARKS = {'chipheo': 'scar', 'namcao': 'glasses', 'bakien': 'mustache', 'baba': 'mole', 'thino': 'bigface'}


def _seg(x1, y1, x2, y2, w, col):
    return (f'<path d="M{_f(x1)},{_f(y1)} L{_f(x2)},{_f(y2)}" stroke="{INK}" stroke-width="{_f(w * 1.9)}" stroke-linecap="round"/>'
            f'<path d="M{_f(x1)},{_f(y1)} L{_f(x2)},{_f(y2)}" stroke="{col}" stroke-width="{_f(w)}" stroke-linecap="round"/>')


def _arm(sx, sy, hx, hy, L, facing, col, D, skin):
    """tay roi 2 doan, khuyu gap xuong (IK 2 xuong), khop chot vang."""
    dx, dy = hx - sx, hy - sy; d = max(1e-3, math.hypot(dx, dy))
    if d > 2 * L * .98:
        hx, hy = sx + dx / d * 2 * L * .98, sy + dy / d * 2 * L * .98; d = 2 * L * .98
    mx, my = (sx + hx) / 2, (sy + hy) / 2
    h = math.sqrt(max(0.0, L * L - (d / 2) ** 2))
    nx, ny = -dy / d, dx / d
    if ny < 0: nx, ny = -nx, -ny        # khuyu luon xuong duoi
    ex, ey = mx + nx * h, my + ny * h
    w = D * .13
    return (_seg(sx, sy, ex, ey, w, col) + _seg(ex, ey, hx, hy, w * .9, col)
            + f'<circle cx="{_f(sx)}" cy="{_f(sy)}" r="{_f(D * .05)}" fill="{GOLD}" stroke="{INK}" stroke-width="{_f(D * .02)}"/>'
            + f'<circle cx="{_f(ex)}" cy="{_f(ey)}" r="{_f(D * .045)}" fill="{GOLD}" stroke="{INK}" stroke-width="{_f(D * .02)}"/>'), (hx, hy)


def _hand(hx, hy, D, skin):
    return f'<ellipse cx="{_f(hx)}" cy="{_f(hy)}" rx="{_f(D * .11)}" ry="{_f(D * .09)}" fill="{skin}" stroke="{INK}" stroke-width="{_f(D * .035)}"/>'


def _prop_extra(kind, hx, hy, D, facing):
    s = D / 150
    if kind == 'bottle':
        return (f'<g transform="rotate({_f(-20 * facing)} {_f(hx)} {_f(hy)})"><path d="M{_f(hx - 12 * s)},{_f(hy - 70 * s)} l0,{_f(-18 * s)} l{_f(24 * s)},0 l0,{_f(18 * s)} q{_f(18 * s)},{_f(12 * s)} {_f(18 * s)},{_f(40 * s)} l0,{_f(50 * s)} l{_f(-60 * s)},0 l0,{_f(-50 * s)} q0,{_f(-28 * s)} {_f(18 * s)},{_f(-40 * s)} Z" fill="#e8e2c8" stroke="{INK}" stroke-width="{_f(5 * s)}"/>'
                f'<rect x="{_f(hx - 14 * s)}" y="{_f(hy - 100 * s)}" width="{_f(28 * s)}" height="{_f(14 * s)}" fill="#c4281f" stroke="{INK}" stroke-width="{_f(3 * s)}"/></g>'), (hx, hy - 100 * s)
    if kind == 'bowl':
        return (f'<path d="M{_f(hx - 42 * s)},{_f(hy - 14 * s)} q{_f(42 * s)},{_f(60 * s)} {_f(84 * s)},0 Z" fill="#f2efe4" stroke="{INK}" stroke-width="{_f(5 * s)}"/>'
                f'<path d="M{_f(hx - 30 * s)},{_f(hy - 22 * s)} q{_f(30 * s)},{_f(-12 * s)} {_f(60 * s)},0" fill="#f6f2dc" stroke="{INK}" stroke-width="{_f(3 * s)}"/>'
                f'<path d="M{_f(hx - 10 * s)},{_f(hy - 40 * s)} q{_f(-8 * s)},{_f(-14 * s)} 0,{_f(-28 * s)} M{_f(hx + 10 * s)},{_f(hy - 40 * s)} q{_f(-8 * s)},{_f(-14 * s)} 0,{_f(-28 * s)}" stroke="#bbb" stroke-width="{_f(4 * s)}" fill="none"/>'
                f'<circle cx="{_f(hx - 12 * s)}" cy="{_f(hy - 25 * s)}" r="{_f(4 * s)}" fill="#5a9a3a"/><circle cx="{_f(hx + 8 * s)}" cy="{_f(hy - 27 * s)}" r="{_f(4 * s)}" fill="#5a9a3a"/>'), (hx, hy - 40 * s)
    if kind == 'fan':
        pts = ' '.join(f'L{_f(hx + facing * math.cos(math.radians(a)) * 70 * s)},{_f(hy + math.sin(math.radians(a)) * 70 * s)}' for a in range(-150, -29, 15))
        return (f'<path d="M{_f(hx)},{_f(hy)} {pts} Z" fill="#e8c66a" stroke="{INK}" stroke-width="{_f(5 * s)}"/>'
                + ''.join(f'<path d="M{_f(hx)},{_f(hy)} L{_f(hx + facing * math.cos(math.radians(a)) * 68 * s)},{_f(hy + math.sin(math.radians(a)) * 68 * s)}" stroke="#8a6a2a" stroke-width="{_f(2.5 * s)}"/>' for a in range(-135, -40, 15))), (hx, hy - 70 * s)
    if kind == 'towel':   # khan trau do
        return (f'<path d="M{_f(hx - 10 * s)},{_f(hy - 10 * s)} q{_f(30 * s)},{_f(-30 * s)} {_f(60 * s)},{_f(-6 * s)} l{_f(-8 * s)},{_f(40 * s)} q{_f(-26 * s)},{_f(-14 * s)} {_f(-52 * s)},{_f(8 * s)} Z" fill="#c4281f" stroke="{INK}" stroke-width="{_f(4 * s)}" stroke-linejoin="round"/>'
                f'<path d="M{_f(hx + 50 * s)},{_f(hy - 16 * s)} l{_f(8 * s)},{_f(10 * s)} M{_f(hx + 44 * s)},{_f(hy + 24 * s)} l{_f(8 * s)},{_f(8 * s)}" stroke="{GOLD}" stroke-width="{_f(3 * s)}"/>'), (hx + 50 * s, hy)
    if kind == 'scroll':  # to chieu vang
        return (f'<rect x="{_f(hx - 8 * s)}" y="{_f(hy - 90 * s)}" width="{_f(70 * s)}" height="{_f(90 * s)}" fill="#f2dc8a" stroke="{INK}" stroke-width="{_f(4 * s)}"/>'
                + ''.join(f'<path d="M{_f(hx + 2 * s)},{_f(hy - (74 - k * 16) * s)} l{_f(50 * s)},0" stroke="#8a6a2a" stroke-width="{_f(3 * s)}"/>' for k in range(4))
                + f'<rect x="{_f(hx - 14 * s)}" y="{_f(hy - 96 * s)}" width="{_f(82 * s)}" height="{_f(10 * s)}" rx="{_f(5 * s)}" fill="#7a1f1a" stroke="{INK}" stroke-width="{_f(3 * s)}"/>'
                + f'<rect x="{_f(hx - 14 * s)}" y="{_f(hy - 4 * s)}" width="{_f(82 * s)}" height="{_f(10 * s)}" rx="{_f(5 * s)}" fill="#7a1f1a" stroke="{INK}" stroke-width="{_f(3 * s)}"/>'), (hx + 30 * s, hy - 90 * s)
    if kind == 'weed':    # bui co nho ca re dai
        return (f'<path d="M{_f(hx)},{_f(hy)} q{_f(-6 * s)},{_f(30 * s)} {_f(4 * s)},{_f(60 * s)} q{_f(-14 * s)},{_f(20 * s)} {_f(-4 * s)},{_f(46 * s)} M{_f(hx + 2 * s)},{_f(hy + 40 * s)} q{_f(16 * s)},{_f(12 * s)} {_f(20 * s)},{_f(34 * s)}" stroke="#8a6a3a" stroke-width="{_f(4 * s)}" fill="none"/>'
                + ''.join(f'<path d="M{_f(hx)},{_f(hy)} q{_f(dx * s)},{_f(-30 * s)} {_f(dx * 2 * s)},{_f(-60 * s)}" stroke="#3e7a2c" stroke-width="{_f(7 * s)}" fill="none" stroke-linecap="round"/>' for dx in (-14, -4, 8, 16))), (hx, hy - 60 * s)
    if kind == 'book':
        return (f'<rect x="{_f(hx - 10 * s)}" y="{_f(hy - 70 * s)}" width="{_f(56 * s)}" height="{_f(74 * s)}" rx="{_f(4 * s)}" fill="#3a5a3a" stroke="{INK}" stroke-width="{_f(4 * s)}"/>'
                f'<path d="M{_f(hx - 2 * s)},{_f(hy - 62 * s)} l0,{_f(58 * s)}" stroke="#d8a93a" stroke-width="{_f(3 * s)}"/>'), (hx + 18 * s, hy - 70 * s)
    if kind == 'magnifier':
        return (f'<path d="M{_f(hx)},{_f(hy)} l{_f(facing * 30 * s)},{_f(-34 * s)}" stroke="{INK}" stroke-width="{_f(12 * s)}" stroke-linecap="round"/>'
                f'<circle cx="{_f(hx + facing * 50 * s)}" cy="{_f(hy - 58 * s)}" r="{_f(28 * s)}" fill="#cfe8f4" fill-opacity=".6" stroke="{INK}" stroke-width="{_f(7 * s)}"/>'), (hx + facing * 50 * s, hy - 58 * s)
    if kind == 'phone':
        return (f'<rect x="{_f(hx - 12 * s)}" y="{_f(hy - 46 * s)}" width="{_f(26 * s)}" height="{_f(50 * s)}" rx="{_f(6 * s)}" fill="#222" stroke="{INK}" stroke-width="{_f(3 * s)}"/>'), (hx, hy - 46 * s)
    if kind == 'cigarette':
        return (f'<path d="M{_f(hx)},{_f(hy)} l{_f(facing * 34 * s)},{_f(-6 * s)}" stroke="#f2efe4" stroke-width="{_f(6 * s)}" stroke-linecap="round"/>'), (hx + facing * 34 * s, hy - 6 * s)
    if kind == 'pen':
        return (f'<path d="M{_f(hx)},{_f(hy)} l{_f(facing * 40 * s)},{_f(-60 * s)}" stroke="{INK}" stroke-width="{_f(14 * s)}" stroke-linecap="round"/>'
                f'<path d="M{_f(hx)},{_f(hy)} l{_f(facing * 40 * s)},{_f(-60 * s)}" stroke="#7a2a20" stroke-width="{_f(7 * s)}" stroke-linecap="round"/>'), (hx + facing * 40 * s, hy - 60 * s)
    return None


def _face(c, name, hx, hy, rx, ry, D, facing, expr):
    o = []; s = D / 150; mark = c.get('mark') or MARKS.get(name)
    ex = hx + facing * rx * .22
    xs = (ex - 22 * s, ex + 22 * s)
    blind = c.get('blind')
    for i, X in enumerate(xs):
        # long may ve son: manh, cong; doi theo bieu cam
        if expr == 'angry':
            inner = (X - hx) * facing > rx * .2
            y1, y2 = (hy - 30 * s, hy - 20 * s) if (i == 0) == (facing > 0) else (hy - 20 * s, hy - 30 * s)
            o.append(f'<path d="M{_f(X - 14 * s)},{_f(y1)} L{_f(X + 14 * s)},{_f(y2)}" stroke="{INK}" stroke-width="{_f(5 * s)}" stroke-linecap="round"/>')
        elif expr in ('sad', 'scared'):
            y1, y2 = (hy - 20 * s, hy - 30 * s) if (i == 0) == (facing > 0) else (hy - 30 * s, hy - 20 * s)
            o.append(f'<path d="M{_f(X - 13 * s)},{_f(y1)} L{_f(X + 13 * s)},{_f(y2)}" stroke="{INK}" stroke-width="{_f(4 * s)}" stroke-linecap="round"/>')
        else:
            o.append(f'<path d="M{_f(X - 13 * s)},{_f(hy - 20 * s)} q{_f(13 * s)},{_f(-10 * s)} {_f(26 * s)},0" stroke="{INK}" stroke-width="{_f(3.5 * s)}" fill="none" stroke-linecap="round"/>')
        # mat
        if blind:
            o.append(f'<path d="M{_f(X - 11 * s)},{_f(hy)} l{_f(22 * s)},0" stroke="{INK}" stroke-width="{_f(4 * s)}" stroke-linecap="round"/>')
        elif expr == 'sleep':
            o.append(f'<path d="M{_f(X - 11 * s)},{_f(hy)} q{_f(11 * s)},{_f(7 * s)} {_f(22 * s)},0" stroke="{INK}" stroke-width="{_f(4 * s)}" fill="none" stroke-linecap="round"/>')
        elif expr == 'happy':
            o.append(f'<path d="M{_f(X - 11 * s)},{_f(hy + 3 * s)} q{_f(11 * s)},{_f(-12 * s)} {_f(22 * s)},0" stroke="{INK}" stroke-width="{_f(4.5 * s)}" fill="none" stroke-linecap="round"/>')
        elif expr == 'surprised':
            o.append(f'<circle cx="{_f(X)}" cy="{_f(hy)}" r="{_f(11 * s)}" fill="#fff" stroke="{INK}" stroke-width="{_f(3.5 * s)}"/><circle cx="{_f(X)}" cy="{_f(hy)}" r="{_f(4 * s)}" fill="{INK}"/>')
        else:
            o.append(f'<path d="M{_f(X - 12 * s)},{_f(hy)} q{_f(12 * s)},{_f(-9 * s)} {_f(24 * s)},0 q{_f(-12 * s)},{_f(9 * s)} {_f(-24 * s)},0 Z" fill="#fff" stroke="{INK}" stroke-width="{_f(3 * s)}"/>'
                     f'<circle cx="{_f(X + facing * 3 * s)}" cy="{_f(hy)}" r="{_f(4.5 * s)}" fill="{INK}"/>')
        # ma do: dau an roi (vui thi dam hon)
        o.append(f'<circle cx="{_f(X - facing * 2 * s)}" cy="{_f(hy + 24 * s)}" r="{_f(10 * s)}" fill="#e0543c" opacity="{".9" if expr == "happy" else ".65"}"/>')
    # moi son
    mx, my = ex, hy + 40 * s
    if expr == 'happy':
        o.append(f'<path d="M{_f(mx - 12 * s)},{_f(my - 3 * s)} q{_f(12 * s)},{_f(14 * s)} {_f(24 * s)},0 Z" fill="#c4281f" stroke="{INK}" stroke-width="{_f(2.5 * s)}"/>')
    elif expr == 'surprised':
        o.append(f'<ellipse cx="{_f(mx)}" cy="{_f(my + 2 * s)}" rx="{_f(7 * s)}" ry="{_f(10 * s)}" fill="#5a1a1a" stroke="{INK}" stroke-width="{_f(3 * s)}"/>')
    elif expr in ('sad', 'scared'):
        o.append(f'<path d="M{_f(mx - 10 * s)},{_f(my + 4 * s)} q{_f(10 * s)},{_f(-9 * s)} {_f(20 * s)},0" stroke="#c4281f" stroke-width="{_f(4 * s)}" fill="none" stroke-linecap="round"/>')
    elif expr == 'sleep':
        o.append(f'<path d="M{_f(mx - 7 * s)},{_f(my)} l{_f(14 * s)},0" stroke="#c4281f" stroke-width="{_f(3.5 * s)}" stroke-linecap="round"/>')
    elif expr == 'angry':
        o.append(f'<path d="M{_f(mx - 11 * s)},{_f(my)} l{_f(22 * s)},0" stroke="#c4281f" stroke-width="{_f(5 * s)}" stroke-linecap="round"/>')
    else:
        o.append(f'<path d="M{_f(mx - 9 * s)},{_f(my)} q{_f(9 * s)},{_f(6 * s)} {_f(18 * s)},0 q{_f(-9 * s)},{_f(-4 * s)} {_f(-18 * s)},0 Z" fill="#c4281f" stroke="{INK}" stroke-width="{_f(2.5 * s)}"/>')
    # ky hieu cam xuc (nhu bo quy tac 6 bieu cam)
    if expr == 'angry':
        gx, gy = hx - facing * rx * .35, hy - ry * (.28 if c.get('hair_style') in ('nonla', 'khan', 'helmet', 'crown') else .55)
        o.append(f'<path d="M{_f(gx - 12 * s)},{_f(gy)} l{_f(9 * s)},{_f(5 * s)} M{_f(gx + 12 * s)},{_f(gy)} l{_f(-9 * s)},{_f(5 * s)} M{_f(gx)},{_f(gy - 12 * s)} l0,{_f(9 * s)}" stroke="#d01f1f" stroke-width="{_f(4.5 * s)}" stroke-linecap="round"/>')
    if expr == 'sad':
        tx, ty = xs[1 if facing > 0 else 0] + facing * 4 * s, hy + 12 * s
        o.append(f'<path d="M{_f(tx)},{_f(ty)} q{_f(9 * s)},{_f(18 * s)} 0,{_f(24 * s)} q{_f(-9 * s)},{_f(-6 * s)} 0,{_f(-24 * s)}" fill="#7cc4f0" stroke="{INK}" stroke-width="{_f(2 * s)}"/>')
    if expr == 'scared':
        for k in range(3):
            x = hx - facing * rx * (.1 - k * .25)
            o.append(f'<path d="M{_f(x)},{_f(hy - ry * .75)} l0,{_f(ry * .3)}" stroke="#7a3fb0" stroke-width="{_f(4 * s)}" stroke-linecap="round"/>')
        sx, sy = hx - facing * rx * .95, hy - ry * .1
        o.append(f'<path d="M{_f(sx)},{_f(sy)} q{_f(10 * s)},{_f(20 * s)} 0,{_f(26 * s)} q{_f(-10 * s)},{_f(-6 * s)} 0,{_f(-26 * s)}" fill="#9fd8f5" stroke="{INK}" stroke-width="{_f(2 * s)}"/>')
    # dau an rieng tung nhan vat
    if mark == 'scar':      # seo khau tren tran Chi Pheo
        X = ex + facing * 32 * s
        o.append(f'<path d="M{_f(X)},{_f(hy - 46 * s)} l{_f(facing * 12 * s)},{_f(30 * s)}" stroke="#7a2a20" stroke-width="{_f(4 * s)}"/>'
                 + ''.join(f'<path d="M{_f(X - 6 * s + facing * k * 4 * s)},{_f(hy - 38 * s + k * 9 * s)} l{_f(12 * s)},{_f(-3 * s)}" stroke="#7a2a20" stroke-width="{_f(3 * s)}"/>' for k in range(3)))
    if mark == 'glasses':
        o.append(''.join(f'<circle cx="{_f(X)}" cy="{_f(hy)}" r="{_f(17 * s)}" fill="none" stroke="{INK}" stroke-width="{_f(4 * s)}"/>' for X in xs)
                 + f'<path d="M{_f(xs[0] + 17 * s)},{_f(hy - 2 * s)} L{_f(xs[1] - 17 * s)},{_f(hy - 2 * s)}" stroke="{INK}" stroke-width="{_f(3.5 * s)}"/>')
    if mark == 'mustache':  # ria tram + rau de cua Ba Kien
        o.append(f'<path d="M{_f(mx)},{_f(my - 8 * s)} q{_f(-18 * s)},{_f(-4 * s)} {_f(-30 * s)},{_f(12 * s)} M{_f(mx)},{_f(my - 8 * s)} q{_f(18 * s)},{_f(-4 * s)} {_f(30 * s)},{_f(12 * s)}" stroke="{INK}" stroke-width="{_f(4.5 * s)}" fill="none" stroke-linecap="round"/>')
    if mark == 'brow':      # may rau sau dam, xech (Tran Thu Do)
        for X in xs:
            o.append(f'<path d="M{_f(X - 17 * s)},{_f(hy - 30 * s + (6 * s if (X - hx) * facing < rx * .2 else 0))} L{_f(X + 17 * s)},{_f(hy - 24 * s - (6 * s if (X - hx) * facing < rx * .2 else 0))}" stroke="{INK}" stroke-width="{_f(9 * s)}" stroke-linecap="round"/>')
    if mark == 'pale':      # quang tham duoi mat (vua om yeu)
        o.append(''.join(f'<path d="M{_f(X - 10 * s)},{_f(hy + 12 * s)} q{_f(10 * s)},{_f(6 * s)} {_f(20 * s)},0" stroke="#8a6a8a" stroke-width="{_f(3 * s)}" fill="none" opacity=".8"/>' for X in xs))
    if mark == 'bangs':     # toc mai bang (be gai)
        o.append(f'<path d="M{_f(hx - rx * .85)},{_f(hy - ry * .45)} Q{_f(hx)},{_f(hy - ry * .2)} {_f(hx + rx * .85)},{_f(hy - ry * .45)} L{_f(hx + rx * .8)},{_f(hy - ry * .6)} Q{_f(hx)},{_f(hy - ry * .75)} {_f(hx - rx * .8)},{_f(hy - ry * .6)} Z" fill="#140f0c"/>')
    if mark == 'dirt':      # vet bun tren ma (nhan vat BAN - Chien Su Ky)
        o.append(f'<ellipse cx="{_f(mx + facing * 26 * s)}" cy="{_f(my - 14 * s)}" rx="{_f(13 * s)}" ry="{_f(7 * s)}" fill="#6a4a2a" opacity=".75" transform="rotate({_f(-18 * facing)} {_f(mx + facing * 26 * s)} {_f(my - 14 * s)})"/>'
                 f'<circle cx="{_f(mx + facing * 40 * s)}" cy="{_f(my - 20 * s)}" r="{_f(4 * s)}" fill="#6a4a2a" opacity=".7"/>')
    if mark == 'mole':
        o.append(f'<circle cx="{_f(mx + facing * 20 * s)}" cy="{_f(my - 10 * s)}" r="{_f(4 * s)}" fill="{INK}"/>')
    if c.get('beard'):
        o.append(f'<path d="M{_f(mx - 6 * s)},{_f(my + 12 * s)} q{_f(6 * s)},{_f(34 * s)} {_f(14 * s)},{_f(36 * s)} q{_f(2 * s)},{_f(-18 * s)} {_f(-2 * s)},{_f(-36 * s)}" fill="{c.get("hair", INK)}" stroke="{INK}" stroke-width="{_f(3 * s)}"/>')
    return ''.join(o)


def _head(c, hx, hy, rx, ry, D, facing):
    """dau go + toc/mu theo hair_style. Tra (sau, truoc, chieu cao them cho bien ten)."""
    hs = c.get('hair_style'); hair = c.get('hair', INK); s = D / 150; ow = D * .045
    back, front, extra = [], [], 0.0
    if hs == 'bun':
        back.append(f'<circle cx="{_f(hx - facing * rx * .95)}" cy="{_f(hy - ry * .45)}" r="{_f(rx * .42)}" fill="{hair}" stroke="{INK}" stroke-width="{_f(ow)}"/>')
    if hs == 'topknot':
        back.append(f'<circle cx="{_f(hx - facing * rx * .15)}" cy="{_f(hy - ry * 1.05)}" r="{_f(rx * .34)}" fill="{hair}" stroke="{INK}" stroke-width="{_f(ow)}"/>'); extra = ry * .4
    if hs in ('bun', 'side', 'band', 'topknot'):
        front.append(f'<path d="M{_f(hx - rx)},{_f(hy - 4 * s)} Q{_f(hx - rx)},{_f(hy - ry * 1.12)} {_f(hx)},{_f(hy - ry)} Q{_f(hx + rx)},{_f(hy - ry * 1.12)} {_f(hx + rx)},{_f(hy - 4 * s)} Q{_f(hx + facing * rx * .2)},{_f(hy - ry * .55)} {_f(hx - rx)},{_f(hy - 4 * s)} Z" fill="{hair}"/>')
    if hs == 'side':
        front.append(f'<path d="M{_f(hx - rx * .9)},{_f(hy - ry * .3)} Q{_f(hx - facing * rx * .1)},{_f(hy - ry * 1.25)} {_f(hx + rx * .98)},{_f(hy - ry * .4)} Q{_f(hx + facing * rx * .2)},{_f(hy - ry * .65)} {_f(hx - rx * .9)},{_f(hy - ry * .3)} Z" fill="{hair}" stroke="{INK}" stroke-width="{_f(ow * .6)}"/>')
    if hs == 'band':
        front.append(f'<path d="M{_f(hx - rx * .98)},{_f(hy - ry * .32)} Q{_f(hx)},{_f(hy - ry * .6)} {_f(hx + rx * .98)},{_f(hy - ry * .32)}" stroke="{c.get("band", "#c4281f")}" stroke-width="{_f(D * .1)}" fill="none"/>')
    if hs == 'bald':
        front.append(f'<path d="M{_f(hx - rx * .96)},{_f(hy - ry * .05)} Q{_f(hx - rx)},{_f(hy - ry * .55)} {_f(hx - rx * .55)},{_f(hy - ry * .7)}" stroke="{hair}" stroke-width="{_f(D * .07)}" fill="none" stroke-linecap="round"/>')
    if hs == 'khan':   # khan xep
        front.append(f'<path d="M{_f(hx - rx * 1.08)},{_f(hy - ry * .25)} Q{_f(hx)},{_f(hy - ry * 1.5)} {_f(hx + rx * 1.08)},{_f(hy - ry * .25)} Q{_f(hx)},{_f(hy - ry * .55)} {_f(hx - rx * 1.08)},{_f(hy - ry * .25)} Z" fill="{c.get("hat", "#111")}" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                     + ''.join(f'<path d="M{_f(hx - rx * .9)},{_f(hy - ry * (.5 + k * .17))} Q{_f(hx)},{_f(hy - ry * (.85 + k * .17))} {_f(hx + rx * .9)},{_f(hy - ry * (.5 + k * .17))}" stroke="#555" stroke-width="{_f(3 * s)}" fill="none"/>' for k in range(3)))
        extra = ry * .3
    if hs == 'nonla':
        front.append(f'<path d="M{_f(hx - rx * 1.7)},{_f(hy - ry * .45)} L{_f(hx)},{_f(hy - ry * 1.75)} L{_f(hx + rx * 1.7)},{_f(hy - ry * .45)} Z" fill="{c.get("hat", "#d8bc78")}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>'
                     f'<path d="M{_f(hx - rx * .9)},{_f(hy - ry * .9)} L{_f(hx + rx * .9)},{_f(hy - ry * .9)}" stroke="#b8963e" stroke-width="{_f(3 * s)}"/>')
        extra = ry * .75
    if hs == 'mien':   # mu mien vang (vua, nu vuong)
        front.append(f'<path d="M{_f(hx - rx * .98)},{_f(hy - ry * .35)} Q{_f(hx - rx)},{_f(hy - ry * 1.1)} {_f(hx)},{_f(hy - ry)} Q{_f(hx + rx)},{_f(hy - ry * 1.1)} {_f(hx + rx * .98)},{_f(hy - ry * .35)} Q{_f(hx)},{_f(hy - ry * .6)} {_f(hx - rx * .98)},{_f(hy - ry * .35)} Z" fill="{hair}"/>'
                     f'<path d="M{_f(hx - rx * .75)},{_f(hy - ry * .72)} L{_f(hx - rx * .8)},{_f(hy - ry * 1.45)} L{_f(hx - rx * .35)},{_f(hy - ry * 1.15)} L{_f(hx)},{_f(hy - ry * 1.6)} L{_f(hx + rx * .35)},{_f(hy - ry * 1.15)} L{_f(hx + rx * .8)},{_f(hy - ry * 1.45)} L{_f(hx + rx * .75)},{_f(hy - ry * .72)} Q{_f(hx)},{_f(hy - ry * .95)} {_f(hx - rx * .75)},{_f(hy - ry * .72)} Z" fill="{GOLD}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>'
                     f'<circle cx="{_f(hx)}" cy="{_f(hy - ry * 1.05)}" r="{_f(rx * .13)}" fill="#c4281f" stroke="{INK}" stroke-width="{_f(ow * .5)}"/>')
        extra = ry * .6
    if hs in ('cap', 'fedora', 'nurse'):
        if hs != 'nurse':
            front.append(f'<path d="M{_f(hx - rx)},{_f(hy - 4 * s)} Q{_f(hx - rx)},{_f(hy - ry * 1.05)} {_f(hx)},{_f(hy - ry)} Q{_f(hx + rx)},{_f(hy - ry * 1.05)} {_f(hx + rx)},{_f(hy - 4 * s)} Q{_f(hx + facing * rx * .2)},{_f(hy - ry * .5)} {_f(hx - rx)},{_f(hy - 4 * s)} Z" fill="{hair}"/>')
        hc = c.get('hat', '#1e2a44')
        if hs == 'cap':     # mu ket canh sat: dinh phang + luoi trai
            front.append(f'<path d="M{_f(hx - rx * 1.05)},{_f(hy - ry * .55)} L{_f(hx - rx * 1.15)},{_f(hy - ry * 1.15)} L{_f(hx + rx * 1.15)},{_f(hy - ry * 1.15)} L{_f(hx + rx * 1.05)},{_f(hy - ry * .55)} Z" fill="{hc}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>'
                         f'<path d="M{_f(hx - facing * rx * .2)},{_f(hy - ry * .55)} Q{_f(hx + facing * rx * .9)},{_f(hy - ry * .45)} {_f(hx + facing * rx * 1.25)},{_f(hy - ry * .62)}" stroke="{INK}" stroke-width="{_f(D * .07)}" fill="none" stroke-linecap="round"/>'
                         f'<circle cx="{_f(hx)}" cy="{_f(hy - ry * .85)}" r="{_f(rx * .14)}" fill="{GOLD}" stroke="{INK}" stroke-width="{_f(ow * .5)}"/>')
            extra = ry * .3
        if hs == 'fedora':  # mu phot (thap nien 1940)
            front.append(f'<path d="M{_f(hx - rx * 1.45)},{_f(hy - ry * .55)} Q{_f(hx)},{_f(hy - ry * .75)} {_f(hx + rx * 1.45)},{_f(hy - ry * .55)} Q{_f(hx)},{_f(hy - ry * .4)} {_f(hx - rx * 1.45)},{_f(hy - ry * .55)} Z" fill="{hc}" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                         f'<path d="M{_f(hx - rx * .85)},{_f(hy - ry * .62)} L{_f(hx - rx * .75)},{_f(hy - ry * 1.3)} Q{_f(hx)},{_f(hy - ry * 1.12)} {_f(hx + rx * .75)},{_f(hy - ry * 1.3)} L{_f(hx + rx * .85)},{_f(hy - ry * .62)} Z" fill="{hc}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>'
                         f'<path d="M{_f(hx - rx * .84)},{_f(hy - ry * .72)} L{_f(hx + rx * .84)},{_f(hy - ry * .72)}" stroke="#7a1f1a" stroke-width="{_f(D * .05)}"/>')
            extra = ry * .35
        if hs == 'nurse':   # toc bui + mu y ta trang
            back.append(f'<circle cx="{_f(hx - facing * rx * .95)}" cy="{_f(hy - ry * .3)}" r="{_f(rx * .38)}" fill="{hair}" stroke="{INK}" stroke-width="{_f(ow)}"/>')
            front.append(f'<path d="M{_f(hx - rx)},{_f(hy - 4 * s)} Q{_f(hx - rx)},{_f(hy - ry * 1.1)} {_f(hx)},{_f(hy - ry)} Q{_f(hx + rx)},{_f(hy - ry * 1.1)} {_f(hx + rx)},{_f(hy - 4 * s)} Q{_f(hx + facing * rx * .2)},{_f(hy - ry * .55)} {_f(hx - rx)},{_f(hy - 4 * s)} Z" fill="{hair}"/>'
                         f'<path d="M{_f(hx - rx * .6)},{_f(hy - ry * .85)} L{_f(hx - rx * .5)},{_f(hy - ry * 1.25)} L{_f(hx + rx * .5)},{_f(hy - ry * 1.25)} L{_f(hx + rx * .6)},{_f(hy - ry * .85)} Z" fill="#fff" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                         f'<path d="M{_f(hx)},{_f(hy - ry * 1.18)} l0,{_f(ry * .26)} M{_f(hx - ry * .13)},{_f(hy - ry * 1.05)} l{_f(ry * .26)},0" stroke="#c4281f" stroke-width="{_f(D * .03)}"/>')
            extra = ry * .3
    if hs == 'helmet':
        front.append(f'<path d="M{_f(hx - rx * 1.1)},{_f(hy - ry * .1)} Q{_f(hx)},{_f(hy - ry * 1.6)} {_f(hx + rx * 1.1)},{_f(hy - ry * .1)} Z" fill="{c.get("helm", "#5e5440")}" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                     f'<circle cx="{_f(hx)}" cy="{_f(hy - ry * 1.15)}" r="{_f(rx * .18)}" fill="#b8241e" stroke="{INK}" stroke-width="{_f(ow * .6)}"/>'); extra = ry * .4
    if hs == 'crown':
        front.append(f'<path d="M{_f(hx - rx * .7)},{_f(hy - ry * .7)} L{_f(hx - rx * .6)},{_f(hy - ry * 1.35)} L{_f(hx + rx * .6)},{_f(hy - ry * 1.35)} L{_f(hx + rx * .7)},{_f(hy - ry * .7)} Z" fill="#2a2018" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                     f'<rect x="{_f(hx - rx * .95)}" y="{_f(hy - ry * 1.45)}" width="{_f(rx * 1.9)}" height="{_f(ry * .16)}" fill="#2a2018" stroke="{INK}" stroke-width="{_f(ow * .6)}"/>'); extra = ry * .45
    return ''.join(back), ''.join(front), extra


SCALE, ANIM = 1.0, 1.0   # 28/11 CCK dang cck2: nhan vat nho lai (0.78), cu dong nhieu hon (ANIM 1.8)


def character(name, x, y, D, facing=1, expr='normal', hands=None, head_rot=0.0, lean=0.0, tag=True, t=0.0, hidden_below=None):
    D = D * SCALE
    c = dict(CH.CHARS.get(name) or EXTRA[name]); s = D / 150; ow = D * .045
    tq = int(t * 12) / 12.0                       # nhip giat kieu roi
    seed = sum(map(ord, name))
    bob = math.sin(t * 4.2 + seed) * D * .035 * ANIM      # nhap nho tren mat nuoc
    sway = math.sin(t * 2.1 + seed * .7) * 2.2 * ANIM + lean
    if ANIM > 1:   # roi lac dau, nghieng nguoi theo nhip (them hoat anh)
        head_rot = head_rot + math.sin(t * 3.3 + seed * 1.3) * 5 * (ANIM - 1)
        x = x + math.sin(t * .9 + seed) * D * .06 * (ANIM - 1)
    wm = c.get('w', 1.0)
    o = [f'<g transform="rotate({_f(sway * facing)} {_f(x)} {_f(y)})">']
    if hidden_below is not None:
        cid = f'rn{abs(hash((name, round(x), round(y)))) % 99999}'
        o.append(f'<clipPath id="{cid}"><rect x="{_f(x - D * 3)}" y="{_f(hidden_below - D * 5)}" width="{_f(D * 6)}" height="{_f(D * 5)}"/></clipPath><g clip-path="url(#{cid})">')
    o.append(f'<g transform="translate(0 {_f(bob)})">')
    # ---- be vay son do (dau an chung) ----
    bh = D * .5; bwb = D * .98 * wm; bwt = D * .7 * wm; by = y - bh
    o.append(f'<path d="M{_f(x - bwb / 2)},{_f(y)} Q{_f(x - bwb * .44)},{_f(y - bh * .7)} {_f(x - bwt / 2)},{_f(by)} L{_f(x + bwt / 2)},{_f(by)} Q{_f(x + bwb * .44)},{_f(y - bh * .7)} {_f(x + bwb / 2)},{_f(y)} Z" fill="{LAC}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>')
    o.append(f'<path d="M{_f(x - bwb * .46)},{_f(y - bh * .2)} L{_f(x + bwb * .46)},{_f(y - bh * .2)}" stroke="{GOLD}" stroke-width="{_f(D * .045)}"/>')
    o.append(f'<path d="M{_f(x - bwt * .5)},{_f(by + D * .02)} L{_f(x + bwt * .5)},{_f(by + D * .02)}" stroke="{GOLD}" stroke-width="{_f(D * .03)}"/>')
    for k in (-1, 0, 1):
        cx_ = x + k * bwb * .26
        o.append(f'<path d="M{_f(cx_ - D * .07)},{_f(y - bh * .52)} q{_f(D * .07)},{_f(-D * .1)} {_f(D * .14)},0 q{_f(-D * .04)},{_f(D * .06)} {_f(-D * .07)},{_f(D * .02)}" stroke="{GOLD}" stroke-width="{_f(D * .022)}" fill="none"/>')
    # ---- than go ----
    th = D * .72; ty = by - th; tw0 = D * .7 * wm; tw1 = D * .58 * wm
    body = (f'M{_f(x - tw0 / 2)},{_f(by)} L{_f(x - tw1 / 2)},{_f(ty + D * .12)} Q{_f(x - tw1 / 2)},{_f(ty)} {_f(x - tw1 / 2 + D * .12)},{_f(ty)} '
            f'L{_f(x + tw1 / 2 - D * .12)},{_f(ty)} Q{_f(x + tw1 / 2)},{_f(ty)} {_f(x + tw1 / 2)},{_f(ty + D * .12)} L{_f(x + tw0 / 2)},{_f(by)} Z')
    if c.get('cape'):
        o.append(f'<path d="M{_f(x - facing * tw1 * .3)},{_f(ty + D * .05)} Q{_f(x - facing * tw0 * 1.1)},{_f(by - D * .2)} {_f(x - facing * tw0 * .9)},{_f(by + D * .1)} L{_f(x)},{_f(by)} Z" fill="{c["cape"]}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>')
    o.append(f'<path d="{body}" fill="{c["outfit"]}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>')
    if c.get('open_shirt'):
        o.append(f'<path d="M{_f(x - D * .14)},{_f(ty + D * .02)} L{_f(x)},{_f(ty + th * .5)} L{_f(x + D * .14)},{_f(ty + D * .02)} Z" fill="{c["skin"]}" stroke="{INK}" stroke-width="{_f(D * .02)}"/>')
    else:
        o.append(f'<path d="M{_f(x + facing * D * .05)},{_f(ty + D * .02)} L{_f(x - facing * D * .1)},{_f(ty + th * .45)}" stroke="{c.get("outfit2", INK)}" stroke-width="{_f(D * .035)}"/>')
    if c.get('tattoo'):
        o.append(f'<path d="M{_f(x - D * .24)},{_f(ty + th * .55)} q{_f(D * .1)},{_f(-D * .12)} {_f(D * .19)},0 t{_f(D * .19)},0" stroke="#2d5e8a" stroke-width="{_f(D * .035)}" fill="none" stroke-linecap="round"/>'
                 f'<circle cx="{_f(x - D * .24)}" cy="{_f(ty + th * .55)}" r="{_f(D * .03)}" fill="#2d5e8a"/>')
    if c.get('scales'):
        for k in range(2):
            yy = ty + th * (.55 + k * .2)
            o.append(f'<path d="M{_f(x - tw0 * .42)},{_f(yy)} q{_f(tw0 * .21)},{_f(D * .07)} {_f(tw0 * .42)},0 q{_f(tw0 * .21)},{_f(D * .07)} {_f(tw0 * .42)},0" stroke="{c.get("outfit2", INK)}" stroke-width="{_f(D * .03)}" fill="none"/>')
    o.append(f'<path d="M{_f(x - tw0 * .46)},{_f(ty + th * .72)} L{_f(x + tw0 * .46)},{_f(ty + th * .72)}" stroke="{c.get("trim", GOLD)}" stroke-width="{_f(D * .07)}"/>')
    # vet bong son mai tren than
    o.append(f'<path d="M{_f(x + facing * tw1 * .18)},{_f(ty + D * .1)} q{_f(D * .04)},{_f(th * .35)} {_f(-D * .03)},{_f(th * .75)}" stroke="#fff" stroke-opacity=".3" stroke-width="{_f(D * .055)}" fill="none" stroke-linecap="round"/>')
    # ---- dau ----
    mark = c.get('mark') or MARKS.get(name)
    rx, ry = D * .4, D * .47
    if mark == 'bigface': rx, ry = D * .47, D * .5
    hx = x + facing * D * .04; hy = ty - D * .1 - ry
    hr = head_rot + (2.5 * math.sin(tq * 5) if expr in ('normal', 'happy') else 0)
    o.append(f'<rect x="{_f(x - D * .09)}" y="{_f(ty - D * .16)}" width="{_f(D * .18)}" height="{_f(D * .2)}" fill="{WOOD}" stroke="{INK}" stroke-width="{_f(ow * .8)}"/>')
    back, front, extra = _head(c, hx, hy, rx, ry, D, facing)
    o.append(f'<g transform="rotate({_f(hr * facing)} {_f(x)} {_f(ty)})">')
    o.append(back)
    o.append(f'<ellipse cx="{_f(hx)}" cy="{_f(hy)}" rx="{_f(rx)}" ry="{_f(ry)}" fill="{c["skin"]}" stroke="{INK}" stroke-width="{_f(ow)}"/>')
    o.append(front)
    o.append(f'<path d="M{_f(hx - facing * rx * .55)},{_f(hy - ry * .3)} q{_f(facing * rx * .2)},{_f(-ry * .35)} {_f(facing * rx * .6)},{_f(-ry * .42)}" stroke="#fff" stroke-opacity=".5" stroke-width="{_f(D * .05)}" fill="none" stroke-linecap="round"/>')
    o.append(_face(c, name, hx, hy, rx, ry, D, facing, expr))
    o.append('</g>')
    o.append('</g>')   # het bob
    if hidden_below is not None: o.append('</g>')
    # ---- tay + do cam (do luon tren ban tay) ----
    L = D * .36; shy = ty + D * .14 + bob
    cxb, cyb = x, ty + th * .5 + bob
    tips, arms, props = [], [], []
    hs = list(hands or [])
    if not hs:   # tay roi buong xuoi, giat nhe theo nhip
        sw = math.sin(tq * 3 + seed) * .06
        hs = [(.48, .32 + sw, None), (-.42, .34 - sw, None)]
    for h in hs:
        dx, dy = h[0], h[1]; pk = h[2] if len(h) > 2 else None; ang = h[3] if len(h) > 3 else 0
        tx_, ty_ = cxb + facing * dx * D, cyb + dy * D
        side = 1 if dx * facing >= 0 else -1
        sx = x + side * tw1 * .42
        a_svg, (hx2, hy2) = _arm(sx, shy, tx_, ty_, L, facing, c['outfit'], D, c['skin'])
        arms.append(a_svg)
        if pk:
            ex_ = _prop_extra(pk, hx2, hy2, D, facing)
            if ex_: ps, tip = ex_
            else: ps, tip = CH.prop_svg(pk, hx2, hy2, ang if facing > 0 else 180 - ang, D)
            props.append(ps); tips.append(tip)
        props.append(_hand(hx2, hy2, D, c['skin']))
    o.append(''.join(arms)); o.append(''.join(props))
    o.append('</g>')
    if tag and c.get('tag'):
        tyy = hy - ry - extra - D * .12 + bob
        if CH.TAGS is not None:
            CH.TAGS.append(dict(x=hx, y=tyy, D=D, text=c['tag'], tilt=abs(lean) + abs(head_rot) * .3))
        else:
            o.append(plaque(c['tag'], hx, tyy, max(22, D * .2)))
    return ''.join(o), tips


def plaque(text, x, y_bottom, fs):
    """bien go treo day: tra svg, day bien tai y_bottom."""
    w = fs * .68 * len(text) + 34; h = fs + 16; y0 = y_bottom - h
    return (f'<path d="M{_f(x - w * .28)},{_f(y0 + 4)} L{_f(x)},{_f(y0 - fs * .7)} L{_f(x + w * .28)},{_f(y0 + 4)}" stroke="#3a2a1a" stroke-width="2.5" fill="none"/>'
            f'<circle cx="{_f(x)}" cy="{_f(y0 - fs * .7)}" r="4.5" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>'
            f'<rect x="{_f(x - w / 2)}" y="{_f(y0)}" width="{_f(w)}" height="{_f(h)}" rx="6" fill="#7a4a24" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="{_f(x - w / 2 + 6)}" y="{_f(y0 + 5)}" width="{_f(w - 12)}" height="{_f(h - 10)}" rx="3" fill="none" stroke="{GOLD}" stroke-width="2"/>'
            f'<text x="{_f(x)}" y="{_f(y_bottom - 9)}" font-family="Be Vietnam Pro, Inter" font-weight="800" font-size="{_f(fs)}" fill="#f6e3b0" text-anchor="middle">{text}</text>')


def install(M, cast=None):
    """M = ksc_svg dang chay. Doi nhan vat + kieu bang ten. cast = {id: cau hinh} tu spec (nhan vat rieng tung tap)."""
    for k, v in EXTRA.items(): CH.CHARS.setdefault(k, v)
    for k, v in (cast or {}).items(): CH.CHARS[k] = v
    CH.character = character
    M.TAG_STYLE = 'go'
