# -*- coding: utf-8 -*-
"""Video tin nhanh kieu "Viego Entertainment" (9:16, 1080x1920).

Bo cuc (theo mau chu gui 25/11/2026):
  1. Mo: anh nua tren + bang mau chu dao nua duoi, vien logo, tag NGAY DANG, tieu de IN HOA (doc tieu de).
  2. Than: anh o dai giua, nen = chinh anh do phong to + lam mo; goc tren trai NGUON, tren phai logo,
     duoi trai tag NGAY DANG. Anh doi 3-4 giay/lan, zoom nhe. Giong doc lien mach, khong phu de.
  3. Ket: the thuong hieu 1,6 giay.

Spec (SPEC_JSON):
{ "engine":"tin", "brand":"VIEGO ENTERTAINMENT", "short":"VIEGO", "color":"#D7141A",
  "date":"25/11/2026", "source":"VNEXPRESS", "video_credit":"", "title":"TIEU DE ...",
  "title_say":"cau doc tieu de", "body_say":"doan doc than bai", "speed":1.1,
  "images":[{"url":"https://...", "credit":"VNEXPRESS", "referer":"https://..."}],
  "seg":3.4, "music":"music_b.mp3", "music_vol":0.3 }
Chay thu khong mang: TIN_LOCAL=1, images[].path = file tren may, "durs":[mo, than].
"""
import json, os, re, subprocess, sys, math, random, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'


def font_path(names):
    for n in names:
        for d in ('/usr/share/fonts', os.path.expanduser('~/.local/share/fonts')):
            for r, _, fs in os.walk(d):
                for f in fs:
                    if f.lower() == n.lower(): return os.path.join(r, f)
    return None


if not font_path(['Anton-Regular.ttf']):   # may dung chung (dung.yml) chua co Anton -> tu tai
    try:
        _fd = os.path.expanduser('~/.local/share/fonts'); os.makedirs(_fd, exist_ok=True)
        with urllib.request.urlopen('https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf', timeout=60) as _r:
            open(os.path.join(_fd, 'Anton-Regular.ttf'), 'wb').write(_r.read())
    except Exception as _ex: print('khong tai duoc Anton', _ex)
F_HEAD = font_path(['Anton-Regular.ttf']) or font_path(['BeVietnamPro-ExtraBold.ttf'])
F_BOLD = font_path(['BeVietnamPro-ExtraBold.ttf', 'BeVietnamPro-Bold.ttf']) or F_HEAD
def fnt(p, s): return ImageFont.truetype(p, s)


def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):  # k<1 toi hon, k>1 sang hon
    return tuple(max(0, min(255, int(v * k if k <= 1 else v + (255 - v) * (k - 1)))) for v in c)


# ---------- tai nguyen ----------
def get(url, dst, referer=''):
    for k in range(3):
        try:
            h = {'User-Agent': UA, 'Accept': 'image/avif,image/webp,image/*,*/*'}
            if referer: h['Referer'] = referer
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r: data = r.read()
            open(dst, 'wb').write(data); return dst
        except Exception as ex: print('tai loi', k, type(ex).__name__, url[:80], flush=True)
    return None


def load_images(sp):
    ims = []
    for i, it in enumerate(sp.get('images', [])):
        p = it.get('path')
        for u in ([it['url']] if it.get('url') else []) + list(it.get('alt') or []):   # thu link chinh roi link du phong
            if p: break
            p = get(u, os.path.join(OUT, f'img{i}'), it.get('referer', ''))
        if not p: continue
        try:
            im = Image.open(p); im.load(); im = im.convert('RGB')
            if im.width < 300 or im.height < 200: print('anh qua nho, bo', i); continue
            ims.append((im, (it.get('credit') or sp.get('source', '')).upper()))
        except Exception as ex: print('anh hong', i, ex)
    if not ims: sys.exit('khong co anh nao dung duoc')
    # 27/11 chu: anh mo -> bo anh trung (cung 1 anh tu 2 bao) + bo anh qua nho neu con du anh to
    def dh(im):
        g = im.convert('L').resize((9, 8), Image.BILINEAR); px = list(g.tobytes())
        return [px[r * 9 + c] > px[r * 9 + c + 1] for r in range(8) for c in range(8)]
    keep, hs = [], []
    for im, cr in ims:
        h = dh(im)
        if any(sum(a != b for a, b in zip(h, o)) <= 6 for o in hs): print('anh trung, bo'); continue
        hs.append(h); keep.append((im, cr))
    big = [x for x in keep if x[0].width >= 700]
    if len(big) >= 3: keep = [x for x in keep if x[0].width >= 700 or x is keep[0]]
    print('anh dung:', [x[0].size for x in keep], flush=True)
    return keep if len(keep) >= 2 else ims


