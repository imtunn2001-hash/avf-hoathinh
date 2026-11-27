import json, re
# KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ, kỳ 7: Ỷ Lan và cái chết của Thượng Dương thái hậu cùng 76 thị nữ (1072–1073).
# Hạt nhân: Toàn thư chép lệnh giam và bức chết là của VUA – mà vua Nhân Tông khi ấy mới lên 7; trước đó bà mẹ đẻ than với con
# "Mẹ già khó nhọc mới có ngày nay, mà giờ phú quý người khác được hưởng". Người phụ nữ từng giữ nước giỏi đến mức vua Thánh Tông
# xấu hổ quay lại đánh Chiêm (1069); về sau dựng hàng trăm chùa, tương truyền để sám hối. Ngô Sĩ Liên chê bà ghen, giết người vô tội.
# Khung cốt truyện 2: Tưởng -> Lật -> Giải nghĩa -> Phán xử. Số viết bằng chữ số; ký hiệu nhịp chỉ đặt SAU câu.
# Nguồn: Wikipedia en (Ỷ Lan; Empress Mother Thượng Dương; Lý Nhân Tông), Đại Đoàn Kết 22/04/2020 "Thái hậu Ỷ Lan – người phụ nữ vĩ đại"
# (trích Toàn thư), VTC News 15/11/2024 "Vị phi tần tài sắc vẹn toàn, hai lần buông rèm nhiếp chính".
# Không dùng (lệch nguồn / 1 nguồn): 72 cung nữ + bà Dương trốn thoát (VTC), 72 chùa + tháp Báo Thiên, Lý Thường Kiệt đồng mưu (1 nguồn), tên thật.
NAMES = ['Ỷ Lan', 'Lý Thánh Tông', 'Thánh Tông', 'Lý Nhân Tông', 'Nhân Tông', 'Thượng Dương', 'Lý Đạo Thành', 'Đạo Thành', 'Thổ Lỗi',
         'Chiêm Thành', 'Chế Củ', 'Ngô Sĩ Liên', 'Toàn thư', 'Lý Thường Kiệt', 'Quang Trung', 'Nguyên phi']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


