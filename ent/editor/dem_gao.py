"""Bo canh 'Chuyen cay gao' (Truyen ky man luc, Nguyen Du, the ky 16) cho dem.py (spec.pack = 'gao').
Nhan vat khong mat: Trinh Trung Ngo (ao dai the, khan dong), Nhi Khanh (toc dai, ao nau tim),
ban buon / dan lang (ao nau, khan), dao si (ao choang xam, bui toc, phat tran), linh dau trau (sung).
Bong ma ve SAU anh sang (post) cho sang mo, trong suot."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter
from dem import W, H, INK, HEAD, tex, lightmap, steam  # noqa: F401

LOOK = {
    'tn': dict(robe=(36, 44, 58), long=True, acc='khandong', acc_c=(20, 24, 34)),
    'nk': dict(robe=(92, 54, 70), long=True, acc='tocdai', acc_c=(10, 9, 10)),
    'dl': dict(robe=(86, 66, 50), long=False, pant=(34, 32, 32), acc='khan', acc_c=(66, 56, 48)),
    'dl2': dict(robe=(70, 74, 62), long=False, pant=(34, 32, 32), acc='buito', acc_c=(12, 10, 10)),
    'ds': dict(robe=(96, 104, 112), long=True, acc='buito', acc_c=(12, 10, 10), beard=True),
    'tuong': dict(robe=(150, 112, 80), long=True, acc='tocdai', acc_c=(120, 88, 62), skin=(150, 112, 80), head=(132, 98, 70)),
    'thinu': dict(robe=(150, 112, 80), long=True, acc='tocdai', acc_c=(14, 12, 12)),   # cung mau tuong dat (cai bay cho cu lat)
    'gia': dict(robe=(82, 70, 58), long=True, acc='khan', acc_c=(200, 196, 186), beard=True),
    'trau': dict(robe=(60, 34, 28), long=False, pant=(30, 22, 20), acc='sung', acc_c=(200, 190, 170)),
}
SK = (128, 96, 76)


def person2(im, x, fy, h, who, flip=1, ph=0.0, pose='down', ghost=0.0, lie=False, rot=0, dan=False, cui=False):
    """ve len lop rieng roi dan vao im (ho tro nam ngang, bong ma trong suot)."""
    L = LOOK[who]; s = h / 100.0; S = int(h * 1.5); SKc = L.get('skin', SK); HD = L.get('head', HEAD)
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy = S / 2, S * .82          # chan nhan vat tren lop
    bob = abs(math.sin(ph * math.pi)) * 1.2 * s if ph else 0
    sh = cy - 79 * s - bob; hy = sh - 11 * s; r = 8.5 * s
    robe = L['robe']
    # toc dai sau lung
    if L['acc'] == 'tocdai':
        d.rounded_rectangle([cx - flip * 4 * s - 7 * s, hy - 2 * s, cx - flip * 4 * s + 7 * s, sh + 34 * s], 6 * s, fill=L['acc_c'])
    # chan
    if not L['long']:
        for k, sg in ((0, -1), (1, 1)):
            off = math.sin((ph + k * .5) * math.pi * 2) * 7 * s if ph else 0
            lx = cx + sg * 4.5 * s
            d.line([(lx, cy - 46 * s - bob), (lx + off, cy - 2 * s)], fill=L['pant'], width=int(6.5 * s))
            d.ellipse([lx + off - 4 * s, cy - 4 * s, lx + off + 5 * s, cy + 1 * s], fill=INK)
        bot = cy - 40 * s - bob; bw = 13 * s
    else:
        bot = cy - 4 * s; bw = 18 * s
        for k, sg in ((0, -1), (1, 1)):
            off = math.sin((ph + k * .5) * math.pi * 2) * 6 * s if ph else 0
            d.ellipse([cx + sg * 5 * s + off - 5 * s, cy - 4 * s, cx + sg * 5 * s + off + 5 * s, cy + 1 * s], fill=INK)
    d.polygon([(cx - 13 * s, sh), (cx + 13 * s, sh), (cx + bw, bot), (cx - bw, bot)], fill=robe, outline=INK, width=2)
    d.line([(cx + flip * 2 * s, sh + 2 * s), (cx + flip * 5 * s, bot - 2 * s)], fill=tuple(max(0, c - 18) for c in robe), width=max(1, int(1.4 * s)))
    # tay
    for sg in (-1, 1):
        ax = cx + sg * 12 * s
        if pose == 'raise':
            ex, ey = ax + sg * 10 * s, sh - 22 * s
        elif pose == 'hold':
            ex, ey = cx + flip * 10 * s, sh + 24 * s
        elif pose == 'point' and sg == flip:
            ex, ey = ax + flip * 30 * s, sh + 6 * s
        elif pose == 'reach' and sg == flip:
            ex, ey = ax + flip * 26 * s, sh + 14 * s
        else:
            sw_ = math.sin((ph + (sg > 0) * .5) * math.pi * 2) * 5 * s if ph else 0
            ex, ey = ax + sg * 3 * s + sw_, sh + 34 * s
        d.line([(ax, sh + 3 * s), (ex, ey)], fill=robe, width=int(5.5 * s))
        d.ellipse([ex - 3 * s, ey - 3 * s, ex + 3 * s, ey + 3 * s], fill=SKc)
        if who == 'ds' and sg == flip:   # phat tran
            d.line([(ex, ey), (ex + flip * 3 * s, ey - 10 * s)], fill=(150, 120, 80), width=max(2, int(1.4 * s)))
            for j in range(6): d.line([(ex + flip * 3 * s, ey - 10 * s), (ex + flip * (j - 1) * 1.2 * s, ey + 14 * s)], fill=(214, 210, 198), width=max(1, int(.8 * s)))
    if dan:   # dan ho cam om truoc nguc
        d.ellipse([cx - 9 * s, sh + 16 * s, cx + 9 * s, sh + 32 * s], fill=(120, 78, 44), outline=INK, width=2)
        d.line([(cx, sh + 18 * s), (cx + flip * 16 * s, sh - 4 * s)], fill=(90, 60, 34), width=max(2, int(2 * s)))
    # dau
    if cui: hy += 4 * s; cx_h = cx + flip * 4 * s
    d.line([(cx, sh), (cx, hy + r * .6)], fill=HD, width=int(4 * s))
    if L['acc'] == 'sung':   # dau trau
        d.ellipse([cx - r * 1.2, hy - r * 1.1, cx + r * 1.2, hy + r * 1.1], fill=(52, 34, 28))
        d.ellipse([cx + flip * r * .4 - r * .7, hy, cx + flip * r * .4 + r * .9, hy + r * 1.2], fill=(70, 48, 40))
        for sg in (-1, 1):
            d.polygon([(cx + sg * r * .6, hy - r * .8), (cx + sg * r * 2.4, hy - r * 1.6), (cx + sg * r * 2.0, hy - r * 2.4), (cx + sg * r * 1.2, hy - r * .9)], fill=L['acc_c'], outline=INK)
    else:
        d.ellipse([cx - r, hy - r, cx + r, hy + r], fill=HD)
        c = L['acc_c']
        if L['acc'] == 'khandong':
            d.ellipse([cx - r * 1.15, hy - r * 1.05, cx + r * 1.15, hy - r * .1], fill=c, outline=(50, 56, 70), width=max(1, int(s)))
        elif L['acc'] == 'tocdai':
            d.chord([cx - r * 1.08, hy - r * 1.1, cx + r * 1.08, hy + r * .6], 180, 360, fill=c)
        elif L['acc'] == 'buito':
            d.chord([cx - r, hy - r * 1.05, cx + r, hy + r * .2], 180, 360, fill=c); d.ellipse([cx - r * .45, hy - r * 1.7, cx + r * .45, hy - r * .8], fill=c)
        elif L['acc'] == 'khan':
            d.chord([cx - r * 1.12, hy - r * 1.15, cx + r * 1.12, hy + r * .9], 180, 360, fill=c)
        if L.get('beard'):
            d.polygon([(cx + flip * r * .2, hy + r * .5), (cx + flip * r * .9, hy + r * .4), (cx + flip * r * .5, hy + r * 2.0)], fill=(220, 218, 210))
    if lie: lay = lay.rotate(90 * flip, resample=Image.BICUBIC, center=(cx, cy - 45 * s))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, center=(cx, cy))
    if ghost:
        a = lay.getchannel('A'); g = Image.new('RGBA', lay.size, (214, 232, 244, 0)); g.putalpha(a.point(lambda v: int(v * ghost)))
        glow = g.filter(ImageFilter.GaussianBlur(10 * s / 4))
        im.paste(glow, (int(x - cx), int(fy - cy)), glow); lay = g
    im.paste(lay, (int(x - cx), int(fy - cy)), lay)


def moon(d, x, y, r=60):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 232, 214))


def river(d, y0, y1, col=(24, 30, 40)):
    d.rectangle([0, y0, W, y1], fill=col)


def ripples(d, y0, y1, t, col=(70, 84, 100), n=26, seed=3):
    r = random.Random(seed)
    for _ in range(n):
        x, y, L_ = r.uniform(0, W), r.uniform(y0, y1), r.uniform(40, 140)
        dx = math.sin(t * 1.3 + x * .01) * 12
        d.line([(x + dx, y), (x + dx + L_, y)], fill=col, width=2)


def boat(d, x, y, w=420, lantern=True):
    d.polygon([(x - w / 2, y), (x + w / 2, y), (x + w / 2 - 50, y + 60), (x - w / 2 + 50, y + 60)], fill=(58, 40, 28), outline=INK, width=2)
    d.line([(x - w / 2 - 20, y - 8), (x + w / 2 + 20, y - 8)], fill=(80, 58, 40), width=10)
    if lantern:
        d.line([(x + w / 2 - 30, y - 8), (x + w / 2 - 30, y - 230)], fill=(40, 30, 24), width=6)
        d.line([(x + w / 2 - 30, y - 230), (x + w / 2 + 20, y - 230)], fill=(40, 30, 24), width=5)
        d.ellipse([x + w / 2 - 2, y - 226, x + w / 2 + 40, y - 172], fill=(230, 130, 64), outline=INK, width=2)


def hut(d, x, y, w=560, h=420, ruined=True, door=True):
    d.polygon([(x - w / 2 - 40, y - h + 160), (x, y - h), (x + w / 2 + 40, y - h + 160)], fill=(70, 60, 44), outline=INK, width=2)
    d.rectangle([x - w / 2, y - h + 160, x + w / 2, y], fill=(64, 52, 40), outline=INK, width=2)
    if ruined:
        d.polygon([(x + 60, y - h + 40), (x + 140, y - h + 90), (x + 70, y - h + 120)], fill=(30, 26, 22))
        for j in range(6): d.line([(x - w / 2 + 30 + j * 90, y - h + 170), (x - w / 2 + 50 + j * 90, y - 10)], fill=(52, 42, 32), width=3)
    if door: d.rectangle([x - 70, y - 220, x + 70, y], fill=(14, 12, 12))


def coffin(d, x, y, w=520):
    d.polygon([(x - w / 2, y - 90), (x + w / 2, y - 110), (x + w / 2 + 30, y - 40), (x + w / 2, y), (x - w / 2, y), (x - w / 2 - 20, y - 50)], fill=(78, 36, 30), outline=INK, width=3)
    d.line([(x - w / 2, y - 60), (x + w / 2 + 10, y - 72)], fill=(54, 24, 20), width=4)


def kapok(im, x, y, t=0, s=1.0, flowers=True, ang=0.0, seed=7):
    """cay gao gia: goc banh re, than thon dan, canh chia tang chech len, cong; hoa do tung chum o nua ngoai canh."""
    S_ = int(1500 * s); lay = Image.new('RGBA', (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bx, by = S_ / 2, S_ * .93; r = random.Random(seed); bark = (64, 56, 50)
    d.polygon([(bx - 95 * s, by), (bx - 34 * s, by - 760 * s), (bx + 30 * s, by - 760 * s), (bx + 100 * s, by)], fill=bark, outline=INK)
    for sg in (-1, 1):
        d.polygon([(bx + sg * 80 * s, by), (bx + sg * 210 * s, by + 6), (bx + sg * 50 * s, by - 170 * s)], fill=(58, 50, 44), outline=INK)
    tips = []
    for tier in range(5):
        yy = by - (300 + tier * 105) * s
        for sg in (-1, 1):
            L_ = (330 - tier * 45 + r.uniform(-40, 40)) * s; up = r.uniform(.25, .55)
            sway = math.sin(t * .8 + tier + sg) * 6 * s
            pts = [(bx + sg * L_ * k, yy - L_ * up * k - 40 * s * k * k + sway * k) for k in (0, .35, .7, 1.0)]
            for k in range(3): d.line([pts[k], pts[k + 1]], fill=bark, width=max(3, int((20 - tier * 2.5 - k * 4) * s)))
            tw = pts[2]; d.line([tw, (tw[0] + sg * 50 * s, tw[1] - 70 * s)], fill=bark, width=max(2, int(6 * s)))
            tips += [pts[2], pts[3], (tw[0] + sg * 50 * s, tw[1] - 70 * s)]
    d.line([(bx, by - 760 * s), (bx + 20 * s, by - 860 * s)], fill=bark, width=int(14 * s)); tips.append((bx + 20 * s, by - 860 * s))
    if flowers:
        for (fx, fy) in tips:
            for _ in range(5):
                ox, oy = r.uniform(-30, 30) * s, r.uniform(-24, 18) * s; rr = r.uniform(9, 15) * s
                d.ellipse([fx + ox - rr, fy + oy - rr, fx + ox + rr, fy + oy + rr], fill=r.choice([(176, 36, 28), (200, 52, 34), (150, 28, 24)]))
    if ang: lay = lay.rotate(ang, resample=Image.BICUBIC, center=(bx, by))
    im.paste(lay, (int(x - bx), int(y - by)), lay)
    if flowers:   # hoa rung duoi goc
        d2 = ImageDraw.Draw(im); r2 = random.Random(seed + 1)
        for _ in range(14):
            fx = x + r2.uniform(-260, 260); fy = y + r2.uniform(-10, 30); d2.ellipse([fx - 8, fy - 5, fx + 8, fy + 5], fill=(150, 30, 24))


def pagoda(d, x, y, w=420):
    d.rectangle([x - w / 2 + 40, y - 220, x + w / 2 - 40, y], fill=(80, 66, 54), outline=INK, width=2)
    d.polygon([(x - w / 2 - 30, y - 220), (x + w / 2 + 30, y - 220), (x + w / 2 - 20, y - 300), (x - w / 2 + 20, y - 300)], fill=(56, 36, 30), outline=INK, width=2)
    for sg in (-1, 1): d.polygon([(x + sg * (w / 2 + 30), y - 220), (x + sg * (w / 2 + 60), y - 260), (x + sg * (w / 2 + 10), y - 240)], fill=(56, 36, 30))
    d.rectangle([x - 40, y - 140, x + 40, y], fill=(30, 22, 18))


class Set:
    def __init__(s, seed, base, bg, lights, amb, dyn=None, post=None):
        s.bg = tex(seed, base); bg(ImageDraw.Draw(s.bg), s.bg)
        s.L = lightmap(lights, amb); s.dyn = dyn; s.pst = post
        if post: s.post = lambda im, t, st: s.pst(im, t, st)

    def draw(s, im, t, st):
        if s.dyn: s.dyn(im, t, st)


WARM = (1.0, .78, .52); MOON = (.7, .8, 1.0); COLDG = (.62, .9, .74)
GROUND = 1250


def _cho(d, im):   # cho Nam Xang ben song dem
    d.rectangle([0, 0, W, 760], fill=(18, 20, 30)); moon(d, 820, 420, 54)
    for j in range(5):   # mai lieu cho
        x = 40 + j * 230; d.polygon([(x, 900), (x + 100, 820), (x + 200, 900)], fill=(44, 36, 30)); d.rectangle([x + 20, 900, x + 180, 1000], fill=(52, 42, 34))
    river(d, 1000, H)


def _cho_dyn(im, t, st):
    d = ImageDraw.Draw(im); ripples(d, 1020, 1500, t); boat(d, 560, 1180)
    if st.get('tn'): person2(im, 470, 1180, 480, 'tn', 1)


def _bo_song(d, im):
    d.rectangle([0, 0, W, 900], fill=(16, 20, 30)); moon(d, 240, 430, 60)
    river(d, 900, 1160); d.rectangle([0, 1160, W, H], fill=(30, 28, 26))
    for j in range(8): d.line([(60 + j * 130, 1160), (40 + j * 130, 1080)], fill=(40, 50, 40), width=4)   # co lau


def _gap_dyn(im, t, st):
    d = ImageDraw.Draw(im); ripples(d, 910, 1150, t, n=16)
    q = min(1.0, t / 2.5)
    person2(im, 380, GROUND, 520, 'tn', 1)
    person2(im, 760 - 60 * q, GROUND, 470, 'nk', -1, ph=t * 1.2 if q < 1 else 0)


def _thuyen_dem(d, im):
    d.rectangle([0, 0, W, 1000], fill=(14, 16, 24)); moon(d, 860, 380, 46); river(d, 1000, H)


def _thuyen_dyn(im, t, st):
    d = ImageDraw.Draw(im); ripples(d, 1010, 1500, t)
    boat(d, 540, 1170, 620)
    if st.get('hai'):
        person2(im, 430, 1170, 420, 'tn', 1); person2(im, 650, 1170, 390, 'nk', -1)
        if st.get('tho'):
            d.rectangle([500, 1010, 590, 1100], fill=(226, 214, 180), outline=INK, width=2)
            for j in range(4): d.line([(512 + j * 20, 1022), (512 + j * 20, 1088)], fill=(60, 50, 40), width=3)
    elif st.get('mot'):
        person2(im, 470, 1170, 420, 'tn', 1)


def _ban_buon(d, im):
    d.rectangle([0, 0, W, 900], fill=(40, 36, 32)); d.rectangle([0, 900, W, H], fill=(52, 44, 36))
    d.rectangle([700, 640, 900, 880], fill=(60, 50, 40), outline=INK, width=2)


def _ban_dyn(im, t, st):
    person2(im, 330, GROUND, 520, 'dl', 1, pose='point'); person2(im, 560, GROUND, 520, 'dl2', 1)
    person2(im, 800, GROUND, 540, 'tn', -1)
    steam(ImageDraw.Draw(im), 800, 560, t, n=2, h=0)   # khong ve (giu cho)


def _leu_ngoai(d, im):
    d.rectangle([0, 0, W, 1000], fill=(14, 16, 22)); moon(d, 200, 360, 40)
    d.rectangle([0, 1000, W, H], fill=(26, 26, 24))
    hut(d, 640, 1150)
    for j in range(7): d.line([(40 + j * 60, 1150), (20 + j * 60, 1040)], fill=(36, 40, 34), width=4)


def _leu_dyn(im, t, st):
    q = min(1.0, t / max(1.0, st['dur'] * .8))
    x0 = 120 + 300 * q
    person2(im, x0 + 140, 1260, 440, 'nk', 1, ph=t * 1.2 if q < 1 else 0)
    person2(im, x0, 1270, 470, 'tn', 1, ph=t * 1.2 + .3 if q < 1 else 0)


def _quan_tai(d, im):
    d.rectangle([0, 0, W, H], fill=(30, 30, 30)); d.rectangle([0, 1100, W, H], fill=(22, 22, 22))
    for j in range(9): d.line([(j * 130, 0), (j * 130 + 20, 1100)], fill=(38, 36, 34), width=6)   # vach lieu
    coffin(d, 560, 1110)


def _qt_dyn(im, t, st):
    if st.get('tn'): person2(im, 230, 1290, 540, 'tn', 1, pose='down')
    if st.get('nk'): person2(im, 330, 1270, 500, 'nk', 1, pose='reach')
    if st.get('chet'):   # nam canh quan tai (khong mau me)
        person2(im, 520, 1440, 460, 'tn', 1, lie=True)


def _qt_post(im, t, st):
    if st.get('hon'):
        a = .35 + .15 * math.sin(t * 2)
        person2(im, 560, 1020, 420, 'nk', -1, ghost=a)


def _duong_chay(d, im):
    d.rectangle([0, 0, W, 1000], fill=(12, 14, 20)); d.rectangle([0, 1000, W, H], fill=(24, 24, 22))
    hut(d, 880, 1050, w=360, h=300); d.polygon([(0, H), (W, H), (760, 1050), (640, 1050)], fill=(32, 30, 28))


def _chay_dyn(im, t, st):
    q = min(1.0, t / max(1.0, st['dur']))
    person2(im, 700 - 520 * q, 1150 + 300 * q, 360 + 260 * q, 'tn', -1, ph=t * 2.6)


def _giuong(d, im):
    d.rectangle([0, 0, W, H], fill=(36, 32, 28)); d.rectangle([0, 1150, W, H], fill=(28, 24, 22))
    d.rectangle([640, 560, 900, 900], fill=(16, 18, 28), outline=(60, 50, 40), width=10)   # cua so dem
    for j in range(3): d.line([(640 + j * 87, 560), (640 + j * 87, 900)], fill=(60, 50, 40), width=6)
    d.rectangle([120, 1040, 760, 1110], fill=(84, 58, 38), outline=INK, width=2)   # giuong
    d.rectangle([140, 1110, 170, 1250], fill=(60, 40, 26)); d.rectangle([710, 1110, 740, 1250], fill=(60, 40, 26))
    d.rectangle([860, 1000, 900, 1150], fill=(70, 50, 34)); d.ellipse([850, 960, 910, 1010], fill=(250, 200, 120))   # den dau


def _giuong_dyn(im, t, st):
    if st.get('troi'):
        person2(im, 420, 1110, 420, 'tn', 1, pose='hold')
        d = ImageDraw.Draw(im)
        for j in range(4): d.line([(360, 860 + j * 40), (480, 875 + j * 40)], fill=(170, 150, 110), width=6)
        person2(im, 150, 1260, 500, 'dl', 1); person2(im, 760, 1260, 500, 'dl2', -1)
    else:
        person2(im, 440, 1250, 520, 'tn', -1, lie=True)


def _giuong_post(im, t, st):
    if st.get('hon'):
        person2(im, 770, 940, 300, 'nk', -1, ghost=.35 + .12 * math.sin(t * 1.7))


def _lang_dem(d, im):
    d.rectangle([0, 0, W, 1000], fill=(12, 16, 22)); d.rectangle([0, 1000, W, H], fill=(22, 26, 24))
    for j in range(4): hut(d, 120 + j * 300, 1000, w=220, h=220, ruined=False, door=False)
    for j in range(5): d.rectangle([0, 1040 + j * 40, W, 1046 + j * 40], fill=(30, 36, 34))   # suong


def _lang_post(im, t, st):
    q = (t * .08) % 1
    person2(im, 300 + 400 * q, 1300, 440, 'tn', 1, ph=t * .8, ghost=.38)
    person2(im, 420 + 400 * q, 1300, 400, 'nk', 1, ph=t * .8 + .5, ghost=.38)


def _dao_mo(d, im):
    d.rectangle([0, 0, W, 900], fill=(14, 16, 22)); d.rectangle([0, 900, W, H], fill=(34, 30, 26))
    for x in (330, 720): d.chord([x - 170, 1020, x + 170, 1240], 180, 360, fill=(60, 50, 40), outline=INK, width=2)


def _dao_dyn(im, t, st):
    d = ImageDraw.Draw(im)
    for j, (x, who) in enumerate([(200, 'dl'), (520, 'dl2'), (860, 'dl')]):
        dig = math.sin(t * 3 + j) * 10
        person2(im, x, 1320, 470, who, 1 if j < 2 else -1, pose='reach')
        d.line([(x + 30, 1060 + dig), (x + 90, 1260 + dig)], fill=(110, 90, 60), width=8)
    d.ellipse([600, 700, 640, 760], fill=(255, 190, 90)); d.line([(620, 760), (620, 900)], fill=(60, 40, 26), width=8)   # duoc


def _nem_song(d, im):
    d.rectangle([0, 0, W, 860], fill=(16, 20, 28)); moon(d, 820, 360, 46)
    river(d, 860, H, (20, 28, 38)); d.polygon([(0, 1000), (420, 1000), (360, 1320), (0, 1320)], fill=(32, 30, 26))


def _nem_dyn(im, t, st):
    d = ImageDraw.Draw(im); ripples(d, 880, 1500, t, n=30)
    person2(im, 300, 1280, 460, 'dl', 1, pose='point'); person2(im, 170, 1300, 440, 'dl2', 1)
    q = min(1.0, t / 1.4); bx, by = 330 + 360 * q, 1060 - 260 * math.sin(q * math.pi) + 120 * q
    if q < 1: d.ellipse([bx - 30, by - 20, bx + 30, by + 20], fill=(120, 110, 90), outline=INK, width=2)
    else:
        for k in range(3):
            rr = 30 + ((t - 1.4) * 80 + k * 40) % 160; d.ellipse([690 - rr, 1180 - rr * .25, 690 + rr, 1180 + rr * .25], outline=(110, 130, 150), width=3)


def _gao_chua(d, im):
    d.rectangle([0, 0, W, 1000], fill=(14, 16, 24)); moon(d, 900, 720, 40)
    river(d, 1180, H, (20, 26, 34)); d.rectangle([0, 1000, W, 1180], fill=(30, 28, 26))
    pagoda(d, 820, 1180, 360)


def _gao_dyn(im, t, st):
    kapok(im, 380, 1200, t, 1.0)


def _gao_post(im, t, st):
    if st.get('hon'):
        person2(im, 300, 1220, 330, 'tn', 1, ph=t * .6, ghost=.4); person2(im, 450, 1220, 300, 'nk', -1, ph=t * .6 + .5, ghost=.4)
    if st.get('dao_si'):
        pass


def _ds_dyn(im, t, st):
    _gao_dyn(im, t, st)
    person2(im, 840, 1330, 560, 'ds', -1, pose='point' if st.get('chi') else 'down')


def _dan_te(d, im):
    d.rectangle([0, 0, W, 960], fill=(16, 16, 22)); d.rectangle([0, 960, W, H], fill=(32, 28, 24))
    d.rectangle([300, 1050, 780, 1090], fill=(120, 30, 26), outline=INK, width=2); d.rectangle([330, 1090, 750, 1220], fill=(96, 24, 22))
    d.rectangle([500, 990, 580, 1050], fill=(150, 120, 60), outline=INK, width=2)   # bat huong
    for x in (360, 720): d.rectangle([x - 10, 960, x + 10, 1050], fill=(236, 230, 210)); d.ellipse([x - 10, 935, x + 10, 965], fill=(255, 210, 120))


def _te_dyn(im, t, st):
    d = ImageDraw.Draw(im); steam(d, 540, 990, t, n=3, h=300, col=(170, 164, 150), w=2)
    person2(im, 540, 1330, 560, 'ds', 1, pose='raise' if int(t * 1.2) % 2 else 'down')
    for j, x in enumerate((120, 260, 820, 960)): person2(im, x, 1380, 430, 'dl' if j % 2 else 'dl2', 1 if x < 540 else -1)


def _bao(d, im):
    d.rectangle([0, 0, W, 1000], fill=(8, 10, 14)); river(d, 1180, H, (14, 18, 24)); d.rectangle([0, 1000, W, 1180], fill=(22, 20, 18))
    pagoda(d, 820, 1180, 360)


def _bao_dyn(im, t, st):
    tl = min(1.0, t / 2.5)
    kapok(im, 380 + tl * 60, 1200 + tl * 40, t * 4, 1.0, flowers=t < 1.2, ang=-tl * 62)
    r = random.Random(int(t * 10))
    d = ImageDraw.Draw(im)
    for _ in range(40):
        x, y = r.uniform(0, W), r.uniform(200, 1200); d.line([(x, y), (x + 30, y + 10)], fill=(60, 50, 44), width=4)


def _bao_post(im, t, st):
    if int(t * 4) % 7 == 0:   # chop
        d = ImageDraw.Draw(im); x = 300 + (int(t) * 97) % 500
        d.line([(x, 0), (x + 40, 240), (x - 20, 420), (x + 30, 640)], fill=(230, 236, 255), width=6)


def _trau(d, im):
    d.rectangle([0, 0, W, 1000], fill=(10, 8, 10)); d.rectangle([0, 1000, W, H], fill=(24, 18, 16))


def _trau_dyn(im, t, st):
    q = (t * .12) % 1
    for row in range(2):
        for j in range(6):
            x = -200 + j * 230 + 300 * q + row * 110; fy = 1150 + row * 170
            person2(im, x, fy, 360 + row * 80, 'trau', 1, ph=t * 1.5 + j * .3)


def _trau_post(im, t, st):
    q = (t * .12) % 1
    person2(im, 560 + 300 * q, 1240, 380, 'tn', 1, ghost=.4); person2(im, 660 + 300 * q, 1240, 350, 'nk', 1, ghost=.4)


def _tu_choi(d, im):
    d.rectangle([0, 0, W, 960], fill=(64, 70, 84)); d.rectangle([0, 960, W, H], fill=(48, 46, 44))
    d.polygon([(0, H), (W, H), (620, 960), (520, 960)], fill=(58, 56, 52))


def _tc_dyn(im, t, st):
    q = min(1.0, t / max(1.0, st['dur']))
    person2(im, 570, 1120 - 140 * q, 400 * (1 - .4 * q), 'ds', 1, ph=t * 1.1)
    d = ImageDraw.Draw(im)
    for j, x in enumerate((160, 360, 760, 940)):
        person2(im, x, 1400, 460, 'dl' if j % 2 else 'dl2', 1 if x < 540 else -1, pose='hold')
        d.rectangle([x - 50, 1080, x + 50, 1100], fill=(150, 40, 30))


def _binh_yen(d, im):
    d.rectangle([0, 0, W, 1000], fill=(96, 104, 120)); river(d, 1180, H, (70, 86, 100)); d.rectangle([0, 1000, W, 1180], fill=(66, 62, 56))
    pagoda(d, 820, 1180, 360)
    d.polygon([(310, 1200), (330, 1120), (430, 1120), (450, 1200)], fill=(70, 60, 54), outline=INK)   # goc cay con lai


def _by_dyn(im, t, st):
    ripples(ImageDraw.Draw(im), 1190, 1500, t, col=(110, 126, 140))


def _duong(d, im):   # duong lang luc chieu, bui tre
    d.rectangle([0, 0, W, 1000], fill=(70, 56, 52)); d.rectangle([0, 1000, W, H], fill=(56, 46, 38))
    for j in range(9):
        x = j * 130 - 20; d.line([(x, 1000), (x + 30, 380)], fill=(40, 46, 34), width=10)
        for k in range(6): d.line([(x + 30 * k / 6, 1000 - 100 * k), (x + 30 * k / 6 + 70, 960 - 100 * k)], fill=(44, 52, 36), width=5)


def _duong_dyn(im, t, st):
    q = min(1.0, t / max(1.0, st['dur']))
    person2(im, 700 - 260 * q, 1300, 470, 'nk', -1, ph=t * 1.1)
    person2(im, 860 - 260 * q, 1300, 420, 'thinu', -1, ph=t * 1.1 + .4, cui=True)
    person2(im, 150, 1330, 500, 'tn', 1)


def _cau(d, im):   # cau Lieu Khe dem trang
    d.rectangle([0, 0, W, 1100], fill=(14, 18, 28)); moon(d, 820, 470, 50); river(d, 1100, H, (18, 24, 34))
    d.arc([60, 860, 1020, 1400], 200, 340, fill=(70, 58, 46), width=40)
    for j in range(9): d.line([(180 + j * 90, 905 - abs(4 - j) * 6), (180 + j * 90, 850 - abs(4 - j) * 6)], fill=(60, 48, 38), width=8)


def _cau_dyn(im, t, st):
    ripples(ImageDraw.Draw(im), 1120, 1500, t)
    person2(im, 560, 920, 360, 'nk', 1, dan=True)
    person2(im, 700, 916, 330, 'thinu', -1, cui=True)
    if st.get('tn'): person2(im, 140, 1320, 520, 'tn', 1, pose='point' if t > 1.5 else 'down')


def _toi_dyn(im, t, st):   # nha toi om: chi thay vien quan tai mo
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W, H], fill=(8, 8, 8))
    person2(im, 300, 1290, 520, 'tn', 1)


def _tuong_dyn(im, t, st):
    _qt_dyn(im, t, st)
    person2(im, 880, 1110, 380, 'tuong', -1, dan=True, cui=True)


def _baisong_post(im, t, st):
    person2(im, 760, 1250, 470, 'nk', -1, ghost=.32 + .12 * math.sin(t * 1.5))


def _baisong_dyn(im, t, st):
    ripples(ImageDraw.Draw(im), 910, 1150, t, n=16)


def _thuyen_trong(im, t, st):
    d = ImageDraw.Draw(im); ripples(d, 1010, 1500, t); boat(d, 540, 1170, 620)
    d.line([(380, 1150), (460, 1130), (520, 1160)], fill=(170, 150, 110), width=6)   # day troi bo lai


def _riu_dyn(im, t, st):
    _gao_dyn(im, t, st)
    sw = (t * 1.4) % 1
    a = -60 + 100 * min(1.0, sw * 2.5)
    person2(im, 610, 1330, 500, 'dl', -1, pose='reach')
    d = ImageDraw.Draw(im); hx, hy = 520, 1030
    ex, ey = hx + 120 * math.cos(math.radians(a + 180)), hy + 120 * math.sin(math.radians(a + 180))
    d.line([(hx, hy), (ex, ey)], fill=(110, 84, 54), width=10)
    if sw < .5: d.polygon([(ex, ey), (ex - 20, ey - 30), (ex + 20, ey - 30)], fill=(170, 170, 170))
    else:   # rìu gãy
        d.polygon([(470, 1000), (450, 960), (490, 970)], fill=(170, 170, 170))


def _riu_post(im, t, st):
    sw = (t * 1.4) % 1
    if .38 < sw < .5:
        d = ImageDraw.Draw(im)
        for k in range(10):
            a = k * 36; d.line([(450, 1000), (450 + 70 * math.cos(math.radians(a)), 1000 + 70 * math.sin(math.radians(a)))], fill=(255, 230, 160), width=4)


def _gocua_post(im, t, st):
    a = .3 + .1 * math.sin(t * 2)
    person2(im, 700, 1200, 360, 'tn', 1, ghost=a); person2(im, 780, 1200, 330, 'nk', 1, ghost=a, pose='reach')


def _gocua_dyn(im, t, st):
    d = ImageDraw.Draw(im); d.rectangle([780, 1040, 860, 1180], fill=(240, 190, 110))   # den trong chua
    kapok(im, 300, 1200, t, 1.0)


def _onggia_dyn(im, t, st):
    person2(im, 330, 1330, 520, 'gia', 1, pose='point'); person2(im, 760, 1330, 560, 'ds', -1)


def _bua_dyn(im, t, st):
    _te_dyn(im, t, st)
    d = ImageDraw.Draw(im)
    for j in range(3): d.rectangle([420 + j * 70, 1010, 460 + j * 70, 1080], fill=(230, 200, 60), outline=(150, 40, 30), width=3)
    fl = 40 + 14 * math.sin(t * 13)
    d.polygon([(780, 1050), (800, 1050 - fl * 2), (820, 1050)], fill=(255, 170, 60)); d.polygon([(788, 1050), (800, 1050 - fl), (812, 1050)], fill=(255, 236, 160))


def _nui(d, im):
    d.rectangle([0, 0, W, H], fill=(110, 116, 132))
    for k, (y, c) in enumerate([(820, (84, 92, 110)), (930, (66, 74, 90)), (1040, (50, 58, 70))]):
        pts = [(0, H)] + [(x, y - 120 * abs(math.sin(x / 210 + k))) for x in range(0, W + 1, 60)] + [(W, H)]
        d.polygon(pts, fill=c)
    d.polygon([(0, H), (W, H), (600, 1050), (560, 1050)], fill=(70, 66, 60))


def _nui_dyn(im, t, st):
    q = min(1.0, t / max(1.0, st['dur']))
    person2(im, 600 - 30 * q, 1500 - 420 * q, 460 * (1 - .65 * q), 'ds', 1, ph=t * 1.1)


def _onggia2_dyn(im, t, st):
    person2(im, 330, 1330, 520, 'gia', 1, pose='point'); person2(im, 760, 1330, 540, 'tn', -1)


def _trau_dyn2(im, t, st):
    _trau_dyn(im, t, st)


def register(SCENES, CAM):
    M = lambda x, y, r, k=1.0: (x, y, r, MOON, k)
    Wm = lambda x, y, r, k=1.0: (x, y, r, WARM, k)
    def mk(name, seed, base, bg, lights, amb, dyn=None, post=None, st=None, cam=None):
        SCENES[name] = lambda: (Set(seed, base, bg, lights, amb, dyn, post), dict(st or {}))
        if cam: CAM[name] = cam
    A = (0.15, 0.15, 0.2)
    mk('g_cho', 21, (24, 24, 30), _cho, [M(820, 420, 300, .9), Wm(730, 1050, 260, 1.0)], A, _cho_dyn, st={'tn': True}, cam=(1.1, 560, 1000))
    mk('g_gap', 22, (20, 22, 30), _bo_song, [M(240, 430, 380, 1.1), M(560, 1000, 420, .5)], A, _gap_dyn, cam=(1.08, 560, 1000))
    mk('g_thuyen', 23, (18, 18, 24), _thuyen_dem, [Wm(730, 1050, 300, 1.3), M(860, 380, 260, .7)], A, _thuyen_dyn, st={'hai': True}, cam=(1.15, 560, 1040))
    mk('g_tho', 23, (18, 18, 24), _thuyen_dem, [Wm(560, 1050, 300, 1.4)], A, _thuyen_dyn, st={'hai': True, 'tho': True}, cam=(1.5, 560, 1040))
    mk('g_sang', 24, (60, 66, 80), _thuyen_dem, [(540, 700, 700, (.7, .78, .9), .9)], (0.4, 0.44, 0.52), _thuyen_dyn, st={'mot': True}, cam=(1.12, 560, 1040))
    mk('g_banbuon', 25, (40, 36, 32), _ban_buon, [Wm(540, 820, 420, 1.2)], (0.2, 0.18, 0.18), _ban_dyn, cam=(1.08, 560, 1000))
    mk('g_leu', 26, (16, 18, 22), _leu_ngoai, [M(200, 360, 300, .8), (640, 1000, 300, (.5, .6, .55), .5)], A, _leu_dyn, cam=(1.05, 560, 1000))
    mk('g_quantai', 27, (30, 30, 30), _quan_tai, [(560, 980, 360, COLDG, 1.1)], (0.1, 0.12, 0.12), _qt_dyn, st={'tn': True, 'nk': True}, cam=(1.05, 560, 1050))
    mk('g_quantai_cl', 27, (30, 30, 30), _quan_tai, [(560, 980, 360, COLDG, 1.1)], (0.1, 0.12, 0.12), _qt_dyn, cam=(1.4, 560, 1040))
    mk('g_chay', 28, (14, 14, 18), _duong_chay, [M(880, 900, 360, .7)], A, _chay_dyn)
    mk('g_benh', 29, (36, 32, 28), _giuong, [Wm(880, 980, 380, 1.2)], (0.12, 0.11, 0.12), _giuong_dyn, _giuong_post, st={'hon': True}, cam=(1.08, 540, 1000))
    mk('g_troi', 29, (36, 32, 28), _giuong, [Wm(880, 980, 420, 1.2)], (0.14, 0.13, 0.13), _giuong_dyn, st={'troi': True}, cam=(1.05, 520, 1000))
    mk('g_chet', 27, (30, 30, 30), _quan_tai, [(560, 980, 380, COLDG, .9)], (0.08, 0.09, 0.1), _qt_dyn, st={'chet': True}, cam=(1.2, 560, 1080))
    mk('g_langma', 30, (14, 18, 22), _lang_dem, [M(540, 900, 600, .6)], A, None, _lang_post, cam=(1.05, 540, 1050))
    mk('g_daomo', 31, (24, 22, 20), _dao_mo, [Wm(620, 760, 420, 1.3)], A, _dao_dyn, cam=(1.05, 540, 1050))
    mk('g_nemsong', 32, (18, 22, 28), _nem_song, [M(820, 360, 320, .8), M(600, 1150, 400, .5)], A, _nem_dyn, cam=(1.08, 520, 1050))
    mk('g_cay', 33, (16, 18, 24), _gao_chua, [M(900, 720, 300, .8), (380, 820, 480, (.9, .55, .5), .7)], A, _gao_dyn, _gao_post, st={'hon': True}, cam=(1.0, 540, 960))
    mk('g_daosi', 33, (16, 18, 24), _gao_chua, [M(900, 720, 300, .8), (380, 820, 480, (.9, .55, .5), .7)], A, _ds_dyn, _gao_post, st={'hon': True, 'chi': True}, cam=(1.0, 540, 960))
    mk('g_dante', 34, (20, 18, 18), _dan_te, [Wm(540, 980, 420, 1.4)], A, _te_dyn, cam=(1.05, 540, 1060))
    mk('g_bao', 35, (8, 10, 14), _bao, [(540, 400, 600, (.6, .66, .8), .8), (420, 1000, 500, (.6, .66, .8), .6)], (0.2, 0.2, 0.26), _bao_dyn, _bao_post)
    mk('g_trau', 36, (12, 10, 10), _trau, [(540, 1000, 600, (.9, .4, .3), .8)], (0.1, 0.07, 0.07), _trau_dyn, _trau_post, cam=(1.05, 540, 1060))
    mk('g_tuchoi', 37, (64, 70, 84), _tu_choi, [(560, 800, 700, (.8, .82, .9), .7)], (0.42, 0.44, 0.5), _tc_dyn)
    mk('g_binhyen', 38, (96, 104, 120), _binh_yen, [(540, 500, 800, (1.0, .9, .78), .6)], (0.5, 0.52, 0.58), _by_dyn)
    mk('g_cay2', 33, (16, 18, 24), _gao_chua, [M(900, 720, 300, .8), (380, 820, 480, (.9, .55, .5), .7)], A, _gao_dyn, cam=(1.0, 540, 960))
    mk('g_quantai_ma', 27, (30, 30, 30), _quan_tai, [(560, 980, 360, COLDG, 1.1)], (0.1, 0.12, 0.12), _qt_dyn, _qt_post, st={'hon': True}, cam=(1.3, 560, 1020))
    mk('g_duong', 41, (70, 56, 52), _duong, [(700, 600, 700, (1.0, .8, .62), .9)], (0.3, 0.27, 0.27), _duong_dyn, cam=(1.05, 520, 1020))
    mk('g_cau', 42, (14, 18, 28), _cau, [M(820, 470, 340, 1.0), M(600, 900, 360, .6)], A, _cau_dyn, cam=(1.05, 540, 1000))
    mk('g_cau_tn', 42, (14, 18, 28), _cau, [M(820, 470, 340, 1.0), M(600, 900, 360, .6)], A, _cau_dyn, st={'tn': True}, cam=(1.05, 520, 1020))
    mk('g_toi', 27, (8, 8, 8), _quan_tai, [(560, 1000, 200, COLDG, .25)], (0.05, 0.05, 0.06), _toi_dyn, cam=(1.1, 480, 1060))
    mk('g_tuong', 27, (30, 30, 30), _quan_tai, [(560, 980, 380, COLDG, 1.1), Wm(880, 900, 220, .6)], (0.1, 0.12, 0.12), _tuong_dyn, st={'tn': True}, cam=(1.05, 560, 1050))
    mk('g_tuong_cl', 27, (30, 30, 30), _quan_tai, [(700, 980, 380, COLDG, 1.0), (880, 900, 260, COLDG, .6)], (0.08, 0.1, 0.1), _tuong_dyn, cam=(1.7, 860, 900))
    mk('g_niu', 27, (30, 30, 30), _quan_tai, [(560, 980, 360, COLDG, 1.1)], (0.1, 0.12, 0.12), _qt_dyn, st={'tn': True, 'nk': True}, cam=(1.35, 300, 1020))
    mk('g_baisong', 22, (20, 22, 30), _bo_song, [M(240, 430, 380, 1.0)], A, _baisong_dyn, _baisong_post, cam=(1.08, 600, 1000))
    mk('g_thuyen_trong', 23, (14, 16, 22), _thuyen_dem, [M(860, 380, 300, .8)], (0.16, 0.17, 0.22), _thuyen_trong, cam=(1.15, 540, 1060))
    mk('g_riu', 33, (16, 18, 24), _gao_chua, [M(900, 720, 300, .8), (380, 820, 480, (.9, .55, .5), .7)], A, _riu_dyn, _riu_post, cam=(1.05, 480, 980))
    mk('g_gocua', 33, (16, 18, 24), _gao_chua, [M(900, 720, 300, .6), Wm(820, 1100, 260, 1.0)], A, _gocua_dyn, _gocua_post, cam=(1.2, 700, 1040))
    mk('g_onggia', 37, (64, 70, 84), _tu_choi, [(560, 800, 700, (.8, .82, .9), .7)], (0.42, 0.44, 0.5), _onggia_dyn, cam=(1.05, 540, 1050))
    mk('g_bua', 34, (20, 18, 18), _dan_te, [Wm(540, 980, 420, 1.4), Wm(800, 1000, 200, 1.0)], A, _bua_dyn, cam=(1.05, 560, 1060))
    mk('g_vaonui', 43, (110, 116, 132), _nui, [(540, 500, 800, (1.0, .9, .8), .5)], (0.5, 0.52, 0.58), _nui_dyn)
    mk('g_onggia2', 41, (70, 56, 52), _duong, [(700, 600, 700, (.85, .85, .9), .8)], (0.36, 0.36, 0.4), _onggia2_dyn, cam=(1.05, 540, 1050))
    mk('g_bia1', 27, (30, 30, 30), _quan_tai, [(560, 980, 360, COLDG, 1.1)], (0.1, 0.12, 0.12), _qt_dyn, _qt_post, st={'tn': True, 'hon': True}, cam=(1.05, 560, 1050))
    mk('g_bia2', 29, (36, 32, 28), _giuong, [Wm(880, 980, 380, 1.2)], (0.12, 0.11, 0.12), _giuong_dyn, _giuong_post, st={'hon': True}, cam=(1.08, 540, 1000))
    mk('g_bia3', 33, (16, 18, 24), _gao_chua, [M(900, 720, 300, .8), (380, 820, 480, (.9, .55, .5), .7)], A, _gao_dyn, _gao_post, st={'hon': True})
