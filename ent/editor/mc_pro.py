#!/usr/bin/env python3
"""AVF MC PRO: dung video MC tu cac clip Veo 8s cho dep, lien mach.
SPEC_JSON = {
  "clips": ["tmp/job/1.mp4", ...], "subs": ["...", ...],
  "title": "...", "source": "...", "accent": "#D4A017",
  "speed": 1.15,          # tang toc
  "unify_voice": true,    # dong nhat giong theo clip 1 (OpenVoice, neu cai duoc)
  "punch": true,          # xen ke canh rong / canh can nhu 2 may quay
  "xfade": 0.25           # chuyen canh mem (giay)
}
"""
import json, os, re, sys, subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 30
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
        f = font(38)
        tw = d.textlength(title, font=f)
        x0, y0 = (W - tw) / 2 - 26, 64
        d.rounded_rectangle([x0, y0, x0 + tw + 52, y0 + 66], 16, fill=accent)
        d.text((x0 + 26, y0 + 11), title, font=f, fill='#1A1A1A')
    if sub:
        f = font(36)
        lines = wrap(d, sub, f, W - 110)[:3]
        lh = 48
        bh = lh * len(lines) + 28
        y0 = H - 230 - bh
        d.rounded_rectangle([36, y0, W - 36, y0 + bh], 18, fill=(0, 0, 0, 175))
        d.rectangle([36, y0, 44, y0 + bh], fill=accent)
        y = y0 + 14
        for ln in lines:
            tw = d.textlength(ln, font=f)
            d.text(((W - tw) / 2, y), ln, font=f, fill='white')
            y += lh
    if source:
        f = font(21)
        tw = d.textlength(source, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 12, H - 78, (W + tw) / 2 + 12, H - 46], 10, fill=(0, 0, 0, 120))
        d.text(((W - tw) / 2, H - 75), source, font=f, fill=(255, 255, 255, 230))
    img.save(path)


def run(a, check=True):
    print('$', ' '.join(a)[:300], flush=True)
    return subprocess.run(a, check=check, capture_output=True, text=True)


def dur(p):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p])
    return float(r.stdout.strip() or 0)


def speech_bounds(p, total):
    """Tim doan co tieng noi: bo khoang lang dau/cuoi."""
    r = run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'silencedetect=n=-38dB:d=0.18', '-f', 'null', '-'], check=False)
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    s, e = 0.0, total
    if starts and starts[0] < 0.05 and ends:
        s = ends[0]
    if starts and starts[-1] > s + 1.0 and (len(ends) < len(starts) or ends[-1] >= total - 0.05):
        e = starts[-1]
    s = max(0.0, s - 0.06)
    e = min(total, e + 0.22)
    if e - s < 1.5:
        s, e = 0.0, total
    return s, e


def unify_voices(wavs):
    """Doi am sac giong cac clip 2..n ve giong clip 1 (OpenVoice V2, MIT)."""
    try:
        import torch
        sys.path.insert(0, 'OpenVoice')
        import types
        if 'wavmark' not in sys.modules:  # khong can watermark -> module gia
            fake = types.ModuleType('wavmark')
            class _M:
                def to(self, *a, **k): return self
            fake.load_model = lambda *a, **k: _M()
            sys.modules['wavmark'] = fake
        from openvoice.api import ToneColorConverter
        ck = 'ov2/converter'
        conv = ToneColorConverter(f'{ck}/config.json', device='cpu')
        conv.watermark_model = None
        conv.load_ckpt(f'{ck}/checkpoint.pth')
        tgt = conv.extract_se([wavs[0]], se_save_path='work/se_ref.pth')
        out = [wavs[0]]
        for i, w in enumerate(wavs[1:], 1):
            src = conv.extract_se([w], se_save_path=f'work/se_{i}.pth')
            o = f'work/u{i}.wav'
            conv.convert(audio_src_path=w, src_se=src, tgt_se=tgt, output_path=o, tau=0.3)
            out.append(o)
        print('dong nhat giong: OK', flush=True)
        return out
    except Exception as e:
        print('dong nhat giong: BO QUA ->', repr(e)[:300], flush=True)
        return wavs


