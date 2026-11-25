import json, re
# CHIEN SU KY - BAN LA LINH, tap 1: linh nha Tran nam 1285 (khang chien chong Nguyen lan 2).
# Hook: chu "Sat That" thich tren tay - bi giac bat thi chinh 2 chu ay giet ban (Wikipedia EN Mongol invasions of Vietnam: 18/2/1285).
# Nguon: Wikipedia (Mongol invasions of Vietnam, Tran Binh Trong, Battle of Chuong Duong, Tran dynasty military), Baomoi (Sat That), Znews.
# Nhan vat 'BAN' co dinh qua moi tap: bang do tren tran (hair_style band) + vet bun tren ma (mark dirt).
NAMES = ['Trần Ích Tắc', 'Sát Thát', 'Hưng Đạo Vương', 'Thoát Hoan', 'Thăng Long', 'Trần Bình Trọng', 'Thiên Mạc', 'Nam Quan', 'Hàm Tử',
         'Chương Dương', 'Toa Đô', 'Mông Cổ', 'Tây Sơn', 'sông Cầu']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


BAN = dict(tag='BẠN', skin='#e2ae80', hair='#140f0c', hair_style='band', band='#c4281f', outfit='#6a5534', outfit2='#4c3c24', trim='#c4281f', mark='dirt')
DONG = dict(tag='ĐỒNG ĐỘI', skin='#d9a070', hair='#140f0c', hair_style='khan', hat='#3a3a2a', outfit='#5a6a44', outfit2='#3e4a2e', trim='#d8a93a')
NGUYEN = dict(tag='QUÂN NGUYÊN', skin='#e8b588', hair='#16120f', hair_style='helmet', helm='#4a4a5a', outfit='#5a4a6a', outfit2='#40344c', trim='#d8a93a', scales=True)
CAST = {
    'ban': BAN, 'linhviet': BAN,                                  # canh tran melee: linhviet = BAN
    'dongdoi': DONG, 'linhviet2': dict(DONG, tag='ĐỒNG ĐỘI'),
    'linhhan': NGUYEN, 'linhnguyen': NGUYEN,
    'me': dict(tag='MẸ BẠN', skin='#d9a77a', hair='#9a9690', hair_style='bun', outfit='#5a4a3a', outfit2='#40342a', trim='#c8a24a'),
    'hungdao': dict(tag='HƯNG ĐẠO VƯƠNG', skin='#e0a878', hair='#1b1512', hair_style='topknot', outfit='#2e4a6a', outfit2='#22384e', trim='#d8a93a', beard=True, mark='brow'),
    'binhtrong': dict(tag='TRẦN BÌNH TRỌNG', skin='#e2ae80', hair='#140f0c', hair_style='topknot', outfit='#7a1f1a', outfit2='#561410', trim='#d8a93a'),
    'ichtac': dict(tag='TRẦN ÍCH TẮC', skin='#f0c49c', hair='#140f0c', hair_style='khan', hat='#d9a52a', outfit='#c99a2a', outfit2='#9a7418', trim='#7a1f1a', mark='pale'),
    'quan': dict(tag='QUAN TRIỀU', skin='#dca476', hair='#140f0c', hair_style='khan', hat='#1a1a1a', outfit='#2e5a46', outfit2='#224436', trim='#d8a93a', beard=True),
    'thoathoan': dict(tag='THOÁT HOAN', skin='#ecbd8c', hair='#16120f', hair_style='helmet', helm='#a8862e', outfit='#8a6a2a', outfit2='#6a5020', trim='#7a1c1a', mark='mustache'),
}
G = 1290
SP = [.55, -.1, 'spear', -70]