def load_clips(sp):
    """27/11 chu: chen clip ngan (tat tieng) vao dau than bai. clips:[{url, start, dur, credit}] - url TikTok/FB (yt-dlp) hoac link mp4."""
    out = []
    for i, c in enumerate((sp.get('clips') or [])[:2]):
        try:
            u = c.get('url', ''); src = os.path.join(OUT, f'clipsrc{i}.mp4')
            ref = c.get('referer', '')
            ok = None
            if 'tiktok.com' in u:   # 27/11 chu cho phep: may dung bi TikTok chan -> tai mp4 qua cong n8n (W102)
                _b = os.environ.get('AVF_TTS_URL', '').split('/webhook/')[0]; _k = os.environ.get('TIN_CLIP_KEY', '')
                ok = get(_b + '/webhook/viego-clip-7m2x?key=' + _k + '&u=' + urllib.request.quote(u, safe=''), src) if (_b and _k) else None
                print('clip tiktok qua n8n', bool(ok), flush=True)
            if ok: pass
            elif re.search(r'\.m3u8(\?|$)', u): src = u; ok = True   # 27/11: video bao dang HLS -> ffmpeg doc thang
            elif re.search(r'\.mp4(\?|$)', u) or 'tiktokcdn' in u or 'tikwm.com' in u: ok = get(u, src, ref)
            else:
                subprocess.run(['yt-dlp', '-q', '--no-warnings', '-f', 'mp4/best', '-o', src, u], timeout=180, check=True); ok = os.path.exists(src)
            if not ok: print('clip tai loi', i); continue
            st = float(c.get('start', 0)); du = max(1.5, min(6.0, float(c.get('dur', 4))))
            d = os.path.join(OUT, f'clip{i}'); os.makedirs(d, exist_ok=True)
            hdr = (['-user_agent', UA] + (['-referer', ref] if ref else [])) if src.startswith('http') else []
            subprocess.check_call(['ffmpeg', '-y', '-v', 'error'] + hdr + ['-ss', '%.2f' % st, '-t', '%.2f' % du, '-i', src, '-an', '-vf', f'fps={FPS},scale={W}:-2:flags=lanczos', '-q:v', '2', os.path.join(d, 'f%04d.jpg')])
            fr = sorted(os.path.join(d, x) for x in os.listdir(d) if x.endswith('.jpg'))
            if len(fr) < FPS: print('clip qua ngan', i); continue
            aw = os.path.join(OUT, f'clipa{i}.wav'); aok = False   # 27/11 chu: giu tieng goc cua clip (ghi nguon tren man hinh)
            try:
                dd = len(fr) / FPS
                subprocess.check_call(['ffmpeg', '-y', '-v', 'error'] + hdr + ['-ss', '%.2f' % st, '-t', '%.2f' % dd, '-i', src, '-vn', '-ac', '2', '-ar', '44100',
                                       '-af', 'apad,atrim=0:%.3f,afade=t=in:d=0.15,afade=t=out:st=%.2f:d=0.3' % (dd, max(0, dd - .3)), aw])
                aok = os.path.exists(aw) and os.path.getsize(aw) > 20000
            except Exception as ex: print('clip khong co tieng', i, type(ex).__name__)
            out.append({'frames': fr, 'credit': str(c.get('credit') or 'MẠNG XÃ HỘI').upper(), 'dur': len(fr) / FPS, 'audio': aw if aok else None})
            print('clip', i, len(fr), 'khung', flush=True)
        except Exception as ex: print('clip loi', i, type(ex).__name__, ex)
    return out


