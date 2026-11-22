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
    if hs == 'helmet':
        front.append(f'<path d="M{_f(hx - rx * 1.1)},{_f(hy - ry * .1)} Q{_f(hx)},{_f(hy - ry * 1.6)} {_f(hx + rx * 1.1)},{_f(hy - ry * .1)} Z" fill="{c.get("helm", "#5e5440")}" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                     f'<circle cx="{_f(hx)}" cy="{_f(hy - ry * 1.15)}" r="{_f(rx * .18)}" fill="#b8241e" stroke="{INK}" stroke-width="{_f(ow * .6)}"/>'); extra = ry * .4
    if hs == 'crown':
        front.append(f'<path d="M{_f(hx - rx * .7)},{_f(hy - ry * .7)} L{_f(hx - rx * .6)},{_f(hy - ry * 1.35)} L{_f(hx + rx * .6)},{_f(hy - ry * 1.35)} L{_f(hx + rx * .7)},{_f(hy - ry * .7)} Z" fill="#2a2018" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                     f'<rect x="{_f(hx - rx * .95)}" y="{_f(hy - ry * 1.45)}" width="{_f(rx * 1.9)}" height="{_f(ry * .16)}" fill="#2a2018" stroke="{INK}" stroke-width="{_f(ow * .6)}"/>'); extra = ry * .45
    return ''.join(back), ''.join(front), extra


def character(name, x, y, D, facing=1, expr='normal', hands=None, head_rot=0.0, lean=0.0, tag=True, t=0.0, hidden_below=None):
    c = dict(CH.CHARS.get(name) or EXTRA[name]); s = D / 150; ow = D * .045
    tq = int(t * 12) / 12.0                       # nhip giat kieu roi
    seed = sum(map(ord, name))
    bob = math.sin(t * 4.2 + seed) * D * .035      # nhap nho tren mat nuoc
    sway = math.sin(t * 2.1 + seed * .7) * 2.2 + lean
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


def install(M):
    """M = ksc_svg dang chay. Doi nhan vat + kieu bang ten."""
    for k, v in EXTRA.items(): CH.CHARS.setdefault(k, v)
    CH.character = character
    M.TAG_STYLE = 'go'
