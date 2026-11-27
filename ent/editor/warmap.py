"""Chiến Sử Ký - ban do tran danh chay theo tung ngay (kieu By The Clock) 9:16, CO GIONG DOC tu 23/11 (spec.voice=false de tat; event.say = loi doc day du): dem ngay + ngay thang,
cu diem doi mau khi that thu, mui ten tan cong, hao vay lan, chu su kien, nhac tram + tieng phao.
SPEC_JSON: {"title","sub","start_date":"1954-03-13","days":56,"phases":[[d0,d1,giay],...],"intro":"...",
  "nodes":[{"name","x","y","fall":ngay,"from":[x,y],"atk":so_ngay_danh,"big":bool}],"events":[{"day","text"}],
  "siege":[ngay_bat_dau, ngay_ket_thuc] | false,"stats":["..."],"end":["..."],"note":"Bản đồ minh họa giản lược",
  "unit":"NGÀY|GIỜ|TUẦN|THÁNG|NĂM" (bo dem), "step_labels":{"1":"13/03/1954",..} (nhan thoi gian tung buoc, bo trong = tu tinh tu start_date khi unit NGÀY),
  "terrain":"valley|plain|coast", "rivers", "sea", "hills", "places", "airstrip", "rim" (vi tri phao ta), "label_us","label_them"}"""
import datetime, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safezone  # noqa: E402  khoa cung bo cuc 20/11
import fx  # noqa: E402  23/11: whoosh doi su kien, ha nhac khi co loi, grade phim tai lieu
from r3 import W, H, FPS, SR, OUT, TMP, load_spec, place, tone, boom, noise, write_audio, Vid, mux, fnt, wrap_bal, ease, decode  # noqa: E402
import json, re, urllib.request  # noqa: E402

MX0, MY0, MS = 195, 462, 690  # khung ban do vuong (22/11: 740->690 de du cho chu su kien to doc duoc tren dien thoai)
# 22/11 bai hoc kenh Dat + QC W53: chu chinh phai doc duoc tren dien thoai -> co chu toi thieu (px tren khung 1080x1920)
MIN_EVENT = 40; EVENT_PX = 50; KEY_PX = 58; LABEL_PX = 34; PLACE_PX = 32; SUB_PX = 48; END_PX = 50
RED = (220, 38, 38); BLUE = (40, 110, 230); GOLD = (250, 204, 21); WHITE = (245, 245, 240); BG = (12, 16, 14)


# ---------------- 23/11: GIONG DOC (chu: "noi dung ban do khong hut view, them am thanh") ----------------
# spec.voice mac dinh BAT: moi su kien duoc doc bang giong Nhat Khoa (W87), thoi luong moi su kien = do dai giong.
# Su kien co the co "say" (loi doc day du); khong co thi doc "text" (bo dau ':' -> '.'). spec.intro_say doc o man mo dau.
W87 = os.environ.get('AVF_TTS_URL', '')   # 27/11: repo cong khai -> cong W97 (X-AVF-Key), khong ghi dia chi trong code
_SO = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']


def _doc3(n, full):
    tr, ch, dv = n // 100, n // 10 % 10, n % 10; o = []
    if full or tr: o.append(_SO[tr] + ' trăm')
    if ch == 0:
        if dv and (full or tr): o.append('linh')
    elif ch == 1: o.append('mười')
    else: o.append(_SO[ch] + ' mươi')
    if dv:
        if dv == 1 and ch > 1: o.append('mốt')
        elif dv == 5 and ch > 0: o.append('lăm')
        elif dv == 4 and ch > 1: o.append('tư')
        else: o.append(_SO[dv])
    return ' '.join(o)


def so_chu(n):
    if n == 0: return 'không'
    parts = []; units = ['', ' nghìn', ' triệu', ' tỷ']; i = 0; first = True
    grp = []
    while n: grp.append(n % 1000); n //= 1000
    for i in range(len(grp) - 1, -1, -1):
        g = grp[i]
        if g == 0: continue
        parts.append(_doc3(g, i < len(grp) - 1) + units[i])
    return ' '.join(parts).strip()


