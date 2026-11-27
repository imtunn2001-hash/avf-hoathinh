"""Mỗi Ngày Một Bước - phim hoat hinh dong luc 9:16 (kieu Day One Films): 1 nhan vat 2D co dinh, moi canh 1 cau,
chu khoa trang to, giong tram cham, nhac nen toi.
SPEC_JSON: {"git_branch":"cp-assets","scenes":[{"img","voice_url","text","key"}],"end_title","end_sub"}"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safezone  # noqa: E402  khoa cung bo cuc 20/11
import fx  # noqa: E402  23/11: chuyen canh whip/zoom, whoosh, grade, ducking, chu nhay theo tu
from r3 import (W, H, FPS, SR, OUT, TMP, load_spec, git_imgs, voices, place, tone, boom, noise, write_audio, Vid, mux,
                fnt, wrap_bal, ease, cover, decode, trim_sil)  # noqa: E402
import chu, ngat, chinh_ta  # noqa: E402  27/11: font Fira Sans, ngat dong theo cum, soat chinh ta

GOLD = (255, 196, 64); WHITE = (255, 255, 255)


def vignette():
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
    a = np.clip((d - 0.55) / 0.6, 0, 1) * 200
    return Image.fromarray(a.astype(np.uint8), 'L')


import functools  # noqa: E402


@functools.lru_cache(maxsize=64)
def key_layout(s):
    """27/11: chu khoa Fira Sans Black, ngat theo cum; thu nho den khi <= 3 dong va khong co dong chi 1 tu"""
    s = ngat.nfc(s); d = ImageDraw.Draw(Image.new('RGB', (10, 10))); sz = 150
    while True:
        f = chu.font('key', sz); lines = ngat.wrap_cum(d, s, f, safezone.MAXW_C540)
        ok = len(lines) <= 3 and all(d.textlength(l, font=f) <= safezone.MAXW_C540 for l in lines)
        if ok and (len(s.split()) < 3 or all(len(l.split()) > 1 for l in lines)): break
        if sz <= 84: break
        sz -= 6
    return f, lines, int(f.size * 1.2)


def key_img(s):
    f, lines, lh = key_layout(s); s = ngat.nfc(s); d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    hh = lh * len(lines) + 40
    im = Image.new('RGBA', (W, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text(((W - d.textlength(l, font=f)) / 2, 20 + i * lh), l, font=f, fill=WHITE,
               stroke_width=9, stroke_fill=(0, 0, 0))
    im.tb = (540 - max(d.textlength(l, font=f) for l in lines) / 2 - 10, 540 + max(d.textlength(l, font=f) for l in lines) / 2 + 10)
    return im


def sub_img(s):
    """giu de tuong thich; chu nhay theo tu dung SubK ben duoi"""
    return SubK(s).draw(1e9)


class SubK:
    """23/11 chu nhay theo tu: tu da doc mau trang, tu dang doc mau vang + nay nhe, tu chua doc mo 40%.
    Bo cuc dong co dinh tu dau (khong xo lech), phu de trong vung an toan, toi da 3-4 dong nhu cu."""
    def __init__(self, s, times=None):
        import doc_so; s = doc_so.chuan_dau(doc_so.chu_so(s))   # 23/11: so bang chu so, dau kieu bao chi
        s = ngat.nfc(s)
        f = chu.font('sub', 58); d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
        lines = ngat.wrap_cum(d, s, f, 780)
        while len(lines) > 3 and f.size > 46: f = chu.font('sub', f.size - 2); lines = ngat.wrap_cum(d, s, f, 780)
        lines = lines[:4]; self.f = f; self.fb = chu.font('bold', f.size)
        self.lh = int(f.size * 1.32); self.hh = self.lh * len(lines) + 34
        self.words = []   # (x, y, tu)
        sp_w = d.textlength(' ', font=f)
        for i, l in enumerate(lines):
            x = 510 - d.textlength(l, font=f) / 2
            for w in l.split(' '):
                self.words.append((x, 14 + i * self.lh, w)); x += d.textlength(w, font=f) + sp_w
        self.times = times or [0.0] * len(self.words)
        self.base = Image.new('RGBA', (W, self.hh), (0, 0, 0, 0))
        ImageDraw.Draw(self.base).rounded_rectangle([90, 0, 930, self.hh], 22, fill=(0, 0, 0, 150))
        self.height = self.hh

    def draw(self, tl):
        im = self.base.copy(); d = ImageDraw.Draw(im)
        cur = max([i for i, t0 in enumerate(self.times) if t0 <= tl] or [-1])
        for i, (x, y, w) in enumerate(self.words):
            if i < cur: col = (240, 240, 240, 255)
            elif i == cur: col = GOLD + (255,)
            else: col = (240, 240, 240, 105)
            dy = -int(6 * (1 - ease((tl - self.times[i]) / 0.16))) if i == cur else 0
            d.text((x, y + dy), w, font=self.f, fill=col, stroke_width=3, stroke_fill=(0, 0, 0, col[3]))
        return im


def key_kinetic(s, kt):
    """chu khoa: tung tu dap vao lan luot (cach 0.12s), phong to vuot da roi ve 1, xoay nhe."""
    f, lines, lh = key_layout(s); d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    im = Image.new('RGBA', (W, lh * len(lines) + 40), (0, 0, 0, 0)); wi = 0
    for i, l in enumerate(lines):
        x = (W - d.textlength(l, font=f)) / 2
        for w in l.split(' '):
            q = (kt - 0.12 * wi) / 0.22; wi += 1
            ww = d.textlength(w + ' ', font=f)
            if q > 0:
                sc = 1.0 + 0.45 * (1 - ease(q)) - 0.06 * np.sin(min(1.0, q) * np.pi) * (q < 1)
                t_ = Image.new('RGBA', (int(ww + 60), lh + 40), (0, 0, 0, 0))
                ImageDraw.Draw(t_).text((30, 20), w, font=f, fill=WHITE, stroke_width=9, stroke_fill=(0, 0, 0))
                if sc != 1.0:
                    t_ = t_.resize((int(t_.width * sc), int(t_.height * sc)), Image.BILINEAR)
                    t_ = t_.rotate(-6 * (1 - ease(q)), resample=Image.BILINEAR)
                cx_, cy_ = x + ww / 2 - 15, 20 + i * lh + lh / 2 + 20
                im.alpha_composite(t_, (int(cx_ - t_.width / 2), int(cy_ - t_.height / 2)))
            x += ww
    return im


def music(dur):
    out = np.zeros(int(SR * (dur + 1)), np.float32)
    chords = [[110.0, 130.8, 164.8], [87.3, 110.0, 130.8], [65.4, 98.0, 130.8], [98.0, 123.5, 146.8]]  # Am F C G (tram)
    bar = 4.0; i = 0
    while i * bar < dur:
        for fq in chords[i % 4]:
            x = tone(fq, bar + 1.0, 0.05, a=1.2, r=1.5) + tone(fq * 2, bar + 1.0, 0.015, a=1.2, r=1.5)
            place(out, x, i * bar)
        place(out, tone(chords[i % 4][0] / 2, 1.2, 0.12, a=0.01, r=1.0), i * bar)  # nhip tram dau o
        i += 1
    return out[:int(SR * dur)]


def main():
    sp = load_spec(); sc = sp['scenes']
    _ct = chinh_ta.soat(' '.join([s.get('text', '') + ' ' + s.get('key', '') for s in sc] + [sp.get('end_title', ''), sp.get('end_sub', '')]))
    if _ct: print('CANH BAO CHINH TA:', ', '.join(_ct))
    git_imgs(sp.get('git_branch'), [s['img'] for s in sc])
    gaps = [s.get('gap', 0.75) for s in sc]
    voice, spans = voices([list(zip(s['voice_urls'], s.get('pauses') or [0.45] * len(s['voice_urls']))) if s.get('voice_urls') else s['voice_url'] for s in sc], gaps, lead=0.5)
    end_d = 3.2; dur = len(voice) / SR + end_d
    os.environ.setdefault('VID_VF', fx.grade_vf(sp.get('grade', 'mnmb')))
    # moc tung cau trong canh (tu file giong da tai) -> moc tung tu cho phu de nhay theo tu
    import doc_so, re
    wtimes = []
    for k, s in enumerate(sc):
        t0, t1 = spans[k]; txt = doc_so.chuan_dau(doc_so.chu_so(s['text']))
        sents = [x.strip() for x in re.findall(r'.+?(?:[.!?…]+(?=\s|$)|$)', txt) if x.strip()]
        segs = []
        if s.get('voice_urls') and len(s['voice_urls']) == len(sents):
            pz = s.get('pauses') or [0.45] * len(sents); c = t0
            for j in range(len(sents)):
                try: dj = len(trim_sil(decode(os.path.join(TMP, 'v%02d_%02d.mp3' % (k, j))))) / SR
                except Exception: segs = []; break
                segs.append((c, c + dj, sents[j])); c += dj + float(pz[j] or 0.45)
        if not segs: segs = [(t0, t1, txt)]
        tt_ = []
        for a_, b_, st_ in segs: tt_ += fx.word_times(st_.split(), a_, b_)
        wtimes.append(tt_)
    # am thanh: nhac ha xuong khi co loi (ducking), whoosh o moi lan chuyen canh
    a = np.zeros(int(SR * dur), np.float32); place(a, voice, 0, 1.0)
    mu = music(dur); vv = np.zeros(len(mu), np.float32); vv[:min(len(voice), len(vv))] = voice[:len(vv)]
    place(a, fx.duck(mu * 1.5, vv, depth=0.62), 0, 1.0)
    for k, (t0, _) in enumerate(spans):
        if k in (0, len(spans) - 1) or sc[k].get('boom'): place(a, boom(1.4, 0.35), max(0, t0 - 0.05))
        if k > 0: place(a, fx.whoosh(0.42, 0.2, up=(k % 2 == 0), seed=k), max(0, t0 - 0.12 - 0.21))
    place(a, boom(2.0, 0.5), len(voice) / SR)
    apath = os.path.join(TMP, 'a.wav'); write_audio(a, apath)
    # hinh
    imgs = [Image.open(s['img']).convert('RGB') for s in sc]
    keys = [key_img(s.get('key', '')) if s.get('key') else None for s in sc]
    subs = [SubK(s['text'], wtimes[k]) for k, s in enumerate(sc)]
    vig = vignette(); black = Image.new('RGB', (W, H), (0, 0, 0))
    endbg = Image.blend(Image.composite(black, cover(imgs[-1], W, H, 1.07, 0.5, 0.49), vig), black, 0.78)
    starts = [0.0] + [spans[k][0] - 0.12 for k in range(1, len(sc))]
    ends = starts[1:] + [len(voice) / SR]

    def scene(k, t):
        ls = ends[k] - starts[k]; lt = (t - starts[k]) / max(0.1, ls)
        # 22/11: day vao nhanh roi cham dan (ease-out) trong 1,2s, sau do troi rat nhe
        tz = max(0.0, t - starts[k]); z = 1.0 + 0.055 * (1 - (1 - min(1.0, tz / 1.2)) ** 3) + 0.015 * lt
        fr = cover(imgs[k], W, H, z, 0.5, 0.45 + 0.04 * lt)
        fr = Image.composite(black, fr, vig).convert('RGBA')
        if keys[k] is not None:
            safezone.check_box(keys[k].tb[0], 330, keys[k].tb[1], 330 + keys[k].height, 'chu khoa ' + str(sc[k].get('key')))
            kk = key_kinetic(sc[k]['key'], tz)
            fr.alpha_composite(kk, (0, int(330 - (kk.height - keys[k].height) / 2)))
        sb = subs[k]; safezone.check_box(90, 1440 - sb.height, 930, 1440, 'phu de')
        fr.alpha_composite(sb.draw(t), (0, 1440 - sb.height))
        return fr.convert('RGB')

    vpath = os.path.join(TMP, 'v.mp4'); v = Vid(vpath)
    n = int(dur * FPS); TA, TB = 0.10, 0.14   # chuyen canh: 0.10s cuoi canh cu + 0.14s dau canh moi
    for fi in range(n):
        t = fi / FPS
        if t >= ends[-1]:  # the ket - 22/11: nen la canh cuoi lam toi (lien mach, khong con khung den)
            te = t - ends[-1]; fr = endbg.copy(); d = ImageDraw.Draw(fr)
            f1 = chu.font('key', 108); f2 = chu.font('sub', 50); al = ease(te / 0.6)
            col = tuple(int(c * al) for c in GOLD)
            for i, l in enumerate(['MỖI NGÀY', 'MỘT BƯỚC'] if sp.get('end_title', 'MỖI NGÀY MỘT BƯỚC') == 'MỖI NGÀY MỘT BƯỚC' else [sp['end_title']]):
                d.text(((W - d.textlength(l, font=f1)) / 2, 760 + i * 125), l, font=f1, fill=col)
            s2 = sp.get('end_sub', 'Theo dõi để mai bước tiếp'); c2 = tuple(int(200 * ease((te - 0.5) / 0.6)) for _ in range(3))
            d.text(((W - d.textlength(s2, font=f2)) / 2, 1040), s2, font=f2, fill=c2)
            v.put(fr); continue
        k = max(i for i in range(len(sc)) if starts[i] <= t)
        nb = k + 1 if k + 1 < len(sc) and starts[k + 1] - t < TA else None
        if nb is not None:   # cuoi canh: bat dau lao sang canh sau
            p = (t - (starts[nb] - TA)) / (TA + TB); v.put(fx.whip(scene(k, t), scene(nb, starts[nb]), p * 1.0, fx.kind_for(nb))); continue
        if k > 0 and t - starts[k] < TB:
            p = (t - (starts[k] - TA)) / (TA + TB); v.put(fx.whip(scene(k - 1, starts[k]), scene(k, t), p, fx.kind_for(k))); continue
        v.put(scene(k, t))
    v.close()
    mux(vpath, apath, os.path.join(OUT, 'out.mp4'))
    print('xong', round(dur, 1), 's')


if __name__ == '__main__':
    main()
