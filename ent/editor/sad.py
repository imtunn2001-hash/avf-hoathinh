"""Reels tam trang cho 2 page pho HN/SG: canh co gai ngoi le duong dem mua + man hinh tin nhan chia tay + stt + nhac buon.
SPEC_JSON = {"photo_git": {"branch","path"} | "photo": "duong dan file",
             "chat": [{"me": false, "t": "..."}, ...], "contact": "Anh", "overlay": "stt ngan 2-4 dong",
             "handle": "truyencuahanoi", "city": "HN", "rot": 0, "dur": 14, "music": "auto"}
Bo cuc: 0 -> c1: anh + mua + den xe chay; c1 -> c2: can man hinh dien thoai, tin nhan hien dan; c2 -> het: anh + chu stt."""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.getcwd()
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
spec = json.loads(os.environ['SPEC_JSON'])
DUR = float(spec.get('dur', 14))


def font(sz, w='ExtraBold'):
    for p in [os.path.join(ROOT, 'fonts', f'BeVietnamPro-{w}.ttf'), os.path.join(ROOT, 'fonts', 'BeVietnamPro-Medium.ttf'),
              '/usr/share/fonts/opentype/inter/Inter-' + ('ExtraBold' if w == 'ExtraBold' else 'Medium') + '.otf']:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    sys.exit('khong co font')


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def wrap(d, s, f, maxw):
    out = []
    for para in s.split('\n'):
        cur = ''
        for w_ in para.split():
            t = (cur + ' ' + w_).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else:
                if cur: out.append(cur)
                cur = w_
        out.append(cur)
    return out


def load_photo():
    if spec.get('photo_git'):
        g = spec['photo_git']
        subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', g['branch']], check=True)
        subprocess.run(['git', 'checkout', 'FETCH_HEAD', '--', g['path']], check=True)
        p = os.path.join(ROOT, g['path'])
    else:
        p = spec['photo']
    im = Image.open(p).convert('RGB')
    iw, ih = im.size; s = max(W / iw, H / ih)
    im = im.resize((int(iw * s) + 2, int(ih * s) + 2), Image.LANCZOS)
    l = (im.width - W) // 2; t = (im.height - H) // 2
    return im.crop((l, t, l + W, t + H))


def pick_music():
    d = os.path.join(ROOT, 'editor', 'street_music'); city = str(spec.get('city', '')).lower(); fs = []
    if spec.get('music') and spec['music'] != 'auto':
        return os.path.join(d, spec['music'])
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        low = f.lower()
        if not low.endswith(('.mp3', '.m4a', '.wav')): continue
        if low.startswith(('hn_', 'sg_')) and not low.startswith(city + '_'): continue
        fs.append(os.path.join(d, f))
    if not fs: return os.path.join(ROOT, 'editor', 'story', 'music_b.mp3')
    return fs[int(spec.get('rot', 0)) % len(fs)]


def zoom(img, z, cx=0.5, cy=0.5):
    cw, ch = W / z, H / z
    x0 = min(max(W * cx - cw / 2, 0), W - cw); y0 = min(max(H * cy - ch / 2, 0), H - ch)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)


