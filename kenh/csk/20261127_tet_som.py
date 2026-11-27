import json, re
# CHIEN SU KY - BAN LA LINH, tap 2: linh Tay Son, Tet Ky Dau 1789 (Ngoc Hoi - Dong Da).
# Hat nhan: Tet nam ay cua ban chi co 1 bua khao quan ngay 30 thang Chap o Tam Diep; toi 30 len duong, giao thua la dem hanh quan,
#           trong khi o Thang Long quan Thanh mo tiec don xuan.
# Nguon: Hoang Le nhat thong chi hoi 14 (Tam Diep 30 thang Chap, "3 suat dinh lay 1", van ghep rom dap nuoc 10 nguoi khenh 1 buc,
#        Ha Hoi nua dem mong 3, trua vao Thang Long); Dai Nam liet truyen qua Znews (doi van go, ao bao sam den khoi thuoc sung, cau gay);
#        Giaoduc.net.vn (len ngoi 25/11 Mau Than = 22/12/1788, Nghe An hon 10 ngay, quan Thanh mo tiec don xuan); Bao Nghe An (20 thang Chap = 15/1/1789 toi Tam Diep).
NAMES = ['Quang Trung', 'Nguyễn Huệ', 'Phú Xuân', 'Tây Sơn', 'Thăng Long', 'Nghệ An', 'Tam Điệp', 'Ninh Bình', 'Tôn Sĩ Nghị', 'Hà Hồi', 'Ngọc Hồi',
         'Mậu Thân', 'Hoàng Lê nhất thống chí', 'Điện Biên Phủ']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


BAN = dict(tag='BẠN', skin='#e2ae80', hair='#140f0c', hair_style='band', band='#c4281f', outfit='#6a5534', outfit2='#4c3c24', trim='#c4281f', mark='dirt')
DONG = dict(tag='ĐỒNG ĐỘI', skin='#d9a070', hair='#140f0c', hair_style='khan', hat='#3a3a2a', outfit='#5a6a44', outfit2='#3e4a2e', trim='#d8a93a')
THANH = dict(tag='QUÂN THANH', skin='#e8b588', hair='#16120f', hair_style='helmet', helm='#5a5a66', outfit='#34507a', outfit2='#263c5c', trim='#d8a93a', scales=True)
CAST = {
    'ban': BAN, 'linhviet': BAN,                                  # canh tran melee: linhviet = BAN
    'dongdoi': DONG, 'linhviet2': dict(DONG, tag='ĐỒNG ĐỘI'),
    'linhhan': THANH, 'linhthanh': THANH,
    'me': dict(tag='MẸ BẠN', skin='#d9a77a', hair='#9a9690', hair_style='bun', outfit='#5a4a3a', outfit2='#40342a', trim='#c8a24a'),
    'quangtrung': dict(tag='VUA QUANG TRUNG', skin='#dca476', hair='#140f0c', hair_style='khan', hat='#c4281f', outfit='#a8231b', outfit2='#7a1812', trim='#d8a93a', beard=True, mark='brow'),
    'quangtrung_den': dict(tag='VUA QUANG TRUNG', skin='#dca476', hair='#140f0c', hair_style='khan', hat='#3a2a22', outfit='#4a2a24', outfit2='#2e1a16', trim='#8a7a5a', beard=True, mark='brow'),
    'tonsinghi': dict(tag='TÔN SĨ NGHỊ', skin='#ecbd8c', hair='#16120f', hair_style='helmet', helm='#a8862e', outfit='#2c4a7a', outfit2='#1f365a', trim='#d8a93a', mark='mustache'),
}
G = 1290
SP = [.55, -.1, 'spear', -70]
BOWL = [.6, -.05, 'bowl']

