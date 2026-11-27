#!/usr/bin/env python3
"""AVF MC V2: video MC kieu 'tiem vang' - 1 giong TTS duy nhat, phu de tu khoa, punch-in.
SPEC_JSON = {
  "lines": [ {"wav": "tmp/job/l0.wav", "caps": [{"t": "*VANG*|DANG CHOI TRO GI?", "pos": "mid"}, ...]}, ...],
  "segments": [ {"clip": "tmp/job/1.mp4", "lines": [0, 1], "zoom": 1.0}, ...],
  "punch": [[1.1, 2.2, 1.45]],   # [tu giay, den giay, he so] tren timeline cuoi
  "gap": 0.06,                  # nghi giua cac cau (giay)
  "sparkle": true
}
Chu: '|' = xuong dong, *...* = to mau vang.
"""
import json, os, re, sys, subprocess, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONTS = [os.environ.get('ENT_FONT', ''), 'fonts/BeVietnamPro-ExtraBold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
YEL = (255, 212, 0, 255)


def font(size):
    for f in FONTS:
        if f and os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def run(a, check=True):
    print('$', ' '.join(a)[:400], flush=True)
    r = subprocess.run(a, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(r.stderr[-3000:], flush=True)
        raise SystemExit(f'loi lenh: {a[0]} ({r.returncode})')
    return r


def dur(p):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p])
    return float(r.stdout.strip() or 0)


def has_audio(p):
    return bool(run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', p]).stdout.strip())


def speech_bounds(p, total):
    """Doan MC dang noi trong clip Veo (de khop mieng voi giong TTS)."""
    if not has_audio(p):
        return 0.15, total - 0.3
    r = run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'silencedetect=n=-32dB:d=0.25', '-f', 'null', '-'], check=False)
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    s, e = 0.0, total
    if st and st[0] < 0.05 and en:
        s = en[0]
    if st and st[-1] > s + 1.0 and (len(en) < len(st) or en[-1] >= total - 0.05):
        e = st[-1]
    if e - s < 2.0:
        s, e = 0.0, total
    return max(0.0, s - 0.05), min(total, e + 0.1)


def star(d, cx, cy, r, fill):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.22
        import math
        a = math.pi / 4 * k - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def sparkle_png(path, source=''):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if source:
        f = font(26)
        tw = d.textlength(source, font=f)
        d.text(((W - tw) / 2, H - 92), source, font=f, fill=(255, 255, 255, 235), stroke_width=3, stroke_fill=(0, 0, 0, 170))
    random.seed(7)
    for (x, y, r) in [(70, 300, 16), (1010, 520, 12), (60, 1500, 13), (1020, 1300, 18), (980, 1780, 11)]:
        star(d, x, y, r, (255, 255, 255, 200))
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(path)


