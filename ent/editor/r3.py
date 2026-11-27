"""Ham dung chung cho 3 dang video moi (motiv / horror / warmap): tai file, doc am thanh, ghi khung hinh qua ffmpeg."""
import json, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series import fnt, get, wrap_bal, ease, cover  # noqa: E402,F401

W, H, FPS, SR = 1080, 1920, 30, 44100
ROOT = os.getcwd()
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(ROOT, 'tmp3'); os.makedirs(TMP, exist_ok=True)


def load_spec():
    sp = json.loads(os.environ.get('SPEC_JSON') or open(sys.argv[1]).read())
    # 22/11: spec.maxrate tuy chon (vd "3200k") cho video dai, giu file < 50MB (gioi han Supabase)
    if isinstance(sp, dict) and sp.get('maxrate'):
        os.environ['VID_MAXRATE'] = str(sp['maxrate'])
    return sp


def git_imgs(branch, paths):
    if not branch: return
    subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', branch], check=True)
    for p in paths:
        __import__('gitlay').lay(p)


def decode(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'])
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def trim_sil(a, th=0.01):
    idx = np.where(np.abs(a) > th)[0]
    if not len(idx): return a
    s = max(0, idx[0] - int(0.03 * SR)); e = min(len(a), idx[-1] + int(0.08 * SR))
    return a[s:e]


def voices(urls, gaps, lead=0.0):
    """tai cac doan giong, noi lai co khoang nghi; tra ve (mang am thanh, [(t0,t1) moi doan])"""
    parts, spans, t = [], [], lead
    if lead: parts.append(np.zeros(int(lead * SR), np.float32))
    for i, u in enumerate(urls):
        if isinstance(u, (list, tuple)):
            # 1 canh nhieu cau (W87): [(url, pause), ...] -> ghep, nghi dung pause giua cac cau
            sub = []
            for k, (uu, pz) in enumerate(u):
                p = os.path.join(TMP, 'v%02d_%02d.mp3' % (i, k)); get(uu, p)
                sub.append(trim_sil(decode(p)))
                if k < len(u) - 1: sub.append(np.zeros(int(float(pz or 0.45) * SR), np.float32))
            a = np.concatenate(sub)
        else:
            p = os.path.join(TMP, 'v%02d.mp3' % i); get(u, p)
            a = trim_sil(decode(p))
        d = len(a) / SR
        spans.append((t, t + d)); parts.append(a); t += d
        g = gaps[i] if i < len(gaps) else 0.5
        parts.append(np.zeros(int(g * SR), np.float32)); t += g
    return np.concatenate(parts), spans


def place(dst, src, t, vol=1.0):
    o = int(t * SR)
    if o >= len(dst): return
    n = min(len(src), len(dst) - o); dst[o:o + n] += src[:n] * vol


def env(n, a=0.005, r=0.2):
    e = np.ones(n, np.float32); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e


def tone(fq, d, vol=0.3, a=0.01, r=0.3, kind='sine'):
    t = np.arange(int(d * SR)) / SR
    x = np.sin(2 * np.pi * fq * t) if kind == 'sine' else np.sign(np.sin(2 * np.pi * fq * t)) * 0.5
    return (x * env(len(t), a, r) * vol).astype(np.float32)


def noise(d, vol=0.2, lp=None):
    x = np.random.randn(int(d * SR)).astype(np.float32)
    if lp:  # loc thong thap don gian
        k = max(1, int(SR / lp)); x = np.convolve(x, np.ones(k) / k, 'same')
    return x * vol


def boom(d=1.2, vol=0.8):
    t = np.arange(int(d * SR)) / SR
    f = 60 * np.exp(-t * 3) + 30
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    return (x * vol).astype(np.float32) + noise(d, 0.08, 400) * np.exp(-t * 6)


def write_audio(a, path):
    a = np.tanh(a * 1.2) * 0.8
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                          '-af', 'loudnorm=I=-19:TP=-2:LRA=11', '-ar', str(SR), '-ac', '2', path], stdin=subprocess.PIPE)
    p.communicate(pcm)


class Vid:
    """ghi khung hinh PIL truc tiep vao ffmpeg"""
    def __init__(self, path):
        mr = os.environ.get('VID_MAXRATE', '4500k')
        try:
            buf = '%dk' % (int(mr.rstrip('kK')) * 2)
        except ValueError:
            mr, buf = '4500k', '9000k'
        vf = os.environ.get('VID_VF', '')   # 23/11: grade mau theo kenh (fx.GRADE)
        self.p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                                   '-r', str(FPS), '-i', '-'] + (['-vf', vf] if vf else []) + ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '25', '-maxrate', mr, '-bufsize', buf,
                                   '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)

    def put(self, img):
        self.p.stdin.write(img.convert('RGB').tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()


def mux(vpath, apath, out):
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', vpath, '-i', apath, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                           '-shortest', '-movflags', '+faststart', out])
