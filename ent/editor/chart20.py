"""Vang 20 Giay - video chart dong 9:16 (35-60s), giong Nhat Khoa + phu de karaoke.
SPEC_JSON = {"branch","dir"} (spec.json trong dir) hoac spec truc tiep (co "candles").
spec: {
  "candles": [{"t":"17/11 09:15","o":..,"h":..,"l":..,"c":..}, ...],   # nen that, cu -> moi
  "symbol": "XAU/USD", "tf": "M15", "date": "17/11/2026",
  "start": 30,                       # so nen hien luc dau
  "voice_urls": [...], "srt_urls": [...]  (hoac voice_url/srt_url),
  "hook_text": "...", "outro": "Câu hỏi cuối",
  "events": [ {"cue":"cụm từ trong lời đọc", "type":"goto","i":57},          # chay nen toi chi so i
              {"cue":"...", "type":"level","price":3846.5,"label":"HỖ TRỢ"},  # ke vung gia
              {"cue":"...", "type":"mark","i":57,"text":"ĐÁY 3.846","side":"low"},
              {"cue":"...", "type":"pop","text":"PHÁ VỠ!","fx":"shake"},       # chu to giua man hinh
              {"cue":"...", "type":"count","from":3846.5,"to":3875.6,"label":"+29 USD"} ]  # so dem chay
}"""
import json, math, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series import get, parse_srt, ease, wrap, wrap_bal, word_times, sfx, _norm, voice_part  # noqa: E402
import safezone  # noqa: E402  khoa cung bo cuc 20/11: moi chu trong SAFE (80,260,940,1460)
SX0, SY0, SX1, SY1 = safezone.SAFE
TW = safezone.MAXW_C540  # 780: be rong chu canh giua

W, H, FPS = 1080, 1920, 30
ROOT = os.getcwd()
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
BG = (8, 12, 24); PANEL_BG = (14, 20, 36); GRID = (32, 42, 66)
GOLD = (245, 196, 66); GOLD2 = (255, 228, 140); WHITE = (255, 255, 255); MUTED = (150, 160, 185)
UP = (34, 197, 94); DN = (239, 68, 68); INK = (16, 16, 24); KEY = (255, 90, 90)
ON_ACC = INK   # mau chu tren nen mau nhan (accent)
# 28/11 FULL KHUNG (chu chot): nen ve tran ngang 0..820, cao 580..1300; truc gia 830-935 (trong SAFE);
# phu de 1320-1452 (2 dong x 46px); so gia lon 404-560. Khong con panel bo goc.
PY0 = 404
CX0, CX1 = 0, 820
CY0, CY1 = 580, 1680   # nen tran xuong ca vung caption app (chi hinh, khong chu)
LY1 = 1300   # nhan chu chi o tren 1300 (duoi la phu de / caption)
SUB_PX, SUB_LINES = 46, 2
MAXLAB = 2   # toi da 2 nhan vung/moc hien cung luc


def apply_theme(th):
    """26/11: moi page 1 mau chu dao. th = {accent, accent2, bg, panel, grid, on_accent} (RGB list)."""
    global GOLD, GOLD2, BG, PANEL_BG, GRID, ON_ACC
    if not th: return
    tp = lambda k, dft: tuple(th.get(k) or dft)
    GOLD = tp('accent', GOLD); GOLD2 = tp('accent2', GOLD2); BG = tp('bg', BG); PANEL_BG = tp('panel', PANEL_BG); GRID = tp('grid', GRID)
    ON_ACC = tp('on_accent', (255, 255, 255) if sum(GOLD) < 520 else INK)


def fnt(bold, size):
    for p in [os.path.join(ROOT, 'fonts', 'BeVietnamPro-ExtraBold.ttf' if bold else 'BeVietnamPro-Medium.ttf'),
              '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf' if bold else '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf']:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    sys.exit('khong co font')


_FC = {}


def F(bold, size):
    k = (bold, size)
    if k not in _FC: _FC[k] = fnt(bold, size)
    return _FC[k]


def vn(x, nd=1):
    s = f'{x:,.{nd}f}'
    return s.replace(',', '#').replace('.', ',').replace('#', '.')


def text_c(d, y, s, f, fill, stroke=3, x0=0, x1=W):
    d.text((x0 + (x1 - x0 - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def cue_times(events, srt, dur):
    words = []
    for a, b, t in srt:
        ws = _norm(t)
        for i, w in enumerate(ws): words.append((a + (b - a) * i / max(1, len(ws)), w))
    last = 0.0; out = []
    for k, e in enumerate(events):
        c = _norm(e.get('cue') or ''); t0 = None
        if 'at' in e: t0 = float(e['at'])
        elif c and words:
            for i in range(len(words) - len(c) + 1):
                if words[i][0] >= last - 0.01 and [w for _, w in words[i:i + len(c)]] == c: t0 = words[i][0]; break
            if t0 is None:  # tim tu dau neu cue nam truoc
                for i in range(len(words) - len(c) + 1):
                    if [w for _, w in words[i:i + len(c)]] == c: t0 = words[i][0]; break
        if t0 is None:
            t0 = dur * (k + 1) / (len(events) + 1); print('cue khong thay:', e.get('cue'))
        out.append(t0); last = t0
    return out


def dashed(d, x0, x1, y, col, w=3, on=18, off=12):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + on, x1), y)], fill=col, width=w); x += on + off


