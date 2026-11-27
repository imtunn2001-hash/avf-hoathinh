"""Font chu video MNMB + Chuyen Dem (27/11, chu: "thay doi font chu cho dep").
key  = chu khoa to (Fira Sans Black)      sub = phu de (Fira Sans SemiBold)
bold = chu dam vua (Fira Sans ExtraBold)  tag = nhan kinh di hep cao (Barlow Condensed ExtraBold)
Thieu file thi lui ve series.fnt (Be Vietnam Pro/Inter) de khong bao gio hong video."""
import os
from PIL import ImageFont

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
FILES = {'key': 'FiraSans-Black.ttf', 'bold': 'FiraSans-ExtraBold.ttf', 'sub': 'FiraSans-SemiBold.ttf',
         'tag': 'BarlowCondensed-ExtraBold.ttf'}
_cache = {}


def font(kind, size):
    size = int(size); k = (kind, size)
    if k in _cache: return _cache[k]
    p = os.path.join(D, FILES[kind])
    if os.path.exists(p):
        f = ImageFont.truetype(p, size)
    else:
        from series import fnt
        f = fnt(kind in ('key', 'bold', 'tag'), size)
    _cache[k] = f
    return f