_MK = re.compile(r'(\{(?:chậm|rất chậm|nhấn|hạ|nhanh|cao)\s*:|\}|\[nghỉ\s*[\d.,]+\s*\]|(?:(?<=\s)|^)/{1,3}(?=\s|$))', re.I)


def loi_doc(t):
    """25/11: giu nguyen ky hieu ngat nghi (skill giong-doc-ngat-nghi, W87 v3): chi doi so -> chu o phan chu."""
    if not _MK.search(t or ''): return _loi_doc(t)
    return re.sub(r'\s+', ' ', ''.join(x if _MK.fullmatch(x) else ' ' + _loi_doc(x) + ' ' for x in _MK.split(t) if x)).strip()


def _loi_doc(t):
    t = re.sub(r'^\s*Ý chính\s*:\s*', '', t)
    t = re.sub(r'(\d)\s*km\b', r'\1 ki lô mét', t)
    t = re.sub(r'(?i)\bngày\s+(?=\d{1,2}/\d{1,2}/\d{3,4})', '', t)
    t = re.sub(r'(\d{1,2})/(\d{1,2})/(\d{3,4})', lambda m: 'ngày %s tháng %s năm %s' % (so_chu(int(m.group(1))), so_chu(int(m.group(2))), so_chu(int(m.group(3)))), t)
    t = re.sub(r'(\d{1,2})/(\d{3,4})', lambda m: 'tháng %s năm %s' % (so_chu(int(m.group(1))), so_chu(int(m.group(2)))), t)
    t = re.sub(r'(?i)\bngày\s+(?=\d{1,2}/\d{1,2}\b)', '', t)
    t = re.sub(r'(\d{1,2})/(\d{1,2})\b', lambda m: 'ngày %s tháng %s' % (so_chu(int(m.group(1))), so_chu(int(m.group(2)))), t)
    t = re.sub(r'(\d{1,2})h(\d{2})\b', lambda m: '%s giờ %s' % (so_chu(int(m.group(1))), so_chu(int(m.group(2))) if int(m.group(2)) else ''), t)
    t = re.sub(r'(\d{1,2})h\b', lambda m: so_chu(int(m.group(1))) + ' giờ', t)
    t = re.sub(r'(\d+)[.,](\d{3})(?!\d)', lambda m: m.group(1) + m.group(2), t)
    t = re.sub(r'(\d+),(\d+)', lambda m: so_chu(int(m.group(1))) + ' phẩy ' + so_chu(int(m.group(2))), t)
    t = re.sub(r'\d+', lambda m: so_chu(int(m.group(0))), t)
    t = t.replace('%', ' phần trăm').replace(':', '.').replace('–', ' đến ').replace(' - ', ', ')
    return re.sub(r'\s+', ' ', t).strip()


def tts_one(text, tag):
    body = json.dumps({'text': text, 'speed': 0.95, 'tag': tag}).encode()
    for k in range(3):
        try:
            req = urllib.request.Request(W87, data=body, headers={'Content-Type': 'application/json', 'X-AVF-Key': os.environ.get('AVF_KEY', '')})
            with urllib.request.urlopen(req, timeout=600) as r: j = json.loads(r.read())
            if j.get('ok'):
                segs = []
                for u, p in zip(j['voice_urls'], j['pauses']):
                    a = decode(u); segs.append(a); segs.append(np.zeros(int(SR * float(p or 0)), np.float32))
                return np.concatenate(segs) if segs else None
            print('W87 loi', tag, str(j)[:160])
        except Exception as ex: print('W87 that bai', tag, k, type(ex).__name__)
    return None


