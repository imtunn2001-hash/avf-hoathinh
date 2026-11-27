"""meo: bai carousel "Meo chon do - luu lai" (affiliate Bi mat do vat). 1080x1350, SVG -> JPG.
SPEC_JSON = {"title","sub","brand","tips":[{"icon":"tem|nhan|lop|canh|thu|sao|tim|nha|bep|giuong|ao|xe|tim","h","b"} x5],
             "cta":{"h","b","btn"}}  (hoac LOCAL_SPEC=duong_dan.json khi test)
Ra: out/m1.jpg ... out/m7.jpg"""
import json, subprocess, sys, os, html

W, H = 1080, 1350
BG = '#FFF7E8'; INK = '#1B1B1F'; ACC = '#E8452C'; ACC2 = '#2E7D5B'; MUTED = '#6B6259'
FONT = "Montserrat"


def esc(s):
    return html.escape(s, quote=False)


def wrap(text, maxc):
    out, line = [], ''
    for w in text.split():
        if len(line) + len(w) + 1 > maxc and line:
            out.append(line); line = w
        else:
            line = (line + ' ' + w).strip()
    if line: out.append(line)
    return out


def tlines(lines, x, y, size, weight=700, fill=INK, lh=1.25, anchor='start'):
    s = ''
    for i, l in enumerate(lines):
        s += f'<text x="{x}" y="{y + i * size * lh:.0f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(l)}</text>'
    return s


def frame(inner, idx, total, brand):
    dots = ''.join(f'<circle cx="{W/2 - (total-1)*14 + i*28:.0f}" cy="1290" r="7" fill="{ACC if i == idx else "#D9CFC2"}"/>' for i in range(total))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="40" y="40" width="{W-80}" height="{H-80}" rx="36" fill="none" stroke="#EADFCF" stroke-width="4"/>
