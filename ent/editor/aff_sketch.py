"""aff_sketch: video doc 9:16 phong cach VE TAY ke chuyen san pham (affiliate).
SPEC_JSON = {"branch","dir"} (hoac LOCAL_DIR=... khi test). Trong dir: spec.json + anh canh + product.jpg (tuy chon).
spec.json = {
  "series": "BÍ MẬT ĐỒ VẬT", "ep": "TẬP 1 · CÁI KÉO",
  "voice_urls": [...], "srt_urls": [...],
  "scenes": [{"type": "img|stamp|counter|check|dark|cart|outro", "img": "sc1.png", "cue": "cụm từ đầu câu",
              "slam": "CHỮ TO", "color": "orange|yellow|green|red|white|blue", "sub": "dòng nhỏ dưới chữ to",
              "stamp": "KHÔNG AI CẢ!", "value": 1000000000, "label": "CHIẾC ĐÃ BÁN",
              "items": [["TIÊU ĐỀ", "mô tả"], ...], "fx": "shake|"}],
  "product_img": "product.jpg", "cta": "BẤM GIỎ HÀNG"
}
Khung 1080x1920, chu trong vung an toan x 80-1000, y 260-1462."""
import json, math, os, re, subprocess, sys, urllib.request, wave, random
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aff_sk as sk  # noqa: E402
from aff_sk import (W, H, INK, ORANGE, YEL, RED, STEEL, R, clamp, lerp, ease, eout, eback, esc, ell, rect, sk as skp,
                    line, text, hatch_lines, clipped, star_burst, check, arrow_down, wpath)  # noqa: E402

FPS = 15
ROOT = os.getcwd()
OUT = os.path.join(ROOT, 'out')
COLORS = {'orange': ORANGE, 'yellow': YEL, 'green': '#2f9e44', 'red': RED, 'white': '#ffffff', 'blue': '#3f7fd0'}
DISP = "'Anton', 'Be Vietnam Pro', Montserrat"
LEAD, TAIL = 0.1, 1.4
G = {}  # du lieu dung chung cho tien trinh con


# ---------------- tai du lieu ----------------
def get(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f:
        f.write(r.read())
    return path


try:
    from lexicon import unlex  # phien am ten rieng -> ten goc cho phu de
except Exception:
    unlex = lambda t: t


def parse_srt(txt):
    out = []
    for b in re.split(r'\n\s*\n', txt.strip()):
        ls = [l for l in b.strip().splitlines() if l.strip()]
        for k, l in enumerate(ls):
            m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)', l)
            if m:
                g = list(map(int, m.groups()))
                out.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, unlex(' '.join(ls[k + 1:]))))
                break
    return out


def dur_of(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())


def load_voice(sp):
    srt, parts, off = [], [], 0.0
    urls = sp.get('voice_urls') or ([sp['voice_url']] if sp.get('voice_url') else [])
    surls = sp.get('srt_urls') or ([sp.get('srt_url', '')] if sp.get('voice_url') else [])
    for i, u in enumerate(urls):
        pth = get(u, os.path.join(OUT, 'vp%d.src' % i))
        wav = os.path.join(OUT, 'vp%d.wav' % i)
        from series import voice_part
        d, lead = voice_part(pth, wav, sp, i, ac=1)
        su = surls[i] if i < len(surls) else ''
        if su:
            try:
                for a, b, t in parse_srt(open(get(su, os.path.join(OUT, 'vp%d.srt' % i)), encoding='utf-8').read()):
                    srt.append((max(0, a - lead) + off, max(0, b - lead) + off, t))
            except Exception as e:
                print('srt', i, e)
        parts.append(wav)
        off += d
    lst = os.path.join(OUT, 'vlist.txt')
    open(lst, 'w').write(''.join("file '%s'\n" % p for p in parts))
    voice = os.path.join(OUT, 'voice.wav')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice])
    return voice, dur_of(voice), srt


def _norm(x):
    return re.sub(r'[^\w ]', ' ', x.lower()).split()


def align_starts(scenes, words):
    """Can tung cau kich ban vao chuoi chu SRT (bo chu so vi TTS doc so thanh chu). Tra list moc hoac None."""
    import difflib
    toks, owner = [], []
    for i, sc in enumerate(scenes):
        for w in _norm(sc.get('say') or ''):
            if any(ch.isdigit() for ch in w):
                continue
            toks.append(w)
            owner.append(i)
    if not toks or not words:
        return None
    sw = [w for _, w in words]
    sm = difflib.SequenceMatcher(None, toks, sw, autojunk=False)
    mp = {}
    for a, b, size in sm.get_matching_blocks():
        for q in range(size):
            mp[a + q] = b + q
    out = []
    for i in range(len(scenes)):
        idx = [j for j, o in enumerate(owner) if o == i]
        t = None
        for rank, j in enumerate(idx[:6]):  # chu dau tien cua cau khop duoc
            if j in mp:
                b = mp[j] - rank
                t = words[max(0, b)][0]
                break
        out.append(t)
    return out