def build_voice(sp):
    """tra (intro_audio|None, [audio su kien]) hoac None neu tat/loi -> ban do chay nhu cu."""
    if sp.get('voice') is False or not sp.get('events'): return None
    from multiprocessing.pool import ThreadPool
    evs = sorted(sp['events'], key=lambda e: e['day'])
    jobs = [('intro', loi_doc(sp.get('intro_say') or sp.get('intro') or ''))] + [('e%d' % i, loi_doc(e.get('say') or e['text'])) for i, e in enumerate(evs)]
    with ThreadPool(4) as tp:
        res = tp.map(lambda j: tts_one(j[1], 'csk-' + j[0]) if j[1] else None, jobs)
    if any(r is None for r in res[1:]):
        print('giong doc thieu -> dung ban khong giong'); return None
    return res[0], res[1:]


def P(x, y): return (MX0 + x * MS, MY0 + y * MS)


def eout(t):
    """ease-out cubic (vao nhanh, cham dan) cho chu xuat hien - 22/11 bai hoc kenh Dat."""
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


def base_map(sp):
    """dia hinh gian luoc. spec: terrain 'valley'(long chao, mac dinh)|'plain'|'coast'; rivers [[[x,y],..],..];
    sea [[x,y],..] (vung bien/vinh); places [{name,x,y}] (dia danh phu); airstrip [x,y0,y1] hoac bo trong"""
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    terrain = sp.get('terrain', 'valley')
    if terrain == 'valley':
        for k in range(14):
            r = 0.72 - k * 0.028; c = (24 + k * 4, 40 + k * 5, 28 + k * 3)
            d.ellipse([P(0.5 - r * 0.62, 0.48 - r), P(0.5 + r * 0.62, 0.48 + r)], fill=c)
        rnd = random.Random(3)
        for _ in range(260):  # bong nui quanh vanh
            a = rnd.random() * 2 * math.pi; rr = 0.42 + rnd.random() * 0.12
            x, y = 0.5 + math.cos(a) * rr * 0.75, 0.48 + math.sin(a) * rr
            if 0 < x < 1 and 0 < y < 1:
                s_ = 0.012 + rnd.random() * 0.02; d.polygon([P(x - s_, y + s_ * 0.7), P(x, y - s_), P(x + s_, y + s_ * 0.7)], fill=(30, 52, 34))
    else:
        d.rectangle([P(0, 0), P(1, 1)], fill=(44, 62, 42))
        rnd = random.Random(4)
        for (mx, my, mr) in sp.get('hills', []):  # cum doi nui [x,y,ban_kinh]
            for _ in range(int(60 * mr / 0.1)):
                a = rnd.random() * 2 * math.pi; rr = rnd.random() * mr
                x, y = mx + math.cos(a) * rr, my + math.sin(a) * rr; s_ = 0.01 + rnd.random() * 0.015
                d.polygon([P(x - s_, y + s_ * 0.7), P(x, y - s_), P(x + s_, y + s_ * 0.7)], fill=(32, 50, 32))
    if sp.get('sea'):
        d.polygon([P(x, y) for x, y in sp['sea']], fill=(30, 62, 96))
    rivers = sp.get('rivers')
    if rivers is None:  # song mac dinh (Nam Rom)
        rivers = [[(0.55 + 0.03 * math.sin(i / 6.0), i / 40.0) for i in range(41)]]
    for rv in rivers:
        d.line([P(x, y) for x, y in rv], fill=(60, 120, 170), width=int(sp.get('river_w', 8)))
    ax = sp.get('airstrip', [0.44, 0.34, 0.62]) if terrain == 'valley' else sp.get('airstrip')
    f = fnt(False, PLACE_PX)
    if ax:
        d.rectangle([P(ax[0] - 0.008, ax[1]), P(ax[0] + 0.008, ax[2])], fill=(90, 90, 84))
        d.text(P(ax[0] - 0.05, ax[2] + 0.01), 'Sân bay', font=f, fill=(170, 170, 160))
    for pl in sp.get('places', []):
        x0, y0 = P(pl['x'], pl['y']); d.text((x0 - d.textlength(pl['name'], font=f) / 2, y0), pl['name'], font=f, fill=(190, 200, 210))
    d.rectangle([0, MY0 - 10, W, MY0 - 6], fill=(40, 50, 44)); d.rectangle([0, MY0 + MS + 6, W, MY0 + MS + 10], fill=(40, 50, 44))
    if sp.get('backdrop', True):   # 23/11: lap kin khung doc – ban do phong to, mo, toi lam nen (het khoang den tren/duoi)
        from PIL import ImageFilter
        sq = im.crop((MX0, MY0, MX0 + MS, MY0 + MS))
        k = max(W, H) / MS * 1.02; bg = sq.resize((int(MS * k), int(MS * k)), Image.BILINEAR)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        bg = Image.blend(bg.filter(ImageFilter.GaussianBlur(12)), Image.new("RGB", (W, H), BG), 0.3)
        bg.paste(im.crop((0, MY0 - 10, W, MY0 + MS + 11)), (0, MY0 - 10))
        im = bg
    return im