CAST = {
    # dấu hiệu riêng: Ỷ Lan nốt ruồi (cô gái: nón lá, áo nâu; phi: búi + áo hồng; thái hậu: miện + áo tím than);
    # Thánh Tông râu + mày rậm; Thượng Dương áo lam, mặt tái; Nhân Tông bé tí, tóc mái; Lý Đạo Thành tóc muối tiêu, khăn đen, râu;
    # Chế Củ búi tó, sẹo, da sẫm.
    'ylan': dict(tag='CÔ GÁI HÁI DÂU', skin='#e8b48a', hair='#140f0c', hair_style='nonla', hat='#d8c48a', outfit='#8a5a34', outfit2='#6a4426', trim='#c8a24a', mark='mole'),
    'ylanphi': dict(tag='NGUYÊN PHI Ỷ LAN', skin='#f0c8a0', hair='#140f0c', hair_style='bun', outfit='#c45a7a', outfit2='#9a4060', trim='#d8a93a', mark='mole'),
    'ylanhau': dict(tag='THÁI HẬU Ỷ LAN', skin='#ecc09a', hair='#140f0c', hair_style='mien', outfit='#4a2a5a', outfit2='#341c42', trim='#d8a93a', mark='mole'),
    'ylangia': dict(tag='THÁI HẬU Ỷ LAN', skin='#e2b48a', hair='#d8d4ca', hair_style='mien', outfit='#4a2a5a', outfit2='#341c42', trim='#d8a93a', mark='mole'),
    'lythanhtong': dict(tag='VUA LÝ THÁNH TÔNG', skin='#e2ae80', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#c4281f', beard=True, mark='brow'),
    'thuongduong': dict(tag='THƯỢNG DƯƠNG THÁI HẬU', skin='#f0d0b0', hair='#140f0c', hair_style='mien', outfit='#2e5a8a', outfit2='#22436a', trim='#d8a93a', mark='pale'),
    'nhantong': dict(tag='VUA LÝ NHÂN TÔNG', skin='#f2caa4', hair='#140f0c', hair_style='mien', outfit='#d9a52a', outfit2='#a87a18', trim='#2e7a5a', mark='bangs'),
    'daothanh': dict(tag='THÁI SƯ LÝ ĐẠO THÀNH', skin='#dca476', hair='#8a8580', hair_style='khan', hat='#1a1a1a', outfit='#7a1f1a', outfit2='#561410', trim='#d8a93a', beard=True),
    'checu': dict(tag='VUA CHIÊM CHẾ CỦ', skin='#a8724a', hair='#140f0c', hair_style='topknot', outfit='#2e6a5a', outfit2='#224e44', trim='#d8a93a', mark='scar'),
}
G = 1290  # mat dat canh stage (GY + 40)

S = [
 dict(type='stage', bg='hall_dim', label='', zoom=1.14,
      cast=[dict(c='ylanhau', x=540, D=170, face=1, expr='sad')],
      cards=[dict(t='1 CÂU THAN', at=0, col='#c4281f', tc='#fff')],
      say='77 người chết vì một câu than. /// Câu than ấy của bà Ỷ Lan, nói với đứa con trai mới lên 7.'),
 dict(type='ke', label='LỆNH CỦA AI?', board='VUA BÉ TÍ|RA LỆNH?', expr='surprised', ask=True, gap=1.2,
      say='Sử chép lệnh ấy là của vua. Một ông vua còn bé tí thì ra lệnh thế nào? [nghỉ 1.2]'),
 dict(type='stage', bg='village', label='NĂM 1063',
      cast=[dict(c='ylan', x=540, D=160, face=1, expr='normal', hands=[[.6, -.15, 'weed']])],
      cards=[dict(t='KHÔNG NGÓ KIỆU VUA', at=1, col='#f2dc8a')],
      say='Vua Lý Thánh Tông đã 40 tuổi mà chưa có con trai. Năm 1063, kiệu vua đi cầu tự, qua làng Thổ Lỗi. Dân làng chen nhau ra xem. Chỉ một cô gái hái dâu đứng tựa bụi cỏ lan, không thèm ngó.'),
 dict(type='stage', bg='hall', label='VÀO CUNG',
      cast=[dict(c='lythanhtong', x=330, D=165, face=1, expr='happy'), dict(c='ylanphi', x=780, D=155, face=-1, expr='happy', at=1)],
      say='Vua lạ, cho gọi cô vào cung. Người đời gọi bà là Ỷ Lan, nghĩa là tựa cây lan.'),
 dict(type='stage', bg='hall', label='NĂM 1066',
      cast=[dict(c='ylanphi', x=540, D=165, face=1, expr='happy')],
      cards=[dict(t='SINH HOÀNG TỬ', at=1, col='#f2dc8a')],
      say='Năm 1066, bà sinh con trai cho vua. Đứa bé ấy sau này là vua Lý Nhân Tông.'),
 dict(type='stage', bg='riverbank', label='NĂM 1069',
      cast=[dict(c='lythanhtong', x=540, D=165, face=1, expr='sad', hands=[[.6, -.25, 'sword']])],
      cards=[dict(t='ĐÁNH MÃI KHÔNG THẮNG', at=1, col='#1a1a1a', tc='#fff')],
      say='Năm 1069, vua đem quân đánh Chiêm Thành, giao việc nước cho bà. Đánh mãi không thắng, vua cho quân quay về.'),
 dict(type='stage', bg='village', label='DÂN KHEN',
      cast=[dict(c='lythanhtong', x=540, D=165, face=1, expr='surprised')],
      cards=[dict(t='NAM NHI THUA ĐÀN BÀ?', at=1, col='#c4281f', tc='#fff')],
      say='Về giữa đường, vua nghe dân khen bà trị nước giỏi. Sử chép vua nói. {chậm: Đàn bà còn làm được như thế, ta là nam nhi lại chẳng được việc gì sao?}'),
 dict(type='stage', bg='riverbank_dawn', label='BẮT VUA CHIÊM',
      cast=[dict(c='checu', x=540, D=160, face=1, expr='scared')],
      cards=[dict(t='DÂNG 3 CHÂU', at=1, col='#f2dc8a')],
      say='Vua quay lại đánh tiếp, bắt sống vua Chiêm là Chế Củ. Chế Củ phải dâng 3 châu đất để được tha.'),
 dict(type='stage', bg='hall_dim', label='NĂM 1072', zoom=1.1,
      cast=[dict(c='nhantong', x=540, D=115, face=1, expr='scared')],
      cards=[dict(t='VUA MỚI LÊN 7', at=1, col='#f2dc8a')],
      say='Đầu năm 1072, vua Thánh Tông mất. Thái tử lên ngôi khi mới lên 7.'),
 dict(type='stage', bg='hall', label='AI NHIẾP CHÍNH?',
      cast=[dict(c='thuongduong', x=330, D=160, face=1, expr='normal'), dict(c='daothanh', x=780, D=160, face=-1, expr='normal', at=1)],
      say='Anh em tưởng mẹ đẻ của vua sẽ cầm quyền. /// Không. Người nhiếp chính là hoàng hậu chính, Thượng Dương thái hậu, cùng thái sư Lý Đạo Thành.'),
 dict(type='stage', bg='hall_dim', label='MẸ ĐẺ ĐỨNG NGOÀI', zoom=1.1,
      cast=[dict(c='ylanphi', x=540, D=165, face=1, expr='angry')],
      cards=[dict(t='TOÀN THƯ CHÉP', at=0, col='#f2dc8a')],
      say='Bà Ỷ Lan là mẹ đẻ, lại phải đứng ngoài. Toàn thư chép bà có tính ghen, và bà than với con trai.'),
 dict(type='stage', bg='hall_dim', label='CÂU THAN', zoom=1.14,
      cast=[dict(c='ylanphi', x=540, D=170, face=1, expr='sad')],
      cards=[dict(t='MẸ GIÀ KHÓ NHỌC', at=1, col='#c4281f', tc='#fff')],
      say='{chậm: Mẹ già khó nhọc mới có ngày nay, mà bây giờ phú quý người khác được hưởng.} // Thế thì mẹ già biết để vào đâu?'),
 dict(type='stage', bg='hall', label='ĐỔI NGƯỜI',
      cast=[dict(c='ylanphi', x=330, D=165, face=1, expr='happy'), dict(c='nhantong', x=780, D=110, face=-1, expr='normal', at=1)],
      cards=[dict(t='MẸ ĐẺ VÀO THAY', x=330, at=0, col='#f2dc8a')],
      say='Ít lâu sau, Thượng Dương thái hậu bị gạt ra. Bà Ỷ Lan vào thay, cùng con trông việc nước.'),
 dict(type='stage', bg='hall_dim', label='NĂM 1073', zoom=1.08,
      cast=[dict(c='thuongduong', x=540, D=165, face=1, expr='scared')],
      cards=[dict(t='76 THỊ NỮ', at=1, col='#1a1a1a', tc='#fff')],
      say='Năm 1073, Toàn thư chép, vua sai giam bà Dương cùng 76 thị nữ vào cung Thượng Dương. {hạ: Rồi bức cả 77 người phải chết, chôn theo lăng vua Thánh Tông.}'),
 dict(type='stage', bg='riverbank', label='ĐẨY ĐI XA',
      cast=[dict(c='daothanh', x=540, D=165, face=1, expr='sad')],
      cards=[dict(t='CAN NGĂN?', at=1, col='#2a4a7a', tc='#fff')],
      say='Thái sư Lý Đạo Thành cũng bị đẩy khỏi triều, đưa đi trấn phương Nam. Sử gia cho rằng ông bị đẩy đi vì dám can ngăn.'),
 dict(type='ke', label='LỆNH CỦA AI?', board='LỆNH VUA|VUA BÉ TÍ', expr='normal',
      say='Giờ anh em hiểu rồi đấy. Trên giấy là lệnh vua. Nhưng ông vua ấy còn bé tí, và người ngồi cạnh vua là mẹ đẻ.'),
 dict(type='stage', bg='paper', label='SỬ GIA PHÁN',
      cast=[dict(c='ngosilien', x=540, D=165, face=1, expr='angry', hands=[[.6, -.2, 'scroll']])],
      cards=[dict(t='GIẾT NGƯỜI VÔ TỘI', at=1, col='#c4281f', tc='#fff')],
      say='Hơn 400 năm sau, sử gia Ngô Sĩ Liên viết thẳng. Bà sùng đạo Phật, mà nỡ giết oan bà thái hậu vô tội.'),
 dict(type='stage', bg='pagoda', label='MẶT KIA',
      cast=[dict(c='ylangia', x=540, D=165, face=1, expr='sad')],
      cards=[dict(t='HÀNG TRĂM NGÔI CHÙA', at=1, col='#2a4a7a', tc='#fff')],
      say='Khoan kết tội vội. Về sau bà dựng hàng trăm ngôi chùa, tháp. Tương truyền là để sám hối chuyện năm 1073.'),
 dict(type='stage', bg='hall', label='GIỮ NƯỚC',
      cast=[dict(c='ylanhau', x=540, D=165, face=1, expr='happy')],
      cards=[dict(t='2 LẦN NHIẾP CHÍNH', at=1, col='#f2dc8a')],
      say='Bà còn cùng con giữ nước, khi Lý Thường Kiệt đánh Tống. Bà mất năm 1117, được thờ ở nhiều nơi đến nay.'),
 dict(type='scales', label='PHÁN XỬ', left='77 NGƯỜI CHẾT', right='GIỮ NƯỚC', ask=True, gap=1.2,
      say='Không ra tay, mẹ con bà có giữ nổi quyền không? Hay đó chỉ là một cơn ghen? {cao: Anh em xử thế nào?} [nghỉ 1.2]'),
 dict(type='ke', label='KỲ SAU', board='QUANG TRUNG|MẤT ĐỘT NGỘT', expr='happy',
      say='Kỳ sau: vua Quang Trung mất đột ngột năm 1792. Bệnh, hay bị hại?'),
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
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 7', hook_text='1 CÂU THAN, 77 NGƯỜI CHẾT',
          next='Kỳ sau: Cái chết của vua Quang Trung', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian7', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
