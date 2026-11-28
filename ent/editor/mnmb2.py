"""Moi Ngay Mot Buoc - dang moi 28/11 (chu gui mau: nen den, 1 den roi tu tran, nguoi hinh bieu tuong mau kem
lam 1 dong tac lap lai, chu co chan: tu dau CAM VANG IN HOA + cau trang hien theo giong).
Chu chot: don gian, mau tram, chu ro, lam noi chu dang doc, BO nen chu, full man hinh theo ti le vang
(chu o 0,382 chieu cao, nhan vat quanh 0,618), co anh bia + hook manh, giong Vbee s_sg_male_thientam_ytstable_vc.

SPEC_JSON: {"texts":[...], "sents":[...], "voice_urls":[...], "pauses":[...],   (ket qua W87)
            "hook":"...", "hook_sub":"...", "leads":[so tu cam moi cau], "poses":[[cum dau cau | so cau, "ten dang"], ...],
            "end_title":"MỖI NGÀY MỘT BƯỚC", "end_sub":"..."}
Dang (poses): ngu, bat, ngoi, guc, dungday, ta, viet, di, dung
Chay thu: DRY=1 FRAMES_AT="0.2,5,12" -> out/at_NN.png
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safezone  # noqa: E402

W, H, FPS = 1080, 1920, 30
ROOT = os.getcwd(); OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
CREAM = (226, 218, 204); DARK = (9, 9, 11)
Y_TXT = int(H * 0.382)          # tam khoi chu (ti le vang)
FLOOR = 1430                    # mat san (chan nhan vat); nhan vat chiem quanh 0,618
U = 470                         # chieu cao nguoi dung (px)
_fc = {}


def lora(size, w='Bold'):
    k = (size, w)
    if k not in _fc:
        p = os.path.join(FD, 'Lora-Variable.ttf')
        if os.path.exists(p):
            f = ImageFont.truetype(p, size); f.set_variation_by_name(w)
        else:
            from series import fnt; f = fnt(w in ('Bold', 'SemiBold'), size)
        _fc[k] = f
    return _fc[k]


# ---------------- nen: den + 1 den roi ----------------
def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W), np.float32) + 0.035
    # chum sang hinh non tu den (540, 150) xuong san
    top = 150.0; t = np.clip((yy - top) / (FLOOR - top), 0, 1)
    half = 70 + 300 * t                      # be rong non tang dan
    core = np.exp(-((xx - 540) / half) ** 2 * 1.6) * np.clip((yy - top + 10) / 60, 0, 1)
    fall = (0.55 * np.exp(-((yy - top) / 520) ** 2) + 0.22 * (1 - t) + 0.10)
    light = core * fall
    pool = np.exp(-(((xx - 540) / 330) ** 2 + ((yy - FLOOR) / 46) ** 2)) * 0.55     # vung sang tren san
    glow = np.exp(-(((xx - 540) / 60) ** 2 + ((yy - top - 30) / 90) ** 2)) * 0.9      # sang ngay duoi bong den
    L = base + light + pool * (yy > FLOOR - 60) + glow
    col = np.stack([L * 236, L * 226, L * 206], -1)
    vg = np.sqrt(((xx - 540) / (W * .75)) ** 2 + ((yy - 900) / (H * .62)) ** 2)
    col *= np.clip(1.15 - vg * 0.55, 0.25, 1)[..., None]
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    with safezone.decor():   # bong den trang tri tren tran
        d.rectangle([536, 0, 544, 120], fill=(30, 30, 32))
        d.rounded_rectangle([516, 116, 564, 152], 6, fill=(22, 22, 24))
        d.ellipse([522, 140, 558, 160], fill=(255, 246, 220))
    return im


# ---------------- nguoi hinh bieu tuong ----------------
# toa do don vi: x sang phai, y huong xuong, san = 0, nguoi dung cao ~1
J = ['hd', 'n', 'h', 'le', 'lh', 're', 'rh', 'lk', 'lf', 'rk', 'rf']
P = {
    'stand': dict(hd=(0, -.90), n=(0, -.76), h=(0, -.45), le=(-.11, -.60), lh=(-.13, -.45), re=(.11, -.60), rh=(.13, -.45),
                  lk=(-.06, -.23), lf=(-.08, 0), rk=(.06, -.23), rf=(.08, 0)),
    'bar_up': dict(hd=(0, -.90), n=(0, -.76), h=(0, -.45), le=(-.22, -.66), lh=(-.20, -.80), re=(.22, -.66), rh=(.20, -.80),
                   lk=(-.07, -.23), lf=(-.10, 0), rk=(.07, -.23), rf=(.10, 0)),
    'bar_dn': dict(hd=(0, -.70), n=(0, -.57), h=(0, -.29), le=(-.22, -.47), lh=(-.20, -.61), re=(.22, -.47), rh=(.20, -.61),
                   lk=(-.21, -.20), lf=(-.12, 0), rk=(.21, -.20), rf=(.12, 0)),
    'sit_head': dict(hd=(.10, -.66), n=(.04, -.60), h=(-.04, -.32), le=(.20, -.40), lh=(.12, -.60), re=(.22, -.39), rh=(.14, -.60),
                     lk=(.20, -.31), lf=(.21, 0), rk=(.23, -.31), rf=(.25, 0)),
    'sit_up': dict(hd=(.02, -.88), n=(0, -.74), h=(-.04, -.32), le=(.06, -.56), lh=(.16, -.44), re=(.08, -.56), rh=(.18, -.44),
                   lk=(.20, -.31), lf=(.21, 0), rk=(.23, -.31), rf=(.25, 0)),
    'slump': dict(hd=(.36, -.55), n=(.24, -.52), h=(-.06, -.32), le=(.30, -.47), lh=(.48, -.48), re=(.31, -.47), rh=(.50, -.48),
                  lk=(.17, -.31), lf=(.18, 0), rk=(.19, -.31), rf=(.21, 0)),
    'write': dict(hd=(.10, -.78), n=(.05, -.65), h=(-.06, -.32), le=(.15, -.50), lh=(.33, -.48), re=(.16, -.51), rh=(.35, -.49),
                  lk=(.17, -.31), lf=(.18, 0), rk=(.19, -.31), rf=(.21, 0)),
    'lie': dict(hd=(-.46, -.40), n=(-.33, -.37), h=(0, -.36), le=(-.26, -.30), lh=(-.12, -.32), re=(-.26, -.30), rh=(-.12, -.32),
                lk=(.22, -.37), lf=(.44, -.36), rk=(.22, -.37), rf=(.44, -.36)),
    'lie_reach': dict(hd=(-.46, -.40), n=(-.33, -.37), h=(0, -.36), le=(-.26, -.30), lh=(-.12, -.32), re=(-.50, -.30), rh=(-.66, -.33),
                      lk=(.22, -.37), lf=(.44, -.36), rk=(.22, -.37), rf=(.44, -.36)),
}


def lerp_pose(a, b, q):
    return {k: (a[k][0] + (b[k][0] - a[k][0]) * q, a[k][1] + (b[k][1] - a[k][1]) * q) for k in J}


def walk_pose(ph):
    s = math.sin(ph * 2 * math.pi); c = math.cos(ph * 2 * math.pi); b = abs(c) * .015
    p = dict(P['stand']); p = {k: (v[0], v[1] - b) for k, v in p.items()}
    p['lk'] = (.10 * s, -.24 - b); p['lf'] = (.20 * s, -.02 * max(0, c)); p['rk'] = (-.10 * s, -.24 - b); p['rf'] = (-.20 * s, -.02 * max(0, -c))
    p['le'] = (-.10 * s, -.60 - b); p['lh'] = (-.17 * s, -.46 - b); p['re'] = (.10 * s, -.60 - b); p['rh'] = (.17 * s, -.46 - b)
    p['hd'] = (.03, -.90 - b); p['n'] = (.02, -.76 - b)
    return p


def ez(q):
    q = max(0.0, min(1.0, q)); return q * q * (3 - 2 * q)


def pose_at(kind, lt, dur):
    """tra ve (pose, props) theo dang va thoi gian trong canh"""
    if kind == 'ta':     # nang ta lap lai nhu mau: len - giu - xuong
        ph = (lt % 3.2) / 3.2
        q = ez(ph / .35) if ph < .35 else (1 if ph < .5 else 1 - ez((ph - .5) / .4))
        return lerp_pose(P['bar_dn'], P['bar_up'], q), {'bar': True}
    if kind == 'ngoi':
        br = .006 * math.sin(lt * 2.2)
        p = {k: (v[0], v[1] + (br if k in ('hd', 'n', 'lh', 'rh') else 0)) for k, v in P['sit_head'].items()}
        return p, {'box': True}
    if kind == 'dungday':   # tu ngoi gu -> ngoi thang -> dung len
        q1 = ez((lt - .4) / 1.0); q2 = ez((lt - 1.6) / 1.1)
        p = lerp_pose(P['sit_head'], P['sit_up'], q1)
        if q2 > 0: p = lerp_pose(p, P['stand'], q2)
        return p, {'box': True, 'dawn': ez((lt - 1.4) / 2.0)}
    if kind == 'guc':
        br = .005 * math.sin(lt * 1.8)
        return {k: (v[0], v[1] + (br if k in ('hd', 'n') else 0)) for k, v in P['slump'].items()}, {'desk': True, 'chair': True, 'lamp': .35}
    if kind == 'viet':
        p = dict(P['write']); w = .025 * math.sin(lt * 7.0); p['rh'] = (p['rh'][0] + w, p['rh'][1] + .006 * math.sin(lt * 14))
        return p, {'desk': True, 'chair': True, 'lamp': 1.0, 'paper': True}
    if kind in ('ngu', 'bat'):
        q = 0.0
        if kind == 'bat':
            ph = (lt % 3.6) / 3.6; q = ez(ph / .3) if ph < .3 else (1 if ph < .55 else 1 - ez((ph - .55) / .3))
        return lerp_pose(P['lie'], P['lie_reach'], q), {'bed': True, 'phone': 1.0}
    if kind == 'di':
        return walk_pose(lt / 1.15), {'road': lt}
    return P['stand'], {}


def draw_person(pose, props, alpha=1.0, cx=540):
    """ve o 2x roi thu nho cho min; tra layer RGBA full khung"""
    S = 2; im = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    u = U * S; X = lambda p: (cx * S + p[0] * u, FLOOR * S + p[1] * u)
    col = CREAM + (255,); dim = (150, 144, 134, 255)
    lw = int(.072 * u); tw = int(.13 * u)
    # do vat phia sau
    if props.get('bed'):
        d.rounded_rectangle([X((-.62, -.30)), X((.58, -.18))], int(.03 * u), fill=dim)
        d.rectangle([X((-.60, -.18)), X((-.56, 0))], fill=dim); d.rectangle([X((.52, -.18)), X((.56, 0))], fill=dim)
        d.rounded_rectangle([X((-.62, -.44)), X((-.58, -.18))], int(.015 * u), fill=dim)
        d.rectangle([X((-.86, -.24)), X((-.70, 0))], fill=(110, 105, 98, 255))       # tu dau giuong
    if props.get('box'):
        d.rounded_rectangle([X((-.22, -.30)), X((.08, 0))], int(.02 * u), fill=dim)
    if props.get('chair'):
        d.rectangle([X((-.18, -.31)), X((.06, -.27))], fill=dim); d.rectangle([X((-.18, -.27)), X((-.15, 0))], fill=dim)
        d.rectangle([X((.03, -.27)), X((.06, 0))], fill=dim); d.rectangle([X((-.20, -.66)), X((-.16, -.27))], fill=dim)
    if props.get('desk'):
        d.rectangle([X((.22, -.46)), X((.70, -.42))], fill=dim)
        d.rectangle([X((.62, -.42)), X((.66, 0))], fill=dim); d.rectangle([X((.24, -.42)), X((.28, 0))], fill=dim)
        if props.get('lamp') is not None:
            d.line([X((.60, -.46)), X((.56, -.66)), X((.46, -.70))], fill=dim, width=int(.02 * u))
            d.polygon([X((.40, -.66)), X((.50, -.74)), X((.52, -.66))], fill=dim)
        if props.get('paper'): d.rectangle([X((.30, -.475)), X((.46, -.46))], fill=(245, 240, 228, 255))
    # than nguoi
    p = {k: X(v) for k, v in pose.items()}
    rr = lambda a, r_: [a[0] - r_, a[1] - r_, a[0] + r_, a[1] + r_]

    def limb(a, b, w_):
        d.line([a, b], fill=col, width=w_); d.ellipse(rr(a, w_ / 2), fill=col); d.ellipse(rr(b, w_ / 2), fill=col)
    limb(p['h'], p['lk'], lw + 6); limb(p['lk'], p['lf'], lw); limb(p['h'], p['rk'], lw + 6); limb(p['rk'], p['rf'], lw)
    for fk in ('lf', 'rf'):   # ban chan
        if not props.get('bed'): d.ellipse([p[fk][0] - lw * .9, p[fk][1] - lw * .45, p[fk][0] + lw * .9, p[fk][1] + lw * .2], fill=col)
    limb(p['n'], p['h'], tw)
    if props.get('bed'):   # chan dap
        d.rounded_rectangle([X((-.30, -.46)), X((.52, -.28))], int(.06 * u), fill=(176, 168, 154, 255))
    limb(p['n'], p['le'], lw); limb(p['le'], p['lh'], lw); limb(p['n'], p['re'], lw); limb(p['re'], p['rh'], lw)
    for hk in ('lh', 'rh'): d.ellipse(rr(p[hk], lw * .62), fill=col)
    d.ellipse(rr(p['hd'], .088 * u), fill=col)
    if props.get('bar'):   # ta don nhu mau
        y = (p['lh'][1] + p['rh'][1]) / 2; x0, x1 = cx * S - .52 * u, cx * S + .52 * u
        d.rectangle([x0, y - .012 * u, x1, y + .012 * u], fill=col)
        for sx in (-1, 1):
            for off, hh in ((.40, .11), (.45, .08), (.50, .05)):
                xx = cx * S + sx * off * u; d.rectangle([xx - .012 * u, y - hh * u, xx + .012 * u, y + hh * u], fill=col)
    im = im.resize((W, H), Image.LANCZOS)
    if props.get('phone'):   # dien thoai sang lanh tren tu
        ph = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(ph); x0, y0 = cx + -.80 * U, FLOOR - .30 * U
        pd.ellipse([x0 - 70, y0 - 70, x0 + 70, y0 + 40], fill=(150, 190, 255, 70)); ph = ph.filter(ImageFilter.GaussianBlur(26))
        pd = ImageDraw.Draw(ph); pd.rounded_rectangle([x0 - 22, y0 - 10, x0 + 22, y0 + 4], 4, fill=(200, 225, 255, 255))
        im = Image.alpha_composite(ph, im)
    if props.get('lamp'):
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g); x0, y0 = cx + .47 * U, FLOOR - .62 * U
        gd.ellipse([x0 - 160, y0 - 40, x0 + 160, y0 + 240], fill=(255, 196, 120, int(60 * props['lamp']))); g = g.filter(ImageFilter.GaussianBlur(50))
        im = Image.alpha_composite(g, im)
    if props.get('road') is not None:   # vach duong troi ve sau
        r_ = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(r_); off = (props['road'] * 160) % 240
        for i in range(-1, 6):
            x = 540 + 520 - i * 240 + off - 260
            rd.rectangle([x, FLOOR + 14, x + 120, FLOOR + 22], fill=(120, 114, 104, 200))
        im = Image.alpha_composite(r_, im)
    if alpha < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    return im


# ---------------- chu ----------------
def gold_text(txt, f):
    """chu cam vang co chieu sau nhu mau (do day xuong), bong toi mem"""
    d0 = ImageDraw.Draw(Image.new('L', (8, 8))); bb = d0.textbbox((0, 0), txt, font=f)
    w_, h_ = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
    m = Image.new('L', (w_, h_), 0); ImageDraw.Draw(m).text((20 - bb[0], 20 - bb[1]), txt, font=f, fill=255)
    gy = np.linspace(0, 1, h_)[:, None]
    g = np.stack([255 - 10 * gy, 196 - 70 * gy, 92 - 62 * gy], -1) * np.ones((1, w_, 1))
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(m)
    sh = Image.new('RGBA', (w_, h_), (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * .85)))
    out = Image.new('RGBA', (w_, h_), (0, 0, 0, 0)); out.alpha_composite(sh, (0, 4)); out.alpha_composite(im)
    return out, bb


def wrap_words(d, words, f, maxw):
    lines, cur = [], []
    for w in words:
        if cur and d.textlength(' '.join(cur + [w]), font=f) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    if cur: lines.append(cur)
    if len(lines) == 2 and len(lines[1]) == 1 and len(lines[0]) > 2: lines[1].insert(0, lines[0].pop())   # tranh dong mo coi
    return lines


class Line:
    """1 cau: dong CAM in hoa (lead) + phan trang hien theo giong; tu dang doc sang vang nhat + nay nhe."""
    def __init__(self, text, n_lead, times, big=False):
        ws = text.split(); n_lead = max(0, min(n_lead, len(ws)))
        self.lead = ' '.join(ws[:n_lead]).upper().rstrip(',')
        self.body = ws[n_lead:]; self.times = times[n_lead:] if times else [0] * len(self.body)
        d = ImageDraw.Draw(Image.new('L', (8, 8)))
        fl = lora(112 if big else 88, 'Bold')
        llines = [' '.join(x) for x in wrap_words(d, self.lead.split(), fl, 780)] if self.lead else []
        while self.lead and (len(llines) > 2 or any(d.textlength(x, font=fl) > 780 for x in llines)) and fl.size > 54:
            fl = lora(fl.size - 4, 'Bold'); llines = [' '.join(x) for x in wrap_words(d, self.lead.split(), fl, 780)]
        self.lead_imgs = [gold_text(s, fl) for s in llines]; self.lh = int(fl.size * 1.18)
        self.fb = lora(66, 'SemiBold')
        self.blines = wrap_words(d, self.body, self.fb, 780)[:3]; self.bh = 84
        tot = len(self.lead_imgs) * self.lh + len(self.blines) * self.bh + (16 if self.lead_imgs and self.blines else 0)
        self.y0 = int(Y_TXT - tot / 2)
        safezone.check_box(150, self.y0, 930, self.y0 + tot, 'chu cau: ' + text[:30])

    def draw(self, im, t, a=1.0):
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y = self.y0
        for (g, bb) in self.lead_imgs:
            ov.alpha_composite(g, (int((W - g.width) / 2), int(y - 20))); y += self.lh
        if self.lead_imgs: y += 16
        d = ImageDraw.Draw(ov); sp = d.textlength(' ', font=self.fb); wi = 0
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        for ln in self.blines:
            x = (W - d.textlength(' '.join(ln), font=self.fb)) / 2
            for w in ln:
                t0 = self.times[wi] if wi < len(self.times) else 0
                t1 = self.times[wi + 1] if wi + 1 < len(self.times) else t0 + .45
                if t < t0 - .05: col = (236, 230, 218, 70)            # chua doc: mo
                elif t < t1 + .05:                                  # dang doc: vang nhat, sang ro
                    col = (255, 214, 140, 255); gd.text((x, y), w, font=self.fb, fill=(255, 190, 90, 150))
                else: col = (240, 236, 228, 255)                    # da doc: trang
                d.text((x + 2, y + 4), w, font=self.fb, fill=(0, 0, 0, int(col[3] * .8)))
                d.text((x, y), w, font=self.fb, fill=col)
                x += d.textlength(w, font=self.fb) + sp; wi += 1
            y += self.bh
        glow = glow.filter(ImageFilter.GaussianBlur(10))
        out = Image.alpha_composite(glow, ov)
        if a < 1: out.putalpha(out.getchannel('A').point(lambda v: int(v * a)))
        im.alpha_composite(out)


def word_times(words, t0, t1):
    wts = [1.0 + .12 * max(0, len(w) - 4) + (.8 if w.endswith((',', ';', ':')) else 0) for w in words]
    tot = sum(wts) or 1; t = t0; out = []
    for wt in wts: out.append(t); t += (t1 - t0) * wt / tot
    return out


# ---------------- am thanh ----------------
def make_music(path, D, sr=44100):
    """pad tram (Am F C G) + not piano thua, rat nho - de giong noi bat"""
    import wave
    n = int(D * sr); t = np.arange(n) / sr; out = np.zeros(n, np.float32)
    ch = [[110.0, 130.8, 164.8], [87.3, 110.0, 130.8], [65.4, 98.0, 130.8], [98.0, 123.5, 146.8]]; bar = 4.0
    for i in range(int(D / bar) + 1):
        a, b = int(i * bar * sr), min(n, int((i + 1.25) * bar * sr))
        if a >= n: break
        tt = t[a:b] - i * bar; env = np.minimum(1, tt / 1.2) * np.exp(-np.maximum(0, tt - bar) * 2.5)
        for fq in ch[i % 4]: out[a:b] += env * (.05 * np.sin(2 * np.pi * fq * tt) + .015 * np.sin(4 * np.pi * fq * tt))
        for k, fq in enumerate(ch[i % 4]):   # 3 not piano roi nhe
            s = int((i * bar + k * 1.3) * sr)
            if s < n:
                L = min(n - s, int(2.5 * sr)); tk = np.arange(L) / sr
                out[s:s + L] += .05 * np.exp(-tk * 2.2) * np.sin(2 * np.pi * fq * 2 * tk)
    out[:int(1.6 * sr)] += (.5 * np.exp(-t[:int(1.6 * sr)] * 3) * np.sin(2 * np.pi * 48 * t[:int(1.6 * sr)])).astype(np.float32)   # tieng 'dum' mo dau
    out = np.clip(out, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype(np.int16).tobytes())


# ---------------- chinh ----------------
def main():
    sp = json.loads(os.environ['SPEC_JSON']) if os.environ.get('SPEC_JSON', '').strip().startswith('{') else json.load(open(os.environ['SPEC_JSON']))
    S = sp['texts']; DRY = os.environ.get('DRY') == '1'
    segs, off, parts = [], 0.15, []        # (bat dau, ket thuc loi, chu, chi so)
    if DRY:
        for i, s in enumerate(S):
            dd = max(1.4, len(s.split()) * .40) + float((sp.get('pauses') or [.45] * 99)[i] or 0)
            segs.append((off, off + dd - .45, s, i)); off += dd
    else:
        from series import get, voice_part
        for i, u in enumerate(sp['voice_urls']):
            pth = get(u, os.path.join(OUT, f'vp{i}.mp3')); wav = os.path.join(OUT, f'vp{i}.wav')
            dd, _ = voice_part(pth, wav, sp, i); pz = float((sp.get('pauses') or [.45] * 99)[i] or 0)
            segs.append((off, off + dd - pz, S[i], i)); parts.append(wav); off += dd
    END = 3.4; D = off + END; T_END = off
    leads = sp.get('leads') or []
    lines = []
    for i, (a, b, s, _) in enumerate(segs):
        ws = s.split(); nl = leads[i] if i < len(leads) else (len(ws) if len(ws) <= 3 else 1)
        lines.append(Line(s, nl if i else len(ws), word_times(ws, a, b), big=(i == 0)))
    # canh (dang nhan vat) theo cau
    poses = sp.get('poses') or [[0, 'ta']]

    def idx_of(key):
        if isinstance(key, int): return key
        for i, s in enumerate(S):
            if s.lower().startswith(str(key).lower()): return i
        raise SystemExit('khong thay cau: ' + str(key))
    pst = sorted([(idx_of(k), n) for k, n in poses])
    spans = []
    for j, (si, n) in enumerate(pst):
        a = 0.0 if j == 0 else segs[si][0] - .2
        b = segs[pst[j + 1][0]][0] - .2 if j + 1 < len(pst) else D
        spans.append((a, b, n))
    BG = make_bg().convert('RGBA')
    hook = (sp.get('hook') or S[0]).upper(); hook_sub = sp.get('hook_sub', '')
    hook_end = segs[0][1] + .35
    HOOK = Line((hook + ' ' + hook_sub).strip(), len(hook.split()), [-9.0] * 99, big=True)

    def frame(t):
        im = BG.copy()
        k = max(j for j, s_ in enumerate(spans) if s_[0] <= t); a, b, n = spans[k]; lt = t - a
        pose, props = pose_at(n, lt, b - a)
        fa = min(1.0, lt / .35) if k else 1.0
        if k and lt < .35:   # chuyen dang: mo dan nguoi cu -> nguoi moi
            pa, pb_ = pose_at(spans[k - 1][2], t - spans[k - 1][0], 1)
            im.alpha_composite(draw_person(pa, pb_, 1 - fa))
        im.alpha_composite(draw_person(pose, props, fa))
        if t >= T_END:   # the ket
            te = t - T_END; al = ez(te / .6)
            g, _ = gold_text(sp.get('end_title', 'MỖI NGÀY MỘT BƯỚC'), lora(84, 'Bold'))
            g.putalpha(g.getchannel('A').point(lambda v: int(v * al)))
            im.alpha_composite(g, (int((W - g.width) / 2), Y_TXT - 80))
            d = ImageDraw.Draw(im); s2 = sp.get('end_sub', 'Theo dõi để mai bước tiếp'); f2 = lora(52, 'Medium')
            d.text(((W - d.textlength(s2, font=f2)) / 2, Y_TXT + 40), s2, font=f2, fill=(236, 230, 218, int(255 * ez((te - .5) / .6))))
            return im.convert('RGB')
        if t < hook_end:   # ANH BIA + HOOK tu khung 0: chu cam to + dong phu trang
            HOOK.draw(im, t)
            return im.convert('RGB')
        cur = next((j for j in range(len(segs) - 1, 0, -1) if segs[j][0] - .15 <= t), None)
        if cur is not None and t < segs[cur][1] + float((sp.get('pauses') or [.45] * 99)[cur] or 0) + .1:
            lines[cur].draw(im, t, min(1.0, (t - segs[cur][0] + .15) / .2))
        return im.convert('RGB')

    at = os.environ.get('FRAMES_AT')
    if at:
        for j, x in enumerate(at.split(',')): frame(float(x)).save(os.path.join(OUT, f'at_{j:02d}.png'))
        print('spans', [(round(a, 1), n) for a, b, n in spans], 'D', round(D, 1)); return
    VK = int(min(3000, 42 * 8 * 1000 / max(10.0, D)))
    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', f'{VK}k', '-bufsize', f'{2 * VK}k', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    for fi in range(int(D * FPS)): p.stdin.write(frame(fi / FPS).tobytes())
    p.stdin.close(); p.wait()
    mus = os.path.join(OUT, 'mus.wav'); make_music(mus, D)
    lst = os.path.join(OUT, 'vlist.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
    voice = os.path.join(OUT, 'voice.wav')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice])
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    mix = '[1:a]adelay=150|150,asplit=2[v][vs];[2:a]volume=0.9[m];[m][vs]sidechaincompress=threshold=0.03:ratio=6:release=400[md];' \
          '[v][md]amix=inputs=2:duration=longest:normalize=0,apad,loudnorm=I=-15:TP=-1.5[a]'
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', voice, '-i', mus, '-filter_complex', mix, '-map', '0:v', '-map', '[a]',
                           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4')); print('ok', round(D, 2))


if __name__ == '__main__':
    main()
