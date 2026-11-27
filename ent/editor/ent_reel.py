#!/usr/bin/env python3
"""AVF ent reel: anh luot chuyen dong (Ken Burns) + chu + nhac nen -> out.mp4 1080x1920.
SPEC_JSON = {"photos":[url..], "hook":"...", "lines":["...",..], "end":"...", "music_url":"...", "accent":"#E8663D"}
"""
import json, os, sys, io, subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, D = 1080, 1920, 30, 3.2
UA = 'AVF-ent-render/1.0 (https://github.com/imtunn2001-hash/avf-editor)'
FONTS = [os.environ.get('ENT_FONT', ''), 'fonts/BeVietnamPro-ExtraBold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']


def font(size):
    for f in FONTS:
        if f and os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=90).read()


def cover(im, w, h):
    iw, ih = im.size
    s = max(w / iw, h / ih)
    im = im.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def wrap(d, text, f, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def overlay(text, path, big=False, accent='#E8663D', y_center=None):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if text:
        size = 92 if big else 66
        while True:
            f = font(size)
            lines = wrap(d, text, f, W - 160)
            if len(lines) <= (5 if big else 4) or size <= 40:
                break
            size -= 4
        lh = int(size * 1.3)
        bh = lh * len(lines) + 70
        yc = y_center if y_center else (int(H * 0.40) if big else int(H * 0.72))
        y0 = yc - bh // 2
        d.rounded_rectangle((50, y0, W - 50, y0 + bh), radius=36, fill=(0, 0, 0, 150))
        if big:
            d.rectangle((50, y0, W - 50, y0 + 12), fill=accent)
        y = y0 + 35
        for ln in lines:
            tw = d.textlength(ln, font=f)
            d.text(((W - tw) / 2 + 3, y + 3), ln, font=f, fill=(0, 0, 0, 160))
            d.text(((W - tw) / 2, y), ln, font=f, fill=(255, 255, 255, 255))
            y += lh
    im.save(path)


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit('ffmpeg loi')


def clip(img, ov, out, i, dur):
    zin = i % 2 == 0
    z = "min(1+0.0009*on,1.12)" if zin else "max(1.12-0.0009*on,1)"
    vf = (f"[0]scale={int(W*1.15)}:{int(H*1.15)},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}[v];"
          f"[v][1]overlay=0:0,fade=t=in:st=0:d=0.3,fade=t=out:st={dur-0.3:.2f}:d=0.3,format=yuv420p")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-framerate', str(FPS), '-t', f'{dur}', '-i', img,
         '-loop', '1', '-framerate', str(FPS), '-t', f'{dur}', '-i', ov, '-filter_complex', vf,
         '-t', f'{dur}', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-an', out])


def vclip(src, ov, out, dur, start):
    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1[v];"
          f"[v][1]overlay=0:0,fade=t=in:st=0:d=0.3,fade=t=out:st={dur-0.3:.2f}:d=0.3,format=yuv420p")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{start:.1f}', '-t', f'{dur}', '-i', src,
         '-loop', '1', '-framerate', str(FPS), '-t', f'{dur}', '-i', ov, '-filter_complex', vf,
         '-t', f'{dur}', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-an', out])


def main():
    spec = json.loads(os.environ.get('SPEC_JSON') or sys.argv[1])
    os.makedirs('work', exist_ok=True)
    os.makedirs('out', exist_ok=True)
    accent = spec.get('accent', '#E8663D')
    imgs = []
    for i, u in enumerate(spec.get('photos', [])[:7]):
        try:
            data = open(u, 'rb').read() if os.path.exists(u) else get(u)
            im = cover(Image.open(io.BytesIO(data)).convert('RGB'), W, H)
            p = f'work/p{i}.jpg'
            im.save(p, quality=92)
            imgs.append(p)
        except Exception as e:
            print('bo anh', u, e)
    vids = []
    for i, u in enumerate(spec.get('videos', [])[:6]):
        try:
            p = f'work/v{i}.media'
            open(p, 'wb').write(open(u, 'rb').read() if os.path.exists(u) else get(u))
            du = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip() or 0)
            if du >= D + 0.5:
                vids.append((p, min(max(0.5, du * 0.3), du - D - 0.2)))
        except Exception as e:
            print('bo video', u, e)
    media = [('v', v) for v in vids] + [('i', p) for p in imgs]
    if len(media) < 3:
        raise SystemExit('thieu anh/video')
    lines = spec.get('lines', [])
    clips = []
    for i, (kind, m) in enumerate(media[:6]):
        text = spec.get('hook', '') if i == 0 else (lines[i - 1] if i - 1 < len(lines) else '')
        ov = f'work/o{i}.png'
        overlay(text, ov, big=(i == 0), accent=accent)
        c = f'work/c{i}.mp4'
        dur = D + (0.6 if i == 0 else 0)
        if kind == 'v':
            vclip(m[0], ov, c, dur, m[1])
        else:
            clip(m, ov, c, i, dur)
        clips.append(c)
    # khung ket
    if spec.get('end'):
        ov = 'work/oe.png'
        overlay(spec['end'], ov, big=True, accent=accent, y_center=int(H * 0.5))
        c = 'work/ce.mp4'
        clip(imgs[0], ov, c, 1, 2.4) if imgs else vclip(vids[0][0], ov, c, 2.4, vids[0][1])
        clips.append(c)
    with open('work/list.txt', 'w') as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'work/list.txt', '-c', 'copy', 'work/v.mp4'])
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'work/v.mp4'], capture_output=True, text=True).stdout.strip())
    music = None
    if spec.get('music_url'):
        try:
            open('work/m.audio', 'wb').write(get(spec['music_url']))
            music = 'work/m.audio'
        except Exception as e:
            print('bo nhac', e)
    if music:
        af = f"[1:a]atrim=start={float(spec.get('music_start', 0)):.1f},asetpts=PTS-STARTPTS,atrim=0:{dur:.2f},afade=t=in:d=1,afade=t=out:st={max(0, dur-1.8):.2f}:d=1.8,volume=0.8[a]"
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'work/v.mp4', '-i', music, '-filter_complex', af, '-map', '0:v', '-map', '[a]',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{dur:.2f}', '-movflags', '+faststart', 'out/out.mp4'])
    else:
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'work/v.mp4', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
             '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-t', f'{dur:.2f}', '-movflags', '+faststart', 'out/out.mp4'])
    print('xong', dur, 'giay', len(imgs), 'anh', 'nhac' if music else 'khong nhac')


if __name__ == '__main__':
    main()
