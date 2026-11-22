import json, re
# KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ, kỳ 3 (BẢN NHÁP, QC 23/11 được 6/10 – cần thêm hạt nhân): Vụ án Lệ Chi Viên (1442).
# Số viết bằng chữ số trong 'say' (máy tự đổi số -> chữ cho giọng, phụ đề giữ số).
NAMES = ['Lê Thái Tông', 'Thái Tông', 'Nguyễn Trãi', 'Nguyễn Thị Lộ', 'Thị Lộ', 'Nguyễn Thị Anh', 'Thị Anh', 'Bang Cơ',
         'Lệ Chi Viên', 'Lệ Chi', 'Côn Sơn', 'Chí Linh', 'Gia Bình', 'Bắc Ninh', 'Bình Ngô đại cáo',
         'Phạm Thị Mẫn', 'Nguyễn Anh Vũ', 'Anh Vũ', 'Lê Thánh Tông', 'Ức Trai', 'Lê Nghi Dân', 'Nghi Dân', 'Trịnh Khả', 'Tán Trù bá']


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
    'anhvu': dict(tag='NGUYỄN ANH VŨ', skin='#ecb88a', hair='#140f0c', hair_style='khan', hat='#1a1a1a', outfit='#2e5a46', outfit2='#224436', trim='#d8a93a'),
}
G = 1290  # mat dat canh stage (GY + 40)