S = [
 dict(type='stage', bg='night', label='', zoom=1.16,
      cast=[dict(c='ban', x=540, D=180, face=1, expr='angry', hands=[SP])],
      cards=[dict(t='ĐÊM 30 TẾT', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=46)],
      say='Đêm 30 Tết, giặc nâng chén mừng xuân, định mồng 6 mới đánh bạn. {chậm: Còn bạn vừa ăn xong cái Tết của mình, và đang đi về phía chúng.}'),
 dict(type='stage', bg='village', label='NĂM 1789',
      cast=[dict(c='ban', x=540, D=165, face=1, expr='normal', hands=[SP])],
      say='Bạn là lính Tây Sơn, mùa xuân năm 1789. Quân Thanh đã chiếm Thăng Long từ cuối năm trước.'),
 dict(type='stage', bg='hall', label='PHÚ XUÂN', zoom=1.1,
      cast=[dict(c='quangtrung', x=540, D=170, face=1, expr='angry', hands=[[.6, -.2, 'sword', -95]])],
      cards=[dict(t='LÊN NGÔI 1788', x=540, y=1175, at=1, col='#f2dc8a', fs=36)],
      say='Ngày 22 tháng 12 năm 1788, Nguyễn Huệ lên ngôi ở Phú Xuân, hiệu Quang Trung, rồi kéo quân ra Bắc.'),
 dict(type='stage', bg='village', label='KÉN LÍNH Ở NGHỆ AN', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='surprised'), dict(c='me', x=760, D=150, face=-1, expr='sad', at=1)],
      cards=[dict(t='3 SUẤT ĐINH LẤY 1', x=330, y=1175, at=1, col='#c4281f', tc='#fff', fs=36)],
      say='Bạn là trai xứ Nghệ. Quân dừng ở Nghệ An hơn 10 ngày để kén lính. Cứ 3 suất đinh thì lấy 1 người. /// Người ấy là bạn.'),
 dict(type='stage', bg='village_night', label='HƠN 1 VẠN QUÂN', zoom=1.14,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='normal', hands=[SP]), dict(c='dongdoi', x=760, D=160, face=-1, expr='normal', from_=1300, at=1, hands=[SP])],
      cards=[dict(t='HƠN 1 VẠN QUÂN', x=330, y=1175, at=1, col='#f2dc8a', fs=34)],
      say='Chưa mấy lúc, đất Nghệ đã có hơn 1 vạn quân như bạn.'),
 dict(type='army_march', label='QUÂN THANH', enemy='linhthanh', leader='tonsinghi',
      say='Tôn Sĩ Nghị cầm quân Thanh đóng ở Thăng Long. Sử ta chép đạo quân sang đánh lên tới 29 vạn.'),
 dict(type='stage', bg='riverbank_dawn', label='NÚI TAM ĐIỆP', zoom=1.1,
      cast=[dict(c='ban', x=420, D=160, face=1, expr='normal', from_=-200, hands=[SP]), dict(c='dongdoi', x=700, D=150, face=1, expr='normal', from_=-400, tag=False, hands=[SP])],
      cards=[dict(t='20 THÁNG CHẠP', x=420, y=1175, at=1, col='#f2dc8a', fs=40)],
      say='Ngày 20 tháng Chạp, bạn tới núi Tam Điệp.'),
 dict(type='stage', bg='village', label='30 THÁNG CHẠP', zoom=1.12,
      cast=[dict(c='ban', x=320, D=165, face=1, expr='surprised', hands=[BOWL]), dict(c='quangtrung', x=760, D=160, face=-1, expr='happy', at=1)],
      cards=[dict(t='ĂN TẾT TRƯỚC', x=320, y=1175, at=1, col='#c4281f', tc='#fff', fs=42)],
      say='Ngày 30 tháng Chạp, nhà vua mở tiệc khao quân. Ông bảo cả quân hãy cúng Tết trước.'),
 dict(type='stage', bg='village', label='LỜI HẸN', zoom=1.16,
      cast=[dict(c='quangtrung', x=540, D=175, face=1, expr='angry', hands=[[.6, -.2, 'sword', -95]])],
      cards=[dict(t='HẸN MỒNG 7', x=540, y=1175, at=1, col='#f2dc8a', fs=36)],
      say='Sử chép lời hẹn của nhà vua. {chậm: Tối 30 lên đường, mồng 7 năm mới vào Thăng Long mở tiệc ăn mừng.}'),
 dict(type='stage', bg='village_night', label='TẾT CỦA BẠN', zoom=1.18,
      cast=[dict(c='ban', x=540, D=180, face=1, expr='sad', hands=[BOWL])],
      cards=[dict(t='TẾT CHỈ 1 BỮA', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=44)],
      say='Vậy là Tết năm ấy của bạn chỉ có 1 bữa. {hạ: Không giao thừa ở nhà, không mồng 1 bên mẹ.}'),
 dict(type='stage', bg='hall_dim', label='Ở THĂNG LONG', zoom=1.12,
      cast=[dict(c='tonsinghi', x=540, D=170, face=1, expr='happy', hands=[BOWL])],
      cards=[dict(t='MỒNG 6 MỚI ĐÁNH', x=540, y=1175, at=1, col='#f2dc8a', fs=38)],
      say='Ở Thăng Long, quân Thanh định qua Tết, mồng 6 mới tiến quân. Giờ chúng mở tiệc đón xuân, canh phòng lơi lỏng. /// Hai bên, hai tờ lịch.'),
 dict(type='stage', bg='night', label='GIAO THỪA', zoom=1.12,
      cast=[dict(c='ban', x=420, D=165, face=1, expr='angry', from_=-200, hands=[SP]), dict(c='dongdoi', x=700, D=150, face=1, expr='angry', from_=-400, tag=False, hands=[SP])],
      say='Đêm giao thừa trời tối đen, bạn lặng lẽ đi giữa hàng quân. Ở quê, mẹ bạn thắp hương một mình. {chậm: Mâm cơm Tết ở Tam Điệp chưa kịp nguội, bạn đã đi xa.}'),
 dict(type='stage', bg='village_night', label='HÀ HỒI · MỒNG 3', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='angry', hands=[SP]), dict(c='linhthanh', x=760, D=160, face=-1, expr='scared', at=2)],
      cards=[dict(t='XIN RA HÀNG', x=330, y=1175, at=2, col='#1a1a1a', tc='#fff', fs=40)],
      say='Nửa đêm mồng 3, quân bạn lặng lẽ vây đồn Hà Hồi. Loa gọi hàng vang lên. Quân giữ đồn rụng rời, xin ra hàng.'),
 dict(type='stage', bg='riverbank_dawn', label='NGỌC HỒI · MỒNG 5', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='scared'), dict(c='dongdoi', x=760, D=160, face=-1, expr='normal', at=1)],
      cards=[dict(t='VÁN GHÉP + RƠM ƯỚT', x=330, y=1175, at=1, col='#f2dc8a', fs=36)],
      say='Mờ sáng mồng 5, trước đồn Ngọc Hồi. Ba tấm ván ghép thành một bức, ngoài phủ rơm dấp nước.'),
 dict(type='stage', bg='riverbank_dawn', label='10 NGƯỜI MỘT BỨC', zoom=1.14,
      cast=[dict(c='ban', x=540, D=170, face=1, expr='angry')],
      cards=[dict(t='20 BỨC VÁN', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=42)],
      say='Cứ 10 người khênh một bức, tất cả 20 bức. Bạn ở hàng đầu một bức.'),
 dict(type='stage', bg='riverbank_dawn', label='BẠN CHỌN?', ask=True, gap=1.2, qx=880, zoom=1.15,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='scared')],
      cards=[dict(t='BẠN LÀM GÌ?', x=540, y=1175, at=1, col='#1a1a1a', tc='#fff', fs=40)],
      say='Trong đồn, giặc bắn ra. Bỏ ván mà chạy, bạn có thể sống. Nhưng 9 người kia sẽ hở lưng. Khênh tiếp thì bạn là người gần đồn nhất. {cao: Bạn chọn đường nào?} [nghỉ 1.2]'),
 dict(type='stage', bg='riverbank_dawn', label='KHÊNH TIẾP', zoom=1.14,
      cast=[dict(c='ban', x=540, D=170, face=1, expr='angry')],
      say='Bạn khênh tiếp. Một bức ván thiếu người là nghiêng, cả 10 người cùng hở. {chậm: Bạn đi, vì 9 người kia cũng đang đi.}'),
 dict(type='melee', label='PHÁ ĐỒN',
      say='Tới sát lũy, cả toán bỏ ván xuống, cầm binh khí xông vào. Đồn Ngọc Hồi vỡ.'),
 dict(type='stage', bg='riverbank_dawn', label='ÁO BÀO SẠM ĐEN', zoom=1.12,
      cast=[dict(c='quangtrung_den', x=540, D=170, face=1, expr='angry', hands=[[.6, -.2, 'sword', -95]])],
      cards=[dict(t='KHÓI THUỐC SÚNG', x=540, y=1175, at=1, col='#1a1a1a', tc='#fff', fs=40)],
      say='Nhà vua cưỡi voi đốc thúc phía sau. Sử chép áo bào của ông sạm đen vì khói thuốc súng.'),
 dict(type='stage', bg='riverbank', label='CẦU PHAO ĐỨT', zoom=1.1,
      cast=[dict(c='tonsinghi', x=540, D=165, face=-1, expr='scared', from_=-200)],
      cards=[dict(t='BỎ CHẠY VỀ BẮC', x=540, y=1175, at=1, col='#f2dc8a', fs=40)],
      say='Tôn Sĩ Nghị bỏ chạy về phương bắc. Cầu phao qua sông đứt, rất nhiều quân Thanh chết đuối.'),
 dict(type='victory', label='TRƯA MỒNG 5', hero='ban', side='dongdoi',
      say='Giữa trưa mồng 5, quân Tây Sơn tiến vào Thăng Long. {chậm: Sớm hơn lời hẹn 2 ngày, và trước ngày giặc định ra quân 1 ngày.}'),
 dict(type='stage', bg='village', label='SAU TRẬN', zoom=1.14,
      cast=[dict(c='ban', x=540, D=170, face=1, expr='happy', hands=[SP])],
      cards=[dict(t='MỒNG 6', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=46)],
      say='Đêm 30, giặc ăn Tết và chờ mồng 6. Bạn bỏ cái Tết của mình. {chậm: Mồng 6 tới, chúng không còn ở Thăng Long để đánh ai nữa.}'),
 dict(type='stage', bg='village', label='NẾU LÀ BẠN?', ask=True, gap=1.2, qx=880, zoom=1.15,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='normal')],
      cards=[dict(t='BẠN CÓ ĐI?', x=540, y=1175, at=0, col='#1a1a1a', tc='#fff', fs=42)],
      say='{cao: Nếu là bạn, bạn có bỏ cái Tết ở nhà để hành quân đêm giao thừa không?} [nghỉ 1.2] Bình luận và theo dõi tập sau nhé.'),
 dict(type='ke', label='TẬP SAU', board='NĂM 1954|KÉO PHÁO', expr='happy',
      say='Tập sau: bạn là lính kéo pháo ở Điện Biên Phủ năm 1954.'),
]
for s in S:
    for c in s.get('cast', []):
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='CHIẾN SỬ KÝ', badge='BẠN LÀ LÍNH · 1789', hook_text='BẠN ĂN TẾT CHỈ 1 BỮA',
          next='Tập sau: bạn là lính kéo pháo năm 1954', cta='THEO DÕI CHIẾN SỬ KÝ', tts=True, speed=0.9, tag='csk-bl2', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