def scene_starts(scenes, srt, dur):
    n = len(scenes)
    words = []
    for a, b, t in srt:
        ws = _norm(t)
        for i, w in enumerate(ws):
            words.append((a + (b - a) * i / max(1, len(ws)), w))
    al = align_starts(scenes, words) if words else None
    st = [0.0]
    for k in range(1, n):
        t0 = None
        if al and al[k] is not None and al[k] > st[-1] + 0.8:
            st.append(min(max(al[k] - 0.12, st[-1] + 0.8), dur - 0.8))
            continue
        c = []
        for w in _norm(scenes[k].get('cue') or ''):  # tu khoa moc (khong chu so)
            if any(ch.isdigit() for ch in w):
                break
            c.append(w)
        c = c[:4] if len(c) >= 2 else []
        if c and words:
            say = _norm(scenes[k].get('say') or '')
            off = next((q for q in range(len(say)) if say[q:q + len(c)] == c), 0)  # so chu dung truoc cue
            for i in range(len(words) - len(c) + 1):
                if words[i][0] > st[-1] + 1.0 and [w for _, w in words[i:i + len(c)]] == c:
                    t0 = words[max(0, i - off)][0] if i - off >= 0 else words[i][0] - 0.3 * off
                    break
        if t0 is None:
            fr = float(scenes[k].get('frac', k / n))
            t0 = words[min(len(words) - 1, int(len(words) * fr))][0] if words else dur * fr
            t0 = max(t0, st[-1] + 1.5)
        st.append(min(max(t0 - 0.1, st[-1] + 0.8), dur - 0.8))
    return st


def sub_chunks(srt):
    """gop/tach cum SRT thanh phu de 1-2 dong (<= ~30 ky tu/dong)"""
    out = []
    for a, b, t in srt:
        t = t.strip()
        if not t:
            continue
        def split_even(ws, n):  # chia list tu thanh n phan dai gan bang nhau
            tot = len(' '.join(ws)); out, cur = [], []
            for w in ws:
                if cur and len(out) < n - 1 and len(' '.join(cur + [w])) > tot / n + 3:
                    out.append(cur); cur = [w]
                else:
                    cur.append(w)
            out.append(cur)
            return out
        words = t.split()
        nb = max(1, math.ceil(len(t) / 64))  # moi khoi toi da 2 dong ~30 ky tu
        blocks = []
        for bw in split_even(words, nb):
            s = ' '.join(bw)
            blocks.append([s] if len(s) <= 30 else [' '.join(x) for x in split_even(bw, 2)])
        tot = sum(len(' '.join(x)) for x in blocks) or 1
        c = a
        for bl in blocks:
            e = c + (b - a) * len(' '.join(bl)) / tot
            out.append((c, e, bl))
            c = e
    return out


def script_subs(scenes, starts, dur):
    """phu de tu chinh cau kich ban (giu chu so), chia theo moc canh -> luon khop hinh."""
    out = []
    n = len(scenes)
    for k, sc in enumerate(scenes):
        say = str(sc.get('say') or '').strip()
        if not say:
            return None
        a = starts[k]
        b = starts[k + 1] if k + 1 < n else dur
        out += sub_chunks([(a, b - 0.05, say)])
    return out


def is_key(w, first):
    s = w.strip('.,!?…:;"“”()')
    if not s:
        return False
    if re.search(r'\d', s):
        return True
    if len(s) > 1 and s.isupper():
        return True
    return (not first) and s[0].isupper()


# ---------------- ve ----------------
def band():
    o = skp(rect(70, 268, 940, 104), '#1f3b73', 'band', 5, 1.4, off=(6, 6))
    series, ep = G['series'], G['ep']
    sz = 50 if len(series) <= 18 else 40
    o += text(110, 337, series, sz, YEL, DISP, 400, 'start', ls=1)
    if ep:
        w = min(420, len(ep) * 17 + 40)
        o += skp(rect(1010 - w - 20, 292, w, 56), ORANGE, 'epb', 4, 1.2, off=(0, 0), double=False)
        o += text(1010 - 20 - w / 2, 330, ep, 26 if len(ep) < 20 else 22, '#fff', weight=800)
    return o


def slam(s, t, t0=0.0, y=508, size=96, col=ORANGE, rot=-3, sub=None, first=False):
    if not s or t < t0:
        return ''
    n = len(s)
    if n > 14:
        size = min(size, int(1250 / n))
    u = clamp((t - t0) / 0.2)
    sc = 1.25 - 0.25 * eout(u)
    op = 1.0 if first else clamp((t - t0) / 0.08)
    inner = text(546, y + 6, s, size, INK, DISP, 400, rot=rot, op=op * 0.9)
    inner += text(540, y, s, size, col, DISP, 400, rot=rot, stroke=INK, sw=9, op=op)
    if sub:
        inner += text(540, y + 58, sub, 38, INK, weight=800, rot=rot, stroke='#fff', sw=8, op=op)
    return '<g transform="translate(540 %.1f) scale(%.3f) translate(-540 %.1f)">%s</g>' % (y, sc, -y, inner)


