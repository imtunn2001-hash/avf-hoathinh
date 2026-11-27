"""Video nhan dinh vang 9:16 (W55): anh chart + giong doc + phu de lon.
SPEC_JSON: {"image_url","voice_url","srt_url","title","sub","cta"}  -> out/out.mp4
Chart zoom/pan cham ve phia ben phai (vung nen moi + hop lenh cho)."""
import json, math, os, re, subprocess, sys, urllib.request, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)


def fnt(bold, size):
    c = [os.path.join(ROOT, 'fonts', 'BeVietnamPro-ExtraBold.ttf' if bold else 'BeVietnamPro-Medium.ttf'),
         '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf' if bold else '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
    for p in c:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    sys.exit('khong co font')


GOLD = (245, 196, 66); GOLD2 = (255, 226, 130); BG1 = (12, 18, 34); BG2 = (6, 10, 20); WHITE = (255, 255, 255)


def get(url, path):
    if os.path.exists(url):
        return url
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
        if len(ls) < 2: continue
        m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)', ls[1] if '-->' in ls[1] else ls[0])
        if not m: continue
        g = list(map(int, m.groups()))
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000; b2 = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = ' '.join(ls[2:] if '-->' in ls[1] else ls[1:])
        out.append((a, b2, unlex(text)))
    return out


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines


NUM = re.compile(r'^[\d.,%]+$')


def draw_caption(d, y, text, f):
    lines = wrap(d, text, f, W - 140)[:3]
    lh = int(f.size * 1.32)
    box_h = len(lines) * lh + 44
    d.rounded_rectangle([40, y - 22, W - 40, y - 22 + box_h], 30, fill=(0, 0, 0))
    for i, ln in enumerate(lines):
        x = (W - d.textlength(ln, font=f)) / 2
        for wd in ln.split(' '):
            col = GOLD2 if NUM.match(wd.strip('.,')) or wd.upper() in ('SELL', 'BUY', 'LIMIT', 'H4', 'H1', 'FIBO') else WHITE
            d.text((x, y + i * lh), wd, font=f, fill=col, stroke_width=2, stroke_fill=(0, 0, 0))
            x += d.textlength(wd + ' ', font=f)


def main():
    spec = json.loads(os.environ.get('SPEC_JSON') or open(sys.argv[1]).read())
    img = Image.open(get(spec['image_url'], os.path.join(OUT, 'chart.png'))).convert('RGB')
    voice = get(spec['voice_url'], os.path.join(OUT, 'voice.mp3'))
    srt = []
    if spec.get('srt_url'):
        try:
            srt = parse_srt(open(get(spec['srt_url'], os.path.join(OUT, 'voice.srt')), encoding='utf-8').read())
        except Exception as e:
            print('srt loi', e)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', voice]).decode().strip())
    LEAD, TAIL = 0.15, 2.2
    D = dur + LEAD + TAIL
    title = spec.get('title', 'NHẬN ĐỊNH VÀNG'); sub = spec.get('sub', ''); cta = spec.get('cta', 'Theo dõi page để nhận kèo mỗi sáng')
    # chart: vung hien thi 1080 x CH o giua
    CH = 1040; CY = 300
    iw, ih = img.size
    base = max(W / iw, CH / ih)  # phu kin khung
    fT = fnt(True, 58); fS = fnt(False, 40); fC = fnt(True, 60); fE = fnt(True, 76); fK = fnt(True, 40); fL = fnt(True, 42)
    # nen tinh
    g = np.linspace(0, 1, H)[:, None, None]
    bgarr = (np.array(BG1) * (1 - g) + np.array(BG2) * g) * np.ones((1, W, 1))
    BGI = Image.fromarray(bgarr.astype('uint8'), 'RGB')
    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    N = int(D * FPS)
    for i in range(N):
        t = i / FPS
        im = BGI.copy(); d = ImageDraw.Draw(im)
        # zoom tu 1.0 -> 1.35, tam di tu giua -> 72% ben phai
        z = 1.05 + 0.5 * ease(t / max(1.0, dur))
        sc = base * z
        cw, chh = W / sc, CH / sc  # vung cat tren anh goc
        fx = 0.5 + 0.22 * ease(t / max(1.0, dur))
        cx = min(max(iw * fx, cw / 2), iw - cw / 2); cy = min(max(ih * 0.5, chh / 2), ih - chh / 2)
        box = (int(cx - cw / 2), int(cy - chh / 2), int(cx + cw / 2), int(cy + chh / 2))
        im.paste(img.crop(box).resize((W, CH), Image.BILINEAR), (0, CY))
        d.rectangle([0, CY - 4, W, CY], fill=GOLD); d.rectangle([0, CY + CH, W, CY + CH + 4], fill=GOLD)
        # tieu de
        d.text(((W - d.textlength(title, font=fT)) / 2, 120), title, font=fT, fill=GOLD, stroke_width=2, stroke_fill=(0, 0, 0))
        if sub:
            d.text(((W - d.textlength(sub, font=fS)) / 2, 205), sub, font=fS, fill=(210, 220, 240))
        # phu de
        tv = t - LEAD
        cur = next((s for s in srt if s[0] - 0.05 <= tv < s[1] + 0.15), None)
        if cur and t < D - TAIL + 0.3:
            draw_caption(d, CY + CH + 60, cur[2], fC)
        # the keo co dinh phia duoi
        lv = [str(x).replace('→', '-').replace('–', '-') for x in (spec.get('levels') or [])]
        if lv:
            y0 = 1600
            n_ = min(3, len(lv)); y0 = H - 90 - (80 + n_ * 64)
            d.rounded_rectangle([40, y0, W - 40, y0 + 70 + n_ * 64], 30, fill=(18, 30, 58), outline=GOLD, width=3)
            d.text((70, y0 + 16), spec.get('levels_title', 'KÈO CHỜ HÔM NAY'), font=fK, fill=GOLD)
            for k, s_ in enumerate(lv[:3]):
                ff = fL
                while d.textlength(s_, font=ff) > W - 150 and ff.size > 28: ff = fnt(True, ff.size - 2)
                d.text((70, y0 + 72 + k * 64), s_, font=ff, fill=WHITE)
        # ket
        if t >= D - TAIL:
            q = ease((t - (D - TAIL)) / 0.4)
            ov = Image.new('RGB', (W, H), BG2); im = Image.blend(im, ov, 0.93 * q); d = ImageDraw.Draw(im)
            for k, line in enumerate(wrap(d, cta, fE, W - 160)):
                d.text(((W - d.textlength(line, font=fE)) / 2, 820 + k * 100), line, font=fE, fill=GOLD if k == 0 else WHITE)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    # nhac nen nhe tong hop
    sr = 44100; n = int(D * sr); tt = np.arange(n) / sr
    y = np.zeros(n)
    for f0, amp in ((110.0, .05), (164.81, .035), (220.0, .03)):
        y += amp * np.sin(2 * np.pi * f0 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * tt))
    y *= np.minimum(1, tt / 1.0) * np.minimum(1, (D - tt) / 1.5)
    with wave.open(os.path.join(OUT, 'bg.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 0.5 * 32767).astype(np.int16).tobytes())
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', voice, '-i', os.path.join(OUT, 'bg.wav'),
                           '-filter_complex', f'[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)}[v];[2:a]volume=0.25[m];[v][m]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-15:TP=-1.5[a]',
                           '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    print('ok', round(D, 2))


if __name__ == '__main__':
    main()
