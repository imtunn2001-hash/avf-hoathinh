# Reels truyen tranh vo chong: anh AI (nhan vat co dinh) + chu thoai + chuyen dong + tieng dong tu tao.
# spec: {panels:[{img, t0, t1, text, anim}], sfx:[{t, kind}], dur, bg?, handle?}
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 44100
FB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
INK = (38, 34, 40)
SPK = {'Vợ': (226, 74, 110), 'Chồng': (46, 104, 196), 'Cô ấy': (226, 74, 110), 'Em': (226, 74, 110), 'Người yêu': (226, 74, 110), 'Anh ấy': (46, 104, 196), 'Anh': (46, 104, 196)}


def font(sz):
    for p in [os.path.join(os.getcwd(), 'fonts', 'BeVietnamPro-ExtraBold.ttf'), FB]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    sys.exit('khong co font')


def wrap(d, s, f, maxw):
    out, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            out.append(cur); cur = w
    if cur: out.append(cur)
    # tranh dong cuoi chi con 1-2 tu: chia lai cho deu
    if len(out) >= 2 and len(out[-1].split()) <= 2:
        words = s.split(); n = len(words)
        for k in range(n // 2, n):
            a, b = ' '.join(words[:k]), ' '.join(words[k:])
            if d.textlength(a, font=f) <= maxw and d.textlength(b, font=f) <= maxw and len(out) == 2:
                if len(words[k:]) >= 2: return [a, b]
    return out


def ease_back(x):
    x = min(max(x, 0), 1); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def round_img(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    return m


def text_block(text, bg):
    # tra ve anh RGBA chua chu thoai, phan ten nguoi noi to mau
    f = font(66); d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    spk, body = None, text
    if ':' in text and text.split(':')[0].split(' (')[0] in SPK:
        spk, body = text.split(':', 1)[0] + ':', text.split(':', 1)[1].strip()
    lines = wrap(d, ((spk + ' ') if spk else '') + body, f, 930)
    lh = 86; im = Image.new('RGBA', (W, lh * len(lines) + 20), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        x = (W - dd.textlength(ln, font=f)) / 2; y = 4 + i * lh
        if i == 0 and spk and ln.startswith(spk):
            col = SPK[spk.split(' (')[0].rstrip(':')]
            dd.text((x, y), spk, font=f, fill=col)
            x += dd.textlength(spk + ' ', font=f); ln = ln[len(spk):].strip()
        dd.text((x, y), ln, font=f, fill=INK)
    return im


def autocrop(im, pad=40, min_ratio=0.9):
    # cat bo dai nen trong 2 ben de tranh to hon tren man doc
    a = np.asarray(im.convert('RGB')).astype(int); edge = np.median(np.concatenate([a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)]), axis=0)
    diff = (np.abs(a - edge).sum(axis=2) > 60).mean(axis=0); cols = np.where(diff > 0.02)[0]
    if len(cols) == 0: return im
    x0, x1 = max(0, cols[0] - pad), min(im.width, cols[-1] + pad)
    need = int(im.height * min_ratio)
    if x1 - x0 < need:
        c = (x0 + x1) // 2; x0 = max(0, min(im.width - need, c - need // 2)); x1 = x0 + need
    return im.crop((x0, 0, x1, im.height))


def bg_of(im):
    a = np.asarray(im.convert('RGB')).astype(int)
    e = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3)])
    return tuple(int(v) for v in np.median(e, axis=0))


# ---------------- am thanh tu tao ----------------
def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * np.exp(-t / r); return e