def subtitle(lines, size=46):
    lh = size * 1.28
    n = len(lines)
    w = min(940, max(len(l) for l in lines) * size * 0.58 + 70)
    hbox = n * lh + 34
    y0 = 1462 - hbox
    o = '<path d="%s" fill="#14110f" opacity="0.82"/>' % wpath(rect(540 - w / 2, y0, w, hbox), 'subbox', 2, True, 40)
    first = True
    for i, l in enumerate(lines):
        y = y0 + 17 + lh * (i + 0.78)
        spans = ''
        for k, wd in enumerate(l.split(' ')):
            key = is_key(wd, first)
            first = wd.endswith(('.', '!', '?', '…'))
            spans += '<tspan fill="%s">%s</tspan>' % (YEL if key else '#ffffff', esc(wd + (' ' if k < len(l.split(' ')) - 1 else '')))
        o += '<text xml:space="preserve" x="540" y="%.1f" font-family="\'Be Vietnam Pro\', Montserrat" font-weight="800" font-size="%d" text-anchor="middle">%s</text>' % (y, size, spans)
    return o


def table():
    y = 1340
    o = skp([(-200, y), (1280, y), (1280, 2100), (-200, 2100)], '#e3c79c', 'table', 5, 2, step=60)
    for k in range(5):
        o += line([(-100 + k * 60, y + 60 + k * 90), (1200 - k * 40, y + 70 + k * 90)], ('grain', k), 2.5, 3, '#9b7650', 0.5)
    return o


def photo(name, cx, cy, size, t, seed, dim=0.0, tilt=-1.5, d=5.0, mv=0, pop=True):
    """anh AI dat trong khung ve tay: the giay, bang dinh, net run; may quay 4 kieu (mv) + bat vao (pop)."""
    if not name:
        return ''
    r = random.Random(repr((seed, sk.BOIL)))
    rot = tilt + r.uniform(-0.35, 0.35)
    dx, dy = r.uniform(-1.5, 1.5), r.uniform(-1.5, 1.5)
    u = ease(t / max(1.0, d))
    m = mv % 4
    px = py = 0.0
    if m == 0:      # day vao
        z = 1.0 + 0.14 * u
    elif m == 1:    # lia trai -> phai
        z = 1.18; px = lerp(-0.07, 0.07, u) * size
    elif m == 2:    # keo ra
        z = 1.16 - 0.14 * u
    else:           # lia duoi -> tren
        z = 1.18; py = lerp(0.07, -0.07, u) * size
    sc = 1.0
    if pop and t < 0.35:
        sc = 0.82 + 0.18 * eback(t / 0.35)
        rot += (1 - t / 0.35) * (4 if mv % 2 else -4)
    s2 = size / 2
    o = skp(rect(cx - s2 - 18, cy - s2 - 18, size + 36, size + 36), '#fffaf0', (seed, 'card'), 5, 1.6, off=(10, 10))
    inner = rect(cx - s2, cy - s2, size, size)
    iw = size * z
    img = '<image x="%.1f" y="%.1f" width="%.1f" height="%.1f" href="%s" preserveAspectRatio="xMidYMid slice"/>' % (cx - iw / 2 - px, cy - iw / 2 - py, iw, iw, name)
    if dim:
        img += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#000" opacity="%.2f"/>' % (cx - s2, cy - s2, size, size, dim)
    o += clipped(inner, img)
    o += skp(inner, None, (seed, 'in'), 4, 1.2, double=False)
    for k, (tx, ty, ta) in enumerate([(cx - s2 + 10, cy - s2 - 6, -35), (cx + s2 - 10, cy - s2 - 6, 35)]):
        o += '<rect x="%.1f" y="%.1f" width="120" height="38" fill="#f3e08a" opacity="0.8" transform="rotate(%d %.1f %.1f)"/>' % (tx - 60, ty - 19, ta, tx, ty)
    return '<g transform="translate(%.1f %.1f) rotate(%.2f %.1f %.1f) translate(%.1f %.1f) scale(%.3f) translate(%.1f %.1f)">%s</g>' % (
        dx, dy, rot, cx, cy, cx, cy, sc, -cx, -cy, o)


