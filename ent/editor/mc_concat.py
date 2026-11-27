#!/usr/bin/env python3
"""AVF MC: ghep cac clip Veo 8s thanh 1 video hoan chinh.
SPEC_JSON = {
  "clips": ["tmp/job/1.mp4", ...],      # duong dan trong repo (hoac URL)
  "subs": ["cau thoai 1", ...],          # phu de tung clip (tuy chon)
  "title": "GIÁ VÀNG TRƯA 11/11",        # dai tieu de tren cung (tuy chon)
  "source": "Nguồn: bảng giá PNJ 11:50", # dong nho duoi cung (tuy chon)
  "speed": 1.1,                           # tang toc doc doc (1.0 - 1.25)
  "accent": "#D4A017"
}
Dau ra: out/out.mp4 (720x1280, 30fps, am thanh chuan hoa -14 LUFS)
"""
import json, os, sys, subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FONTS = [os.environ.get('ENT_FONT', ''), 'fonts/BeVietnamPro-ExtraBold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']


def font(size):
    for f in FONTS:
        if f and os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def overlay(path, title='', sub='', source='', accent='#D4A017'):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if title:
        f = font(40)
        tw = d.textlength(title, font=f)
        x0, y0 = (W - tw) / 2 - 28, 70
        d.rounded_rectangle([x0, y0, x0 + tw + 56, y0 + 72], 18, fill=accent)
        d.text((x0 + 28, y0 + 12), title, font=f, fill='#1A1A1A')
    if sub:
        f = font(34)
        lines = wrap(d, sub, f, W - 120)[:3]
        lh = 46
        bh = lh * len(lines) + 30
        y0 = H - 250 - bh
        d.rounded_rectangle([40, y0, W - 40, y0 + bh], 20, fill=(0, 0, 0, 165))
        y = y0 + 15
        for ln in lines:
            tw = d.textlength(ln, font=f)
            d.text(((W - tw) / 2, y), ln, font=f, fill='white')
            y += lh
    if source:
        f = font(22)
        tw = d.textlength(source, font=f)
        d.text(((W - tw) / 2, H - 70), source, font=f, fill=(255, 255, 255, 210))
    img.save(path)


def run(a):
    print(' '.join(a))
    subprocess.run(a, check=True)


def main():
    spec = json.loads(os.environ.get('SPEC_JSON') or sys.argv[1])
    os.makedirs('work', exist_ok=True)
    os.makedirs('out', exist_ok=True)
    sp = max(1.0, min(1.25, float(spec.get('speed', 1.1))))
    subs = spec.get('subs', [])
    parts = []
    for i, c in enumerate(spec['clips']):
        src = c if os.path.exists(c) else None
        if not src:
            src = f'work/in{i}.mp4'
            open(src, 'wb').write(urllib.request.urlopen(c, timeout=120).read())
        ov = f'work/ov{i}.png'
        overlay(ov, spec.get('title', ''), subs[i] if i < len(subs) else '', spec.get('source', ''), spec.get('accent', '#D4A017'))
        p = f'work/p{i}.mp4'
        fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,"
              f"setpts=PTS/{sp},fps=30[v];[v][1:v]overlay=0:0[vo];"
              f"[0:a]atempo={sp},aresample=48000,aformat=channel_layouts=stereo[ao]")
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-i', ov, '-filter_complex', fc,
             '-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
             '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', p])
        parts.append(p)
    with open('work/list.txt', 'w') as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'work/list.txt',
         '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k',
         '-movflags', '+faststart', 'out/out.mp4'])
    print('xong', len(parts), 'clip, toc do', sp)


if __name__ == '__main__':
    main()