def sfx(kind):
    if kind == 'boing':
        n = int(SR * 0.7); t = np.arange(n) / SR
        f = 180 + 260 * np.exp(-t * 5) * (1 + 0.35 * np.sin(2 * np.pi * 14 * t))
        return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.28)
    if kind == 'whoosh':
        n = int(SR * 0.5); x = np.random.randn(n); t = np.arange(n) / SR
        k = np.exp(-((t - 0.22) / 0.12) ** 2); y = np.convolve(x, np.ones(6) / 6, 'same') - np.convolve(x, np.ones(40) / 40, 'same')
        return 0.5 * y * k
    if kind == 'click':
        n = int(SR * 0.06); return 0.7 * np.random.randn(n) * env(n, 0.0005, 0.008)
    if kind == 'ding':
        n = int(SR * 1.0); t = np.arange(n) / SR
        return 0.35 * (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)) * env(n, 0.002, 0.35)
    if kind == 'sparkle':
        out = np.zeros(int(SR * 0.8))
        for i, fq in enumerate([1568, 2093, 2637, 3136]):
            n = int(SR * 0.3); t = np.arange(n) / SR; s = int(i * 0.07 * SR)
            out[s:s + n] += 0.18 * np.sin(2 * np.pi * fq * t) * env(n, 0.002, 0.08)
        return out
    if kind == 'crickets':
        n = int(SR * 2.4); t = np.arange(n) / SR
        chirp = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 30 * t) > 0.2)
        gate = ((t % 0.8) < 0.22).astype(float)
        return 0.08 * chirp * gate
    if kind == 'slide_up':
        n = int(SR * 0.6); t = np.arange(n) / SR; f = 400 + 1400 * (t / t[-1]) ** 1.5
        return 0.3 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, (t[-1] - t) * 12) * np.minimum(1, t * 40)
    if kind == 'kick':
        n = int(SR * 0.35); t = np.arange(n) / SR; f = 120 * np.exp(-t * 18) + 45
        return 0.9 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.09) + 0.3 * np.random.randn(n) * env(n, 0.0005, 0.02)
    if kind == 'gulp':
        n = int(SR * 0.25); t = np.arange(n) / SR; f = 300 - 500 * t
        return 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.005, 0.08)
    if kind == 'ting':  # tin nhan den
        n = int(SR * 0.5); t = np.arange(n) / SR
        return 0.3 * (np.sin(2 * np.pi * 1760 * t) * env(n, 0.001, 0.12) + np.roll(np.sin(2 * np.pi * 2349 * t) * env(n, 0.001, 0.15), int(0.09 * SR)))
    if kind == 'vibrate':
        n = int(SR * 0.9); t = np.arange(n) / SR
        return 0.35 * np.sign(np.sin(2 * np.pi * 150 * t)) * ((t % 0.45) < 0.3) * np.random.uniform(0.7, 1, n) * 0.6
    if kind == 'kiss':
        n = int(SR * 0.18); t = np.arange(n) / SR; f = 2200 - 6000 * t
        return 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.03) + 0.2 * np.random.randn(n) * env(n, 0.0005, 0.01)
    if kind == 'heartbeat':
        out = np.zeros(int(SR * 2.0))
        for k in range(3):
            for dt, a in [(0, 1.0), (0.18, 0.7)]:
                n = int(SR * 0.15); t = np.arange(n) / SR; s = int((k * 0.62 + dt) * SR)
                out[s:s + n] += 0.8 * a * np.sin(2 * np.pi * (60 - 80 * t) * t) * env(n, 0.002, 0.05)
        return out
    if kind == 'knock':
        out = np.zeros(int(SR * 0.7))
        for k in range(3):
            n = int(SR * 0.08); t = np.arange(n) / SR; s = int(k * 0.18 * SR)
            out[s:s + n] += 0.7 * (np.sin(2 * np.pi * 180 * t) + 0.4 * np.random.randn(n)) * env(n, 0.0005, 0.02)
        return out
    if kind == 'run':  # buoc chan chay
        out = np.zeros(int(SR * 1.0))
        for k in range(8):
            n = int(SR * 0.05); s = int(k * 0.11 * SR)
            out[s:s + n] += 0.4 * np.random.randn(n) * env(n, 0.0005, 0.012)
        return np.convolve(out, np.ones(8) / 8, 'same') * 3
    if kind == 'slurp':
        n = int(SR * 0.7); t = np.arange(n) / SR; x = np.random.randn(n)
        y = np.convolve(x, np.ones(3) / 3, 'same') * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) * np.minimum(1, t * 10) * np.minimum(1, (t[-1] - t) * 8)
        return 0.25 * y
    if kind == 'chatter':  # rang va lap cap vi lanh
        out = np.zeros(int(SR * 1.2))
        for k in range(16):
            n = int(SR * 0.02); s = int(k * 0.07 * SR)
            out[s:s + n] += 0.35 * np.random.randn(n) * env(n, 0.0003, 0.004)
        return out
    if kind == 'scratch':  # dia nhac ret
        n = int(SR * 0.45); t = np.arange(n) / SR; f = 900 * np.sin(2 * np.pi * 3 * t) + 1100
        return 0.3 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.random.uniform(0.6, 1, n) * np.minimum(1, (t[-1] - t) * 10)
    if kind == 'drumroll':
        n = int(SR * 1.2); t = np.arange(n) / SR
        return 0.3 * np.random.randn(n) * (0.5 + 0.5 * np.sin(2 * np.pi * 22 * t)) * np.minimum(1, t * 1.2) * np.convolve(np.ones(n), [1], 'same')
    if kind == 'wahwah':  # ken buon kieu bi hai
        out = np.zeros(int(SR * 2.5))
        for k, (fq, d) in enumerate([(392, 0.4), (370, 0.4), (349, 0.4), (330, 1.0)]):
            n = int(SR * d); t = np.arange(n) / SR; s = int(k * 0.42 * SR)
            vib = 1 + (0.03 * np.sin(2 * np.pi * 6 * t) if k == 3 else 0)
            ph = 2 * np.pi * np.cumsum(fq * vib) / SR
            tone = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)
            out[s:s + n] += 0.18 * tone * np.minimum(1, t * 30) * np.minimum(1, (t[-1] - t) * 6)
        return out
    n = int(SR * 0.09); t = np.arange(n) / SR
    return 0.4 * np.sin(2 * np.pi * 900 * t) * env(n, 0.001, 0.03)  # pop


