"""KHOA CUNG BO CUC (chu chot 20/11): vung an toan chung cho TikTok + Facebook Reels + YouTube Shorts, khung 1080x1920.

Do tren giao dien that (anh chu chup TikTok 20/11 + tai lieu Reels/Shorts):
- Tren: 0..250   thanh trang thai + tab "Dang follow / De xuat" + o TIM KIEM cua TikTok
- Duoi: 1460..1920 ten kenh, caption, nhac, thanh tien do (TikTok/Reels/Shorts)
- Phai: x>940 tu y~900 tro xuong: cot nut tim / binh luan / luu / chia se / avatar
- Trai: chua le 80px cho dep, tranh bo cong man hinh
=> Moi CHU va noi dung chinh phai nam trong SAFE = (80, 260, 940, 1460).

Cach khoa: import safezone o dau moi may dung. Moi lenh ImageDraw.text ve len khung 1080x1920 deu bi kiem tra hop bao;
chu nao ra ngoai SAFE -> dung may, KHONG xuat video. Chu trang tri o mep (REC, dong ho...) phai boc trong `with decor():`.
Anh ghep (paste) chu len khung dung check_box(x0, y0, x1, y1, ten).
"""
import contextlib
from PIL import ImageDraw

W, H = 1080, 1920
SAFE = (80, 260, 940, 1460)
CX = (SAFE[0] + SAFE[2]) // 2          # tam ngang vung an toan = 510
MAXW = SAFE[2] - SAFE[0] - 40           # be rong chu toi da khi canh giua theo CX = 820
MAXW_C540 = 2 * (SAFE[2] - 540) - 20    # be rong chu toi da khi canh giua theo W/2 = 780
_state = {'decor': 0, 'bad': []}


@contextlib.contextmanager
def decor():
    _state['decor'] += 1
    try: yield
    finally: _state['decor'] -= 1


def check_box(x0, y0, x1, y1, what='box'):
    if _state['decor']: return
    s = SAFE
    if x0 < s[0] - 2 or y0 < s[1] - 2 or x1 > s[2] + 2 or y1 > s[3] + 2:
        raise SystemExit(f'LOI BO CUC (safezone): "{what}" o ({int(x0)},{int(y0)})-({int(x1)},{int(y1)}) ra ngoai vung an toan {SAFE}')


_orig_text = ImageDraw.ImageDraw.text


def _text(self, xy, text, *a, **kw):
    img = getattr(self, '_image', None)
    if img is not None and tuple(img.size) == (W, H) and str(text).strip():
        try:
            bb = self.textbbox(xy, text, font=kw.get('font'), anchor=kw.get('anchor'), stroke_width=kw.get('stroke_width', 0) or 0)
            check_box(*bb, what=str(text)[:40])
        except SystemExit:
            raise
        except Exception:
            pass
    return _orig_text(self, xy, text, *a, **kw)


ImageDraw.ImageDraw.text = _text
