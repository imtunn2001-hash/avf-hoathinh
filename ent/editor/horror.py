"""Chuyện Đêm - kinh di 'luat le' kieu analog horror (VHS) 9:16.
SPEC_JSON: {"git_branch","file_no":"#001","rule_top","rule_bot","clock":"02:13:07","scenes":[{"img","voice_url","text","tag"?,"sfx"?,"glitch"?}],
            "end_top","end_bot"}"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safezone  # noqa: E402  khoa cung bo cuc 20/11
from r3 import (W, H, FPS, SR, OUT, TMP, load_spec, git_imgs, voices, place, tone, boom, noise, write_audio, Vid, mux,
                fnt, wrap_bal, ease, cover)  # noqa: E402
import chu, ngat, chinh_ta  # noqa: E402  27/11: font Fira Sans + Barlow, ngat dong theo cum, soat chinh ta

RED = (230, 40, 40); WHITE = (235, 238, 230)


def mono(size):
    # 27/11: Fira Sans SemiBold (du dau tieng Viet, gon, de doc tren nen toi)
    return chu.font('sub', size)


def tagf(size):
    # 27/11: nhan do / chu luat: Barlow Condensed ExtraBold (hep, cao, kieu bang canh bao)
    return chu.font('tag', size)


RNG = np.random.default_rng(7)
NOISE = [RNG.normal(0, 14, (H // 2, W // 2, 1)).astype(np.float32) for _ in range(6)]
SCAN = np.ones((H, 1, 1), np.float32); SCAN[::3] = 0.8


def vhs(img, fi, glitch=0.0):
    a = np.asarray(img, np.float32)
    lum = a @ np.array([0.3, 0.59, 0.11], np.float32)
    g = np.stack([lum * 0.86, lum * 1.0, lum * 0.9], -1) * 0.55 + a * 0.45  # nga xanh xam
    out = g.copy()
    sh = 5 + int(glitch * 18)
    out[:, sh:, 0] = g[:, :-sh, 0]; out[:, :-sh, 2] = g[:, sh:, 2]  # lech mau
    nz = NOISE[fi % 6].repeat(2, 0).repeat(2, 1)
    out = out * SCAN + nz
    out *= 0.9 + 0.08 * np.sin(fi * 1.7) * (0.5 + glitch)
    if glitch > 0 or fi % 97 < 3:  # vet xe ngang
        y0 = int((fi * 131) % (H - 120)); hh = 40 + int(glitch * 200)
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], int(30 + glitch * 120), axis=1) * 1.15
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def hud(fr, fi, t, sp):
    with safezone.decor():
        _hud(fr, fi, t, sp)


def _hud(fr, fi, t, sp):
    d = ImageDraw.Draw(fr); f = mono(40)
    if (fi // 15) % 2 == 0: d.ellipse((60, 92, 92, 124), fill=RED)
    d.text((108, 84), 'REC', font=f, fill=WHITE)
    no = 'HỒ SƠ ' + sp.get('file_no', '#001'); d.text((W - 60 - d.textlength(no, font=f), 84), no, font=f, fill=WHITE)
    h, m, s = [int(x) for x in sp.get('clock', '02:13:07').split(':')]
    tt = h * 3600 + m * 60 + s + int(t)
    ck = '%02d:%02d:%02d AM' % (tt // 3600 % 24, tt // 60 % 60, tt % 60)
    d.text((60, H - 150), ck, font=f, fill=WHITE)
    d.text((W - 60 - d.textlength('SP', font=f), H - 150), 'SP', font=f, fill=WHITE)


def type_text(d, s, f, y, frac, fill, maxw=None, lh=None):
    maxw = maxw or safezone.MAXW_C540
    s = ngat.nfc(s); lines = ngat.wrap_cum(d, s, f, maxw); lh = lh or int(f.size * 1.38)
    tot = sum(len(l) for l in lines); show = int(tot * min(1, frac)); y0 = y
    for l in lines:
        part = l[:max(0, show)]; show -= len(l)
        if part: d.text(((W - d.textlength(l, font=f)) / 2, y0), part, font=f, fill=fill, stroke_width=3, stroke_fill=(0, 0, 0))
        y0 += lh
    return y0


def sfx_track(a, kind, t):
    if kind == 'ting':
        place(a, tone(1318.5, 1.6, 0.18, r=1.4), t); place(a, tone(1046.5, 1.8, 0.12, r=1.6), t + 0.35)
    elif kind == 'heart':
        for k in range(5): place(a, boom(0.5, 0.45), t + k * 0.95); place(a, boom(0.4, 0.3), t + k * 0.95 + 0.28)
    elif kind == 'knock':
        for k in range(3): place(a, noise(0.08, 0.5, 900) * np.linspace(1, 0, int(0.08 * SR)), t + k * 0.45)
    elif kind == 'static':
        place(a, noise(0.9, 0.22), t)
    elif kind == 'drop':
        place(a, boom(2.5, 0.8), t)


def main():
    sp = load_spec(); sc = sp['scenes']
    _ct = chinh_ta.soat(' '.join([x.get('text', '') + ' ' + x.get('tag', '') for x in sc] + [sp.get(k, '') for k in ('rule_top', 'rule_bot', 'end_top', 'end_bot')]))
    if _ct: print('CANH BAO CHINH TA:', ', '.join(_ct))
    git_imgs(sp.get('git_branch'), [s['img'] for s in sc])
    intro = 0.12   # 28/11 chu chot hook 2 giay: giong vao ngay, bang luat chuyen xuong canh 2
    gaps = [s.get('gap', 0.8) for s in sc]
    voice, spans = voices([list(zip(s['voice_urls'], s.get('pauses') or [0.45] * len(s['voice_urls']))) if s.get('voice_urls') else s['voice_url'] for s in sc], gaps, lead=intro)
    end_d = 3.0; vend = len(voice) / SR; dur = vend + end_d
    # am thanh: drone + re bang + hieu ung
    a = np.zeros(int(SR * dur), np.float32)
    tt = np.arange(len(a)) / SR
    a += (np.sin(2 * np.pi * 55 * tt) * 0.05 + np.sin(2 * np.pi * 58.3 * tt) * 0.04 + np.sin(2 * np.pi * 110.5 * tt) * 0.015).astype(np.float32)
    a += noise(dur, 0.018, 3000)[:len(a)]
    place(a, voice, 0, 1.0)
    sfx_track(a, 'static', 0.0); sfx_track(a, 'drop', 2.6)
    for k, s in enumerate(sc):
        if s.get('sfx'): sfx_track(a, s['sfx'], spans[k][0] + s.get('sfx_at', 0.2))
    for k in range(1, len(sc)):   # 23/11: moi lan doi canh co tieng xe bang ngan (khop hinh cuon VHS)
        place(a, noise(0.22, 0.16, 5000) * np.linspace(1, 0, int(0.22 * SR)) ** 2, max(0, spans[k][0] - 0.2))
    sfx_track(a, 'static', vend); sfx_track(a, 'drop', vend + 0.3)
    apath = os.path.join(TMP, 'a.wav'); write_audio(a, apath)
    # hinh
    imgs = [Image.open(s['img']).convert('RGB') for s in sc]
    starts = [0.0] + [spans[k][0] - 0.15 for k in range(1, len(sc))]
    ends = starts[1:] + [vend]
    black = Image.new('RGB', (W, H), (4, 6, 5))
    fsub = mono(48); ftag = tagf(150); frule = mono(64); frule2 = tagf(120)
    vpath = os.path.join(TMP, 'v.mp4'); v = Vid(vpath)
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        if t < starts[0]:  # the luat mo dau
            fr = black.copy(); d = ImageDraw.Draw(fr)
            y = type_text(d, sp['rule_top'], frule, 700, (t - 0.3) / 1.9, WHITE)
            if t > 2.6:
                d2 = ngat.nfc(sp['rule_bot'])
                while d.textlength(d2, font=frule2) > safezone.MAXW_C540 and frule2.size > 56: frule2 = tagf(frule2.size - 4)
                d.text(((W - d.textlength(d2, font=frule2)) / 2, y + 60), d2, font=frule2, fill=RED,
                                            stroke_width=4, stroke_fill=(0, 0, 0))
            fr = vhs(fr, fi, 0.6 if t < 0.5 or 2.6 < t < 2.8 else 0.0)
            v.put(fr); continue
        if t >= vend:  # ket: nhieu + chu
            te = t - vend; fr = black.copy(); d = ImageDraw.Draw(fr)
            y = type_text(d, sp.get('end_top', ''), mono(52), 760, te / 1.0, WHITE)
            if te > 1.1: type_text(d, sp.get('end_bot', ''), tagf(84), y + 50, (te - 1.1) / 0.8, RED)
            v.put(vhs(fr, fi, 0.8 if te < 0.4 else 0.0)); continue
        k = max(i for i in range(len(sc)) if starts[i] <= t); ls = ends[k] - starts[k]; lt = (t - starts[k]) / max(0.1, ls)
        fr = cover(imgs[k], W, H, 1.03 + 0.06 * lt, 0.5 + 0.02 * np.sin(t * 0.7), 0.5)
        d = ImageDraw.Draw(fr)
        s = sc[k]; tin = t - starts[k]
        if s.get('tag') and tin < 2.4:
            al = ease(tin / 0.25) * (1 - ease((tin - 1.9) / 0.5))
            col = tuple(int(c * al + 10 * (1 - al)) for c in RED)
            while d.textlength(s['tag'], font=ftag) > safezone.MAXW_C540 and ftag.size > 70: ftag = tagf(ftag.size - 6)
            d.text(((W - d.textlength(s['tag'], font=ftag)) / 2, 330), s['tag'], font=ftag, fill=col, stroke_width=5, stroke_fill=(0, 0, 0))
        v0, v1 = spans[k]; frac = (t - v0) / max(0.3, (v1 - v0) * 0.92)
        import doc_so; s = dict(s, text=doc_so.chuan_dau(doc_so.chu_so(s['text'])))   # 23/11: so + chinh ta cho phu de
        fs_ = fsub; nl = len(ngat.wrap_cum(d, s['text'], fs_, safezone.MAXW_C540))
        while nl * int(fs_.size * 1.38) > 1440 - 900 and fs_.size > 40: fs_ = mono(fs_.size - 2); nl = len(ngat.wrap_cum(d, s['text'], fs_, safezone.MAXW_C540))  # 22/11: phu de >= 40px
        lh_ = int(fs_.size * 1.38)
        type_text(d, s['text'], fs_, min(1250, 1438 - nl * lh_), frac, WHITE, lh=lh_)
        if k == (1 if len(sc) > 1 else 0) and tin < 3.6 and (sp.get('rule_top') or sp.get('rule_bot')):   # 28/11 bang luat chong len canh 2
            al = ease(tin / 0.3) * (1 - ease((tin - 3.2) / 0.4))
            if al > 0.01:
                ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                fr1 = mono(52); fr2 = tagf(96)
                t1 = ngat.nfc(sp.get('rule_top', '')); t2 = ngat.nfc(sp.get('rule_bot', ''))
                while t1 and od.textlength(t1, font=fr1) > safezone.MAXW_C540 and fr1.size > 36: fr1 = mono(fr1.size - 2)
                while t2 and od.textlength(t2, font=fr2) > safezone.MAXW_C540 and fr2.size > 52: fr2 = tagf(fr2.size - 4)
                od.rectangle((80, 520, 1000 - 60, 520 + 230), fill=(0, 0, 0, int(190 * al)))
                if t1: od.text(((W - od.textlength(t1, font=fr1)) / 2, 545), t1, font=fr1, fill=(235, 235, 235, int(255 * al)))
                if t2: od.text(((W - od.textlength(t2, font=fr2)) / 2, 620), t2, font=fr2, fill=RED + (int(255 * al),), stroke_width=4, stroke_fill=(0, 0, 0, int(255 * al)))
                fr = Image.alpha_composite(fr.convert('RGBA'), ov).convert('RGB'); d = ImageDraw.Draw(fr)
        hud(fr, fi, t, sp)
        gl = 0.0
        if tin < 0.18 and k > 0: gl = 0.7
        if s.get('glitch') and t > ends[k] - 2.2: gl = max(gl, 0.4 + 0.5 * ((t - (ends[k] - 2.2)) / 2.2))
        fr = vhs(fr, fi, gl)
        if k > 0 and tin < 0.22:   # 23/11 chuyen canh: hinh cuon doc nhu bang VHS mat dong bo (tracking roll)
            q = tin / 0.22; arr = np.asarray(fr); sh_ = int(H * 0.35 * (1 - q) ** 2)
            arr = np.roll(arr, sh_, axis=0).copy(); band = max(0, sh_ - 40)
            if sh_ > 0: arr[band:sh_] = (arr[band:sh_] * 0.25).astype(np.uint8)
            fr = Image.fromarray(arr)
        if s.get('glitch') and ends[k] - 0.5 < t: fr = black.copy()
        v.put(fr)
    v.close()
    mux(vpath, apath, os.path.join(OUT, 'out.mp4'))
    print('xong', round(dur, 1), 's')


if __name__ == '__main__':
    main()
