"""Doc so va chuan chinh ta cho may dung AVF (chu chot 23/11/2026).

- Phu de / chu tren hinh: viet SO bang chu so (2026, 59.000 dong, 19:20, 15/8/2003).
- Giong doc (TTS): doc_tts(text) tu doi so -> chu tieng Viet; kich ban KHONG can tu viet so bang chu nua.
- Chinh ta: chuan_dau(text) dat dau theo kieu bao chi pho bien (hòa, tòa, thủy, dọa, hủy), dung cho moi chu hien tren hinh.
"""
import re
import unicodedata

CS = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']


def _hai_so(n, day_du):
    """0..99; day_du=True khi dung sau hang tram (them 'linh')."""
    c, d = divmod(n, 10)
    if c == 0:
        return ('linh ' + CS[d]) if day_du and d else (CS[d] if not day_du else '')
    if c == 1:
        s = 'mười'
        if d == 5: return s + ' lăm'
        return s + (' ' + CS[d] if d else '')
    s = CS[c] + ' mươi'
    if d == 0: return s
    if d == 1: return s + ' mốt'
    if d == 5: return s + ' lăm'
    if d == 4: return s + ' tư'
    return s + ' ' + CS[d]


def _ba_so(n, day_du):
    t, r = divmod(n, 100)
    if t == 0 and not day_du:
        return _hai_so(r, False)
    s = CS[t] + ' trăm'
    if r: s += ' ' + _hai_so(r, True)
    return s


def so_chu(n):
    """so nguyen -> chu: 2003 -> hai nghìn không trăm linh ba; 1988 -> một nghìn chín trăm tám mươi tám."""
    n = int(n)
    if n < 0: return 'âm ' + so_chu(-n)
    if n < 10: return CS[n]
    if n < 100: return _hai_so(n, False)
    don = ['', 'nghìn', 'triệu', 'tỷ', 'nghìn tỷ', 'triệu tỷ']
    nhom = []
    while n: nhom.append(n % 1000); n //= 1000
    out = []
    for i in range(len(nhom) - 1, -1, -1):
        g = nhom[i]
        if g == 0:
            continue
        day_du = i < len(nhom) - 1
        out.append(_ba_so(g, day_du) + (' ' + don[i] if don[i] else ''))
    return ' '.join(out).replace('  ', ' ').strip()


def _so_thuc(s):
    """'7,2' -> bảy phẩy hai ; '59.000' -> năm mươi chín nghìn ; '1.200,5' -> ..."""
    s = s.strip()
    if re.fullmatch(r'\d{1,3}(\.\d{3})+(,\d+)?', s): s = s.replace('.', '')
    if ',' in s:
        a, b = s.split(',', 1)
        b = b.rstrip('0')   # 28/11 chu chot: 5,0 -> 'năm', 5,10 -> 'năm phẩy một'
        if not b: return so_chu(a)
        bb = ' '.join(CS[int(c)] for c in b) if b.startswith('0') or len(b) > 2 else so_chu(b)
        return so_chu(a) + ' phẩy ' + bb
    return so_chu(s)


def _ngay(d):
    d = int(d)
    return ('mồng ' + CS[d]) if d <= 10 and d != 10 else ('mồng mười' if d == 10 else so_chu(d))


def _thang(m):
    m = int(m)
    return {4: 'tư', 1: 'một'}.get(m, so_chu(m))


