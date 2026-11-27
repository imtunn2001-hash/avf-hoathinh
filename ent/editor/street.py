#!/usr/bin/env python3
"""Video 1 anh duong pho chuyen dong + 1 caption dung yen (page giai tri HN/SG).
SPEC_JSON: {"query": "Hanoi street", "caption": "...", "music": "music_b.mp3", "dur": 12,
            "photo_url": "(tuy chon)", "sample_branch": "(tuy chon: day out.mp4 len nhanh nay)"}"""
import json, os, random, subprocess, sys, textwrap, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

spec = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.loads(os.environ['SPEC_JSON'])
ROOT = os.getcwd(); OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
DUR = float(spec.get('dur', 12))
UA = 'AVF-street/1.0 (github imtunn2001-hash)'


def get(url, binary=False, timeout=40):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = r.read()
    return d if binary else json.loads(d.decode())


def pick_photo(query):
    qs = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6, 'gsrlimit': 40,
          'gsrsearch': query + ' filetype:bitmap', 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata',
          'iiurlwidth': 3000, 'iiextmetadatafilter': 'LicenseShortName|Artist'}
    r = get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(qs))
    c = []
    for p in (r.get('query') or {}).get('pages', {}).values():
        ii = (p.get('imageinfo') or [{}])[0]; em = ii.get('extmetadata') or {}
        lic = (em.get('LicenseShortName') or {}).get('value', '')
        w, h = ii.get('width', 0), ii.get('height', 0)
        if not lic.lower().startswith(('cc0', 'public domain', 'pd', 'cc by')): continue
        if w < 1800 or w / max(h, 1) < 1.25: continue
        import re
        art = re.sub('<[^>]+>', '', (em.get('Artist') or {}).get('value', '')).strip()[:60] or 'không rõ tác giả'
        c.append({'url': ii.get('thumburl') or ii['url'], 'lic': lic, 'art': art, 'title': p.get('title', '')})
    if not c: raise SystemExit('khong tim thay anh: ' + query)
    random.shuffle(c)
    return c[0]


def font(sz, w='ExtraBold'):
    fb = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if w == 'ExtraBold' else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    for f in [os.path.join(ROOT, 'fonts', 'BeVietnamPro-' + w + '.ttf'), fb]:
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def caption_layer(text):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sz = 66; f = font(sz)
    lines = []
    for para in str(text).split('\n'):
        words = para.split(); cur = ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if d.textlength(t, font=f) <= 900: cur = t
            else: lines.append(cur); cur = wd
        if cur: lines.append(cur)
    lh = int(sz * 1.32); y = int(H * 0.2)
    for ln in lines:
        tw = d.textlength(ln, font=f); x = (W - tw) / 2
        d.text((x, y), ln, font=f, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0, 255))
        y += lh
    return lay


def pick_music():
    m = spec.get('music', 'auto')
    if m and m != 'auto':
        return os.path.join(ROOT, 'editor', 'wb', m), 0.0
    d = os.path.join(ROOT, 'editor', 'street_music'); city = str(spec.get('city', '')).lower()
    fs = []
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith(('.mp3', '.m4a', '.wav', '.aac', '.ogg')): continue
            low = f.lower()
            if low.startswith(('hn_', 'sg_')) and not low.startswith(city + '_'): continue
            fs.append(os.path.join(d, f))
    if not fs:
        fs = [os.path.join(ROOT, 'editor', 'wb', x) for x in ('music_a.mp3', 'music_b.mp3')]
    f = fs[int(spec.get('rot', 0)) % len(fs)]
    try:
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip())
    except Exception:
        dur = 0
    start = min(45.0, dur * 0.25) if dur > DUR * 3 else 0.0
    return f, start


def mood_layer(text, handle):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sz = 42; f = font(sz, 'Medium'); maxw = 540
    lines = []
    for para in str(text).replace('\\n', '\n').split('\n'):
        para = para.strip()
        if not para: lines.append(''); continue
        cur = ''
        for wd in para.split():
            t = (cur + ' ' + wd).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: lines.append(cur); cur = wd
        if cur: lines.append(cur)
    while lines and not lines[-1]: lines.pop()
    lh = int(sz * 1.3); bw = max([d.textlength(l, font=f) for l in lines if l] + [10])
    x0 = int((W - bw) / 2); total = lh * len(lines); y = int(H * 0.47 - total / 2)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    yy = y
    for ln in lines:
        ds.text((x0 + 2, yy + 3), ln, font=f, fill=(0, 0, 0, 170)); yy += lh
    sh = sh.filter(ImageFilter.GaussianBlur(4)); lay.alpha_composite(sh)
    yy = y
    for ln in lines:
        d.text((x0, yy), ln, font=f, fill=(245, 245, 245, 255)); yy += lh
    if handle:
        fh = font(22, 'Medium'); hw = d.textlength(handle, font=fh)
        d.text((x0 + bw - hw + 40, yy + 40), handle, font=fh, fill=(235, 235, 235, 220))
    return lay


