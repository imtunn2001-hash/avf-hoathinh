import json, re
# KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ, kỳ 4: Lê Long Đĩnh – vua Ngọa Triều (1005–1009).
# Hạt nhân: người duy nhất ôm xác vua Trung Tông mà khóc (Lý Công Uẩn) được kẻ giết vua thăng chức, 4 năm sau lên ngôi;
# mọi bộ sử chép về Long Đĩnh đều viết sau khi nhà Lý lên ngôi. Khung cốt truyện 2: Tưởng -> Lật -> Giải nghĩa -> Phán xử.
# Số viết bằng chữ số trong 'say' (máy tự đổi số -> chữ cho giọng, phụ đề giữ số). Ký hiệu nhịp chỉ đặt SAU câu.
NAMES = ['Lê Long Đĩnh', 'Long Đĩnh', 'Lê Long Việt', 'Long Việt', 'Lý Công Uẩn', 'Lê Đại Hành', 'Trung Tông', 'Ngọa Triều',
         'Minh Xưởng', 'Đại Tạng', 'Cửu kinh', 'Toàn thư', 'Tiền Lê', 'Dương Nhật Lễ', 'Ngô Sĩ Liên', 'Lê Văn Hưu']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


CAST = {
    'longdinh': dict(tag='LÊ LONG ĐĨNH', skin='#e6b088', hair='#140f0c', hair_style='mien', outfit='#7a1f1a', outfit2='#561410', trim='#d8a93a', mark='pale'),
    'longdinh_tu': dict(tag='LÊ LONG ĐĨNH', skin='#e6b088', hair='#140f0c', hair_style='topknot', outfit='#7a1f1a', outfit2='#561410', trim='#d8a93a', mark='scar'),
    'longviet': dict(tag='LÊ TRUNG TÔNG', skin='#f0c49c', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f'),
    'lehoan': dict(tag='LÊ ĐẠI HÀNH', skin='#d9a070', hair='#d8d4ca', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#2e4a6a', beard=True, mark='brow'),
    'conguan': dict(tag='LÝ CÔNG UẨN', skin='#e2ae80', hair='#140f0c', hair_style='khan', hat='#c4281f', outfit='#2e4a6a', outfit2='#22384e', trim='#d8a93a'),
    'conguan_vua': dict(tag='LÝ CÔNG UẨN', skin='#e2ae80', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#2e4a6a'),
    'minhxuong': dict(tag='LÊ MINH XƯỞNG', skin='#ecb88a', hair='#140f0c', hair_style='topknot', outfit='#2e7a5a', outfit2='#225a44', trim='#d8a93a'),
    'nhasu': dict(tag='NHÀ SƯ', skin='#e2b48a', hair='#cfa078', hair_style='bald', outfit='#c47a2a', outfit2='#9a5a1a', trim='#d8a93a'),
}
G = 1290  # mat dat canh stage (GY + 40)

S = [
 dict(type='stage', bg='hall_dim', label='', zoom=1.14,
      cast=[dict(c='conguan', x=540, D=175, face=1, expr='sad')],
      cards=[dict(t='CHỈ 1 NGƯỜI Ở LẠI', x=540, y=720, at=0, col='#1a1a1a', tc='#fff', fs=42), dict(t='4 NĂM SAU: LÊN NGÔI', x=540, y=850, at=2, col='#f2dc8a', fs=42)],
      say='Vua bị giết lúc nửa đêm, chỉ một người ở lại ôm xác mà khóc. // Kẻ giết vua không trừ người ấy, lại còn thăng chức. /// 4 năm sau, chính người ấy ngồi lên ngai vàng.'),
 dict(type='ke', label='AI VIẾT SỬ?', board='AI KHÓC VUA?|AI VIẾT SỬ?', expr='surprised', ask=True, gap=1.2,
      say='Kẻ giết vua là Lê Long Đĩnh, ông vua bị gọi là Ngọa Triều. Người khóc là Lý Công Uẩn. Vậy những gì sử chép về Long Đĩnh, ai đã viết? [nghỉ 1.2]'),
 dict(type='stage', bg='hall', label='NĂM 1005',
      cast=[dict(c='longviet', x=760, D=155, face=-1, expr='happy', at=1), dict(c='longdinh_tu', x=300, D=160, face=1, expr='angry', at=1)],
      cards=[dict(t='VUA LÊ ĐẠI HÀNH MẤT', x=540, y=720, at=0, col='#1a1a1a', tc='#fff', fs=40)],
      say='Năm 1005, vua Lê Đại Hành mất. Các hoàng tử không ai chịu ai. Thái tử Long Việt lên ngôi, tức vua Trung Tông.'),
 dict(type='stage', bg='night', label='3 NGÀY', zoom=1.1,
      cast=[dict(c='longdinh_tu', x=330, D=165, face=1, expr='angry')],
      cards=[dict(t='3 NGÀY LÀM VUA', x=540, y=720, at=0, col='#f2dc8a'), dict(t='ĐÊM TRÈO TƯỜNG VÀO CUNG', x=540, y=850, at=1, col='#c4281f', tc='#fff', fs=38)],
      say='Ông làm vua được đúng 3 ngày. Toàn thư chép, Long Đĩnh sai người đêm trèo tường vào cung. Trung Tông bị giết.'),
 dict(type='stage', bg='hall_empty', label='LÝ CÔNG UẨN', zoom=1.12,
      cast=[dict(c='conguan', x=330, D=170, face=1, expr='sad'), dict(c='longdinh_tu', x=770, D=160, face=-1, expr='normal', from_=1300, at=2)],
      cards=[dict(t='THĂNG CHỨC', x=770, y=720, at=2, col='#2a7a4a', tc='#fff')],
      say='Quần thần bỏ chạy hết. Chỉ Lý Công Uẩn ôm xác vua mà khóc. {chậm: Long Đĩnh cho là người trung, rồi thăng chức cho ông.}'),
 dict(type='stage', bg='hall', label='CUỐI NĂM 1005',
      cast=[dict(c='longdinh', x=540, D=165, face=1, expr='happy', at=0), dict(c='quan', x=180, D=150, face=1, expr='scared', at=1), dict(c='quan', x=900, D=150, face=-1, expr='scared', at=1, tag=False)],
      say='Cuối năm 1005, Long Đĩnh lên ngôi. Từ đây, sử bắt đầu chép về ông những chuyện rất nặng.'),
 dict(type='stage', bg='paper', label='SỬ CHÉP',
      cast=[dict(c='nhasu', x=780, D=165, face=-1, expr='scared', at=1)],
      cards=[dict(t='QUẤN CỎ MÀ ĐỐT', x=330, y=720, at=0, col='#c4281f', tc='#fff', fs=40), dict(t='RÓC MÍA TRÊN ĐẦU SƯ', x=330, y=860, at=1, col='#1a1a1a', tc='#fff', fs=38)],
      say='Toàn thư chép, ông cho quấn cỏ gianh vào tù nhân mà đốt. Có lần ông róc mía ngay trên đầu một nhà sư, coi như trò đùa.'),
 dict(type='stage', bg='hall_dim', label='NGỌA TRIỀU', zoom=1.12,
      cast=[dict(c='longdinh', x=540, D=170, face=1, expr='sad'), dict(c='quan', x=880, D=150, face=-1, expr='surprised', at=1, tag=False)],
      cards=[dict(t='NẰM MÀ THIẾT TRIỀU', x=540, y=720, at=1, col='#f2dc8a', fs=42)],
      say='Sử còn chép ông mắc bệnh, không ngồi được. Đến buổi chầu thì nằm mà nghe tâu. Người đời gọi ông là vua Ngọa Triều.'),
 dict(type='stage', bg='riverbank', label='NĂM 1007',
      cast=[dict(c='minhxuong', x=380, D=165, face=1, expr='happy', from_=-150, hands=[[.6, -.2, 'scroll']])],
      cards=[dict(t='SANG NHÀ TỐNG', x=760, y=720, at=1, col='#f2dc8a')],
      say='Nhưng chính ông vua ấy làm một việc ít ai nhắc. /// Năm 1007, ông sai em trai Minh Xưởng sang nhà Tống. Mục đích là xin kinh sách.'),
 dict(type='stage', bg='pagoda', label='KINH ĐẠI TẠNG',
      cast=[dict(c='nhasu', x=760, D=160, face=-1, expr='happy', hands=[[.6, -.2, 'book']])],
      cards=[dict(t='KINH ĐẠI TẠNG', x=330, y=720, at=0, col='#f2dc8a'), dict(t='CỬU KINH', x=330, y=850, at=1, col='#2a4a7a', tc='#fff')],
      say='Ông xin bộ kinh Đại Tạng và Cửu kinh. Có người coi đây là lần đầu kinh Đại Tạng chữ Hán về nước ta. Ông còn sửa lại triều phục quan văn võ.'),
 dict(type='ke', label='VÌ SAO?', board='BẠO CHÚA?|XIN KINH PHẬT?', expr='surprised', ask=True, gap=1.2,
      say='Một bạo chúa giết người làm trò, sao lại đi xin kinh Phật? [nghỉ 1.2]'),
 dict(type='timeline', label='MỐC THỜI GIAN',
      points=[dict(y='1005', t='LONG ĐĨNH LÊN NGÔI', at=0), dict(y='1009', t='LONG ĐĨNH MẤT', at=1)],
      say='Anh em nhìn mốc thời gian này. Năm 1009, Long Đĩnh mất, sử chép mới 24 tuổi. Con ông còn nhỏ. Triều thần đưa Lý Công Uẩn lên ngôi.'),
 dict(type='stage', bg='hall', label='NGƯỜI LÊN NGÔI', zoom=1.12,
      cast=[dict(c='conguan_vua', x=540, D=170, face=1, expr='happy', at=0)],
      cards=[dict(t='NHÀ TIỀN LÊ: 3 ĐỜI VUA', x=540, y=720, at=1, col='#1a1a1a', tc='#fff', fs=40)],
      say='Đúng là người từng ôm xác vua mà khóc năm nào. {chậm: Nhà Tiền Lê mất từ đó, chỉ sau 3 đời vua.}'),
 dict(type='stage', bg='paper', label='AI VIẾT SỬ?',
      cast=[dict(c='ngosilien', x=800, D=170, face=-1, expr='normal', hands=[[.6, -.3, 'pen']])],
      cards=[dict(t='LÊ VĂN HƯU: 1272', x=330, y=720, at=0, col='#f2dc8a', fs=40), dict(t='TRIỀU SAU CẦN LÝ DO?', x=330, y=860, at=2, col='#c4281f', tc='#fff', fs=36)],
      say='Mọi bộ sử ta còn giữ đều viết sau khi nhà Lý lên ngôi. Bộ sử đầu tiên của Lê Văn Hưu xong năm 1272, hơn 260 năm sau. Có người nghi, triều mới cần một lý do cho việc thay ngôi. /// Một ông vua cũ thật xấu là lý do tốt nhất.'),
 dict(type='stage', bg='hall_dim', label='CÓ THẬT KHÔNG?',
      cast=[dict(c='longdinh', x=760, D=165, face=-1, expr='sad')],
      cards=[dict(t='GIẾT ANH: SỬ CHÉP RÕ', x=330, y=720, at=0, col='#c4281f', tc='#fff', fs=36), dict(t='CHUYỆN ĐỐT NGƯỜI: THỔI PHỒNG?', x=420, y=860, at=1, col='#2a4a7a', tc='#fff', fs=34)],
      say='Nhưng khoan bênh vội. Chuyện giết anh cướp ngôi, sử chép rõ. Còn chuyện đốt người, róc mía, có nhà nghiên cứu cho là bị thổi phồng.'),
 dict(type='stage', bg='hall_dim', label='CÁI CHẾT', zoom=1.1,
      cast=[dict(c='longdinh', x=540, D=165, face=1, expr='sad')],
      cards=[dict(t='VÌ BỆNH?', x=300, y=720, at=0, col='#f2dc8a'), dict(t='HAY BỊ ĐẦU ĐỘC?', x=700, y=850, at=1, col='#c4281f', tc='#fff', fs=40)],
      say='Cả cái chết của ông cũng là dấu hỏi. Sử chép ông chết vì bệnh. {hạ: Có người lại đặt giả thuyết ông bị đầu độc, nhưng chưa có chứng cứ.}'),
 dict(type='stage', bg='hall', label='MẶT KIA',
      cast=[dict(c='longdinh_tu', x=300, D=160, face=1, expr='angry'), dict(c='longdinh', x=790, D=160, face=-1, expr='normal', at=1)],
      cards=[dict(t='GIẾT ANH', x=300, y=720, at=0, col='#c4281f', tc='#fff'), dict(t='XIN KINH', x=790, y=720, at=1, col='#2a7a4a', tc='#fff')],
      say='Một hoàng tử giết anh để cướp ngôi. Một ông vua xin kinh Phật, sửa triều phục. Cả hai đều là Lê Long Đĩnh.'),
 dict(type='stage', bg='hall_dim', label='PHÁN XỬ', ask=True, gap=1.2, qx=880,
      cast=[dict(c='longdinh', x=700, D=165, face=-1, expr='sad')],
      cards=[dict(t='BẠO CHÚA THẬT?', x=330, y=720, at=0, col='#c4281f', tc='#fff', fs=40), dict(t='HAY BỊ BÔI ĐEN?', x=330, y=860, at=1, col='#1a1a1a', tc='#fff', fs=40)],
      say='Và người cần một vua cũ thật xấu nhất, lại chính là người đã khóc năm ấy. /// Long Đĩnh là bạo chúa thật, hay bị triều sau bôi đen? {cao: Anh em xử thế nào?} [nghỉ 1.2]'),
 dict(type='ke', label='KỲ SAU', board='NĂM 1369|AI NGỒI NGAI?', expr='happy',
      say='Kỳ sau: năm 1369, một người không mang dòng máu họ Trần lại ngồi lên ngai vua Trần. Ai đã đưa người ấy lên?'),
]
# Dao dien can mat (z~1.85) -> the chu dat cao se bi cat/de bang tieu de (y 256-510), dat tren dau thi chong bien ten.
# Quy tac: moi nhan vat toi da 1 the, dat ngang nguc (y 1175, cung x nhan vat); 1 nhan vat -> dua ve giua.
ONE = {'': ('CHỈ 1 NGƯỜI Ở LẠI', 0), '3 NGÀY': ('3 NGÀY LÀM VUA', 0), 'SỬ CHÉP': ('RÓC MÍA TRÊN ĐẦU SƯ', 1),
       'KINH ĐẠI TẠNG': ('KINH ĐẠI TẠNG', 0), 'AI VIẾT SỬ?': ('LÊ VĂN HƯU: 1272', 1), 'CÓ THẬT KHÔNG?': ('THỔI PHỒNG?', 2),
       'CÁI CHẾT': ('BỆNH HAY ĐẦU ĐỘC?', 1), 'PHÁN XỬ': ('BẠO CHÚA HAY BỊ BÔI ĐEN?', 1)}
for s in S:
    if s['type'] != 'stage' or not s.get('cards'): continue
    cs = s.get('cast', [])
    if s['label'] in ONE:
        t, a = ONE[s['label']]; c0 = s['cards'][0]
        s['cards'] = [dict(c0, t=t, at=a, fs=min(c0.get('fs', 44), 40 if len(t) < 16 else 34))]
    if len(cs) == 1: cs[0]['x'] = 540
    for cd in s['cards']:
        cd['y'] = 1175
        if len(cs) == 1: cd['x'] = 540
for s in S:
    for c in s.get('cast', []):
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 4', hook_text='NGƯỜI KHÓC VUA LÊN NGÔI',
          next='Kỳ sau: Dương Nhật Lễ – vua Trần không họ Trần', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian4', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
