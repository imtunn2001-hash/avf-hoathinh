"""ANH BIA YouTube (Shorts 1080x1920) - mau chung moi kenh (chu chot 27/11: "anh bia ro rang, nguoi xem nam ro thong tin").
Nguyen tac (nghien cuu 27/11):
- 2-4 chu TO o giua anh (anh bia hien nho o trang kenh / tim kiem / trang chu) -> doc duoc o co dien thoai.
- Chu bia KHAC tieu de, bo sung cho tieu de (tieu de ke, bia gay to mo).
- 1 kieu thong nhat moi kenh: nhan kenh tren cung + nhan tap/phan + chu chinh + 1 dong phu.
- Moi thu quan trong nam giua (x 100-980, y 380-1500) vi cac man hinh cat anh doc; day duoi de trong cho so view YouTube.
- Nen la hinh canh manh nhat, lam toi 2 dau, lam net vung giua.
Dung:
  python3 editor/thumb.py spec.json out/thumb.jpg     (spec: {channel, img, text, hl?, badge?, sub?})
  from thumb import make_thumb
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chu  # noqa: E402
import ngat  # noqa: E402

W, H = 1080, 1920
# mau nhan dien tung kenh: (ten tren nhan, mau nhan, mau chu nhan, mau chu nhan manh, font chu chinh)
STYLE = {
    'mnmb': ('MỖI NGÀY MỘT BƯỚC', (255, 196, 64), (24, 16, 0), (255, 196, 64), 'key'),
    'cd':   ('CHUYỆN ĐÊM', (200, 24, 30), (255, 255, 255), (255, 60, 60), 'tag'),
    'cck':  ('CHUYỆN CHƯA KỂ', (13, 42, 107), (255, 212, 0), (255, 212, 0), 'key'),
    'ksc':  ('KÝ SỬ CHIẾN', (176, 32, 24), (255, 230, 170), (255, 200, 60), 'key'),
    'war':  ('CHIẾN SỬ KÝ', (176, 32, 24), (255, 230, 170), (255, 200, 60), 'key'),
    'lt':   ('LIÊN THIÊN', (22, 92, 70), (255, 255, 255), (130, 235, 180), 'key'),
}
DEF = ('AVF', (255, 255, 255), (0, 0, 0), (255, 212, 0), 'key')


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def _grad(h, top, bot):
    """lop toi: dam o tren (top) va duoi (bot), trong o giua"""
    g = Image.new('L', (1, h))
    for y in range(h):
        t = y / (h - 1)
        a = max(top * (1 - t / 0.30) if t < 0.30 else 0, bot * ((t - 0.42) / 0.58) if t > 0.42 else 0)
        g.putpixel((0, y), int(255 * min(1, a)))
    return g.resize((W, h))


def pill(d, x, y, text, f, bg, fg, pad=(28, 14), anchor='l'):
    tw = d.textlength(text, font=f); bb = f.getbbox('ĐẤY')
    w = tw + pad[0] * 2; h = (bb[3] - bb[1]) + pad[1] * 2 + 8
    if anchor == 'r': x = x - w
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2 if h < 90 else 22, fill=bg)
    d.text((x + pad[0], y + pad[1] + 4 - bb[1]), text, font=f, fill=fg)
    return x, y, x + w, y + h


def _cat_ten(lines, orig):
    """True neu xuong dong cat doi ten rieng (vd BẠCH / ĐẰNG)"""
    ow = ngat.nfc(orig).split(' '); k = 0
    for l in lines[:-1]:
        k += len(l.split(' '))
        if k < len(ow):
            a, b = ow[k - 1], ow[k]
            if a[:1].isupper() and b[:1].isupper() and not a.isupper() and not ngat.DAU.search(a): return True
    return False


def make_thumb(img, channel, text, hl='', badge='', sub='', out='out/thumb.jpg', focus=0.5):
    """img = khung hinh canh (da cat bo chu/phu de cua video). Bo cuc 'the anh':
    nen = chinh khung do lam mo + toi; tren cung nhan kenh + nhan tap; giua la the anh net; duoi la 2-4 chu TO + 1 dong phu."""
    name, cbg, cfg, chl, fk = STYLE.get(channel, DEF)
    src = (img if isinstance(img, Image.Image) else Image.open(img)).convert('RGB')
    bg = cover(src, W, H).filter(ImageFilter.GaussianBlur(38))
    bg = ImageEnhance.Brightness(bg).enhance(0.42)
    bg = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), bg, _grad(H, 0.6, 0.75))
    # the anh: rong 1000, cao toi da 660, cat giua theo focus
    cw, chh = 1000, 660
    s_ = cw / src.width; ih = int(src.height * s_)
    card = src.resize((cw, ih), Image.LANCZOS)
    if ih > chh:
        y0 = int((ih - chh) * focus); card = card.crop((0, y0, cw, y0 + chh)); ih = chh
    card = ImageEnhance.Contrast(card).enhance(1.08); card = ImageEnhance.Color(card).enhance(1.1)
    cx, cy = 40, 400
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([cx + 6, cy + 14, cx + cw + 6, cy + ih + 14], 34, fill=200)
    bg.paste(Image.new('RGB', (W, H), (0, 0, 0)), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    m = Image.new('L', (cw, ih), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ih - 1], 30, fill=255)
    bg.paste(card, (cx, cy), m)
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([cx - 3, cy - 3, cx + cw + 3, cy + ih + 3], 32, outline=cbg if channel != 'cck' else (255, 212, 0), width=6)
    # nhan kenh + nhan tap (de len mep tren the anh)
    fb = chu.font('bold', 44)
    pill(d, 70, 300, name, fb, cbg, cfg)
    if badge:
        pill(d, 1010, 300, ngat.nfc(badge).upper(), fb, (255, 255, 255), (15, 15, 15), anchor='r')
    # chu chinh 2-4 chu, 1 chu nhan mau kenh
    t = ngat.nfc(text).upper(); hlw = set(ngat.nfc(hl).upper().split()) if hl else set()
    maxw = 960; lines = None
    for maxl in (2, 3):
        sz = 190 if fk == 'key' else 220
        while sz >= (120 if maxl == 2 else 96):
            f = chu.font(fk, sz); ls = ngat.wrap_cum(d, t, f, maxw, orig=text)
            if len(ls) <= maxl and all(d.textlength(l, font=f) <= maxw for l in ls) and not _cat_ten(ls, text): lines = ls; break
            sz -= 6
        if lines: break
    if not lines: f = chu.font(fk, 96); lines = ngat.wrap_cum(d, t, f, maxw, orig=text)[:3]
    lh = int(f.size * (1.04 if fk == 'tag' else 1.1))
    sb = chu.font('sub', 52); sub = ngat.nfc(sub)
    sub_lines = ngat.wrap_cum(d, sub, sb, 900)[:2] if sub else []
    total = lh * len(lines) + (20 + len(sub_lines) * 64 if sub_lines else 0)
    top = cy + ih + 40; bot = 1560
    y = int(top + max(0, (bot - top - total) / 2))
    for i, l in enumerate(lines):
        x = (W - d.textlength(l, font=f)) / 2
        for wd in l.split(' '):
            col = chl if wd.strip('.,!?:…"“”') in hlw else (255, 255, 255)
            d.text((x, y + i * lh), wd, font=f, fill=col, stroke_width=max(7, f.size // 20), stroke_fill=(0, 0, 0))
            x += d.textlength(wd + ' ', font=f)
    y += lh * len(lines) + 20
    for l in sub_lines:
        tw = d.textlength(l, font=sb)
        d.text(((W - tw) / 2, y), l, font=sb, fill=(225, 225, 225), stroke_width=3, stroke_fill=(0, 0, 0)); y += 64
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    q = 92
    while True:
        bg.save(out, quality=q, optimize=True)
        if os.path.getsize(out) < 1_900_000 or q <= 60: break
        q -= 8
    return out


if __name__ == '__main__':
    sp = json.load(open(sys.argv[1]))
    print(make_thumb(sp['img'], sp.get('channel', ''), sp['text'], sp.get('hl', ''), sp.get('badge', ''), sp.get('sub', ''),
                     sys.argv[2] if len(sys.argv) > 2 else 'out/thumb.jpg', sp.get('focus', 0.45)))
