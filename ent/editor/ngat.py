"""Ngat dong phu de theo CUM NGHIA (27/11, chu dan: "de y ky chinh ta, cach ngat nghi").
- Uu tien xuong dong sau dau cau (, . : ; ? !).
- Khong de dong ket thuc bang tu noi/hu tu (cua, va, nhung, cac, mot, la, thi, ...) -> tu do phai sang dong sau cung cum.
- Khong de dong bat dau bang tu dem sau (nay, ay, do, nua, ...).
- Khong de dong cuoi chi 1 tu (mo coi); can bang do dai cac dong.
- Chuan hoa NFC de dau tieng Viet khong bi tach roi khi ve.
Dung: lines = wrap_cum(draw, text, font, maxw)"""
import re
import unicodedata

KHONG_CUOI = set('''của và với cho để từ ở trong ngoài trên dưới những các mỗi một là thì mà nên vì nhưng rằng khi nếu được bị
đã đang sẽ không chưa chẳng rất lại cũng như hay hoặc hoặc tại do bởi qua về theo sau trước giữa vào ra cả từng
anh chị em ông bà cô chú bạn tôi mình nó họ ta người con cái chiếc những sự việc nỗi niềm cuộc'''.split())
KHONG_DAU = set('này ấy đó đấy nữa thôi nhé nhỉ à ạ hả chứ đâu kia'.split())
DAU = re.compile(r'[,.:;?!…]["”’)]*$')


def nfc(s):
    return unicodedata.normalize('NFC', re.sub(r'\s+', ' ', s or '').strip())


def _bare(w):
    return re.sub(r'[^\w]', '', w).lower()


def wrap_cum(d, s, f, maxw, max_lines=None, orig=None):
    """orig: ban chu thuong/hoa goc cua s (khi s da viet HOA) de nhan ra ten rieng, khong cat doi ten."""
    s = nfc(s)
    ws = s.split(' ')
    ow = nfc(orig).split(' ') if orig and len(nfc(orig).split(' ')) == len(ws) else ws
    if not ws or not s: return []
    sp = d.textlength(' ', font=f)
    wl = [d.textlength(w, font=f) for w in ws]
    n = len(ws)
    tot = sum(wl) + sp * (n - 1)
    # so dong toi thieu
    INF = float('inf')

    def width(i, j):  # tu i..j-1
        return sum(wl[i:j]) + sp * (j - i - 1)

    def brk_cost(j):  # xuong dong SAU tu j-1
        if j >= n: return 0.0
        a, b = ws[j - 1], ws[j]
        c = 0.0
        if DAU.search(a): c -= 60 if a.rstrip('"”’)')[-1] in ',;:' else 130
        elif _bare(a) in KHONG_CUOI: c += 80
        else: c += 25          # cat giua cum khong co dau: phat nhe (co the la tu ghep "trì | hoãn")
        if _bare(b) in KHONG_DAU: c += 80
        oa, ob = ow[j - 1], ow[j]   # ten rieng (Bạch Đằng, Lão Hạc): 2 tu viet hoa chu dau dung canh nhau
        if oa[:1].isupper() and ob[:1].isupper() and not oa.isupper() and not DAU.search(oa): c += 150
        return c

    best = None
    lo = max(1, int(-(-tot // maxw)))
    for L in range(lo, (max_lines or lo + 2) + 1):
        target = tot / L
        # dp[k][j]: chi phi chia ws[:j] thanh k dong
        dp = [[INF] * (n + 1) for _ in range(L + 1)]; bk = [[-1] * (n + 1) for _ in range(L + 1)]
        dp[0][0] = 0.0
        for k in range(1, L + 1):
            for j in range(1, n + 1):
                for i in range(j - 1, -1, -1):
                    w = width(i, j)
                    if w > maxw: break
                    if dp[k - 1][i] == INF: continue
                    c = dp[k - 1][i] + ((w - target) / max(1.0, target)) ** 2 * 45 + brk_cost(j)
                    if j - i == 1 and n > 2: c += 110   # dong chi 1 tu: xau
                    if c < dp[k][j]: dp[k][j] = c; bk[k][j] = i
        if dp[L][n] < INF:
            c = dp[L][n] + (L - lo) * 200     # them dong thi phat
            if best is None or c < best[0]:
                out = []; j = n
                for k in range(L, 0, -1):
                    i = bk[k][j]; out.append(' '.join(ws[i:j])); j = i
                best = (c, out[::-1])
    if best is None:   # tu qua dai: tra ve tung tu
        return ws
    return best[1]
