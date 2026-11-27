#!/usr/bin/env python3
"""AVF ent: dung anh khung chu (nen mau) + tai/cat anh that cho bai nhieu anh.
Dau vao: bien moi truong SPEC_JSON = {"card":{"text","bg","fg"},"photos":[url,...]}
Dau ra: out/01_card.jpg, out/02.jpg, out/03.jpg ...
"""
import json, os, sys, io, urllib.request
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 800
FONTS = [os.environ.get('ENT_FONT', ''), 'fonts/BeVietnamPro-ExtraBold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
UA = 'AVF-ent-render/1.0 (https://github.com/imtunn2001-hash/avf-editor)'


def font(size):
    for f in FONTS:
        if f and os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, maxw):
    lines = []
    for para in text.split('\n'):
        words, cur = para.split(), ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if draw.textlength(t, font=fnt) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def card(text, bg, fg, path):
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    pad_x, pad_y = 90, 80
    for size in range(78, 30, -2):
        f = font(size)
        lines = wrap(d, text, f, W - 2 * pad_x)
        lh = int(size * 1.32)
        if lh * len(lines) <= H - 2 * pad_y:
            break
    total = lh * len(lines)
    y = (H - total) // 2
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, y), ln, font=f, fill=fg)
        y += lh
    img.save(path, 'JPEG', quality=92)


def photo(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    data = urllib.request.urlopen(req, timeout=60).read()
    im = Image.open(io.BytesIO(data)).convert('RGB')
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((1080, 1080), Image.LANCZOS)
    im.save(path, 'JPEG', quality=90)


def main():
    spec = json.loads(os.environ.get('SPEC_JSON') or sys.argv[1])
    os.makedirs('out', exist_ok=True)
    c = spec['card']
    card(c['text'], c.get('bg', '#C8243B'), c.get('fg', '#FFFFFF'), 'out/01_card.jpg')
    ok = 0
    for i, u in enumerate(spec.get('photos', [])[:6]):
        try:
            photo(u, 'out/%02d.jpg' % (i + 2))
            ok += 1
        except Exception as e:
            print('bo anh', u, e)
    print('xong: 1 card +', ok, 'anh')


if __name__ == '__main__':
    main()
