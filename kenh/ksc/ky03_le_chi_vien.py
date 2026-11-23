import json, re
# KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ, kỳ 3: Vụ án Lệ Chi Viên (1442) – hạt nhân: người minh oan (Tư Thành) chào đời ~2 tuần trước đêm vườn vải.
# Số viết bằng chữ số trong 'say' (máy tự đổi số -> chữ cho giọng, phụ đề giữ số).
NAMES = ['Lê Thái Tông', 'Thái Tông', 'Nguyễn Trãi', 'Nguyễn Thị Lộ', 'Thị Lộ', 'Nguyễn Thị Anh', 'Thị Anh', 'Bang Cơ',
         'Lệ Chi Viên', 'Lệ Chi', 'Côn Sơn', 'Chí Linh', 'Gia Bình', 'Bắc Ninh', 'Bình Ngô đại cáo',
         'Phạm Thị Mẫn', 'Nguyễn Anh Vũ', 'Anh Vũ', 'Lê Thánh Tông', 'Ức Trai', 'Lê Nghi Dân', 'Nghi Dân', 'Trịnh Khả', 'Tán Trù bá',
         'Ngô Thị Ngọc Dao', 'Ngọc Dao', 'Tư Thành', 'Ngô Sĩ Liên', 'Lê Long Đĩnh', 'Long Đĩnh', 'Ngọa Triều', 'Lam Sơn']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