def main():
    spec = json.loads(os.environ.get('SPEC_JSON') or sys.argv[1])
    os.makedirs('work', exist_ok=True)
    os.makedirs('out', exist_ok=True)
    sp = max(1.0, min(1.3, float(spec.get('speed', 1.15))))
    xf = max(0.0, min(0.5, float(spec.get('xfade', 0.25))))
    subs = spec.get('subs', [])
    acc = spec.get('accent', '#D4A017')
    # 1) cat lang + tang toc, tach am thanh
    vids, wavs, keep = [], [], []
    for i, c in enumerate(spec['clips']):
        src = c if os.path.exists(c) else None
        if not src:
            src = f'work/in{i}.mp4'
            open(src, 'wb').write(urllib.request.urlopen(c, timeout=120).read())
        t = dur(src)
        has_a = run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', src]).stdout.strip()
        if not has_a:
            print(f'CANH BAO: clip {i+1} khong co am thanh -> bo qua clip nay', flush=True)
            continue
        s, e = speech_bounds(src, t)
        zoom = spec.get('punch', True) and len(vids) % 2 == 1
        vf = f"trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS,setpts=PTS/{sp}," \
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
        if zoom:
            vf += f",scale={int(W*1.14)}:{int(H*1.14)},crop={W}:{H}:{int(W*0.07)}:{int(H*0.035)}"
        vf += f",fps={FPS}"
        v = f'work/v{i}.mp4'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', v])
        a = f'work/a{i}.wav'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af', f"atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,atempo={sp},aresample=44100", '-ac', '1', a])
        vids.append(v)
        wavs.append(a)
        keep.append(i)
        print(f'clip {i+1}: {t:.2f}s -> giu {s:.2f}-{e:.2f} -> {(e-s)/sp:.2f}s', flush=True)
    # 2) dong nhat giong
    if spec.get('unify_voice', True) and len(wavs) > 1:
        wavs = unify_voices(wavs)
    # 3) ghep tung canh voi chu + am thanh
    parts = []
    for i, (v, a) in enumerate(zip(vids, wavs)):
        k = keep[i]
        ov = f'work/ov{i}.png'
        overlay(ov, spec.get('title', ''), subs[k] if k < len(subs) else '', spec.get('source', ''), acc)
        p = f'work/p{i}.mp4'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', v, '-i', a, '-i', ov, '-filter_complex',
             '[0:v][2:v]overlay=0:0[vo];[1:a]aresample=48000,aformat=channel_layouts=stereo[ao]',
             '-map', '[vo]', '-map', '[ao]', '-shortest', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
             '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', p])
        parts.append(p)
    # 4) chuyen canh mem
    if len(parts) == 1 or xf <= 0:
        with open('work/list.txt', 'w') as f:
            for p in parts:
                f.write(f"file '{os.path.abspath(p)}'\n")
        run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'work/list.txt', '-c', 'copy', 'work/cat.mp4'])
    else:
        ds = [dur(p) for p in parts]
        args = ['ffmpeg', '-y', '-loglevel', 'error']
        for p in parts:
            args += ['-i', p]
        fc, vl, al, off = [], '[0:v]', '[0:a]', 0.0
        for i in range(1, len(parts)):
            off += ds[i - 1] - xf
            fc.append(f'{vl}[{i}:v]xfade=transition=fade:duration={xf}:offset={off:.3f}[vx{i}]')
            fc.append(f'{al}[{i}:a]acrossfade=d={xf}:c1=tri:c2=tri[ax{i}]')
            vl, al = f'[vx{i}]', f'[ax{i}]'
        args += ['-filter_complex', ';'.join(fc), '-map', vl, '-map', al, '-c:v', 'libx264', '-preset', 'veryfast',
                 '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', 'work/cat.mp4']
        run(args)
    # 5) chuan hoa am luong
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'work/cat.mp4', '-c:v', 'copy',
         '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', 'out/out.mp4'])
    print('xong', len(parts), 'canh,', round(dur('out/out.mp4'), 2), 'giay', flush=True)


if __name__ == '__main__':
    main()