def date_of(sp, day):
    d0 = datetime.date.fromisoformat(sp['start_date'])
    return (d0 + datetime.timedelta(days=max(1, day) - 1)).strftime('%d/%m/%Y')


def arrow(d, a, b, w, col):
    d.line([a, b], fill=col, width=w)
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); s = w * 2.6
    d.polygon([b, (b[0] - s * math.cos(ang - 0.45), b[1] - s * math.sin(ang - 0.45)),
               (b[0] - s * math.cos(ang + 0.45), b[1] - s * math.sin(ang + 0.45))], fill=col)


def fit(d, s, size, bold=True, maxw=None):
    maxw = maxw or safezone.MAXW_C540; f = fnt(bold, size)
    while d.textlength(s, font=f) > maxw and f.size > 30: f = fnt(bold, f.size - 4)
    return f


def split_key(text):
    """22/11: 'Hà Hồi đầu hàng: địch bỏ đồn...' -> ('HÀ HỒI ĐẦU HÀNG', 'địch bỏ đồn...'). Mot diem nhin: cum y chinh to, mau nhan."""
    k = text.find(':')
    if 0 < k <= 40 and len(text[:k].split()) <= 6 and text[k + 1:].strip():
        r = text[k + 1:].strip(); return text[:k].strip().upper(), r[:1].upper() + r[1:]
    return '', text


def cap_layout(d, text, avail):
    """chon co chu lon nhat vua chieu cao avail. Khong thu nho duoi MIN_EVENT: qua dai -> dung may (spec phai rut gon)."""
    key, rest = split_key(text)
    for size in range(EVENT_PX, MIN_EVENT - 1, -2):
        f = fnt(False, size); lines = wrap_bal(d, rest, f, 780); lh = int(size * 1.28)
        fk = fnt(True, KEY_PX - (EVENT_PX - size)) if key else None
        if fk is not None and d.textlength(key, font=fk) > 780: fk = fit(d, key, fk.size, True, 780)
        hk = int(fk.size * 1.2) + 6 if fk else 0
        hh = hk + lh * len(lines) + 30
        if len(lines) <= 3 and hh <= avail: return key, fk, lines, f, lh, hk, hh
    raise SystemExit('LOI BO CUC: su kien qua dai, chu se nho hon %dpx: %s' % (MIN_EVENT, text[:60]))


def caption(d, lay, y, al=1.0, dy=0):
    """ve khoi su kien; al/dy cho hieu ung vao (ease-out: mo dan + truot len)."""
    key, fk, lines, f, lh, hk, hh = lay; y = y + dy
    d.rounded_rectangle([100, y, 940, y + hh], 18, fill=(0, 0, 0, int(225 * al)))
    if key:
        d.text((520 - d.textlength(key, font=fk) / 2, y + 14), key, font=fk, fill=GOLD + (int(255 * al),))
    for i, l in enumerate(lines):
        d.text((520 - d.textlength(l, font=f) / 2, y + 15 + hk + i * lh), l, font=f, fill=WHITE + (int(255 * al),))