def mascot(cx, cy, s, t, expr='talk', point=None, seed='bi'):
    """Linh vat 'THAM TU BI': kinh lup co mat, mu tham tu, tay tron lo lung. cx,cy = tam mat kinh."""
    R_ = 92 * s
    bob = 6 * s * math.sin(t * 5)
    cy = cy + bob
    o = ''
    # can kinh (go)
    hx, hy = cx + R_ * 0.62, cy + R_ * 0.62
    handle = [(hx - 16 * s, hy - 6 * s), (hx + 6 * s, hy - 22 * s), (hx + 118 * s, hy + 96 * s), (hx + 96 * s, hy + 116 * s)]
    o += skp(handle, '#9b6a3c', (seed, 'h'), 5, 1.2)
    o += line([(hx + 40 * s, hy + 18 * s), (hx + 98 * s, hy + 76 * s)], (seed, 'hl'), 3, 1, '#c99a66', 0.9)
    # vanh + kinh
    o += skp([ell(cx, cy, R_ + 20 * s, R_ + 20 * s, 26), ell(cx, cy, R_, R_, 24)], ORANGE, (seed, 'rim'), 5, 1.4)
    o += skp(ell(cx, cy, R_, R_, 24), '#dff1fb', (seed, 'gl'), 3, 1.0, off=(0, 0), double=False)
    o += '<path d="M%.1f,%.1f A%.1f,%.1f 0 0 1 %.1f,%.1f" fill="none" stroke="#fff" stroke-width="%.1f" stroke-linecap="round" opacity="0.9"/>' % (
        cx - R_ * 0.62, cy - R_ * 0.25, R_ * 0.7, R_ * 0.7, cx - R_ * 0.2, cy - R_ * 0.66, 9 * s)
    # mu tham tu
    hb = cy - R_ - 14 * s
    o += skp([(cx - 70 * s, hb + 6 * s), (cx + 70 * s, hb + 6 * s), (cx + 58 * s, hb - 10 * s), (cx - 58 * s, hb - 10 * s)], '#6b4b8a', (seed, 'brim'), 4, 1)
    dome = [(cx - 52 * s + 104 * s * i / 10, hb - 8 * s - 58 * s * math.sin(math.pi * i / 10) ** 0.8) for i in range(11)]
    o += skp(dome, '#7d5aa0', (seed, 'dome'), 4.5, 1.2)
    o += skp(rect(cx - 52 * s, hb - 22 * s, 104 * s, 13 * s), YEL, (seed, 'band'), 3, 0.8, off=(0, 0), double=False)
    # mat
    blink = (t % 3.2) < 0.12
    for k2, sd in enumerate((-1, 1)):
        ex, ey = cx + sd * 30 * s, cy - 8 * s
        if blink or (expr == 'wink' and sd == 1) or expr == 'happy':
            o += line([(ex - 15 * s, ey + 4 * s), (ex, ey - 10 * s), (ex + 15 * s, ey + 4 * s)], (seed, 'e', k2), 5 * s + 1, 0.8)
        else:
            o += skp(ell(ex, ey, 18 * s, 22 * s, 12), '#fff', (seed, 'ey', k2), 4 * s + 0.5, 0.8, off=(0, 0), double=False)
            o += '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff"/>' % (ex + 3 * s, ey + 3 * s, 9 * s, INK, ex + 6 * s, ey - 1 * s, 3 * s)
        o += line([(ex - 14 * s, ey - 30 * s), (ex + 14 * s, ey - 33 * s - sd * 2 * s)], (seed, 'b', k2), 5 * s, 0.8)
    # mieng (noi khi talk)
    if expr == 'talk':
        op = abs(math.sin(t * 11))
        o += skp(ell(cx, cy + 34 * s, 13 * s, (4 + 9 * op) * s, 12), '#7a2b22', (seed, 'm'), 3.5 * s + 0.5, 0.6, off=(0, 0), double=False)
    else:
        o += line([(cx - 16 * s, cy + 30 * s), (cx, cy + 40 * s), (cx + 16 * s, cy + 30 * s)], (seed, 'm'), 5 * s, 0.8)
    o += '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#ff8f8f" opacity="0.55"/>' % (cx - 52 * s, cy + 22 * s, 12 * s, 7 * s)
    o += '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#ff8f8f" opacity="0.55"/>' % (cx + 52 * s, cy + 22 * s, 12 * s, 7 * s)
    # tay tron
    hand_l = (cx - R_ - 40 * s, cy + 40 * s + 8 * s * math.sin(t * 6))
    hand_r = point if point else (cx + R_ + 34 * s, cy - 10 * s + 8 * s * math.sin(t * 6 + 1))
    for k2, hp in enumerate((hand_l, hand_r)):
        o += skp(ell(hp[0], hp[1], 20 * s, 20 * s, 12), '#ffd9a8', (seed, 'hd', k2), 4, 0.8)
    o += tag_bi(cx, hb - 92 * s, s)
    return o


def tag_bi(x, y, s):
    t_ = 'THÁM TỬ BÍ'
    w = 30 * s * 0.66 * len(t_) + 40 * s
    o = skp(rect(x - w / 2, y - 22 * s, w, 44 * s), INK, 'tagbi', 3, 1, off=(0, 0), double=False)
    o += text(x, y + 10 * s, t_, 26 * s, '#fff', weight=800)
    return o


def price_tag(x, y, price, t):
    if not price:
        return ''
    sc = eback(clamp((t - 0.5) / 0.3))
    if sc <= 0:
        return ''
    w = max(200, len(price) * 30 + 60)
    g = skp([(x - w / 2, y - 48), (x + w / 2, y - 48), (x + w / 2 + 26, y), (x + w / 2, y + 48), (x - w / 2, y + 48)], RED, 'ptag', 5, 1.4, off=(6, 6))
    g += '<circle cx="%.1f" cy="%.1f" r="9" fill="#fffaf0" stroke="%s" stroke-width="3"/>' % (x - w / 2 + 26, y, INK)
    g += text(x + 14, y + 20, price, 54, '#fff', DISP, 400)
    return '<g transform="translate(%.1f %.1f) rotate(8) scale(%.3f) translate(%.1f %.1f)">%s</g>' % (x, y, sc, -x, -y, g)