def pluck(fq, dur, amp):
    n = int(SR * dur); p = max(2, int(SR / fq)); buf = np.random.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.497 * (buf[i % p] + buf[(i + 1) % p])
    return amp * out


def music(dur, bpm=104, mood='cute'):
    # vong hop am vui C-G-Am-F, dan go nhe (tu tao, khong ban quyen)
    beat = 60 / bpm; out = np.zeros(int(SR * (dur + 2)))
    chords = [[261.6, 329.6, 392.0], [196.0, 246.9, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 349.2]]
    mel = [523.3, 587.3, 659.3, 783.9, 659.3, 587.3, 523.3, 440.0]
    if mood == 'tense':  # hoi hop truoc cu ngoat
        bpm = 92; beat = 60 / bpm
        chords = [[220.0, 261.6, 329.6], [207.7, 246.9, 329.6], [220.0, 261.6, 329.6], [196.0, 246.9, 293.7]]
        mel = [440.0, 0, 415.3, 0, 440.0, 0, 493.9, 0]
    cache = {}
    def pl(fq, d, a):
        k = (round(fq, 1), d, a)
        if k not in cache: cache[k] = pluck(fq, d, a)
        return cache[k]
    i = 0
    while i * beat < dur + 1:
        c = chords[(i // 4) % 4]; s = int(i * beat * SR)
        for j, fq in enumerate(c):
            x = pl(fq, 0.9, 0.16); o = s + int(j * 0.012 * SR); out[o:o + len(x)] += x[:len(out) - o]
        if i % 2 == 1:
            fq = mel[(i // 2) % 8]
            if not fq: i += 1; continue
            x = pl(fq, 0.5, 0.12); o = s + int(beat * 0.5 * SR); out[o:o + len(x)] += x[:len(out) - o]
        i += 1
    out = out[:int(SR * dur)]; fade = int(SR * 0.4); out[-fade:] *= np.linspace(1, 0, fade)
    return out


def mix_audio(spec, path):
    dur = spec['dur']; a = music(dur, mood=spec.get('mood', 'cute')) * spec.get('music_vol', 0.55)
    for s in spec.get('sfx', []):
        x = sfx(s['kind']) * s.get('vol', 1.0); o = int(s['t'] * SR); e = min(len(a), o + len(x)); a[o:e] += x[:e - o]
    a = np.tanh(a * 1.5) * 0.75; pcm = (a * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


# ---------------- hinh ----------------
def render(spec, out):
    panels = spec['panels']; dur = spec['dur']
    imgs = [Image.open(p['img']).convert('RGB') for p in panels]
    bg = tuple(spec.get('bg') or bg_of(imgs[0]))
    PW = 1030; prep = []
    imgs = [autocrop(im) for im in imgs]
    for p, im in zip(panels, imgs):
        h = int(PW * im.height / im.width); im = im.resize((PW, h), Image.LANCZOS)
        fr = Image.new('RGB', (PW + 12, h + 12), INK); fr.paste(im, (6, 6))
        prep.append((fr, round_img(fr, 34), text_block(p.get('text', ''), bg) if p.get('text') else None))
    hf = font(34)
    wav = out + '.wav'; mix_audio(spec, wav)
    tmp = out + '.tmp.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-19:TP=-2:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-shortest', '-movflags', '+faststart', tmp], stdin=subprocess.PIPE)
    N = int(dur * FPS)
    for k in range(N):
        t = k / FPS
        idx = max(i for i, p in enumerate(panels) if t >= p['t0'] - 1e-6); p = panels[idx]; fr, mask, tb = prep[idx]
        lt = t - p['t0']; ln = p['t1'] - p['t0']; anim = p.get('anim', 'zoom')
        canvas = Image.new('RGB', (W, H), bg)
        s = 1.0 + 0.05 * (lt / ln); dx = dy = 0
        if 'pop' in anim: s *= 0.82 + 0.18 * ease_back(lt / 0.35)
        if 'shake' in anim and lt < 0.6: dx = int(18 * math.sin(lt * 70) * (1 - lt / 0.6)); dy = int(10 * math.cos(lt * 55) * (1 - lt / 0.6))
        if 'bounce' in anim: dy = int(-60 * abs(math.sin(lt * 7)) * math.exp(-lt * 2.2))
        w2, h2 = int(fr.width * s), int(fr.height * s)
        f2 = fr.resize((w2, h2), Image.BILINEAR); m2 = mask.resize((w2, h2), Image.BILINEAR)
        cy = spec.get('panel_cy', 1130)
        canvas.paste(f2, ((W - w2) // 2 + dx, cy - h2 // 2 + dy), m2)
        if tb is not None:
            tt = lt - p.get('text_delay', 0)
            if tt >= 0:
                a = min(1, tt / 0.18); sc = 0.9 + 0.1 * ease_back(tt / 0.3)
                t2 = tb.resize((int(tb.width * sc), int(tb.height * sc)), Image.BILINEAR)
                if a < 1: t2.putalpha(t2.getchannel('A').point(lambda v: int(v * a)))
                ty = cy - fr.height // 2 - 60 - t2.height
                canvas.paste(t2, ((W - t2.width) // 2, ty), t2)
        if 'flash' in anim and lt < 0.25:
            canvas = Image.blend(canvas, Image.new('RGB', (W, H), (255, 255, 255)), 0.85 * (1 - lt / 0.25))
        if spec.get('cta') and idx == len(panels) - 1 and lt > 0.8:
            d = ImageDraw.Draw(canvas); cf = font(46); s2 = spec['cta']; tw = d.textlength(s2, font=cf)
            y0 = cy + fr.height // 2 + 70; bump = int(6 * math.sin(lt * 6))
            d.rounded_rectangle([(W - tw) / 2 - 34, y0 - 18 + bump, (W + tw) / 2 + 34, y0 + 66 + bump], 40, fill=(255, 255, 255), outline=SPK['Vợ'], width=5)
            d.text(((W - tw) / 2, y0 + bump), s2, font=cf, fill=SPK['Vợ'])
        if spec.get('handle'):
            d = ImageDraw.Draw(canvas); h = spec['handle']
            d.text(((W - d.textlength(h, font=hf)) / 2, cy + fr.height // 2 + 70), h, font=hf, fill=(150, 140, 130))
        ff.stdin.write(canvas.tobytes())
    ff.stdin.close(); ff.wait(); os.remove(wav)
    if ff.returncode == 0: os.replace(tmp, out)
    else: sys.exit('ffmpeg loi')


if __name__ == '__main__':
    spec = json.loads(os.environ.get('SPEC_JSON') or open(sys.argv[1]).read())
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join('out', 'out.mp4')
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    if spec.get('git_branch'):  # anh nam tren nhanh cp-assets
        subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', spec['git_branch']], check=True)
        for p in spec['panels']:
            __import__('gitlay').lay(p['img'])
    render(spec, out)
