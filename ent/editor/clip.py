# Cat 1 video ke chuyen dai (khung vuong) thanh 2-3 Reels doc 9:16 ~58s.
# Dau vao SPEC_JSON: {"video_url": "...", "title": "cau hook/tieu de", "label": "Ten loat - Tap N", "n": 3, "dur": 58}
# Dau ra: out/clip1.mp4 ... out/clipN.mp4
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = json.loads(os.environ.get('SPEC_JSON') or open(sys.argv[1]).read())
N = max(1, min(3, int(spec.get('n', 3))))
DUR = float(spec.get('dur', 58))
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
SRC = '/tmp/clip_src.mp4'
subprocess.run(['curl', '-fsSL', '--retry', '3', '--max-time', '600', '-o', SRC, spec['video_url']], check=True)


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return float(r.stdout.strip())


def dims(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0:s=x', path], capture_output=True, text=True)
    w, h = r.stdout.strip().split('x')[:2]
    return int(w), int(h)


T = probe(SRC)
SW, SH = dims(SRC)
VERTICAL = SH > SW * 1.2  # video goc da la khung doc 9:16 -> giu nguyen full man hinh, khong lot khung
# Tim khoang lang (ngat cau) de cat dung cuoi cau, khong cat giua chu
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', SRC, '-af', 'silencedetect=noise=-32dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True)
sil = []  # (bat dau lang, het lang)
cur = None
for line in r.stderr.splitlines():
    m = re.search(r'silence_start: ([\d.]+)', line)
    if m: cur = float(m.group(1))
    m = re.search(r'silence_end: ([\d.]+)', line)
    if m and cur is not None: sil.append((cur, float(m.group(1)))); cur = None


def snap_start(t):
    c = [e for s, e in sil if t - 6 <= e <= t + 8]
    return min(c, key=lambda e: abs(e - t)) if c else t


def snap_end(st):
    c = [s for s, e in sil if st + DUR - 18 <= s <= st + DUR]
    return max(c) + 0.15 if c else min(st + DUR, T)


plan = []
targets = [0.0, 0.38 * T, 0.68 * T][:N]
for k, tg in enumerate(targets):
    st = 0.0 if k == 0 else snap_start(tg)
    if plan and st < plan[-1][1]: st = snap_start(plan[-1][1] + 1)  # khong de 2 clip trung doan
    if plan and st < plan[-1][1]: st = plan[-1][1]
    en = min(snap_end(st), T)
    if en - st < 20: continue
    plan.append((st, en))
print('plan', T, plan, flush=True)


def font(sz, w='ExtraBold'):
    for f in [os.path.join(ROOT, 'fonts', 'BeVietnamPro-' + w + '.ttf'), '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for w in str(text).split():
        tt = (cur + ' ' + w).strip()
        if d.textlength(tt, font=f) <= maxw: cur = tt
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def frame_png(k, total, path):
    W, H = 1080, 1920
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    label = str(spec.get('label') or '').upper()
    if label:
        f0 = font(34); pw = d.textlength(label, font=f0) + 56
        d.rounded_rectangle(((W - pw) / 2, 120, (W + pw) / 2, 184), 32, fill=(214, 40, 40, 255))
        d.text(((W - pw) / 2 + 28, 130), label, font=f0, fill=(255, 255, 255, 255))
    title = str(spec.get('title') or '')
    if total > 1 and k > 0: title = 'PHẦN ' + str(k + 1) + ': ' + title
    f1 = font(60); L = wrap(d, title, f1, 980)
    if len(L) > 3: f1 = font(52); L = wrap(d, title, f1, 990)
    if len(L) > 4: L = L[:4]; L[3] = L[3].rstrip(' ,.:') + '…'
    step = 76 if len(L) <= 3 else 66; y = 214
    for ln in L:
        tw = d.textlength(ln, font=f1)
        d.text(((W - tw) / 2, y), ln, font=f1, fill=(255, 214, 64, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255)); y += step
    f2 = font(40); foot = 'XEM TRỌN TẬP TRÊN PAGE • MỖI TỐI 19:00'
    tw = d.textlength(foot, font=f2)
    d.rounded_rectangle(((W - tw) / 2 - 30, 1640, (W + tw) / 2 + 30, 1720), 40, fill=(255, 255, 255, 235))
    d.text(((W - tw) / 2, 1655), foot, font=f2, fill=(20, 20, 20, 255))
    im.save(path)


def band_png(k, total, path):
    # Video goc da doc: chi 1 dai nho tren cung (khong che chu/hinh cua video), khong lap lai tieu de
    W, H = 1080, 1920
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    txt = ('PHẦN %d/%d · ' % (k + 1, total) if total > 1 else '') + 'XEM TRỌN TẬP TRÊN PAGE 19:00'
    f = font(36); tw = d.textlength(txt, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 28, 40, (W + tw) / 2 + 28, 108), 34, fill=(214, 40, 40, 235))
    d.text(((W - tw) / 2, 52), txt, font=f, fill=(255, 255, 255, 255))
    im.save(path)


for k, (st, en) in enumerate(plan):
    png = '/tmp/clip_frame_%d.png' % k
    out = os.path.join(OUT, 'clip%d.mp4' % (k + 1)); d = en - st
    if VERTICAL:
        band_png(k, len(plan), png)
        fil = ('[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v0];'
               '[v0][1:v]overlay=0:0,format=yuv420p,fade=t=out:st=%.2f:d=0.4[v];'
               '[0:a]afade=t=out:st=%.2f:d=0.4[a]') % (max(0, d - 0.4), max(0, d - 0.4))
    else:
        frame_png(k, len(plan), png)
        # Video vuong: phong to het chieu ngang, dat giua man hinh
        fil = ('[0:v]scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];'
               'color=c=0x0d0d12:s=1080x1920:d=%.2f[bg];[bg][v0]overlay=0:520[b1];[b1][1:v]overlay=0:0,format=yuv420p,fade=t=out:st=%.2f:d=0.4[v];'
               '[0:a]afade=t=out:st=%.2f:d=0.4[a]') % (d, max(0, d - 0.4), max(0, d - 0.4))
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', '%.2f' % st, '-t', '%.2f' % d, '-i', SRC, '-loop', '1', '-t', '%.2f' % d, '-i', png,
                    '-filter_complex', fil, '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], check=True)
    print('ok', out, round(d, 1), flush=True)
json.dump([{'file': 'clip%d.mp4' % (k + 1), 'start': round(s, 2), 'dur': round(e - s, 2)} for k, (s, e) in enumerate(plan)], open(os.path.join(OUT, 'clips.json'), 'w'))
