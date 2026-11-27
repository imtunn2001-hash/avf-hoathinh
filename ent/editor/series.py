"""Series ngan ke chuyen (CCK / CSK) - bo cuc theo skill ke-chuyen-series-ngan, 1080x1920.
SPEC_JSON = {"branch","dir"}; trong dir: spec.json + anh canh (sc1.png..).
spec.json: {"channel":"cck|war","series":"...","part":1,"total":4,"ep_title":"...","voice_url","srt_url","scenes":["sc1.png",...],"next":"Phần 2: ...?"}"""
import json, math, os, re, subprocess, sys, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safezone  # noqa: E402  khoa cung bo cuc 20/11

W, H, FPS = 1080, 1920, 30
ROOT = os.getcwd()
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
BLUE1 = (13, 42, 107); BLUE2 = (18, 58, 143); YEL = (255, 212, 0); WHITE = (255, 255, 255); INK = (20, 20, 28)


def fnt(bold, size):
    for p in [os.path.join(ROOT, 'fonts', 'BeVietnamPro-ExtraBold.ttf' if bold else 'BeVietnamPro-Medium.ttf'),
              '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf' if bold else '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf']:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    sys.exit('khong co font')


def get(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f:
        f.write(r.read())
    return path


try:
    from lexicon import unlex  # phien am ten rieng -> ten goc cho phu de
except Exception:
    unlex = lambda t: t
try:
    from lexicon import fix_cues
except Exception:
    fix_cues = lambda s: s


def parse_srt(txt):
    out = []
    for b in re.split(r'\n\s*\n', txt.strip()):
        ls = [l for l in b.strip().splitlines() if l.strip()]
        for k, l in enumerate(ls):
            m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)', l)
            if m:
                g = list(map(int, m.groups()))
                out.append((g[0]*3600+g[1]*60+g[2]+g[3]/1000, g[4]*3600+g[5]*60+g[6]+g[7]/1000, unlex(' '.join(ls[k+1:]))))
                break
    return out


TRIM_HEAD = 'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.04'
TRIM_TAIL = 'areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,areverse'


def _dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())


def voice_part(pth, wav, sp, i, sr=44100, ac=2):
    """Chuan hoa 1 doan giong. spec co 'pauses' (W87, chu chot 21/11): moi doan = 1 cau doc lien,
    cat lang 2 dau roi chen dung pauses[i] giay. Khong co: giu kieu cu (dem 0.12s).
    Tra (thoi luong, lead) - lead la phan lang dau da cat, tru vao moc SRT cua doan."""
    ps = sp.get('pauses')
    if not ps:
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', pth, '-ar', str(sr), '-ac', str(ac), '-af', 'apad=pad_dur=0.12', wav])
        return _dur(wav), 0.0
    head = wav + '.h.wav'
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', pth, '-ar', str(sr), '-ac', str(ac), '-af', TRIM_HEAD, head])
    lead = max(0.0, _dur(pth) - _dur(head))
    p = float(ps[i]) if i < len(ps) and ps[i] is not None else 0.45
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', head, '-ar', str(sr), '-ac', str(ac), '-af', TRIM_TAIL + ',apad=pad_dur=%.2f' % max(0.0, p - 0.1), wav])
    return _dur(wav), lead


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def eout(t):
    """ease-out cubic: vao nhanh, cham dan (22/11 bai hoc kenh Dat)."""
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


REFRAME = 4.0  # 22/11 (QC lap 14 lan: 1 tranh giu 8-9s don dieu): canh dai > 5,5s doi khung nhin moi 4s
FRAMES = [(0.0, 0.0), (0.10, -0.10), (0.06, 0.10), (0.14, 0.0)]  # (them zoom, lech ngang) tung khung nhin


