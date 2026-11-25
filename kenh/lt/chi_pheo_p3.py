"""LIÊN THIÊN – Chí Phèo (Nam Cao), PHẦN 3/3: bà cô ngăn cản -> Thị Nở dứt tình -> "Ai cho tao lương thiện?" -> kết (kể nhẹ) -> lò gạch cũ.
python3 chi_pheo_p3.py <thu_muc_ra> -> spec.json + spec_t.json (bản soát). Số viết bằng chữ số trong 'say' (máy tự đọc).
Ký hiệu nhịp chỉ đặt SAU dấu câu hoặc bọc cả câu (W87 v3.1).
Hook: khuôn H (lật nghĩa "Bạn tưởng… thật ra…"), dựa trên chi tiết trong truyện: Chí "càng uống càng tỉnh".
Ngoài lề (≥ 2 nguồn): Nam Cao hy sinh 30/11/1951, 36 tuổi, bị quân Pháp giết trên đường công tác vùng địch hậu
(Đại Đoàn Kết 28/10/2023; Nhân Dân "Nhặt từ sách" – hồi ký Hoàng Trung Thông; Wikipedia: ambushed, age 36;
Tiền Phong 15/3/2008 – giỗ 30/11); mộ thất lạc, mãi sau mới tìm được hài cốt đưa về quê (Đại Đoàn Kết: năm 1996;
Tiền Phong 2008: "cách đây đúng mười năm… tìm được hài cốt cha tôi") -> chỉ nói "hơn 40 năm".
Trích nguyên văn duy nhất: "Ai cho tao lương thiện?" (4 từ).
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CAST = {
    'bakien': dict(tag='BÁ KIẾN', skin='#e6b48a', hair='#1b1512', hair_style='khan', hat='#1a1a1a', outfit='#2b2b36', outfit2='#1c1c24', trim='#b8963e', w=1.25, beard=True),
    'cothino': dict(tag='BÀ CÔ THỊ NỞ', skin='#d8a87c', hair='#8a8a8a', hair_style='bun', outfit='#4a4038', outfit2='#342c26', trim='#342c26', mark='brow'),
}
S = [
 dict(type='drunk', label='',
      say='{cao: Anh em tưởng Chí Phèo say rượu nên mới cầm dao?} /// Thật ra, hôm ấy càng uống, hắn càng tỉnh. // {chậm: Và tỉnh ra mới là lúc đáng sợ nhất.}'),
 dict(type='ke', label='PHẦN TRƯỚC', board='BÁT CHÁO|HÀNH', expr='normal',
      say='{nhanh: Phần trước, sau bát cháo hành của Thị Nở, Chí Phèo bỗng thèm được làm người lương thiện.} Hắn rủ Thị về ở chung một nhà. // Thị bảo phải về hỏi bà cô đã. /// Hôm nay, bà cô trả lời.'),
 dict(type='stage', label='BÀ CÔ MẮNG', bg='village',
      cast=[dict(c='cothino', x=330, D=180, expr='angry'), dict(c='thino', x=790, D=150, face=-1, expr='happy', **{'from': 1300})],
      cards=[dict(t='ĐI LẤY THẰNG CHÍ PHÈO?', x=540, y=640, at=1, col='#c4281f', tc='#fff', fs=38)],
      say='Thị Nở hớn hở về kể với bà cô. Bà cô nghe xong thì mắng xối xả. Thị đã lỡ thì, ế chồng thì thôi. Ai lại đi lấy một thằng chỉ có nghề rạch mặt ăn vạ.'),
 dict(type='stage', label='CÁI TIẾNG', bg='paper',
      cast=[dict(c='chipheo', x=540, D=170, expr='sad')],
      cards=[dict(t='QUỶ DỮ', x=540, y=1090, at=1, col='#c4281f', tc='#fff', fs=28), dict(t='RẠCH MẶT', x=540, y=1170, at=1, col='#c4281f', tc='#fff', fs=28), dict(t='ĂN VẠ', x=540, y=1250, at=1, col='#c4281f', tc='#fff', fs=28)],
      say='Bà cô không hỏi Chí bây giờ ra sao. Bà chỉ nhìn cái tiếng mà cả làng đã dán lên người hắn. // Và cái tiếng ấy, không bát cháo nào rửa sạch được.'),
 dict(type='stage', label='THỊ NỞ QUAY LẠI', bg='riverbank_dawn',
      cast=[dict(c='chipheo', x=320, D=175, expr='surprised'), dict(c='thino', x=780, D=165, face=-1, expr='angry', at=1, **{'from': 1300})],
      say='Thị Nở hằm hằm quay lại, trút hết lời bà cô lên đầu Chí. Hắn ngẩn người, đưa tay níu lại. /// {nhanh: Thị gạt phắt ra, rồi bỏ về.}'),
 dict(type='drunk', label='CÀNG UỐNG CÀNG TỈNH',
      say='Hắn lại tìm đến rượu. Nhớ không, cụ Bá từng dập cơn chửi của Chí bằng một chén rượu. Bao năm, rượu giúp hắn quên mình là ai. /// {chậm: Lần này, càng uống hắn càng tỉnh.}'),
 dict(type='stage', label='MÙI CHÁO HÀNH', bg='room',
      cast=[dict(c='chipheo', x=540, D=185, expr='sad', hands=[[.6, -.15, 'bowl']])],
      say='Hơi rượu không át được nữa. Hắn chỉ còn thoảng thấy mùi cháo hành. // {hạ: Rồi hắn ôm mặt, khóc rưng rức.}'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='TỈNH TÁO|CỨU HAY GIẾT?', expr='normal', ask=True, gap=1.2,
      say='Anh em thử nghĩ. Nếu hôm ấy Chí say khướt như mọi lần, có khi hắn ngủ một giấc rồi quên hết. {cao: Vậy cái tỉnh táo ấy cứu hắn, hay giết hắn?} [nghỉ 1.2]'),
 dict(type='stage', label='XÁCH DAO RA ĐƯỜNG', bg='village',
      cast=[dict(c='chipheo', x=540, D=185, expr='angry', hands=[[.7, -.1, 'sword', 20]])],
      say='Hắn giắt dao, đi ra đường. Miệng lầm bầm sẽ đến nhà bà cô Thị Nở. /// Nhưng chân hắn không rẽ vào đó. // {chậm: Nó đưa hắn thẳng tới cổng nhà cụ Bá.}'),
 dict(type='stage', label='VÌ SAO LÀ CỤ BÁ?', bg='paper',
      cast=[dict(c='bakien', x=540, D=175, expr='happy')],
      cards=[dict(t='GHEN → ĐẨY ĐI TÙ', x=540, y=1090, at=2, col='#c4281f', tc='#fff', fs=28), dict(t='RƯỢU + ĐỒNG BẠC', x=540, y=1170, at=2, col='#c4281f', tc='#fff', fs=28), dict(t='TAY SAI', x=540, y=1250, at=2, col='#c4281f', tc='#fff', fs=28)],
      say='Vì sao lại là cụ Bá? Tỉnh ra, Chí lần ngược lại đời mình. Bà cô chỉ nhắc lại cái tiếng. Kẻ ghen mà đẩy hắn vào tù, rồi mua hắn bằng rượu và đồng bạc, là cụ Bá. /// {hạ: Say thì chân đi lung tung. Tỉnh thì chân biết đúng đường.}'),
 dict(type='stage', label='NHÀ CỤ BÁ', bg='room',
      cast=[dict(c='bakien', x=320, D=180, expr='happy'), dict(c='chipheo', x=780, D=180, face=-1, expr='angry', at=1, **{'from': 1300})],
      say='Cụ Bá cứ tưởng Chí lại đến xin tiền như mọi lần. /// Nhưng lần này, Chí không xin.'),
 dict(type='stage', label='CÂU HỎI CỦA CHÍ', bg='paper',
      cast=[dict(c='chipheo', x=540, D=190, expr='angry')],
      cards=[dict(t='AI CHO TAO LƯƠNG THIỆN?', x=540, y=1180, at=2, col='#c4281f', tc='#fff', fs=28)],
      say='Hắn chỉ thẳng vào mặt cụ Bá. Hắn nói hắn muốn làm người lương thiện. Rồi hắn hỏi. /// {nhấn: Ai cho tao lương thiện?} // Làm sao xóa được những vết sẹo trên mặt này?'),
 dict(type='silence', label='CẢ LÀNG',
      say='Câu hỏi ấy không chỉ dành cho cụ Bá. Nó hỏi cả làng Vũ Đại, những người đã đóng cửa trước mặt hắn. /// {hạ: Cánh cửa lương thiện, chính họ đã khóa lại.}'),
 dict(type='stage', label='KẾT THÚC', bg='village_night',
      cards=[dict(t='HẾT', x=540, y=700, at=1, col='#1a1a1a', tc='#fff', fs=46)],
      say='Rồi mọi chuyện kết thúc rất nhanh. Chí vung dao. Cụ Bá chết, và Chí cũng tự kết liễu đời mình. // {hạ: Cả làng xôn xao, có người còn thầm mừng.}'),
 dict(type='kiln', label='CÁI LÒ GẠCH CŨ',
      say='Còn Thị Nở, nghe tin, thị nhìn nhanh xuống bụng mình. Thị chợt nhớ đến cái lò gạch cũ bỏ hoang. /// {chậm: Nơi năm xưa, người ta nhặt được Chí.} // Nhớ phần 1 không? Cái tên đầu tiên Nam Cao đặt cho truyện là Cái lò gạch cũ. /// {hạ: Đến đây mới hiểu vì sao. Một Chí Phèo mới có khi lại sắp ra đời.}'),
 dict(type='writer', label='CHUYỆN NGOÀI SÁCH',
      say='Nam Cao viết Chí Phèo năm 1941, khi mới ngoài 20 tuổi. Mười năm sau, ngày 30/11/1951, ông bị quân Pháp giết trên đường đi công tác, lúc mới 36 tuổi. /// {hạ: Mộ ông thất lạc hơn 40 năm, mãi sau này mới được tìm thấy và đưa về quê.}'),
 dict(type='ke', label='HẾT CHÍ PHÈO', board='TẬP SAU|LÃO HẠC', expr='normal',
      say='{cao: Theo anh em, ai mới thật sự giết Chí Phèo?} [nghỉ 1.0] Bình luận nhé. // Tập sau, Liên Thiên kể Lão Hạc, và vì sao một ông lão bán chó lại khóc như con nít. Theo dõi Liên Thiên để xem nhé.'),
]
NAMES = ['Chí Phèo', 'Bá Kiến', 'Thị Nở', 'Vũ Đại', 'Nam Cao', 'Lão Hạc', 'Liên Thiên']
def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    return x
for s in S: s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='LIÊN THIÊN – CHÍ PHÈO', badge='PHẦN 3/3', hook_text='CHÍ PHÈO KHÔNG HỀ SAY',
          next='Tập sau: Lão Hạc', cta='THEO DÕI LIÊN THIÊN', tts=True, speed=0.9, tag='lt-cp3', cast=CAST, shots=S)
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