def bokeh_sprite(r, col):
    s = Image.new('RGBA', (r * 4, r * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.ellipse([r, r, r * 3, r * 3], fill=(*col, 150))
    return s.filter(ImageFilter.GaussianBlur(r * 0.45))


def green_quad(img):
    import numpy as np
    a = np.asarray(img).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (g > 150) & (g - r > 70) & (g - b > 70)
    ys, xs = np.nonzero(m)
    if len(xs) < 1500: return None, None
    s1, s2 = xs + ys, xs - ys
    tl = (xs[s1.argmin()], ys[s1.argmin()]); br = (xs[s1.argmax()], ys[s1.argmax()])
    tr = (xs[s2.argmax()], ys[s2.argmax()]); bl = (xs[s2.argmin()], ys[s2.argmin()])
    return [tl, tr, br, bl], m


def persp_coeffs(dst, src):
    import numpy as np
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def main():
    random.seed(int(spec.get('rot', 0)) + 7)
    photo = load_photo()
    dark = photo.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35))
    chat = spec.get('chat') or []
    n_msg = len(chat)
    C1 = float(spec.get('c1', 4.5)); C2 = C1 + max(4.5, 0.95 * n_msg + 1.6)
    D = max(DUR, C2 + 4.0)
    # mua
    drops = [[random.uniform(0, W), random.uniform(0, H), random.uniform(1300, 2100), random.uniform(25, 60), random.randint(40, 110)] for _ in range(230)]
    # den xe (bokeh) chay ngang o nua duoi
    cols = [(255, 236, 190), (255, 210, 120), (255, 80, 60), (255, 255, 255), (255, 170, 80)]
    cars = []
    for _ in range(14):
        r = random.randint(26, 64); spr = bokeh_sprite(r, random.choice(cols))
        cars.append([spr, random.uniform(-300, W + 300), random.uniform(H * 0.42, H * 0.7), random.choice([-1, 1]) * random.uniform(120, 320)])
    # giot nuoc tren kinh dien thoai
    gdrops = [(random.uniform(0, 1), random.uniform(0, 1), random.randint(6, 18)) for _ in range(45)]
    fN = font(40, 'Medium'); fNm = font(42); fMsg = font(46, 'Medium'); fSt = font(26, 'Medium')
    fOv = font(62); fH = font(30, 'Medium')
    contact = spec.get('contact', 'Anh')
    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)

    def street(t, z0, z1, a, b):
        q = (t - a) / max(0.1, b - a)
        return layers(zoom(photo, z0 + (z1 - z0) * ease(q), 0.5, 0.55).convert('RGBA'), t)

    def layers(im, t, k=1.0):
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for spr, x, y, v in (cars if k > 0.3 else []):
            xx = (x + v * t) % (W + 600) - 300
            ov.alpha_composite(spr, (int(xx - spr.width / 2), int(y - spr.height / 2)))
        im.alpha_composite(ov)
        rl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rl)
        for x, y, v, ln, al in drops:
            yy = (y + v * t) % (H + 100) - 50; xx = x - 0.18 * (yy - y)
            rd.line([(xx, yy), (xx - ln * 0.18, yy - ln)], fill=(220, 230, 255, int(al * (0.35 + 0.65 * k))), width=2)
        im.alpha_composite(rl)
        # toi goc
        vg = Image.new('L', (W, H), 0); vd = ImageDraw.Draw(vg)
        for k in range(10): vd.rectangle([k * 18, k * 26, W - k * 18, H - k * 26], outline=int(150 - k * 15), width=26)
        im.paste((0, 0, 0), (0, 0), vg.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.6)))
        return im

    def phone(t, slide=True, t0=None):
        tt = t - (C1 if t0 is None else t0)
        im = dark.copy().convert('RGBA'); d = ImageDraw.Draw(im)
        pw, ph = 800, 1560; px = (W - pw) // 2; py = (H - ph) // 2 + (int(30 * (1 - ease(tt / 0.6))) if slide else 0)
        d.rounded_rectangle([px - 14, py - 14, px + pw + 14, py + ph + 14], 90, fill=(18, 18, 22))
        d.rounded_rectangle([px, py, px + pw, py + ph], 78, fill=(12, 12, 16))
        # thanh tren
        d.rounded_rectangle([px + pw // 2 - 90, py + 24, px + pw // 2 + 90, py + 64], 20, fill=(0, 0, 0))
        hy = py + 110
        d.ellipse([px + 40, hy, px + 120, hy + 80], fill=(70, 80, 100))
        d.text((px + 80 - d.textlength(contact[:1], font=fNm) / 2, hy + 12), contact[:1], font=fNm, fill=(230, 230, 240))
        d.text((px + 140, hy + 4), contact, font=fNm, fill=(240, 240, 245))
        d.text((px + 140, hy + 54), 'Hoạt động 1 phút trước', font=fSt, fill=(140, 140, 155))
        d.line([(px + 30, hy + 104), (px + pw - 30, hy + 104)], fill=(40, 40, 48), width=2)
        # tin nhan
        y = hy + 140; maxw = int(pw * 0.66)
        shown = min(n_msg, int(max(0.0, tt - 0.5) / 0.95) + 1) if tt > 0.5 else 0
        blocks = []
        for i in range(shown):
            m = chat[i]; me = bool(m.get('me'))
            lines = wrap(d, m.get('t', ''), fMsg, maxw - 48)
            bh = len(lines) * 58 + 38; bw = max(d.textlength(l, font=fMsg) for l in lines) + 48
            blocks.append((me, lines, bw, bh, i))
        tot = sum(b[3] + 18 for b in blocks) + (90 if shown < n_msg else 50)
        y = py + ph - 130 - tot  # neo tin nhan ve phia duoi nhu app that
        for me, lines, bw, bh, i in blocks:
            age = tt - 0.5 - i * 0.95; q = ease(age / 0.25)
            x = px + pw - 36 - bw if me else px + 36
            if y + bh > hy + 120:
                col = (0, 122, 255) if me else (44, 44, 52)
                d.rounded_rectangle([x, y + 10 * (1 - q), x + bw, y + bh + 10 * (1 - q)], 34, fill=col)
                for k, l in enumerate(lines): d.text((x + 24, y + 16 + k * 58 + 10 * (1 - q)), l, font=fMsg, fill=(255, 255, 255))
            y += bh + 18
        # dang soan tin / da xem
        if shown < n_msg and tt > 0.2 and not chat[shown].get('me'):
            bx, by = px + 36, min(y, py + ph - 130)
            d.rounded_rectangle([bx, by, bx + 130, by + 70], 34, fill=(44, 44, 52))
            for k in range(3):
                a = 0.5 + 0.5 * math.sin(tt * 9 - k * 0.9)
                d.ellipse([bx + 28 + k * 30, by + 27, bx + 44 + k * 30, by + 43], fill=(int(120 + 100 * a),) * 3)
        if shown == n_msg and n_msg and chat[-1].get('me') and tt - 0.5 - (n_msg - 1) * 0.95 > 0.9:
            s = 'Đã xem'; d.text((px + pw - 36 - d.textlength(s, font=fSt), min(y, py + ph - 120)), s, font=fSt, fill=(150, 150, 165))
        # o nhap
        d.rounded_rectangle([px + 30, py + ph - 110, px + pw - 30, py + ph - 40], 35, fill=(30, 30, 36))
        d.text((px + 60, py + ph - 94), 'Nhắn tin...', font=fSt, fill=(110, 110, 120))
        # giot nuoc tren kinh
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
        for gx, gy, r in gdrops:
            cx, cy = px + gx * pw, py + gy * ph
            gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 210, 230, 38), outline=(230, 235, 255, 70), width=2)
            gd.ellipse([cx - r * 0.4, cy - r * 0.6, cx - r * 0.1, cy - r * 0.3], fill=(255, 255, 255, 90))
        im.alpha_composite(gl)
        return im

    quad, gm = green_quad(photo)
    if quad and spec.get('mode', 'ots') == 'ots':
        return main_ots(photo, quad, phone, layers, chat, fOv, fH, raw, p)

    for fi in range(int(D * FPS)):
        t = fi / FPS
        if t < C1:
            im = street(t, 1.0, 1.08, 0, C1)
            if t > C1 - 0.4: im = Image.blend(im, phone(C1), ease((t - (C1 - 0.4)) / 0.4))
        elif t < C2:
            im = phone(t)
            if t > C2 - 0.4: im = Image.blend(im, street(t, 1.12, 1.04, C2, D), ease((t - (C2 - 0.4)) / 0.4))
        else:
            im = street(t, 1.12, 1.04, C2, D)
            d = ImageDraw.Draw(im)
            ov = (spec.get('overlay') or '').strip()
            if ov:
                q = ease((t - C2 - 0.3) / 0.8)
                fo = fOv
                while max(d.textlength(l, font=fo) for l in ov.split('\n')) > W - 160 and fo.size > 40: fo = font(fo.size - 4)
                lines = wrap(d, ov, fo, W - 160)
                y0 = int(H * 0.40 - len(lines) * 44)
                layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
                for k, l in enumerate(lines):
                    ld.text(((W - ld.textlength(l, font=fo)) / 2, y0 + k * int(fo.size * 1.42)), l, font=fo, fill=(255, 255, 255, int(255 * q)), stroke_width=3, stroke_fill=(0, 0, 0, int(200 * q)))
                im.alpha_composite(layer)
            hd = spec.get('handle')
            if hd:
                d = ImageDraw.Draw(im); s = '@' + hd
                d.text(((W - d.textlength(s, font=fH)) / 2, H - 260), s, font=fH, fill=(230, 230, 235))
        if t > D - 0.6:
            im = Image.blend(im.convert('RGBA'), Image.new('RGBA', (W, H), (0, 0, 0, 255)), ease((t - (D - 0.6)) / 0.6))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait()
    finish(D)
    print('ok', round(D, 2))


