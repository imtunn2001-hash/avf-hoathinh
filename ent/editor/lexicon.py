"""Doi nguoc cach doc phien am (tu dien W57 / avf.tts_lexicon) ve ten goc cho PHU DE.
W57 thay ten nuoc ngoai bang phien am Viet truoc khi gui EverAI, nen file SRT tra ve chua phien am.
Danh sach REV lay tu: select say, src from avf.tts_lexicon where enabled and not sub_keep.
Them tu moi vao bang thi cap nhat REV o day (tu dai truoc)."""
import re

REV = [["Âu sần In phi ni ti","Ocean Infinity"],["Da ha ri","Zaharie"],["I ga ri","IGARI"],["Linh Tiên Ghi","Ling Tien Gi"],["He lần Linh","Helen Ling"],["Đờ Kinh en Ai","The King and I"],["Gơ khơ","Gurkha"],["Ma lai a","Malaya"],["em hát ba bảy không","MH370"],["Ca mơ rơn Hai lần","Cameron Highlands"],["Con ni Mang xcau","Connie Mangskau"],["Ca li phoóc ni a","California"],["Mun lai Cót tịch","Moonlight Cottage"],["Pen xin vê ni a","Pennsylvania"],["Cu a la Lăm pơ","Kuala Lumpur"],["In đô nê xi a","Indonesia"],["Ác hen ti na","Argentina"],["Ô rang Át li","Orang Asli"],["Ô xtrây li a","Australia"],["Oa sinh tơn","Washington"],["Phi líp pin","Philippines"],["Ma lai xi a","Malaysia"],["Gim Tôm xơn","Jim Thompson"],["Ta mam Sút","Tamam Shud"],["Mang xcau","Mangskau"],["Ti ta níc","Titanic"],["Ca giê bê","KGB"],["pê en giê","PNJ"],["U crai na","Ukraine"],["Xin ga po","Singapore"],["Xô mơ tơn","Somerton"],["ét giê xê","SJC"],["Tếch dát","Texas"],["Đe la oe","Delaware"],["Brót uây","Broadway"],["Xi ai ây","CIA"],["Ép bi ai","FBI"],["A đơ lết","Adelaide"],["Mi an ma","Myanmar"],["I xra en","Israel"],["Phây búc","Facebook"],["Tích tóc","TikTok"],["Pho rếch","Forex"],["Tôm xơn","Thompson"],["Niu Oóc","New York"],["Ô ét ét","OSS"],["Diu túp","YouTube"],["e tê ép","ETF"],["xê pê i","CPI"],["Tun min","Toulmin"],["Bra xin","Brazil"],["Chi lê","Chile"],["Hít le","Hitler"],["Bô ing","Boeing"],["Na xa","NASA"],["Da lô","Zalo"],["Pê ru","Peru"],["I rắc","Iraq"],["Pa ri","Paris"],["Đô gi","DOJI"],["Liu","Lew"]]
_RX = [(re.compile(r'(?<![\w])' + r'\s+'.join(map(re.escape, s.split())) + r'(?![\w])', re.I if s[0].islower() else 0), d) for s, d in REV]


def unlex(t):
    for rx, d in _RX:
        t = rx.sub(d, t)
    return t



def fix_cues(srt):
    """Phien am nhieu tu bi SRT cat ngang 2 dong (vd 'Đờ Kinh en' | 'Ai vo nhac kich') -> dua ve ten goc o dong truoc."""
    out = [list(c) for c in srt]
    for i in range(len(out) - 1):
        a, b = out[i][2].split(), out[i + 1][2].split()
        for say, src in REV:
            w = say.split()
            if len(w) < 2: continue
            for k in range(1, len(w)):
                if [x.lower() for x in a[-k:]] == [x.lower() for x in w[:k]] and [x.lower().strip('.,?!') for x in b[:len(w) - k]] == [x.lower() for x in w[k:]]:
                    tail = b[len(w) - k - 1][len(w[-1]):] if len(w) - k >= 1 else ''
                    a = a[:-k] + [src + tail]; b = b[len(w) - k:]
                    break
        out[i][2], out[i + 1][2] = ' '.join(a), ' '.join(b)
    # 26/11 (QC v20 '100 29.000.000 một'): so doc bang chu bi SRT cat ngang 2 dong -> don ca cum so sang dong sau
    try:
        import doc_so
        NW = set(doc_so._DG) | doc_so._MUL | {'mười', 'linh', 'lẻ'}
        for i in range(len(out) - 1):
            a, b = out[i][2].split(), out[i + 1][2].split()
            if not a or not b or a[-1] != a[-1].rstrip('.,!?…:;"“”()'): continue
            if b[0].strip('.,!?…:;"“”()').lower() not in NW | {'rưỡi'}: continue
            k = 0
            while k < len(a) and a[-1 - k].lower() in NW: k += 1
            if k == 0 or k == len(a): continue
            if not any(w.lower() in doc_so._MUL | {'mười'} for w in a[-k:]): continue   # 'năm' / 'một' le loi: de nguyen
            a0, a1 = out[i][0], out[i][1]; cut = a1 - (a1 - a0) * k / len(a)
            out[i][2] = ' '.join(a[:-k]); out[i][1] = cut
            out[i + 1][2] = ' '.join(a[-k:] + b); out[i + 1][0] = min(out[i + 1][0], cut)
    except Exception as e:
        print('noi so', e)
    # 23/11 (chu chot): phu de hien SO bang chu so (2026, 59.000) va dau kieu bao chi (hòa, tòa, thủy)
    try:
        import doc_so
        prev_end = True
        for c in out:
            t0 = c[2]
            c[2] = doc_so.chuan_dau(doc_so.chu_so(t0, dau_cau=prev_end))
            prev_end = t0.rstrip().endswith(('.', '!', '?', '…', ':'))
    except Exception as e:
        print('doc_so', e)
    return [tuple(c) for c in out if c[2].strip()]


if __name__ == '__main__':
    print(fix_cues([(0, 1, 'vở nhạc kịch Đờ Kinh en'), (1, 2, 'Ai, trên sân khấu')]))
    print(unlex('Gim Tôm xơn mất tích ở Ca mơ rơn Hai lần, Ma lai xi a. Ông làm cho Ô ét ét, sau đó Xi ai ây vào cuộc.'))