def reframe(ts, seg_len):
    if seg_len <= 5.5: return 0.0, 0.0
    j = int(ts // REFRAME)
    if j == 0: return FRAMES[0]
    q = eout((ts - j * REFRAME) / 0.4); a, b = FRAMES[(j - 1) % 4], FRAMES[j % 4]
    return a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines


def wrap_bal(d, s, f, maxw):
    # chia dong can bang, tranh 1 tu mo coi o dong cuoi
    lines = wrap(d, s, f, maxw)
    if len(lines) < 2: return lines
    tot = d.textlength(s, font=f); n = len(lines)
    for k in range(20):
        tw = tot / n * (1.0 + 0.04 * k)
        if tw > maxw: break
        b = wrap(d, s, f, tw)
        if len(b) == n: return b
    return lines


def _norm(x):
    return re.sub(r'[^\w ]', ' ', x.lower()).split()


def scene_starts(sp, srt, n, dur):
    # moc canh theo cues (cum tu trong loi doc) -> thoi diem trong SRT; khong co thi chia theo so chu
    cues = sp.get('cues') or []
    words = []
    for a, b, t in srt:
        ws = _norm(t)
        for i, w in enumerate(ws): words.append((a + (b - a) * i / max(1, len(ws)), w))
    st = [0.0]
    for k in range(1, n):
        t0 = None
        c = _norm(cues[k]) if k < len(cues) and cues[k] else []
        if c and words:
            for i in range(len(words) - len(c) + 1):
                if words[i][0] > st[-1] + 1.0 and [w for _, w in words[i:i + len(c)]] == c: t0 = words[i][0]; break
        if t0 is None:
            t0 = words[int(len(words) * k / n)][0] if words else dur * k / n
            t0 = max(t0, st[-1] + 1.5)
        st.append(min(t0 - 0.15, dur - 1.0))
    return st


def merge_short_cues(srt, min_w=3, max_w=9):
    """22/11 (QC lap 4 lan): cum SRT chi 1-2 chu ('đi', 'thấy') hien 1 minh tren man -> gop vao cum ben canh
    (uu tien cum truoc neu tong <= max_w chu - 9 chu van vua 2 dong chu 64px va 2 cum sat nhau), de moi dong phu de la 1 cum nghia tron ven."""
    out = [list(x) for x in srt]; i = 0
    while i < len(out):
        a, b, t = out[i]; n = len(t.split())
        if n < min_w and len(out) > 1:
            pv = out[i - 1] if i > 0 else None; nx = out[i + 1] if i + 1 < len(out) else None
            if pv and len(pv[2].split()) + n <= max_w and a - pv[1] < 0.6:
                pv[1] = b; pv[2] = pv[2] + ' ' + t; out.pop(i); continue
            if nx and len(nx[2].split()) + n <= max_w and nx[0] - b < 0.6:
                nx[0] = a; nx[2] = t + ' ' + nx[2]; out.pop(i); continue
        i += 1
    return [tuple(x) for x in out]


def word_times(srt):
    # moc tung chu trong moi dong SRT, chia theo do dai chu (karaoke)
    out = []
    for a, b, t in merge_short_cues(srt):
        ws = t.split()
        wt = [len(w) + 2 for w in ws]; tot = float(sum(wt)) or 1.0; c = a
        line = []
        for w, k in zip(ws, wt):
            e = c + (b - a) * k / tot; line.append((c, e, w)); c = e
        out.append((a, b, line))
    return out


def sfx(kind, path):
    # tieng hieu ung tu tao, khong ban quyen
    if kind == 'whoosh':
        f = "anoisesrc=d=0.45:c=pink:a=0.5,highpass=f=500,lowpass=f=6000,afade=t=in:d=0.18,afade=t=out:st=0.2:d=0.25"
    elif kind == 'sting':
        f = "sine=f=55:d=0.9,volume=2.5,afade=t=out:st=0.05:d=0.85"
    else:  # pop
        f = "sine=f=880:d=0.08,afade=t=out:d=0.08"
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f, '-ar', '44100', '-ac', '2', path])
    return path


def band(d, y0, y1):
    for y in range(y0, y1):
        a = (y - y0) / max(1, y1 - y0)
        d.line([(0, y), (W, y)], fill=tuple(int(BLUE1[i] * (1 - a) + BLUE2[i] * a) for i in range(3)))


def text_c(d, y, s, f, fill, stroke=3):
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def cover(img, w, h, z, fx, fy):
    iw, ih = img.size; s = max(w / iw, h / ih) * z
    cw, ch = w / s, h / s
    cx = min(max(iw * fx, cw / 2), iw - cw / 2); cy = min(max(ih * fy, ch / 2), ih - ch / 2)
    return img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((w, h), Image.BILINEAR)