def doc_tts(text):
    """doi so trong cau sang chu de giong doc; giu nguyen phan chu."""
    t = text
    # giu nguyen [[ ]] (W87 dung de doc ten rieng)
    # khoang ngay: 25–30/1/1789
    t = re.sub(r'\b(\d{1,2})\s*[–-]\s*(\d{1,2})/(\d{1,2})/(\d{3,4})\b',
               lambda m: f'{_ngay(m[1])} đến {_ngay(m[2])} tháng {_thang(m[3])} năm {so_chu(m[4])}', t)
    # ngay day du d/m/yyyy (tranh lap 'ngay ngay')
    def _dmy(m):
        pre = m[1] or ''
        dd = _ngay(m[2])
        if pre.lower().startswith('mồng'): dd = dd.replace('mồng ', '')
        return f'{pre}{dd} tháng {_thang(m[3])} năm {so_chu(m[4])}'
    t = re.sub(r'((?:[Nn]gày|[Tt]ối|[Ss]áng|[Tt]rưa|[Cc]hiều|[Đđ]êm|[Rr]ạng sáng|[Mm]ồng) )?\b(\d{1,2})/(\d{1,2})/(\d{3,4})\b', _dmy, t)
    def _dm(m):
        pre = m[1] or ''; dd = _ngay(m[2])
        if pre.lower().startswith('mồng'): dd = dd.replace('mồng ', '')
        return f'{pre}{dd} tháng {_thang(m[3])}'
    t = re.sub(r'((?:[Mm]ồng) )?\b(\d{1,2})/(\d{1,2})\b(?!/)', _dm, t)   # d/m
    t = re.sub(r'\b[Tt]háng (\d{1,2})/(\d{3,4})\b', lambda m: f'tháng {_thang(m[1])} năm {so_chu(m[2])}', t)
    # gio: 19:19:51, 19:20, 17h05, 7h
    t = re.sub(r'\b(\d{1,2}):(\d{2}):(\d{2})\b', lambda m: f'{so_chu(m[1])} giờ {so_chu(m[2])} phút {so_chu(m[3])} giây', t)
    t = re.sub(r'\b(\d{1,2}):(\d{2})\b', lambda m: f'{so_chu(m[1])} giờ' + ((f' {so_chu(m[2])}' + (' phút' if int(m[2]) < 10 else '')) if int(m[2]) else ''), t)
    t = re.sub(r'\b(\d{1,2})h(\d{2})\b', lambda m: f'{so_chu(m[1])} giờ {so_chu(m[2])}', t)
    t = re.sub(r'\b(\d{1,2})h\b', lambda m: f'{so_chu(m[1])} giờ', t)
    # thu tu
    t = re.sub(r'\b([Tt]hứ) (\d{1,2})\b', lambda m: m[1] + ' ' + ({1: 'nhất', 4: 'tư'}.get(int(m[2]), so_chu(m[2]))), t)
    # khoang so 1953–1954
    t = re.sub(r'\b(\d+)\s*[–]\s*(\d+)\b', lambda m: f'{so_chu(m[1])} đến {so_chu(m[2])}', t)
    # phan tram, don vi
    t = re.sub(r'(\d+(?:[.,]\d+)*)\s*%', lambda m: _so_thuc(m[1]) + ' phần trăm', t)
    t = re.sub(r'\bkm\b', 'ki lô mét', t); t = re.sub(r'\bkg\b', 'ki lô gam', t)
    t = re.sub(r'\b(\d+)\s*m\b', lambda m: so_chu(m[1]) + ' mét', t)
    # so con lai: 59.000 ; 7,2 ; 2026
    t = re.sub(r'\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d+,\d+\b|\b\d+\b', lambda m: _so_thuc(m[0]), t)
    t = t.replace('–', ', ').replace('—', ', ')
    return re.sub(r'\s{2,}', ' ', t).strip()


# --- chinh ta: dau thanh kieu bao chi (hòa, khỏe, thủy) ---
_TONE = {'̀', '́', '̃', '̉', '̣'}


def _cd_tu(w):
    """oa/oe/uy mo (khong co phu am cuoi): dat dau o chu dau. Bo qua 'qu'."""
    n = unicodedata.normalize('NFD', w)
    base = ''.join(c for c in n if c not in _TONE)
    tones = [c for c in n if c in _TONE]
    if len(tones) != 1: return w
    b = base.lower()
    m = re.search(r'(oa|oe|uy)$', b)
    if not m or b.endswith(('qua', 'quy', 'que')): return w
    i = m.start()
    # chen dau sau chu cai dau cua cum (vi tri i trong base NFD: base khong dau, nhung con dau phu nhu ^ (khong co o oa/oe/uy))
    cs = list(base); cs.insert(i + 1, tones[0])
    return unicodedata.normalize('NFC', ''.join(cs))


def chuan_dau(text):
    if not text: return text
    return re.sub(r'[^\W\d_]+', lambda m: _cd_tu(m[0]), text)