<text x="90" y="118" font-family="{FONT}" font-size="30" font-weight="800" fill="{ACC}" letter-spacing="3">{esc(brand)}</text>
<text x="{W-90}" y="118" font-family="{FONT}" font-size="30" font-weight="700" fill="{MUTED}" text-anchor="end">{idx+1}/{total}</text>
{inner}
{dots}
</svg>'''


def icon(kind, cx, cy, r=120, label='CR'):
    c = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF" stroke="{INK}" stroke-width="8"/>'
    if kind == 'tem':
        c += f'<rect x="{cx-70}" y="{cy-48}" width="140" height="96" rx="14" fill="{ACC2}"/><text x="{cx}" y="{cy+24}" font-family="{FONT}" font-size="64" font-weight="900" fill="#fff" text-anchor="middle">{esc(str(label)[:4])}</text>'
    elif kind == 'nhan':
        c += f'<rect x="{cx-60}" y="{cy-75}" width="120" height="150" rx="10" fill="#fff" stroke="{INK}" stroke-width="7"/>' + ''.join(f'<rect x="{cx-40}" y="{cy-50+i*28}" width="{80 if i%2==0 else 56}" height="10" rx="5" fill="{INK}"/>' for i in range(4))
    elif kind == 'lop':
        for i, col in enumerate([INK, '#F2C14E', '#9AD1B9']):
            rr = 80 - i * 18
            c += f'<path d="M {cx-rr} {cy+30} A {rr} {rr} 0 0 1 {cx+rr} {cy+30} Z" fill="{col}"/>'
    elif kind == 'canh':
        c += f'<path d="M {cx} {cy-80} L {cx+80} {cy+60} L {cx-80} {cy+60} Z" fill="#F2C14E" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/><rect x="{cx-7}" y="{cy-30}" width="14" height="52" rx="7" fill="{INK}"/><circle cx="{cx}" cy="{cy+40}" r="9" fill="{INK}"/>'
    elif kind == 'thu':
        c += f'<path d="M {cx-70} {cy+10} A 70 70 0 0 1 {cx+70} {cy+10} Z" fill="{ACC}"/><path d="M {cx-60} {cy+10} L {cx-40} {cy+70} M {cx+60} {cy+10} L {cx+40} {cy+70}" stroke="{INK}" stroke-width="8" stroke-linecap="round"/><path d="M {cx-40} {cy+70} L {cx+40} {cy+70}" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
    elif kind == 'tien':
        c += f'<rect x="{cx-75}" y="{cy-45}" width="150" height="90" rx="12" fill="#9AD1B9" stroke="{INK}" stroke-width="7"/><circle cx="{cx}" cy="{cy}" r="26" fill="#fff" stroke="{INK}" stroke-width="6"/><text x="{cx}" y="{cy+12}" font-family="{FONT}" font-size="34" font-weight="900" fill="{INK}" text-anchor="middle">đ</text>'
    elif kind == 'dongho':
        c += f'<circle cx="{cx}" cy="{cy}" r="70" fill="#fff" stroke="{INK}" stroke-width="8"/><path d="M {cx} {cy} L {cx} {cy-45} M {cx} {cy} L {cx+35} {cy+15}" stroke="{ACC}" stroke-width="9" stroke-linecap="round"/>'
    elif kind == 'sao':
        import math
        pts = ' '.join(f'{cx + (70 if i % 2 == 0 else 30) * math.sin(math.pi * i / 5):.0f},{cy - (70 if i % 2 == 0 else 30) * math.cos(math.pi * i / 5):.0f}' for i in range(10))
        c += f'<polygon points="{pts}" fill="#F2C14E" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
    elif kind == 'thuoc':
        c += f'<rect x="{cx-80}" y="{cy-25}" width="160" height="50" rx="8" fill="#F2C14E" stroke="{INK}" stroke-width="7"/>' + ''.join(f'<path d="M {cx-60+i*24} {cy-25} L {cx-60+i*24} {cy-5}" stroke="{INK}" stroke-width="5"/>' for i in range(6))
    elif kind == 'giot':
        c += f'<path d="M {cx} {cy-75} C {cx+55} {cy-10} {cx+60} {cy+20} {cx} {cy+65} C {cx-60} {cy+20} {cx-55} {cy-10} {cx} {cy-75} Z" fill="#7FC4E8" stroke="{INK}" stroke-width="7"/>'
    else:  # check (mac dinh)
        c += f'<path d="M {cx-55} {cy} L {cx-15} {cy+40} L {cx+60} {cy-45}" fill="none" stroke="{ACC2}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>'
    return c


def cover(d):
    s = tlines(['LƯU LẠI TRƯỚC KHI MUA'], 90, 330, 40, 800, ACC)
    s += tlines(wrap(d['title'], 14), 90, 470, 110, 900, INK, 1.1)
    s += tlines(wrap(d['sub'], 30), 90, 960, 50, 600, MUTED)
    s += f'<rect x="90" y="1110" width="440" height="84" rx="42" fill="{INK}"/><text x="310" y="1165" font-family="{FONT}" font-size="34" font-weight="800" fill="#fff" text-anchor="middle">Vuốt sang xem →</text>'
    return s


def tip(d, n):
    s = f'<text x="90" y="300" font-family="{FONT}" font-size="150" font-weight="900" fill="{ACC}">{n}</text>'
    s += icon(d.get('icon', 'check'), W - 240, 300, 115, d.get('label', 'CR'))
    s += tlines(wrap(d['h'], 18), 90, 560, 76, 900, INK, 1.15)
    hl = len(wrap(d['h'], 18))
    s += tlines(wrap(d['b'], 28), 90, 560 + hl * 88 + 70, 52, 500, INK, 1.38)
    return s


def cta(d):
    s = tlines(wrap(d['h'], 18), 90, 360, 80, 900, INK, 1.15)
    s += f'<rect x="90" y="640" width="{W-180}" height="300" rx="30" fill="#fff" stroke="{INK}" stroke-width="6"/>'
    s += tlines(wrap(d['b'], 30), 130, 720, 46, 700, INK, 1.35)
    s += f'<rect x="90" y="1010" width="{W-180}" height="110" rx="55" fill="{ACC}"/><text x="{W/2}" y="1083" font-family="{FONT}" font-size="44" font-weight="900" fill="#fff" text-anchor="middle">{esc(d["btn"])}</text>'
    return s


def build(spec, out):
    os.makedirs(out, exist_ok=True)
    slides = [cover(spec)] + [tip(t, i + 1) for i, t in enumerate(spec['tips'])] + [cta(spec['cta'])]
    files = []
    for i, inner in enumerate(slides):
        svg = frame(inner, i, len(slides), spec.get('brand', 'BÍ MẬT ĐỒ VẬT'))
        p = os.path.join(out, f's{i+1}.svg'); open(p, 'w').write(svg)
        png = p[:-4] + '.png'
        subprocess.run(['rsvg-convert', '-w', str(W), '-h', str(H), p, '-o', png], check=True)
        files.append(png)
    return files


if __name__ == '__main__':
    if os.environ.get('LOCAL_SPEC'):
        spec = json.load(open(os.environ['LOCAL_SPEC'], encoding='utf-8'))
    else:
        spec = json.loads(os.environ['SPEC_JSON'])
    if len(spec.get('tips', [])) < 3:
        sys.exit('can it nhat 3 meo')
    out = os.path.join(os.getcwd(), 'out')
    pngs = build(spec, os.path.join(out, 'meo'))
    from PIL import Image
    for i, p in enumerate(pngs):
        Image.open(p).convert('RGB').save(os.path.join(out, 'm%d.jpg' % (i + 1)), quality=90)
    print('ok', len(pngs))
