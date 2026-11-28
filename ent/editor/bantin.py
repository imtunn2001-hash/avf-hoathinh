"""BAN TIN VANG kieu thoi su (chu duyet bo cuc 26/11, theo video mau chu gui) - 9:16.
Bo cuc:
  1. Canh mo 3,5s: nua tren la anh chinh (slide dau), nua duoi nen mau page + hoa van cham mo,
     vien logo page nam ngay mep giua 2 nua, tag "NGAY DANG", tieu de IN HOA 3-4 dong trang, ket bang "…".
  2. Than: anh nam o dai giua khung, tren/duoi la chinh anh do phong to + lam mo de lap nen.
     Goc tren trai "NGUON: ...", goc tren phai logo page, goc duoi trai tag ngay dang.
     Moi cau (hoac moi 3-4s) doi 1 anh, zoom nhe, chuyen mo 0,25s.
  3. Ket: khong lam man ket rieng (TikTok tu gan). Cau mien tru o loi doc + caption.
Moi chu nam trong SAFE (80-940, 260-1460).
SPEC_JSON = spec truc tiep:
{ page:{name, short, accent, accent2, bg}, date:"25/11/2026", source:"NGUỒN: PNJ, SJC, COMEX",
  headline:"... …", voice_urls:[...], pauses:[...], candles:[{t,o,h,l,c}],
  slides:[{"sent":0, "kind":"board"|"chart"|"news"|"big", ...}] }   # sent = so thu tu cau bat dau doi anh
"""
import json, math, os, random, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series import get, ease, voice_part  # noqa: E402
import safezone  # noqa: E402
from chart20 import F, vn  # noqa: E402

W, H, FPS = 1080, 1920, 30
SX0, SY0, SX1, SY1 = safezone.SAFE
ROOT = os.getcwd(); OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
WHITE = (255, 255, 255); BLACK = (0, 0, 0); UP = (34, 197, 94); DN = (239, 68, 68); MUTED = (170, 178, 196)
# 28/11 FULL KHUNG (chu chot): bo dai anh giua + nen mo; moi anh ve tren nen tran 1080x1920,
# noi dung dat tu OY xuong; chu trong SAFE (x 80-940, y 260-1460), nen chart tran xuong day.
OY = 440
SW, SH_ = 1080, 1000                   # lop noi dung (chart: cao toi day khung)
LYMAX = 1380 - OY                      # chu trong lop phai < y nay


def tup(x, d): return tuple(x) if x else d


def wrap(d, txt, f, maxw):
    out, cur = [], ''
    for w in txt.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out


