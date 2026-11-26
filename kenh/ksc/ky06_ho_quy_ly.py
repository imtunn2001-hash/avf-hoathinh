import json, re
# KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ, kỳ 6: Hồ Quý Ly – người vua Nghệ Tông tin nhất lại kết thúc nhà Trần (1371–1400).
# Hạt nhân: chính Thượng hoàng Nghệ Tông (1394) ban tranh "Tứ phụ" rồi dặn "nếu quan gia hèn kém ngu tối thì khanh tự nhận lấy ngôi vua";
# Quý Ly khóc lạy thề với trời; 6 năm sau (1400) lên ngôi. Câu dặn giống lời Lưu Bị dặn Gia Cát Lượng.
# Khung cốt truyện 2: Tưởng -> Lật -> Giải nghĩa -> Phán xử. Số viết bằng chữ số; ký hiệu nhịp chỉ đặt SAU câu.
# Nguồn: Cương mục/Toàn thư trích qua nghiencuuquocte.org (Hồ Bạch Thảo, "Trần Thuận Tông lên ngôi, Chế Bồng Nga bị giết"), lendang.vn,
# nguoikesu.com (Hồ Quý Ly), voer.edu.vn (Trần Thuận Tông), baodaklak.vn (tiền giấy), Wikipedia en (Hồ Quý Ly, Trần Nghệ Tông, Trần Phế Đế, Trần Thuận Tông).
NAMES = ['Hồ Quý Ly', 'Quý Ly', 'Nghệ Tông', 'Minh Tông', 'Duệ Tông', 'Trần Phế Đế', 'Phế Đế', 'Thuận Tông', 'Huy Ninh', 'Thanh Hóa',
         'Thăng Long', 'Chiêm Thành', 'Khu mật viện đại sứ', 'Đồng bình chương sự', 'Chu Công', 'Hoắc Quang', 'Gia Cát Lượng', 'Tô Hiến Thành',
         'Lưu Bị', 'An Tôn', 'Đại Ngu', 'Tây Đô', 'Ỷ Lan', 'Hồ Liêm']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