def finish(D):
    raw = os.path.join(OUT, 'v_tmp.mp4')
    mus = pick_music()
    # mua nen nhe tu tao (khong ban quyen)
    rain = os.path.join(OUT, 'rain.wav')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'anoisesrc=d={D:.2f}:c=pink:a=0.25', '-af', 'highpass=f=900,lowpass=f=7000', '-ar', '44100', '-ac', '2', rain])
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    fc = f'[1:a]volume=0.95,afade=t=in:d=0.6,afade=t=out:st={D - 1.2:.2f}:d=1.2[m];[2:a]volume=0.10[r];[m][r]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-15:TP=-1.5[a]'
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-stream_loop', '-1', '-i', mus, '-i', rain, '-filter_complex', fc,
                           '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    print('nhac', os.path.basename(mus))


def float_chat(im, tt, chat, end, left=True):
    """Tin nhan phong to noi o nua tren khung (doc duoc tren dien thoai nho), hien dan theo dong thoi gian."""
    f = font(48, 'Medium'); d0 = ImageDraw.Draw(im)
    shown = min(len(chat), int(max(0.0, tt - 0.5) / 0.95) + 1) if tt > 0.5 else 0
    fade = 1.0 - ease((tt - end) / 0.6) if tt > end else 1.0
    items = []
    for i in range(max(0, shown - 4), shown):
        m = chat[i]; lines = wrap(d0, m['t'], f, 560)
        bw = max(d0.textlength(l, font=f) for l in lines) + 56; bh = len(lines) * 60 + 40
        items.append((m.get('me'), lines, bw, bh, i))
    y = 250
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for me, lines, bw, bh, i in items:
        age = tt - 0.5 - i * 0.95; q = ease(age / 0.3) * fade
        cx0, cx1 = (50, int(W * 0.66)) if left else (int(W * 0.34), W - 50)
        x = cx1 - bw if me else cx0
        col = (0, 122, 255, int(225 * q)) if me else (40, 40, 48, int(215 * q))
        ld.rounded_rectangle([x, y + 14 * (1 - q), x + bw, y + bh + 14 * (1 - q)], 36, fill=col)
        for k, l in enumerate(lines):
            ld.text((x + 28, y + 18 + k * 60 + 14 * (1 - q)), l, font=f, fill=(255, 255, 255, int(255 * q)))
        y += bh + 22
    if shown < len(chat) and not chat[shown].get('me') and tt > 0.2:
        bx = 50 if left else int(W * 0.34)
        ld.rounded_rectangle([bx, y, bx + 140, y + 76], 36, fill=(40, 40, 48, int(215 * fade)))
        for k in range(3):
            a = 0.5 + 0.5 * math.sin(tt * 9 - k * 0.9)
            ld.ellipse([bx + 32 + k * 32, y + 29, bx + 50 + k * 32, y + 47], fill=(int(120 + 100 * a),) * 3 + (int(255 * fade),))
    im.alpha_composite(layer)
    return im