def grade(im):
    from PIL import ImageEnhance
    im = ImageEnhance.Color(im).enhance(0.55)
    im = ImageEnhance.Brightness(im).enhance(0.6)
    im = ImageEnhance.Contrast(im).enhance(0.92)
    tint = Image.new('RGB', im.size, (70, 66, 48))
    return Image.blend(im, tint, 0.12)


def main():
    src = spec.get('photo_url') or ''
    credit = {}
    if not src and not spec.get('photo_git'):
        ph = pick_photo(spec.get('query', 'Hanoi street'))
        src = ph['url']; credit = ph
    raw = os.path.join('/tmp', 'street_src.jpg')
    pg = spec.get('photo_git')
    if pg:
        subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', pg['branch']], check=True)
        raw = os.path.join('/tmp', 'street_src' + os.path.splitext(pg['path'])[1])
        open(raw, 'wb').write(subprocess.run(['git', 'show', 'FETCH_HEAD:' + pg['path']], check=True, capture_output=True).stdout)
    elif src.startswith('/'): raw = src
    else: open(raw, 'wb').write(get(src, binary=True, timeout=90))
    im = Image.open(raw).convert('RGB')
    # dua anh ve chieu cao 1.12*H, giu ti le
    sc = max(H * 1.12 / im.height, W * 1.3 / im.width)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    vign = Image.new('L', (W, H), 0); dv = ImageDraw.Draw(vign)
    dv.ellipse((-W * 0.35, -H * 0.15, W * 1.35, H * 1.15), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new('RGB', (W, H), (0, 0, 0))
    mood = spec.get('style') == 'mood'
    if mood: im = grade(im)
    cap = mood_layer(spec.get('caption', ''), spec.get('handle', '')) if mood else caption_layer(spec.get('caption', ''))
    n = int(DUR * FPS)
    dirn = random.choice([1, -1])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '/tmp/street_v.mp4'], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / max(n - 1, 1); e = t * t * (3 - 2 * t) * 0.85 + t * 0.15  # em dau
        z = 1.0 + 0.07 * t  # zoom cham
        vw, vh = W / z, H / z
        x0 = (im.width - vw) * (e if dirn > 0 else 1 - e)
        y0 = min(max(0.0, (im.height - vh) / 2 - 18 * t), im.height - vh)
        if mood:
            import math
            sec = i / FPS
            x0 = min(max(0.0, x0 + 7 * math.sin(sec * 1.3) + 3 * math.sin(sec * 3.1)), im.width - vw)
            y0 = min(max(0.0, y0 + 6 * math.sin(sec * 1.7 + 1) + 2 * math.sin(sec * 4.3)), im.height - vh)
        fr = im.transform((W, H), Image.AFFINE, (vw / W, 0, x0, 0, vh / H, y0), resample=Image.BILINEAR)
        fr = Image.composite(fr, Image.blend(fr, dark, 0.5 if mood else 0.35), vign)
        fr = fr.convert('RGBA'); fr.alpha_composite(cap)
        ff.stdin.write(fr.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    mus, mstart = pick_music()
    credit['music'] = os.path.basename(mus)
    vf = f"fade=t=in:st=0:d=0.4,fade=t=out:st={DUR - 0.6:.2f}:d=0.6"
    af = f"volume={float(spec.get('music_vol', 0.8))},afade=t=in:d=0.8,afade=t=out:st={DUR - 1.5:.2f}:d=1.5"
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/street_v.mp4', '-stream_loop', '-1', '-ss', f'{mstart:.1f}', '-i', mus, '-t', f'{DUR:.2f}',
                    '-vf', vf, '-af', af, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', os.path.join(OUT, 'out.mp4')], check=True)
    json.dump(credit, open(os.path.join(OUT, 'credit.json'), 'w'), ensure_ascii=False)
    print('ok', credit)
    br = spec.get('sample_branch')
    if br:
        g = ['git', '-c', 'user.name=avf-bot', '-c', 'user.email=avf-bot@users.noreply.github.com']
        subprocess.run(['git', 'checkout', '-q', '-b', br], check=True)
        subprocess.run(['git', 'add', '-f', 'out/out.mp4', 'out/credit.json'], check=True)
        subprocess.run(g + ['commit', '-q', '-m', 'sample ' + br], check=True)
        subprocess.run(['git', 'push', '-q', '-f', 'origin', 'HEAD:refs/heads/' + br], check=True)


main()
