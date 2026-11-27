#!/usr/bin/env python3
"""Whiteboard (tay ve) explainer reel 1080x1920.

SPEC (env SPEC_JSON or argv[1] path):
{
  "dir": "assets folder", "tag": "GOC AI CHO SHOP #01", "hand": "hand1.png",
  "font": "PatrickHand.ttf", "music": "music.mp3" (optional), "gap": 0.22,
  "lines": [{"wav": "l0.wav", "caps": ["chunk *keyword*", ...]}],
  "sections": [{"title": "...", "lines": [0,1,2],
                 "sketches": [{"img": "s1a.png", "line": 0, "label": "..."}]}]
}
"""
import json, os, subprocess, sys, wave, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
PAPER = np.array([243, 239, 225], np.float32)
INK = np.array([38, 36, 34], np.float32)
random.seed(7); np.random.seed(7)

spec = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.loads(os.environ['SPEC_JSON'])
D = spec.get('dir', '.')
OUT = spec.get('out', 'out/out.mp4')
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
TMP = spec.get('tmp', '/tmp/wb'); os.makedirs(TMP, exist_ok=True)
P = lambda f: f if os.path.isabs(f) else os.path.join(D, f)
FONT = P(spec.get('font', 'PatrickHand.ttf'))
def font(sz): return ImageFont.truetype(FONT, sz)

# ---------------- audio: voice timeline ----------------
def read_wav(p):
    w = wave.open(p); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: x = x.reshape(-1, 2).mean(1)
    return x, sr
def trim(x, sr, th=0.012):
    a = np.abs(x); idx = np.where(a > th)[0]
    if not len(idx): return x
    s = max(0, idx[0] - int(0.04 * sr)); e = min(len(x), idx[-1] + int(0.08 * sr))
    return x[s:e]
GAP = float(spec.get('gap', 0.22))
voice = []; marks = []; t = 0.35; SR = 24000
def speed_wav(wp):
    sp_ = float(spec.get('voice_speed', 1.0))
    if abs(sp_ - 1.0) <= 0.01: return wp
    fp = os.path.join(TMP, 'sp_' + os.path.basename(wp))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wp, '-filter:a', 'atempo=%.3f' % sp_, '-ac', '1', fp], check=True)
    return fp
if spec.get('voice'):
    # 1 file giong cho ca kich ban -> tach cau theo khoang lang gan vi tri du kien nhat
    x, sr = read_wav(speed_wav(P(spec['voice']))); SR = sr; x = trim(x, sr)
    hop = max(1, int(sr * 0.02)); n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    th = max(0.006, float(np.percentile(e, 90)) * 0.07); sil = e < th
    gaps = []; i = 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]: j += 1
            if (j - i) * 0.02 >= 0.16: gaps.append((i * 0.02, j * 0.02))
            i = j
        else: i += 1
    L = spec['lines']; w = [max(4, len(str(l.get('text') or ' '.join(l.get('caps') or [])))) for l in L]
    dur = len(x) / sr; cum = np.cumsum(w)[:-1] / sum(w) * dur
    bounds = []; last = 0.0
    for c in cum:
        cand = [g for g in gaps if (g[0] + g[1]) / 2 > last + 0.4]
        g = min(cand, key=lambda g: abs((g[0] + g[1]) / 2 - c)) if cand else None
        if g is None or abs((g[0] + g[1]) / 2 - c) > max(1.6, dur * 0.06): g = (c, c)
        bounds.append(g); last = (g[0] + g[1]) / 2
    st = 0.0
    for k in range(len(L)):
        en = bounds[k][0] if k < len(bounds) else dur
        marks.append((t + st, t + en)); st = bounds[k][1] if k < len(bounds) else dur
    voice.append((t, x)); t = t + dur + 0.3
for ln in ([] if spec.get('voice') else spec['lines']):
    x, sr = read_wav(speed_wav(P(ln['wav']))); SR = sr; x = trim(x, sr)
    marks.append((t, t + len(x) / sr)); voice.append((t, x)); t += len(x) / sr + GAP
