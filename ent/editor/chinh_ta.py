"""Soat chinh ta tieng Viet theo CAU TAO AM TIET (27/11).
Bat duoc: van khong ton tai (vd "ngiệp", "trog", "nguời"), sai luat c/k, g/gh, ng/ngh,
thanh sai voi phu am cuoi p/t/c/ch (vd "hoãt"), dau bi tach roi (NFD).
Khong bat duoc: tu dung am tiet nhung sai nghia ("dành"/"giành") -> van can nguoi/Claude doc lai.
Bo qua: tu co so, chu f/j/w/z, tu viet hoa (ten rieng), tu viet tat toan chu hoa.
Dung: python3 editor/chinh_ta.py "van ban"  -> in cac tu nghi sai, exit 1 neu co."""
import re
import sys
import unicodedata

TONE = {'̀': 'huyen', '́': 'sac', '̃': 'nga', '̉': 'hoi', '̣': 'nang'}
ONSETS = ['ngh', 'ng', 'nh', 'ch', 'gh', 'gi', 'kh', 'ph', 'qu', 'th', 'tr',
          'b', 'c', 'd', 'đ', 'g', 'h', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'x', '']
RHYMES = set('''a ac ach ai am an ang anh ao ap at au ay
ăc ăm ăn ăng ăp ăt
âc âm ân âng âp ât âu ây
e ec em en eng eo ep et
ê êch êm ên ênh êp êt êu
i ia ich im in inh ip it iu
iêc iêm iên iêng iêp iêt iêu
o oa oac oach oai oam oan oang oanh oao oap oat oay oc oe oen oeo oet oi om on ong oong ooc op ot
oăc oăm oăn oăng oăt
ô ôc ôi ôm ôn ông ôp ôt
ơ ơi ơm ơn ơp ơt
u ua uân uât uâng uây uc uê uêch uênh ui um un ung uơ uy uya uych uyên uyêt uynh uyp uyt uyu up ut
uôc uôi uôm uôn uông uôt
ư ưa ưc ưi ưm ưn ưng ưt ưu ươc ươi ươm ươn ương ươp ươt ươu
y yêm yên yêng yêt yêu'''.split())
FRONT = ('i', 'e', 'ê', 'y')
STOP = ('p', 't', 'c', 'ch')


def tach(syl):
    """tra ve (am tiet bo thanh, thanh)"""
    d = unicodedata.normalize('NFD', syl.lower())
    tone = 'ngang'
    for ch, name in TONE.items():
        if ch in d: tone = name; d = d.replace(ch, '')
    return unicodedata.normalize('NFC', d), tone


def hop_le(syl):
    base, tone = tach(syl)
    for on in ONSETS:
        if not base.startswith(on): continue
        r = base[len(on):]
        if on == 'gi':   # gì, gìn, giếng: chu i dung chung voi van
            if r.startswith('i'): continue
            if r not in RHYMES or r == '': r = 'i' + r
        if on == 'qu' and (r == '' or r[0] in 'uo'): continue
        if r not in RHYMES: continue
        if on in ('c', 'g', 'ng') and r.startswith(FRONT): continue          # ce, gi(e), nge -> sai
        if on in ('k', 'gh', 'ngh') and not r.startswith(FRONT): continue    # ka, gha, ngha -> sai
        if r.endswith(STOP) and tone not in ('sac', 'nang'): continue        # hoãt -> sai
        return True
    return False


def soat(text):
    """tra ve danh sach tu nghi sai chinh ta (khong trung lap)"""
    t = text or ''
    bad = []
    if unicodedata.normalize('NFC', t) != t: bad.append('(dau bi tach - can NFC)')
    t = unicodedata.normalize('NFC', t)
    for raw in re.findall(r"[\w'’-]+", t):
        for w in raw.split('-'):
            if not w or re.search(r'[\d_fjwzFJWZ]', w): continue
            # tu co chu hoa ma khong co dau tieng Viet -> coi la ten/viet tat nuoc ngoai (Ocean, KGB), bo qua
            if w != w.lower() and not re.search(r'[à-ỹđ]', w.lower()): continue
            if not hop_le(w) and w.lower() not in bad: bad.append(w.lower())
    return bad


if __name__ == '__main__':
    s = ' '.join(sys.argv[1:]) or sys.stdin.read()
    b = soat(s)
    print('OK' if not b else 'NGHI SAI: ' + ', '.join(b))
    sys.exit(1 if b else 0)