def free_y(placed, x0, x1, h, cands, dy=0, gap=6):
    """chon y dau tien trong cands ma hop (x0,y+dy,x1,y+dy+h) khong cham hop nao da dat; giu trong vung ve nen.
    Khong co cho trong -> lay cho de it nhat. (25/11: chong nhan gia/nhan nen de nhau)"""
    best, bo = None, None
    for y in cands:
        top = y + dy
        if top < CY0 or top + h > LY1: continue
        ov = sum(max(0, min(x1, b[2]) - max(x0, b[0]) + gap) * max(0, min(top + h, b[3]) - max(top, b[1]) + gap)
                 for b in placed if min(x1, b[2]) + gap > max(x0, b[0]) and min(top + h, b[3]) + gap > max(top, b[1]))
        if ov == 0: return y
        if bo is None or ov < bo: best, bo = y, ov
    y = best if best is not None else cands[0]
    return min(max(y + dy, CY0), LY1 - h) - dy


def load_spec():
    inp = json.loads(os.environ['SPEC_JSON'])
    if 'candles' in inp: return inp, ROOT
    br, dd = inp['branch'], inp['dir'].strip('/')
    subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
    __import__('gitlay').lay(dd)
    return json.load(open(os.path.join(ROOT, dd, 'spec.json'), encoding='utf-8')), os.path.join(ROOT, dd)


G_SPANS = []


def own_srt(texts, spans):
    """26/11 chu chot 'tranh thieu tu, sai chu': phu de lay DUNG chu minh viet (khong lay SRT cua may doc,
    vd 'Fed' bi ra 'Phet'). Moi cau tach theo dau phay, cum dai > 9 chu chia doi; thoi gian chia theo do dai chu."""
    out = []
    for txt, (a, b) in zip(texts, spans):
        pcs = [x.strip() for x in re.split(r'(?<=[,.;:?!])\s+', txt.strip()) if x.strip()]
        ch = []
        for pc in pcs:
            ws = pc.split()
            while len(ws) > 9:
                k = (len(ws) + 1) // 2; ch.append(' '.join(ws[:k])); ws = ws[k:]
            if ws: ch.append(' '.join(ws))
        tot = float(sum(len(c) + 3 for c in ch)) or 1.0; t = a
        for c in ch:
            e = t + (b - a) * (len(c) + 3) / tot; out.append((t, e, c)); t = e
    return out