def main():
    inp = json.loads(os.environ['SPEC_JSON'])
    br, dd = inp['branch'], inp['dir'].strip('/')
    subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
    __import__('gitlay').lay(dd)
    D_ = os.path.join(ROOT, dd)
    sp = json.load(open(os.path.join(D_, 'spec.json'), encoding='utf-8'))
    ch = sp.get('channel', 'cck')
    srt = []
    if sp.get('voice_urls'):
        # nhieu doan giong (doan co ten rieng doc cham hon) -> ghep lai, doi moc SRT
        parts, off = [], 0.0
        for i, u in enumerate(sp['voice_urls']):
            pth = get(u, os.path.join(OUT, f'vp{i}.mp3'))
            wav = os.path.join(OUT, f'vp{i}.wav')
            dd, lead = voice_part(pth, wav, sp, i)
            su = (sp.get('srt_urls') or [])[i] if i < len(sp.get('srt_urls') or []) else ''
            if su:
                try:
                    for a, b, t in parse_srt(open(get(su, os.path.join(OUT, f'vp{i}.srt')), encoding='utf-8').read()):
                        srt.append((max(0, a - lead) + off, max(0, b - lead) + off, t))
                except Exception as e: print('srt', i, e)
            parts.append(wav); off += dd
        lst = os.path.join(OUT, 'vlist.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
        voice = os.path.join(OUT, 'voice.wav')
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', voice])
    else:
        voice = get(sp['voice_url'], os.path.join(OUT, 'voice.mp3'))
        try: srt = parse_srt(open(get(sp['srt_url'], os.path.join(OUT, 'v.srt')), encoding='utf-8').read())
        except Exception as e: print('srt', e)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', voice]).decode().strip())
    LEAD, TAIL = 0.3, 3.0
    D = dur + LEAD + TAIL
    imgs = [Image.open(os.path.join(D_, s)).convert('RGB') for s in sp['scenes'] if os.path.exists(os.path.join(D_, s))]
    if not imgs: sys.exit('khong co anh canh')
    global BLUE1, BLUE2
    if ch == 'ksc': BLUE1, BLUE2 = (70, 16, 14), (120, 34, 24)  # Ky Su Chien: do dong
    mpath = os.path.join(ROOT, 'editor', 'war' if ch in ('war', 'ksc') else 'story', sp.get('mascot', 'mascot.jpg'))
    masc = Image.open(mpath).convert('RGB')
    # tach nen trang cua mascot
    ma = np.array(masc).astype(int); alpha = (255 - np.clip((ma.min(axis=2) - 195) * 7, 0, 255)).astype('uint8')
    am = Image.fromarray(alpha).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    mascA = masc.copy(); mascA.putalpha(am)
    mascA = mascA.resize((330, 330), Image.LANCZOS)
    fS = fnt(True, 54); fE = fnt(True, 50); fC = fnt(True, 66); fP = fnt(True, 40); fN = fnt(True, 66)
    series = sp['series'].upper(); ept = sp['ep_title']; part = f"PHẦN {sp['part']}/{sp['total']}" if int(sp.get('total', 1)) > 1 else (sp.get('badge') or '')
    # khung
    # 19/11: bo cuc theo vung an toan Reels/TikTok/Shorts (tren 160px, duoi ~480px, phai ~140px bi giao dien che)
    TOP = (0, 406); PANEL = (100, 418, 100 + 800, 418 + 794); BOT = (1222, 1290)
    n = len(imgs); seg = dur / n
    srt = fix_cues(srt)
    starts = scene_starts(sp, srt, n, dur)
    print('starts', [round(x, 1) for x in starts])
    fx = [str(x or '').lower() for x in (sp.get('fx') or [])] + [''] * n
    hook = (sp.get('hook_text') or '').strip().upper()
    wts = word_times(srt)
    fH = fnt(True, 92); fCk = fnt(True, 64)
    KEY = (255, 77, 77)
    raw = os.path.join(OUT, 'v_tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', raw], stdin=subprocess.PIPE)
    base = Image.new('RGB', (W, H), (10, 18, 40)); bd = ImageDraw.Draw(base)
    band(bd, TOP[0], TOP[1]); bd.rectangle([0, TOP[1] - 8, W, TOP[1]], fill=YEL)
    # ten series: 1 dong, tu thu nho chu cho vua vung an toan
    while bd.textlength(series, font=fS) > safezone.MAXW_C540 and fS.size > 40: fS = fnt(True, fS.size - 2)
    if bd.textlength(series, font=fS) <= safezone.MAXW_C540: text_c(bd, 276, series, fS, YEL)
    else:  # qua dai: 2 dong chu 40
        for k, ln in enumerate(wrap_bal(bd, series, fS, safezone.MAXW_C540)[:2]): text_c(bd, 268 + k * 42, ln, fS, YEL)
    band(bd, BOT[0], BOT[1]); bd.rectangle([0, BOT[0], W, BOT[0] + 6], fill=(120, 80, 255))
    fE1 = fnt(True, 44)
    for k, ln in enumerate(wrap(bd, ept, fE1, safezone.MAXW_C540)[:1]):
        text_c(bd, BOT[0] + 10, ln, fE1, YEL)
    pw = bd.textlength(part, font=fP)
    for i in range(int(D * FPS)):
        t = i / FPS; tv = t - LEAD
        im = base.copy(); d = ImageDraw.Draw(im)
        k = max([i_ for i_ in range(n) if starts[i_] <= max(0.0, tv)] or [0])
        e_ = starts[k + 1] if k + 1 < n else dur; lt = (tv - starts[k]) / max(0.5, e_ - starts[k])
        pwid, phei = PANEL[2] - PANEL[0], PANEL[3] - PANEL[1]
        d.rectangle(PANEL, fill=WHITE)
        f_ = fx[k]; ts = max(0.0, tv - starts[k])
        rz, rx = reframe(ts, e_ - starts[k])
        z = 1.04 + 0.08 * ease(lt) + rz
        if f_ == 'punch': z = 1.04 + 0.22 * (1 - ease(ts / 0.45)) + 0.06 * ease(lt) + rz
        sc = cover(imgs[k], pwid - 20, phei - 20, z, 0.5 + 0.04 * math.sin(k) + rx, 0.5)
        if lt < 0.08 and k > 0 and f_ not in ('flash', 'punch'):  # pop-in
            q = ease(lt / 0.08); sc = Image.blend(cover(imgs[k - 1], pwid - 20, phei - 20, 1.12, 0.5, 0.5), sc, q)
        ox = oy = 0
        if f_ == 'shake' and ts < 0.7:
            amp = 16 * (1 - ts / 0.7); ox = int(amp * math.sin(ts * 90)); oy = int(amp * math.cos(ts * 71))
        im.paste(sc, (PANEL[0] + 10 + ox, PANEL[1] + 10 + oy))
        if f_ in ('flash', 'shake') and ts < 0.3 and tv >= 0:
            im = Image.blend(im, Image.new('RGB', (W, H), WHITE), 0.75 * (1 - ts / 0.3)); d = ImageDraw.Draw(im)
        # 19/11: bo mascot de len tranh (che noi dung)
        d = ImageDraw.Draw(im)
        bx = (W - pw) / 2
        if part: d.rounded_rectangle([bx - 22, 350, bx + pw + 22, 400], 18, fill=(200, 30, 40)); d.text((bx, 352), part, font=fP, fill=WHITE)
        # chu hook 3-7 chu, 0-2.6s
        if hook and tv < 2.6:
            q = ease(min(1.0, (tv + LEAD) / 0.25)) * (1 - ease(max(0.0, tv - 2.3) / 0.3))
            hl = wrap_bal(d, hook, fH, safezone.MAXW_C540)[:3]; hh = 110 * len(hl) + 50
            y0 = PANEL[1] + 330
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([100, y0, 980, y0 + hh], 30, fill=(10, 12, 24, int(215 * q)))
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            if q > 0.05:
                sz = int(92 * (0.85 + 0.15 * q)); f2 = fnt(True, sz)
                for j, ln in enumerate(hl):
                    text_c(d, y0 + 28 + j * 110, ln, f2, YEL, 5)
        cur = next((s for s in wts if s[0] - 0.05 <= tv < s[1] + 0.1), None)
        if cur and t < D - TAIL:
            ws = cur[2]; txt = ' '.join(w for _, _, w in ws)
            lines = wrap_bal(d, txt, fCk, safezone.MAXW_C540)[:2]
            y = 1292; wi = 0
            for j, ln in enumerate(lines):
                x = (W - d.textlength(ln, font=fCk)) / 2
                for wd in ln.split(' '):
                    a_, b_, _ = ws[wi] if wi < len(ws) else (0, 0, wd); wi += 1
                    key = (wd.strip('.,!?…:;"“”').isupper() and len(wd.strip('.,!?…:;"“”')) > 1) or re.match(r'^[\d.,%]+$', wd.strip('.,!?'))
                    wl = d.textlength(wd, font=fCk)
                    if a_ <= tv < b_ + 0.02:  # chu dang doc: nen vang, nay nhe
                        pq = ease(min(1.0, (tv - a_) / 0.08))
                        d.rounded_rectangle([x - 10, y + j * 80 - 4 - 6 * pq, x + wl + 10, y + j * 80 + 82], 14, fill=YEL)
                        d.text((x, y + j * 80 - 6 * pq), wd, font=fCk, fill=INK)
                    else:
                        col = KEY if key else (WHITE if tv >= a_ else (225, 230, 240))
                        d.text((x, y + j * 80), wd, font=fCk, fill=col, stroke_width=4, stroke_fill=(0, 0, 0))
                    x += d.textlength(wd + ' ', font=fCk)
        if t >= D - TAIL:
            q = ease((t - (D - TAIL)) / 0.35)
            im = Image.blend(im, Image.new('RGB', (W, H), (8, 12, 28)), 0.9 * q); d = ImageDraw.Draw(im)
            nxt = sp.get('next') or 'Phần tiếp theo'
            text_c(d, 560, 'ĐÓN XEM', fnt(True, 96), YEL, 5)
            for j, ln in enumerate(wrap_bal(d, nxt, fN, safezone.MAXW_C540)[:3]):
                text_c(d, 720 + j * 90, ln, fN, WHITE, 4)
            fB = fnt(True, 42); lab = '👉 Bấm THEO DÕI để không bỏ lỡ'.replace('👉 ', '')
            bw = d.textlength(lab, font=fB)
            d.rounded_rectangle([(W - bw) / 2 - 40, 1060, (W + bw) / 2 + 40, 1150], 30, fill=(200, 30, 40))
            d.text(((W - bw) / 2, 1078), lab, font=fB, fill=WHITE)
            if t >= D - 1.0: im.paste(mascA, (W // 2 - 165, 1170), mascA)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    mus = os.path.join(ROOT, 'editor', 'war' if ch in ('war', 'ksc') else 'story', 'music_a.mp3')
    tmp = os.path.join(OUT, 'out.tmp.mp4')
    wh = sfx('whoosh', os.path.join(OUT, 'wh.wav')); st = sfx('sting', os.path.join(OUT, 'st.wav'))
    ev = [(starts[k] + LEAD - 0.12, wh, 0.35) for k in range(1, n)] + [(starts[k] + LEAD, st, 0.6) for k in range(n) if fx[k] in ('shake', 'flash')]
    if hook: ev.append((LEAD, st, 0.5))
    ins, fl = [], []
    for j, (tt, f_, vol) in enumerate(ev):
        ins += ['-i', f_]; ms = max(0, int(tt * 1000))
        fl.append(f'[{3 + j}:a]adelay={ms}|{ms},volume={vol}[e{j}]')
    mixin = '[v][m]' + ''.join(f'[e{j}]' for j in range(len(ev)))
    fc = f'[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)}[v];[2:a]volume=0.12[m];' + ''.join(x + ';' for x in fl) + \
         f'{mixin}amix=inputs={2 + len(ev)}:duration=first:normalize=0,apad,loudnorm=I=-15:TP=-1.5[a]'
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-i', voice, '-stream_loop', '-1', '-i', mus] + ins +
                          ['-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{D:.2f}', tmp])
    os.replace(tmp, os.path.join(OUT, 'out.mp4'))
    print('ok', round(D, 2))


if __name__ == '__main__':
    main()