def layout_labels(d, nodes, sp):
    """21/11: dat nhan cu diem khong de nhau / khong de o vuong / khong de dia danh. Thu 8 vi tri, het cho thi thu nho chu."""
    def box_txt(cx, top, s, f): w = d.textlength(s, font=f); return (cx - w / 2, top, cx + w / 2, top + f.size * 1.15)
    def hit(a, b, pad=4): return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])
    obst = []
    fp = fnt(False, PLACE_PX)
    for pl in sp.get('places', []):
        x0, y0 = P(pl['x'], pl['y']); obst.append(box_txt(x0, y0, pl['name'], fp))
    for n in nodes:
        r = 0.03 if n.get('big') else 0.022; a = P(n['x'] - r, n['y'] - r); b = P(n['x'] + r, n['y'] + r); obst.append((a[0], a[1], b[0], b[1]))
    out = {}
    for n in sorted(nodes, key=lambda n: (not n.get('big'), n['y'])):
        r = 0.03 if n.get('big') else 0.022; cx, cy = P(n['x'], n['y']); rp = r * MS
        best = None
        for size in (LABEL_PX, LABEL_PX - 4, LABEL_PX - 8):
            f = fnt(True, size); w = d.textlength(n['name'], font=f); h = f.size * 1.15
            cands = [(cx, cy + rp + 6), (cx, cy - rp - 6 - h), (cx + rp + 8 + w / 2, cy - h / 2), (cx - rp - 8 - w / 2, cy - h / 2),
                     (cx + rp + w / 2, cy + rp + 4), (cx - rp - w / 2, cy + rp + 4), (cx + rp + w / 2, cy - rp - 4 - h), (cx - rp - w / 2, cy - rp - 4 - h)]
            for (mx, top) in cands:
                bx = box_txt(mx, top, n['name'], f)
                if bx[0] < MX0 + 4 or bx[2] > MX0 + MS - 4 or bx[1] < MY0 + 4 or bx[3] > MY0 + MS - 4: continue
                k = sum(1 for o in obst if hit(bx, o))
                if best is None or k < best[0]: best = (k, mx, top, f, bx)
                if k == 0: break
            if best and best[0] == 0: break
        _, mx, top, f, bx = best
        obst.append(bx); out[n['name']] = (mx, top, f)
    return out