if __name__ == '__main__':
    for x in ['Tối 15/8/2003, chị Hoan bị hại.', 'Ngày 26/3/2004, toà tuyên.', 'lúc 19:19:51 đến 19:20:31', '59.000 đồng và 7,2 tỷ',
              'năm 2026, 1988, 1961, 2005, 105, 1015, 21, 24, 15, 1.200 km', 'từ 25–30/1/1789', 'thứ 4', '19:05', 'mồng 5/7/2013',
              '1953–1954', '75 tuổi', '12 năm tù', '3 triệu đồng', '60%']:
        print(x, '=>', doc_tts(x))
    print(chuan_dau('Toà án huỷ bản án, doạ nạt, hoá ra, Thuỷ, quý, hoàn, khoẻ, Hoà Bình, TOÀ'))


# --- chu -> so cho PHU DE (kich ban cu viet so bang chu) ---
_DG = {'không': 0, 'một': 1, 'mốt': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 'tư': 4, 'năm': 5, 'lăm': 5, 'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9}
_MUL = {'mươi', 'trăm', 'nghìn', 'ngàn', 'triệu', 'tỷ', 'tỉ'}
_KEY = _MUL | {'mười'}


def _parse(toks):
    """toks: list tu thuong -> (gia tri, so tu dung). Dung som khi gap tu khong hop le."""
    total = 0; group = 0; pend = None; used = 0; prev = None
    for i, w in enumerate(toks):
        nxt = toks[i + 1] if i + 1 < len(toks) else ''
        if w in ('linh', 'lẻ'):
            if prev not in ('trăm', 'nghìn', 'ngàn'): break
            prev = w; used = i + 1; continue
        if w == 'mười':
            if pend is not None: break
            group += 10; pend = None; prev = w; used = i + 1; continue
        if w == 'mươi':
            if pend is None: break
            group += pend * 10; pend = None; prev = w; used = i + 1; continue
        if w == 'trăm':
            if pend is None: break
            group += pend * 100; pend = None; prev = w; used = i + 1; continue
        if w in ('nghìn', 'ngàn', 'triệu', 'tỷ', 'tỉ'):
            g = group + (pend or 0)
            if g == 0: break
            mul = {'nghìn': 1000, 'ngàn': 1000, 'triệu': 10 ** 6, 'tỷ': 10 ** 9, 'tỉ': 10 ** 9}[w]
            total += g * mul; group = 0; pend = None; prev = w; used = i + 1; continue
        if w in _DG:
            d = _DG[w]
            ok = False
            if w in ('năm', 'một', 'không'):
                ok = nxt in _MUL or prev in ('linh', 'lẻ') or (w == 'một' and prev in ('mươi', 'mười')) or (w == 'năm' and prev == 'mươi' and False)
                if w == 'không': ok = nxt == 'trăm'
            elif w in ('mốt', 'tư', 'lăm'):
                ok = prev in ('mươi', 'mười') or (pend is not None and w != 'tư')
                if pend is not None and w in ('lăm', 'mốt'):   # 'hai lăm' = 25
                    group += pend * 10 + d; pend = None; prev = 'mươi'; used = i + 1; continue
            else:
                ok = True
            if not ok or pend is not None: break
            if prev in ('mươi', 'mười', 'linh', 'lẻ'):
                group += d; prev = 'dv'; used = i + 1; continue
            pend = d; prev = w; used = i + 1; continue
        break
    # bo duoi chua dung (vd 'hai' cuoi khong co he so)
    val = total + group + (pend or 0)
    return val, used


def _gon(v):
    """26/11: so tien lon gon kieu bao: 129100000 -> '129,1 triệu', 7200000000 -> '7,2 tỷ'; le qua 2 so thap phan -> 129.150.500."""
    for mul, ten in ((10 ** 9, 'tỷ'), (10 ** 6, 'triệu')):
        if v >= mul and v % (mul // 100) == 0:
            a = f'{v / mul:.2f}'.rstrip('0').rstrip('.')
            return a.replace('.', ',') + ' ' + ten
    return f'{v:,}'.replace(',', '.')


def chu_so(text, dau_cau=True):
    """'năm một nghìn chín trăm bốn mươi mốt' -> 'năm 1941'; 'ba trăm năm mươi nghìn' -> '350.000'; giu chu o dau cau va ten rieng."""
    toks = re.split(r'(\s+)', text)
    out = []; i = 0; start = dau_cau
    words = [(j, t) for j, t in enumerate(toks)]
    res = list(toks)
    j = 0; n = len(toks)
    while j < n:
        t = toks[j]
        if not t.strip(): j += 1; continue
        core = t.strip('.,!?…:;"“”()')
        low = core.lower()
        is_start = start; start = t.endswith(('.', '!', '?', '…', ':'))
        if low in _DG or low == 'mười':
            # gom chuoi tu so lien nhau (chi cach bang khoang trang, khong dau cau o giua)
            seq = []; idx = []; k = j
            while k < n:
                tk = toks[k]
                if not tk.strip(): k += 1; continue
                c = tk.strip('.,!?…:;"“”()'); lc = c.lower()
                if lc not in _DG and lc not in _MUL and lc not in ('mười', 'linh', 'lẻ'): break
                seq.append(lc); idx.append(k)
                if tk != c and not tk.startswith(c): break      # tu co dau cau dung truoc
                if tk.rstrip('.,!?…:;"“”()') != tk: break     # dau cau sau tu -> het chuoi
                k += 1
            val, used = _parse(seq)
            okv = used >= 1 and (any(s in _KEY for s in seq[:used]) or val >= 10)
            if okv and (is_start or core[:1].isupper()):   # dau cau / ten rieng: giu chu, bo qua ca chuoi
                j = idx[used - 1] + 1; start = toks[idx[used - 1]].endswith(('.', '!', '?', '…', ':')); continue
            if okv:
                prevw = ''
                for q in range(j - 1, -1, -1):
                    if toks[q].strip(): prevw = toks[q].strip('.,!?…:;"“”()').lower(); break
                last = idx[used - 1]
                # 26/11 (QC v20: '6.000.000 rưỡi', '129.000.000 một'): duoi 'rưỡi' / so le sau triệu-tỷ / 'phẩy'
                if used >= 2 and seq[used - 1] in _DG and seq[used - 2] in ('triệu', 'tỷ', 'tỉ'):   # 'năm triệu hai' = 5,2 triệu, khong phai 5.000.002
                    b_ = 10 ** 6 if seq[used - 2] == 'triệu' else 10 ** 9
                    val += _DG[seq[used - 1]] * (b_ // 10 - 1)
                unit = seq[used - 1]; base = {'triệu': 10 ** 6, 'tỷ': 10 ** 9, 'tỉ': 10 ** 9, 'nghìn': 1000, 'ngàn': 1000}.get(unit)
                if base and toks[last].rstrip('.,!?…:;"“”()') == toks[last]:
                    nx = [q for q in range(last + 1, n) if toks[q].strip()][:2]
                    w1 = toks[nx[0]].strip('.,!?…:;"“”()').lower() if nx else ''
                    w2 = toks[nx[1]].strip('.,!?…:;"“”()').lower() if len(nx) > 1 else ''
                    end1 = nx and toks[nx[0]].rstrip('.,!?…:;"“”()') != toks[nx[0]]
                    if w1 == 'rưỡi':
                        k_ = val // base
                        val += base // 2 if k_ < 100 else (base * 50 if k_ % 100 == 0 else 0); last = nx[0]
                    elif base >= 10 ** 6 and w1 in _DG and w1 != 'không' and (end1 or w2 not in _MUL | {'mươi', 'mười', 'linh', 'lẻ'}):
                        val += _DG[w1] * base // 10; last = nx[0]
                s_ = str(val) if (prevw == 'năm' and 1000 <= val <= 2199) or val < 1000 else _gon(val)
                tail = toks[last][len(toks[last].rstrip('.,!?…:;"“”()')):]
                head = toks[j][:len(toks[j]) - len(toks[j].lstrip('"“('))]
                res[j] = head + s_ + (tail if last == j else '')
                for q in range(j + 1, last + 1): res[q] = ''
                if last != j: res[last] = tail
                start = toks[last].endswith(('.', '!', '?', '…', ':'))
                j = last + 1; continue
        j += 1
    s = ''.join(res)
    return re.sub(r' {2,}', ' ', s).replace(' ,', ',').replace(' .', '.')
