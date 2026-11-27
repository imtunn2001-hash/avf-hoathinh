import json, re
# CHIEN SU KY - BAN LA LINH, tap 3: linh phao, Dien Bien Phu thang 1-3/1954 (keo phao vao, keo phao ra).
# Hat nhan: keo phao vao mat chung 7 dem; chieu 26/1/1954 phao da san sang ban thi co lenh "keo phao ra" (doi phuong cham danh nhanh -> danh chac).
# Nguon: Nhan Dan special "Keo phao vao, keo phao ra" (hoi ky Vo Nguyen Giap: chieu 26/1 chuan bi ban, lenh 17 gio keo ra, "quan lenh nhu son",
#        sau Tet mo duong o to keo phao, cong su chiu dan 105/155, khai hoa 17h10 13/3); Nhan Dan special hoi ky Pham Ngoc Mau (duong rong chung 3 m,
#        dung den hang tram nguoi 1 khau, cam den lua, nguy trang; keo ra kho hon vi dich biet duong, may bay ban pha; doi phuong cham);
#        VOH 5/2026 (phao 105 nang 2,4 tan, duong ~15 km keo tay, toi go, chen banh, 7 dem 8 ngay, Ho keo phao - Hoang Van);
#        Thuong hieu & Cong luan 2014 (2,5 tan, duong moi 15 km rong 3 m, G du kien 25/1 hoan 24 gio, toi 26/1 keo ra);
#        Wikipedia Charles Piroth + Bao Phap luat (Piroth tu sat 15/3/1954 vi khong dap duoc phao Viet Minh);
#        VietNamNet 2024 + Wikipedia (To Vinh Dien lay than chen phao khi phao truot doc; 7 dem moi khau; may bay Phap nem bom).
NAMES = ['Điện Biên Phủ', 'Mường Thanh', 'Võ Nguyên Giáp', 'Tô Vĩnh Diện', 'Hoàng Vân', 'Hò kéo pháo', 'Him Lam', 'Bạch Đằng', 'Pi-rốt']


def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x


# BAN: dung cau hinh co dinh, chi doi ao sang mau xanh bo doi 1954
BAN = dict(tag='BẠN', skin='#e2ae80', hair='#140f0c', hair_style='band', band='#c4281f', outfit='#5e6b3c', outfit2='#434d2a', trim='#c4281f', mark='dirt')
DONG = dict(tag='ĐỒNG ĐỘI', skin='#d9a070', hair='#140f0c', hair_style='cap', hat='#5e6b3c', outfit='#5e6b3c', outfit2='#434d2a', trim='#d8a93a')
CAST = {
    'ban': BAN, 'linhviet': BAN,
    'dongdoi': DONG, 'linhviet2': dict(DONG, tag='ĐỒNG ĐỘI'),
    'tvd': dict(DONG, tag='TÔ VĨNH DIỆN', skin='#d39a66'),
    'dongdoi2': dict(DONG, tag='ĐỒNG ĐỘI', skin='#cf9262'),
}
G = 1290
SHOVEL = [.7, -.2, 'shovel', 60]
FLAG = [.55, -.9, 'flag', -80]

