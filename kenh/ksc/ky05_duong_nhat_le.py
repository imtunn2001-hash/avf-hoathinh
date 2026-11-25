import json, re
# KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ, kỳ 5: Dương Nhật Lễ – vua nhà Trần không mang dòng máu họ Trần (1369–1370).
# Hạt nhân: người đưa Nhật Lễ lên ngai (Hiến Từ thái hậu, bà nội trên danh nghĩa) bị chính Nhật Lễ đầu độc 6 tháng sau;
# mẹ Nhật Lễ (đào hát, vai Vương Mẫu) chạy sang Chiêm Thành xin báo thù -> 1371 Chế Bồng Nga đánh vào Thăng Long.
# Khung cốt truyện 2: Tưởng -> Lật -> Giải nghĩa -> Phán xử. Số viết bằng chữ số; ký hiệu nhịp chỉ đặt SAU câu.
# Nguồn: Toàn thư/Cương mục (trích qua nghiencuuquocte.org, scov.gov.vn), kienthuc.net.vn, Wikipedia en (Dương Nhật Lễ, Trần Nghệ Tông, Chiến tranh Chiêm – Việt 1367–1390).
NAMES = ['Dương Nhật Lễ', 'Nhật Lễ', 'Hiến Từ', 'Trần Dụ Tông', 'Dụ Tông', 'Trần Phủ', 'Cung Định vương', 'Cung Túc vương', 'Nguyên Dục',
         'Minh Tông', 'Dương Khương', 'Vương Mẫu', 'Đại Định', 'Toàn thư', 'Nghệ Tông', 'Trần Nguyên Trác', 'Thiên Ninh', 'Chế Bồng Nga',
         'Chiêm Thành', 'Thăng Long', 'Hồ Quý Ly', 'Đà Giang', 'Trần Kính', 'Trần Ngô Lang', 'Liễu']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