def cover(im, w, h, sharp=False):
    s = max(w / im.width, h / im.height); im2 = im.resize((max(w, int(im.width * s + .5)), max(h, int(im.height * s + .5))), Image.LANCZOS)
    x = (im2.width - w) // 2; y = (im2.height - h) // 2
    im2 = im2.crop((x, y, x + w, y + h))
    if sharp and s > 1.15: im2 = im2.filter(ImageFilter.UnsharpMask(radius=2, percent=min(110, int(40 + 35 * s)), threshold=2))   # 27/11 chu: anh nho phong to -> lam net lai
    return im2


# ---------- do hoa tinh ----------
def logo(sp, scale=1.0):
    """logo goc phai: vong tron trang chu cai dau + chu NEWS."""
    c = hexrgb(sp.get('color', '#D7141A')); r = int(30 * scale)
    f1 = fnt(F_HEAD, int(36 * scale)); f2 = fnt(F_HEAD, int(46 * scale))
    tw = int(f2.getlength('NEWS')); im = Image.new('RGBA', (2 * r + 10 + tw + 4, 2 * r + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((1, 1, 2 * r + 1, 2 * r + 1), fill=(255, 255, 255, 255))
    ch = (sp.get('short') or sp.get('brand', 'V'))[0].upper()
    d.text((r + 1, r + 1), ch, font=f1, fill=c + (255,), anchor='mm')
    d.text((2 * r + 10, r + 2), 'NEWS', font=f2, fill=(255, 255, 255, 255), anchor='lm', stroke_width=1, stroke_fill=(0, 0, 0, 90))
    return im


def pill(sp):
    """vien thuong hieu: vien bo tron, vong tron + ten kenh."""
    c = hexrgb(sp.get('color', '#D7141A')); f = fnt(F_HEAD, 44); txt = sp.get('brand', 'VIEGO ENTERTAINMENT').upper()
    tw = int(f.getlength(txt)); h = 84; w = tw + 130
    im = Image.new('RGBA', (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w + 4, h + 4), radius=h // 2, fill=shade(c, .55) + (255,), outline=(255, 255, 255, 235), width=4)
    d.ellipse((22, 18, 22 + 52, 18 + 52), fill=(255, 255, 255, 255))
    d.text((48, 45), txt[0], font=fnt(F_HEAD, 34), fill=c + (255,), anchor='mm')
    d.text((92, h // 2 + 5), txt, font=f, fill=(255, 255, 255, 255), anchor='lm')
    return im


def tag(sp, alpha=255):
    f = fnt(F_HEAD, 42); txt = 'NGÀY ĐĂNG: ' + sp.get('date', '')
    tw = int(f.getlength(txt)); im = Image.new('RGBA', (tw + 48, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(12, 0), (tw + 48, 0), (tw + 36, 70), (0, 70)], fill=(255, 255, 255, int(alpha * .26)))
    d.text((24, 35), txt, font=f, fill=(255, 255, 255, alpha), anchor='lm')
    return im


def source_text(credit, sp):
    f = fnt(F_HEAD, 40); lines = ['NGUỒN: ' + credit] if credit else []
    if sp.get('video_credit'): lines.append('VIDEO: ' + sp['video_credit'].upper())
    im = Image.new('RGBA', (760, 56 * max(1, len(lines)) + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, l in enumerate(lines): d.text((0, 2 + 56 * k), l, font=f, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 120))
    return im


def wrap(text, f, maxw):
    words = text.split(); lines = []; cur = ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if f.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines


def red_panel(sp, y0):
    """bang mau duoi canh mo: chuyen mau + luoi cham mo (thay ban do the gioi)."""
    c = hexrgb(sp.get('color', '#D7141A')); hh = H - y0
    pn = Image.new('RGB', (W, hh)); px = ImageDraw.Draw(pn)
    top, bot = shade(c, .95), shade(c, .42)
    for y in range(hh):
        t = y / hh; px.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    dots = Image.new('L', (W, hh), 0); dd = ImageDraw.Draw(dots)
    for y in range(int(hh * .45), hh, 22):   # luoi cham kieu ban do, dam dan ve cuoi
        for x in range(0, W, 22):
            v = math.sin(x * .011) * math.cos(y * .009) + math.sin((x + y) * .004)
            if v > .35: dd.ellipse((x, y, x + 7, y + 7), fill=int(70 * min(1, (y - hh * .45) / (hh * .3))))
    pn.paste(Image.new('RGB', (W, hh), shade(c, 1.35)), (0, 0), dots)
    fade = Image.new('L', (W, hh), 255); fd = ImageDraw.Draw(fade)
    for y in range(120): fd.line([(0, y), (W, y)], fill=int(255 * y / 120))
    return pn, fade


# ---------- khung hinh ----------
class Scene:
    def __init__(self, sp, ims, clips=None):
        self.sp = sp; self.ims = ims
        self.clips = clips or []; self.cd = sum(c['dur'] for c in self.clips)   # 27/11: clip chen
        self.logo = logo(sp); self.pill = pill(sp); self.tag = tag(sp)
        self.bgs, self.fgs, self.srcs = [], [], []
        for i, (im, cr) in enumerate(ims):   # toan canh + 2 can canh trai/phai -> it anh van khong lap y het (QC 25/11)
            bg = cover(im, W, H).filter(ImageFilter.GaussianBlur(38))
            bg = Image.blend(bg, Image.new('RGB', (W, H), (25, 25, 30)), .25)
            fh = int(im.height * W / im.width)
            if fh > 1180: fh = 1180   # anh doc: cat bot cho vua dai giua
            if fh < 620: fh = 620       # anh rat ngang: phong cho day dai
            vs = [cover(im, W, fh, True)]
            if im.width >= 900:
                cw = int(im.width * .62); chh = int(cw * fh / W)
                if chh <= im.height:
                    for fx in (.0, 1.0):   # can canh nua trai / nua phai
                        x0 = int((im.width - cw) * fx); y0 = max(0, int((im.height - chh) * .4))
                        cc = im.crop((x0, y0, x0 + cw, y0 + chh)); vs.append(cover(cc, W, fh, True))
            self.bgs.append(bg); self.fgs.append(vs); self.srcs.append(source_text(cr, sp))
        nv = max(len(v) for v in self.fgs)
        self.seq = [(i, v) for v in range(nv) for i in range(len(ims)) if v < len(self.fgs[i])]
        # canh mo
        self.y_split = 1000
        self.panel, self.panel_mask = red_panel(sp, self.y_split - 120)
        f = fnt(F_HEAD, 78); title = sp.get('title', '').upper()   # 27/11 chu: khung dau = anh bia -> tieu de to, ro
        lines = wrap(title, f, W - 120)
        while len(lines) > 5 and f.size > 50: f = fnt(F_HEAD, f.size - 4); lines = wrap(title, f, W - 120)
        self.title_img = Image.new('RGBA', (W, 100 * len(lines) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(self.title_img)
        lh = int(f.size * 1.32)
        for k, l in enumerate(lines): d.text((60, 6 + lh * k), l, font=f, fill=(255, 226, 54, 255) if k == 0 else (255, 255, 255, 255), stroke_width=3, stroke_fill=(60, 0, 0, 200))   # dong dau vang
        self.title_img = self.title_img.crop((0, 0, W, lh * len(lines) + 24))

    def intro(self, t, T):
        im0, _ = self.ims[0]; z = 1.0 + .05 * t / max(T, .1)
        top = cover(im0, int(W * z), int((self.y_split + 40) * z), True); x = (top.width - W) // 2; y = (top.height - self.y_split - 40) // 2
        fr = Image.new('RGB', (W, H), (0, 0, 0)); fr.paste(top.crop((x, y, x + W, y + self.y_split + 40)), (0, 0))
        fr.paste(self.panel, (0, self.y_split - 120), self.panel_mask)
        fr.paste(self.srcs[0], (60, 120), self.srcs[0]); fr.paste(self.logo, (W - 60 - self.logo.width, 108), self.logo)
        k = 1.0; ease = 1.0   # 27/11 chu: khung dau tien phai la ANH BIA day du (TikTok/FB/YouTube lay khung dau) -> khong truot/hien dan
        px = int(-400 * (1 - ease)); fr.paste(self.pill, (40 + px, self.y_split - 46), self.pill)
        fr.paste(self.tag, (56, self.y_split + 72), self.tag)
        a = 1.0; ti = self.title_img.copy()
        if a < 1: ti.putalpha(ti.getchannel('A').point(lambda v: int(v * a)))
        fr.paste(ti, (0, self.y_split + 170 + int(30 * (1 - a))), ti)
        return fr

    def body_one(self, k, u):
        """k: thu tu canh trong than bai, u: 0..1 tien trinh."""
        i, v = self.seq[k % len(self.seq)]
        bg = self.bgs[i]; fg = self.fgs[i][v]; z = 1.0 + .06 * u
        f2 = fg.resize((int(fg.width * z), int(fg.height * z)), Image.BICUBIC)   # 27/11: BILINEAR lam mo
        cx = (f2.width - W) // 2; f2 = f2.crop((cx, 0, cx + W, f2.height))
        fr = bg.copy(); y = (H - f2.height) // 2 - 20
        fr.paste(f2, (0, y))
        fr.paste(self.srcs[i], (60, 250), self.srcs[i]); fr.paste(self.logo, (W - 60 - self.logo.width, 238), self.logo)
        fr.paste(self.tag, (56, H - 300), self.tag)
        return fr

    def clip_frame(self, u):
        """27/11: khung clip, u = giay tinh tu dau than bai."""
        for ci, c in enumerate(self.clips):
            if u < c['dur'] or ci == len(self.clips) - 1: break
            u -= c['dur']
        idx = max(0, min(len(c['frames']) - 1, int(u * FPS)))
        fg = Image.open(c['frames'][idx]).convert('RGB')
        if 'bg' not in c:
            c['bg'] = Image.blend(cover(fg, W, H).filter(ImageFilter.GaussianBlur(38)), Image.new('RGB', (W, H), (25, 25, 30)), .25)
            c['src'] = source_text('', dict(self.sp, video_credit=c['credit']))
        if fg.height > 1180: y0 = (fg.height - 1180) // 2; fg = fg.crop((0, y0, W, y0 + 1180))
        fr = c['bg'].copy(); fr.paste(fg, (0, (H - fg.height) // 2 - 20))
        fr.paste(c['src'], (60, 250), c['src']); fr.paste(self.logo, (W - 60 - self.logo.width, 238), self.logo)
        fr.paste(self.tag, (56, H - 300), self.tag)
        return fr

    def outro(self, t, T):
        c = hexrgb(self.sp.get('color', '#D7141A'))
        fr = Image.new('RGB', (W, H), shade(c, .45)); fr.paste(self.panel, (0, H - self.panel.height), self.panel_mask)
        d = ImageDraw.Draw(fr); k = min(1, t / .3)
        lg = logo(self.sp, 2.0); fr.paste(lg, ((W - lg.width) // 2, 760), lg)
        d.text((W // 2, 960), 'THEO DÕI', font=fnt(F_HEAD, 58), fill=(255, 255, 255), anchor='mm')
        d.text((W // 2, 1050), self.sp.get('brand', '').upper(), font=fnt(F_HEAD, 74), fill=(255, 255, 255), anchor='mm')
        d.text((W // 2, 1150), 'ĐỂ CẬP NHẬT TIN NÓNG MỖI NGÀY', font=fnt(F_HEAD, 40), fill=(255, 225, 225), anchor='mm')
        if k < 1: fr = Image.blend(Image.new('RGB', (W, H), (0, 0, 0)), fr, k)
        return fr


# ---------- giong doc ----------
def tts(text, speed, tag_):
    import doc_so
    url = os.environ.get('AVF_TTS_URL', '')
    if not url: sys.exit('thieu AVF_TTS_URL')
    body = json.dumps({'text': doc_so.doc_tts(text), 'speed': speed, 'tag': tag_}).encode()
    for k in range(3):
        try:
            req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'X-AVF-Key': os.environ.get('AVF_KEY', '')})
            with urllib.request.urlopen(req, timeout=900) as r: j = json.loads(r.read())
            if j.get('ok'):
                for u in j['voice_urls']: print('::add-mask::' + u, flush=True)
                return list(zip(j['voice_urls'], j['pauses']))
            print('giong loi', j.get('error'))
        except Exception as ex: print('giong that bai', k, type(ex).__name__)
    sys.exit('khong co giong')


def dur_of(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())


def build_voice(parts, name, pause_k, tail=0):
    """noi cac cum giong lien mach: nghi ngan = pause W87 x pause_k (nhip doc tin nhanh)."""
    wavs = []
    for k, (u, pz) in enumerate(parts):
        mp = get(u, os.path.join(OUT, f'{name}_{k}.mp3'))
        if not mp: sys.exit('tai giong loi')
        pad = 0 if k == len(parts) - 1 else min(.4, max(.06, float(pz or .3) * pause_k))
        wv = os.path.join(OUT, f'{name}_{k}.wav')
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', mp, '-ar', '44100', '-ac', '2', '-af',
                               'silenceremove=start_periods=1:start_threshold=-60dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.15,areverse,apad=pad_dur=%.2f' % pad, wv])   # 26/11: do mau Theanh28 nghi giua cau 0,2-0,4s; giu 0,15s duoi cau, nguong -55dB khong an chu   # 25/11: KHONG cat duoi cau (lam mat chu cuoi cau)
        if tail and k == len(parts) - 1:   # 26/11 chu: keo dai tieng cuoi cau ket cho do cut
            d0 = dur_of(wv); cut = max(0.0, d0 - 0.45); w2 = wv[:-4] + '_t.wav'
            subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', wv, '-filter_complex',
                                   '[0]atrim=0:%.3f,asetpts=PTS-STARTPTS[a];[0]atrim=%.3f,asetpts=PTS-STARTPTS,atempo=%.2f[b];[a][b]concat=n=2:v=0:a=1' % (cut, cut, tail), w2]); wv = w2
        wavs.append(wv)
    lst = os.path.join(OUT, f'{name}.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in wavs))
    out = os.path.join(OUT, f'{name}.wav'); subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out])
    return out, dur_of(out)


def main():
    sp = json.loads(os.environ['SPEC_JSON'])
    ims = load_images(sp); sc = Scene(sp, ims, load_clips(sp))
    local = os.environ.get('TIN_LOCAL') or sp.get('durs')
    if local:
        t1, t2 = (sp.get('durs') or [5.0, 20.0]); va = vb = None
    elif sp.get('voice_a') and sp.get('voice_b'):   # may dung rieng (ent.yml): n8n goi W87 truoc, gui san [[url, nghi], ...]
        pk = float(sp.get('pause_k', .45))
        va, t1 = build_voice(sp['voice_a'], 'va', pk)
        vb, t2 = build_voice(sp['voice_b'], 'vb', pk, float(sp.get('tail_slow', 0)))
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        spd = float(sp.get('speed', 1.1)); pk = float(sp.get('pause_k', .45))
        va, t1 = build_voice(tts(sp['title_say'], spd, 'tin-a'), 'va', pk)
        vb, t2 = build_voice(tts(sp['body_say'], spd, 'tin-b'), 'vb', pk, float(sp.get('tail_slow', 0)))
    LEAD, GAP, OUTRO = .15, .35, 1.6
    ca = None; CA = 0.0
    if va and sc.clips and any(c.get('audio') for c in sc.clips) and sp.get('clip_audio', True):   # 27/11 chu: giong doc dung lai trong luc clip phat tieng goc
        parts = []
        for k, c in enumerate(sc.clips):
            p = c.get('audio')
            if not p:
                p = os.path.join(OUT, f'clipsil{k}.wav'); subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', '%.3f' % c['dur'], p])
            parts.append(p)
        lst = os.path.join(OUT, 'ca.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
        ca = os.path.join(OUT, 'ca.wav'); subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', ca])
        CA = sc.cd + .15
    T1 = LEAD + t1 + GAP; T2 = t2 + .5 + CA; D = T1 + T2 + OUTRO
    seg = float(sp.get('seg', 3.4)); n = len(ims)
    order = list(range(1, n)) + [0] if n > 1 else [0]   # than bai bat dau tu anh 2, het vong quay lai
    XF = .3
    if os.environ.get('BOARD'):
        for j, x in enumerate([.2, T1 * .9, T1 + .5, T1 + seg + .5, T1 + T2 * .7, T1 + T2 + .8]):
            frame(sc, x, T1, T2, D, seg, order, XF).save(os.path.join(OUT, f'board_{j}.png'))
        print('board ok'); return
    nfr = int(D * FPS); raw = os.path.join(OUT, 'v_tmp.mp4')
    pr = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', os.environ.get('X264_PRESET', 'medium'), '-crf', os.environ.get('X264_CRF', '16'), '-profile:v', 'high', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    for fi in range(nfr): pr.stdin.write(frame(sc, fi / FPS, T1, T2, D, seg, order, XF).tobytes())
    pr.stdin.close(); pr.wait()
    if pr.returncode: sys.exit('ffmpeg loi')
    final = os.path.join(OUT, 'out.mp4')
    if va:
        mus = mood_music(sp) or os.path.join(ROOT, 'editor', 'story', sp.get('music', 'music_b.mp3'))   # 27/11 chu: nhac theo khong khi tin
        sfx = sfx_track(str(sp.get('mood') or ''), T1, D)
        if not os.path.exists(mus):   # khong co nhac -> tao khoang lang
            mus = os.path.join(OUT, 'lang.wav'); subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', '5', mus])
        B = T1 + CA
        fc = (f'[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)}[a1];[2:a]adelay={int(B*1000)}|{int(B*1000)}[a2];'
              + (f'[4:a]adelay={int(T1*1000)}|{int(T1*1000)},volume={float(sp.get("clip_vol", .9))}[a3];[a1][a2][a3]amix=inputs=3' if ca else '[a1][a2]amix=inputs=2')
              + ':duration=longest:normalize=0,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2[vx];'
              f'[vx]asplit=2[v][vk];[3:a]volume={float(sp.get("music_vol", .3))}[m0];[m0][vk]sidechaincompress=threshold=0.025:ratio=6:attack=30:release=600[m];'
              + (f'[{5 if ca else 4}:a]volume={float(sp.get("sfx_vol", .55))}[sx];[v][m][sx]amix=inputs=3' if sfx else '[v][m]amix=inputs=2')
              + ':duration=first:normalize=0,apad,loudnorm=I=-14:TP=-1.5[a]')
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', va, '-i', vb, '-stream_loop', '-1', '-i', mus] + (['-i', ca] if ca else []) + (['-i', sfx] if sfx else []) + ['-filter_complex', fc,
                               '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', f'{D:.2f}', final])
    else: os.replace(raw, final)
    print('ok', round(D, 2), 'giay, anh', n)


# ---------- nhac + hieu ung theo khong khi (27/11 chu) ----------
MOODS = {'vui': 3, 'hai': 2, 'buon': 3, 'cam_dong': 2, 'kich_tinh': 3, 'rung_ron': 1, 'tin_tuc': 3}   # nhac Pixabay (da loc bai co Content ID), luu Supabase avf-media/viego/music/
MUSIC_BASE = os.environ.get('AVF_MEDIA_BASE', '').rstrip('/') + '/viego/music/' if os.environ.get('AVF_MEDIA_BASE') else ''   # 27/11 repo cong khai


def mood_music(sp):
    m = str(sp.get('mood') or '').strip()
    if sp.get('music_url'): return get(sp['music_url'], os.path.join(OUT, 'nhac.mp3'))
    if m not in MOODS: return None
    k = random.randint(1, MOODS[m]); p = get(MUSIC_BASE + f'{m}_{k}.mp3', os.path.join(OUT, f'nhac_{m}.mp3'))
    print('nhac nen', m, k, bool(p), flush=True)
    return p


SFX = {   # tao bang ffmpeg, khong dung file ngoai -> khong lo ban quyen
    'boom': "aevalsrc='0.95*sin(2*PI*(62-34*t)*t)*exp(-2.6*t)+0.25*sin(2*PI*31*t)*exp(-1.8*t)':s=44100:d=1.8",
    'hit': "aevalsrc='0.8*sin(2*PI*(90-50*t)*t)*exp(-5*t)':s=44100:d=0.9",
    'whoosh': "anoisesrc=d=0.65:c=pink:a=0.7:r=44100,highpass=f=350,lowpass=f=6000,afade=t=in:d=0.45:curve=exp,afade=t=out:st=0.45:d=0.2",
    'ding': "aevalsrc='0.45*sin(2*PI*1320*t)*exp(-6*t)+0.25*sin(2*PI*1980*t)*exp(-9*t)+0.15*sin(2*PI*2640*t)*exp(-12*t)':s=44100:d=0.8",
    'swell': "anoisesrc=d=1.6:c=brown:a=0.35:r=44100,lowpass=f=900,afade=t=in:d=1.2:curve=qsin,afade=t=out:st=1.2:d=0.4",
}


def sfx_track(m, T1, D):
    plan = {'kich_tinh': [('boom', 0.0), ('whoosh', T1 - .5), ('hit', T1 - .05)], 'rung_ron': [('boom', 0.0), ('whoosh', T1 - .5)],
            'vui': [('ding', .05), ('whoosh', T1 - .5)], 'hai': [('ding', .05), ('whoosh', T1 - .5)],
            'tin_tuc': [('whoosh', T1 - .5)], 'buon': [('swell', max(0, T1 - 1.4))], 'cam_dong': [('swell', max(0, T1 - 1.4))]}.get(m)
    if not plan: return None
    try:
        ins, fc = [], []
        for k, (n, t) in enumerate(plan):
            ins += ['-f', 'lavfi', '-i', SFX[n]]; ms = int(max(0, t) * 1000)
            fc.append(f'[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms}[s{k}]')
        fc.append(''.join(f'[s{k}]' for k in range(len(plan))) + f'amix=inputs={len(plan)}:normalize=0,apad,atrim=0:{D:.2f}[o]')
        out = os.path.join(OUT, 'sfx.wav')
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[o]', out])
        print('hieu ung', m, [n for n, _ in plan], flush=True); return out
    except Exception as ex: print('hieu ung loi', type(ex).__name__, ex); return None


def frame(sc, t, T1, T2, D, seg, order, XF):
    if t < T1: return sc.intro(t, T1)
    if t >= T1 + T2: return sc.outro(t - T1 - T2, D - T1 - T2)
    u = t - T1
    if sc.cd:   # 27/11 chu: clip chen dau than bai (tat tieng, giong doc van chay)
        if u < sc.cd:
            fr = sc.clip_frame(u)
            return Image.blend(sc.intro(T1, T1), fr, u / XF) if u < XF else fr
        u -= sc.cd
    k = int(u // seg) + 1; p = (u % seg) / seg   # +1: bo qua toan canh anh 1 (da dung o canh mo)
    fr = sc.body_one(k, p)
    if k == 1 and u < XF: fr = Image.blend(sc.clip_frame(sc.cd - .01) if sc.cd else sc.intro(T1, T1), fr, u / XF)   # chuyen tu canh mo / clip
    elif k > 1 and (u % seg) < XF:
        fr = Image.blend(sc.body_one(k - 1, 1.0), fr, (u % seg) / XF)
    return fr


if __name__ == '__main__':
    main()
