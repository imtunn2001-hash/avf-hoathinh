#!/usr/bin/env python3
"""AVF Video Editor (FFmpeg). Usage: python editor/render.py spec.json out.mp4
spec.json: {
  "mc_video": "mc.mp4" | null, "mc_image": "mc.png" | null,   # MC la nhan vat chinh (video HeyGen hoac anh tinh de demo)
  "fps": "30" | "native",                                      # native = giu fps goc cua MP4 (vd 25) -> khong lap khung hinh
  "trim_start": 17.10,                                         # cat dong bo hinh+tieng tu giay nay (bo phan doc huong dan); mac dinh 0
  "voice_trim": 0,                                             # chi dung khi "voice" rieng CHUA cat; mac dinh 0 (coi la da cat san, khong cat 2 lan)
  "voice": "voice.mp3" | null,                                 # null => dung am thanh trong mc_video
  "sentences": ["...", ...],                                   # kich ban theo cau (dung de hien phu de dung chinh ta)
  "keywords": ["vàng", ...],                                   # tu khoa to mau vang
  "cards": [{"sentence": 2, "title": "...", "sub": "...", "label": "MINH HỌA", "kind": "text|chart|arrows"}],
  "channel_tag": "GOLD AI NEWS • BẢN TIN VÀNG"
}
Timing: faster-whisper (neu co) -> neu loi, fallback khoang lang + chia theo so tu. Bao cao ra timing.json.
"""
import json, re, subprocess, sys, random, math, os, difflib
from PIL import Image, ImageDraw, ImageFont
FB = os.environ.get('AVF_FONT', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
spec = json.load(open(sys.argv[1])); OUT = sys.argv[2]
def run(c, **k): return subprocess.run(c, check=True, capture_output=True, text=True, **k)
src = spec.get('mc_video') or spec['mc_image']; is_vid = bool(spec.get('mc_video'))
voice = spec.get('voice') or spec.get('mc_video')
# trim_start chi cat nguon CHUA cat (video HeyGen goc va am thanh cua chinh video do).
# Neu co 'voice' rieng thi coi la da cat san: chi cat them neu dat 'voice_trim' (mac dinh 0). Che do anh tinh: bo qua trim_start.
VTRIM = float(spec.get('trim_start', 0)) if is_vid else 0.0
ATRIM = float(spec.get('voice_trim', 0)) if spec.get('voice') else VTRIM
if not is_vid and float(spec.get('trim_start', 0)): print('CANH BAO: che do anh tinh bo qua trim_start')
TRIM = ATRIM
probe = lambda f: float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).stdout.strip())
D = probe(voice) - ATRIM
if is_vid: D = min(D, probe(src) - VTRIM)
D = round(D, 2)
if D <= 1: raise SystemExit(f'trim_start={VTRIM}/voice_trim={ATRIM} vuot do dai nguon')
# am thanh da cat dong bo (cung moc voi hinh) dung cho phu de
run(['ffmpeg','-y','-ss',str(TRIM),'-t',str(D),'-i',voice,'-vn','-ac','1','-ar','16000','voice_work.wav'])
WORK = 'voice_work.wav'
sents = spec['sentences']
words = [(w, si) for si, s in enumerate(sents) for w in s.split()]
norm = lambda w: re.sub(r'[^\wÀ-ỹ]', '', w).lower()
# ---------- timing ----------
def whisper_times():
    from faster_whisper import WhisperModel
    wav = WORK
    m = WhisperModel(os.environ.get('AVF_WHISPER','small'), device='cpu', compute_type='int8')
    segs, _ = m.transcribe(wav, language='vi', word_timestamps=True, vad_filter=False, initial_prompt=' '.join(sents))
    ws = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
    a = [norm(w) for w, _ in words]; b = [x[0] for x in ws]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False); tim = [None]*len(a)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): tim[blk.a+k] = (ws[blk.b+k][1], ws[blk.b+k][2])
    ok = sum(t is not None for t in tim)
    if ok < 0.6*len(a): raise RuntimeError(f'whisper khop {ok}/{len(a)} tu')
    # noi suy cho tu thieu
    i = 0
    while i < len(tim):
        if tim[i] is None:
            j = i
            while j < len(tim) and tim[j] is None: j += 1
            lo = tim[i-1][1] if i > 0 else 0.0; hi = tim[j][0] if j < len(tim) else D
            for k in range(i, j): tim[k] = (lo+(hi-lo)*(k-i)/(j-i), lo+(hi-lo)*(k-i+0.9)/(j-i))
            i = j
        else: i += 1
    return tim, f'whisper({ok}/{len(a)} tu khop)'