CAST = {
    'lethaitong': dict(tag='LÊ THÁI TÔNG', skin='#f0c49c', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f'),
    'nguyentrai': dict(tag='NGUYỄN TRÃI', skin='#e2ae80', hair='#e8e4da', hair_style='khan', hat='#1a1a1a', outfit='#2e4a6a', outfit2='#22384e', trim='#d8a93a', beard=True),
    'thilo': dict(tag='NGUYỄN THỊ LỘ', skin='#f0c8a0', hair='#140f0c', hair_style='bun', outfit='#2e7a74', outfit2='#225a56', trim='#d8a93a'),
    'thianh': dict(tag='NGUYỄN THỊ ANH', skin='#ecc09a', hair='#140f0c', hair_style='mien', outfit='#7a1f3a', outfit2='#56142a', trim='#d8a93a', mark='brow'),
    'bangco': dict(tag='BANG CƠ', skin='#f4cca6', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f'),
    'thanhtong': dict(tag='LÊ THÁNH TÔNG', skin='#ecb88a', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#2e4a6a', mark='brow'),
    'phamthiman': dict(tag='PHẠM THỊ MẪN', skin='#f0c8a0', hair='#140f0c', hair_style='bun', outfit='#8a3a5a', outfit2='#6a2a44', trim='#d8a93a'),
    'trinhkha': dict(tag='TRỊNH KHẢ', skin='#d9a070', hair='#d8d4ca', hair_style='khan', hat='#1a1a1a', outfit='#5a3a6a', outfit2='#44284e', trim='#d8a93a', beard=True),
    'ngocdao': dict(tag='NGÔ THỊ NGỌC DAO', skin='#f2caa4', hair='#140f0c', hair_style='bun', outfit='#c4703a', outfit2='#9a5228', trim='#d8a93a', mark='mole'),
    'nghidan': dict(tag='LÊ NGHI DÂN', skin='#d9a070', hair='#140f0c', hair_style='topknot', outfit='#3a3a4a', outfit2='#2a2a36', trim='#c4281f', mark='scar'),
    'anhvu': dict(tag='NGUYỄN ANH VŨ', skin='#ecb88a', hair='#140f0c', hair_style='khan', hat='#1a1a1a', outfit='#2e5a46', outfit2='#224436', trim='#d8a93a'),
}
G = 1290  # mat dat canh stage (GY + 40)

S = [
 dict(type='stage', bg='lychee', label='', zoom=1.12,
      cast=[dict(c='nguyentrai', x=300, D=165, face=1, expr='scared'), dict(c='lethaitong', x=790, D=150, face=-1, expr='normal', at=2)],
      cards=[dict(t='TRU DI 3 HỌ', x=540, y=700, at=1, col='#c4281f', tc='#fff'), dict(t='VƯỜN VẢI, 1442', x=540, y=830, at=2, col='#f2dc8a')],
      say='Nguyễn Trãi bị xử chém cả 3 họ. Người sau này minh oan cho ông… lúc ấy chưa đầy 1 tháng tuổi. Tất cả bắt đầu từ một đêm ở vườn vải, năm 1442.'),
 dict(type='ke', label='AI GIẾT VUA?', board='AI GIẾT VUA?|ĐỨA BÉ LÀ AI?', expr='surprised', ask=True, gap=1.2,
      say='Đêm ấy vua chết. Một ông già 62 tuổi bị khép tội giết vua. Còn đứa bé kia là ai? Và vì sao phải đợi nó lớn?'),
 dict(type='stage', bg='pagoda', label='CÔN SƠN, CHÍ LINH',
      cast=[dict(c='nguyentrai', x=330, D=175, face=1, expr='normal', hands=[[.6, -.2, 'book']])],
      cards=[dict(t='BÌNH NGÔ ĐẠI CÁO', x=330, y=720, at=0, col='#f2dc8a', fs=40)],
      say='Nguyễn Trãi, người viết Bình Ngô đại cáo, lúc ấy đã xin về ở ẩn. Ông lui về Côn Sơn, đất Chí Linh. Không binh quyền, không phe cánh.'),
 dict(type='stage', bg='hall', label='BÀ THỊ LỘ',
      cast=[dict(c='lethaitong', x=760, D=150, face=-1, expr='happy'), dict(c='thilo', x=300, D=160, face=1, expr='happy', at=1)],
      cards=[dict(t='LỄ NGHI HỌC SĨ', x=300, y=720, at=2, col='#2e7a74', tc='#fff')],
      say='Bên ông có bà Nguyễn Thị Lộ, người vợ lẽ giỏi văn chương. Vua mến tài, vời bà vào cung. Phong cho bà chức lễ nghi học sĩ.'),
 dict(type='stage', bg='hall', label='THÁNG 7 ÂM LỊCH',
      cast=[dict(c='ngocdao', x=420, D=165, face=1, expr='happy')],
      cards=[dict(t='TƯ THÀNH CHÀO ĐỜI', x=540, y=720, at=1, col='#f2dc8a', fs=42), dict(t='NGÀY 20/7 ÂM LỊCH', x=540, y=850, at=1, col='#1a1a1a', tc='#fff', fs=38)],
      say='Còn trong cung, tháng 7 âm lịch năm ấy, bà Ngô Thị Ngọc Dao sinh một con trai, tên Tư Thành. Anh em nhớ cái tên này nhé.'),
 dict(type='stage', bg='pagoda', label='DUYỆT QUÂN',
      cast=[dict(c='nguyentrai', x=260, D=165, face=1, expr='happy'), dict(c='lethaitong', x=760, D=150, face=-1, expr='happy', from_=1300, at=1)],
      say='Ít ngày sau, vua đi tuần miền đông, duyệt quân ở Chí Linh. Trên đường, vua ghé chùa Côn Sơn. Nguyễn Trãi ra đón.'),
 dict(type='stage', bg='lychee', label='LỆ CHI VIÊN',
      cast=[dict(c='lethaitong', x=780, D=150, face=-1, expr='happy'), dict(c='thilo', x=330, D=160, face=1, expr='normal', at=0)],
      cards=[dict(t='NGÀY 4/8 ÂM LỊCH', x=540, y=700, at=1, col='#f2dc8a')],
      say='Bà Lộ theo hầu vua. Ngày 4/8 âm lịch, đoàn dừng ở Lệ Chi Viên, tức vườn vải. Nay thuộc đất Bắc Ninh.'),
 dict(type='stage', bg='lychee_dawn', label='SÁNG HÔM SAU', zoom=1.1,
      cast=[dict(c='thilo', x=300, D=160, face=1, expr='scared', at=1), dict(c='quan', x=820, D=165, face=-1, expr='surprised', at=2)],
      cards=[dict(t='VUA BĂNG', x=540, y=710, at=2, col='#1a1a1a', tc='#fff')],
      say='Sử chép, đêm ấy vua bị bệnh. Bà Lộ thức suốt đêm hầu vua. Rồi vua băng, chưa tròn 20 tuổi.'),
 dict(type='stage', bg='hall_empty', label='ĐỔ TỘI',
      cast=[dict(c='thilo', x=540, D=160, face=1, expr='scared'), dict(c='quan', x=180, D=160, face=1, expr='angry', at=0), dict(c='quan', x=900, D=160, face=-1, expr='angry', at=0, tag=False)],
      cards=[dict(t='GIẾT VUA?', x=540, y=710, at=0, col='#c4281f', tc='#fff')],
      say='Triều đình nói bà Lộ giết vua. Mà bà là vợ lẽ của Nguyễn Trãi. Thế là ông bị kéo theo.'),
 dict(type='stage', bg='paper', label='NGÀY 16/8 ÂM LỊCH',
      cast=[dict(c='nguyentrai', x=760, D=180, face=-1, expr='sad')],
      cards=[dict(t='12 NGÀY', x=330, y=720, at=0, col='#f2dc8a'), dict(t='TRU DI TAM TỘC', x=330, y=860, at=1, col='#c4281f', tc='#fff', fs=46)],
      say='Ngày 16/8 âm lịch, chỉ 12 ngày sau. Nguyễn Trãi bị xử tru di tam tộc. Một vụ giết vua, xử xong chưa đầy nửa tháng.'),
 dict(type='timeline', label='AI ĐƯỢC LỢI?',
      points=[dict(y='1440', t='NGHI DÂN: THÁI TỬ', at=0), dict(y='1441', t='NGHI DÂN BỊ PHẾ', at=1), dict(y='1441', t='BANG CƠ: THÁI TỬ', at=2), dict(y='1442', t='VUA BĂNG', at=3)],
      say='Giờ hỏi ngược lại: vua chết thì ai được lợi? Năm 1440, thái tử là Nghi Dân, con trưởng. Năm 1441, Nghi Dân bị phế. Ngôi thái tử về tay Bang Cơ, mới vài tháng tuổi.'),
 dict(type='stage', bg='hall', label='AI LÊN NGÔI?', zoom=1.1,
      cast=[dict(c='bangco', x=540, y=1010, D=100, face=1, expr='happy', at=0), dict(c='thianh', x=830, D=165, face=-1, expr='normal', at=1)],
      say='Vua chết, Bang Cơ lên ngôi khi chưa đầy 2 tuổi. Người cầm quyền thật là mẹ cậu, bà Nguyễn Thị Anh.'),
 dict(type='stage', bg='hall_dim', label='GIẢ THUYẾT', zoom=1.1,
      cast=[dict(c='thianh', x=700, D=175, face=-1, expr='angry'), dict(c='bangco', x=380, D=100, face=1, expr='normal', tag=False)],
      cards=[dict(t='AI ĐỨNG SAU?', x=540, y=720, at=0, col='#c4281f', tc='#fff')],
      say='Nhiều nhà nghiên cứu nghi chính bà đứng sau vụ án. Dẹp người có tiếng nói, để con mình ngồi yên trên ngai.'),
 dict(type='stage', bg='hall_dim', label='NĂM 1451',
      cast=[dict(c='thianh', x=780, D=170, face=-1, expr='angry'), dict(c='trinhkha', x=300, D=170, face=1, expr='scared', at=1)],
      cards=[dict(t='LÝ DO: SỬ KHÔNG RÕ', x=540, y=720, at=2, col='#1a1a1a', tc='#fff', fs=40)],
      say='Năm 1451, đến lượt Trịnh Khả, một công thần Lam Sơn. Ông bị giết cùng con trai. Sử không chép rõ vì sao. Nhiều người lại nghi bà đứng sau.'),
 dict(type='stage', bg='paper', label='CÓ THẬT KHÔNG?',
      cast=[dict(c='ngosilien', x=820, D=170, face=-1, expr='normal', hands=[[.6, -.3, 'pen']])],
      cards=[dict(t='BỊ HẠI?', x=340, y=720, at=0, col='#c4281f', tc='#fff', fs=40), dict(t='HAY BẠO BỆNH?', x=340, y=860, at=1, col='#2a4a7a', tc='#fff', fs=40)],
      say='Nhưng khoan kết luận. Có người cho rằng vua chết vì bệnh. Sử gia Ngô Sĩ Liên tin Nguyễn Trãi oan. Nhưng ông vẫn nghi bà Lộ.'),
 dict(type='stage', bg='village', label='MỘT NGƯỜI THOÁT',
      cast=[dict(c='phamthiman', x=420, D=160, face=1, expr='scared', from_=-150, at=1)],
      cards=[dict(t='TƯƠNG TRUYỀN', x=420, y=720, at=0, col='#f2dc8a', fs=40)],
      say='Nhà Nguyễn Trãi chưa tuyệt. Tương truyền, bà Phạm Thị Mẫn, một người vợ của ông, trốn thoát khi đang mang thai. Đứa con ấy là Nguyễn Anh Vũ.'),
 dict(type='stage', bg='hall_dim', label='NĂM 1459', zoom=1.1,
      cast=[dict(c='nghidan', x=330, D=170, face=1, expr='angry', hands=[[.6, -.2, 'sword']]), dict(c='thianh', x=800, D=165, face=-1, expr='scared', at=1)],
      say='Năm 1459, Nghi Dân đem người vào cung lúc nửa đêm. Bang Cơ bị giết. Bà Thị Anh cũng không thoát.'),
 dict(type='stage', bg='hall', label='NGƯỜI LÊN NGÔI', zoom=1.12,
      cast=[dict(c='thanhtong', x=540, D=165, face=1, expr='normal', at=1)],
      cards=[dict(t='TƯ THÀNH = LÊ THÁNH TÔNG', x=540, y=720, at=1, col='#f2dc8a', fs=38)],
      say='Chưa đầy một năm sau, Nghi Dân bị lật. Người được đưa lên ngôi… chính là cậu bé Tư Thành năm nào. Tức vua Lê Thánh Tông.'),
 dict(type='stage', bg='hall', label='NĂM 1464',
      cast=[dict(c='thanhtong', x=760, D=160, face=-1, expr='normal'), dict(c='anhvu', x=300, D=150, face=1, expr='happy', at=1)],
      cards=[dict(t='TÁN TRÙ BÁ', x=330, y=720, at=1, col='#2a7a4a', tc='#fff')],
      say='Năm 1464, vua minh oan cho Nguyễn Trãi. Truy tặng tước Tán Trù bá. Cho con ông, Nguyễn Anh Vũ, ra làm quan.'),
 dict(type='stage', bg='lychee', label='PHÁN XỬ', ask=True, gap=1.2, qx=880,
      cast=[dict(c='thilo', x=720, D=165, face=-1, expr='sad')],
      cards=[dict(t='NGUYỄN TRÃI: OAN', x=330, y=720, at=0, col='#2a7a4a', tc='#fff', fs=38), dict(t='BÀ LỘ: ?', x=330, y=860, at=1, col='#c4281f', tc='#fff')],
      say='Nhưng bà Lộ thì chưa từng được minh oan. Thủ phạm thật là ai, sử cũng im lặng. Bà Lộ giết vua, hay chỉ là người gánh tội thay?'),
 dict(type='ke', label='KỲ SAU', board='NĂM 1005|NGỌA TRIỀU', expr='happy',
      say='Anh em bình luận nhé. Kỳ sau: năm 1005, một hoàng tử giết anh để cướp ngôi. Sử gọi ông là vua Ngọa Triều. Nhưng có thật ông nằm mà thiết triều?'),
]
for s in S:
    for c in s.get('cast', []):
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 3', hook_text='AI GIẾT VUA Ở VƯỜN VẢI?',
          next='Kỳ sau: Lê Long Đĩnh – vua Ngọa Triều', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian3', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
