# -*- coding: utf-8 -*-
"""'Nghe' video thay nguoi (chay tren GitHub Actions): do nhip giong + chep loi (faster-whisper) + so voi kich ban.
Vao: NGHE_JSON = {"job": "...", "items": [{"name": "...", "url": "https://...mp4", "script": "loi doc goc (tuy chon)"}]}
Ra: out/nghe.json
"""
import json, os, re, subprocess, sys, unicodedata, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nhip

OUT = 'out'; os.makedirs(OUT, exist_ok=True)
cfg = json.loads(os.environ['NGHE_JSON'])


def norm(s):
    s = unicodedata.normalize('NFC', s.lower())
    return re.sub(r'[^\w\s]', ' ', s).split()


def diff_words(ref, hyp):
    """chu co trong kich ban ma khong nghe thay (LCS don gian)."""
    a, b = norm(ref), norm(hyp)
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            dp[i][j] = dp[i + 1][j + 1] + 1 if a[i] == b[j] else max(dp[i + 1][j], dp[i][j + 1])
    i = j = 0; miss = []; cur = []
    while i < n and j < m:
        if a[i] == b[j]:
            if cur: miss.append(' '.join(cur)); cur = []
            i += 1; j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]: cur.append(a[i]); i += 1
        else: j += 1
    cur += a[i:]
    if cur: miss.append(' '.join(cur))
    return {'khop_pct': round(100 * dp[0][0] / max(n, 1), 1), 'thieu': miss[:40]}


model = None
res = {'job': cfg.get('job'), 'items': []}
for k, it in enumerate(cfg['items']):
    src = os.path.join(OUT, f'v{k}')
    req = urllib.request.Request(it['url'], headers={'User-Agent': 'Mozilla/5.0'})
    open(src, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
    wav = src + '.wav'
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', '16000', wav])
    r = nhip.analyse(wav, it.get('name', str(k)))
    try:
        if model is None:
            from faster_whisper import WhisperModel
            model = WhisperModel(os.environ.get('WHISPER', 'small'), device='cpu', compute_type='int8')
        audio = nhip.load(wav)   # mang float32 16 kHz -> khong qua PyAV
        segs, _ = model.transcribe(audio, language='vi', word_timestamps=True, vad_filter=False, beam_size=5)
        segs = list(segs)
        r['chep_loi'] = ' '.join(s.text.strip() for s in segs)
        words = [w for s in segs for w in (s.words or [])]
        r['tu'] = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for w in words]
        if it.get('script'): r['so_kich_ban'] = diff_words(it['script'], r['chep_loi'])
    except Exception as ex:
        r['chep_loi_loi'] = repr(ex)[:300]
    res['items'].append(r)
    print(json.dumps({x: y for x, y in r.items() if x not in ('cum', 'tu')}, ensure_ascii=False)[:3000], flush=True)
json.dump(res, open(os.path.join(OUT, 'nghe.json'), 'w'), ensure_ascii=False, indent=1)