def cap_png(path, text, pos='mid'):
    """Phu de tu khoa: chu IN HOA dam, vien den, chu *...* mau vang."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lines = [ln.strip() for ln in text.upper().split('|') if ln.strip()]
    size = 84 if max(len(re.sub(r'\*', '', ln)) for ln in lines) <= 16 else 70
    f = font(size)
    lh = int(size * 1.18)
    y0 = int(H * (0.055 if pos == 'top' else 0.655)) - (lh * len(lines) // 2 if pos != 'top' else 0)
    for i, ln in enumerate(lines):
        segs = re.split(r'(\*[^*]+\*)', ln)
        parts = [(s.strip('*'), YEL if s.startswith('*') else (255, 255, 255, 255)) for s in segs if s]
        tw = sum(d.textlength(t, font=f) for t, _ in parts)
        x = (W - tw) / 2
        y = y0 + i * lh
        for t, col in parts:
            # bong do mem + vien den
            d.text((x + 4, y + 6), t, font=f, fill=(0, 0, 0, 120), stroke_width=7, stroke_fill=(0, 0, 0, 120))
            d.text((x, y), t, font=f, fill=col, stroke_width=7, stroke_fill=(20, 20, 20, 255))
            x += d.textlength(t, font=f)
    img.save(path)


def main():
    spec = json.loads(os.environ.get('SPEC_JSON') or sys.argv[1])
    os.makedirs('work', exist_ok=True)
    os.makedirs('out', exist_ok=True)
    gap = float(spec.get('gap', 0.06))
    L = spec['lines']
    # 1) giong doc: noi cac cau TTS thanh 1 file, tinh moc thoi gian tung cau
    t, marks = 0.0, []
    with open('work/alist.txt', 'w') as fl:
        for i, ln in enumerate(L):
            a = f'work/l{i}.wav'
            run(['ffmpeg', '-y', '-loglevel', 'error', '-i', ln['wav'], '-af',
                 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,aresample=48000',
                 '-ac', '2', a])
            d = dur(a)
            marks.append((t, t + d))
            fl.write(f"file '{os.path.abspath(a)}'\n")
            t += d
            if i < len(L) - 1 and gap > 0:
                g = f'work/g{i}.wav'
                run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', f'{gap:.3f}', g])
                fl.write(f"file '{os.path.abspath(g)}'\n")
                t += gap
    total = t + 0.35
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'work/alist.txt',
         '-af', f'apad=pad_dur=0.35', '-c:a', 'pcm_s16le', 'work/voice.wav'])
    for i, (a, b) in enumerate(marks):
        print(f'cau {i+1}: {a:.2f}-{b:.2f}s', flush=True)
    # 2) hinh: moi doan clip Veo duoc keo gian cho vua cac cau no dam nhan
    segs = spec['segments']
    vparts = []
    for k, sg in enumerate(segs):
        li = sg['lines']
        a = marks[li[0]][0]
        b = marks[li[-1]][1] + (gap if k < len(segs) - 1 else 0.35)
        if k < len(segs) - 1:
            b = marks[segs[k + 1]['lines'][0]][0]
        D = b - a
        src = sg['clip']
        T = dur(src)
        s, e = speech_bounds(src, T)
        if D > e - s:  # cau TTS dai hon: lay them phan cuoi clip thay vi keo cham
            e = min(T, s + D)
        f = max(0.8, min(1.35, D / (e - s)))
        if D / (e - s) > 1.35:
            s = max(0.0, e - D / 1.35)
            f = D / (e - s)
        z = float(sg.get('zoom', 1.0))
        vf = f"trim={s:.3f}:{e:.3f},setpts=(PTS-STARTPTS)*{f:.5f},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1"
        if z > 1.001:
            vf += f",scale={int(W*z)}:{int(H*z)}:flags=lanczos,crop={W}:{H}:{int(W*(z-1)/2)}:{int(H*(z-1)*0.25)}"
        vf += f",fps={FPS},trim=duration={D:.3f}"
        v = f'work/s{k}.mp4'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', v])
        print(f'doan {k+1}: clip {T:.2f}s, lay {s:.2f}-{e:.2f} -> {D:.2f}s (x{f:.2f}) zoom {z}', flush=True)
        vparts.append(v)
    with open('work/vlist.txt', 'w') as fl:
        for v in vparts:
            fl.write(f"file '{os.path.abspath(v)}'\n")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'work/vlist.txt', '-c', 'copy', 'work/vcat.mp4'])
    # 3) punch-in (canh can bat ngo nhu video mau)
    src = 'work/vcat.mp4'
    pun = []
    for p in spec.get('punch', []):
        if isinstance(p, dict):  # {"line": i, "from_end": 0.9, "z": 1.45}
            a0, b0 = marks[p['line']]
            pun.append([max(a0, b0 - float(p.get('from_end', 1.0))), b0 + gap, float(p.get('z', 1.4))])
        else:
            pun.append(p)
    pun = sorted([p for p in pun if p[1] > p[0]])
    if pun:
        cuts, cur = [], 0.0
        for a, b, z in pun:
            if a > cur:
                cuts.append((cur, a, 1.0))
            cuts.append((a, b, float(z)))
            cur = b
        cuts.append((cur, total, 1.0))
        fc = [f"[0:v]split={len(cuts)}" + ''.join(f'[c{i}]' for i in range(len(cuts)))]
        for i, (a, b, z) in enumerate(cuts):
            x = f"[c{i}]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS"
            if z > 1.001:
                cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
                x += f",crop={cw}:{ch}:{(W-cw)//2}:{int(H*0.06)},scale={W}:{H}:flags=lanczos,setsar=1"
            fc.append(x + f"[p{i}]")
        fc.append(''.join(f'[p{i}]' for i in range(len(cuts))) + f"concat=n={len(cuts)}:v=1:a=0[v]")
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-filter_complex', ';'.join(fc), '-map', '[v]',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', 'work/vpun.mp4'])
        src = 'work/vpun.mp4'
    # 4) phu de tu khoa theo dung moc cau + sao lap lanh
    ins, ovs = [], []
    if spec.get('sparkle', True) or spec.get('source'):
        sparkle_png('work/sp.png', spec.get('source', ''))
        ins += ['-loop', '1', '-t', f'{total:.3f}', '-i', 'work/sp.png']
        ovs.append((None, None))
    n = 0
    for i, ln in enumerate(L):
        caps = ln.get('caps') or []
        if not caps:
            continue
        a, b = marks[i]
        if i < len(L) - 1:
            b = marks[i + 1][0]
        else:
            b = total
        step = (b - a) / len(caps)
        for j, c in enumerate(caps):
            p = f'work/cap{n}.png'
            cap_png(p, c['t'], c.get('pos', 'mid'))
            ca, cb = a + j * step, a + (j + 1) * step
            ins += ['-loop', '1', '-t', f'{total:.3f}', '-i', p]
            ovs.append((ca, cb))
            n += 1
    fc, last = [], '[0:v]'
    for k, (ca, cb) in enumerate(ovs, start=1):
        if ca is None:
            fc.append(f"{last}[{k}:v]overlay=0:0[o{k}]")
        else:
            # hien chu kieu 'bat len': mo dan 0.08s
            fc.append(f"[{k}:v]format=rgba,fade=in:st={ca:.3f}:d=0.08:alpha=1[f{k}]")
            fc.append(f"{last}[f{k}]overlay=0:0:enable='between(t,{ca:.3f},{cb:.3f})'[o{k}]")
        last = f'[o{k}]'
    na = len(ovs) + 1
    args = ['ffmpeg', '-y', '-loglevel', 'error', '-i', src] + ins + ['-i', 'work/voice.wav']
    if fc:
        args += ['-filter_complex', ';'.join(fc), '-map', last]
    else:
        args += ['-map', '0:v']
    args += ['-map', f'{na}:a', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-t', f'{total:.3f}',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
             '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', 'out/out.mp4']
    run(args)
    print('xong', len(vparts), 'doan,', round(dur('out/out.mp4'), 2), 'giay', flush=True)


if __name__ == '__main__':
    main()
