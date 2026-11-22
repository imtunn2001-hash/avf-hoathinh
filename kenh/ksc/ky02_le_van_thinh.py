import json, re
# KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ, kỳ 2: Thái sư Lê Văn Thịnh "hóa hổ" (1096).
# Số viết bằng chữ số trong 'say' (máy tự đổi số -> chữ cho giọng, phụ đề giữ số).
NAMES = ['Lê Văn Thịnh', 'Văn Thịnh', 'Lý Nhân Tông', 'Nhân Tông', 'Mục Thận', 'Dâm Đàm', 'Đại Lý', 'Thao Giang', 'Phú Thọ',
         'Quảng Nguyên', 'Cao Bằng', 'Gia Bình', 'Bắc Ninh', 'Đại Việt sử lược', 'Phan Huy Lê', 'Ỷ Lan', 'Lệ Chi Viên',
         'Nguyễn Trãi', 'Tống', 'Trích Sài', 'Thượng Dương', 'Ngô Sĩ Liên']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


CAST = {
    'levanthinh': dict(tag='LÊ VĂN THỊNH', skin='#e2ae80', hair='#140f0c', hair_style='khan', hat='#1a1a1a', outfit='#7a1f3a', outfit2='#56142a', trim='#d8a93a', beard=True),
    'nhantong': dict(tag='LÝ NHÂN TÔNG', skin='#ecb88a', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f'),
    'mucthan': dict(tag='MỤC THẬN', skin='#c98a5a', hair='#140f0c', hair_style='nonla', outfit='#6a5a3a', outfit2='#4e422a', trim='#3a2a1a', mark='brow'),
    'ylan': dict(tag='THÁI HẬU Ỷ LAN', skin='#ecc09a', hair='#140f0c', hair_style='mien', outfit='#5a2a6a', outfit2='#401e4e', trim='#d8a93a'),
    'sutong': dict(tag='SỨ NHÀ TỐNG', skin='#ecc4a0', hair='#140f0c', hair_style='khan', hat='#2a2a3a', outfit='#2a4a7a', outfit2='#1e3860', trim='#d8a93a', mark='mustache'),
    'phanhuyle': dict(tag='GS. PHAN HUY LÊ', skin='#e8b890', hair='#d8d4ca', hair_style='side', outfit='#4a5a6a', outfit2='#36424e', trim='#d8a93a', mark='glasses'),
}
G = 1290  # mat dat canh stage (GY + 40)

S = [
 dict(type='damdam', phase='reveal', reveal_at=1, label='',
      say='Năm 1096, sử chép một vị thái sư hóa thành hổ, định giết vua. Ông là Lê Văn Thịnh. Người đỗ đầu khoa thi đầu tiên của nước ta.'),
 dict(type='ke', label='TỘI CHẾT, SAO CHỈ ĐÀY?', board='TỘI GIẾT VUA|SAO CHỈ BỊ ĐÀY?', expr='surprised', ask=True, gap=1.2,
      say='Mưu giết vua, xưa là tội chết. Vậy mà ông chỉ bị đày. Anh em thử nghĩ xem. Vua tin, hay không tin chuyện hóa hổ?'),
 dict(type='stage', bg='hall', label='KHOA THI ĐẦU TIÊN',
      cast=[dict(c='nhantong', x=760, D=150, face=-1, expr='happy'), dict(c='levanthinh', x=300, D=165, face=1, expr='happy', at=1, hands=[[.6, -.2, 'scroll']])],
      cards=[dict(t='NĂM 1075', x=540, y=700, at=0, col='#f2dc8a')],
      say='Lùi về năm 1075. Vua Lý Nhân Tông mở khoa thi đầu tiên. Người đứng đầu là Lê Văn Thịnh, quê vùng Gia Bình, Bắc Ninh nay.'),
 dict(type='stage', bg='hall', label='THẦY CỦA VUA',
      cast=[dict(c='levanthinh', x=320, D=170, face=1, expr='normal', hands=[[.6, -.3, 'book']]), dict(c='nhantong', x=760, D=150, face=-1, expr='happy')],
      cards=[dict(t='THỊ LANG BỘ BINH', x=540, y=720, at=1, col='#2a4a7a', tc='#fff')],
      say='Ông được cử vào dạy học cho vua. Rồi lên làm Thị lang bộ Binh.'),
 dict(type='stage', bg='paper', label='ĐÒI ĐẤT',
      cast=[dict(c='levanthinh', x=300, D=170, face=1, expr='angry'), dict(c='sutong', x=790, D=165, face=-1, expr='normal')],
      cards=[dict(t='BIÊN GIỚI VIỆT – TỐNG', x=540, y=700, at=0, col='#f2dc8a', fs=40)],
      say='Mấy năm sau, ông sang đất Tống bàn chuyện biên giới. Nhà Tống đang chiếm mấy vùng đất của ta.'),
 dict(type='stage', bg='paper', label='SỬ CÒN CHÉP', zoom=1.1,
      cast=[dict(c='levanthinh', x=540, D=180, face=1, expr='angry', hands=[[.7, -.6, None]])],
      cards=[dict(t='ĐẤT TỪ XƯA ĐÃ CÓ CHỦ', x=540, y=720, at=1, col='#c4281f', tc='#fff', fs=42)],
      say='Ông nói một câu, sử còn chép lại. Đất biên cương tuy xa xôi, nhưng từ xưa đã có chủ.'),
 dict(type='stage', bg='hall', label='6 HUYỆN, 3 ĐỘNG',
      cast=[dict(c='nhantong', x=540, y=1010, D=100, face=1, expr='happy', tag=False), dict(c='levanthinh', x=820, D=165, face=-1, expr='happy')],
      cards=[dict(t='6 HUYỆN + 3 ĐỘNG', x=280, y=720, at=0, col='#2a7a4a', tc='#fff', fs=40), dict(t='THÁI SƯ', x=820, y=690, at=2, col='#d8a93a', fs=44)],
      say='Nhà Tống trả lại 6 huyện và 3 động vùng Quảng Nguyên. Nay thuộc Cao Bằng. Về nước, ông được phong Thái sư, đứng đầu triều.'),
 dict(type='damdam', phase='calm', label='THÁNG 3 NĂM 1096',
      say='Rồi tháng 3 năm 1096. Vua ngồi thuyền nhỏ, xem đánh cá ở hồ Dâm Đàm.'),
 dict(type='damdam', phase='fog', boat_at=1, label='SƯƠNG MÙ',
      say='Bỗng sương mù kéo tới, dày đặc. Trong sương, một chiếc thuyền lao thẳng về phía vua.'),
 dict(type='damdam', phase='fog', spear_at=0, tiger_at=1, net_at=2, label='CON HỔ',
      say='Vua phóng giáo. Sương tan, trong thuyền có một con hổ. Ông chài Mục Thận quăng lưới trùm lấy.'),
 dict(type='damdam', phase='reveal', reveal_at=0, label='GỠ LƯỚI', gap=.8,
      say='Gỡ lưới ra… thì là Thái sư Lê Văn Thịnh.'),
 dict(type='stage', bg='night', label='PHÉP LẠ ĐẠI LÝ',
      cast=[dict(c='levanthinh', x=760, D=170, face=-1, expr='scared'), dict(c='nguoila', x=300, D=155, face=1, expr='normal', tag=False, at=0)],
      cards=[dict(t='GIA NÔ NGƯỜI ĐẠI LÝ', x=330, y=700, at=0, col='#5a2a6a', tc='#fff', fs=38)],
      say='Sử chép, ông có người gia nô gốc nước Đại Lý, biết phép lạ. Ông mượn phép ấy, toan giết vua.'),
 dict(type='stage', bg='hall_empty', label='KHÔNG NỠ GIẾT',
      cast=[dict(c='nhantong', x=760, D=150, face=-1, expr='sad'), dict(c='levanthinh', x=300, D=165, face=1, expr='sad')],
      cards=[dict(t='ĐÀY LÊN THAO GIANG', x=540, y=720, at=2, col='#1a1a1a', tc='#fff', fs=40)],
      say='Tội ấy đáng chết. Nhưng vua cho rằng ông có công, không nỡ giết. Chỉ đày lên Thao Giang, nay thuộc Phú Thọ. Về sau, sử gia Ngô Sĩ Liên còn chê vua quá nương tay.'),
 dict(type='stage', bg='lake', label='NGƯỜI ĐƯỢC THƯỞNG',
      cast=[dict(c='mucthan', x=540, D=170, face=1, expr='happy')],
      cards=[dict(t='ĐƯỢC PHONG QUAN', x=300, y=700, at=0, col='#2a7a4a', tc='#fff', fs=40), dict(t='ĐẤT DÂM ĐÀM', x=780, y=820, at=0, col='#f2dc8a', fs=40)],
      say='Còn ông chài Mục Thận được phong quan. Được ban luôn đất quanh hồ Dâm Đàm làm thái ấp.'),
 dict(type='doubt2', label='', ),
 dict(type='stage', bg='paper', label='CÓ THẬT KHÔNG?',
      cast=[dict(c='phanhuyle', x=800, D=170, face=-1, expr='normal', at=2)],
      cards=[dict(t='ĐẠI VIỆT SỬ LƯỢC', x=330, y=700, at=0, col='#f6e8b8', fs=40), dict(t='KHÔNG CÓ HỔ', x=330, y=840, at=1, col='#c4281f', tc='#fff', fs=44)],
      say='Nhưng khoan tin. Bộ Đại Việt sử lược cũng chép vụ này. Nhưng trong đó… không hề có con hổ. Giáo sư Phan Huy Lê cũng cho rằng chuyện hóa hổ không thể xảy ra.'),
 dict(type='stage', bg='lake', label='CON HỔ TỪ ĐÂU RA?',
      cast=[dict(c='mucthan', x=720, D=170, face=-1, expr='happy')],
      cards=[dict(t='TRUYỆN THỜ THẦN', x=320, y=700, at=0, col='#f2dc8a', fs=40), dict(t='LÀNG TRÍCH SÀI', x=320, y=830, at=1, col='#2a7a4a', tc='#fff', fs=40)],
      say='Có ý kiến cho rằng con hổ đến từ một truyện thờ thần. Truyện ấy ca ngợi Mục Thận, thành hoàng làng Trích Sài ven hồ.'),
 dict(type='stage', bg='hall_dim', label='AI ĐỨNG SAU?',
      cast=[dict(c='ylan', x=720, D=170, face=-1, expr='normal', at=1)],
      cards=[dict(t='GIẢ THUYẾT', x=330, y=720, at=0, col='#c4281f', tc='#fff')],
      say='Nhiều nhà sử học tin ông bị hãm hại trong cuộc tranh quyền. Có giả thuyết chỉ về Thái hậu Ỷ Lan, người rất mộ đạo Phật. Bà từng hạ cả Hoàng hậu Thượng Dương. Nhưng đến nay, chưa ai chứng minh được.'),
 dict(type='stage', bg='village', label='MẶT KIA',
      cast=[dict(c='levanthinh', x=540, D=170, face=1, expr='happy')],
      cards=[dict(t='14 LÀNG THỜ ÔNG', x=540, y=700, at=0, col='#f2dc8a', fs=42)],
      say='Ngày nay, 14 làng ở Bắc Ninh vẫn thờ ông làm thành hoàng. Quê ông ở Gia Bình còn đền thờ.'),
 dict(type='scales', label='NGHỊCH THẦN HAY BỊ OAN?', left='CON HỔ DÂM ĐÀM', right='NGƯỜI GIỮ ĐẤT', ask=True, gap=1.2,
      say='Một người đòi lại đất cho nước. Rồi bị chép thành hổ dữ. Nếu anh em chép sử, anh em ghi ông là nghịch thần? Hay người bị oan?'),
 dict(type='ke', label='KỲ SAU', board='LỆ CHI VIÊN|1442', expr='happy',
      say='Viết câu trả lời dưới bình luận nhé. Kỳ sau: vụ án Lệ Chi Viên. Vua chết sau một đêm, và người bị khép tội… là Nguyễn Trãi.'),
]
S = [s for s in S if s['type'] != 'doubt2']
for s in S:
    for c in s.get('cast', []):
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 2', hook_text='THÁI SƯ HÓA HỔ GIẾT VUA?',
          next='Kỳ sau: Vụ án Lệ Chi Viên', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian2', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