def cart(x, y, s, seed):
    o = line([(x - 120 * s, y - 120 * s), (x - 80 * s, y - 120 * s), (x - 40 * s, y + 10 * s), (x + 110 * s, y + 10 * s)], (seed, 'h'), 9, 1.5)
    basket = [(x - 70 * s, y - 95 * s), (x + 140 * s, y - 95 * s), (x + 115 * s, y - 15 * s), (x - 45 * s, y - 15 * s)]
    o += skp(basket, YEL, (seed, 'b'), 6, 1.5, hatch=clipped(basket, hatch_lines(x - 80 * s, y - 100 * s, x + 150 * s, y, 16, seed, 2.5, INK, 0.3)))
    o += skp(ell(x - 25 * s, y + 40 * s, 18 * s, 18 * s, 10), INK, (seed, 'w1'), 3, 0.8)
    o += skp(ell(x + 95 * s, y + 40 * s, 18 * s, 18 * s, 10), INK, (seed, 'w2'), 3, 0.8)
    return o


def card_item(x, y, w, h, h1, h2, prog, seed):
    if prog <= 0:
        return ''
    u = eback(prog * 2.5)
    g = skp(rect(x, y, w, h), '#fffaf0', (seed, 'c'), 5, 1.6, off=(8, 8))
    g += skp(ell(x + 70, y + h / 2, 44, 44, 14), '#d8f5d0', (seed, 'cc'), 4, 1)
    g += check(x + 72, y + h / 2, 0.8, (prog - 0.15) * 3, (seed, 'ck'))
    # QC 26-27/11: dong phu chi ~1% khung -> to len 36-48px (tu co theo do dai, vua 680px ngang the)
    g += text(x + 135, y + h / 2 - 12, h1, 56 if len(h1) <= 16 else 46, INK, DISP, 400, 'start')
    if h2:
        g += text(x + 135, y + h / 2 + 50, h2, max(34, min(48, int(680 / (0.64 * max(1, len(h2)))))), '#3d342c', weight=800, anchor='start')
    cx, cy = x + w / 2, y + h / 2
    return '<g transform="translate(%.1f %.1f) scale(%.3f) translate(%.1f %.1f)">%s</g>' % (cx, cy, u, -cx, -cy, g)


def fmt_num(v):
    try:
        return '{:,}'.format(int(v)).replace(',', '.')
    except Exception:
        return str(v)


def draw_scene(sc, k, t, d):
    """tra ve (world, overlay, shake)"""
    ty = sc.get('type', 'img')
    col = COLORS.get(sc.get('color', 'orange'), ORANGE)
    img = sc.get('img_local')
    o, ov, shake = '', '', 0.0
    first = (k == 0)
    if ty == 'dark':
        o += '<rect x="-400" y="-400" width="1880" height="2720" fill="#1d1a17"/>'
        o += photo(img, 540, 960, 600, t, ('ph', k), dim=0.55, tilt=2, d=d, mv=k)
        ov += slam(sc.get('slam', ''), t, 0.0, 508, 104, col if sc.get('color') else '#ffffff', -4, sc.get('sub'), first)
        if sc.get('fx') == 'shake':
            shake = 10 * math.exp(-t * 9)
        return o, ov, shake
    o += table()
    if ty in ('img', 'stamp', 'outro'):
        if first or ty == 'outro':
            # hook + ket: tranh nho hon, Tham tu Bi dung canh ben phai dan chuyen
            o += photo(img, 455, 930, 620, t, ('ph', k), d=d, mv=k)
            ms = eback(clamp((t - 0.15) / 0.35))
            if ms > 0:
                mx, my = 862, 1085
                o += '<g transform="translate(%.1f %.1f) scale(%.3f) translate(%.1f %.1f)">%s</g>' % (mx, my, ms, -mx, -my, mascot(mx, my, 0.82, t, 'wink' if (ty == 'outro' and t > d * 0.6) else 'talk'))
        else:
            o += photo(img, 540, 965, 730, t, ('ph', k), d=d, mv=k)
        if ty == 'stamp' and sc.get('stamp'):
            ts = d * 0.42
            if t >= ts:
                u = clamp((t - ts) / 0.15)
                scl = 1.6 - 0.6 * u
                st = skp(rect(170, 1060, 740, 150), '#fff', ('stamp', k), 9, 2, off=(0, 0)).replace(INK, RED)
                s = sc['stamp']
                st += text(540, 1165, s, min(100, int(1300 / max(1, len(s)))), RED, DISP, 400)
                o += '<g transform="translate(540 1135) rotate(-6) scale(%.3f) translate(-540 -1135)" opacity="0.95">%s</g>' % (scl, st)
                shake = 12 * math.exp(-(t - ts) * 9)
        ov += slam(sc.get('slam', ''), t, 0.0, 508, 96, col, -3, sc.get('sub') if ty == 'outro' else None, first)
    elif ty == 'counter':
        o += photo(img, 540, 1080, 500, t, ('ph', k), tilt=2, d=d, mv=k)
        v = sc.get('value', 0)
        try:
            n = int(float(v) * eout(t / 0.9))
            s = fmt_num(n) + ('+' if t > 0.9 and sc.get('plus', True) else '')
        except Exception:
            s = str(v)
        o += text(540, 690, s, min(100, int(1500 / max(1, len(s)))), col, DISP, 400, stroke=INK, sw=7)
        o += text(540, 755, sc.get('label', ''), 42, INK, weight=800)
        ov += slam(sc.get('slam', ''), t, 0.0, 508, 96, ORANGE, -3, None, first)
    elif ty == 'check':
        items = (sc.get('items') or [])[:3]
        n = max(1, len(items))
        hh = 190
        gap = (650 - n * hh) / max(1, n - 1) if n > 1 else 0
        step = min(0.5, d * 0.55 / n)  # QC: hien du 3 the trong ~1,5 s, khong de khung trong 1 the
        y0 = 600 if n > 1 else 860
        for i, it in enumerate(items):
            h1 = it[0] if isinstance(it, (list, tuple)) else str(it)
            h2 = it[1] if isinstance(it, (list, tuple)) and len(it) > 1 else ''
            o += card_item(130, y0 + i * (hh + gap), 820, hh, h1, h2, (t - 0.2 - i * step) / 0.7, ('ci', k, i))
        ov += slam(sc.get('slam', ''), t, 0.0, 508, 96, col, -3, None, first)
    elif ty == 'cart':
        pimg = G.get('product_local') or img
        o += photo(pimg, 500, 880, 600, t, ('ph', k), tilt=-2, d=d, mv=0)
        o += price_tag(700, 640, G.get('price', ''), t)
        if t > 0.4:
            o += cart(250, 1290, 0.9, ('cart', k))
            o += arrow_down(560, 1270 + 16 * math.sin(t * 8), 0.9, ('ar', k))
            o += mascot(880, 1130, 0.62, t, 'talk', point=(650, 1235 + 16 * math.sin(t * 8)))
        ov += slam(sc.get('slam') or G.get('cta') or 'BẤM GIỎ HÀNG', t, 0.0, 508, 104, col, -3, None, first)
    return o, ov, shake


