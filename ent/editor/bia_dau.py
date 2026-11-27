"""Chen ANH BIA lam khung dau video ngay luc dung (chu chot 27/11: TikTok/Facebook tu lay khung dau lam bia).
Dung cho video KHONG di qua W102 (W102 chi lam cho mnmb/cd/cck/war/lt sau khi len YouTube):
- bantin (ban tin vang 5 page): chu bia lay spec.thumb {text,hl,sub} neu co, khong thi rut tu headline (cum co con so).
- ksc (Ky Su Chien, dung.yml): chu bia = hook_text, nhan = badge.
Cach goi: python3 bia_dau.py <kind> [video=out/out.mp4]  (SPEC_JSON trong env).
Video goc doi ten thanh out/goc.mp4; loi thi giu nguyen video goc (khong bao gio lam hong ban dung)."""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thumb  # noqa: E402
import thumb_job as TJ  # noqa: E402


def cum_so(headline):
    """Lay cum ngan co con so trong headline (uu tien cum noi lo/lai/tang/giam), toi da 7 chu."""
    h = re.sub(r'\s+', ' ', str(headline).replace('\n', ' ')).strip().rstrip('…. ')
    parts = [p.strip() for p in re.split(r'[,.:;–|]\s|\s-\s', h) if p.strip()]
    parts = [re.sub(r'^(SÁNG|TRƯA|CHIỀU|TỐI|ĐÊM|HÔM)\s+(NAY|QUA)\s+', '', p, flags=re.I) for p in parts]
    KW = re.compile(r'MẤT|LỖ|HỤT|LỜI|LÃI|TĂNG|GIẢM|RƠI|BẬT|THỦNG|VỌT', re.I)
    co_so = [p for p in parts if re.search(r'\d', p)]
    if co_so:
        t = sorted(co_so, key=lambda p: (not KW.search(p), len(p.split())))[0]
    else:
        t = parts[0] if parts else h
    ws = t.split()[:7]
    while len(ws) > 2 and ws[-1].upper() in ('RỒI', 'VÀ', 'NHƯNG', 'MÀ', 'THÌ', 'CỦA', 'LÀ', 'CHO', 'ĐỂ', 'VỚI'):
        ws.pop()
    return ' '.join(ws)


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else ''
    vp = sys.argv[2] if len(sys.argv) > 2 else 'out/out.mp4'
    sp = json.loads(os.environ.get('SPEC_JSON') or '{}')
    th = sp.get('thumb') or {}
    if kind == 'bantin':
        P = sp.get('page') or {}
        acc = tuple(P.get('accent') or (230, 57, 70))
        thumb.STYLE['_page'] = (str(P.get('name') or 'BẢN TIN VÀNG').upper()[:24], acc, (255, 255, 255), tuple(P.get('accent2') or (255, 212, 0)), 'key')
        ch = '_page'
        text = th.get('text') or cum_so(sp.get('headline', ''))
        hl, sub = th.get('hl', ''), th.get('sub', '')
        badge = th.get('badge') if th.get('badge') is not None else str(sp.get('date', ''))[:5]
        band = (300, 1300)
    elif kind == 'ksc':
        ch = 'ksc'
        text = th.get('text') or str(sp.get('hook_text') or sp.get('series') or '')
        hl, sub = th.get('hl', ''), th.get('sub', '')
        badge = th.get('badge') if th.get('badge') is not None else str(sp.get('badge') or '')
        band = TJ.BAND.get('ksc', (430, 1300))
    else:
        print('bia_dau: bo qua kind', kind); return
    if not text or not os.path.exists(vp):
        print('bia_dau: thieu chu bia hoac video, bo qua'); return
    d = TJ.dur(vp)
    ts = [t + 0.12 for t in TJ.cuts(vp, d) if d * 0.10 <= t <= d * 0.85]
    if len(ts) > 24: ts = ts[::max(1, len(ts) // 24)]
    best = None
    for t in ts:
        try: im = TJ.frame(vp, min(t, d - 0.2)).crop((0, band[0], 1080, band[1]))
        except Exception: continue
        sc = TJ.score(im)
        if best is None or sc > best[0]: best = (sc, t, im)
    if best is None:
        print('bia_dau: khong lay duoc khung, bo qua'); return
    od = os.path.dirname(vp) or '.'
    jpg = os.path.join(od, 'bia.jpg')
    thumb.make_thumb(best[2], ch, TJ.ngat.nfc(text), hl, badge or '', sub, jpg)
    goc = os.path.join(od, 'goc.mp4'); tmp = os.path.join(od, 'co_bia.mp4')
    shutil.copyfile(vp, goc)
    TJ.ghep_bia(goc, jpg, tmp)
    if os.path.getsize(tmp) > 10000:
        shutil.move(tmp, vp)
        print('bia_dau: da chen bia khung dau -', text)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('bia_dau: loi, giu video goc:', str(e)[:200])