TOTAL = t + 1.4
vbuf = np.zeros(int(TOTAL * SR) + SR, np.float32)
for st, x in voice: i = int(st * SR); vbuf[i:i + len(x)] += x

# ---------------- graphics helpers ----------------
def paper_bg():
    n = np.random.normal(0, 2.2, (H // 4, W // 4)).astype(np.float32)
    n = np.array(Image.fromarray(n).resize((W, H), Image.BICUBIC))
    yy, xx = np.mgrid[0:H, 0:W]; v = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    bg = PAPER[None, None, :] + n[..., None] - (v * 10)[..., None]
    return np.clip(bg, 0, 255)
BG = paper_bg()

def fx(s):
    return str(s).replace('→', '=>').replace('↑', ' tăng').replace('↓', ' giảm').replace('–', '-')

def text_size(f, s):
    b = f.getbbox(s); return b[2] - b[0], b[3] - b[1], b[1]

def load_sketch(path, box):
    x, y, w, h = box
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    # paper colour of the AI image = median of border pixels
    border = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    pc = np.median(border, 0)
    # crop to content
    dist = np.abs(a - pc).max(2)
    ys, xs = np.where(dist > 40)
    if len(xs):
        m = 14; x0, x1 = max(0, xs.min() - m), min(a.shape[1], xs.max() + m); y0, y1 = max(0, ys.min() - m), min(a.shape[0], ys.max() + m)
        im = im.crop((x0, y0, x1, y1))
    s = min(w / im.width, h / im.height)
    nw, nh = max(1, int(im.width * s)), max(1, int(im.height * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    dist = np.abs(a - pc).max(2)
    alpha = np.clip((dist - 14) / 36, 0, 1)
    gray = a.mean(2)
    ink = (gray < 115) & (alpha > 0.5)
    ox, oy = x + (w - nw) // 2, y + (h - nh) // 2
    return dict(rgb=a, alpha=alpha, ink=ink, x=ox, y=oy, w=nw, h=nh)

def stroke_order(ink, cell=14):
    h, w = ink.shape
    gh, gw = (h + cell - 1) // cell, (w + cell - 1) // cell
    pad = np.zeros((gh * cell, gw * cell), bool); pad[:h, :w] = ink
    cnt = pad.reshape(gh, cell, gw, cell).sum((1, 3))
    cells = np.argwhere(cnt > 2)
    if not len(cells): return np.full(ink.shape, 0, np.int32), np.zeros((0, 2)), 0
    pts = cells.astype(np.float32)
    n = len(pts); used = np.zeros(n, bool); order = []
    cur = np.argmin(pts[:, 0] * 0.6 + pts[:, 1])
    for _ in range(n):
        used[cur] = True; order.append(cur)
        d = np.abs(pts[:, 0] - pts[cur, 0]) + np.abs(pts[:, 1] - pts[cur, 1]); d[used] = 1e9
        nx = int(np.argmin(d))
        if d[nx] >= 1e9: break
        cur = nx
    rank = np.full((gh, gw), 10 ** 9, np.int32)
    for r, c in enumerate(order): rank[cells[c][0], cells[c][1]] = r
    full = np.kron(rank, np.ones((cell, cell), np.int32))[:h, :w]
    centers = np.array([[(cells[c][1] + 0.5) * cell, (cells[c][0] + 0.5) * cell] for c in order], np.float32)
    return full, centers, len(order)


def render_board(bd, path, size=1000):
    """Bang gia ve tay: nen kem, net muc den hoi run, so lieu chinh xac."""
    rnd = random.Random(hash(bd.get('title', '')) & 0xffff)
    rows = [list(r) for r in bd.get('rows') or []]; head = bd.get('head')
    ncol = max([len(r) for r in rows] + [len(head) if head else 0])
    im = Image.new('RGB', (size, size), (242, 238, 223)); d = ImageDraw.Draw(im)
    ft = font(78); fh = font(52); fr = font(60); fn = font(40)
    def wline(x0, y0, x1, y1, w=6):
        n = 12; pts = []
        for i in range(n + 1):
            t = i / n; pts.append((x0 + (x1 - x0) * t + rnd.uniform(-2.5, 2.5), y0 + (y1 - y0) * t + rnd.uniform(-2.5, 2.5)))
        d.line(pts, fill=(30, 28, 26), width=w, joint='curve')
    y = 60
    ttl = fx(bd.get('title', '')); tw = d.textlength(ttl, font=ft); d.text(((size - tw) / 2, y), ttl, font=ft, fill=(30, 28, 26))
    y += 110; wline(140, y, size - 140, y, 5); y += 40
    allr = ([head] if head else []) + rows
    rh = 118; top = y; left, right = 60, size - 60
    colw = [0.46, 0.27, 0.27] if ncol == 3 else ([0.5, 0.5] if ncol == 2 else [1.0])
    xs = [left]; 
    for c in colw: xs.append(xs[-1] + (right - left) * c)
    # khung
    bottom = top + rh * len(allr)
    wline(left, top, right, top); wline(left, bottom, right, bottom); wline(left, top, left, bottom); wline(right, top, right, bottom)
    for i in range(1, len(allr)): wline(left, top + rh * i, right, top + rh * i, 4)
    for x in xs[1:-1]: wline(x, top, x, bottom, 4)
    for ri, r in enumerate(allr):
        yy = top + rh * ri
        is_head = head is not None and ri == 0
        if is_head:
            d.rectangle((left + 6, yy + 6, right - 6, yy + rh - 6), fill=(250, 226, 140))
        for ci, cell in enumerate(r):
            f = fh if is_head else (fr if ci else fh)
            cell = fx(cell); w_ = d.textlength(cell, font=f)
            cx = xs[ci] + ((xs[ci + 1] - xs[ci]) - w_) / 2 if ci else xs[ci] + 24
            col = (30, 28, 26)
            if not is_head and ncol == 3 and ci == 2: col = (190, 45, 40)
            if not is_head and ncol == 3 and ci == 1: col = (40, 120, 60)
            d.text((cx, yy + (rh - f.size) / 2 - 6), cell, font=f, fill=col)
    if bd.get('note'):
        nw = d.textlength(bd['note'], font=fn); d.text(((size - nw) / 2, bottom + 40), bd['note'], font=fn, fill=(70, 66, 60))
    im.save(path)

# ---------------- hand ----------------
def load_hand(path, target_w=560):
    im = Image.open(path).convert('RGB'); a = np.asarray(im).astype(np.int16)
    bgc = np.median(np.concatenate([a[:5].reshape(-1, 3), a[:, -5:].reshape(-1, 3)]), 0)
    diff = np.abs(a - bgc).max(2) > 28
    # flood fill background from border
    from collections import deque
    h, w = diff.shape; bgm = np.zeros((h, w), bool); q = deque()
    for xx in range(w):
        for yy in (0, h - 1): q.append((yy, xx))
    for yy in range(h):
        for xx in (0, w - 1): q.append((yy, xx))
    while q:
        yy, xx = q.popleft()
        if yy < 0 or xx < 0 or yy >= h or xx >= w or bgm[yy, xx] or diff[yy, xx]: continue
        bgm[yy, xx] = True; q.extend(((yy + 1, xx), (yy - 1, xx), (yy, xx + 1), (yy, xx - 1)))
    al = (~bgm).astype(np.uint8) * 255
    rgba = Image.fromarray(np.dstack([a.astype(np.uint8), al]), 'RGBA')
    rgba = rgba.crop(rgba.getbbox())
    alf = Image.fromarray(np.asarray(rgba)[..., 3]).filter(ImageFilter.GaussianBlur(1.2))
    rgba.putalpha(alf)
    s = target_w / rgba.width; rgba = rgba.resize((target_w, int(rgba.height * s)), Image.LANCZOS)
    A = np.asarray(rgba)[..., 3] > 128
    ys, xs = np.where(A); k = np.argmin(xs + 0.35 * ys)  # left-most opaque pixel = pen tip
    tip = (int(xs[k]), int(ys[k]))
    # soft shadow
    sh = Image.new('RGBA', rgba.size, (0, 0, 0, 0)); sh.putalpha(Image.fromarray((np.asarray(rgba)[..., 3] * 0.22).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)))
    return np.asarray(rgba).astype(np.float32), np.asarray(sh).astype(np.float32), tip
HAND, HSH, TIP = load_hand(P(spec.get('hand', 'hand1.png')))

def paste_rgba(frame, rgba, x, y):
    h, w = rgba.shape[:2]
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1: return
    sub = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3:4] / 255
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a

def draw_hand(frame, px, py):
    paste_rgba(frame, HSH, int(px - TIP[0] + 18), int(py - TIP[1] + 22))
    paste_rgba(frame, HAND, int(px - TIP[0]), int(py - TIP[1]))

# ---------------- text layers (rgba arrays) ----------------
def text_layer(s, sz, color=(38, 36, 34), maxw=1000):
    s = fx(s)
    f = font(sz); tw, th, off = text_size(f, s)
    im = Image.new('RGBA', (tw + 20, th + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((10, 10 - off), s, font=f, fill=color + (255,))
    a = np.asarray(im).astype(np.float32)
    if a.shape[1] > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS); a = np.asarray(im).astype(np.float32)
    return a

def tag_layer(s):
    f = font(34); tw, th, off = text_size(f, s)
    im = Image.new('RGBA', (tw + 44, th + 26), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, tw + 41, th + 23), radius=(th + 20) // 2, outline=(200, 60, 55, 255), width=3)
    d.text((22, 13 - off), s, font=f, fill=(200, 60, 55, 255))
    return np.asarray(im).astype(np.float32)

def label_layer(s):
    s = fx(s)
    f = font(40); tw, th, off = text_size(f, s)
    im = Image.new('RGBA', (tw + 40, th + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, tw + 36, th + 26), radius=10, fill=(255, 240, 160, 255), outline=(40, 38, 36, 255), width=3)
    d.text((20, 15 - off), s, font=f, fill=(40, 38, 36, 255))
    return np.asarray(im).astype(np.float32)

def caption_layer(s, sz=62, maxw=900):
    s = fx(s)
    # *kw* -> yellow highlight ; wraps to max 2 lines
    f = font(sz)
    toks = []
    for i, part in enumerate(s.split('*')):
        for wd in part.split():
            toks.append((wd, i % 2 == 1))
    sp = text_size(f, ' ')[0] or sz // 4
    lines = [[]]; cw = 0
    for wd, hl in toks:
        ww = text_size(f, wd)[0]
        if lines[-1] and cw + sp + ww > maxw: lines.append([]); cw = 0
        lines[-1].append((wd, hl, ww)); cw += (sp if cw else 0) + ww
    lh = int(sz * 1.25)
    im = Image.new('RGBA', (maxw + 40, lh * len(lines) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    asc = f.getbbox('Ấg')[1]
    for li, ln in enumerate(lines):
        tw = sum(x[2] for x in ln) + sp * (len(ln) - 1); x = (maxw + 40 - tw) // 2; y = 12 + li * lh
        # merge consecutive highlighted words into one box
        j = 0
        while j < len(ln):
            if ln[j][1]:
                k = j; x0 = x + sum(z[2] + sp for z in ln[:j])
                while k + 1 < len(ln) and ln[k + 1][1]: k += 1
                x1 = x0 + sum(z[2] for z in ln[j:k + 1]) + sp * (k - j)
                d.rounded_rectangle((x0 - 8, y + 4, x1 + 8, y + lh - 2), radius=8, fill=(255, 226, 90, 255))
                j = k + 1
            else: j += 1
        cx = x
        for wd, hl, ww in ln:
            d.text((cx, y - asc + int(sz * 0.18)), wd, font=f, fill=(34, 32, 30, 255)); cx += ww + sp
    return np.asarray(im).astype(np.float32)

# ---------------- layout ----------------
TOP = 330; BOT = 1360
def boxes(n):
    if n == 1: return [(140, TOP + 40, 800, 800)]
    if n == 2: return [(40, TOP, 600, 560), (440, TOP + 500, 600, 520)]
    if n == 3: return [(40, TOP, 490, 490), (550, TOP, 490, 490), (250, TOP + 520, 580, 500)]
    return [(40, TOP, 490, 490), (550, TOP, 490, 490), (40, TOP + 520, 490, 490), (550, TOP + 520, 490, 490)]

# ---------------- build timeline ----------------
events = []  # list of dicts
SECTIONS = spec['sections']
sec_times = []
for si, sec in enumerate(SECTIONS):
    st = marks[sec['lines'][0]][0] - (0.25 if si else 0.35)
    en = marks[sec['lines'][-1]][1] + GAP
    if si == len(SECTIONS) - 1: en = TOTAL
    sec_times.append((max(0, st), en))
for si in range(len(SECTIONS) - 1):  # make contiguous
    sec_times[si] = (sec_times[si][0], sec_times[si + 1][0])
sec_times[0] = (0, sec_times[0][1])

# HOOK: dong chu to hien ngay frame 0 den het cau dau (giu chan 3 giay dau)
HOOK_TXT = str(spec.get('hook') or '').strip()
def hook_layer(s, sz=100, maxw=920):
    s = fx(s); f = font(sz); words = s.split(); lines = []; cur = ''
    for wd in words:
        tt = (cur + ' ' + wd).strip()
        if text_size(f, tt)[0] <= maxw: cur = tt
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    lines = lines[:3]; lh = int(sz * 1.18)
    wmax = max(text_size(f, l)[0] for l in lines) + 80
    im = Image.new('RGBA', (wmax + 20, lh * len(lines) + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, wmax + 10, lh * len(lines) + 60), radius=26, fill=(206, 52, 46, 255), outline=(38, 36, 34, 255), width=5)
    asc = f.getbbox('Ấg')[1]
    for i, ln in enumerate(lines):
        tw = text_size(f, ln)[0]; d.text(((wmax + 20 - tw) // 2, 34 + i * lh - asc + int(sz * 0.12)), ln, font=f, fill=(255, 246, 200, 255))
    im = im.rotate(-2.5, resample=Image.BICUBIC, expand=True)
    return np.asarray(im).astype(np.float32)
HOOK = hook_layer(HOOK_TXT) if HOOK_TXT else None
HOOK_END = (marks[0][1] + 0.15) if HOOK is not None else 0.0

prepared = []
for si, sec in enumerate(SECTIONS):
    kinds = ['board' if sk.get('board') else 'img' for sk in sec['sketches']]
    if 'board' in kinds:
        ib = [i for i, k in enumerate(kinds) if k == 'img']; bb = [i for i, k in enumerate(kinds) if k == 'board']
        bxs = [None] * len(kinds); H_ = BOT - TOP
        if ib:
            top_h = 470 if len(ib) == 1 else 440
            wi = 1000 // len(ib)
            for j, i in enumerate(ib): bxs[i] = (40 + j * wi + (wi - min(wi, top_h)) // 2, TOP, min(wi, top_h), top_h)
            y0 = TOP + top_h + 30; hb = (BOT - y0) // len(bb)
        else:
            y0 = TOP + 20; hb = (H_ - 20) // len(bb)
        for j, i in enumerate(bb): bxs[i] = (40, y0 + j * hb, 1000, hb - 10)
    else:
        bxs = boxes(len(sec['sketches']))
    ss = []
    s0, s1 = sec_times[si]
    title_t = (-1.0, -0.5) if si == 0 else (s0 + 0.05, s0 + 0.75)  # canh dau: tieu de hien ngay
    starts = []
    for k, sk in enumerate(sec['sketches']):
        lt = marks[sk.get('line', sec['lines'][0])][0]
        starts.append(max(lt, title_t[1] if k == 0 else 0, HOOK_END if si == 0 else 0))
    for k, sk in enumerate(sec['sketches']):
        if sk.get('board'):
            bp = os.path.join(TMP, 'board_%d_%d.png' % (si, k)); render_board(sk['board'], bp); d = load_sketch(bp, bxs[k])
        else:
            d = load_sketch(P(sk['img']), bxs[k])
        rank, centers, n = stroke_order(d['ink'])
        st = max(starts[k], (ss[-1]['end'] + 0.1) if ss else 0)
        nxt = starts[k + 1] if k + 1 < len(starts) else s1 - 0.4
        dur = float(np.clip(nxt - st - 0.15, 1.2, 2.6))
        d.update(rank=rank, centers=centers, n=n, start=st, draw=dur * 0.78, fill=dur * 0.22, end=st + dur, label=sk.get('label'))
        if d['label']:
            L = label_layer(d['label'])
            lx = int(np.clip(d['x'] - 10, 20, W - L.shape[1] - 20)); ly = int(max(TOP - 30, d['y'] - L.shape[0] // 2))
            d['lab'] = (L, lx, ly)
        ss.append(d)
    prepared.append(dict(sketches=ss, title=text_layer(sec['title'], 84, maxw=1000), t0=s0, t1=s1, title_t=title_t))

TAG = tag_layer(spec.get('tag', ''))
caps = []  # (t0, t1, layer)
for li, ln in enumerate(spec['lines']):
    a, b = marks[li]; chunks = ln.get('caps') or []
    if not chunks: continue
    wts = [max(4, len(c.replace('*', ''))) for c in chunks]; tot = sum(wts); cur = a
    for c, wt in zip(chunks, wts):
        e = cur + (b - a) * wt / tot
        caps.append((cur - 0.05, e + (GAP if c is chunks[-1] else 0), caption_layer(c)))
        cur = e

# ---------------- render ----------------
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
HOME = (W + 120, H + 200)  # hand rest offscreen
def comp_sketch(frame, d, t):
    if t < d['start']: return None
    p = (t - d['start']) / d['draw']
    x, y, w, h = d['x'], d['y'], d['w'], d['h']
    reg = frame[y:y + h, x:x + w]
    if p >= 1:
        q = ease((t - d['start'] - d['draw']) / d['fill'])
        a = d['alpha'][..., None]
        inkonly = np.where(d['ink'][..., None], INK, reg)
        full = reg * (1 - a) + d['rgb'] * a
        reg[:] = inkonly * (1 - q) + full * q
        return None
    nrev = int(d['n'] * ease(p * 1.02))
    m = (d['rank'] < nrev) & d['ink']
    reg[m] = INK
    if d['n'] and nrev > 0:
        c = d['centers'][min(nrev - 1, d['n'] - 1)]
        jx = math.sin(t * 37) * 3; jy = math.cos(t * 29) * 3
        return (x + c[0] + jx, y + c[1] + jy)
    return (x, y)

def render():
    nfr = int(TOTAL * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', os.path.join(TMP, 'v.mp4')]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    last_hand = HOME; draw_act = np.zeros(nfr, np.float32)
    for fi in range(nfr):
        t = fi / FPS
        si = max(i for i, s in enumerate(prepared) if s['t0'] <= t + 1e-6)
        S = prepared[si]
        fr = BG.copy()
        paste_rgba(fr, TAG, 36, 92)
        # title written left->right
        tl = S['title']; p = ease((t - S['title_t'][0]) / (S['title_t'][1] - S['title_t'][0]))
        hand = None
        if p > 0:
            cw = int(tl.shape[1] * p); paste_rgba(fr, tl[:, :cw], 30, 160)
            ul = int((tl.shape[1] - 20) * p)
            fr[160 + tl.shape[0] + 2:160 + tl.shape[0] + 8, 40:40 + ul] = (226, 120, 60)
            if p < 1: hand = (30 + cw, 160 + tl.shape[0] * 0.7); draw_act[fi] = 0.6
        for d in S['sketches']:
            hp = comp_sketch(fr, d, t)
            if hp is not None: hand = hp; draw_act[fi] = 1.0
            if d.get('lab') and t >= d['start'] + d['draw']:
                L, lx, ly = d['lab']; q = ease((t - d['start'] - d['draw']) / 0.25)
                if q < 1:
                    sc = 0.6 + 0.4 * q; Li = Image.fromarray(L.astype(np.uint8), 'RGBA'); Li = Li.resize((max(1, int(Li.width * sc)), max(1, int(Li.height * sc))))
                    La = np.asarray(Li).astype(np.float32); La[..., 3] *= q
                    paste_rgba(fr, La, lx + (L.shape[1] - La.shape[1]) // 2, ly + (L.shape[0] - La.shape[0]) // 2)
                else: paste_rgba(fr, L, lx, ly)
        # section fade-out to paper in last 0.25s
        if si < len(prepared) - 1 and t > S['t1'] - 0.25:
            q = ease((t - (S['t1'] - 0.25)) / 0.25)
            r = fr[TOP - 60:BOT + 10]; r[:] = r * (1 - q) + BG[TOP - 60:BOT + 10] * q
            th = fr[150:300]; th[:] = th * (1 - q) + BG[150:300] * q
        if HOOK is not None and t < HOOK_END:
            sc = 1.0 + 0.03 * math.sin(t * 8)
            Hi = Image.fromarray(HOOK.astype(np.uint8), 'RGBA'); Hi = Hi.resize((int(Hi.width * sc), int(Hi.height * sc)))
            Ha = np.asarray(Hi).astype(np.float32)
            if t > HOOK_END - 0.2: Ha[..., 3] *= max(0.0, (HOOK_END - t) / 0.2)
            paste_rgba(fr, Ha, (W - Ha.shape[1]) // 2, 820 - Ha.shape[0] // 2)
        for a, b, L in caps:
            if a <= t < b:
                q = ease((t - a) / 0.12)
                if q < 1: L = L.copy(); L[..., 3] *= q
                paste_rgba(fr, L, (W - L.shape[1]) // 2, 1405)
        # hand motion
        tgt = hand if hand is not None else HOME
        k = 0.55 if hand is not None else 0.18
        last_hand = (last_hand[0] + (tgt[0] - last_hand[0]) * k, last_hand[1] + (tgt[1] - last_hand[1]) * k)
        if last_hand[0] < W + 60 and last_hand[1] < H + 100: draw_hand(fr, *last_hand)
        pr.stdin.write(fr.astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait()
    return draw_act

act = render()

# ---------------- audio mix ----------------
sr = SR; n = len(vbuf)
# marker scribble sfx
env = np.repeat(act, int(sr / FPS))[:n]; env = np.pad(env, (0, max(0, n - len(env))))
noise = np.random.normal(0, 1, n).astype(np.float32)
from numpy.fft import rfft, irfft
spec_ = rfft(noise); fr_ = np.fft.rfftfreq(n, 1 / sr); spec_[(fr_ < 2500) | (fr_ > 7000)] = 0; scr = irfft(spec_, n).astype(np.float32)
scr /= (np.abs(scr).max() + 1e-6)
mod = 0.55 + 0.45 * np.sin(2 * np.pi * 7.5 * np.arange(n) / sr) * np.sin(2 * np.pi * 2.1 * np.arange(n) / sr)
k = np.ones(int(sr * 0.05)) / int(sr * 0.05); env = np.convolve(env, k, 'same')
sfx = scr * mod * env * float(spec.get('sfx_vol', 0.012))
mix = vbuf + sfx
wav_p = os.path.join(TMP, 'vo.wav')
wv = wave.open(wav_p, 'w'); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(sr); wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
music = spec.get('music')
inputs = ['-i', os.path.join(TMP, 'v.mp4'), '-i', wav_p]
if music and os.path.exists(P(music)):
    inputs += ['-stream_loop', '-1', '-i', P(music)]
    af = (f"[2:a]volume=0.13,afade=t=in:d=0.6,afade=t=out:st={TOTAL - 1.6:.2f}:d=1.5,aresample=48000[m];"
          f"[1:a]aresample=48000,volume=1.0[v];[m][v]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[md];"
          f"[1:a]aresample=48000[v2];[md][v2]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    # sidechain needs the voice twice; use asplit
    af = (f"[1:a]aresample=48000,asplit=2[v1][v2];[2:a]aresample=48000,volume={float(spec.get('music_vol', 0.07))},afade=t=in:d=0.6,afade=t=out:st={TOTAL - 1.6:.2f}:d=1.5[m];"
          f"[m][v1]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=350[md];[md][v2]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
else:
    af = "[1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', af, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', f'{TOTAL:.2f}', '-movflags', '+faststart', OUT], check=True)
print('OK', OUT, round(TOTAL, 2))