def split2(s):
    """chia tieu de thanh toi da 2 dong can bang"""
    w = s.split()
    if len(s) <= 11 or len(w) < 2:
        return [s]
    best = min(range(1, len(w)), key=lambda i: abs(len(' '.join(w[:i])) - len(' '.join(w[i:]))))
    return [' '.join(w[:best]), ' '.join(w[best:])]


def cover_svg():
    """27/11: KHUNG BIA (0,3 s dau + out/cover.png) - Facebook lay khung dau lam anh xem truoc reel."""
    sk.BOIL = 0
    sk._clip_id[0] = 0
    sc0 = G['scenes'][0]
    title = str(G.get('cover_title') or sc0.get('slam') or G.get('ep') or '').upper()
    lines = split2(title)
    o = table()
    pimg = G.get('product_local') or sc0.get('img_local')
    o += photo(pimg, 470, 1030, 600, 2.0, ('cv', 'p'), tilt=-3, d=5, mv=0, pop=False)
    o += mascot(860, 1180, 0.78, 0.4, 'wink', point=(700, 1060))
    ov = ''
    y = 520 if len(lines) == 2 else 590
    for i, l in enumerate(lines):
        size = min(150, int(1650 / max(1, len(l))))
        yy = y + i * (size * 1.02)
        ov += text(548, yy + 8, l, size, INK, DISP, 400, rot=-3, op=0.9)
        ov += text(540, yy, l, size, ORANGE if i == 0 else YEL, DISP, 400, rot=-3, stroke=INK, sw=11)
    sub = str(G.get('cover_sub') or 'XEM ĐẾN CUỐI BẠN SẼ BẤT NGỜ!')
    w = min(900, len(sub) * 26 + 80)
    ov += skp(rect(540 - w / 2, 1378, w, 76), RED, 'cvsub', 5, 1.2, off=(6, 6))
    ov += text(540, 1428, sub, 38 if len(sub) <= 30 else 32, '#fff', weight=800)
    s = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H)
    s += '<image x="0" y="0" width="%d" height="%d" href="paper.png"/>' % (W, H)
    s += o + G['band'] + ov + '</svg>'
    return s


def frame_svg(gi):
    t = gi / FPS
    if t < LEAD and G.get('cover', True):
        return G['cover_svg']
    tv = t - LEAD
    sk.BOIL = int(gi * 8 / FPS)
    sk._clip_id[0] = 0
    st = G['starts']
    scenes = G['scenes']
    k = max([i for i in range(len(scenes)) if st[i] <= max(0.0, tv)] or [0])
    e = st[k + 1] if k + 1 < len(scenes) else G['dur'] + TAIL
    ts = max(0.0, tv - st[k]) if k > 0 else t
    world, ov, shake = draw_scene(scenes[k], k, ts, e - st[k])
    r = random.Random(gi)
    sx, sy = r.uniform(-1, 1) * shake, r.uniform(-1, 1) * shake
    s = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H)
    s += '<image x="0" y="0" width="%d" height="%d" href="paper.png"/>' % (W, H)
    s += '<g transform="translate(%.1f %.1f)">%s</g>' % (sx, sy, world)
    s += G['band'] + ov
    cur = next((c for c in G['subs'] if c[0] - 0.05 <= tv < c[1] + 0.12), None)
    if cur and tv < G['dur']:
        s += subtitle(cur[2])
    s += '</svg>'
    return s


