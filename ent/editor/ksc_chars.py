"""Bo nhan vat Ky Su Chien theo skill "hoat-hinh-2d-ve-bang-code" (don vi D = be rong dau).
- Cao ~2,2D: dau tron D (toc + dau 1 khoi), than ong 1,1D x 0,88D day bo tron, khong co, khong chan, khong canh tay.
- Ban tay tron r 0,14D lo lung, chi hien khi cam do / chi tro. Vien ngoai 0,045D #111, chi tiet 0,025D.
- Quay 3/4, mac dinh nhin phai; facing=-1 lat lai. 6 bieu cam: normal, happy, angry, sad, surprised, scared.
- Bang ten luon tren dau. Ve 2 luot: luot 1 khoi den + stroke den gap doi vien, luot 2 to mau khong stroke.
Moi nhan vat chi la 1 cau hinh trong CHARS; sua ham chung la ca dan doi theo.
"""
import math

INK = '#111'
TAGS = None   # list -> gom nhan ten thay vi ve tai cho
CHARS = {
    'ngoquyen': dict(tag='NGÔ QUYỀN', skin='#e0a878', hair='#1b1512', hair_style='topknot', outfit='#3a3a48', outfit2='#26262f', trim='#d4aa3c', cape='#b8241e', prop='sword', beard=True),
    'linhviet': dict(tag='QUÂN TA', skin='#d69a68', hair='#1e1714', hair_style='band', band='#c4281f', outfit='#34428a', outfit2='#26326a', trim='#c4281f', prop='spear'),
    'linhviet2': dict(tag='QUÂN TA', skin='#cd9262', hair='#1e1714', hair_style='band', band='#c4281f', outfit='#7e5434', outfit2='#5e3e26', trim='#c4281f', prop='oar'),
    'hoangthao': dict(tag='LƯU HOẰNG THÁO', skin='#ecbd8c', hair='#16120f', hair_style='crown', outfit='#b89a3c', outfit2='#8a7028', trim='#7a1c1a', prop='sword'),
    'linhhan': dict(tag='QUÂN NAM HÁN', skin='#e8b588', hair='#16120f', hair_style='helmet', helm='#5e5440', outfit='#847660', outfit2='#5f5444', trim='#7a1c1a', prop='spear', scales=True),
    'tranhungdao': dict(tag='TRẦN HƯNG ĐẠO', skin='#dca070', hair='#1b1512', hair_style='topknot', outfit='#7a2420', outfit2='#561814', trim='#d4aa3c', cape='#2b2b36', prop='sword', beard=True),
    'linhnguyen': dict(tag='QUÂN NGUYÊN', skin='#e2b07e', hair='#16120f', hair_style='helmet', helm='#7a5a34', outfit='#4d5c3c', outfit2='#36422a', trim='#2a2018', prop='spear', scales=True),
    'anduongvuong': dict(tag='AN DƯƠNG VƯƠNG', skin='#e0a878', hair='#1b1512', hair_style='crown', outfit='#a8822c', outfit2='#7e601c', trim='#7a1c1a', cape='#7a1c1a', prop='sword', beard=True),
    'caolo': dict(tag='CAO LỖ', skin='#d69a68', hair='#1b1512', hair_style='topknot', outfit='#3e5a3a', outfit2='#2c4229', trim='#d4aa3c', prop='crossbow', beard=True),
    'linhaulac': dict(tag='QUÂN ÂU LẠC', skin='#d69a68', hair='#1e1714', hair_style='band', band='#c4281f', outfit='#5a6e3a', outfit2='#41502a', trim='#c4281f', prop='crossbow'),
    'linhtrieu': dict(tag='QUÂN TRIỆU ĐÀ', skin='#e8b588', hair='#16120f', hair_style='helmet', helm='#4e4a44', outfit='#6c6a74', outfit2='#4e4c56', trim='#2a2018', prop='spear', scales=True),
    'trieuda': dict(tag='TRIỆU ĐÀ', skin='#ecbd8c', hair='#16120f', hair_style='crown', outfit='#3e3c48', outfit2='#2a2832', trim='#b8963e', cape='#4e4c56', prop='sword', beard=True),
    'hoctro': dict(tag='HỌC TRÒ', skin='#ecb88a', hair='#1e1714', hair_style='nonla', hat='#e2c47a', outfit='#efe6cf', outfit2='#cfc3a3', trim='#5a8a5a', prop='board'),
}


