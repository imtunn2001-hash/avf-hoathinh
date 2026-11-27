#!/usr/bin/env python3
"""Video giai thich / ke chuyen khung vuong 1080x1080 (kenh Chuyen Chua Ke), hoac kho doc 9:16 neu layout = "v916".
spec (json):
  dir: thu muc chua tai nguyen (anh canh, giong)
  title: tieu de (1-2 dong) tren banner; part: chu tren banner duoi (vd "Phan 1"); channel: ten kenh
  scenes: [{img: "s01.png", label: "CHU KHOA" (tuy chon), text: "loi doc cua canh"}]
  voice: [{wav: "v01.wav", scenes: [0,1,2,...]}]   # moi file giong doc lien cac canh
  voice_speed: 1.12, music: "editor/story/music_x.mp3", music_vol: 0.10, sfx_vol: 0.35
  out: duong dan mp4
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

spec = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.loads(os.environ['SPEC_JSON'])
ROOT = os.getcwd(); D = spec.get('dir', '.'); TMP = spec.get('tmp', '/tmp/explain'); os.makedirs(TMP, exist_ok=True)
P = lambda f: f if os.path.isabs(f) else os.path.join(D, f)
W = H = 1080; FPS = int(spec.get('fps', 25))
PY0, PH = 236, 608  # khung 16:9 o giua
VERT = spec.get('layout') == 'v916'  # kho doc 9:16, hinh phu kin man hinh
if VERT: W, H = 1080, 1920; PY0, PH = 0, 1920
NAVY = (22, 30, 92); NAVY2 = (14, 20, 66); YEL = (255, 214, 64)


def font(sz, w='ExtraBold'):
    for f in [os.path.join(ROOT, 'fonts', 'BeVietnamPro-' + w + '.ttf'), '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


# ---------------- am thanh: giong -> moc thoi gian tung canh ----------------
def read_wav(p):
    w = wave.open(p); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: x = x.reshape(-1, 2).mean(1)
    if sr != 24000:  # dong nhat tan so mau (giong du phong co the la 44.1/48 kHz)
        n = int(len(x) * 24000 / sr); x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32); sr = 24000
    return x, sr


def trim(x, sr, th=0.012):
    a = np.abs(x); idx = np.where(a > th)[0]
    if not len(idx): return x
    return x[max(0, idx[0] - int(0.03 * sr)): min(len(x), idx[-1] + int(0.06 * sr))]


def speed(wp):
    sp = float(spec.get('voice_speed', 1.0))
    if abs(sp - 1) < 0.01: return wp
    fp = os.path.join(TMP, 'sp_' + os.path.basename(wp))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wp, '-filter:a', 'atempo=%.3f' % sp, '-ac', '1', '-ar', '24000', fp], check=True)
    return fp


def extra_imgs(sc):
    return [sc[k] for k in ('img2', 'img3', 'img4') if sc.get(k)]


SC = spec['scenes']; N = len(SC)
# ANH TU LIEU THAT (Wikimedia Commons): scene.real = {url, credit}. Tai ve, thay vao o hinh phu cuoi cung
# cua canh (khong dung canh 1 = hook). Loi tai -> bo qua, giu anh ve.
REAL = set()
for k, sc in enumerate(SC):
    r = sc.get('real') or {}
    if k == 0 or not r.get('url'): continue
    fp = os.path.join(TMP, 'real_%02d.jpg' % k)
    try:
        import urllib.request
        req = urllib.request.Request(r['url'], headers={'User-Agent': 'AVF-StoryBot/1.0'})
        open(fp, 'wb').write(urllib.request.urlopen(req, timeout=40).read())
        im = Image.open(fp); im.verify()
        if im.width < 500 or im.height < 400: raise ValueError('nho')
    except Exception as e:
        print('real_bo', k, str(e)[:80], flush=True); continue
    slot = 'img3' if sc.get('img3') else ('img2' if not sc.get('img2') else 'img3')
    sc[slot] = fp; REAL.add(fp)
print('anh_tu_lieu', len(REAL), flush=True)
# CANH QUAY THAT (Pixabay video): scene.broll = {url}. Tai mp4, chen nhu 1 o hinh phu (canh dong). Loi -> bo qua.
VIDS = set()
for k, sc in enumerate(SC):
    b = sc.get('broll') or {}
    if k == 0 or not b.get('url'): continue
    slot = next((s for s in ('img2', 'img3', 'img4') if not sc.get(s)), None)
    if not slot: continue
    fp = os.path.join(TMP, 'broll_%02d.mp4' % k)
    try:
        import urllib.request
        req = urllib.request.Request(b['url'], headers={'User-Agent': 'Mozilla/5.0 (compatible; AVF-StoryBot/1.0)'})
        open(fp, 'wb').write(urllib.request.urlopen(req, timeout=90).read())
        pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', fp], capture_output=True, text=True, timeout=30)
        vw_, vh_ = [int(x) for x in pr.stdout.strip().split(',')[:2]]
        if vw_ < 480 or vh_ < 360: raise ValueError('nho')
    except Exception as e:
        print('broll_bo', k, str(e)[:80], flush=True); continue
    sc[slot] = fp; VIDS.add(fp)
print('canh_quay_that', len(VIDS), flush=True)
starts = [0.0] * N; ends = [0.0] * N; mids = [None] * N
voice = []; t = 0.06; SR = 24000  # hook: noi ngay, khong im lang dau video
for ch in spec['voice']:
    x, sr = read_wav(speed(P(ch['wav']))); SR = sr; x = trim(x, sr)
    idxs = ch['scenes']; dur = len(x) / sr
    hop = int(sr * 0.02); n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)); th = max(0.006, float(np.percentile(e, 90)) * 0.07); sil = e < th
    gaps = []; i = 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]: j += 1
            if (j - i) * 0.02 >= 0.12: gaps.append((i * 0.02, j * 0.02))
            i = j
        else: i += 1
    wts = [max(6, len(SC[k].get('text', ''))) for k in idxs]; cum = np.cumsum(wts)[:-1] / sum(wts) * dur
    bounds = []; last = 0.0
    for c in cum:
        cand = [g for g in gaps if (g[0] + g[1]) / 2 > last + 0.6]
        g = min(cand, key=lambda g: abs((g[0] + g[1]) / 2 - c)) if cand else None
        if g is None or abs((g[0] + g[1]) / 2 - c) > max(2.0, dur * 0.08): g = (c, c)
        bounds.append(g); last = (g[0] + g[1]) / 2
    for q, k in enumerate(idxs):
        starts[k] = t + (0 if q == 0 else (bounds[q - 1][0] + bounds[q - 1][1]) / 2)
        ends[k] = t + ((bounds[q][0] + bounds[q][1]) / 2 if q < len(bounds) else dur)
    if len(idxs) == 1:
        k0 = idxs[0]; M = len(extra_imgs(SC[k0])) + 1
        if M > 1:
            # canh nhieu hinh: doi hinh o khoang ngat cau gan cac moc j/M cua doan giong
            cs = []; lastc = 0.0
            for j in range(1, M):
                tg = dur * j / M
                cg = [g for g in gaps if abs((g[0] + g[1]) / 2 - tg) <= dur * 0.12 and (g[0] + g[1]) / 2 > lastc + 1.2]
                c = min(((g[0] + g[1]) / 2 for g in cg), key=lambda m: abs(m - tg)) if cg else tg
                if c <= lastc + 1.2: c = lastc + 1.2
                cs.append(t + c); lastc = c
            mids[k0] = cs
    voice.append((t, x)); t += dur + 0.35
TOTAL = t + 1.6
ends[-1] = TOTAL
for k in range(N - 1): ends[k] = starts[k + 1]
starts[0] = 0.0
for k in range(N):
    M = len(extra_imgs(SC[k])) + 1
    if M > 1 and mids[k] is None:
        mids[k] = [starts[k] + (ends[k] - starts[k]) * j / M for j in range(1, M)]
    if mids[k]:
        ok = []; prev = starts[k]
        for c in mids[k]:
            if prev + 1.2 < c < ends[k] - 1.2: ok.append(c); prev = c
        mids[k] = ok or None
HOOK_CUTS = [c for c in (0.9, 1.8, 2.7, 3.6) if c < ends[0] - 0.4]

# ---------------- do hoa co dinh ----------------
def frame_base():
    if VERT: return Image.new('RGB', (W, H), (0, 0, 0))
    im = Image.new('RGB', (W, H), NAVY2); d = ImageDraw.Draw(im)
    for y in range(PY0):
        a = y / PY0; d.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] * (1 - a * 0.25)) for i in range(3)))
    for y in range(PY0 + PH, H):
        a = (y - PY0 - PH) / (H - PY0 - PH); d.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] * (0.8 + 0.2 * a)) for i in range(3)))
    for x in range(-H, W, 46): d.line([(x, 0), (x + PY0, PY0)], fill=(28, 38, 108), width=10)
    return im


def overlay_vert(title, part, channel):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g = Image.new('L', (1, H), 0)
    for y in range(H):
        a = 0
        if y < 420: a = int(215 * (1 - y / 420) ** 1.3)
        elif y > 1380: a = int(190 * ((y - 1380) / (H - 1380)) ** 1.2)
        g.putpixel((0, y), a)
    lay.paste(Image.new('RGBA', (W, H), (8, 6, 4, 255)), (0, 0), g.resize((W, H)))
    d = ImageDraw.Draw(lay)
    f0 = font(30); pill = (str(part) + '  •  ' + str(channel)).strip(' •').upper()
    pw = d.textlength(pill, font=f0) + 48
    d.rounded_rectangle(((W - pw) / 2, 58, (W + pw) / 2, 108), 25, fill=(150, 24, 24, 235))
    d.text(((W - pw) / 2 + 24, 64), pill, font=f0, fill=(255, 236, 200, 255))
    f = font(66); lines = []
    for para in str(title).split('\n'):
        cur = ''
        for wd in para.split():
            tt = (cur + ' ' + wd).strip()
            if d.textlength(tt, font=f) <= 960: cur = tt
            else: lines.append(cur); cur = wd
        if cur: lines.append(cur)
    y = 140
    for ln in lines[:3]:
        tw = d.textlength(ln, font=f); d.text(((W - tw) / 2, y), ln, font=f, fill=YEL, stroke_width=7, stroke_fill=(20, 10, 4)); y += 82
    return lay


def overlay_top(title, part, channel):
    if VERT: return overlay_vert(title, part, channel)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = font(50); lines = []
    for para in str(title).split('\n'):
        cur = ''
        for wd in para.split():
            tt = (cur + ' ' + wd).strip()
            if d.textlength(tt, font=f) <= 960: cur = tt
            else: lines.append(cur); cur = wd
        if cur: lines.append(cur)
    lines = lines[:2]; lh = 62; y = int(PY0 / 2 - lh * len(lines) / 2) - 6
    for ln in lines:
        tw = d.textlength(ln, font=f); d.text(((W - tw) / 2, y), ln, font=f, fill=YEL, stroke_width=4, stroke_fill=(10, 14, 40)); y += lh
    d.rounded_rectangle((W / 2 - 230, PY0 - 22, W / 2 + 230, PY0 - 12), 5, fill=YEL)
    # vien sang tim duoi khung
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
    dg.rounded_rectangle((W / 2 - 300, PY0 + PH - 4, W / 2 + 300, PY0 + PH + 10), 7, fill=(170, 90, 255, 230))
    glow = glow.filter(ImageFilter.GaussianBlur(8)); lay.alpha_composite(glow)
    d.rounded_rectangle((W / 2 - 260, PY0 + PH - 1, W / 2 + 260, PY0 + PH + 5), 3, fill=(215, 170, 255, 255))
    f2 = font(46); tw = d.textlength(part, font=f2)
    d.text(((W - tw) / 2, PY0 + PH + 62), part, font=f2, fill=YEL, stroke_width=3, stroke_fill=(10, 14, 40))
    f3 = font(26, 'Medium') if os.path.exists(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Medium.ttf')) else font(26)
    tw = d.textlength(channel, font=f3); d.text(((W - tw) / 2, PY0 + PH + 140), channel, font=f3, fill=(220, 225, 255, 230))
    return lay


def label_img(s, accent, big=False):
    f = font((84 if VERT else 64) if big else (62 if VERT else 40)); d0 = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    maxw = (960 if VERT else 1100) if big else (900 if VERT else 640)
    words = str(s).upper().split(); lines = []; cur = ''
    for wd in words:
        tt = (cur + ' ' + wd).strip()
        if d0.textlength(tt, font=f) <= maxw: cur = tt
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    lines = lines[:2]; lh = int((76 if VERT else 50) * (1.35 if big else 1))
    wmax = int(max(d0.textlength(l, font=f) for l in lines)) + 40
    im = Image.new('RGBA', (wmax, lh * len(lines) + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        x = (wmax - d.textlength(ln, font=f)) / 2 if (VERT or big) else 20
        d.text((x, 10 + i * lh), ln, font=f, fill=accent, stroke_width=(10 if VERT else 8) if big else (8 if VERT else 5), stroke_fill=(12, 16, 44))
    return im


ACC = [(64, 196, 255), (255, 214, 64), (120, 230, 120), (255, 120, 120)]


def real_tag():
    f = font(30, 'Bold') if os.path.exists(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Bold.ttf')) else font(30)
    txt = 'ẢNH TƯ LIỆU'; d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10))); tw = int(d0.textlength(txt, font=f))
    im = Image.new('RGBA', (tw + 44, 52), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw + 43, 51), 26, fill=(0, 0, 0, 170)); d.text((22, 8), txt, font=f, fill=(255, 255, 255, 235))
    return im


REAL_TAG = real_tag()
base = frame_base(); top = overlay_top(spec.get('title', ''), spec.get('part', ''), spec.get('channel', ''))
panels = []; panels2 = []; labels = []


class VidPanel:
    """Canh quay that: doc tuan tu khung hinh tu ffmpeg (da phong kin khung), lap lai khi het."""
    def __init__(self, fn):
        self.fn = fn; self.width = int(W * 1.08) // 2 * 2; self.height = int(PH * 1.08) // 2 * 2
        self.p = None; self.cur = -1; self.off = 0; self.last = None; self.n = self.width * self.height * 3

    def _open(self):
        if self.p: self.p.kill()
        vf = 'scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d,eq=saturation=0.85:contrast=1.05' % (self.width, self.height, self.width, self.height, FPS)
        self.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', self.fn, '-an', '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.cur = -1

    def get(self, lt):
        idx = max(0, int(lt * FPS))
        if self.p is None or idx < self.off + self.cur: self.off = 0; self._open()
        while self.off + self.cur < idx:
            buf = self.p.stdout.read(self.n)
            if len(buf) < self.n:  # het video -> lap lai tu dau
                if self.cur < 0: break
                self.off = self.off + self.cur + 1; self._open(); continue
            self.last = Image.frombuffer('RGB', (self.width, self.height), buf, 'raw', 'RGB', 0, 1); self.cur += 1
        return self.last if self.last is not None else Image.new('RGB', (self.width, self.height), (0, 0, 0))


def load_panel(fn):
    if fn in VIDS: return VidPanel(fn)
    im = Image.open(P(fn)).convert('RGB')
    sc = max(W * 1.08 / im.width, PH * 1.08 / im.height); return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


REALP = set()  # id() cua panel la anh tu lieu that -> ve nhan "ANH TU LIEU"
for k, s in enumerate(SC):
    panels.append(load_panel(s['img']))
    p2 = []; cs = []
    for fn, c in zip(extra_imgs(s), mids[k] or []):
        try:
            pl = load_panel(fn); p2.append(pl); cs.append(c)
            if fn in REAL: REALP.add(id(pl))
        except Exception: pass
    mids[k] = cs or None
    panels2.append(p2 or None)
    # Canh 1 = HOOK: chu to, mau vang, hien ngay khung dau
    labels.append(label_img(s['label'], (255, 214, 64) if k == 0 else ACC[k % len(ACC)], big=(k == 0)) if s.get('label') else None)


def ease_out_back(x):
    c1 = 1.70158; c3 = c1 + 1; x = min(1, max(0, x)); return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def frame_at(tt):
    k = 0
    while k < N - 1 and tt >= starts[k + 1]: k += 1
    st, en = starts[k], ends[k]; lt0 = tt - st
    im = panels[k]; sub = 0
    if panels2[k] is not None:
        cs = mids[k]
        while sub < len(cs) and tt >= cs[sub]: sub += 1
        if sub > 0: im = panels2[k][sub - 1]; st = cs[sub - 1]
        if sub < len(cs): en = cs[sub]
    flash = 0.0
    if k == 0 and HOOK_CUTS and tt < HOOK_CUTS[-1] + 0.9:
        # HOOK: cat nhanh moi 0.9s + chop sang o moi nhat cat
        L = [panels[0]] + list(panels2[0] or [])
        hs = sum(1 for c in HOOK_CUTS if tt >= c)
        im = L[hs % len(L)]; st = HOOK_CUTS[hs - 1] if hs else 0.0
        en = HOOK_CUTS[hs] if hs < len(HOOK_CUTS) else HOOK_CUTS[-1] + 0.9
        sub = 0
        if hs: flash = max(0.0, 1 - (tt - st) / 0.12)
    elif k == 0 and HOOK_CUTS and panels2[0] is not None and sub == 0:
        im = panels[0]
    lt = tt - st; dur = max(0.5, en - st)
    if isinstance(im, VidPanel): im = im.get(lt)
    fr = base.copy()
    hook = (k == 0 and tt < 0.7)
    z = 1.0 + 0.045 * min(1, lt / dur)
    ent = 1.0 if hook else min(1, lt / 0.28)
    if hook: z = 1.0 + 0.10 * (1 - min(1, lt / 0.6)) ** 2 + 0.045 * min(1, lt / dur)  # khung dau sang ngay + punch-in
    z *= 0.94 + 0.06 * (1 - (1 - ent) ** 3)
    vw, vh = W / z, PH / z
    mode = (k + sub) % 3
    x0 = (im.width - vw) / 2 + (im.width - vw) / 2 * (0.6 if mode == 1 else (-0.6 if mode == 2 else 0)) * (lt / dur - 0.5)
    y0 = (im.height - vh) / 2
    crop = im.transform((W, PH), Image.AFFINE, (vw / W, 0, x0, 0, vh / PH, y0), resample=Image.BILINEAR)
    if ent < 1:
        crop = Image.blend(Image.new('RGB', (W, PH), (8, 10, 30)), crop, 0.35 + 0.65 * ent)
    if flash > 0:
        crop = Image.blend(crop, Image.new('RGB', (W, PH), (255, 255, 255)), 0.55 * flash)
    fr.paste(crop, (0, PY0))
    fr = fr.convert('RGBA'); fr.alpha_composite(top)
    if id(im) in REALP: fr.alpha_composite(REAL_TAG, (36, (H - 330) if VERT else (PY0 + PH - 64)))
    lb = labels[k]
    if lb is not None and k == 0:
        # hook: dap manh vao (1.5x -> 1x trong 0.25s), sau do nhip nhe
        s = (1.5 - 0.5 * min(1, lt0 / 0.25) ** 0.5) if lt0 < 0.25 else 1.0 + 0.035 * math.sin(lt0 * 7.0)
        s = min(s, (W - 30) / max(1, lb.width))
        lw, lh = int(lb.width * s), int(lb.height * s)
        l2 = lb.resize((lw, lh), Image.BILINEAR)
        cx, cy = (W / 2, 1290) if VERT else (W / 2, PY0 + PH * 0.78)
        fr.alpha_composite(l2, (int(cx - lw / 2), int(cy - lh / 2)))
    elif lb is not None and lt0 > 0.25:
        a = ease_out_back((lt0 - 0.25) / 0.35); s = max(0.05, a)
        lw, lh = int(lb.width * s), int(lb.height * s)
        if lw > 4 and lh > 4:
            l2 = lb.resize((lw, lh), Image.BILINEAR)
            cx, cy = (W / 2, 1290) if VERT else (40 + lb.width / 2, PY0 + 26 + lb.height / 2)
            fr.alpha_composite(l2, (int(cx - lw / 2), int(cy - lh / 2)))
    return fr.convert('RGB')


vid = os.path.join(TMP, 'v.mp4')
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', vid], stdin=subprocess.PIPE)
nf = int(TOTAL * FPS)
for i in range(nf):
    ff.stdin.write(frame_at(i / FPS).tobytes())
ff.stdin.close(); ff.wait()

# ---------------- tron am thanh ----------------
vbuf = np.zeros(int(TOTAL * SR) + SR, np.float32)
for st, x in voice: i = int(st * SR); vbuf[i:i + len(x)] += x


def synth_whoosh(sr, d=0.45):
    n = int(sr * d); rng = np.random.default_rng(7); w = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    # loc thong thap don gian theo thoi gian (quet)
    out = np.zeros(n, np.float32); a = 0.0
    for i in range(n):
        alpha = 0.04 + 0.5 * (i / n); a = a + alpha * (w[i] - a); out[i] = a
    return out / (np.abs(out).max() + 1e-6) * env


def synth_pop(sr, d=0.09):
    n = int(sr * d); tt = np.arange(n) / sr; f = 900 - 500 * tt / d
    return (np.sin(2 * math.pi * f * tt) * np.exp(-tt * 45)).astype(np.float32)


sfx = np.zeros_like(vbuf); wh = synth_whoosh(SR); pp = synth_pop(SR); sv = float(spec.get('sfx_vol', 0.3))
for k in range(N):
    i = int(max(0, starts[k] - 0.18) * SR); sfx[i:i + len(wh)] += wh[:max(0, len(sfx) - i)] * sv * 0.6
    if SC[k].get('label'):
        j = int((starts[k] + 0.25) * SR); sfx[j:j + len(pp)] += pp[:max(0, len(sfx) - j)] * sv
    for c in (mids[k] or []):
        i = int(max(0, c - 0.15) * SR); sfx[i:i + len(wh)] += wh[:max(0, len(sfx) - i)] * sv * 0.35
def synth_boom(sr, d=0.9):
    n = int(sr * d); tt = np.arange(n) / sr; rng = np.random.default_rng(3)
    low = np.sin(2 * math.pi * (70 - 35 * tt / d) * tt) * np.exp(-tt * 4.5)
    hit = rng.standard_normal(n).astype(np.float32) * np.exp(-tt * 30) * 0.5
    return ((low + hit) / 1.4).astype(np.float32)
bm = synth_boom(SR); sfx[0:len(bm)] += bm[:len(sfx)] * min(1.0, sv * 2.2)
for c in HOOK_CUTS:
    i = int(max(0, c - 0.12) * SR); sfx[i:i + len(wh)] += wh[:max(0, len(sfx) - i)] * sv * 0.7
mix = vbuf + sfx
wav = os.path.join(TMP, 'a.wav')
with wave.open(wav, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
out = spec.get('out', os.path.join(ROOT, 'out', 'out.mp4')); os.makedirs(os.path.dirname(out), exist_ok=True)
mus = spec.get('music'); mv = float(spec.get('music_vol', 0.10))
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', wav]
if mus and os.path.exists(os.path.join(ROOT, mus) if not os.path.isabs(mus) else mus):
    cmd += ['-stream_loop', '-1', '-i', os.path.join(ROOT, mus) if not os.path.isabs(mus) else mus,
            '-filter_complex', f'[2:a]volume={mv},afade=t=in:d=0.05,afade=t=out:st={TOTAL - 2:.2f}:d=2[m];[1:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-15:TP=-1.5[a]',
            '-map', '0:v', '-map', '[a]']
else:
    cmd += ['-filter_complex', '[1:a]loudnorm=I=-15:TP=-1.5[a]', '-map', '0:v', '-map', '[a]']
vq = ['-preset', 'medium', '-crf', str(spec.get('crf', 25))]
if VERT:  # kho doc nang hon: gioi han bitrate de file < 50 MB (Telegram)
    vq = ['-preset', 'faster', '-crf', str(spec.get('crf', 27)), '-maxrate', spec.get('maxrate', '850k'), '-bufsize', '1700k']
cmd += ['-t', f'{TOTAL:.2f}', '-c:v', 'libx264'] + vq + ['-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True)
print('ok', round(TOTAL, 1), 's', N, 'canh', sum(len(x) for x in panels2 if x), 'hinh phu')