def render_one(gi):
    svg = frame_svg(gi)
    p = os.path.join(G['wd'], 'f%d.svg' % (os.getpid()))
    with open(p, 'w', encoding='utf-8') as f:
        f.write(svg)
    return subprocess.run(['rsvg-convert', '-f', 'png', p], capture_output=True, check=True).stdout


def init_worker(g):
    G.update(g)


# ---------------- am thanh ----------------
SR = 44100
rng = np.random.default_rng(7)


def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def _tone(f, d, r=0.2):
    n = int(d * SR)
    return np.sin(2 * np.pi * f * np.arange(n) / SR) * _env(n, 0.003, r)


def _noise(d):
    return rng.normal(0, 1, int(d * SR))


def _lp(x, k):
    return np.convolve(x, np.ones(k) / k, 'same')


def sfx_bank():
    def whoosh():
        n = _noise(0.35); x = n - _lp(n, 6); tt = np.linspace(0, 1, len(x)); return x * np.sin(np.pi * tt) ** 2 * 0.35
    def pop():
        n = int(0.12 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * (900 - 5000 * tt) * tt) * _env(n, 0.001, 0.04)
    def thud():
        n = int(0.5 * SR); tt = np.arange(n) / SR
        return np.sin(2 * np.pi * (120 - 80 * tt) * tt) * _env(n, 0.002, 0.12) + _lp(_noise(0.5), 30) * _env(n, 0.001, 0.05) * 2
    def ding():
        return _tone(1568, 0.9, 0.3) * 0.5 + _tone(2093, 0.9, 0.25) * 0.35 + _tone(3136, 0.9, 0.1) * 0.15
    def coin():
        return np.concatenate([_tone(1976, 0.08, 0.05), _tone(2637, 0.4, 0.15)]) * 0.5
    def sting():
        o = np.zeros(int(1.4 * SR))
        for f in (110, 116.5, 164.8):
            x = np.sign(np.sin(2 * np.pi * f * np.arange(len(o)) / SR)) * 0.5 * _env(len(o), 0.003, 0.6)
            o += x * 0.25
        return o
    return dict(whoosh=whoosh(), pop=pop(), thud=thud(), ding=ding(), coin=coin(), sting=sting())


def pluck(f, d=0.45):
    N = int(SR / f); buf = rng.uniform(-1, 1, N); n = int(d * SR); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N]) * 0.996
    return out