def main_ots(photo, quad, phone, layers, chat, fOv, fH, raw, p):
    """1 canh: camera sau lung cheo, man hinh dien thoai (vung xanh) ghep tin nhan, day may vao man hinh roi lui ra."""
    import numpy as np
    S = 2
    big = photo.resize((W * S, H * S), Image.LANCZOS)
    a = np.asarray(big).astype(int); gm2 = (a[..., 1] - np.maximum(a[..., 0], a[..., 2]) > 35)
    a[gm2] = (16, 16, 20)
    # khu anh sang xanh hat len mat/tay: chi trong vung quanh dien thoai (rong gap ~3 lan)
    qx = [x * S for x, _ in quad]; qy = [y * S for _, y in quad]
    cw_ = (max(qx) - min(qx)); ch_ = (max(qy) - min(qy))
    X0_, X1_ = int(max(0, min(qx) - 2.2 * cw_)), int(min(W * S, max(qx) + 2.8 * cw_)); Y0_, Y1_ = int(max(0, min(qy) - 3.2 * ch_)), int(min(H * S, max(qy) + 1.5 * ch_))
    sub = a[Y0_:Y1_, X0_:X1_]; r_, g_, b_ = sub[..., 0], sub[..., 1], sub[..., 2]
    lim = (r_ + b_) // 2 + np.abs(r_ - b_) // 4
    sub[..., 1] = np.where(g_ > lim, lim + (g_ - lim) // 5, g_)
    a[Y0_:Y1_, X0_:X1_] = sub
    big = Image.fromarray(np.clip(a, 0, 255).astype('uint8'))
    q = [(x * S, y * S) for x, y in quad]
    xs = [x for x, _ in q]; ys = [y for _, y in q]
    x0, y0, x1, y1 = int(min(xs)) - 4, int(min(ys)) - 4, int(max(xs)) + 5, int(max(ys)) + 5
    bw, bh = x1 - x0, y1 - y0
    pm = Image.new('L', (bw, bh), 0); ImageDraw.Draw(pm).polygon([(x - x0, y - y0) for x, y in q], fill=255, outline=255, width=10)
    pm = pm.filter(ImageFilter.GaussianBlur(1.2))
    SW, SH = 800, 1560; sx, sy = (W - SW) // 2, (H - SH) // 2
    co = persp_coeffs([(x - x0, y - y0) for x, y in q], [(0, 0), (SW, 0), (SW, SH), (0, SH)])
    n = len(chat); CS = 0.6
    C2 = CS + 0.5 + 0.95 * n + 2.2
    D = max(DUR, C2 + 4.2)
    pcx = sum(xs) / 4 / (W * S); pcy = sum(ys) / 4 / (H * S)
    qw = (max(xs) - min(xs)) / S; qh = (max(ys) - min(ys)) / S
    zmax = float(spec.get('zmax', max(1.25, min(1.7, 0.45 * W / max(qw, 1)))))
    # tam khung: giua dien thoai va mat co gai, de luon thay ca nguoi lan man hinh
    left_side = pcx < 0.5
    pcx = 0.6 * pcx + 0.4 * 0.5; pcy = 0.6 * pcy + 0.4 * 0.45
    print('quad', quad, 'zmax', round(zmax, 2))

    def cam(t):
        if t < 1.2: return 1.0 + 0.03 * t / 1.2, 0.5, 0.5
        if t < 3.4:
            k = ease((t - 1.2) / 2.2); return 1.03 + (zmax - 1.03) * k, 0.5 + (pcx - 0.5) * k, 0.5 + (pcy - 0.5) * k
        if t < C2: return zmax * (1 + 0.02 * (t - 3.4) / max(0.1, C2 - 3.4)), pcx, pcy
        k = ease((t - C2) / 1.4); return zmax * 1.02 + (1.06 - zmax * 1.02) * k, pcx + (0.5 - pcx) * k, pcy + (0.5 - pcy) * k

    for fi in range(int(D * FPS)):
        t = fi / FPS
        scr = phone(t, slide=False, t0=CS).crop((sx, sy, sx + SW, sy + SH)).convert('RGB')
        warped = scr.transform((bw, bh), Image.PERSPECTIVE, co, Image.BICUBIC)
        fr = big.copy(); fr.paste(warped, (x0, y0), pm)
        z, cx, cy = cam(t)
        cw, ch = W * S / z, H * S / z
        X0 = min(max(W * S * cx - cw / 2, 0), W * S - cw); Y0 = min(max(H * S * cy - ch / 2, 0), H * S - ch)
        im = fr.crop((int(X0), int(Y0), int(X0 + cw), int(Y0 + ch))).resize((W, H), Image.BILINEAR).convert('RGBA')
        im = layers(im, t, 0.6)
        if CS + 0.3 < t < C2 + 0.6:
            im = float_chat(im, t - CS, chat, C2 - CS, left_side)
        if t >= C2 + 0.8:
            ov = (spec.get('overlay') or '').strip()
            if ov:
                d = ImageDraw.Draw(im); a = ease((t - C2 - 0.8) / 0.8); fo = fOv
                while max(d.textlength(l, font=fo) for l in ov.split('\n')) > W - 160 and fo.size > 40: fo = font(fo.size - 4)
                lines = wrap(d, ov, fo, W - 160); y0_ = int(H * 0.30 - len(lines) * 44)
                layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
                ld.rectangle([0, y0_ - 80, W, y0_ + len(lines) * int(fo.size * 1.42) + 80], fill=(0, 0, 0, int(90 * a)))
                layer = layer.filter(ImageFilter.GaussianBlur(40)); ld = ImageDraw.Draw(layer)
                for k, l in enumerate(lines):
                    ld.text(((W - ld.textlength(l, font=fo)) / 2, y0_ + k * int(fo.size * 1.42)), l, font=fo, fill=(255, 255, 255, int(255 * a)), stroke_width=3, stroke_fill=(0, 0, 0, int(200 * a)))
                im.alpha_composite(layer)
            hd = spec.get('handle')
            if hd:
                d = ImageDraw.Draw(im); s_ = '@' + hd
                d.text(((W - d.textlength(s_, font=fH)) / 2, H - 260), s_, font=fH, fill=(230, 230, 235))
        if t > D - 0.6:
            im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), ease((t - (D - 0.6)) / 0.6))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait()
    finish(D)
    print('ok ots', round(D, 2))


if __name__ == '__main__':
    main()