CAST = {
    # mỗi người 1 dấu hiệu riêng: Hiến Từ tóc bạc + mũ miện; Nhật Lễ cầm quạt tuồng; Vương Mẫu nốt ruồi + quạt; Dương Khương khăn đỏ + ria;
    # Nguyên Dục râu + khăn xanh; Dụ Tông quầng mắt; Trần Phủ mày rậm; Thiên Ninh búi tóc áo lục; Chế Bồng Nga búi tó + sẹo.
    'hientu': dict(tag='HIẾN TỪ THÁI HẬU', skin='#e6b48a', hair='#e8e4da', hair_style='mien', outfit='#5a2a5a', outfit2='#421e42', trim='#d8a93a'),
    'nhatle': dict(tag='DƯƠNG NHẬT LỄ', skin='#f0c49c', hair='#140f0c', hair_style='mien', outfit='#c4502a', outfit2='#9a3a1c', trim='#d8a93a'),
    'vuongmau': dict(tag='MẸ NHẬT LỄ', skin='#f2caa4', hair='#140f0c', hair_style='bun', outfit='#c45a7a', outfit2='#9a4060', trim='#d8a93a', mark='mole'),
    'duongkhuong': dict(tag='DƯƠNG KHƯƠNG', skin='#e2ae80', hair='#140f0c', hair_style='khan', hat='#c4281f', outfit='#6a4a8a', outfit2='#4e366a', trim='#d8a93a', mark='mustache'),
    'nguyendu': dict(tag='CUNG TÚC VƯƠNG', skin='#e2ae80', hair='#140f0c', hair_style='khan', hat='#2e4a6a', outfit='#2e4a6a', outfit2='#22384e', trim='#d8a93a', beard=True),
    'dutong': dict(tag='TRẦN DỤ TÔNG', skin='#e2b48a', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#7a1f1a', mark='pale'),
    'tranphu': dict(tag='TRẦN PHỦ', skin='#d9a070', hair='#3a3a3a', hair_style='khan', hat='#1a1a1a', outfit='#2e5a46', outfit2='#224436', trim='#d8a93a', beard=True, mark='brow'),
    'nghetong': dict(tag='VUA NGHỆ TÔNG', skin='#d9a070', hair='#3a3a3a', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#2e4a6a', beard=True, mark='brow'),
    'thienninh': dict(tag='CÔNG CHÚA THIÊN NINH', skin='#f0c8a0', hair='#140f0c', hair_style='bun', outfit='#2e7a5a', outfit2='#225a44', trim='#d8a93a'),
    'chebongnga': dict(tag='CHẾ BỒNG NGA', skin='#b07a52', hair='#140f0c', hair_style='topknot', outfit='#7a3a1a', outfit2='#5a2a12', trim='#d8a93a', beard=True, mark='scar'),
}
G = 1290  # mat dat canh stage (GY + 40)
FAN = [[.6, -.2, 'fan']]

S = [
 dict(type='stage', bg='hall_dim', label='', zoom=1.14,
      cast=[dict(c='hientu', x=540, D=170, face=1, expr='scared')],
      icons=[dict(icon='bottle', x=820, y=1060, s=1.1, at=1)],
      cards=[dict(t='6 THÁNG SAU: ĐẦU ĐỘC BÀ', at=1, col='#c4281f', tc='#fff')],
      say='Bà đưa cháu lên ngai vàng. // 6 tháng sau, cháu đầu độc bà. /// Người cháu ấy làm vua nhà Trần, mà không mang dòng máu họ Trần.'),
 dict(type='ke', label='BÀ CÓ BIẾT?', board='DÒNG MÁU|CỦA AI?', expr='surprised', ask=True, gap=1.2,
      say='Đó là Dương Nhật Lễ, năm 1369. Bà nội có biết đứa cháu này mang dòng máu của ai không? [nghỉ 1.2]'),
 dict(type='stage', bg='hall', label='NĂM 1369',
      cast=[dict(c='dutong', x=540, D=165, face=1, expr='sad')],
      cards=[dict(t='VUA MẤT, KHÔNG CON', at=0, col='#1a1a1a', tc='#fff')],
      say='Năm 1369, vua Trần Dụ Tông mất mà không có con. Sử chép vua để lại di chiếu cho Nhật Lễ nối ngôi.'),
 dict(type='stage', bg='hall', label='TRIỀU THẦN',
      cast=[dict(c='tranphu', x=540, D=165, face=1, expr='normal', at=0), dict(c='quan', x=180, D=150, face=1, expr='normal', at=1, tag=False)],
      cards=[dict(t='MUỐN LẬP TRẦN PHỦ', at=1, col='#2a7a4a', tc='#fff')],
      say='Quần thần thì muốn lập Cung Định vương Trần Phủ. Ông là con vua Minh Tông, đúng dòng họ Trần.'),
 dict(type='stage', bg='hall', label='HIẾN TỪ THÁI HẬU', zoom=1.12,
      cast=[dict(c='hientu', x=540, D=170, face=1, expr='angry')],
      cards=[dict(t='TOÀN THƯ CHÉP', at=1, col='#f2dc8a')],
      say='Hiến Từ thái hậu, mẹ vua vừa mất, gạt lời quần thần, đón Nhật Lễ vào cung. Trên danh nghĩa, bà là bà nội của Nhật Lễ. Toàn thư chép bà nói thế này. Cung Túc vương Nguyên Dục là con trưởng, vậy mà không được làm vua, lại mất sớm. {chậm: Nhật Lễ chẳng phải là con Nguyên Dục đó sao?}'),
 dict(type='stage', bg='night', label='SÂN KHẤU TUỒNG', zoom=1.1,
      cast=[dict(c='vuongmau', x=330, D=160, face=1, expr='happy', hands=FAN), dict(c='duongkhuong', x=770, D=160, face=-1, expr='happy', at=1)],
      cards=[dict(t='ĐÀO HÁT', x=330, at=0, col='#f2dc8a')],
      say='Nhưng sử chép một chuyện khác hẳn. /// Mẹ Nhật Lễ là đào hát, chồng bà là kép hát Dương Khương.'),
 dict(type='stage', bg='night', label='VAI VƯƠNG MẪU', zoom=1.12,
      cast=[dict(c='vuongmau', x=540, D=170, face=1, expr='happy', hands=FAN)],
      cards=[dict(t='VƯƠNG MẪU HIẾN BÀN ĐÀO', at=0, col='#f2dc8a')],
      say='Bà nổi tiếng với vai Vương Mẫu trong tích Vương Mẫu hiến bàn đào. Người ta gọi luôn bà là Vương Mẫu.'),
 dict(type='stage', bg='hall_dim', label='BÍ MẬT', zoom=1.12,
      cast=[dict(c='nguyendu', x=300, D=160, face=1, expr='happy'), dict(c='vuongmau', x=780, D=160, face=-1, expr='scared', at=1)],
      say='Cung Túc vương mê sắc đẹp, lấy bà làm vợ. {hạ: Khi ấy bà đang mang thai con của Dương Khương.} // Đứa bé sinh ra trong phủ vương, được nhận làm con. Đó chính là Nhật Lễ. Sử không chép bà thái hậu có biết hay không.'),
 dict(type='stage', bg='hall', label='ĐẠI ĐỊNH',
      cast=[dict(c='nhatle', x=540, D=165, face=1, expr='happy', at=0, hands=FAN), dict(c='quan', x=180, D=150, face=1, expr='scared', at=1, tag=False), dict(c='quan', x=900, D=150, face=-1, expr='scared', at=1, tag=False)],
      cards=[dict(t='NIÊN HIỆU ĐẠI ĐỊNH', at=0, col='#f2dc8a')],
      say='Tháng 6 năm 1369, Nhật Lễ lên ngôi, đặt niên hiệu Đại Định. Ngồi lên ngai rồi, ông mới lộ mặt thật.'),
 dict(type='stage', bg='hall_dim', label='RƯỢU VÀ HÁT', zoom=1.1,
      cast=[dict(c='nhatle', x=540, D=165, face=1, expr='happy', hands=[[.6, -.2, 'bottle']])],
      cards=[dict(t='MUỐN ĐỔI SANG HỌ DƯƠNG', at=1, col='#c4281f', tc='#fff')],
      say='Toàn thư chép, ông ngày ngày rượu chè, chỉ mê hát xướng. Ông còn muốn đổi lại sang họ Dương.'),
 dict(type='ke', label='VÌ SAO?', board='VUA NHÀ TRẦN|ĐỔI HỌ DƯƠNG?', expr='surprised', ask=True, gap=1.2,
      say='Một ông vua muốn bỏ họ của chính triều đại mình. Vậy ông đang ngồi ngai của ai? [nghỉ 1.2]'),
 dict(type='stage', bg='hall_dim', label='THÁNG 12', zoom=1.12,
      cast=[dict(c='hientu', x=540, D=170, face=1, expr='sad')],
      icons=[dict(icon='bottle', x=820, y=1060, s=1.1, at=1)],
      cards=[dict(t='BÀ HỐI HẬN', at=0, col='#1a1a1a', tc='#fff')],
      say='Hiến Từ thái hậu bắt đầu hối hận. /// {hạ: Tháng 12 năm ấy, Nhật Lễ ngầm sai đánh thuốc độc giết bà.}'),
 dict(type='stage', bg='night', label='NĂM 1370',
      cast=[dict(c='nhatle', x=540, D=165, face=1, expr='angry')],
      cards=[dict(t='MƯU GIẾT VUA THẤT BẠI', at=0, col='#c4281f', tc='#fff')],
      say='Năm 1370, tôn thất Trần Nguyên Trác mưu giết Nhật Lễ nhưng thất bại. Những người dự mưu đều bị giết.'),
 dict(type='stage', bg='riverbank', label='DẤY BINH',
      cast=[dict(c='tranphu', x=330, D=165, face=1, expr='angry', from_=-150), dict(c='thienninh', x=770, D=155, face=-1, expr='angry', at=1)],
      cards=[dict(t='TRỐN LÊN ĐÀ GIANG', x=330, at=0, col='#f2dc8a')],
      say='Trần Phủ trốn lên Đà Giang. Ông cùng em trai Trần Kính và em gái là công chúa Thiên Ninh dấy binh.'),
 dict(type='stage', bg='hall', label='THÁNG 11/1370',
      cast=[dict(c='nghetong', x=330, D=165, face=1, expr='normal', at=0), dict(c='nhatle', x=780, D=160, face=-1, expr='sad', at=1)],
      say='Tháng 11 năm 1370, Trần Phủ lên ngôi, tức vua Nghệ Tông. Nhật Lễ bị phế, đem giam.'),
 dict(type='stage', bg='hall_dim', label='KẾT CỤC', zoom=1.1,
      cast=[dict(c='nhatle', x=540, D=165, face=1, expr='angry')],
      cards=[dict(t='BỊ XỬ TỬ', at=1, col='#1a1a1a', tc='#fff')],
      say='Bị giam rồi, ông vẫn giết Trần Ngô Lang, người đã khuyên ông nhường ngôi. Vua Nghệ Tông liền cho xử tử Nhật Lễ cùng con trai là Liễu.'),
 dict(type='stage', bg='beach_night', label='CHIÊM THÀNH',
      cast=[dict(c='vuongmau', x=330, D=160, face=1, expr='sad', from_=-150), dict(c='chebongnga', x=780, D=170, face=-1, expr='angry', at=1)],
      cards=[dict(t='XIN BÁO THÙ', x=330, at=0, col='#c4281f', tc='#fff')],
      say='Chuyện chưa hết. /// Mẹ Nhật Lễ chạy sang Chiêm Thành, xin vua Chế Bồng Nga báo thù cho con.'),
 dict(type='stage', bg='hall_empty', label='NĂM 1371', zoom=1.1,
      cast=[dict(c='chebongnga', x=540, D=175, face=1, expr='angry')],
      cards=[dict(t='THĂNG LONG BỊ ĐỐT', at=1, col='#c4281f', tc='#fff')],
      say='Năm 1371, quân Chiêm đánh thẳng vào Thăng Long. {chậm: Kinh thành bị cướp phá, cung điện bị đốt.} Vua Nghệ Tông phải bỏ chạy.'),
 dict(type='stage', bg='paper', label='MẶT KIA',
      cast=[dict(c='nhatle', x=540, D=165, face=1, expr='sad')],
      cards=[dict(t='SỬ DO PHE THẮNG CHÉP', at=1, col='#2a4a7a', tc='#fff')],
      say='Khoan kết tội vội. Ông mang họ Trần từ lúc lọt lòng, lớn lên trong phủ vương. Mọi điều ta biết về ông đều do phe thắng chép lại.'),
 dict(type='stage', bg='hall_dim', label='PHÁN XỬ', ask=True, gap=1.2, qx=880,
      cast=[dict(c='nhatle', x=540, D=165, face=-1, expr='sad')],
      cards=[dict(t='KẺ ÁC HAY ĐẶT NHẦM CHỖ?', at=1, col='#c4281f', tc='#fff')],
      say='Bà nội đã hối hận, ngai vàng đang lung lay. Ông ngồi chờ bị phế, hay ra tay trước? /// Nhật Lễ là kẻ ác, hay chỉ là người bị đặt nhầm chỗ? {cao: Anh em xử thế nào?} [nghỉ 1.2]'),
 dict(type='ke', label='KỲ SAU', board='NGƯỜI ĐƯỢC TIN|HỒ QUÝ LY', expr='happy',
      say='Kỳ sau: người vua Nghệ Tông tin nhất, lại chính là người kết thúc nhà Trần. Đó là Hồ Quý Ly.'),
]
# Dao dien can mat: moi nhan vat toi da 1 the, dat ngang nguc (y 1175, cung x nhan vat); 1 nhan vat -> dua ve giua.
for s in S:
    if s['type'] != 'stage': continue
    cs = s.get('cast', [])
    if len(cs) == 1: cs[0]['x'] = 540
    for cd in s.get('cards', []):
        cd['y'] = 1175
        cd.setdefault('x', 540)
        if len(cs) == 1: cd['x'] = 540
        cd.setdefault('fs', 40 if len(cd['t']) < 16 else 34)
for s in S:
    for c in s.get('cast', []):
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 5', hook_text='6 THÁNG SAU, ĐẦU ĐỘC BÀ',
          next='Kỳ sau: Hồ Quý Ly – người được tin nhất', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian5', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
