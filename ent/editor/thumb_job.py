"""Dung ANH BIA tu video da xong (moi kenh, 27/11). Chay trong ent.yml kind=thumb.
SPEC_JSON: {"channel","video_url","text"?,"hl"?,"badge"?,"sub"?,"cap"?,"band"?:[y0,y1],"t"?:giay}
- Lay cac khung ngay SAU moi lan chuyen canh (luc chu/phu de chua kip hien), chi giu dai giua (band) - bo chu khoa o tren va phu de o duoi.
- Cham diem do net + mau + do sang, chon khung tot nhat trong 10%-85% thoi luong.
- Thieu chu bia thi tu rut tu caption (dong 1, cat theo dau – : , .), badge tu "Phần n/m".
Ra out/thumb.jpg (< 2 MB, 1080x1920) + out/thumb.json (khung da chon)
+ out/out.mp4 = video goc co ANH BIA o khung dau tien (1 khung) de TikTok/Facebook tu lay lam bia (chu chot 27/11)."""
import json
import os
import re
import subprocess
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from thumb import make_thumb  # noqa: E402
import ngat  # noqa: E402

OUT = 'out'
BIA_SAN = {'cd', 'mnmb'}   # dang moi 28/11: khung dau video da la anh bia + hook
# dai hinh "sach" (khong chu) cua tung loai video, toa do tren khung 1080x1920
BAND = {'mnmb': (650, 1170), 'cd': (520, 1080), 'cck': (430, 1300), 'lt': (430, 1300), 'ksc': (430, 1300),
        'war': (440, 1150)}


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())


def cuts(p, d):
    """moc chuyen canh (giay)"""
    try:
        r = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-vf', "select='gt(scene,0.28)',showinfo", '-an', '-f', 'null', '-'],
                           capture_output=True, text=True, timeout=600)
        ts = [float(x) for x in re.findall(r'pts_time:([\d.]+)', r.stderr)]
    except Exception:
        ts = []
    if len(ts) < 4: ts = list(np.arange(d * 0.1, d * 0.85, 2.0))
    return ts


def frame(p, t):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '%.3f' % t, '-i', p, '-frames:v', '1', '-vf', 'scale=1080:1920',
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return Image.frombytes('RGB', (1080, 1920), raw)


def score(im):
    a = np.asarray(im.convert('L').resize((270, int(270 * im.height / im.width))), np.float32)
    lap = np.asarray(im.convert('L').resize((270, int(270 * im.height / im.width))).filter(ImageFilter.FIND_EDGES), np.float32)
    c = np.asarray(im.resize((90, int(90 * im.height / im.width))), np.float32)
    col = np.std(c[..., 0] - c[..., 1]) + np.std(0.5 * (c[..., 0] + c[..., 1]) - c[..., 2])
    br = a.mean()
    pen = 0.35 if br < 35 else (0.6 if br > 225 else 1.0)
    return (lap.std() + 0.6 * col) * pen


def tu_cap(cap, name=''):
    l1 = (cap or name or '').split('\n')[0]
    l1 = re.sub(r'#\S+', '', l1)
    l1 = re.sub(r'[\U0001F000-\U0001FFFF☀-➿]', '', l1).strip()
    m = re.search(r'[Pp]hần\s*(\d+\s*/\s*\d+)', l1)
    badge = ('PHẦN ' + m.group(1).replace(' ', '')) if m else ''
    head = re.split(r'\s[–-]\s|:|\||[.?!,]', l1)[0].strip()
    ws = head.split()
    if len(ws) > 6: head = ' '.join(ws[:5]) + '…'
    return head, badge