S = [
 dict(type='stage', bg='village_night', label='', zoom=1.16,
      cast=[dict(c='ban', x=540, D=180, face=1, expr='scared')],
      cards=[dict(t='SÁT THÁT', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=46)],
      say='Trên cánh tay bạn vừa thích 2 chữ. {chậm: Nếu giặc bắt được bạn, chính 2 chữ ấy sẽ giết bạn.}'),
 dict(type='stage', bg='village', label='NĂM 1285',
      cast=[dict(c='ban', x=540, D=165, face=1, expr='normal', hands=[SP])],
      say='Bạn là lính nhà Trần, năm 1285. Quân Nguyên sắp kéo sang đánh nước ta lần thứ hai.'),
 dict(type='stage', bg='village', label='HAI CHỮ', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='angry'), dict(c='dongdoi', x=760, D=160, face=-1, expr='angry', from_=1300, at=1)],
      cards=[dict(t='GIẾT GIẶC MÔNG CỔ', x=330, y=1175, at=1, col='#f2dc8a', fs=32)],
      say='Người nào trong quân cũng thích lên tay 2 chữ Sát Thát. Nghĩa là giết giặc Mông Cổ.'),
 dict(type='stage', bg='village_night', label='KHÔNG XÓA ĐƯỢC', zoom=1.16,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='angry')],
      cards=[dict(t='HẾT ĐƯỜNG ĐẦU HÀNG', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=36)],
      say='Chữ thích vào da thì không xóa được. Bị bắt là chết. {chậm: Từ hôm ấy, bạn không còn đường đầu hàng.}'),
 dict(type='stage', bg='riverbank', label='TỔNG CHỈ HUY',
      cast=[dict(c='hungdao', x=760, D=150, face=-1, expr='normal', hands=[[.6, -.2, 'scroll']]), dict(c='ban', x=300, D=165, face=1, expr='surprised', at=1)],
      say='Tổng chỉ huy là Hưng Đạo Vương. Bạn chỉ thấy ông từ rất xa, và chưa bao giờ dám ngẩng lên.'),
 dict(type='army_march', label='CUỐI THÁNG 1', enemy='linhnguyen', leader='thoathoan',
      say='Cuối tháng 1 năm 1285, giặc vượt ải Nam Quan. Sách vở chép số quân rất khác nhau, nhưng đều là hàng chục vạn.'),
 dict(type='stage', bg='hall_dim', label='HOÀNG THÂN HÀNG GIẶC',
      cast=[dict(c='ichtac', x=760, D=160, face=-1, expr='scared'), dict(c='thoathoan', x=320, D=165, face=1, expr='happy', at=1)],
      cards=[dict(t='SANG HÀNG GIẶC', x=760, y=1175, at=1, col='#1a1a1a', tc='#fff', fs=36)],
      say='Rồi tin dữ tới. Hoàng thân Trần Ích Tắc cùng một số quan lại đã sang hàng giặc. Trên tay họ không có chữ nào.'),
 dict(type='stage', bg='riverbank', label='BẠN CHỌN?', ask=True, gap=1.2, qx=880, zoom=1.15,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='scared', hands=[SP])],
      cards=[dict(t='BẠN LÀM GÌ?', x=540, y=1175, at=1, col='#1a1a1a', tc='#fff', fs=40)],
      say='Giặc đông. Vua đã rút. Người hoàng tộc đã hàng. {cao: Còn bạn, với 2 chữ không xóa được trên tay, bạn sẽ làm gì?} [nghỉ 1.2]'),
 dict(type='stage', bg='riverbank_dawn', label='RÚT',
      cast=[dict(c='ban', x=420, D=160, face=-1, expr='sad', from_=900, hands=[SP]), dict(c='dongdoi', x=700, D=150, face=-1, expr='sad', from_=1250, tag=False)],
      say='Bạn không có đường hàng. Nên bạn theo quân rút, giữ sức chờ ngày đánh lại. Cả kinh thành Thăng Long cũng bị bỏ trống.'),
 dict(type='stage', bg='hall_empty', label='THĂNG LONG', zoom=1.12,
      cast=[dict(c='thoathoan', x=540, D=170, face=1, expr='surprised', from_=-200)],
      cards=[dict(t='KHO GẠO TRỐNG', x=540, y=1175, at=2, col='#f2dc8a', fs=40)],
      say='Thoát Hoan vào Thăng Long. Hắn chỉ thấy một cung điện trống. /// Lương thực đã được mang đi hết.'),
 dict(type='stage', bg='riverbank', label='SÔNG CẦU', zoom=1.1,
      cast=[dict(c='dongdoi', x=330, D=160, face=1, expr='scared'), dict(c='linhnguyen', x=760, D=165, face=-1, expr='angry', from_=1300, hands=[[.6, -.2, 'sword', -95]])],
      cards=[dict(t='THẤY CHỮ LÀ GIẾT', x=330, y=1175, at=2, col='#c4281f', tc='#fff', fs=32)],
      say='Không phải ai cũng rút kịp. Tháng 2, giặc vượt sông Cầu và bắt được nhiều lính Trần. {hạ: Thấy 2 chữ Sát Thát trên tay, chúng giết ngay.}'),
 dict(type='stage', bg='riverbank_dawn', label='BÃI THIÊN MẠC',
      cast=[dict(c='binhtrong', x=330, D=165, face=1, expr='angry'), dict(c='thoathoan', x=770, D=160, face=-1, expr='happy', at=1)],
      cards=[dict(t='DỤ PHONG VƯƠNG', x=330, y=1175, at=1, col='#f2dc8a', fs=34)],
      say='Cũng tháng ấy, tướng Trần Bình Trọng bị bắt ở bãi Thiên Mạc. Giặc dụ phong cho ông làm vương.'),
 dict(type='stage', bg='night', label='MA NƯỚC NAM', zoom=1.18,
      cast=[dict(c='binhtrong', x=540, D=180, face=1, expr='angry')],
      cards=[dict(t='THÀ LÀM MA NƯỚC NAM', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=38)],
      say='{chậm: Ông đáp, ta thà làm ma nước Nam, chứ không thèm làm vương đất Bắc.} Tin ấy truyền đến tận chỗ bạn nấp.'),
 dict(type='stage', bg='village_night', label='VƯỜN KHÔNG NHÀ TRỐNG', zoom=1.12,
      cast=[dict(c='ban', x=540, D=170, face=1, expr='scared', hands=[SP])],
      say='Bạn sống những tháng ấy giữa vườn không nhà trống. Giặc đến đâu cũng không có gạo, không có người.'),
 dict(type='stage', bg='hall_dim', label='MÙA HÈ',
      cast=[dict(c='thoathoan', x=540, D=170, face=1, expr='sad')],
      cards=[dict(t='NẮNG NÓNG + DỊCH BỆNH', x=540, y=1175, at=0, col='#f2dc8a', fs=36)],
      say='Rồi mùa hè tới. Quân giặc gặp nắng nóng và dịch bệnh. /// Chính Thoát Hoan cũng phải tính đường rút.'),
 dict(type='melee', label='PHẢN CÔNG',
      say='Tháng 5, quân Trần phản công. Trận Hàm Tử thắng trước. Lần này, bạn cầm giáo xông lên.'),
 dict(type='victory', label='CHƯƠNG DƯƠNG', hero='ban', side='dongdoi',
      say='Tháng 6, quân Trần thắng lớn ở Chương Dương. Tướng giặc Toa Đô cũng tử trận trong mùa hè ấy.'),
 dict(type='stage', bg='night', label='ỐNG ĐỒNG', zoom=1.12,
      cast=[dict(c='thoathoan', x=540, D=165, face=-1, expr='scared', from_=-200)],
      cards=[dict(t='TRỐN TRONG ỐNG ĐỒNG', x=540, y=1175, at=1, col='#f2dc8a', fs=38)],
      say='Thoát Hoan tháo chạy về nước. Sử chép hắn phải nấp trong ống đồng cho lính khiêng đi.'),
 dict(type='stage', bg='paper', label='KẾT QUẢ',
      cards=[dict(t='~5 VẠN QUÂN NGUYÊN BỊ BẮT', x=540, y=760, at=0, col='#c4281f', tc='#fff', fs=36), dict(t='CHỪNG 6 THÁNG', x=540, y=900, at=1, col='#f2dc8a', fs=40)],
      say='Theo một số tài liệu, khoảng 5 vạn quân Nguyên bị bắt. Cuộc chiến kéo dài chừng 6 tháng.'),
 dict(type='stage', bg='hall', label='HÒM THƯ XIN HÀNG', zoom=1.1,
      cast=[dict(c='quan', x=540, D=160, face=1, expr='scared', hands=[[.6, -.2, 'scroll']])],
      cards=[dict(t='ĐỐT HẾT', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=44)],
      say='Thắng trận, triều đình bắt được cả một hòm thư xin hàng của quan lại. /// Thượng hoàng sai đốt hết, để những người ấy yên lòng.'),
 dict(type='stage', bg='village', label='VỀ LÀNG', zoom=1.14,
      cast=[dict(c='ban', x=540, D=170, face=1, expr='happy', from_=-150)],
      cards=[dict(t='SÁT THÁT', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=44)],
      say='Bạn về làng. {chậm: Thư xin hàng thì đốt được. Còn 2 chữ trên tay bạn, không ai đốt được.}'),
 dict(type='stage', bg='village', label='NẾU LÀ BẠN?', ask=True, gap=1.2, qx=880, zoom=1.15,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='normal')],
      cards=[dict(t='BẠN CÓ DÁM?', x=540, y=1175, at=0, col='#1a1a1a', tc='#fff', fs=42)],
      say='{cao: Nếu là bạn, bạn có dám thích 2 chữ ấy lên tay không?} [nghỉ 1.2] Bình luận cho mình biết nhé.'),
 dict(type='ke', label='TẬP SAU', board='NĂM 1789|ĂN TẾT SỚM?', expr='happy',
      say='Tập sau: bạn là lính Tây Sơn năm 1789, và bạn được ăn Tết sớm giữa đường hành quân.'),
]
for s in S:
    for c in s.get('cast', []):
        if 'from_' in s and False: pass
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='CHIẾN SỬ KÝ', badge='BẠN LÀ LÍNH · 1285', hook_text='BẠN CÓ 2 CHỮ TRÊN TAY',
          next='Tập sau: bạn là lính Tây Sơn năm 1789', cta='THEO DÕI CHIẾN SỬ KÝ', tts=True, speed=0.9, tag='csk-bl1', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