S = [
 dict(type='stage', bg='lychee', label='', zoom=1.12,
      cast=[dict(c='lethaitong', x=760, D=150, face=-1, expr='normal'), dict(c='nguyentrai', x=260, D=165, face=1, expr='scared', at=2)],
      cards=[dict(t='VƯỜN VẢI, 1442', x=540, y=700, at=1, col='#f2dc8a')],
      say='Một ông vua chưa tròn 20 tuổi chết sau một đêm, trong vườn vải. Năm ấy là 1442. Và người bị khép tội giết vua… lại là Nguyễn Trãi.'),
 dict(type='ke', label='AI CẦN VUA CHẾT?', board='AI CẦN|VUA CHẾT?', expr='surprised', ask=True, gap=1.2,
      say='Lúc ấy ông đã xin về ở ẩn. Không binh quyền, cũng chẳng có ai để đưa lên ngai. Anh em thử nghĩ xem. Ai mới là người cần vua chết?'),
 dict(type='stage', bg='pagoda', label='CÔN SƠN, CHÍ LINH',
      cast=[dict(c='nguyentrai', x=330, D=175, face=1, expr='normal', hands=[[.6, -.2, 'book']])],
      cards=[dict(t='BÌNH NGÔ ĐẠI CÁO', x=330, y=720, at=0, col='#f2dc8a', fs=40)],
      say='Nguyễn Trãi, người viết Bình Ngô đại cáo, lúc ấy đã ngoài 60. Ông lui về Côn Sơn, đất Chí Linh.'),
 dict(type='stage', bg='hall', label='BÀ THỊ LỘ',
      cast=[dict(c='lethaitong', x=760, D=150, face=-1, expr='happy'), dict(c='thilo', x=300, D=160, face=1, expr='happy', at=1)],
      cards=[dict(t='LỄ NGHI HỌC SĨ', x=300, y=720, at=2, col='#2e7a74', tc='#fff')],
      say='Bên ông có bà Nguyễn Thị Lộ, người thiếp giỏi văn chương. Vua mến tài, vời bà vào cung. Phong cho bà chức lễ nghi học sĩ.'),
 dict(type='stage', bg='pagoda', label='THÁNG 7 ÂM LỊCH',
      cast=[dict(c='nguyentrai', x=260, D=165, face=1, expr='happy'), dict(c='lethaitong', x=520, D=150, face=-1, expr='happy', from_=1300, at=1)],
      cards=[dict(t='DUYỆT QUÂN', x=300, y=720, at=0, col='#f2dc8a')],
      say='Tháng 7 âm lịch năm ấy, vua đi duyệt quân ở Chí Linh. Trên đường, vua ghé chùa Côn Sơn. Nguyễn Trãi ra đón.'),
 dict(type='stage', bg='lychee', label='LỆ CHI VIÊN',
      cast=[dict(c='lethaitong', x=780, D=150, face=-1, expr='happy'), dict(c='thilo', x=330, D=160, face=1, expr='normal', at=0)],
      cards=[dict(t='NGÀY 4/8 ÂM LỊCH', x=540, y=700, at=1, col='#f2dc8a')],
      say='Đi theo hầu vua là bà Lộ. Ngày 4/8 âm lịch, đoàn dừng lại ở Lệ Chi Viên, tức vườn vải. Nay thuộc Gia Bình, Bắc Ninh.'),
 dict(type='stage', bg='lychee_dawn', label='SÁNG HÔM SAU', zoom=1.1,
      cast=[dict(c='thilo', x=300, D=160, face=1, expr='scared', at=1), dict(c='quan', x=820, D=165, face=-1, expr='surprised', at=1)],
      cards=[dict(t='VUA BĂNG', x=540, y=710, at=2, col='#1a1a1a', tc='#fff')],
      say='Sử chép, đêm ấy bà Lộ thức hầu vua. Rồi trời sáng, vua không dậy nữa. Thi hài được đưa gấp về kinh.'),
 dict(type='stage', bg='hall_empty', label='ĐỔ TỘI',
      cast=[dict(c='thilo', x=540, D=160, face=1, expr='scared'), dict(c='quan', x=180, D=160, face=1, expr='angry', at=0), dict(c='quan', x=900, D=160, face=-1, expr='angry', at=0, tag=False)],
      cards=[dict(t='GIẾT VUA?', x=540, y=710, at=0, col='#c4281f', tc='#fff')],
      say='Cả triều đổ tội cho bà Lộ: chính bà giết vua. Mà bà là vợ lẽ của Nguyễn Trãi. Thế là ông bị kéo theo.'),
 dict(type='stage', bg='paper', label='NGÀY 16/8 ÂM LỊCH',
      cast=[dict(c='nguyentrai', x=760, D=180, face=-1, expr='sad')],
      cards=[dict(t='~12 NGÀY', x=330, y=720, at=0, col='#f2dc8a'), dict(t='TRU DI TAM TỘC', x=330, y=860, at=1, col='#c4281f', tc='#fff', fs=46), dict(t='HỌ CHA · HỌ MẸ · HỌ VỢ', x=540, y=1000, at=2, col='#1a1a1a', tc='#fff', fs=36)],
      say='Ngày 16/8 âm lịch, chỉ khoảng 12 ngày sau. Nguyễn Trãi bị xử tru di tam tộc. Tức là cả họ cha, họ mẹ, họ vợ. Một vụ giết vua, xử xong chưa đầy nửa tháng.'),
 dict(type='timeline', label='AI ĐƯỢC LỢI?',
      points=[dict(y='1440', t='NGHI DÂN: THÁI TỬ', at=0), dict(y='1441', t='NGHI DÂN BỊ PHẾ', at=1), dict(y='1441', t='BANG CƠ: THÁI TỬ', at=2), dict(y='1442', t='VUA BĂNG', at=3)],
      say='Giờ lùi lại 2 năm. Năm 1440, thái tử là Nghi Dân, con trưởng của vua. Năm 1441, Nghi Dân bị phế. Ngôi thái tử về tay Bang Cơ. Lúc ấy cậu mới được vài tháng tuổi.'),
 dict(type='stage', bg='hall', label='AI LÊN NGÔI?', zoom=1.1,
      cast=[dict(c='bangco', x=540, y=1010, D=100, face=1, expr='happy', at=0), dict(c='thianh', x=830, D=165, face=-1, expr='normal', at=1)],
      say='Một năm sau, vua chết. Bang Cơ lên ngôi khi chưa đầy 2 tuổi. Người cầm quyền thật… là mẹ cậu, bà Nguyễn Thị Anh.'),
 dict(type='stage', bg='hall_dim', label='GIẢ THUYẾT', zoom=1.1,
      cast=[dict(c='thianh', x=700, D=175, face=-1, expr='angry'), dict(c='bangco', x=380, D=100, face=1, expr='normal', tag=False)],
      cards=[dict(t='AI ĐỨNG SAU?', x=540, y=720, at=0, col='#c4281f', tc='#fff')],
      say='Nhiều nhà sử học nghi chính bà đứng sau vụ án. Dẹp những người có tiếng nói. Để con mình ngồi yên trên ngai.'),
 dict(type='stage', bg='hall_dim', label='NĂM 1451',
      cast=[dict(c='thianh', x=780, D=170, face=-1, expr='angry'), dict(c='trinhkha', x=300, D=170, face=1, expr='scared', at=1)],
      cards=[dict(t='THÊM MỘT CÔNG THẦN', x=540, y=720, at=1, col='#1a1a1a', tc='#fff', fs=40)],
      say='Và bà không dừng ở đó. Năm 1451, bà cho giết thêm một công thần Lam Sơn nữa. Ông Trịnh Khả.'),
 dict(type='stage', bg='paper', label='CÓ THẬT KHÔNG?',
      cast=[dict(c='ngosilien', x=820, D=170, face=-1, expr='normal', hands=[[.6, -.3, 'pen']])],
      cards=[dict(t='GIẢ THUYẾT: BỊ HẠI', x=340, y=720, at=0, col='#c4281f', tc='#fff', fs=38), dict(t='HAY: BẠO BỆNH?', x=340, y=860, at=2, col='#2a4a7a', tc='#fff', fs=38)],
      say='Nhưng khoan kết luận. Đó vẫn chỉ là giả thuyết. Có người cho rằng vua chết vì bạo bệnh. Sử cũ còn chê vua ham tửu sắc.'),
 dict(type='stage', bg='village', label='MỘT NGƯỜI THOÁT',
      cast=[dict(c='phamthiman', x=420, D=160, face=1, expr='scared', from_=-150, at=1)],
      cards=[dict(t='ĐANG MANG THAI', x=420, y=720, at=1, col='#f2dc8a', fs=40)],
      say='Nhưng nhà Nguyễn Trãi chưa tuyệt. Bà Phạm Thị Mẫn, một người vợ của ông, đang mang thai. Bà trốn thoát. Sử chép, đứa con ấy tên Nguyễn Anh Vũ.'),
 dict(type='stage', bg='hall', label='NĂM 1464',
      cast=[dict(c='thanhtong', x=760, D=160, face=-1, expr='normal'), dict(c='anhvu', x=300, D=150, face=1, expr='happy', at=1)],
      cards=[dict(t='TÁN TRÙ BÁ', x=330, y=720, at=1, col='#2a7a4a', tc='#fff')],
      say='Mãi 22 năm sau, vua Lê Thánh Tông minh oan cho Nguyễn Trãi. Truy tặng tước Tán Trù bá.'),
 dict(type='stage', bg='night', label='SAO KHUÊ', zoom=1.12,
      cast=[dict(c='nguyentrai', x=540, D=175, face=1, expr='happy')],
      cards=[dict(t='ỨC TRAI TÂM THƯỢNG', x=540, y=700, at=0, col='#f2dc8a', fs=40), dict(t='QUANG KHUÊ TẢO', x=540, y=810, at=0, col='#f2dc8a', fs=40)],
      say='Vua để lại một câu, đến giờ vẫn còn được nhắc. Lòng Ức Trai sáng như sao Khuê.'),
 dict(type='stage', bg='paper', label='CÒN BÀ LỘ?',
      cast=[dict(c='thilo', x=540, D=165, face=1, expr='sad')],
      cards=[dict(t='VẪN CÒN TRANH CÃI', x=540, y=720, at=1, col='#c4281f', tc='#fff')],
      say='Còn bà Thị Lộ? Người bị gọi là kẻ giết vua. Đến nay, các nhà sử học vẫn còn tranh cãi.'),
 dict(type='stage', bg='lychee', label='PHÁN XỬ', ask=True, gap=1.2, qx=880,
      cast=[dict(c='thanhtong', x=640, D=165, face=-1, expr='normal')],
      cards=[dict(t='CHẾT OAN', x=300, y=720, at=0, col='#2a7a4a', tc='#fff'), dict(t='THỦ PHẠM: ?', x=300, y=860, at=1, col='#c4281f', tc='#fff')],
      say='Lê Thánh Tông minh oan cho Nguyễn Trãi, tức là nhận ông chết oan. Còn thủ phạm thật là ai, sử không chép vua nói một lời. Anh em nghĩ vì sao vua im lặng?'),
 dict(type='ke', label='KỲ SAU', board='ĐÊM 1459|NGHI DÂN', expr='happy',
      say='Viết câu trả lời dưới bình luận nhé. Kỳ sau: năm 1459, bà Thị Anh và con trai bị giết trong một đêm. Kẻ ra tay… chính là thái tử bị phế năm nào, Nghi Dân.'),
]
for s in S:
    for c in s.get('cast', []):
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 3', hook_text='AI GIẾT VUA Ở VƯỜN VẢI?',
          next='Kỳ sau: Lê Nghi Dân đoạt ngôi', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian3', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