def silence_times():
    out = subprocess.run(['ffmpeg','-hide_banner','-i',WORK,'-af','silencedetect=noise=-35dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
    act = []; p = 0.0
    for k, a in enumerate(st):
        if a > p+0.05: act.append((p, a))
        p = en[k] if k < len(en) else D
    if p < D-0.05: act.append((p, D))
    tot = sum(b-a for a, b in act)
    def at(x):
        for a, b in act:
            if x <= b-a+1e-9: return a+x
            x -= b-a
        return act[-1][1]
    wt = [1.0+0.25*(len(norm(w)) > 5)+0.5*(w[-1] in ',.!?') for w, _ in words]; T = sum(wt); c = 0; tim = []
    for x in wt: tim.append((at(c/T*tot), at((c+x*0.88)/T*tot))); c += x
    # neo dau cau vao khoang lang gan nhat (chinh xac hon chia deu theo so tu)
    ends = [en_ for en_ in en if en_ < D-0.3]
    first = []; i = 0
    for s_ in sents: first.append(i); i += len(s_.split())
    S = [act[0][0]]; used = set()
    for si in range(1, len(sents)):
        t0 = tim[first[si]][0]; cand = [e for e in ends if abs(e-t0) < 1.3 and e > S[-1]+0.4 and e not in used]
        e = min(cand, key=lambda e: abs(e-t0)) if cand else t0; used.add(e); S.append(e)
    S.append(act[-1][1]); tim = []
    for si, s_ in enumerate(sents):
        lo, hi = S[si], S[si+1]-(0.1 if si+1 < len(sents) else 0)
        seg = [(max(a_, lo), min(b_, hi)) for a_, b_ in act if min(b_, hi) > max(a_, lo)] or [(lo, hi)]
        tot_s = sum(b_-a_ for a_, b_ in seg)
        def at_s(x, seg=seg):
            for a_, b_ in seg:
                if x <= b_-a_+1e-9: return a_+x
                x -= b_-a_
            return seg[-1][1]
        ws_ = s_.split(); w_ = [1.0+0.25*(len(norm(w)) > 5)+0.5*(w[-1] in ',.!?') for w in ws_]; T_ = sum(w_); c_ = 0
        for x in w_: tim.append((at_s(c_/T_*tot_s), at_s((c_+x*0.88)/T_*tot_s))); c_ += x
    return tim, 'silence-fallback(uoc luong)'
try: tim, method = whisper_times()
except Exception as e: print('whisper khong dung duoc:', str(e)[:120]); tim, method = silence_times()
print('timing method:', method)
sstart = []; i = 0
for s in sents: sstart.append(tim[i][0]); i += len(s.split())
json.dump({'method': method, 'duration': D, 'words': [{'w': w, 's': round(a, 2), 'e': round(b, 2)} for (w, _), (a, b) in zip(words, tim)]}, open('timing.json','w'), ensure_ascii=False)
# ---------- subtitles (ASS) ----------
KW = set(norm(k) for kw in spec.get('keywords', []) for k in kw.split())
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
GOLD, WHITE = '&H3CC8FF&', '&HFFFFFF&'; ev = []; chunks = []; idx = 0
for s in sents:
    n_w = len(s.split()); k = 0
    while k < n_w:
        n = min(4, n_w-k)
        if n_w-k-n == 1: n = min(5, n+1)
        chunks.append(list(range(idx+k, idx+k+n))); k += n
    idx += n_w
for ch in chunks:
    for j, wi in enumerate(ch):
        st = tim[wi][0]; en = tim[ch[j+1]][0] if j+1 < len(ch) else tim[wi][1]+0.12; txt = []
        for wk in ch:
            w = words[wk][0]
            if wk == wi: txt.append(r'{\c'+GOLD+r'\fscx115\fscy115}'+w+r'{\c'+WHITE+r'\fscx100\fscy100}')
            elif norm(w) in KW: txt.append(r'{\c'+GOLD+r'}'+w+r'{\c'+WHITE+r'}')
            else: txt.append(w)
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{{\\an2\\fad(40,0)}}"+' '.join(txt))
tag = spec.get('channel_tag', '')
if tag: ev.append(f"Dialogue: 1,{ts(0.2)},{ts(2.6)},Tag,,0,0,0,,{{\\an1\\pos(70,330)\\fad(300,300)}}{tag}")
open('subs.ass','w').write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Sub,DejaVu Sans,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,300,1
Style: Tag,DejaVu Sans,40,&H0037C8FF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,3,2,0,1,60,60,60,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""+'\n'.join(ev)+'\n')
# ---------- cards (b-roll / bieu do minh hoa, luon co nhan) ----------
font = lambda s: ImageFont.truetype(FB, s)
def ctr(d, y, t, s, col=(255,255,255)):
    f = font(s); w = d.textlength(t, font=f); d.text(((900-w)/2, y), t, font=f, fill=col)
cards = []
for n, c in enumerate(spec.get('cards', [])):
    im = Image.new('RGBA', (900, 400), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,899,399), 40, fill=(8,24,56,215), outline=(255,200,60,255), width=5)
    kind = c.get('kind', 'text'); label = c.get('label', '')
    if kind == 'chart':
        random.seed(n+3); pts = []; y = 250
        for i in range(24): y += random.uniform(-26,22); y = min(max(y,120),300); pts.append((70+i*33, y))
        ctr(d, 18, c['title'], 38, (255,200,60)); d.line(pts, fill=(255,200,60), width=8, joint='curve')
        d.text((70,350), label or 'MINH HỌA - không phải số liệu thực', font=font(26), fill=(200,210,230))
    elif kind == 'arrows':
        ctr(d, 40, c['title'], 58, (255,200,60))
        d.polygon([(250,330),(170,200),(330,200)], fill=(255,90,90)); d.text((120,340), c.get('left',''), font=font(34), fill=(255,255,255))
        d.polygon([(650,200),(570,330),(730,330)], fill=(80,220,120)); d.text((520,340), c.get('right',''), font=font(34), fill=(255,255,255))
    else:
        ctr(d, 70, c['title'], 86 if len(c['title']) < 14 else 64, (255,200,60)); ctr(d, 200, c.get('sub',''), 44)
        if label: d.text((20,360), label, font=font(24), fill=(200,210,230))
    fn = f'card{n}.png'; im.save(fn)
    a = sstart[c['sentence']]+0.3; b = (sstart[c['sentence']+1]-0.2) if c['sentence']+1 < len(sents) else D-0.2
    cards.append((fn, a, b))