S = [
 dict(type='stage', bg='night', label='', zoom=1.16,
      cast=[dict(c='ban', x=540, D=180, face=1, expr='angry')],
      cards=[dict(t='LỆNH: KÉO RA', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=46)],
      say='Bạn kéo pháo 7 đêm, rồi phải kéo ra. // {chậm: Lệnh ấy tới đúng chiều pháo đã sẵn sàng bắn.}'),
 dict(type='stage', bg='night', label='NĂM 1954', zoom=1.1,
      cast=[dict(c='ban', x=540, D=165, face=1, expr='normal')],
      cards=[dict(t='ĐIỆN BIÊN PHỦ', x=540, y=1175, at=1, col='#f2dc8a', fs=40)],
      say='Bạn là lính pháo, tháng 1 năm 1954, ở Điện Biên Phủ. Quân Pháp đóng chặt trong lòng chảo Mường Thanh.'),
 dict(type='stage', bg='riverbank_dawn', label='PHÁO 105 LY', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='surprised'), dict(c='dongdoi', x=760, D=155, face=-1, expr='normal', at=1)],
      cards=[dict(t='HƠN 2 TẤN', x=330, y=1175, at=0, col='#c4281f', tc='#fff', fs=44)],
      say='Khẩu pháo 105 ly của bạn nặng hơn 2 tấn. Xe chỉ kéo được tới cửa rừng. Đoạn còn lại phải kéo bằng tay.'),
 dict(type='stage', bg='riverbank_dawn', label='ĐƯỜNG MỚI MỞ', zoom=1.12,
      cast=[dict(c='ban', x=420, D=160, face=1, expr='normal', from_=-200), dict(c='dongdoi', x=700, D=150, face=1, expr='normal', from_=-400, tag=False)],
      cards=[dict(t='KHOẢNG 15 KM', x=540, y=1175, at=0, col='#f2dc8a', fs=42)],
      say='Con đường kéo pháo mới mở dài khoảng 15 km. Lòng đường rộng chừng 3 mét, vắt qua núi cao.'),
 dict(type='stage', bg='night', label='KHÔNG CÓ MÁY', zoom=1.14,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='angry'), dict(c='dongdoi', x=760, D=155, face=-1, expr='angry', at=1)],
      cards=[dict(t='DÂY + TỜI GỖ', x=330, y=1175, at=1, col='#f2dc8a', fs=42)],
      say='Bạn không có máy kéo. Chỉ có dây chão, tời làm bằng gỗ rừng, và đôi vai.'),
 dict(type='stage', bg='night', label='CHÈN BÁNH', zoom=1.18,
      cast=[dict(c='ban', x=540, D=180, face=1, expr='scared', hands=[[.6, -.1, 'mallet', 40]])],
      cards=[dict(t='NHÍCH 1 CHÚT, CHÈN', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=38)],
      say='Pháo nhích lên một chút, bạn phải chèn bánh ngay. {hạ: Trượt một lần là pháo lao xuống vực.}'),
 dict(type='stage', bg='night', label='LÊN DỐC CAO', zoom=1.12,
      cast=[dict(c='dongdoi', x=300, D=150, face=1, expr='angry'), dict(c='ban', x=540, D=165, face=1, expr='angry', at=1), dict(c='dongdoi2', x=790, D=150, face=1, expr='angry', at=1, tag=False)],
      cards=[dict(t='HÀNG TRĂM NGƯỜI', x=360, y=1175, at=1, col='#f2dc8a', fs=40)],
      say='Lên dốc cao, một khẩu pháo cần tới hàng trăm người cùng kéo.'),
 dict(type='stage', bg='village_night', label='CẤM ĐÈN LỬA', zoom=1.12,
      cast=[dict(c='ban', x=540, D=170, face=1, expr='normal')],
      cards=[dict(t='NGỤY TRANG PHÁO', x=540, y=1175, at=1, col='#1a1a1a', tc='#fff', fs=34)],
      say='Bạn kéo trong đêm, cấm đèn lửa. Gần sáng, cả đơn vị chặt cây rừng phủ kín pháo.'),
 dict(type='stage', bg='night', label='HÒ KÉO PHÁO', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='happy'), dict(c='dongdoi', x=760, D=155, face=-1, expr='happy', at=1)],
      cards=[dict(t='HÒ KÉO PHÁO', x=330, y=1175, at=0, col='#f2dc8a', fs=44)],
      say='Tiếng hò giữ nhịp cho cả trăm người cùng dồn sức. Nhạc sĩ Hoàng Vân viết bài Hò kéo pháo, về chính những đêm như thế.'),
 dict(type='stage', bg='riverbank_dawn', label='VÀO TRẬN ĐỊA', zoom=1.14,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='happy')],
      cards=[dict(t='CHỪNG 7 ĐÊM', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=44)],
      say='Mất chừng 7 đêm, khẩu pháo của bạn mới vào tới trận địa.'),
 dict(type='stage', bg='riverbank_dawn', label='26/1/1954', zoom=1.12,
      cast=[dict(c='ban', x=540, D=170, face=1, expr='angry')],
      icons=[dict(icon='clock', x=830, y=860, s=1.2, at=0)],
      cards=[dict(t='CHỜ LỆNH BẮN', x=540, y=1175, at=1, col='#f2dc8a', fs=42)],
      say='Chiều ngày 26 tháng 1, pháo đã ở vị trí. Bạn chỉ chờ lệnh bắn loạt đầu tiên.'),
 dict(type='stage', bg='riverbank_dawn', label='ĐIỆN THOẠI', zoom=1.18,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='surprised')],
      icons=[dict(icon='phone', x=830, y=860, s=1.2, at=0)],
      cards=[dict(t='KÉO PHÁO RA', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=46)],
      say='Điện thoại báo lệnh mới. /// {chậm: Kéo pháo ra, về chỗ tập kết cũ, đợi lệnh.}'),
 dict(type='stage', bg='night', label='QUÂN LỆNH', zoom=1.16,
      cast=[dict(c='ban', x=540, D=180, face=1, expr='sad')],
      cards=[dict(t='QUÂN LỆNH NHƯ SƠN', x=540, y=1175, at=1, col='#1a1a1a', tc='#fff', fs=38)],
      say='Bảy đêm mồ hôi, giờ phải làm ngược lại. {hạ: Người lính như bạn chỉ có một câu: quân lệnh như sơn.}'),
 dict(type='stage', bg='village', label='ĐỔI CÁCH ĐÁNH', zoom=1.1,
      cast=[dict(c='dongdoi', x=540, D=165, face=1, expr='normal')],
      icons=[dict(icon='map', x=830, y=860, s=1.2, at=0)],
      cards=[dict(t='ĐÁNH CHẮC', x=540, y=1175, at=1, col='#f2dc8a', fs=46)],
      say='Đại tướng Võ Nguyên Giáp đã đổi cách đánh. Bỏ đánh nhanh giải quyết nhanh. Chuyển sang đánh chắc tiến chắc.'),
 dict(type='stage', bg='night', label='KÉO RA', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=-1, expr='scared'), dict(c='dongdoi', x=760, D=155, face=-1, expr='scared', at=1)],
      cards=[dict(t='KHÓ HƠN KÉO VÀO', x=330, y=1175, at=1, col='#c4281f', tc='#fff', fs=38)],
      say='Kéo ra còn khó hơn kéo vào. Địch đã biết đường, máy bay bắn phá dọc tuyến.'),
 dict(type='stage', bg='night', label='BẠN CHỌN?', ask=True, gap=1.2, qx=880, zoom=1.15,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='scared')],
      cards=[dict(t='BUÔNG HAY CHÈN?', x=540, y=1175, at=1, col='#1a1a1a', tc='#fff', fs=40)],
      say='Một khẩu pháo nặng hàng tấn tuột dốc, lao về phía vực. Buông tay thì bạn sống. Lao vào chèn thì pháo còn. {cao: Bạn chọn gì?} [nghỉ 1.2]'),
 dict(type='stage', bg='night', label='TÔ VĨNH DIỆN', zoom=1.14,
      cast=[dict(c='tvd', x=540, D=170, face=1, expr='angry')],
      cards=[dict(t='LẤY THÂN CHÈN PHÁO', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=38)],
      say='Có người đã chọn lao vào. Anh Tô Vĩnh Diện lấy thân mình chèn pháo, và hy sinh. {chậm: Khẩu pháo được giữ lại.}'),
 dict(type='stage', bg='riverbank_dawn', label='SAU TẾT', zoom=1.12,
      cast=[dict(c='ban', x=330, D=165, face=1, expr='angry', hands=[SHOVEL]), dict(c='dongdoi', x=760, D=155, face=-1, expr='normal', at=1, hands=[SHOVEL])],
      cards=[dict(t='ĐÀO HẦM PHÁO', x=330, y=1175, at=1, col='#f2dc8a', fs=42)],
      say='Sau Tết, đường mới mở cho ô tô kéo pháo. Bạn đào hầm cho pháo, chịu được cả đạn 155 ly của Pháp.'),
 dict(type='stage', bg='night', label='13/3/1954', zoom=1.14,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='angry')],
      cards=[dict(t='KHAI HỎA', x=540, y=1175, at=0, col='#c4281f', tc='#fff', fs=48)],
      say='Chiều ngày 13 tháng 3 năm 1954, pháo ta khai hỏa vào Him Lam. Him Lam thất thủ ngay trong đêm.'),
 dict(type='stage', bg='night', label='PHÁO TRONG HẦM', zoom=1.14,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='happy')],
      cards=[dict(t='PHÁO PHÁP BẤT LỰC', x=540, y=1175, at=1, col='#f2dc8a', fs=38)],
      say='Pháo của bạn bắn từ trong hầm, pháo binh Pháp không dập nổi. // Ngày 15 tháng 3, chỉ huy pháo binh Pháp là Pi-rốt tự sát.'),
 dict(type='stage', bg='riverbank_dawn', label='7/5/1954', zoom=1.12,
      cast=[dict(c='ban', x=330, D=170, face=1, expr='happy', hands=[FLAG]), dict(c='dongdoi', x=760, D=155, face=-1, expr='happy', at=1)],
      cards=[dict(t='56 NGÀY ĐÊM', x=330, y=1175, at=1, col='#f2dc8a', fs=44)],
      say='Ngày 7 tháng 5, sau 56 ngày đêm, Bộ chỉ huy tập đoàn cứ điểm bị bắt sống.'),
 dict(type='stage', bg='riverbank_dawn', label='BƯỚC LÙI', zoom=1.16,
      cast=[dict(c='ban', x=540, D=180, face=1, expr='happy', hands=[FLAG])],
      cards=[dict(t='LÙI ĐỂ THẮNG', x=540, y=1175, at=1, col='#c4281f', tc='#fff', fs=44)],
      say='Tháng 1, kéo pháo ra trông như lùi một bước. Nhờ lùi, pháo của bạn mới có hầm. {chậm: Tháng 5, bước lùi ấy thành chiến thắng.}'),
 dict(type='stage', bg='night', label='NẾU LÀ BẠN?', ask=True, gap=1.2, qx=880, zoom=1.15,
      cast=[dict(c='ban', x=540, D=175, face=1, expr='normal')],
      cards=[dict(t='BẠN CÓ CAM LÒNG?', x=540, y=1175, at=0, col='#1a1a1a', tc='#fff', fs=40)],
      say='{cao: Nếu là bạn, kéo pháo vào 7 đêm, bạn có cam lòng kéo ra không?} [nghỉ 1.2] Bình luận và theo dõi tập sau nhé.'),
 dict(type='ke', label='TẬP SAU', board='NĂM 1288|CẮM CỌC', expr='happy',
      say='Tập sau: bạn là lính cắm cọc trên sông Bạch Đằng năm 1288.'),
]
for s in S:
    for c in s.get('cast', []):
        if 'from_' in c: c['from'] = c.pop('from_')
        c.setdefault('y', G)
    s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='CHIẾN SỬ KÝ', badge='BẠN LÀ LÍNH · 1954', hook_text='BẠN KÉO PHÁO VÀO, RỒI RA',
          next='Tập sau: bạn là lính cắm cọc năm 1288', cta='THEO DÕI CHIẾN SỬ KÝ', tts=True, speed=0.9, tag='csk-bl3', cast=CAST, shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu', len(sp['hook_text']), 'ky tu hook')