# ---------------- ve tung anh (1080 x 900) ----------------
def full_bg(P):
    im = Image.new('RGB', (W, H), P['bg']); d = ImageDraw.Draw(im)
    for y in range(H):   # gradient nhe tran khung
        k = y / H; c = tuple(int(P['bg'][i] * (1 - .35 * k) + P['accent'][i] * .14 * (1 - k)) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    mp = map_pattern(P, W, H, seed=11); a = mp.getchannel('A').point(lambda v: v // 2); mp.putalpha(a)
    im = im.convert('RGBA'); im.alpha_composite(mp); return im.convert('RGB')


def slide_bg(P, h=SH_):
    im = Image.new('RGBA', (SW, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)


def s_board(P, s):
    im, d = slide_bg(P)
    with safezone.decor():
        d.text((70, 60), s.get('title', ''), font=F(True, 58), fill=P['accent2'])
        d.text((70, 132), s.get('sub', ''), font=F(False, 34), fill=MUTED)
        y = 260
        d.text((430, y), 'MUA VÀO', font=F(True, 34), fill=MUTED); d.text((690, y), 'BÁN RA', font=F(True, 34), fill=MUTED)
        y += 64
        for r in s.get('rows', []):
            d.rounded_rectangle([50, y - 14, SW - 50, y + 150], 24, fill=tuple(min(255, c + 22) for c in P['bg']) + (235,))
            d.text((80, y + 6), r['name'], font=F(True, 40), fill=WHITE)
            d.text((80, y + 64), r.get('note', ''), font=F(False, 30), fill=MUTED)
            for x, k in ((430, 'buy'), (690, 'sell')):
                fv = F(True, 50)
                while d.textlength(r[k], font=fv) > 240 and fv.size > 34: fv = F(True, fv.size - 2)
                d.text((x, y + 4), r[k], font=fv, fill=WHITE)
                ch = r.get(k + '_ch', '')
                if ch: d.text((x, y + 72), ch, font=F(True, 36), fill=DN if ch.startswith(('−', '-')) else UP)
            y += 190
        if s.get('foot'):
            d.text((70, SH_ - 150), s['foot'], font=F(True, 38), fill=P['accent2'])
    return im


def s_big(P, s):
    im, d = slide_bg(P)
    with safezone.decor():
        f = F(True, 150); t = s['big']; tw = d.textlength(t, font=f)
        while tw > SW - 140: f = F(True, f.size - 8); tw = d.textlength(t, font=f)
        d.text(((SW - tw) / 2, 330), t, font=f, fill=s.get('color') and tuple(s['color']) or P['accent2'], stroke_width=4, stroke_fill=BLACK)
        y = 560
        for ln in wrap(d, s.get('cap', ''), F(True, 52), SW - 160):
            d.text(((SW - d.textlength(ln, font=F(True, 52))) / 2, y), ln, font=F(True, 52), fill=WHITE); y += 70
        if s.get('top'): d.text(((SW - d.textlength(s['top'], font=F(True, 44))) / 2, 220), s['top'], font=F(True, 44), fill=MUTED)
    return im


def s_news(P, s):
    im, d = slide_bg(P)
    with safezone.decor():
        d.rounded_rectangle([70, 160, 70 + d.textlength(s['src'], font=F(True, 38)) + 50, 230], 14, fill=WHITE)
        d.text((95, 168), s['src'], font=F(True, 38), fill=P['bg'])
        y = 280
        for ln in wrap(d, s['title'], F(True, 60), SW - 160):
            d.text((80, y), ln, font=F(True, 60), fill=WHITE); y += 80
        d.rectangle([80, y + 20, 280, y + 28], fill=P['accent'])
        if s.get('note'):
            y += 70
            for ln in wrap(d, s['note'], F(False, 40), SW - 160):
                d.text((80, y), ln, font=F(False, 40), fill=MUTED); y += 56
    return im


def s_chart(P, s, C):
    CHH = H - OY; im, d = slide_bg(P, CHH)
    i0, i1 = int(s.get('i0', 0)), int(s.get('i1', len(C) - 1)); cs = C[i0:i1 + 1]
    lv = s.get('levels', [])
    lo = min([c['l'] for c in cs] + [x['price'] for x in lv]); hi = max([c['h'] for c in cs] + [x['price'] for x in lv])
    pad = (hi - lo) * .14; lo -= pad; hi += pad
    X0, X1, Y0, Y1 = 0, 820, 260, CHH - 60
    Y = lambda v: Y1 - (v - lo) / (hi - lo) * (Y1 - Y0)
    slot = (X1 - X0) / len(cs); bw = max(4, slot * .62)
    with safezone.decor():
        d.text((60, 40), s.get('title', 'VÀNG THẾ GIỚI (USD/ounce)'), font=F(True, 46), fill=P['accent2'])
        d.text((60, 102), s.get('sub', ''), font=F(False, 32), fill=MUTED)
        step = 25 if hi - lo < 220 else 50
        g = math.ceil(lo / step) * step
        while g < hi:
            d.line([(X0, Y(g)), (X1 + 8, Y(g))], fill=tuple(min(255, c + 26) for c in P['bg']), width=1)
            if Y(g) < LYMAX - 30: d.text((X1 + 18, Y(g) - 16), vn(g, 0), font=F(False, 28), fill=MUTED)
            g += step
        for k, c in enumerate(cs):
            x = X0 + (k + .5) * slot; col = UP if c['c'] >= c['o'] else DN
            d.line([(x, Y(c['h'])), (x, Y(c['l']))], fill=col, width=3)
            a, b = sorted([Y(c['o']), Y(c['c'])]); d.rectangle([x - bw / 2, a, x + bw / 2, max(b, a + 2)], fill=col)
        for x_ in lv:
            y = Y(x_['price']); xx = X0
            while xx < X1: d.line([(xx, y), (min(xx + 16, X1), y)], fill=P['accent'], width=4); xx += 28
            lab = x_['label']; lw = d.textlength(lab, font=F(True, 34)); yt = min(y + 8, LYMAX - 60)
            d.rounded_rectangle([X1 - lw - 30, yt, X1 - 6, yt + 48], 10, fill=P['accent']); d.text((X1 - lw - 18, yt + 4), lab, font=F(True, 34), fill=WHITE)
        for m in s.get('marks', []):
            k = int(m['i']) - i0
            if not 0 <= k < len(cs): continue
            c = cs[k]; x = X0 + (k + .5) * slot; low = m.get('side', 'low') == 'low'
            yb = Y(c['l']) + 12 if low else Y(c['h']) - 12; ya = yb + (60 if low else -60)
            d.line([(x, ya), (x, yb)], fill=P['accent2'], width=5)
            d.polygon([(x, yb), (x - 13, yb + (22 if low else -22)), (x + 13, yb + (22 if low else -22))], fill=P['accent2'])
            f = F(True, 40); tw = d.textlength(m['text'], font=f); tx = min(max(80, x - tw / 2), X1 - tw); ty = ya + (8 if low else -54)
            if ty > LYMAX - 60: ty = Y(c['h']) - 70   # day qua thap -> nhan len tren nen
            ty = min(ty, LYMAX - 60)
            d.rounded_rectangle([tx - 12, ty - 4, tx + tw + 12, ty + 50], 12, fill=BLACK, outline=P['accent2'], width=2)
            d.text((tx, ty), m['text'], font=f, fill=WHITE)
        d.text((60, 150), cs[0]['t'] + '  →  ' + cs[-1]['t'], font=F(False, 28), fill=MUTED)
    return im


def make_slide(P, s, C):
    k = s['kind']
    lay = {'board': s_board, 'big': s_big, 'news': s_news}[k](P, s) if k != 'chart' else s_chart(P, s, C)
    im = full_bg(P).convert('RGBA'); im.alpha_composite(lay, (0, OY)); return im.convert('RGB')


# ---------------- khung hinh ----------------
def cover_fill(img, w, h):
    r = max(w / img.width, h / img.height); im = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    return im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))


def blur_bg(img):
    b = cover_fill(img, W, H).filter(ImageFilter.GaussianBlur(38))
    return Image.blend(b, Image.new('RGB', (W, H), BLACK), .45)


def map_pattern(P, w, h, seed=7):
    """hoa van cham mo kieu ban do the gioi (tu ve, khong dung anh co ban quyen)."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); r = random.Random(seed)
    blobs = [(r.uniform(.05, .95) * w, r.uniform(.15, .95) * h, r.uniform(90, 230)) for _ in range(9)]
    for y in range(0, h, 16):
        for x in range(0, w, 16):
            if any((x - bx) ** 2 / (br * 1.6) ** 2 + (y - by) ** 2 / br ** 2 < 1 for bx, by, br in blobs):
                d.ellipse([x, y, x + 6, y + 6], fill=(255, 255, 255, 34))
    return im


def logo_pill(d, P, x, y, h=78):
    f = F(True, 40); name = P['name']; tw = d.textlength(name, font=f)
    d.rounded_rectangle([x, y, x + h + tw + 40, y + h], h // 2, fill=P['accent'], outline=WHITE, width=4)
    d.ellipse([x + 8, y + 8, x + h - 8, y + h - 8], fill=WHITE)
    fs = F(True, 30); st = P.get('short', name[:2]); sw = d.textlength(st, font=fs)
    d.text((x + h / 2 - sw / 2, y + h / 2 - 20), st, font=fs, fill=P['accent'])
    d.text((x + h + 10, y + h / 2 - 25), name, font=f, fill=WHITE)
    return x + h + tw + 40


def date_tag(d, P, x, y, txt, fs=30):
    f = F(True, fs); tw = d.textlength(txt, font=f)
    d.rectangle([x, y, x + tw + 28, y + fs + 20], fill=(235, 238, 242))
    d.text((x + 14, y + 8), txt, font=f, fill=P['bg'])


def main():
    sp = json.loads(os.environ['SPEC_JSON'])
    P = sp['page']; P['accent'] = tup(P.get('accent'), (230, 57, 70)); P['accent2'] = tup(P.get('accent2'), (255, 190, 190)); P['bg'] = tup(P.get('bg'), (20, 8, 12))
    C = sp.get('candles') or []
    # giong: noi tung cau, giu pauses -> moc bat dau tung cau
    parts, starts, off = [], [], 0.0
    for i, u in enumerate(sp['voice_urls']):
        pth = u if os.path.exists(u) else get(u, os.path.join(OUT, f'vp{i}.mp3'))
        wav = os.path.join(OUT, f'vp{i}.wav'); dd, _ = voice_part(pth, wav, sp, i)
        starts.append(off); parts.append(wav); off += dd
    lst = os.path.join(OUT, 'vlist.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    voice = os.path.join(OUT, 'voice.wav')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice])
    LEAD, TAIL = 0.2, 1.2; D = off + LEAD + TAIL; COVER = float(sp.get('cover_sec', 3.6))
    # anh + moc doi anh
    sl = sp['slides']; imgs = [make_slide(P, s, C) for s in sl]
    bgs = [blur_bg(im) for im in imgs]
    t0s = [max(0.0, starts[min(len(starts) - 1, int(s.get('sent', 0)))] + LEAD) for s in sl]; t0s[0] = 0.0
    for k in range(1, len(t0s)): t0s[k] = max(t0s[k], t0s[k - 1] + 1.5)
    # lop co dinh than video
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    src = sp.get('source', 'NGUỒN: PNJ, SJC, COMEX')
    for j, ln in enumerate(src.split('\n')): od.text((SX0 + 4, 276 + j * 40), ln, font=F(True, 30), fill=WHITE, stroke_width=3, stroke_fill=BLACK)
    f = F(True, 34); nm = P['name']; tw = od.textlength(nm, font=f)
    od.rounded_rectangle([SX1 - tw - 34, 268, SX1, 322], 27, fill=(*P['accent'], 235)); od.text((SX1 - tw - 17, 274), nm, font=f, fill=WHITE)
    date_tag(od, P, SX0, 1388, 'NGÀY ĐĂNG: ' + sp.get('date', ''))
    # canh mo (tinh) - nua duoi
    cov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(cov)
    TOP = 960
    for y in range(TOP, H):
        k = (y - TOP) / (H - TOP); c = tuple(int(P['accent'][i] * (1 - .45 * k) + P['bg'][i] * .45 * k) for i in range(3))
        cd.line([(0, y), (W, y)], fill=(*c, 255))
    cov.alpha_composite(map_pattern(P, W, H - TOP), (0, TOP))
    cd = ImageDraw.Draw(cov)
    logo_pill(cd, P, SX0, TOP - 40)
    date_tag(cd, P, SX0, TOP + 72, 'NGÀY ĐĂNG: ' + sp.get('date', ''), 28)
    fh = F(True, 66); hl = wrap(cd, sp['headline'].upper(), fh, SX1 - SX0 - 10)
    while (len(hl) > 4 or TOP + 140 + len(hl) * int(fh.size * 1.16) > SY1 - 10) and fh.size > 44:
        fh = F(True, fh.size - 4); hl = wrap(cd, sp['headline'].upper(), fh, SX1 - SX0 - 10)
    for j, ln in enumerate(hl): cd.text((SX0, TOP + 136 + j * int(fh.size * 1.16)), ln, font=fh, fill=WHITE)
    cd.text((SX0 + 4, 276), src.split('\n')[0], font=F(True, 30), fill=WHITE, stroke_width=3, stroke_fill=BLACK)

    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)

    def band(k, t):   # phan noi dung anh k (cho canh mo)
        return imgs[k].crop((0, OY - 40, W, OY + 860))

    def body(k, t):   # full khung, khong zoom (zoom day chu ra ngoai vung an toan)
        return imgs[k]

    for fi in range(int(D * FPS)):
        t = fi / FPS; k = max(i for i in range(len(t0s)) if t0s[i] <= t)
        fr = body(k, t)
        if k > 0 and t - t0s[k] < .25: fr = Image.blend(body(k - 1, t), fr, ease((t - t0s[k]) / .25))
        if t < COVER:   # canh mo: anh chinh nua tren + the tieu de nua duoi
            b0 = band(0, t); fr = bgs[0].copy()
            sc = b0.resize((W, int(900 * .7)), Image.LANCZOS); fr.paste(sc, (0, TOP - sc.height - 10))   # anh chinh nam duoi dong nguon
            q = ease(min(1.0, t / .3)); cv = cov if q >= 1 else Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 0)), cov, q)
            fr = fr.convert('RGBA'); fr.alpha_composite(cv); fr = fr.convert('RGB')
            if t > COVER - .3: fr = Image.blend(fr, body(k, t), ease((t - (COVER - .3)) / .3))
        else:
            fr = fr.convert('RGBA'); fr.alpha_composite(ov); fr = fr.convert('RGB')
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    mus = os.path.join(ROOT, 'editor', 'story', sp.get('music', 'music_b.mp3'))
    fc = f'[1:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)}[v];[2:a]volume=0.08[m];[v][m]amix=inputs=2:duration=first:normalize=0,apad,loudnorm=I=-15:TP=-1.5[a]'
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', voice, '-stream_loop', '-1', '-i', mus, '-filter_complex', fc,
                           '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4')); print('ok', round(D, 2), 'slides', [round(x, 1) for x in t0s])


if __name__ == '__main__':
    main()