# ---------- zoom + filter graph ----------
def src_fps():
    # tra ve (chuoi phan so goc, so thuc), vd ('30000/1001', 29.97)
    r = run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=avg_frame_rate','-of','csv=p=0',src]).stdout.strip()
    a, b = (r.split('/') + ['1'])[:2]
    try: v = float(a)/float(b)
    except Exception: v = 0.0
    return (r if '/' in r else a, v)
want = str(spec.get('fps', '30')).lower()
if want == 'native' and is_vid:
    fr, nf = src_fps()
    if 23 <= nf <= 31: FPSF, FPS = fr, nf          # giu CHINH XAC nhip goc (ke ca 24000/1001, 30000/1001)
    else: FPSF, FPS = '30', 30.0
else: FPSF, FPS = '30', 30.0
print('fps dau ra:', FPSF, f'= {FPS:.4f}', '(che do:', want + ')')
zkw = set(norm(k) for k in spec.get('zoom_words', ['vàng','đô','chốt','cao','ngược','nhạy','thận','kênh']))
pt = [tim[i][0] for i, (w, _) in enumerate(words) if norm(w) in zkw]
zexpr = f"1.0+0.06*(on/{FPS:.6f})/{D}+" + '+'.join(f"if(gte(on/{FPS:.6f},{x:.2f}),0.045*exp(-7*(on/{FPS:.6f}-{x:.2f})),0)" for x in pt) if pt else f"1.0+0.06*(on/{FPS:.6f})/{D}"
inp = (['-ss',str(VTRIM),'-t',str(D),'-i',src] if is_vid else ['-loop','1','-framerate',FPSF,'-t',str(D),'-i',src])
vi = 1 if spec.get('voice') else 0
if spec.get('voice'): inp += ['-ss',str(ATRIM),'-t',str(D),'-i', spec['voice']]
for fn, a, b in cards: inp += ['-loop','1','-t',str(D),'-i',fn]
n_in = (2 if spec.get('voice') else 1)
inp += ['-f','lavfi','-t',str(D),'-i','sine=f=220:r=44100','-f','lavfi','-t',str(D),'-i','sine=f=277.18:r=44100','-f','lavfi','-t',str(D),'-i','sine=f=329.63:r=44100','-f','lavfi','-t','0.6','-i','anoisesrc=d=0.6:c=pink:r=44100']
pre = f"fps={FPSF},scale=2160:3840:force_original_aspect_ratio=increase:flags=lanczos,crop=2160:3840,setsar=1" if is_vid else "scale=2160:3840:flags=lanczos"
fil = [f"[0:v]{pre},zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPSF}[b0]"]
prev = 'b0'
for i, (fn, a, b) in enumerate(cards):
    k = n_in+i
    fil.append(f"[{k}:v]scale=760:-1,format=rgba,fade=t=in:st={a:.2f}:d=0.3:alpha=1,fade=t=out:st={b-0.3:.2f}:d=0.3:alpha=1[k{i}]")
    fil.append(f"[{prev}][k{i}]overlay=x=160:y='if(lt(t,{a+0.3:.2f}),60-120*(1-(t-{a:.2f})/0.3),60)':enable='between(t,{a:.2f},{b:.2f})'[o{i}]"); prev = f'o{i}'