def build_voice(sp):
    srt = []
    urls = sp.get('voice_urls') or ([sp['voice_url']] if sp.get('voice_url') else [])
    surls = sp.get('srt_urls') or ([sp.get('srt_url', '')] if sp.get('voice_url') else [])
    parts, off, spans = [], 0.0, []
    ps = sp.get('pauses') or []
    for i, u in enumerate(urls):
        pth = u if os.path.exists(u) else get(u, os.path.join(OUT, f'vp{i}.mp3'))
        wav = os.path.join(OUT, f'vp{i}.wav')
        dd, lead = voice_part(pth, wav, sp, i)
        su = surls[i] if i < len(surls) else ''
        if su:
            try:
                txt = open(su if os.path.exists(su) else get(su, os.path.join(OUT, f'vp{i}.srt')), encoding='utf-8').read()
                for a, b, t in parse_srt(txt): srt.append((max(0, a - lead) + off, max(0, b - lead) + off, t))
            except Exception as e: print('srt', i, e)
        parts.append(wav)
        pz = float(ps[i]) if i < len(ps) and ps[i] is not None else 0.0
        spans.append((off, off + max(0.3, dd - pz))); off += dd
    lst = os.path.join(OUT, 'vlist.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    voice = os.path.join(OUT, 'voice.wav')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice])
    from series import fix_cues
    G_SPANS[:] = spans
    return voice, fix_cues(srt), off


def main():
    sp, _ = load_spec()
    apply_theme(sp.get('theme'))
    news = sp.get('news') or {}
    C = sp['candles']; N = len(C)
    voice, srt, dur = build_voice(sp)
    if sp.get('sub_texts') and len(sp['sub_texts']) == len(G_SPANS): srt = own_srt(sp['sub_texts'], G_SPANS)
    LEAD, TAIL = 0.1, 2.8
    D = dur + LEAD + TAIL
    evs = sp.get('events') or []
    et = cue_times(evs, srt, dur)
    for e, t in zip(evs, et): e['t'] = t
    print('events', [(e['type'], round(e['t'], 1)) for e in evs])
    # moc chay nen: (thoi diem, so nen hien)
    start = int(sp.get('start', max(20, N // 3)))
    keys = [(0.0, float(start))]
    for e in evs:
        if e['type'] == 'goto':
            keys.append((max(keys[-1][0] + 0.3, e['t']), float(min(N, int(e['i']) + 1))))
    if keys[-1][1] < N: keys.append((max(keys[-1][0] + 0.5, dur * 0.9), float(N)))
    # chay deu giua 2 moc, nhung nen moi chi chay trong 2.5s truoc moc (tranh chay qua cham)

    def shown(tv):
        if tv <= keys[0][0]: return keys[0][1]
        for (a, x), (b, y) in zip(keys, keys[1:]):
            if tv < b:
                run = min(b - a, max(1.0, min(4.5, abs(y - x) * 0.15)))
                s = b - run
                return x if tv < s else x + (y - x) * ease((tv - s) / run)
        return keys[-1][1]

    WIN = int(sp.get('window', 46))
    # 28/11 (mau Hash Forex): chua o trong ben phai cho duong du bao 'path'
    FUT = int(sp.get('future', 8 if any(e['type'] == 'path' for e in evs) else 0))
    # cai tien 22/11 (QC: 'khung cuoi chart dung yen'): het nen moi thi zoom cham vao cac nen gan nhat
    ZS = keys[-1][0] + 1.0
    ZD = dur + 1.0 - ZS   # zoom deu toi het loi doc, khong dung lai giua chung
    ZOOM = sp.get('end_zoom', True) is not False and ZD >= 3.0
    ZT = max(14.0, min(N, WIN) * 0.5)   # so nen con lai trong khung khi zoom het muc

    def winf(tv):
        if not ZOOM or tv <= ZS: return float(WIN)
        return WIN - (WIN - ZT) * ease((tv - ZS) / ZD)
    # KHOA CUNG 20/11: panel nam tron trong SAFE; tren 260-400 la tieu de, duoi 1190-1455 la phu de
    PX0, PX1 = SX0, SX1
    wts = word_times(srt)
    hook = (sp.get('hook_text') or '').strip().upper()
    sym = sp.get('symbol', 'XAU/USD'); tf = sp.get('tf', 'M15'); date = sp.get('date', '')
    o0 = C[0]['o']
    base = Image.new('RGB', (W, H), BG); bd = ImageDraw.Draw(base)
    # header: thuong hieu trai, ma + khung + ngay phai (do rong de khong de chu)
    fb = F(True, 64); bx = SX0 + 10
    b1, b2 = (sp.get('brand') or ['VÀNG', '20 GIÂY'])[:2]
    while bd.textlength(b1 + ' ' + b2, font=fb) > SX1 - SX0 - 20 and fb.size > 40: fb = F(True, fb.size - 2)
    bd.text((bx, 268), b1, font=fb, fill=GOLD, stroke_width=2, stroke_fill=(0, 0, 0))
    bd.text((bx + bd.textlength(b1 + ' ', font=fb), 268), b2, font=fb, fill=WHITE)
    r = ' · '.join(x for x in [f'{sym} · {tf}', date] if x); fr = F(True, 32)
    while bd.textlength(r, font=fr) > SX1 - SX0 - 20 and fr.size > 22: fr = F(True, fr.size - 2)
    if news.get('source'): r = r + ' · ' + news['source'].replace('Nguồn: ', 'Nguồn ')
    while bd.textlength(r, font=fr) > SX1 - SX0 - 20 and fr.size > 22: fr = F(True, fr.size - 2)
    bd.text((bx, 346), r, font=fr, fill=GOLD2)
    bd.rectangle([SX0, 392, SX1, 396], fill=GOLD)
    for yy in range(CY0 - 20, H):   # nen toi dan xuong duoi cho phu de noi ro
        k = min(1.0, max(0.0, (yy - 1500) / 400)); bd.line([(0, yy), (W, yy)], fill=tuple(int(BG[i] * (1 - 0.5 * k)) for i in range(3)))
    lo_s = hi_s = None
    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-tune', 'animation', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    for fi in range(int(D * FPS)):
        t = fi / FPS; tv = t - LEAD
        im = base.copy(); d = ImageDraw.Draw(im)
        sh = shown(max(0.0, tv)); full = int(sh); frac = sh - full
        vis = [dict(c) for c in C[:full]]
        if frac > 0.02 and full < N:   # nen dang hinh thanh
            c = C[full]; q = ease(frac)
            cc = c['o'] + (c['c'] - c['o']) * q
            vis.append({'t': c['t'], 'o': c['o'], 'c': cc, 'h': max(c['o'], cc, c['o'] + (c['h'] - c['o']) * q), 'l': min(c['o'], cc, c['o'] + (c['l'] - c['o']) * q)})
        vis = vis or [dict(C[0])]
        wf = winf(tv); i0f = max(0.0, len(vis) - wf)
        i0 = int(math.ceil(i0f - 1e-6)); win = vis[i0:]
        active = [e for e in evs if e['t'] <= tv]; placed0 = []
        lv = [e for e in active if e['type'] == 'level']
        xp = [e['price'] for e in lv]   # 28/11: khung gia chua du vung to / mui ten / duong du bao
        for e in active:
            if e['type'] in ('zone', 'arrow'): xp += [e['p0'], e['p1']]
            elif e['type'] == 'path': xp += [p_['price'] for p_ in e['pts']]
        lo = min([c['l'] for c in win] + xp)
        hi = max([c['h'] for c in win] + xp)
        pad = (hi - lo) * 0.12 + 0.5; lo -= pad; hi += pad
        lo_s = lo if lo_s is None else lo_s + (lo - lo_s) * 0.12
        hi_s = hi if hi_s is None else hi_s + (hi - hi_s) * 0.12
        Y = lambda v: CY1 - (v - lo_s) / max(1e-6, hi_s - lo_s) * (CY1 - CY0)
        # luoi + truc gia
        step = [0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100][0]
        for s_ in [0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100]:
            if (hi_s - lo_s) / s_ <= 7: step = s_; break
        g = math.ceil(lo_s / step) * step
        while g < hi_s:
            y = Y(g)
            if CY0 - 5 < y < CY1 + 5:
                d.line([(0, y), (CX1 + 10, y)], fill=GRID, width=1)
                if y < LY1: d.text((CX1 + 20, y - 15), vn(g, 0 if step >= 1 else 1), font=F(False, 26), fill=MUTED)
            g += step
        slot = (CX1 - CX0) / (wf + FUT); bw = max(4, min(slot * 0.62, 40))
        X = lambda j: CX0 + (j - i0f + 0.5) * slot
        # 28/11: vung gia to mau (OB / FVG / vung gia tri) ve TRUOC nen
        zs = [e for e in active if e['type'] == 'zone']
        if zs:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            for e in zs:
                q = ease((tv - e['t']) / 0.5); col = tuple(e.get('color') or GOLD)
                ya, yb = sorted([Y(e['p0']), Y(e['p1'])]); ya = max(CY0, ya); yb = min(CY1, yb)
                if yb - ya < 2: yb = ya + 2
                xa = max(CX0, X(int(e['i0'])) - slot / 2) if 'i0' in e else CX0
                xb = xa + (CX1 - xa) * q
                od.rectangle([xa, ya, xb, yb], fill=col + (70,), outline=col + (200,), width=2)
            im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')); d = ImageDraw.Draw(im)
            for e in zs[-MAXLAB:]:
                if tv - e['t'] < 0.3 or not e.get('label'): continue
                col = tuple(e.get('color') or GOLD); ya = max(CY0, min(Y(e['p0']), Y(e['p1'])))
                xa = max(CX0, X(int(e['i0'])) - slot / 2) if 'i0' in e else CX0
                f_ = F(True, 30); lab = e['label']; lw = d.textlength(lab, font=f_); xa = max(SX0, xa)
                ly = free_y(placed0, xa + 6, xa + lw + 30, 40, [ya + 6, ya - 46, ya + 52])
                placed0.append((xa + 6, ly, xa + lw + 30, ly + 40))
                d.rounded_rectangle([xa + 6, ly, xa + lw + 30, ly + 40], 10, fill=(0, 0, 0), outline=col, width=2)
                d.text((xa + 18, ly + 3), lab, font=f_, fill=col)
        for k, c in enumerate(win):
            j = i0 + k; x = X(j)
            if x - bw / 2 < CX0 - 1: continue
            col = UP if c['c'] >= c['o'] else DN
            d.line([(x, Y(c['h'])), (x, Y(c['l']))], fill=col, width=3)
            y0, y1 = sorted([Y(c['o']), Y(c['c'])])
            d.rectangle([x - bw / 2, y0, x + bw / 2, max(y1, y0 + 2)], fill=col)
        last = vis[-1]
        # vung gia
        placed = placed0   # hop nhan da ve trong khung nay (zone, level, mark) de khong de nhau
        for e in lv:
            q = ease((tv - e['t']) / 0.5); y = Y(e['price'])
            col = tuple(e.get('color') or (UP if 'HỖ TRỢ' in e.get('label', '').upper() else (DN if 'KHÁNG' in e.get('label', '').upper() else GOLD)))
            dashed(d, CX0, CX0 + (CX1 - CX0) * q, y, col, 4 if e in lv[-MAXLAB:] else 2)
            lab = f"{e.get('label', '')} {vn(e['price'])}".strip()
            if q > 0.3 and e in lv[-MAXLAB:]:
                lw = d.textlength(lab, font=F(True, 32)); lx = CX1 - lw - 30
                # 25/11: QC 24h nhieu lan 'nhan vung gia de nhau' -> tim cho trong (duoi vach, tren vach, roi xa dan)
                ly = free_y(placed, lx - 12, lx + lw + 12, 42, [y + 8, y - 50, y + 54, y - 96, y + 100, y - 142])
                placed.append((lx - 12, ly, lx + lw + 12, ly + 42))
                d.rounded_rectangle([lx - 12, ly, lx + lw + 12, ly + 42], 12, fill=col)
                d.text((lx, ly + 3), lab, font=F(True, 32), fill=INK if col != GOLD else ON_ACC)
        # danh dau nen: nhan chu chi giu 6s, sau do con mui ten nho
        for e in active:
            if e['type'] != 'mark': continue
            j = int(e['i'])
            if j < i0 or j >= len(vis): continue
            c = vis[j]; x = X(j); age = tv - e['t']; q = ease(age / 0.35)
            low = e.get('side', 'low') == 'low'
            yb = Y(c['l']) + 14 if low else Y(c['h']) - 14
            mk = [m for m in active if m['type'] == 'mark' and tv - m['t'] <= 4][-MAXLAB:]
            if age > 4 or e not in mk:
                d.polygon([(x, yb), (x - 9, yb + (16 if low else -16)), (x + 9, yb + (16 if low else -16))], fill=GOLD); continue
            ya = yb + (56 if low else -56) * q
            d.line([(x, ya), (x, yb)], fill=GOLD, width=5)
            d.polygon([(x, yb), (x - 14, yb + (22 if low else -22)), (x + 14, yb + (22 if low else -22))], fill=GOLD)
            f_ = F(True, 36); tw = d.textlength(e['text'], font=f_); tx = min(max(SX0 + 14, x - tw / 2), CX1 - tw)
            ty = ya + (8 if low else -52)
            ty = min(max(ty, CY0 + 4), LY1 - 50)
            sg = 1 if low else -1
            ty = free_y(placed, tx - 14, tx + tw + 14, 50, [ty + sg * k * 54 for k in range(4)] + [ty - sg * k * 54 for k in range(1, 4)], dy=-4)
            placed.append((tx - 14, ty - 4, tx + tw + 14, ty + 46))
            d.rounded_rectangle([tx - 14, ty - 4, tx + tw + 14, ty + 46], 12, fill=(0, 0, 0), outline=GOLD, width=2)
            d.text((tx, ty), e['text'], font=f_, fill=GOLD2)
        # 28/11: mui ten doc ve dan + nhan xoay (RETEST, SUPPORT...) kieu mau Hash Forex
        for e in active:
            if e['type'] != 'arrow': continue
            j = int(e['i'])
            if j < i0 or j >= len(vis) + FUT: continue
            x = X(j); q = ease((tv - e['t']) / 0.6); col = tuple(e.get('color') or GOLD)
            ya, yb = Y(e['p0']), Y(e['p0'] + (e['p1'] - e['p0']) * q)
            d.line([(x, ya), (x, yb)], fill=col, width=4)
            up = e['p1'] > e['p0']
            d.polygon([(x, yb), (x - 11, yb + (18 if up else -18)), (x + 11, yb + (18 if up else -18))], fill=col)
            if q > 0.5 and e.get('label'):
                f_ = F(True, 28); lab = e['label']; tw = int(d.textlength(lab, font=f_)) + 8
                lay = Image.new('RGBA', (tw, 36), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((4, 1), lab, font=f_, fill=WHITE + (255,), stroke_width=2, stroke_fill=(0, 0, 0, 255))
                lay = lay.rotate(90 if up else -90, expand=True)
                ym = (Y(e['p0']) + Y(e['p1'])) / 2 - lay.size[1] / 2
                xm = int(max(SX0, min(x + 10, CX1 - lay.size[0]))); ym = int(min(max(ym, CY0), LY1 - lay.size[1]))
                lw_, lh_ = lay.size
                ym = int(free_y(placed, xm, xm + lw_, lh_, [ym] + [ym + sg_ * k_ * 30 for k_ in range(1, 8) for sg_ in (-1, 1)]))
                ym = int(min(max(ym, CY0), LY1 - lh_)); placed.append((xm, ym, xm + lw_, ym + lh_))
                im.paste(lay, (xm, ym), lay); d = ImageDraw.Draw(im)
        # 28/11: duong du bao net dut tu nen cuoi sang vung trong ben phai (kich ban co dieu kien)
        for e in active:
            if e['type'] != 'path': continue
            q = ease((tv - e['t']) / 1.0); col = tuple(e.get('color') or WHITE)
            pts = [(X(len(vis) - 1), Y(last['c']))] + [(X(len(vis) - 1 + float(p_['di'])), Y(p_['price'])) for p_ in e['pts']]
            segs = list(zip(pts, pts[1:])); tot = sum(math.dist(a_, b_) for a_, b_ in segs) or 1; lim = tot * q; acc = 0
            for a_, b_ in segs:
                L = math.dist(a_, b_)
                if acc >= lim: break
                k_ = min(1.0, (lim - acc) / max(L, 1e-6)); bx_ = (a_[0] + (b_[0] - a_[0]) * k_, a_[1] + (b_[1] - a_[1]) * k_)
                n_ = max(1, int(math.dist(a_, bx_) // 14))
                for m_ in range(n_):
                    if m_ % 2: continue
                    p1_ = (a_[0] + (bx_[0] - a_[0]) * m_ / n_, a_[1] + (bx_[1] - a_[1]) * m_ / n_)
                    p2_ = (a_[0] + (bx_[0] - a_[0]) * (m_ + 1) / n_, a_[1] + (bx_[1] - a_[1]) * (m_ + 1) / n_)
                    d.line([p1_, p2_], fill=col, width=4)
                acc += L
            if q >= 0.99:
                (ax_, ay_), (bx2, by2) = pts[-2], pts[-1]; ang = math.atan2(by2 - ay_, bx2 - ax_)
                d.polygon([(bx2, by2), (bx2 - 22 * math.cos(ang - 0.45), by2 - 22 * math.sin(ang - 0.45)), (bx2 - 22 * math.cos(ang + 0.45), by2 - 22 * math.sin(ang + 0.45))], fill=col)
                if e.get('label'):
                    f_ = F(True, 30); lw = d.textlength(e['label'], font=f_); lx = max(SX0, min(bx2 - lw / 2, CX1 - lw)); ly = min(max(CY0, by2 + (-50 if by2 > ay_ else 14)), LY1 - 40)
                    d.text((lx, ly), e['label'], font=f_, fill=col, stroke_width=3, stroke_fill=(0, 0, 0))
        # the gia hien tai ben phai
        yl = min(Y(last['c']), LY1 - 24); colL = UP if last['c'] >= last['o'] else DN
        dashed(d, X(len(vis) - 1) + bw, CX1 + 10, yl, colL, 2, 8, 8)
        fT = F(True, 28); tag = vn(last['c']); tw = d.textlength(tag, font=fT)
        while CX1 + 18 + tw > SX1 - 4 and fT.size > 20: fT = F(True, fT.size - 2); tw = d.textlength(tag, font=fT)
        d.rounded_rectangle([CX1 + 10, yl - 22, CX1 + 24 + tw, yl + 22], 8, fill=colL)
        d.text((CX1 + 17, yl - 18), tag, font=fT, fill=WHITE)
        # so lon goc tren panel
        cnt = [e for e in active if e['type'] == 'count' and tv - e['t'] < float(e.get('hold', 5))]
        if cnt:
            e = cnt[-1]; q = ease((tv - e['t']) / 1.2); val = e['from'] + (e['to'] - e['from']) * q
            big = vn(val); sub = e.get('label', ''); subc = UP if e['to'] >= e['from'] else DN
        else:
            ref = sp.get('ref') or {'price': o0, 'label': 'so với ' + C[0]['t']}
            rl = [e for e in lv]
            if rl and not sp.get('ref'): ref = {'price': rl[-1]['price'], 'label': ('trên ' if last['c'] >= rl[-1]['price'] else 'dưới ') + rl[-1].get('label', '').lower()}
            big = vn(last['c']); ch_ = last['c'] - ref['price']; sub = ('+' if ch_ >= 0 else '−') + vn(abs(ch_)) + ' USD ' + ref['label']; subc = UP if ch_ >= 0 else DN
        d.text((PX0 + 26, PY0 + 18), big, font=F(True, 84), fill=WHITE)
        fS = F(True, 36)
        while d.textlength(sub, font=fS) > PX1 - PX0 - 50 and fS.size > 24: fS = F(True, fS.size - 2)
        d.text((PX0 + 30, PY0 + 116), sub, font=fS, fill=subc)
        tl = last['t']; d.text((PX1 - 26 - d.textlength(tl, font=F(False, 30)), PY0 + 34), tl, font=F(False, 30), fill=MUTED)
        # chu to giua man hinh
        pops = [e for e in active if e['type'] == 'pop' and tv - e['t'] < float(e.get('hold', 1.6))]
        ox = oy = 0
        if pops:
            e = pops[-1]; ts = tv - e['t']
            if e.get('fx') == 'shake' and ts < 0.6:
                amp = 14 * (1 - ts / 0.6); ox = int(amp * math.sin(ts * 90)); oy = int(amp * math.cos(ts * 71))
            if e.get('fx') in ('shake', 'flash') and ts < 0.25:
                im = Image.blend(im, Image.new('RGB', (W, H), WHITE), 0.55 * (1 - ts / 0.25)); d = ImageDraw.Draw(im)
            hd = float(e.get('hold', 1.6)) - 0.3
            sz = int(118 * (1.35 - 0.35 * ease(ts / 0.18))) if ts < hd else int(118 * (1 - (ts - hd) / 0.3 * 0.2))
            a = 1.0 if ts < hd else max(0.0, 1 - (ts - hd) / 0.3)
            txt = e['text'].upper(); f2 = F(True, max(40, sz)); tw = d.textlength(txt, font=f2)
            while tw > TW - 60 and f2.size > 36: f2 = F(True, f2.size - 4); tw = d.textlength(txt, font=f2)
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            yc = (CY0 + LY1) / 2 - 70
            od.rounded_rectangle([(W - tw) / 2 - 40, yc - 20, (W + tw) / 2 + 40, yc + f2.size + 40], 28, fill=(0, 0, 0, int(200 * a)))
            od.text(((W - tw) / 2, yc), txt, font=f2, fill=(*(GOLD if e.get('color') != 'red' else KEY), int(255 * a)), stroke_width=4, stroke_fill=(0, 0, 0, int(255 * a)))
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
        if ox or oy:
            im = im.transform((W, H), Image.AFFINE, (1, 0, -ox, 0, 1, -oy), fillcolor=BG); d = ImageDraw.Draw(im)
        # hook 0-2.6s
        if hook and tv < 2.6 and news:   # 26/11 the BAN TIN kieu thoi su: nhan + ngay, tieu de tren nen mau page, dong nguon
            q = ease(min(1.0, (tv + LEAD) / 0.25)) * (1 - ease(max(0.0, tv - 2.3) / 0.3))
            fHk = F(True, 80)
            while len(wrap_bal(d, hook, fHk, TW - 60)) > 4 and fHk.size > 52: fHk = F(True, fHk.size - 4)
            hl = wrap_bal(d, hook, fHk, TW - 60)[:4]; lhk = int(fHk.size * 1.18)
            kick = (news.get('kicker') or 'BẢN TIN VÀNG') + ('  ·  ' + news['date'] if news.get('date') else '')
            fK = F(True, 38); kw = d.textlength(kick, font=fK)
            hh = lhk * len(hl) + 60; y0 = (CY0 + LY1) / 2 - hh / 2 - 10
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rectangle([0, PY0, W, CY1], fill=(*BG, int(150 * q)))
            od.rounded_rectangle([SX0, y0, SX1, y0 + hh], 18, fill=(*GOLD, int(245 * q)))
            od.rounded_rectangle([SX0, y0 - 74, SX0 + kw + 44, y0 - 10], 14, fill=(255, 255, 255, int(250 * q)))
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            if q > 0.05:
                d.text((SX0 + 22, y0 - 68), kick, font=fK, fill=GOLD)
                for j, ln in enumerate(hl):
                    d.text((SX0 + 30, y0 + 30 + j * lhk), ln, font=fHk, fill=ON_ACC if ON_ACC != INK else INK)
                src = news.get('source', '')
                if src: d.text((SX0 + 6, y0 + hh + 18), src, font=F(True, 32), fill=GOLD2, stroke_width=2, stroke_fill=(0, 0, 0))
        elif hook and tv < 2.6:
            q = ease(min(1.0, (tv + LEAD) / 0.25)) * (1 - ease(max(0.0, tv - 2.3) / 0.3))
            fHk = F(True, 88)
            while len(wrap_bal(d, hook, fHk, TW - 40)) > 3 and fHk.size > 56: fHk = F(True, fHk.size - 4)
            hl = wrap_bal(d, hook, fHk, TW - 40)[:3]; lhk = int(fHk.size * 1.2); hh = lhk * len(hl) + 56
            y0 = (CY0 + LY1) / 2 - hh / 2 - 40
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([SX0, y0, SX1, y0 + hh], 30, fill=(10, 10, 16, int(225 * q)))
            od.rounded_rectangle([SX0, y0, SX1, y0 + hh], 30, outline=(*GOLD, int(255 * q)), width=5)
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            if q > 0.05:
                f2 = F(True, int(fHk.size * (0.85 + 0.15 * q)))
                for j, ln in enumerate(hl): text_c(d, y0 + 30 + j * lhk, ln, f2, GOLD, 5)
        # phu de karaoke
        cur = next((s for s in wts if s[0] - 0.05 <= tv < s[1] + 0.1), None)
        if cur and t < D - TAIL:
            # 28/11 chu chot: phu de nho lai (46px), toi da 2 dong, vien mong + nen toi -> net tren dien thoai
            ws = cur[2]; txt = ' '.join(w for _, _, w in ws); fC = F(True, SUB_PX)
            allL = wrap_bal(d, txt, fC, TW - 40); LH = int(fC.size * 1.3)
            # dong co tu dang doc -> hien trang 2 dong chua no
            cnt_, cw = 0, 0
            for j, ln in enumerate(allL):
                n_ = len(ln.split(' '))
                if any(a_ <= tv for a_, _, _ in ws[cnt_:cnt_ + n_]): cw = j
                cnt_ += n_
            pg = cw // SUB_LINES; lines = allL[pg * SUB_LINES:(pg + 1) * SUB_LINES]
            wi = sum(len(l_.split(' ')) for l_ in allL[:pg * SUB_LINES])
            y = SY1 - 8 - len(lines) * LH
            bwm = max(d.textlength(l_, font=fC) for l_ in lines)
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).rounded_rectangle([(W - bwm) / 2 - 24, y - 12, (W + bwm) / 2 + 24, y + len(lines) * LH + 4], 16, fill=(0, 0, 0, 170))
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            for j, ln in enumerate(lines):
                x = (W - d.textlength(ln, font=fC)) / 2
                for wd in ln.split(' '):
                    a_, b_, _ = ws[wi] if wi < len(ws) else (0, 0, wd); wi += 1
                    s_ = wd.strip('.,!?…:;"“”')
                    key = (s_.isupper() and len(s_) > 1) or re.match(r'^[\d.,%+\-]+$', s_ or 'x')
                    wl = d.textlength(wd, font=fC)
                    if a_ <= tv < b_ + 0.02:
                        d.rounded_rectangle([x - 5, y + j * LH - 2, x + wl + 5, y + j * LH + LH - 6], 8, fill=GOLD)
                        d.text((x, y + j * LH), wd, font=fC, fill=ON_ACC)
                    else:
                        col = (GOLD2 if key else (WHITE if tv >= a_ else (200, 206, 220)))
                        d.text((x, y + j * LH), wd, font=fC, fill=col, stroke_width=1, stroke_fill=(0, 0, 0))
                    x += d.textlength(wd + ' ', font=fC)
        # ket: vong lap + theo doi
        if t >= D - TAIL:
            q = ease((t - (D - TAIL)) / 0.35)
            im = Image.blend(im, Image.new('RGB', (W, H), BG), 0.88 * q); d = ImageDraw.Draw(im)
            if q > 0.5:
                outro = (sp.get('outro') or '').strip()
                y = 600; fO = F(True, 68)
                while len(wrap_bal(d, outro, fO, TW)) > 3 and fO.size > 44: fO = F(True, fO.size - 4)
                for ln in wrap_bal(d, outro, fO, TW)[:3]:
                    text_c(d, y, ln, fO, WHITE, 4); y += int(fO.size * 1.35)
                lab = sp.get('cta', 'THEO DÕI VÀNG 20 GIÂY'); fB = F(True, 50); bw_ = d.textlength(lab, font=fB)
                while bw_ > TW - 80 and fB.size > 30: fB = F(True, fB.size - 2); bw_ = d.textlength(lab, font=fB)
                d.rounded_rectangle([(W - bw_) / 2 - 40, y + 60, (W + bw_) / 2 + 40, y + 156], 34, fill=GOLD)
                d.text(((W - bw_) / 2, y + 78), lab, font=fB, fill=ON_ACC)
                text_c(d, y + 196, sp.get('cta_sub', 'Mỗi ngày 1 pha giá thật'), F(False, 38), MUTED, 0)
                # mien tru: QC 23-24/11 che ~1,5% khung, kho doc tren dien thoai -> 34 -> 46px, vien den
                text_c(d, y + 262, 'Thông tin tham khảo', F(True, 46), GOLD2, 3)
                text_c(d, y + 324, 'Không phải khuyến nghị đầu tư', F(True, 46), GOLD2, 3)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    # am thanh: giong + nhac nho + whoosh khi chay nen + sting khi pop
    mus = os.path.join(ROOT, 'editor', 'story', sp.get('music', 'music_b.mp3'))
    wh = sfx('whoosh', os.path.join(OUT, 'wh.wav')); st = sfx('sting', os.path.join(OUT, 'st.wav')); pp = sfx('pop', os.path.join(OUT, 'pp.wav'))
    ev = []
    for e in evs:
        if e['type'] == 'goto': ev.append((e['t'] + LEAD - 0.1, wh, 0.3))
        elif e['type'] == 'pop': ev.append((e['t'] + LEAD, st if e.get('fx') in ('shake', 'flash') else pp, 0.55))
        elif e['type'] in ('level', 'mark', 'zone', 'arrow'): ev.append((e['t'] + LEAD, pp, 0.35))
        elif e['type'] == 'path': ev.append((e['t'] + LEAD - 0.1, wh, 0.3))
    if hook: ev.append((LEAD, st, 0.5))
    ins, fl = [], []
    for j, (tt, f_, vol) in enumerate(ev):
        ins += ['-i', f_]; ms = max(0, int(tt * 1000))
        fl.append(f'[{3 + j}:a]adelay={ms}|{ms},volume={vol}[e{j}]')
    mixin = '[v][m]' + ''.join(f'[e{j}]' for j in range(len(ev)))
    fc = f'[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)}[v];[2:a]volume=0.10[m];' + ''.join(x + ';' for x in fl) + \
         f'{mixin}amix=inputs={2 + len(ev)}:duration=first:normalize=0,apad,loudnorm=I=-15:TP=-1.5[a]'
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', voice, '-stream_loop', '-1', '-i', mus] + ins +
                          ['-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    print('ok', round(D, 2))


if __name__ == '__main__':
    main()