CAST = {
    # dấu hiệu riêng: Quý Ly khăn tím + ria + râu, áo tím; Nghệ Tông tóc bạc, mày rậm, râu; Phế Đế quầng mắt; Thuận Tông áo vàng viền xanh;
    # Thiếu Đế bé tí, tóc mái; Huy Ninh búi tóc áo hồng; Duệ Tông đội mũ trụ.
    'quyly': dict(tag='LÊ QUÝ LY', skin='#dca476', hair='#140f0c', hair_style='khan', hat='#3a1a4a', outfit='#5a2a7a', outfit2='#421e5a', trim='#d8a93a', beard=True, mark='mustache'),
    'quylyvua': dict(tag='HỒ QUÝ LY', skin='#dca476', hair='#8a8580', hair_style='mien', outfit='#5a2a7a', outfit2='#421e5a', trim='#d8a93a', beard=True, mark='mustache'),
    'nghetong': dict(tag='THƯỢNG HOÀNG NGHỆ TÔNG', skin='#d9a070', hair='#e8e4da', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#2e4a6a', beard=True, mark='brow'),
    'huyninh': dict(tag='CÔNG CHÚA HUY NINH', skin='#f0c8a0', hair='#140f0c', hair_style='bun', outfit='#c45a7a', outfit2='#9a4060', trim='#d8a93a'),
    'duetong': dict(tag='VUA DUỆ TÔNG', skin='#e2ae80', hair='#140f0c', hair_style='helmet', hat='#8a6a2a', outfit='#7a1f1a', outfit2='#561410', trim='#d8a93a'),
    'phede': dict(tag='TRẦN PHẾ ĐẾ', skin='#e2b48a', hair='#140f0c', hair_style='mien', outfit='#c99a2a', outfit2='#9a7418', trim='#7a1f1a', mark='pale'),
    'thuantong': dict(tag='VUA THUẬN TÔNG', skin='#f0c49c', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#2e7a5a'),
    'thieude': dict(tag='THIẾU ĐẾ', skin='#f2caa4', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f', mark='bangs'),
}
G = 1290  # mat dat canh stage (GY + 40)

S = [
 dict(type='stage', bg='hall_dim', label='', zoom=1.14,
      cast=[dict(c='nghetong', x=540, D=170, face=1, expr='sad')],
      cards=[dict(t='KHANH CỨ LẤY NGÔI', at=1, col='#c4281f', tc='#fff')],
      say='Vua dặn quyền thần: nếu con trẫm hèn kém, khanh cứ lấy ngôi. /// 6 năm sau, nhà Trần mất ngôi vào tay chính người ấy. Đó là Hồ Quý Ly.'),
 dict(type='ke', label='THẬT HAY THỬ?', board='TRAO NGÔI|HAY THỬ?', expr='surprised', ask=True, gap=1.2,
      say='Vua thật lòng trao ngôi, hay đang thử lòng ông? [nghỉ 1.2]'),
 dict(type='stage', bg='village', label='GỐC HỌ HỒ',
      cast=[dict(c='quyly', x=540, D=165, face=1, expr='normal')],
      cards=[dict(t='VỐN MANG HỌ LÊ', at=1, col='#f2dc8a')],
      say='Thuở ấy ông còn mang họ Lê, quê ở Thanh Hóa. Tổ tiên ông họ Hồ, làm con nuôi nhà họ Lê nên đổi họ.'),
 dict(type='stage', bg='hall', label='ANH EM HỌ',
      cast=[dict(c='nghetong', x=330, D=165, face=1, expr='happy'), dict(c='quyly', x=780, D=160, face=-1, expr='happy', at=1)],
      say='Ông có hai bà cô cùng vào cung vua Minh Tông. Một bà sinh ra vua Nghệ Tông. // Vậy là Quý Ly với vua là anh em họ.'),
 dict(type='stage', bg='hall_empty', label='NĂM 1371',
      cast=[dict(c='quyly', x=330, D=160, face=1, expr='happy'), dict(c='huyninh', x=780, D=155, face=-1, expr='happy', at=1)],
      cards=[dict(t='KHU MẬT VIỆN ĐẠI SỨ', x=330, at=0, col='#f2dc8a')],
      say='Năm 1371, Thăng Long vừa bị quân Chiêm đốt phá. Vua Nghệ Tông cho Quý Ly làm Khu mật viện đại sứ. Vua còn gả em gái vừa góa chồng là công chúa Huy Ninh cho ông.'),
 dict(type='stage', bg='riverbank', label='NĂM 1377',
      cast=[dict(c='duetong', x=540, D=165, face=1, expr='angry')],
      cards=[dict(t='VUA TỬ TRẬN', at=1, col='#1a1a1a', tc='#fff')],
      say='Năm 1377, vua Duệ Tông đánh Chiêm Thành và tử trận. Sử chép, Quý Ly lo lương thảo, nghe tin thì bỏ về trước. {hạ: Sử không thấy chép ông bị trách phạt gì.}'),
 dict(type='stage', bg='hall', label='NĂM 1387',
      cast=[dict(c='quyly', x=540, D=170, face=1, expr='happy', from_=-150)],
      cards=[dict(t='ĐỒNG BÌNH CHƯƠNG SỰ', at=1, col='#f2dc8a')],
      say='Năm 1387, Quý Ly được phong Đồng bình chương sự, ngang hàng tể tướng.'),
 dict(type='stage', bg='hall_dim', label='NĂM 1388',
      cast=[dict(c='phede', x=330, D=160, face=1, expr='scared'), dict(c='quyly', x=780, D=160, face=-1, expr='angry', at=1)],
      cards=[dict(t='MƯU BỚT QUYỀN', x=330, at=0, col='#1a1a1a', tc='#fff')],
      say='Năm 1388, vua Trần Phế Đế ngầm bàn cách bớt quyền Quý Ly. Quý Ly biết tin, vào tâu Thượng hoàng trước.'),
 dict(type='stage', bg='hall_dim', label='PHẾ VUA', zoom=1.1,
      cast=[dict(c='nghetong', x=540, D=170, face=1, expr='angry')],
      cards=[dict(t='PHẾ CHÁU RUỘT', at=1, col='#c4281f', tc='#fff')],
      say='Thượng hoàng nghe theo, phế luôn ông vua là cháu ruột mình. {hạ: Phế Đế bị giáng tước, rồi bị bức chết.}'),
 dict(type='stage', bg='hall', label='VUA MỚI',
      cast=[dict(c='thuantong', x=540, D=140, face=1, expr='normal')],
      cards=[dict(t='VUA 11 TUỔI', at=0, col='#f2dc8a')],
      say='Ngai vàng trao cho con út của Thượng hoàng, mới 11 tuổi. Đó là vua Thuận Tông. Hoàng hậu của vua là con gái lớn của Quý Ly.'),
 dict(type='stage', bg='hall', label='ĐẦU NĂM 1394', zoom=1.08,
      cast=[dict(c='quyly', x=540, D=165, face=1, expr='surprised')],
      icons=[dict(icon='tuphu', x=830, y=1010, s=1.2, at=0)],
      cards=[dict(t='TRANH TỨ PHỤ', at=1, col='#f2dc8a')],
      say='Đầu năm 1394, Thượng hoàng sai vẽ một bức tranh, ban cho Quý Ly. Tranh vẽ 4 bề tôi giúp vua nhỏ. Trong đó có Gia Cát Lượng và Tô Hiến Thành. Ý vua rất rõ: khanh giúp vua cũng nên như những người ấy.'),
 dict(type='stage', bg='hall_dim', label='THÁNG 4/1394', zoom=1.12,
      cast=[dict(c='nghetong', x=540, D=170, face=1, expr='sad')],
      cards=[dict(t='SỬ CHÉP LỜI DẶN', at=0, col='#f2dc8a')],
      say='Tháng 4 năm ấy, Thượng hoàng Nghệ Tông gọi Quý Ly vào cung. Sử chép lời ông dặn. Quan gia giúp được thì giúp. {chậm: Nếu hèn kém ngu tối, thì khanh tự nhận lấy ngôi vua.}'),
 dict(type='stage', bg='hall_dim', label='LỜI THỀ', zoom=1.1,
      cast=[dict(c='quyly', x=540, D=165, face=1, expr='sad')],
      cards=[dict(t='KHÓC LẠY, THỀ VỚI TRỜI', at=1, col='#2a4a7a', tc='#fff')],
      say='Quý Ly bỏ mũ, rập đầu xuống đất, vừa khóc vừa thề. Nếu không hết lòng phò vua, con cháu ông sẽ bị trời ghét bỏ.'),
 dict(type='ke', label='LỜI CŨ', board='LƯU BỊ DẶN|KHỔNG MINH', expr='normal',
      say='Câu dặn ấy giống hệt lời Lưu Bị dặn Gia Cát Lượng năm xưa. Gia Cát Lượng cũng khóc, và giữ trọn lời. // Có người cho rằng, đó là một lời thử lòng.'),
 dict(type='stage', bg='hall_empty', label='CUỐI NĂM 1394',
      cast=[dict(c='quyly', x=540, D=165, face=1, expr='normal')],
      cards=[dict(t='DỜI ĐÔ VỀ AN TÔN', at=1, col='#f2dc8a')],
      say='Cuối năm 1394, Thượng hoàng qua đời. /// Năm 1397, Quý Ly ép vua dời đô về An Tôn, Thanh Hóa.'),
 dict(type='stage', bg='hall_dim', label='NĂM 1398',
      cast=[dict(c='thuantong', x=330, D=155, face=1, expr='sad'), dict(c='thieude', x=780, D=110, face=-1, expr='normal', at=1)],
      cards=[dict(t='NHƯỜNG CON 3 TUỔI', x=330, at=0, col='#f2dc8a')],
      say='Năm 1398, vua Thuận Tông bị ép nhường ngôi cho con mới 3 tuổi. Đứa bé là cháu ngoại Quý Ly. Một năm sau, ông vua cũ bị ép đi tu, rồi bị giết.'),
 dict(type='stage', bg='hall', label='NĂM 1400', zoom=1.12,
      cast=[dict(c='quylyvua', x=540, D=170, face=1, expr='happy')],
      cards=[dict(t='QUỐC HIỆU ĐẠI NGU', at=1, col='#c4281f', tc='#fff')],
      say='Năm 1400, Quý Ly phế luôn đứa cháu ngoại, tự lên ngôi. Ông lấy lại họ Hồ, đặt quốc hiệu Đại Ngu. {chậm: Nhà Trần chấm dứt từ đây.}'),
 dict(type='stage', bg='paper', label='MẶT KIA',
      icons=[dict(icon='banknote', x=540, y=960, s=1.7, at=0)],
      cards=[dict(t='TIỀN GIẤY 1396', at=1, col='#2a4a7a', tc='#fff')],
      say='Khoan kết tội vội. Năm 1396, ông cho phát hành tiền giấy, lần đầu tiên trong sử nước ta. Ông hạn chế ruộng đất của quý tộc, xây thành Tây Đô, nay là di sản thế giới.'),
 dict(type='stage', bg='riverbank', label='NĂM 1407',
      cast=[dict(c='quylyvua', x=540, D=165, face=1, expr='scared')],
      cards=[dict(t='BỊ QUÂN MINH BẮT', at=1, col='#1a1a1a', tc='#fff')],
      say='Cuối năm 1406, quân Minh tràn sang. Giữa năm 1407, cha con ông bị bắt, giải về phương Bắc.'),
 dict(type='stage', bg='hall_dim', label='PHÁN XỬ', ask=True, gap=1.2, qx=880,
      cast=[dict(c='quylyvua', x=540, D=165, face=-1, expr='sad')],
      cards=[dict(t='KẺ PHẢN THỀ?', at=1, col='#c4281f', tc='#fff')],
      say='Ông là kẻ phản lời thề, hay chỉ làm đúng điều vua cũ đã cho phép? {cao: Anh em xử thế nào?} [nghỉ 1.2]'),
 dict(type='ke', label='KỲ SAU', board='Ỷ LAN|76 CUNG NỮ', expr='happy',
      say='Kỳ sau: bà Ỷ Lan, và cái chết của 76 cung nữ.'),
]
# Dao dien can mat: moi nhan vat toi da 1 the, dat ngang nguc (y 1175, cung x nhan vat); 1 nhan vat -> dua ve giua.
for s in S:
    if s['type'] != 'stage': continue
    cs = s.get('cast', [])
    if len(cs) == 1 and not s.get('icons'): cs[0]['x'] = 540
    for cd in s.get('cards', []):
        cd['y'] = 1175
        cd.setdefault('x', 540)
        if len(cs) == 1 and not s.get('icons'): cd['x'] = 540
        cd.setdefault('fs', 40 if len(cd['t']) < 16 else 34)
for s in S:
    for c in s.get('cast', []):
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 6', hook_text='VUA DẶN: CỨ LẤY NGÔI',
          next='Kỳ sau: Ỷ Lan và 76 cung nữ', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian6', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