def main():
    sp = load_spec(); nodes = sp['nodes']
    intro = sp.get('intro_sec', 4.0)
    vo = build_voice(sp)
    # bang thoi gian: t -> ngay (so thuc)
    segs = []; t = intro; voice_at = []
    if vo:   # co giong: moi su kien chiem dung do dai cau doc, ngay chay tu ngay su kien nay sang su kien sau
        ia, eas = vo; evs_v = sorted(sp['events'], key=lambda e: e['day'])
        if ia is not None: intro = max(intro, len(ia) / SR + 0.5); voice_at.append((0.25, ia))
        t = intro
        for i, e in enumerate(evs_v):
            sec = len(eas[i]) / SR + 0.3   # 23/11: nghi 0.45 -> 0.3 de video gon ve <= 60s
            d0 = e['day'] if i else 0; d1 = (evs_v[i + 1]['day'] - 0.001) if i + 1 < len(evs_v) else sp['days']
            if i == 0 and e['day'] > 0: segs.append((t, t + 1.2, 0, e['day'] - 0.001)); t += 1.2; d0 = e['day']
            segs.append((t, t + sec, d0, max(d0, d1))); voice_at.append((t + 0.1, eas[i])); t += sec
    else:
        for d0, d1, sec in sp['phases']:
            segs.append((t, t + sec, d0, d1)); t += sec
    t_days = t; stats_d = 5.5; end_d = 3.5; dur = t_days + stats_d + end_d

    def day_at(tt):
        if tt < intro: return 0.0
        for a, b, d0, d1 in segs:
            if tt < b: return d0 + (d1 - d0 + 0.999) * ((tt - a) / (b - a))
        return float(sp['days']) + 0.999

    # am thanh: trong tram + phao khi co cu diem that thu + tick doi ngay
    a = np.zeros(int(SR * dur), np.float32); beat = 60 / 72
    for k in range(int(dur / beat)):
        place(a, boom(0.7, 0.22 if k % 4 else 0.34), k * beat)
    prev = -1; fall_t = {}
    for fi in range(int(t_days * FPS)):
        tt = fi / FPS; dd = int(day_at(tt))
        if dd != prev and dd >= 1:
            place(a, tone(1800, 0.03, 0.08, a=0.001, r=0.02), tt); prev = dd
        for n in nodes:
            if n['name'] not in fall_t and day_at(tt) >= n['fall'] + 0.85:
                fall_t[n['name']] = tt
                for j in range(4): place(a, boom(1.2, 0.6), tt - 0.6 + j * 0.18)
    place(a, tone(220, 4.0, 0.06, a=0.6, r=2) + tone(277.2, 4.0, 0.05, a=0.6, r=2) + tone(329.6, 4.0, 0.05, a=0.6, r=2), t_days)
    if vo:   # giong doc len tren; 23/11: nhac + phao tu ha khi co loi (ducking), len lai khi nghi; whoosh moi lan sang su kien
        a *= 0.6; vv = np.zeros_like(a)
        for t0, va in voice_at:
            i0 = int(t0 * SR); n = min(len(va), len(vv) - i0)
            if n > 0: vv[i0:i0 + n] += va[:n] * 0.9
        a = fx.duck(a, vv, depth=0.6)
        for j, (t0, _) in enumerate(voice_at[1:] if len(voice_at) > 1 else []):
            place(a, fx.whoosh(0.4, 0.14, up=(j % 2 == 0), seed=j), max(0, t0 - 0.3))
        a = a + vv
    apath = os.path.join(TMP, 'a.wav'); write_audio(a, apath)

    bm = base_map(sp)
    ft = fnt(True, 58); fs = fnt(False, 30); fday = fnt(True, 60); fdate = fnt(False, 34)
    os.environ.setdefault('VID_VF', fx.grade_vf(sp.get('grade', 'war')))
    vpath = os.path.join(TMP, 'v.mp4'); v = Vid(vpath)
    rnd = random.Random(5)
    labpos = layout_labels(ImageDraw.Draw(bm), nodes, sp)
    dim = Image.blend(bm, Image.new('RGB', (W, H), BG), 0.72)  # nen the so lieu / man ket: ban do mo
    # su kien: thoi diem bat dau (de lam hieu ung vao) + bo cuc chu tinh truoc (kiem co chu toi thieu ngay tu dau)
    cap_y = MY0 + MS + 56; dd0 = ImageDraw.Draw(bm.copy(), 'RGBA')
    evs_all = sorted(sp.get('events', []), key=lambda e: e['day']); ev_t = {}
    import doc_so; evs_all = [dict(e, text=doc_so.chuan_dau(e['text'])) for e in evs_all]   # 23/11: dau kieu bao chi tren chu
    for fi in range(int(t_days * FPS) + 1):
        dy_ = day_at(fi / FPS)
        for k, e in enumerate(evs_all):
            if k not in ev_t and e['day'] <= dy_: ev_t[k] = fi / FPS
    ev_lay = [cap_layout(dd0, e['text'], 1455 - cap_y) for e in evs_all]
    rim = [tuple(p) for p in sp['rim']] if 'rim' in sp else ([(0.5 + math.cos(a_) * 0.36, 0.48 + math.sin(a_) * 0.55) for a_ in np.linspace(0, 2 * math.pi, 22, endpoint=False)] if sp.get('terrain', 'valley') == 'valley' else [])
    for fi in range(int(dur * FPS)):
        tt = fi / FPS
        if tt >= t_days:  # the so lieu + ket
            fr = dim.copy(); d = ImageDraw.Draw(fr)
            if tt < t_days + stats_d:
                te = tt - t_days; y = 600
                ft2 = fit(d, sp['title'], 58); d.text(((W - d.textlength(sp['title'], font=ft2)) / 2, 420), sp['title'], font=ft2, fill=GOLD)
                for i, s in enumerate(sp.get('stats', [])):
                    al = eout((te - 0.15 - i * 0.6) / 0.35)
                    if al <= 0: continue
                    f2 = fnt(True, 58)
                    for ln in wrap_bal(d, s, f2, safezone.MAXW_C540):
                        d.text(((W - d.textlength(ln, font=f2)) / 2, y), ln, font=f2, fill=tuple(int(c * al) for c in WHITE)); y += 74
                    y += 50
            else:
                te = tt - t_days - stats_d; y = 760
                for i, s in enumerate(sp.get('end', [])):
                    f2 = fnt(i != 1, 60 if i == 0 else END_PX); col = GOLD if i == 0 else WHITE
                    al = eout((te - i * 0.4) / 0.35)
                    for ln in wrap_bal(d, s, f2, safezone.MAXW_C540):
                        d.text(((W - d.textlength(ln, font=f2)) / 2, y), ln, font=f2, fill=tuple(int(c * al) for c in col)); y += int(f2.size * 1.3)
                    y += 30
            v.put(fr); continue
        day = day_at(tt); di = int(day)
        fr = bm.copy(); d = ImageDraw.Draw(fr, 'RGBA')
        # phao ta tren nui (tu ngay 1)
        if di >= 1:
            for (x, y) in rim:
                d.ellipse([P(x - 0.009, y - 0.009), P(x + 0.009, y + 0.009)], fill=RED)
        # hao vay lan: tu vanh vao trong theo ngay
        s0, s1 = sp.get('siege', [6, 56]) if sp.get('siege', True) else (10 ** 9, 10 ** 9 + 1)
        if day >= s0:
            pr = min(1.0, (day - s0) / max(1, s1 - s0))
            for (x, y) in rim[::2]:
                ex = x + (0.48 - x) * 0.75 * pr; ey = y + (0.48 - y) * 0.75 * pr
                d.line([P(x, y), P(ex, ey)], fill=(220, 38, 38, 170), width=5)
        # mui ten tan cong
        for n in nodes:
            atk = n.get('atk', 1)
            if day >= 1 and n['fall'] - atk + 0.0 <= day < n['fall'] + 0.9 and n.get('from'):
                arrow(d, P(*n['from']), P(n['x'] + (n['from'][0] - n['x']) * 0.18, n['y'] + (n['from'][1] - n['y']) * 0.18), 9, RED)
        # cu diem
        for n in nodes:
            fallen = day >= n['fall'] + 0.85; r = 0.03 if n.get('big') else 0.022
            x, y = n['x'], n['y']
            if fallen:
                ft_ = fall_t.get(n['name'], 0); age = tt - ft_
                if 0 <= age < 1.0:
                    rr = r + 0.08 * ease(age); al = int(255 * (1 - age))
                    d.ellipse([P(x - rr, y - rr), P(x + rr, y + rr)], outline=(250, 204, 21, al), width=6)
                d.rectangle([P(x - r, y - r), P(x + r, y + r)], fill=RED, outline=(255, 255, 255), width=3)
            else:
                d.ellipse([P(x - r * 2.2, y - r * 2.2), P(x + r * 2.2, y + r * 2.2)], fill=(40, 110, 230, 60))
                d.rectangle([P(x - r, y - r), P(x + r, y + r)], fill=BLUE, outline=(255, 255, 255), width=3)
            mx_, top_, f_ = labpos[n['name']]
            d.text((mx_ - d.textlength(n['name'], font=f_) / 2, top_), n['name'], font=f_, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
        # dau trang: ten tran + dem ngay
        d.rectangle([0, 0, W, MY0 - 12], fill=BG + (175,)) if sp.get('backdrop', True) else d.rectangle([0, 0, W, MY0 - 12], fill=BG)
        ft2 = fit(d, sp['title'], 58); d.text(((W - d.textlength(sp['title'], font=ft2)) / 2, 272), sp['title'], font=ft2, fill=GOLD)
        if di >= 1:
            s = '%s %d' % (sp.get('unit', 'NGÀY'), min(di, sp['days'])); s2 = ' / %d' % sp['days']
            wd = d.textlength(s, font=fday) + d.textlength(s2, font=fdate); x0 = (W - wd) / 2
            d.text((x0, 338), s, font=fday, fill=WHITE); d.text((x0 + d.textlength(s, font=fday), 364), s2, font=fdate, fill=(160, 160, 150))
            dl = sp.get('step_labels') or {}
            dt = dl.get(str(min(di, sp['days']))) or (date_of(sp, min(di, sp['days'])) if sp.get('start_date') and sp.get('unit', 'NGÀY') == 'NGÀY' else '')
            if dt: d.text(((W - d.textlength(dt, font=fdate)) / 2, 408), dt, font=fdate, fill=GOLD)
        else:
            s = sp.get('sub', ''); fsub = fit(d, s, SUB_PX, False); d.text(((W - d.textlength(s, font=fsub)) / 2, 340), s, font=fsub, fill=WHITE)
        # chu thich mau
        # chu giai: do khoang cach theo do dai chu (21/11: tranh de nhau), ghi chu dua vao goc duoi phai khung ban do
        lu, lt = sp.get('label_us', 'Quân ta'), sp.get('label_them', 'Quân Pháp'); fl = fs
        while 26 + 10 + d.textlength(lu, font=fl) + 36 + 26 + 10 + d.textlength(lt, font=fl) > MS and fl.size > 22: fl = fnt(False, fl.size - 2)
        tot = 26 + 10 + d.textlength(lu, font=fl) + 36 + 26 + 10 + d.textlength(lt, font=fl); lx0 = (W - tot) / 2; ly0 = MY0 + MS + 16
        d.rectangle([lx0, ly0 + 4, lx0 + 26, ly0 + 30], fill=RED); d.text((lx0 + 36, ly0), lu, font=fl, fill=WHITE)
        lx1 = lx0 + 36 + d.textlength(lu, font=fl) + 36
        d.rectangle([lx1, ly0 + 4, lx1 + 26, ly0 + 30], fill=BLUE); d.text((lx1 + 36, ly0), lt, font=fl, fill=WHITE)
        note = sp.get('note', '')
        if note:
            fnn = fnt(False, 20); nw = d.textlength(note, font=fnn)
            d.rectangle([MX0 + MS - nw - 18, MY0 + MS - 34, MX0 + MS - 4, MY0 + MS - 6], fill=(0, 0, 0, 150))
            d.text((MX0 + MS - nw - 11, MY0 + MS - 32), note, font=fnn, fill=(170, 170, 160))
        # su kien gan nhat
        ks = [k for k, e in enumerate(evs_all) if e['day'] <= day]
        if ks:
            k = ks[-1]; p_ = eout((tt - ev_t.get(k, 0)) / 0.3) if ev_t.get(k, 0) > 0 else 1.0  # ease-out 0,3s: mo dan + truot len 24px
            caption(d, ev_lay[k], cap_y, 0.35 + 0.65 * p_, int(24 * (1 - p_)))
        v.put(fr)
    v.close()
    mux(vpath, apath, os.path.join(OUT, 'out.mp4'))
    print('xong', round(dur, 1), 's')


if __name__ == '__main__':
    main()