fil.append(f"[{prev}]subtitles=subs.ass,fade=t=in:st=0:d=0.3,fade=t=out:st={D-0.4:.2f}:d=0.4[vout]")
m = n_in+len(cards)
fil.append(f"[{m}:a][{m+1}:a][{m+2}:a]amix=inputs=3:normalize=0,volume=0.30,afade=t=in:d=1.5,afade=t=out:st={max(D-1.5,0):.2f}:d=1.5[mus]")
ns = max(len(cards), 1)
if cards:
    fil.append(f"[{m+3}:a]highpass=f=600,lowpass=f=6000,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.35,volume=0.5,asplit={ns}"+''.join(f'[w{i}]' for i in range(ns)))
    for i, (fn, a, b) in enumerate(cards): fil.append(f"[w{i}]adelay={int(a*1000)}|{int(a*1000)}[wd{i}]")
fil.append(f"[{vi}:a]asplit=2[v1][v2]")
fil.append("[mus][v2]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[mduck]")
fil.append("[v1][mduck]"+''.join(f'[wd{i}]' for i in range(len(cards)))+f"amix=inputs={2+len(cards)}:normalize=0:duration=first,alimiter=limit=0.89[aout]")
cmd = ['ffmpeg','-y','-hide_banner','-loglevel','error']+inp+['-filter_complex',';'.join(fil),'-map','[vout]','-map','[aout]','-t',str(D),'-r',FPSF,'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT]
subprocess.run(cmd, check=True)
print('OK', OUT, D, 's')
