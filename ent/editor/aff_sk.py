# aff_sk: engine ve tay (net run, to lech, gach bong) cho kind aff_sketch
import math, random

W, H = 1080, 1920
FPS = 15          # vẽ 15 hình/giây (kiểu hoạt hình vẽ tay "on twos"), xuất 30fps
INK = '#2b2420'
PAPER = '#f6eedb'
ORANGE = '#ff7a1a'
YEL = '#ffd23f'
STEEL = '#cfd8de'
RED = '#e0412f'
BLUE = '#3f7fd0'

BOIL = 0  # chỉ số "sôi nét" toàn cục, đặt mỗi khung


def R(*k):
    return random.Random(repr(k))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, u):
    return a + (b - a) * u


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def eout(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def eback(u):
    u = clamp(u)
    c = 1.9
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------- hình học ----------
def ell(cx, cy, rx, ry, n=None, a0=0):
    n = n or max(12, int((rx + ry) / 9))
    return [(cx + rx * math.cos(a0 + 2 * math.pi * i / n), cy + ry * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def resample(pts, closed, step=26):
    out = []
    m = len(pts) if closed else len(pts) - 1
    for i in range(m):
        a = pts[i]
        b = pts[(i + 1) % len(pts)]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / step))
        for j in range(n):
            u = j / n
            out.append((lerp(a[0], b[0], u), lerp(a[1], b[1], u)))
    if not closed:
        out.append(pts[-1])
    return out


def jit(pts, seed, amp):
    r = R(seed, BOIL)
    return [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in pts]


def smooth(pts, closed):
    n = len(pts)
    if n < 3:
        return 'M%.1f,%.1f L%.1f,%.1f' % (pts[0][0], pts[0][1], pts[-1][0], pts[-1][1])
    d = 'M%.1f,%.1f' % pts[0]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += ' C%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        d += 'Z'
    return d


def wpath(pts, seed, amp=2.2, closed=True, step=26):
    return smooth(jit(resample(pts, closed, step), seed, amp), closed)


def sk(shapes, fill=None, seed=0, w=5.0, amp=2.2, closed=True, off=(4, 3), hatch=None, op=1.0, step=26, double=True):
    """shapes: 1 list điểm hoặc list các list (đường evenodd)."""
    if shapes and isinstance(shapes[0], tuple):
        shapes = [shapes]
    o = ''
    if fill and closed:
        d = ' '.join(wpath([(x + off[0], y + off[1]) for x, y in s], (seed, 'f', i), amp * 1.3, True, step) for i, s in enumerate(shapes))
        o += '<path d="%s" fill="%s" fill-rule="evenodd" opacity="%.2f"/>' % (d, fill, op)
    if hatch:
        o += hatch
    d = ' '.join(wpath(s, (seed, 'a', i), amp, closed, step) for i, s in enumerate(shapes))
    o += '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round"/>' % (d, INK, w)
    if double:
        d2 = ' '.join(wpath(s, (seed, 'b', i), amp * 1.6, closed, step) for i, s in enumerate(shapes))
        o += '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round" opacity="0.45"/>' % (d2, INK, w * 0.45)
    return o


def line(pts, seed=0, w=5, amp=2.0, col=INK, op=1.0):
    d = wpath(pts, seed, amp, False, 22)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round" opacity="%.2f"/>' % (d, col, w, op)


def hatch_lines(x0, y0, x1, y1, gap=16, seed=0, w=2.2, col=INK, op=0.35, ang=1.0):
    """gạch chéo trong hộp (dùng kèm clipPath nếu cần)"""
    o = ''
    r = R(seed, BOIL)
    k = 0
    x = x0 - (y1 - y0) * ang
    while x < x1:
        a = (x + r.uniform(-3, 3), y1)
        b = (x + (y1 - y0) * ang + r.uniform(-3, 3), y0)
        o += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" opacity="%.2f" stroke-linecap="round"/>' % (a[0], a[1], b[0], b[1], col, w, op)
        x += gap
        k += 1
    return o


_clip_id = [0]


def clipped(shape_pts, inner):
    _clip_id[0] += 1
    cid = 'c%d' % _clip_id[0]
    d = smooth(resample(shape_pts, True), True)
    return '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">%s</g>' % (cid, d, cid, inner)


def text(x, y, s, size=40, col=INK, font="'Be Vietnam Pro', Montserrat", weight=800, anchor='middle', rot=0, stroke=None, sw=0, op=1.0, ls=0):
    tr = ' transform="rotate(%.2f %.1f %.1f)"' % (rot, x, y) if rot else ''
    st = ' stroke="%s" stroke-width="%.1f" stroke-linejoin="round" paint-order="stroke"' % (stroke, sw) if stroke else ''
    return '<text xml:space="preserve" x="%.1f" y="%.1f" font-family="%s" font-weight="%d" font-size="%.1f" fill="%s" text-anchor="%s" opacity="%.2f" letter-spacing="%.1f"%s%s>%s</text>' % (
        x, y, font, weight, size, col, anchor, op, ls, st, tr, esc(s))


# ---------- đạo cụ & hiệu ứng ----------
def star_burst(cx, cy, r, seed=0, col=YEL, n=10):
    pts = []
    rr = R(seed, BOIL)
    for i in range(2 * n):
        a = math.pi * i / n
        rad = r if i % 2 == 0 else r * 0.48
        rad *= rr.uniform(0.9, 1.1)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return sk(pts, col, seed, 5, 1.5, step=40)


def puff(cx, cy, r, seed, col='#e9e4da'):
    pts = ell(cx, cy, r, r * 0.85, 16)
    return sk(pts, col, seed, 4, r * 0.06, off=(0, 0))


def check(cx, cy, s, prog, seed=0, col='#2f9e44'):
    pts = [(cx - 40 * s, cy), (cx - 10 * s, cy + 32 * s), (cx + 48 * s, cy - 40 * s)]
    # vẽ dần
    if prog <= 0:
        return ''
    segs = resample(pts, False, 6)
    k = max(2, int(len(segs) * clamp(prog)))
    return line(segs[:k], seed, 14 * s, 1.5, col)


def arrow_down(cx, cy, s, seed=0, col=RED):
    body = [(cx - 22 * s, cy - 90 * s), (cx + 22 * s, cy - 90 * s), (cx + 22 * s, cy), (cx + 55 * s, cy), (cx, cy + 60 * s), (cx - 55 * s, cy), (cx - 22 * s, cy)]
    return sk(body, col, seed, 5, 2, step=30)
