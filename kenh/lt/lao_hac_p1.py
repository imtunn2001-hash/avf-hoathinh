"""LIÊN THIÊN – Lão Hạc (Nam Cao), PHẦN 1/2: con trai bỏ đi phu cao su -> cậu Vàng -> ốm, bão, hết việc -> bán chó -> khóc hu hu.
python3 lao_hac_p1.py <thu_muc_ra> -> spec.json + spec_t.json (bản soát). Số viết bằng chữ số trong 'say' (máy tự đọc).
Ký hiệu nhịp chỉ đặt SAU dấu câu hoặc bọc cả câu (W87 v3.1).
Hook: khuôn "chi tiết lạ nhất" + lật – con chó do anh con trai mua "định để đến lúc cưới vợ thì giết thịt" (nguyên tác; Zing News trích),\nvậy mà bán nó lão lại "cười như mếu", "hu hu khóc". Bản 1 (khuôn D câu hỏi) bị chấm 5/10 vì đại trà + 3 chỗ lệch nguyên tác -> viết lại.
6 hook đã viết: (1) chi tiết ngoài lề "Lão Hạc có thật, ở ngay cạnh nhà Nam Cao" – (2) câu hỏi thẳng – (3) lật nghĩa
"Anh em tưởng lão bán chó vì đói? Lão bán để giữ phần cho con" – (4) gọi tên kiểu người "Nếu bố mẹ anh em ở quê hay nói tao ổn…"
– (5) cảnh hành động "Lão gọi con chó về ăn cơm. Lần cuối." – (6) lật "Con chó ấy không phải của lão" – (7) chi tiết lạ "Con chó làm lão khóc vốn được mua về để giết thịt" [CHỌN].
Ngoài lề (≥ 2 nguồn): nguyên mẫu lão Hạc là ông Trùm San, nhà ngay cạnh nhà Nam Cao ở làng Đại Hoàng, nuôi một con chó vàng,
con trai (Thụ) vào Nam làm phu/công nhân đồn điền cao su (VTC News 04/12/2023 "Chuyện 2 ông trùm là nguyên mẫu nhân vật lão Hạc";
Hội Nhà văn VN vanvn.vn 30/01/2024 theo Tiền Phong "Chuyện Lão Hạc, cậu Vàng, Chí Phèo, Thị Nở vẫn còn tiếp…").
Trích nguyên văn duy nhất: "Cậu Vàng đi đời rồi, ông giáo ạ!" (7 từ).
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CAST = {
    'laohac': dict(tag='LÃO HẠC', skin='#d9a070', hair='#e8e4da', hair_style='bald', outfit='#7a5a3a', outfit2='#5a4028', trim='#3a2a1a', mark='brow'),
    'onggiao': dict(tag='ÔNG GIÁO', skin='#e6b48a', hair='#140f0c', hair_style='khan', hat='#2a2a2a', outfit='#efe6cf', outfit2='#cfc3a3', trim='#7a5a2a', mark='mustache'),
    'contrai': dict(tag='CON TRAI LÃO', skin='#e0a878', hair='#140f0c', hair_style='band', outfit='#4a6a4a', outfit2='#36503a', trim='#c8a24a'),
    'muc': dict(tag='THẰNG MỤC', skin='#d8a070', hair='#140f0c', hair_style='khan', hat='#3a3a2a', outfit='#5a5a4a', outfit2='#44443a', trim='#2a2a2a', mark='scar'),
    'xien': dict(tag='THẰNG XIÊN', skin='#e0aa7c', hair='#140f0c', hair_style='nonla', outfit='#6a4a3a', outfit2='#4e362a', trim='#2a2a2a', mark='mole'),
    'trumsan': dict(tag='ÔNG TRÙM SAN', skin='#d9a070', hair='#e8e4da', hair_style='khan', hat='#4a3a2a', outfit='#6a5a4a', outfit2='#4e4236', trim='#3a2a1a', mark='pale'),
}
S = [
 dict(type='stage', label='', bg='village',
      cast=[dict(c='laohac', x=300, D=170, expr='sad', at=1)],
      icons=[dict(icon='dog', x=720, y=1170, s=1.4, at=0)],
      cards=[dict(t='KHÓC HU HU', x=540, y=1150, at=1, col='#c4281f', tc='#fff', fs=30)],
      say='{cao: Con chó lão Hạc bán đi, vốn được mua về để giết thịt.} /// {chậm: Vậy sao bán nó, lão lại khóc hu hu như con nít?}'),
 dict(type='ke', label='LIÊN THIÊN', board='LÃO HẠC|NAM CAO', expr='happy',
      say='Lại một truyện của Nam Cao. /// Lần này không có dao, chỉ có một con chó vàng.'),
 dict(type='stage', label='THÁCH CƯỚI', bg='village',
      cast=[dict(c='laohac', x=320, D=175, expr='sad'), dict(c='contrai', x=780, D=175, face=-1, expr='angry')],
      cards=[dict(t='THÁCH CƯỚI CAO', x=540, y=1150, at=1, col='#c4281f', tc='#fff', fs=30)],
      say='Lão Hạc góa vợ, sống với đứa con trai duy nhất. Nhưng đám cưới của anh không thành. // Nhà gái thách cưới cao quá. Nhà lão nghèo, lo không nổi.'),
 dict(type='stage', label='ĐI PHU CAO SU', bg='paper',
      cast=[dict(c='contrai', x=540, D=180, expr='sad', hands=[[.6, -.15, 'scroll']])],
      cards=[dict(t='ĐỒN ĐIỀN CAO SU', x=540, y=1150, at=0, col='#2e5a46', tc='#fff', fs=30)],
      say='Anh con trai phẫn chí, ký giấy đi làm phu đồn điền cao su. Con chó lẽ ra thành cỗ cưới, nay được sống. /// {hạ: Ở nhà chỉ còn ông lão, mảnh vườn, và cậu Vàng.}'),
 dict(type='stage', label='CẬU VÀNG', bg='village',
      cast=[dict(c='laohac', x=330, D=175, expr='happy')],
      icons=[dict(icon='dog', x=760, y=1170, s=1.3, at=0), dict(icon='bowl', x=640, y=1225, s=.8, at=1)],
      say='Lão gọi nó là cậu Vàng. Lão bắt rận cho nó, đem nó ra ao tắm, ăn gì cũng chia cho nó. // Rồi lão ngồi nói chuyện với nó, như nói với một đứa cháu nhỏ về bố của nó.'),
 dict(type='stage', label='ỐM, BÃO, HẾT VIỆC', bg='room',
      cast=[dict(c='laohac', x=540, D=180, expr='sad')],
      cards=[dict(t='ỐM MỘT TRẬN DÀI', x=540, y=1090, at=0, col='#4a4038', tc='#fff', fs=28), dict(t='BÃO PHÁ SẠCH HOA MÀU', x=540, y=1170, at=1, col='#4a4038', tc='#fff', fs=28), dict(t='GẠO CỨ ĐẮT LÊN', x=540, y=1250, at=2, col='#4a4038', tc='#fff', fs=28)],
      say='Rồi lão ốm một trận dài, ốm xong thì yếu hẳn. Một trận bão phá sạch hoa màu trong vườn. Làng hết việc, gạo thì cứ đắt lên. // {hạ: Mỗi ngày, lão phải lo cơm cho cả mình lẫn con chó.}'),
 dict(type='ke', label='ANH EM CHỌN GÌ?', board='PHẦN CỦA CON|HAY CHÓ?', expr='normal', ask=True, gap=1.2,
      say='Lão vẫn còn mảnh vườn và chút tiền để dành. Nhưng vườn với tiền ấy, lão coi là phần của con. {cao: Nếu anh em là lão Hạc, tiêu vào phần của con, hay bán con chó của con?} [nghỉ 1.2]'),
 dict(type='stage', label='SANG NHÀ ÔNG GIÁO', bg='room',
      cast=[dict(c='onggiao', x=320, D=175, expr='surprised'), dict(c='laohac', x=780, D=175, face=-1, expr='sad', at=1, **{'from': 1300})],
      cards=[dict(t='"CẬU VÀNG ĐI ĐỜI RỒI"', x=540, y=1150, at=3, col='#c4281f', tc='#fff', fs=30)],
      say='Lão chọn bán cậu Vàng. // Rồi lão sang nhà ông giáo, người hàng xóm hay chữ. Vừa thấy ông giáo, lão báo ngay. /// {nhấn: Cậu Vàng đi đời rồi, ông giáo ạ!}'),
 dict(type='stage', label='CƯỜI NHƯ MẾU', bg='room',
      cast=[dict(c='laohac', x=540, D=195, expr='sad')],
      say='Lão cố cười, mà trông như mếu. Gương mặt già nhăn nhúm lại, nước mắt trào ra. /// {chậm: Rồi lão khóc hu hu như một đứa trẻ.}'),
 dict(type='stage', label='LÃO KỂ LẠI', bg='village',
      cast=[dict(c='muc', x=300, D=170, expr='normal', at=2, **{'from': -250}), dict(c='xien', x=860, D=165, face=-1, expr='normal', at=3, **{'from': 1350})],
      icons=[dict(icon='dog', x=580, y=1170, s=1.2, at=0), dict(icon='bowl', x=700, y=1225, s=.8, at=1)],
      say='Lão kể lại. Hôm ấy, lão gọi cậu Vàng về ăn cơm như mọi ngày. /// {nhanh: Thằng Mục nấp sẵn sau lưng nó, tóm hai chân sau, dốc ngược lên.} Rồi Mục với Xiên trói chặt bốn chân.'),
 dict(type='stage', label='CÁI NHÌN', bg='village',
      icons=[dict(icon='dog_tied', x=540, y=1150, s=1.6, at=0)],
      say='Lúc ấy nó mới biết. Nó ư ử, nhìn lão. /// {hạ: Cái nhìn như trách: nó tin lão thế, sao lão nỡ lừa nó.}'),
 dict(type='stage', label='LÃO TỰ TRÁCH', bg='paper',
      cast=[dict(c='laohac', x=540, D=180, expr='sad')],
      cards=[dict(t='LÃO ĐÃ LỪA NÓ', x=540, y=1150, at=0, col='#c4281f', tc='#fff', fs=30)],
      say='Lão khóc vì chuyện ấy. // Lão tự trách mình già rồi, còn đi lừa một con chó tin mình.'),
 dict(type='stage', label='CÁI NGHÈO', bg='riverbank_dawn',
      cast=[dict(c='contrai', x=760, D=150, face=-1, expr='sad')],
      icons=[dict(icon='dog_sad', x=330, y=1170, s=1.3, at=0)],
      say='Mà con chó ấy đâu phải của lão. Nó là của đứa con trai, sống sót vì đám cưới đổ bể. // Cái nghèo làm hỏng đám cưới đã tha cho nó một lần. /// {hạ: Giờ cũng chính cái nghèo ấy bắt nó đi.}'),
 dict(type='stage', label='KIẾP CHÓ, KIẾP NGƯỜI', bg='room',
      cast=[dict(c='onggiao', x=320, D=175, expr='sad'), dict(c='laohac', x=780, D=175, face=-1, expr='sad')],
      say='Ông giáo an ủi: giết nó là hóa kiếp cho nó đấy. // Lão Hạc đáp, giọng chua chát. {chậm: Hóa kiếp làm người, nhưng kiếp người như lão thì sướng gì hơn?}'),
 dict(type='stage', label='NGOÀI SÁCH: LÀNG ĐẠI HOÀNG', bg='village',
      cast=[dict(c='trumsan', x=360, D=175, expr='normal')],
      icons=[dict(icon='dog', x=790, y=1170, s=1.2, at=1)],
      say='Chuyện ngoài sách. Ở làng Đại Hoàng, quê Nam Cao, người làng kể nguyên mẫu lão Hạc là ông Trùm San. // Nhà ông ngay cạnh nhà văn. Ông nghèo, cũng nuôi một con chó vàng. Con trai ông cũng bỏ làng vào Nam làm cao su. /// {hạ: Nỗi đau ấy, Nam Cao thấy ngay bên kia hàng rào.}'),
 dict(type='ke', label='PHẦN SAU', board='PHẦN 2|BINH TƯ', expr='normal',
      say='{cao: Nếu anh con trai trở về, biết cha đã bán con chó, anh sẽ trách hay thương?} [nghỉ 1.0] Bình luận nhé. // Phần sau, lão nhờ ông giáo giữ hộ hai thứ. Rồi lão sang xin Binh Tư một món, làm ông giáo nghi ngờ. Theo dõi Liên Thiên để xem nhé.'),
]
NAMES = ['Lão Hạc', 'Mục', 'Xiên', 'Nam Cao', 'Chí Phèo', 'Liên Thiên', 'Đại Hoàng', 'Trùm San', 'Binh Tư', 'cậu Vàng', 'Cậu Vàng']
def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    return x
for s in S: s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='LIÊN THIÊN – LÃO HẠC', badge='PHẦN 1/2', hook_text='MUA VỀ ĐỂ GIẾT THỊT',
          next='Phần sau: Lão Hạc P2', cta='THEO DÕI LIÊN THIÊN', tts=True, speed=0.9, tag='lt-lh1', cast=CAST, shots=S)
json.dump(sp, open(os.path.join(OUT, 'spec.json'), 'w'), ensure_ascii=False)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'editor'))
t = json.loads(json.dumps(sp)); t['tts'] = False
B = lambda x: re.sub(r'\s+', ' ', re.sub(r'(^|\s)/{1,3}(?=\s|$)', ' ', re.sub(r'\{(?:chậm|rất chậm|nhấn|hạ|nhanh|cao)\s*:\s*', '', re.sub(r'\[nghỉ\s*[\d.,]+\s*\]', ' ', x)).replace('}', ''))).strip()
for s in t['shots']:
    n = [x for x in re.split(r'(?<=[.?!…])\s+', B(s['say'])) if x]; d = 0.0; se = []
    for x in n: se.append(round(d, 2)); d += .32 * len(x.split()) + .3
    s['dur'] = d + 1.0; s['_sent'] = se
t['durs'] = [s['dur'] for s in t['shots']]
json.dump(t, open(os.path.join(OUT, 'spec_t.json'), 'w'), ensure_ascii=False)
print(len(S), 'canh', sum(len(B(s['say']).split()) for s in S), 'tu', round(sum(t['durs']) / .9), 's')
