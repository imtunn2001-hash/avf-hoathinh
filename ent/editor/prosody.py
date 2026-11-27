"""Giong doc co nhip (skill giong-doc-ngat-nghi).

parse(script, base_speed) -> list cum {text, speed, pitch, volume, pause_after}
  Ky hieu: /  //  ///  [nghi 1.2]  {cham: ..} {rat cham: ..} {nhan: ..} {ha: ..} {nhanh: ..} {cao: ..}
build(chunks, out_wav, workdir) : moi cum co 'url' (mp3 TTS) -> cat lang dau/cuoi, dem dung pause_after, noi lai.
  Tra ve list do dai tung cum (giay, da gom ca khoang nghi).
main(): kind 'prosody' tren GitHub (ent.yml): SPEC_JSON {title, chunks:[{text,url,pause_after}]} -> out/out.mp4 (the chu + giong) + qc.json.
"""
import json, os, re, subprocess, sys, urllib.request

PAUSE = {'/': 0.25, '//': 0.5, '///': 0.9}
STYLE = {   # ten -> (he so speed so voi base, pitch, volume, nghi truoc)
    'cham': (0.8 / 0.95, 1.0, 100, 0.0), 'rat cham': (0.7 / 0.95, 1.0, 100, 0.0),
    'nhan': (0.85 / 0.95, 1.05, 100, 0.15), 'ha': (0.85 / 0.95, 0.93, 85, 0.0),
    'nhanh': (1.05 / 0.95, 1.0, 100, 0.0), 'cao': (1.0, 1.06, 100, 0.0),
}
ALIAS = {'chậm': 'cham', 'rất chậm': 'rat cham', 'nhấn': 'nhan', 'hạ': 'ha', 'nhanh': 'nhanh', 'cao': 'cao'}
TOK = re.compile(r'\{([^:{}]+):\s*([^{}]*)\}|\[nghỉ\s*([\d.]+)\]|(/{1,3})|([^{}\[/]+)')
SR = 44100
TRIM = ('silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.04,areverse,'
        'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,areverse')


def _syl(t): return len(re.findall(r'\w+', t))


def parse(script, base_speed=0.95):
    out = []
    def add(text, style=None):
        text = ' '.join(text.split())
        if not text: return
        k = ALIAS.get(style.strip(), style.strip()) if style else None
        f, pitch, vol, pre = STYLE.get(k, (1.0, 1.0, 100, 0.0))
        if pre and out: out[-1]['pause_after'] = max(out[-1]['pause_after'], pre)
        out.append(dict(text=text, speed=round(base_speed * f, 2), pitch=pitch, volume=vol, pause_after=0.0, style=k or ''))
    for m in TOK.finditer(script):
        st, body, sec, sl, plain = m.groups()
        if st is not None: add(body, st)
        elif sec: (out[-1].__setitem__('pause_after', out[-1]['pause_after'] + float(sec)) if out else None)
        elif sl: (out[-1].__setitem__('pause_after', max(out[-1]['pause_after'], PAUSE[sl])) if out else None)
        elif plain:
            # cau ket thuc bang dau cham/hoi ma khong co ky hieu -> nghi mac dinh
            for part in re.split(r'(?<=[.!?…])\s+', plain):
                if part.strip():
                    add(part)
                    if re.search(r'[.!?…]\s*$', part): out[-1]['pause_after'] = max(out[-1]['pause_after'], 0.6 if part.strip().endswith('?') else 0.4)
    # cum qua ngan (< 3 am tiet) doc rieng nghe cut: khong nghi sau -> gop vao cum SAU; co nghi -> gop vao cum TRUOC
    merged = []; i = 0
    while i < len(out):
        c = out[i]
        if _syl(c['text']) < 3 and c['pause_after'] < 0.2 and i + 1 < len(out):
            out[i + 1]['text'] = c['text'] + ' ' + out[i + 1]['text']; i += 1; continue
        if _syl(c['text']) < 3 and merged and merged[-1]['pause_after'] <= 0.2:
            merged[-1]['text'] += ' ' + c['text']; merged[-1]['pause_after'] = c['pause_after']; i += 1; continue
        merged.append(c); i += 1
    return merged


def _get(url, path):
    if os.path.exists(url): return url
    for _ in range(3):
        try:
            urllib.request.urlretrieve(url, path); return path
        except Exception as e: err = e
    raise err


def build(chunks, out_wav, workdir):
    parts, durs = [], []
    for i, c in enumerate(chunks):
        src = _get(c['url'], os.path.join(workdir, f'pc{i}.mp3')); wv = os.path.join(workdir, f'pc{i}.wav')
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', src, '-ar', str(SR), '-ac', '2',
                               '-af', TRIM + ',apad=pad_dur=%.2f' % max(0.0, float(c.get('pause_after', 0)) - 0.1), wv])   # 0.1 s = phan lang 2 dau giu lai khi cat
        d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wv]).decode())
        parts.append(wv); durs.append(d)
    lst = os.path.join(workdir, 'pl.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out_wav])
    return durs


def silences(wav, n=-40, d=0.2):
    r = subprocess.run(['ffmpeg', '-i', wav, '-af', f'silencedetect=n={n}dB:d={d}', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]
    return [(round(a, 2), round(b - a, 2)) for a, b in zip(st, en)]


def main():
    sp = json.loads(os.environ['SPEC_JSON']); out = os.path.join(os.getcwd(), 'out'); os.makedirs(out, exist_ok=True)
    wav = os.path.join(out, 'voice.wav'); durs = build(sp['chunks'], wav, out)
    D = sum(durs) + 0.6
    title = sp.get('title', 'Thu giong doc').replace("'", "’").replace(':', '\\:')
    tmp = os.path.join(out, 'out.tmp.mp4')
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'color=c=0x0d2a6b:s=1080x1080:r=30:d={D:.2f}', '-i', wav,
                           '-vf', f"drawtext=text='{title}':fontcolor=0xffd400:fontsize=56:x=(w-tw)/2:y=(h-th)/2",
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', tmp])
    os.replace(tmp, os.path.join(out, 'out.mp4'))
    sil = silences(wav)
    plan = []; t = 0.0
    for c, d in zip(sp['chunks'], durs): t += d; plan.append(dict(text=c.get('text', '')[:40], end=round(t, 2), pause=c.get('pause_after', 0)))
    json.dump(dict(duration=round(D, 2), chunks=plan, silences=sil), open(os.path.join(out, 'qc.json'), 'w'), ensure_ascii=False)
    print('ok', round(D, 2), len(durs))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'parse':
        print(json.dumps(parse(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.95), ensure_ascii=False, indent=1))
    else:
        main()