def _f(v): return f'{v:.1f}'


def head_shapes(c, cx, cy, D, facing):
    """khoi dau + toc (1 khoi). Tra ve list path (d, fill)."""
    r = D / 2; out = []
    hs = c.get('hair_style')
    # dau + toc chung 1 khoi: hinh tron + mai toc phia sau/tren
    hair_pts = (f'M{_f(cx - r)},{_f(cy)} A{_f(r)},{_f(r)} 0 0 1 {_f(cx + r)},{_f(cy)} '
                f'L{_f(cx + r * .98)},{_f(cy - r * .05)} Q{_f(cx + r * .2 * facing)},{_f(cy - r * .55)} {_f(cx - r * .98)},{_f(cy - r * .05)} Z')
    out.append(('circle', (cx, cy, r), c['skin']))
    out.append(('path', hair_pts, c['hair']))
    if hs == 'topknot':
        out.append(('circle', (cx - facing * r * .15, cy - r * 1.08, r * .32), c['hair']))
    return out


def prop_svg(kind, hx, hy, ang, D, col_dark='#6b4a2a'):
    """do cam tay, goc ang (do, 0 = huong phai, + quay xuong). Tra ve svg (2 luot vien)."""
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a)
    ow = D * .045
    def line(x1, y1, x2, y2, w, col):
        return (f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{INK}" stroke-width="{_f(w + 2 * ow)}" stroke-linecap="round"/>'
                f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{col}" stroke-width="{_f(w)}" stroke-linecap="round"/>')
    def poly(pts, col):
        s = ' '.join(f'{_f(x)},{_f(y)}' for x, y in pts)
        return f'<polygon points="{s}" fill="{col}" stroke="{INK}" stroke-width="{_f(ow)}" stroke-linejoin="round"/>'
    if kind == 'spear':
        b = (hx - ux * D * .9, hy - uy * D * .9); t = (hx + ux * D * 1.7, hy + uy * D * 1.7)
        tip = (t[0] + ux * D * .34, t[1] + uy * D * .34); px, py = -uy * D * .1, ux * D * .1
        return line(*b, *t, D * .07, '#8a5e34') + poly([(t[0] + px, t[1] + py), tip, (t[0] - px, t[1] - py)], '#c9ccd4'), tip
    if kind == 'sword':
        t = (hx + ux * D * 1.15, hy + uy * D * 1.15); px, py = -uy * D * .16, ux * D * .16
        return line(hx, hy, *t, D * .1, '#d8dbe2') + line(hx + px, hy + py, hx - px, hy - py, D * .07, '#7a5a2a'), t
    if kind == 'oar':
        b = (hx - ux * D * .35, hy - uy * D * .35); t = (hx + ux * D * 1.9, hy + uy * D * 1.9); bl = (t[0] + ux * D * .5, t[1] + uy * D * .5)
        return line(*b, *t, D * .07, '#9a6a3c') + line(*t, *bl, D * .22, '#a8743f'), bl
    if kind == 'mallet':
        t = (hx + ux * D * .9, hy + uy * D * .9); px, py = -uy * D * .26, ux * D * .26
        return line(hx, hy, *t, D * .08, '#8a5e34') + line(t[0] + px, t[1] + py, t[0] - px, t[1] - py, D * .3, '#6b4524'), t
    if kind == 'flag':
        t = (hx + ux * D * 1.8, hy + uy * D * 1.8); b = (hx - ux * D * .5, hy - uy * D * .5)
        return line(*b, *t, D * .07, '#8a5e34') + poly([t, (t[0] + D * .75, t[1] + D * .2), (t[0] + D * .05, t[1] + D * .55)], '#c4281f'), t
    if kind == 'board':
        t = (hx + ux * D * 1.0, hy + uy * D * 1.0)
        return line(hx, hy, *t, D * .05, '#6b4a2a'), t
    if kind in ('crossbow', 'crossbow_r'):   # nỏ: bang ngang + canh cung o dau + day; 'crossbow_r' = day da bat
        t = (hx + ux * D * 1.25, hy + uy * D * 1.25); b = (hx - ux * D * .25, hy - uy * D * .25)
        px, py = -uy, ux; bw = D * .55; fx_, fy_ = hx + ux * D * 1.0, hy + uy * D * 1.0
        a1 = (fx_ + px * bw - ux * D * .18, fy_ + py * bw - uy * D * .18); a2 = (fx_ - px * bw - ux * D * .18, fy_ - py * bw - uy * D * .18)
        nut = (hx + ux * D * .15, hy + uy * D * .15) if kind == 'crossbow' else (fx_ - ux * D * .05, fy_ - uy * D * .05)
        bow = f'<path d="M{_f(a1[0])},{_f(a1[1])} Q{_f(fx_ + ux * D * .12)},{_f(fy_ + uy * D * .12)} {_f(a2[0])},{_f(a2[1])}" stroke="{INK}" stroke-width="{_f(D * .13)}" fill="none" stroke-linecap="round"/><path d="M{_f(a1[0])},{_f(a1[1])} Q{_f(fx_ + ux * D * .12)},{_f(fy_ + uy * D * .12)} {_f(a2[0])},{_f(a2[1])}" stroke="#7a5230" stroke-width="{_f(D * .07)}" fill="none" stroke-linecap="round"/>'
        strg = f'<path d="M{_f(a1[0])},{_f(a1[1])} L{_f(nut[0])},{_f(nut[1])} L{_f(a2[0])},{_f(a2[1])}" stroke="#e8e0c8" stroke-width="{_f(D * .025)}" fill="none"/>'
        arrow = line(nut[0], nut[1], t[0], t[1], D * .035, '#c9a35a') if kind == 'crossbow' else ''
        trig = f'<rect x="{_f(hx - D * .05)}" y="{_f(hy)}" width="{_f(D * .1)}" height="{_f(D * .18)}" fill="#d4aa3c" stroke="{INK}" stroke-width="{_f(ow * .6)}"/>'
        return line(*b, *t, D * .09, '#8a5e34') + trig + bow + strg + arrow, t
    if kind == 'shovel':
        t = (hx + ux * D * 1.2, hy + uy * D * 1.2); px, py = -uy * D * .2, ux * D * .2
        return line(hx - ux * D * .4, hy - uy * D * .4, *t, D * .07, '#8a5e34') + poly([(t[0] + px, t[1] + py), (t[0] + ux * D * .45 + px * .6, t[1] + uy * D * .45 + py * .6), (t[0] + ux * D * .45 - px * .6, t[1] + uy * D * .45 - py * .6), (t[0] - px, t[1] - py)], '#a8adb6'), t
    if kind == 'shield':
        return (f'<circle cx="{_f(hx)}" cy="{_f(hy)}" r="{_f(D * .42)}" fill="#9c6e3c" stroke="{INK}" stroke-width="{_f(ow)}"/>'
                f'<circle cx="{_f(hx)}" cy="{_f(hy)}" r="{_f(D * .14)}" fill="#6e4a26" stroke="{INK}" stroke-width="{_f(ow * .6)}"/>'), (hx, hy)
    return '', (hx, hy)


def face_svg(c, cx, cy, D, facing, expr, t=0.0):
    r = D / 2; ow2 = D * .025; s = []
    ex = cx + facing * r * .28; ex2 = cx + facing * r * .62    # 2 mat lech ve huong nhin (3/4)
    ey = cy + r * .12
    def eye(x, big=False):
        if expr == 'happy':
            return f'<path d="M{_f(x - r * .12)},{_f(ey + r * .03)} Q{_f(x)},{_f(ey - r * .14)} {_f(x + r * .12)},{_f(ey + r * .03)}" fill="none" stroke="{INK}" stroke-width="{_f(ow2 * 1.4)}" stroke-linecap="round"/>'
        if expr == 'surprised':
            return f'<circle cx="{_f(x)}" cy="{_f(ey)}" r="{_f(r * .13)}" fill="#fff" stroke="{INK}" stroke-width="{_f(ow2)}"/><circle cx="{_f(x)}" cy="{_f(ey)}" r="{_f(r * .05)}" fill="{INK}"/>'
        return f'<ellipse cx="{_f(x)}" cy="{_f(ey)}" rx="{_f(r * .065)}" ry="{_f(r * .1)}" fill="{INK}"/>'
    s.append(eye(ex)); s.append(eye(ex2))
    # long may
    bw = r * .16; by = ey - r * .2
    for x in (ex, ex2):
        if expr == 'angry':
            inner = 1 if (x - cx) * facing < r * .4 else -1
            s.append(f'<line x1="{_f(x - bw)}" y1="{_f(by - r * .06 * inner * facing)}" x2="{_f(x + bw)}" y2="{_f(by + r * .06 * inner * facing)}" stroke="{INK}" stroke-width="{_f(ow2 * 1.6)}" stroke-linecap="round"/>')
        elif expr in ('sad', 'scared'):
            s.append(f'<line x1="{_f(x - bw)}" y1="{_f(by + r * .04)}" x2="{_f(x + bw)}" y2="{_f(by - r * .05)}" stroke="{INK}" stroke-width="{_f(ow2 * 1.4)}" stroke-linecap="round"/>')
        else:
            s.append(f'<line x1="{_f(x - bw)}" y1="{_f(by)}" x2="{_f(x + bw)}" y2="{_f(by - r * .02)}" stroke="{INK}" stroke-width="{_f(ow2 * 1.3)}" stroke-linecap="round"/>')
    mx = cx + facing * r * .48; my = cy + r * .5
    if expr == 'happy':
        for x in (ex, ex2): s.append(f'<ellipse cx="{_f(x)}" cy="{_f(ey + r * .24)}" rx="{_f(r * .1)}" ry="{_f(r * .05)}" fill="#f08a8a" opacity=".75"/>')
    if expr == 'angry':   # gan do tren tran
        gx, gy = cx - facing * r * .25, cy - r * .3
        s.append(f'<path d="M{_f(gx - r * .1)},{_f(gy)} l{_f(r * .08)},{_f(r * .04)} M{_f(gx + r * .1)},{_f(gy)} l{_f(-r * .08)},{_f(r * .04)} M{_f(gx)},{_f(gy - r * .1)} l0,{_f(r * .08)}" stroke="#d01f1f" stroke-width="{_f(ow2 * 1.5)}" stroke-linecap="round"/>')
        s.append(f'<path d="M{_f(mx - r * .1)},{_f(my)} l{_f(r * .2)},0" stroke="{INK}" stroke-width="{_f(ow2 * 1.4)}" stroke-linecap="round"/>')
    if expr == 'sad':
        tx, ty = ex2 + facing * r * .02, ey + r * .2
        s.append(f'<path d="M{_f(tx)},{_f(ty)} q{_f(r * .07)},{_f(r * .14)} 0,{_f(r * .18)} q{_f(-r * .07)},{_f(-r * .04)} 0,{_f(-r * .18)}" fill="#7cc4f0" stroke="{INK}" stroke-width="{_f(ow2 * .6)}"/>')
    if expr == 'surprised':
        s.append(f'<ellipse cx="{_f(mx)}" cy="{_f(my)}" rx="{_f(r * .07)}" ry="{_f(r * .1)}" fill="#5a1a1a" stroke="{INK}" stroke-width="{_f(ow2)}"/>')
    if expr == 'scared':
        for k in range(3):
            x = cx - facing * r * (.05 - k * .15)
            s.append(f'<line x1="{_f(x)}" y1="{_f(cy - r * .55)}" x2="{_f(x)}" y2="{_f(cy - r * .25)}" stroke="#7a3fb0" stroke-width="{_f(ow2 * 1.3)}" stroke-linecap="round"/>')
        sx, sy = cx - facing * r * .85, cy - r * .1
        s.append(f'<path d="M{_f(sx)},{_f(sy)} q{_f(r * .08)},{_f(r * .16)} 0,{_f(r * .2)} q{_f(-r * .08)},{_f(-r * .04)} 0,{_f(-r * .2)}" fill="#9fd8f5" stroke="{INK}" stroke-width="{_f(ow2 * .6)}"/>')
        s.append(f'<path d="M{_f(mx - r * .08)},{_f(my)} q{_f(r * .04)},{_f(-r * .05)} {_f(r * .08)},0 q{_f(r * .04)},{_f(r * .05)} {_f(r * .08)},0" fill="none" stroke="{INK}" stroke-width="{_f(ow2)}"/>')
    return ''.join(s)


def character(name, x, y, D, facing=1, expr='normal', hands=None, head_rot=0.0, lean=0.0, tag=True, t=0.0, hidden_below=None):
    """x,y = diem cham dat (day than). hands = [(dx, dy, prop, ang)] theo don vi D tinh tu tam than (dx theo huong nhin).
    lean = nghieng ca nguoi (do, + nga ve phia truoc). hidden_below: y cat than (ngoi trong thuyen)."""
    c = CHARS[name]; r = D / 2; ow = D * .045
    bw, bh = D * .88, D * 1.1
    bx0, by0 = x - bw / 2, y - bh
    hcx, hcy = x + facing * D * .04, by0 - r * .9
    tr = f'rotate({_f(lean * facing)} {_f(x)} {_f(y)})'
    body = f'M{_f(bx0)},{_f(by0 + D * .2)} Q{_f(bx0)},{_f(by0)} {_f(bx0 + D * .2)},{_f(by0)} L{_f(bx0 + bw - D * .2)},{_f(by0)} Q{_f(bx0 + bw)},{_f(by0)} {_f(bx0 + bw)},{_f(by0 + D * .2)} L{_f(bx0 + bw)},{_f(y - D * .3)} Q{_f(bx0 + bw)},{_f(y)} {_f(x)},{_f(y)} Q{_f(bx0)},{_f(y)} {_f(bx0)},{_f(y - D * .3)} Z'
    hs = head_shapes(c, hcx, hcy, D, facing)
    extra_back, extra_front = [], []
    if c.get('cape'):
        extra_back.append(('path', f'M{_f(x - facing * bw * .35)},{_f(by0 + D * .1)} Q{_f(x - facing * bw * 1.0)},{_f(y - D * .4)} {_f(x - facing * bw * .8)},{_f(y)} L{_f(x)},{_f(y)} Z', c['cape']))
    if c.get('hair_style') == 'helmet':
        extra_front.append(('path', f'M{_f(hcx - r * 1.08)},{_f(hcy - r * .05)} Q{_f(hcx)},{_f(hcy - r * 1.55)} {_f(hcx + r * 1.08)},{_f(hcy - r * .05)} Z', c['helm']))
        extra_front.append(('circle', (hcx, hcy - r * 1.22, r * .16), '#b8241e'))
    if c.get('hair_style') == 'crown':
        extra_front.append(('path', f'M{_f(hcx - r * .6)},{_f(hcy - r * .75)} L{_f(hcx - r * .5)},{_f(hcy - r * 1.35)} L{_f(hcx + r * .5)},{_f(hcy - r * 1.35)} L{_f(hcx + r * .6)},{_f(hcy - r * .75)} Z', '#2a2018'))
        extra_front.append(('path', f'M{_f(hcx - r * .85)},{_f(hcy - r * 1.35)} L{_f(hcx + r * .85)},{_f(hcy - r * 1.35)} L{_f(hcx + r * .85)},{_f(hcy - r * 1.2)} L{_f(hcx - r * .85)},{_f(hcy - r * 1.2)} Z', '#2a2018'))
    if c.get('hair_style') == 'nonla':
        extra_front.append(('path', f'M{_f(hcx - r * 1.5)},{_f(hcy - r * .45)} L{_f(hcx)},{_f(hcy - r * 1.6)} L{_f(hcx + r * 1.5)},{_f(hcy - r * .45)} Z', c['hat']))
    def draw(shapes, pass_):
        out = []
        for kind, g, col in shapes:
            if pass_ == 1:
                st = f'fill="{INK}" stroke="{INK}" stroke-width="{_f(ow * 2)}" stroke-linejoin="round"'
            else:
                st = f'fill="{col}"'
            if kind == 'circle': out.append(f'<circle cx="{_f(g[0])}" cy="{_f(g[1])}" r="{_f(g[2])}" {st}/>')
            else: out.append(f'<path d="{g}" {st}/>')
        return ''.join(out)
    shapes = extra_back + [('path', body, c['outfit'])] + hs + extra_front
    s = [f'<g transform="{tr}">']
    if hidden_below is not None: s.append(f'<clipPath id="cl{abs(hash((name, x, y))) % 99999}"><rect x="{_f(x - D * 3)}" y="{_f(hidden_below - D * 4)}" width="{_f(D * 6)}" height="{_f(D * 4)}"/></clipPath><g clip-path="url(#cl{abs(hash((name, x, y))) % 99999})">')
    s.append(draw(shapes, 1)); s.append(draw(shapes, 2))
    # chi tiet trang phuc (vien mong)
    ow2 = D * .025
    s.append(f'<path d="M{_f(bx0 + D * .05)},{_f(by0 + bh * .45)} L{_f(bx0 + bw - D * .05)},{_f(by0 + bh * .45)}" stroke="{c["trim"]}" stroke-width="{_f(D * .09)}"/>')
    s.append(f'<path d="M{_f(x + facing * D * .05)},{_f(by0 + D * .05)} L{_f(x - facing * D * .12)},{_f(by0 + bh * .42)}" stroke="{c["outfit2"]}" stroke-width="{_f(ow2 * 2)}" fill="none"/>')
    if c.get('scales'):
        for k in range(3):
            yy = by0 + bh * (.55 + k * .14)
            s.append(f'<path d="M{_f(bx0 + D * .08)},{_f(yy)} q{_f(bw * .2)},{_f(D * .08)} {_f(bw * .42)},0 q{_f(bw * .2)},{_f(D * .08)} {_f(bw * .42)},0" stroke="{c["outfit2"]}" stroke-width="{_f(ow2 * 1.5)}" fill="none"/>')
    if c.get('hair_style') == 'band':
        s.append(f'<path d="M{_f(hcx - r * .97)},{_f(hcy - r * .18)} Q{_f(hcx)},{_f(hcy - r * .42)} {_f(hcx + r * .97)},{_f(hcy - r * .18)}" stroke="{c["band"]}" stroke-width="{_f(D * .1)}" fill="none"/>')
        tx = hcx - facing * r * 1.0; wv = math.sin(t * 9) * D * .06
        s.append(f'<path d="M{_f(tx)},{_f(hcy - r * .2)} q{_f(-facing * D * .2)},{_f(wv)} {_f(-facing * D * .34)},{_f(D * .12 + wv)}" stroke="{c["band"]}" stroke-width="{_f(D * .08)}" fill="none" stroke-linecap="round"/>')
    if c.get('beard'):
        s.append(f'<path d="M{_f(hcx + facing * r * .2)},{_f(hcy + r * .78)} q{_f(facing * r * .15)},{_f(r * .5)} {_f(facing * r * .35)},{_f(r * .1)}" fill="{c["hair"]}" stroke="{INK}" stroke-width="{_f(ow2)}"/>')
    if c.get('hair_style') == 'nonla':
        s.append(f'<path d="M{_f(hcx - r * .7)},{_f(hcy - r * .78)} L{_f(hcx + r * .7)},{_f(hcy - r * .78)}" stroke="#b8963e" stroke-width="{_f(ow2)}"/>')
    s.append(face_svg(c, hcx, hcy, D, facing, expr, t))
    if hidden_below is not None: s.append('</g>')
    # ban tay + do cam (do luon tren ban tay)
    tips = []
    cxb, cyb = x, y - bh * .5
    hand_svg, prop_layer = [], []
    for h in (hands or []):
        dx, dy = h[0], h[1]; pk = h[2] if len(h) > 2 else None; ang = h[3] if len(h) > 3 else 0
        hx, hy = cxb + facing * dx * D, cyb + dy * D
        a_world = ang if facing > 0 else 180 - ang
        if pk:
            ps, tip = prop_svg(pk, hx, hy, a_world, D); prop_layer.append(ps); tips.append(tip)
        hand_svg.append(f'<circle cx="{_f(hx)}" cy="{_f(hy)}" r="{_f(D * .14)}" fill="{c["skin"]}" stroke="{INK}" stroke-width="{_f(ow)}"/>')
    s.append(''.join(hand_svg)); s.append(''.join(prop_layer))
    s.append('</g>')
    if tag and c.get('tag'):
        ty = hcy - r * (1.95 if c.get('hair_style') in ('helmet', 'nonla', 'crown', 'topknot') else 1.45)
        if TAGS is not None:   # gom nhan len lop tren cung, frame_svg loc va ve (khong bi buom/thuyen che)
            TAGS.append(dict(x=hcx, y=ty, D=D, text=c['tag'], tilt=abs(lean) + abs(head_rot) * .3))
        else:
            fs = max(18, D * .24); tw = fs * .72 * len(c['tag']) + 30
            s.append(f'<rect x="{_f(hcx - tw / 2)}" y="{_f(ty - fs - 4)}" width="{_f(tw)}" height="{_f(fs + 14)}" rx="{_f(fs * .4)}" fill="#111" opacity=".82"/>'
                     f'<text x="{_f(hcx)}" y="{_f(ty + 2)}" font-family="Be Vietnam Pro, Inter" font-weight="800" font-size="{_f(fs)}" fill="#ffd400" text-anchor="middle">{c["tag"]}</text>')
    return ''.join(s), tips