def main():
    sp = json.loads(os.environ.get('SPEC_JSON') or open(sys.argv[1]).read())
    ch = sp.get('channel', '')
    os.makedirs(OUT, exist_ok=True)
    vp = os.path.join(OUT, 'src.mp4')
    src = sp.get('video_url') or ''
    if src.startswith('http'):
        urllib.request.urlretrieve(src, vp)
    else:
        vp = src
    d = dur(vp)
    if ch in BIA_SAN and sp.get('t') is None:
        # 28/11 chu chot: kenh da co ANH BIA + HOOK ngay khung dau -> lay luon khung 0,05 s lam bia, khong ve them, khong chen bia vao video
        frame(vp, 0.05).save(os.path.join(OUT, 'thumb.jpg'), quality=90)
        json.dump({'t': 0.05, 'bia_san': True}, open(os.path.join(OUT, 'thumb.json'), 'w'))
        import shutil; shutil.copyfile(vp, os.path.join(OUT, 'out.mp4'))
        print('anh bia: lay khung dau 0,05 s (kenh co bia san)'); return
    y0, y1 = sp.get('band') or BAND.get(ch, (430, 1300))
    if sp.get('t') is not None:
        ts = [float(sp['t'])]
    else:
        off = 0.7 if ch == 'cd' else 0.12   # Chuyen Dem: tranh khung nhieu VHS ngay luc chuyen canh
        ts = [t + off for t in cuts(vp, d) if d * 0.10 <= t <= d * 0.85]
        if len(ts) > 24: ts = ts[::max(1, len(ts) // 24)]
    best = None
    for t in ts:
        try: im = frame(vp, min(t, d - 0.2)).crop((0, y0, 1080, y1))
        except Exception: continue
        sc = score(im)
        if best is None or sc > best[0]: best = (sc, t, im)
    if best is None: sys.exit('khong lay duoc khung hinh')
    text, hl, badge, sub = sp.get('text'), sp.get('hl', ''), sp.get('badge'), sp.get('sub', '')
    if not text or badge is None:
        h2, b2 = tu_cap(sp.get('cap', ''), sp.get('name', ''))
        text = text or h2; badge = b2 if badge is None else badge
    text = ngat.nfc(text)
    make_thumb(best[2], ch, text, hl, badge or '', sub, os.path.join(OUT, 'thumb.jpg'))
    json.dump({'t': round(best[1], 2), 'score': round(float(best[0]), 1), 'text': text, 'badge': badge, 'n': len(ts)},
              open(os.path.join(OUT, 'thumb.json'), 'w'), ensure_ascii=False)
    print('anh bia: khung', round(best[1], 2), 's /', len(ts), 'khung thu -', text)
    try:
        ghep_bia(vp, os.path.join(OUT, 'thumb.jpg'), os.path.join(OUT, 'out.mp4'))
    except Exception as e:
        print('khong ghep duoc bia vao video:', str(e)[:200])


def ghep_bia(vp, img, out):
    """Chen anh bia lam KHUNG DAU (1 khung) roi noi video goc; tieng day lui dung 1 khung."""
    r = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,width,height',
                                 '-of', 'csv=p=0', vp]).decode().strip().split(',')
    w, h = int(r[0]), int(r[1]); a, b = r[2].split('/'); fps = float(a) / float(b or 1)
    one = 1.0 / fps
    has_a = bool(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', vp]).strip())
    fc = ('[1:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,setsar=1,fps=%s,format=yuv420p,trim=end_frame=1[c];'
          '[0:v]setsar=1,format=yuv420p[v];[c][v]concat=n=2:v=1:a=0[vo]') % (w, h, w, h, r[2])
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', vp, '-loop', '1', '-t', '%.4f' % (one * 2), '-i', img, '-filter_complex']
    if has_a:
        fc += ';[0:a]adelay=%d:all=1[ao]' % round(one * 1000)
        cmd += [fc, '-map', '[vo]', '-map', '[ao]', '-c:a', 'aac', '-b:a', '192k']
    else:
        cmd += [fc, '-map', '[vo]']
    cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    print('video co bia khung dau:', out, round(one, 3), 's')


if __name__ == '__main__':
    main()
