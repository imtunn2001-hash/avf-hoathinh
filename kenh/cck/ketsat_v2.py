"""CCK dang cck2 (chu chot 28/11 23:24): Vết máu trên két sắt – Vĩnh Yên 2007, viet lai: tap 90–120 giay, khong tom tat,
nhieu nhan vat + boi canh, moi cau 1 hinh dung loi, nhac theo tinh tiet (mood). python3 ketsat_v2.py <thu_muc_ra>
Tu lieu nhu ketsat.py: Tiền Phong 16/1/2007, Dân trí 16/1/2007, Tiền Phong 28/8/2007, Tiền Phong 3/8/2011, Công an nhân dân 11/1/2009.
Khong ve nan nhan, khong ta cach gay an. Tap nay = PHAN 1 (truoc va ngay xay ra vu an, toi luc cong an vao nha).
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CAST = {
    'bong': dict(tag='?', skin='#d6a272', hair='#1a1410', hair_style='side', outfit='#3a4a5a', outfit2='#2a3644', trim='#e8e2d2', mark='brow'),
    'dtv': dict(tag='ĐIỀU TRA VIÊN', skin='#e0aa7c', hair='#1a1410', hair_style='cap', hat='#3a5a3a', outfit='#4a6a44', outfit2='#36502f', trim='#d8a93a', mark='glasses'),
    'ts': dict(tag='TRINH SÁT', skin='#e0aa7c', hair='#1a1410', hair_style='side', outfit='#6a6a5a', outfit2='#4e4e42', trim='#3a2a1a'),
    'ts2': dict(tag='TRINH SÁT', skin='#d9a070', hair='#1a1410', hair_style='cap', hat='#3a5a3a', outfit='#4a6a44', outfit2='#36502f', trim='#d8a93a'),
    'phapy': dict(tag='PHÁP Y', skin='#e0aa7c', hair='#3a3430', hair_style='side', outfit='#e8e8e2', outfit2='#c8c8c0', trim='#2e6ab0', mark='glasses'),
    'hangxom': dict(tag='HÀNG XÓM', skin='#d9a070', hair='#1a1410', hair_style='bun', outfit='#7a5a6a', outfit2='#5a4250', trim='#3a2a1a'),
    'hangxom2': dict(tag='HÀNG XÓM', skin='#d29a6a', hair='#5a5048', hair_style='nonla', outfit='#5a6a4a', outfit2='#44503a', trim='#3a2a1a'),
    'xeom': dict(tag='XE ÔM', skin='#c98f60', hair='#1a1410', hair_style='cap', hat='#2a4a7a', outfit='#6a5a3a', outfit2='#4e422a', trim='#3a2a1a'),
    'nguoinha': dict(tag='NGƯỜI NHÀ', skin='#e0aa7c', hair='#1a1410', hair_style='side', outfit='#5a5a6a', outfit2='#44445a', trim='#3a2a1a'),
}
G = 1030  # mat san
P1 = [
 dict(type='stage', label='', bg='room', mood='soc', zoom=1.12,
      icons=[dict(icon='envelope', x=540, y=900, s=2.4, at=0), dict(icon='paper', x=380, y=1080, s=1.0, at=1), dict(icon='paper', x=540, y=1110, s=1.0, at=1), dict(icon='paper', x=700, y=1080, s=1.0, at=1)],
      cards=[dict(t='10.000 ĐÔ?', x=540, y=760, at=0, col='#f2dc8a'), dict(t='6 TỜ GIẤY CẮT', x=540, y=1240, at=1, col='#c4281f', tc='#fff')],
      say='Phong bì ghi 10.000 đô la. Mở ra chỉ có 6 tờ giấy cắt cho bằng tờ đô. /// Kẻ cầm nó đã gõ cửa một ngôi nhà ở Vĩnh Yên.'),
 dict(type='stage', label='SÁNG 12/1/2007', bg='street', mood='mo',
      extras=[dict(c='xeom', x0=-150, x1=1250, y=G + 40, D=120, v=110), dict(c='hangxom2', x0=1200, x1=-150, y=G + 30, D=110, v=70, at=1)],
      cast=[dict(c='bong', x=560, D=165, expr='normal', tag=False, **{'from': -220})], icons=[dict(icon='giftbag', x=760, y=980, s=1.3, at=1)],
      say='Sáng 12/1/2007, phường Liên Bảo, thành phố Vĩnh Yên. Phố vẫn đông người qua lại. Một thanh niên đứng trước cổng một ngôi nhà, tay xách túi quà.'),
 dict(type='stage', label='"CÔ ƠI!"', bg='street', mood='mo',
      cast=[dict(c='bong', x=420, D=165, expr='normal', tag=False), dict(c='hangxom', x=860, D=140, expr='surprised', face=-1, at=2)],
      icons=[dict(icon='key', x=640, y=880, s=1.0, at=1)],
      say='Hắn gọi to: "Cô ơi!". Cửa vẫn cài từ bên trong, không ai ra mở. Một người hàng xóm nhìn thấy hắn đứng đó khá lâu. /// Rồi hắn lặng lẽ bỏ đi.'),
 dict(type='items', label='NGƯỜI HÀNG XÓM NHỚ LẠI', mood='dieu_tra',
      items=[dict(icon='clock', t='CAO KHOẢNG 1,6 M', at=1), dict(icon='shirt', t='QUẦN BÒ, ÁO KHOÁC', at=2), dict(icon='footprint', t='GIÀY TRẮNG', at=3)],
      say='Về sau, báo chí đăng lại mô tả về người thanh niên ấy. Cao khoảng 1,6 mét, tóc ngắn. Mặc quần bò, áo phông, khoác thêm áo ngoài. Chân đi một đôi giày trắng.'),
 dict(type='stage', label='CHỦ NHÀ', bg='room', mood='mo',
      icons=[dict(icon='clock', x=300, y=760, s=1.5, at=0), dict(icon='car', x=780, y=1080, s=1.3, at=2), dict(icon='phone', x=300, y=1060, s=1.0, at=3)],
      cards=[dict(t='BÀ THỦ · 53 TUỔI', x=640, y=820, at=0, col='#f2dc8a'), dict(t='CHỒNG ĐI HÀ NỘI', x=600, y=960, at=2)],
      say='Chủ nhà là bà Lăng Thị Thủ, 53 tuổi. Chồng bà là lãnh đạo Sở Giao thông vận tải tỉnh. Hôm ấy ông đi họp ở Hà Nội. Trong nhà chỉ có một mình bà.'),
 dict(type='stage', label='14 GIỜ CHIỀU', bg='street', mood='cang',
      extras=[dict(c='hangxom2', x0=-120, x1=1200, y=G + 30, D=105, v=60)],
      cast=[dict(c='bong', x=600, D=170, expr='happy', tag=False, **{'from': 1300})], icons=[dict(icon='giftbag', x=380, y=980, s=1.3, at=1)],
      say='Khoảng 14 giờ chiều, người thanh niên ấy quay lại. Vẫn túi quà trên tay. Lần này cửa mở.'),
 dict(type='stage', label='LỜI GIỚI THIỆU', bg='room', mood='cang',
      cast=[dict(c='bong', x=330, D=165, expr='happy', tag=False)],
      cards=[dict(t='"SINH VIÊN"', x=720, y=800, at=0, col='#f2dc8a'), dict(t='HỌC GIAO THÔNG', x=720, y=930, at=1), dict(t='NGƯỜI QUEN?', x=720, y=1060, at=2, col='#c4281f', tc='#fff')],
      say='Hắn tự giới thiệu là sinh viên vừa ra trường. Hắn nói mình học Trường Trung cấp Giao thông. Hắn còn nói có người thân quen biết chồng bà.'),
 dict(type='items', label='LỜI NHỜ VẢ', mood='cang',
      items=[dict(icon='giftbag', t='QUÀ BIẾU', at=1), dict(icon='envelope', t='"10.000 ĐÔ"', at=2), dict(icon='paper', t='XIN MỘT CHỖ LÀM', at=3)],
      say='Rồi hắn đặt quà xuống, kèm một lời nhờ vả. Hắn nói có 10.000 đô la, muốn xin một chỗ làm. Quà biếu, người quen, chuyện xin việc. Đủ để chủ nhà không nghi ngờ.'),
 dict(type='stage', label='NGÔI NHÀ IM LẶNG', bg='room', mood='soc', night=True,
      icons=[dict(icon='clock', x=540, y=820, s=2.0, at=0)],
      say='Chuyện xảy ra sau đó mình sẽ không kể chi tiết. Bà Thủ bị sát hại ngay trong ngôi nhà của mình. /// Và kẻ lạ chưa rời đi ngay. Hắn còn lên tầng 2, nơi có một chiếc két sắt. Phần 2, mình kể tiếp.'),
]
P2 = [
 dict(type='stage', label='', bg='room', mood='cang', icons=[dict(icon='safe', x=540, y=960, s=2.2, at=0), dict(icon='corkscrew', x=680, y=820, s=1.2, at=0)],
      say='Một cái mở nút chai rượu, cạy vào một chiếc két sắt. Phần trước, kẻ lạ đã vào được nhà bà Thủ bằng một phong bì giả.'),
 dict(type='stage', label='TẦNG 2', bg='room', mood='cang',
      cast=[dict(c='bong', x=330, D=160, expr='angry', tag=False)],
      icons=[dict(icon='shirt', x=760, y=1040, s=1.1, at=0), dict(icon='safe', x=780, y=830, s=1.7, at=2), dict(icon='corkscrew', x=560, y=720, s=1.1, at=3)],
      say='Hắn rửa tay, lấy quần áo trong tủ thay ra. Rồi hắn lên tầng 2. Ở đó có một chiếc két sắt. Hắn cạy nó bằng một cái mở nút chai rượu. {chậm: Chiếc két không hề mở ra.}'),
 dict(type='stage', label='HẮN BỎ ĐI', bg='street', mood='cang',
      cast=[dict(c='bong', x=540, D=160, expr='scared', tag=False, **{'from': 520})],
      extras=[dict(c='hangxom', x0=980, y=G + 30, D=120)],
      icons=[dict(icon='shirt', x=260, y=1000, s=1.1, at=1), dict(icon='footprint', x=420, y=1060, s=.9, at=1), dict(icon='giftbag', x=180, y=1080, s=1.0, at=1)],
      say='Hắn vội vã bỏ đi. Bỏ lại bộ quần áo cũ, đôi giày, và cả túi quà mang theo từ sáng.'),
 dict(type='stage', label='CÔNG AN CÓ MẶT', bg='street', mood='dieu_tra',
      cast=[dict(c='dtv', x=300, D=170, expr='normal', **{'from': -220}), dict(c='ts', x=560, D=160, expr='normal', at=1, **{'from': -260}),
            dict(c='phapy', x=820, D=160, expr='normal', at=1, **{'from': 1320})],
      extras=[dict(c='hangxom', x0=1010, y=G + 20, D=105), dict(c='hangxom2', x0=60, y=G + 20, D=105)],
      icons=[dict(icon='car', x=880, y=1120, s=1.2, at=0)],
      say='Khi công an có mặt, hàng xóm đã đứng kín đầu ngõ. Điều tra viên, trinh sát và pháp y lần lượt vào nhà. Ngôi nhà còn đầy dấu vết.'),
 dict(type='stage', label='TRONG TÚI QUÀ', bg='room', mood='dieu_tra',
      cast=[dict(c='dtv', x=280, D=165, expr='surprised', hands=[(.6, -.3, 'magnifier')])],
      icons=[dict(icon='giftbag', x=560, y=1000, s=1.3, at=0), dict(icon='envelope', x=780, y=880, s=1.4, at=1), dict(icon='paper', x=780, y=1080, s=1.0, at=2)],
      cards=[dict(t='HỘP CHOCOPIE', x=540, y=1160, at=0), dict(t='6 TỜ GIẤY', x=800, y=800, at=2, col='#c4281f', tc='#fff')],
      say='Trong túi quà có một hộp bánh Chocopie. Cạnh đó là chiếc phong bì. Bên trong là 6 tờ giấy, cắt cẩn thận cho vừa tờ đô la.'),
 dict(type='stage', label='HẮN ĐÃ TÍNH TRƯỚC', bg='room', mood='dieu_tra',
      cast=[dict(c='dtv', x=300, D=165, expr='normal'), dict(c='ts', x=780, D=160, expr='surprised', face=-1, at=1)],
      cards=[dict(t='TÍNH TỪ TRƯỚC', x=540, y=800, at=1, col='#c4281f', tc='#fff'), dict(t='BIẾT NGHỀ ÔNG', x=540, y=930, at=2, col='#f2dc8a')],
      say='Điều tra viên hiểu ngay một điều. Muốn cắt giấy cho bằng tờ đô, phải ngồi chuẩn bị từ trước. Hắn còn biết chồng bà làm ngành giao thông. Vậy hắn là người quen, hay là kẻ đã rình rất kỹ?'),
 dict(type='stage', label='VẾT LẠ', bg='room', mood='cang',
      cast=[dict(c='phapy', x=300, D=160, expr='normal', hands=[(.6, -.3, 'magnifier')])],
      icons=[dict(icon='safe', x=760, y=860, s=1.8, at=0), dict(icon='drop', x=830, y=760, s=.8, at=1), dict(icon='fingerprint', x=690, y=960, s=.9, at=2)],
      say='Pháp y lên tầng 2, đứng trước chiếc két sắt bị cạy dở. Trên cánh két có một vệt máu còn mới. /// {chậm: Và vệt máu ấy không phải của bà Thủ.} Phần 2, mình kể tiếp.'),
]
EP = [('p1', P1, 'PHẦN 1', 'PHONG BÌ 10.000 ĐÔ TOÀN GIẤY', 'Phần 2: Chiếc két sắt ở tầng 2'), ('p2', P2, 'PHẦN 2', 'CẠY KÉT BẰNG MỞ NÚT CHAI', 'Phần 3: Vết máu trên két')]
KH = re.compile(r'\s*(///|//|\[nghỉ\s*[\d.,]+\s*\])\s*|\{(?:nhanh|chậm|rất chậm|hạ|cao|nhấn):\s*|\}')
for name, S, badge, hook, nxt in EP:
    sp = dict(engine='vh', chars='roinuoc', format='vertical', style='cck2', series='VẾT MÁU TRÊN KÉT SẮT', badge=badge, hook_text=hook,
              cover_sub='Vĩnh Yên, 2007', next=nxt, cta='THEO DÕI CHUYỆN CHƯA KỂ', tts=True, dao_dien=True, speed=0.92,
              tag=f'cck-ketsat2-{name}', cast=CAST, shots=S)
    json.dump(sp, open(os.path.join(OUT, f'{name}.json'), 'w'), ensure_ascii=False)
    t = json.loads(json.dumps(sp)); t['tts'] = False; durs = []
    for s in t['shots']:
        n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['_sent'] = [.2 + 1.9 * i for i in range(n)]; durs.append(1.9 * n + 1.5)
    t['durs'] = durs
    json.dump(t, open(os.path.join(OUT, f'{name}_t.json'), 'w'), ensure_ascii=False)
    sach = [KH.sub(' ', s['say']) for s in S]
    print(name, len(S), 'canh', sum(len(x.split()) for x in sach), 'tu')