def music(D):
    notes = {'C': 261.6, 'D': 293.7, 'E': 329.6, 'F': 349.2, 'G': 392.0, 'A': 440.0, 'B': 493.9}
    cache = {}
    def pl(f):
        k = round(f, 1)
        if k not in cache:
            cache[k] = pluck(f)
        return cache[k]
    beat = 60 / 112
    prog = ['C', 'A', 'F', 'G']
    mel = ['E', 'G', 'C', 'G', 'A', 'C', 'E', 'C', 'F', 'A', 'C', 'A', 'G', 'B', 'D', 'B']
    mus = np.zeros(int((D + 1) * SR))
    t, i = 0.0, 0
    while t < D:
        j = int(t * SR)
        if i % 2 == 0:
            x = pl(notes[prog[(i // 8) % 4]] / 2); mus[j:j + len(x)] += x[:len(mus) - j] * 0.6
        f = notes[mel[i % 16]] * (2 if i % 4 == 3 else 1)
        x = pl(f); mus[j:j + len(x)] += x[:len(mus) - j] * 0.45
        t += beat / 2; i += 1
    return mus


def build_audio(voice, D, starts, scenes):
    bank = sfx_bank()
    n = int((D + 1) * SR)
    sfx = np.zeros(n)
    def put(t, x, v):
        i = int(max(0, t) * SR); x = x[:n - i]; sfx[i:i + len(x)] += x * v
    for k, sc in enumerate(scenes):
        t0 = LEAD + starts[k]
        put(t0 - 0.1, bank['whoosh'], 0.8)
        ty = sc.get('type')
        nxt = LEAD + (starts[k + 1] if k + 1 < len(scenes) else D - LEAD)
        if ty == 'stamp':
            put(t0 + (nxt - t0) * 0.42, bank['thud'], 1.0)
        elif ty == 'counter':
            for q in range(8):
                put(t0 + q * 0.16, bank['coin'], 0.5)
            put(t0 + 1.35, bank['ding'], 0.6)
        elif ty == 'check':
            m = len(sc.get('items') or [])
            for q in range(m):
                put(t0 + 0.6 + q * (nxt - t0) * 0.8 / max(1, m), bank['ding'], 0.6)
        elif ty == 'dark':
            put(t0, bank['sting'], 0.7)
        elif ty == 'cart':
            put(t0 + 0.4, bank['pop'], 0.8)
        if k == 0:
            put(LEAD, bank['thud'], 0.8)
    mus = music(D)[:n]
    tt = np.arange(n) / SR
    for k, sc in enumerate(scenes):
        if sc.get('type') == 'dark':
            a = LEAD + starts[k]
            b = LEAD + (starts[k + 1] if k + 1 < len(scenes) else D)
            mus[(tt > a) & (tt < b)] *= 0.3
    mus *= np.clip((D - tt) / 0.8, 0, 1)
    bed = sfx * 0.35 + mus * 0.12
    bed /= max(1e-6, np.max(np.abs(bed))) / 0.7
    p = os.path.join(OUT, 'bed.wav')
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(bed, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return p


# ---------------- giay ----------------
def make_paper(path):
    from PIL import Image
    r = np.random.default_rng(3)
    base = np.array([246, 238, 219], np.float32)
    n = r.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    low = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255 - 0.5
    fine = r.normal(0, 1, (H, W)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    shade = 1 - 0.07 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    out = base[None, None, :] * shade[..., None] + (low * 14 + fine * 4)[..., None]
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(path)


def prep_img(src, dst, size=760, fit=False):
    from PIL import Image
    im = Image.open(src).convert('RGB')
    w, h = im.size
    if fit:  # anh san pham that: giu nguyen ca chiec, dat giua nen trang (khong cat)
        sc = (size * 0.92) / max(w, h)
        im = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS)
        bg = Image.new('RGB', (size, size), (255, 255, 255))
        bg.paste(im, ((size - im.size[0]) // 2, (size - im.size[1]) // 2))
        bg.save(dst, quality=92)
        return os.path.basename(dst)
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((size, size), Image.LANCZOS)
    im.save(dst, quality=90)
    return os.path.basename(dst)


def main():
    os.makedirs(OUT, exist_ok=True)
    if os.environ.get('LOCAL_DIR'):
        D_ = os.environ['LOCAL_DIR']
    else:
        inp = json.loads(os.environ['SPEC_JSON'])
        br, dd = inp['branch'], inp['dir'].strip('/')
        subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
        __import__('gitlay').lay(dd)
        D_ = os.path.join(ROOT, dd)
    sp = json.load(open(os.path.join(D_, 'spec.json'), encoding='utf-8'))
    wd = os.path.join(OUT, 'svg')
    os.makedirs(wd, exist_ok=True)
    make_paper(os.path.join(wd, 'paper.png'))
    scenes = [dict(s) for s in sp['scenes']]
    last_img = None
    for i, s in enumerate(scenes):
        src = os.path.join(D_, s.get('img') or '')
        if s.get('img') and os.path.exists(src):
            last_img = prep_img(src, os.path.join(wd, 'i%d.jpg' % i))
        s['img_local'] = last_img  # canh thieu anh -> dung anh canh truoc
    if last_img is None:
        sys.exit('khong co anh canh')
    for s in scenes:  # canh dau thieu anh -> lay anh dau tien co
        if not s['img_local']:
            s['img_local'] = next(x['img_local'] for x in scenes if x['img_local'])
    prod = None
    if sp.get('product_img') and os.path.exists(os.path.join(D_, sp['product_img'])):
        prod = prep_img(os.path.join(D_, sp['product_img']), os.path.join(wd, 'product.jpg'), fit=True)
    voice, dur, srt = load_voice(sp)
    starts = scene_starts(scenes, srt, dur)
    print('dur', round(dur, 2), 'starts', [round(x, 1) for x in starts])
    D = dur + LEAD + TAIL
    g = dict(series=str(sp.get('series', '')).upper(), ep=str(sp.get('ep', '')).upper(), scenes=scenes, starts=starts,
             dur=dur, subs=script_subs(scenes, starts, dur) or sub_chunks(srt), product_local=prod, cta=sp.get('cta'), wd=wd, price=str(sp.get('price') or '')[:14])
    G.update(g)
    G['band'] = band()
    G['cover_title'], G['cover_sub'], G['cover'] = sp.get('cover_title'), sp.get('cover_sub'), sp.get('cover', True)
    G['cover_svg'] = cover_svg()
    cp = os.path.join(wd, 'cover.svg')
    with open(cp, 'w', encoding='utf-8') as f:
        f.write(G['cover_svg'])
    subprocess.run(['rsvg-convert', '-f', 'png', '-o', os.path.join(OUT, 'cover.png'), cp], check=False)
    nfr = int(D * FPS)
    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'png', '-i', '-',
                          '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', '30', raw], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get('NPROC', '4')), initializer=init_worker, initargs=(dict(G),)) as pool:
        for png in pool.imap(render_one, range(nfr), chunksize=6):
            p.stdin.write(png)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit('ffmpeg video loi')
    bed = build_audio(voice, D, starts, scenes)
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    ms = int(LEAD * 1000)
    fc = '[1:a]adelay=%d|%d,apad[v];[2:a]volume=0.45[b];[v][b]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]' % (ms, ms)
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', voice, '-i', bed, '-filter_complex', fc, '-map', '0:v', '-map', '[a]',
                           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-t', '%.2f' % D, '-movflags', '+faststart', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    print('ok', round(D, 2))


if __name__ == '__main__':
    main()
