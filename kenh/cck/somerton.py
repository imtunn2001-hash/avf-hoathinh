"""CCK series: Bí ẩn người đàn ông Somerton (3 phần, rối nước). python3 somerton.py <thu_muc_ra> -> p1.json p2.json p3.json (+ _t bản soát)."""
import json, re, sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
NAMES = ['Somerton', 'Adelaide', 'Glenelg', 'Keane', 'Tamám Shud', 'Rubaiyat', 'Omar Khayyam', 'Alf Boxall', 'Boxall', 'Woomera', 'Derek Abbott',
         'Abbott', 'Colleen Fitzpatrick', 'Carl Webb', 'Charles', 'Melbourne', 'Jo Thomson', 'Úc', 'Ba Tư']
NUM = {'1/12/1948': 'một tháng mười hai năm một nghìn chín trăm bốn mươi tám', '1948': 'một nghìn chín trăm bốn mươi tám', '1949': 'một nghìn chín trăm bốn mươi chín',
       '2021': 'hai nghìn không trăm hai mươi mốt', '2022': 'hai nghìn không trăm hai mươi hai', '1905': 'một nghìn chín trăm linh năm',
       '1941': 'một nghìn chín trăm bốn mươi mốt', '1946': 'một nghìn chín trăm bốn mươi sáu', '1947': 'một nghìn chín trăm bốn mươi bảy'}
SAY = {'Tamám Shud': 'Ta-mam Sút', 'Rubaiyat': 'Ru-bai-ơ-ét', 'Omar Khayyam': 'Ô-ma Khai-am', 'Alf Boxall': 'An-phơ Bốc-xồn', 'Boxall': 'Bốc-xồn',
       'Woomera': 'U-mê-ra', 'Derek Abbott': 'Đê-rếch Áp-bốt', 'Abbott': 'Áp-bốt', 'Colleen Fitzpatrick': 'Cô-lin Phít-pa-trích', 'Carl Webb': 'Các Ueb',
       'Charles': 'Sác-lơ', 'Melbourne': 'Men-bơn', 'Jo Thomson': 'Giô Tôm-sơn', 'Somerton': 'Xô-mơ-tơn', 'Adelaide': 'A-đơ-lết', 'Glenelg': 'Gờ-len-eo', 'Keane': 'Kin'}
def tts(x):
    for k in sorted(NUM, key=len, reverse=True): x = x.replace(k, NUM[k])
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<![\wÀ-ỹ\[])' + re.escape(n) + r'(?![\wÀ-ỹ\]])', '[[' + SAY.get(n, n) + ']]', x)
    return x
CAST = {
    'somerton': dict(tag='NGƯỜI VÔ DANH', skin='#ecc4a0', hair='#8a6a4a', hair_style='side', outfit='#6e6458', outfit2='#4e463c', trim='#c4281f'),
    'carlwebb': dict(tag='CARL WEBB', skin='#ecc4a0', hair='#8a6a4a', hair_style='side', outfit='#6e6458', outfit2='#4e463c', trim='#c4281f'),
    'jo': dict(tag='Y TÁ JO', skin='#f0c8a0', hair='#5a3a22', hair_style='nurse', outfit='#e8eef2', outfit2='#c8d2da', trim='#5a8aa8'),
    'abbott': dict(tag='GS DEREK ABBOTT', skin='#ecc4a0', hair='#d8d4ca', hair_style='side', outfit='#3a5a7a', outfit2='#2a4460', trim='#d8a93a', mark='glasses'),
    'fitz': dict(tag='COLLEEN FITZPATRICK', skin='#f0c8a0', hair='#c9a060', hair_style='bun', outfit='#7a3a5a', outfit2='#5a2a44', trim='#d8a93a'),
    'ronald': dict(tag='NGƯỜI NHẶT SÁCH', skin='#e8b890', hair='#3a2a1a', hair_style='fedora', hat='#3a3a44', outfit='#5a6a52', outfit2='#44503e', trim='#3a2a1a'),
    'boxall': dict(tag='ALF BOXALL', skin='#e8b890', hair='#3a2a1a', hair_style='cap', hat='#4a5a3a', outfit='#5e6a44', outfit2='#46502f', trim='#d8a93a'),
}
P1 = [
 dict(type='beach', label='', who='somerton', tag=False, say='Tìm tên một người chết, cảnh sát làm hằng ngày. Vậy sao người đàn ông này… phải chờ bảy mươi tư năm mới có tên?'),
 dict(type='ke', label='CHUYỆN CHƯA KỂ', board='BÍ ẨN|SOMERTON', expr='happy', say='Hôm nay mình kể vụ bí ẩn nổi tiếng nhất nước Úc. Chuyện dài, mình chia làm ba phần. Anh em nhớ để ý từng món đồ trong túi ông ấy nhé.'),
 dict(type='beach', label='SÁNG 1/12/1948', who='somerton', people=[dict(c='dan_tay', x0=-200, x1=330, at=1)], say='Sáng 1/12/1948, bãi biển Somerton, thành phố Adelaide. Người đi dạo thấy một người đàn ông ngồi tựa tường chắn sóng. Chân duỗi thẳng, hai bàn chân bắt chéo. Trông như đang ngủ.'),
 dict(type='beach', label='TỐI HÔM TRƯỚC', who='somerton', night=True, people=[dict(c='dan_tay', x0=1250, x1=820, at=0)], say='Tối hôm trước, vài người đã thấy đúng ông ấy, đúng tư thế ấy. Họ tưởng ông say rượu nên không ai lại gần. Sáng ra, ông đã chết.'),
 dict(type='items', label='TRONG TÚI ÁO', items=[dict(icon='ticket', t='VÉ TÀU CHƯA DÙNG', at=0), dict(icon='comb', t='LƯỢC LÀM Ở MỸ', at=0), dict(icon='cigarette', t='BAO THUỐC LÁ', at=0), dict(icon='paper', t='KHÔNG GIẤY TỜ', at=1, x=True)],
      say='Trong túi có một vé tàu chưa dùng, một cái lược làm ở Mỹ, một bao thuốc lá. Nhưng không ví, không giấy tờ, không một cái tên.'),
 dict(type='items', label='NHÃN MÁC BỊ CẮT', items=[dict(icon='shirt', t='MỌI NHÃN MÁC', at=1, x=True)], say='Lạ hơn nữa. Tất cả nhãn mác trên quần áo… đều đã bị cắt sạch. Như thể có ai đó không muốn ông được nhận ra.'),
 dict(type='stage', label='KHÁM NGHIỆM', bg='room', cast=[dict(c='bacsi', x=380, D=170, expr='normal', hands=[(.6, -.3, 'magnifier')])], cards=[dict(t='CHẤT ĐỘC?', x=760, y=800, at=1, col='#c4281f', tc='#fff'), dict(t='KHÔNG TÌM THẤY', x=760, y=960, at=2)],
      say='Bác sĩ khám nghiệm kết luận ông không chết tự nhiên. Ông nghi là chất độc. Nhưng xét nghiệm… không tìm ra bất cứ chất độc nào.'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='CHẾT VÌ GÌ?|AI LÀ AI?', expr='normal', ask=True, gap=1.2, say='Thử nghĩ xem. Một người khoẻ mạnh, quần áo chỉn chu, chết không rõ vì sao. Không ai đến nhận. Anh em sẽ tìm manh mối ở đâu đầu tiên?'),
 dict(type='station', label='GA ADELAIDE', who='canhsat', bag_at=1, cut=True, say='Tháng một năm 1949, nhà ga Adelaide báo có một chiếc vali nâu bị bỏ quên. Nó được gửi ngày ba mươi tháng mười một, đúng một ngày trước khi ông chết. Và nhãn của vali… cũng đã bị gỡ.'),
 dict(type='items', label='TRONG VALI', items=[dict(icon='thread', t='CHỈ MÀU CAM HIẾM', at=0), dict(icon='screwdriver', t='TUA VÍT THỢ ĐIỆN', at=0), dict(icon='letter', t='TÊN: KEANE', at=1), dict(icon='map', t='KHÔNG AI MẤT TÍCH', at=2, x=True)],
      say='Trong vali có cuộn chỉ màu cam hiếm thấy ở Úc, và một cái tua vít của thợ điện. Vài món ghi tên Keane. Nhưng tìm khắp các nước nói tiếng Anh, không có ông Keane nào mất tích.'),
 dict(type='scrap', label='TÚI ÁO BÍ MẬT', word='Tamám Shud', mean='NGHĨA LÀ: ĐÃ HẾT', mean_at=3, say='Rồi tháng sáu năm 1949, người ta lục lại quần ông. Trong một túi nhỏ giấu kín, có một mẩu giấy cuộn tròn. Trên đó in hai chữ tiếng Ba Tư: Tamám Shud. Nghĩa là: đã hết.'),
 dict(type='ke', label='PHẦN 2', board='MẨU GIẤY|XÉ TỪ ĐÂU?', expr='surprised', say='Mẩu giấy ấy bị xé từ trang cuối một cuốn sách thơ. Vậy cuốn sách đang ở đâu? Phần hai: cuốn sách xuất hiện, kèm một mật mã chưa ai giải được.'),
]
P2 = [
 dict(type='car', label='', who='ronald', open_at=0, say='Một người đàn ông thấy trong xe mình có một cuốn sách lạ. Trang cuối bị xé mất đúng một mẩu. Và mẩu giấy đó… đang nằm trong túi một người chết.'),
 dict(type='ke', label='PHẦN TRƯỚC', board='NGƯỜI VÔ DANH|SOMERTON', expr='normal', say='Phần trước, mình kể về người đàn ông chết trên bãi biển Somerton, không tên, nhãn mác bị cắt sạch. Hôm nay là cuốn sách.'),
 dict(type='stage', label='THÁNG 7/1949', bg='street', cast=[dict(c='ronald', x=360, D=170, expr='normal', hands=[(.6, -.3, 'book')]), dict(c='canhsat', x=780, D=170, face=-1, expr='surprised', at=1)],
      say='Tháng bảy năm 1949, anh ta mang sách đến cảnh sát. Anh kể: cuốn sách nằm trong chiếc xe mui trần đậu ở Glenelg, gần bãi biển, từ cuối năm trước.'),
 dict(type='items', label='KHỚP NHAU', items=[dict(icon='book', t='TẬP THƠ RUBAIYAT', at=0), dict(icon='paper', t='MẨU GIẤY: KHỚP', at=2)], say='Đó là tập thơ Rubaiyat của Omar Khayyam. Đem mẩu giấy ướm vào chỗ rách. Khớp.'),
 dict(type='code', label='MẬT MÃ', lines=['WRGOABABD', 'MLIAOI', 'WTBIMPANETP', 'MLIABOAIAQC', 'ITTMTSAMSTGAB'], stamp='CHƯA GIẢI ĐƯỢC',
      say='Soi kỹ bìa sau, thấy năm dòng chữ in hoa viết rất mờ. Dòng thứ hai bị gạch đi. Bảy mươi năm nay, giới giải mã vẫn chưa ai đọc được.'),
 dict(type='door', label='SỐ ĐIỆN THOẠI', who='jo', caller='canhsat', number='MỘT SỐ ĐIỆN THOẠI', open_at=1, say='Bìa sau còn có một số điện thoại. Số của một nữ y tá, sống cách chỗ tìm thấy xác chừng bốn trăm mét.'),
 dict(type='door', label='PHẢN ỨNG LẠ', who='jo', caller='canhsat', open_at=0, shake_at=1, say='Cô nói với cảnh sát: tôi không biết người này. Nhưng khi họ đưa tượng thạch cao khuôn mặt người chết… cô sững người, như sắp ngất. Và cô không chịu nhìn lại lần nào nữa.'),
 dict(type='ke', label='TẠI SAO?', board='KHÔNG QUEN?|SAO LẠI SỮNG?', expr='normal', ask=True, gap=1.2, say='Anh em thử nghĩ. Nếu thật không quen, sao lại sững người? Còn nếu quen… sao không nói?'),
 dict(type='stage', label='ALF BOXALL', bg='room', cast=[dict(c='boxall', x=380, D=170, expr='happy', hands=[(.6, -.3, 'book')])], cards=[dict(t='VẪN CÒN SỐNG', x=780, y=780, at=2, col='#2a7a4a', tc='#fff'), dict(t='SÁCH NGUYÊN VẸN', x=780, y=940, at=3)],
      say='Cô kể: hồi chiến tranh, cô từng tặng một cuốn Rubaiyat cho sĩ quan Alf Boxall. Cảnh sát nghĩ người chết chắc là anh này. Nhưng Boxall vẫn còn sống. Cuốn sách của anh vẫn nguyên trang cuối.'),
 dict(type='spy', label='TIN ĐỒN', title='GIẢ THUYẾT: ĐIỆP VIÊN?', say='Thế là tin đồn nổ ra. Năm 1949, chiến tranh lạnh vừa bắt đầu. Gần Adelaide có mỏ urani và bãi thử tên lửa Woomera. Người ta đồn: một điệp viên bị thủ tiêu.'),
 dict(type='board', label='GHÉP LẠI', cards=['NHÃN MÁC BỊ CẮT', 'MẨU TAMÁM SHUD', 'MẬT MÃ 5 DÒNG', 'Y TÁ SỮNG SỜ', 'ĐỘC KHÔNG DẤU VẾT'], at=[0, 0, 0, 0, 0], links=[[0, 2], [1, 2], [2, 3], [3, 4], [1, 3]],
      say='Ghép tất cả lại, nghe y như phim gián điệp. Nhưng suốt bảy mươi năm, chưa ai chứng minh được điều gì.'),
 dict(type='ke', label='PHẦN 3', board='VÀI SỢI TÓC|74 NĂM SAU', expr='surprised', say='Rồi người ta phát hiện vài sợi tóc kẹt trong chiếc mặt nạ thạch cao. Và bảy mươi tư năm sau, người vô danh… có tên. Phần ba nhé.'),
]
P3 = [
 dict(type='lab', label='', who='abbott', say='Bảy mươi tư năm không ai biết ông là ai. Lời giải lại nằm trong vài sợi tóc… kẹt ở một chiếc mặt nạ thạch cao.'),
 dict(type='ke', label='HAI PHẦN TRƯỚC', board='MẬT MÃ|Y TÁ JO', expr='normal', say='Hai phần trước: người chết không tên trên bãi biển Somerton, mẩu giấy Tamám Shud, mật mã chưa ai giải, và cô y tá sững người. Giờ là phần cuối.'),
 dict(type='stage', label='MẶT NẠ THẠCH CAO', bg='room', cast=[dict(c='canhsat', x=360, D=170, expr='normal')], cards=[dict(t='MẶT NẠ 1948', x=760, y=800, at=0), dict(t='CÒN DÍNH TÓC', x=760, y=960, at=1, col='#c4281f', tc='#fff')],
      say='Năm 1948, cảnh sát đúc một chiếc mặt nạ thạch cao từ khuôn mặt người chết, để đi hỏi người quen. Họ không ngờ, vài sợi tóc đã dính lại trong lớp thạch cao.'),
 dict(type='grave', label='NĂM 2021', stone='NGƯỜI VÔ DANH|1948', dig_at=0, say='Năm 2021, mộ của ông được khai quật để lấy mẫu. Nhưng chìa khoá thật sự… vẫn là mấy sợi tóc kia.'),
 dict(type='lab', label='GIẢI MÃ ADN', who='abbott', who2='fitz', say='Giáo sư Derek Abbott ở Đại học Adelaide, cùng nhà phả hệ người Mỹ Colleen Fitzpatrick, lấy ADN từ sợi tóc. Rồi họ đem so với các trang gia phả.'),
 dict(type='tree', label='CÂY GIA PHẢ', count='HƠN 4.000 NGƯỜI', name='CARL WEBB', name_at=2, say='Họ dựng một cây gia phả hơn bốn nghìn người. Lần ngược từng nhánh họ hàng xa. Cuối cùng chỉ còn một người không có giấy khai tử: Carl Webb.'),
 dict(type='stage', label='CARL WEBB', bg='room', cast=[dict(c='carlwebb', x=360, D=175, expr='normal')], cards=[dict(t='KỸ SƯ ĐIỆN', x=780, y=760, at=1), dict(t='SINH 1905', x=780, y=900, at=1), dict(t='TUA VÍT: KHỚP', x=780, y=1040, at=3, col='#2a7a4a', tc='#fff')],
      say='Carl Webb, thường gọi là Charles. Kỹ sư điện, thợ làm dụng cụ, sinh năm 1905 ở Melbourne. Nhớ cái tua vít thợ điện trong vali không? Khớp.'),
 dict(type='stage', label='MỘT CUỘC ĐỜI', bg='room', cast=[dict(c='carlwebb', x=360, D=175, expr='sad')], cards=[dict(t='CƯỚI 1941', x=780, y=760, at=0), dict(t='VỢ BỎ ĐI 1946', x=780, y=900, at=1), dict(t='BIẾN MẤT 1947', x=780, y=1040, at=2, col='#c4281f', tc='#fff')],
      say='Ông cưới vợ năm 1941. Năm 1946, vợ ông bỏ đi, kể rằng ông đối xử tệ. Năm 1947 ông rời nhà… rồi biến mất khỏi mọi giấy tờ.'),
 dict(type='ke', label='CHƯA HẾT', board='CÓ TÊN RỒI|NHƯNG…', expr='scared', ask=True, gap=1.2, say='Có tên rồi, nhưng câu hỏi vẫn còn nguyên. Ông chết vì sao? Mật mã viết gì? Và cô y tá kia… thật ra là ai với ông?'),
 dict(type='stage', label='CHƯA XÁC NHẬN', bg='room', cast=[dict(c='canhsat', x=200, D=150, expr='normal')], cards=[dict(t='GIẢ THUYẾT: TỰ ĐẦU ĐỘC', x=640, y=780, at=0, fs=36), dict(t='CẢNH SÁT CHƯA XÁC NHẬN', x=640, y=940, at=1, col='#c4281f', tc='#fff', fs=36)],
      say='Nhóm của giáo sư Abbott cho rằng ông tự đầu độc. Nhưng đến giờ, cảnh sát Nam Úc vẫn chưa xác nhận kết quả. Họ chỉ nói: lạc quan một cách thận trọng.'),
 dict(type='timeline', label='74 NĂM', points=[dict(y='1948', t='BÃI BIỂN', at=0), dict(y='1949', t='MẨU GIẤY', at=1), dict(y='2021', t='KHAI QUẬT', at=1), dict(y='2022', t='CÓ TÊN', at=2)],
      say='Một mẩu giấy, một cuốn sách, một mật mã, mấy sợi tóc. Từ năm 1948 đến năm 2022. Bảy mươi tư năm để trả lại một cái tên.'),
 dict(type='beach', label='TAMÁM SHUD', who='somerton', tag=False, ask=True, gap=1.0, say='Tìm tên một người chết, cảnh sát làm hằng ngày. Với ông Carl Webb, việc đó mất bảy mươi tư năm. Theo anh em, mật mã năm dòng kia viết gì? Bình luận cho mình biết nhé.'),
]
EP = [('p1', P1, 'PHẦN 1/3', 'NGƯỜI VÔ DANH 74 NĂM', 'Phần 2: Cuốn sách và mật mã'),
      ('p2', P2, 'PHẦN 2/3', 'CUỐN SÁCH TRONG XE', 'Phần 3: Vài sợi tóc'),
      ('p3', P3, 'PHẦN 3/3', 'LỜI GIẢI TRONG SỢI TÓC', 'Theo dõi để xem vụ tiếp theo')]
for name, S, badge, hook, nxt in EP:
    for s in S: s['tts'] = tts(s['say'])
    sp = dict(engine='vh', chars='roinuoc', format='vertical', series='BÍ ẨN NGƯỜI ĐÀN ÔNG SOMERTON', badge=badge, hook_text=hook, next=nxt,
              cta='THEO DÕI CHUYỆN CHƯA KỂ', tts=True, speed=1.0, tag=f'cck-som-{name}', cast=CAST, shots=S)
    json.dump(sp, open(os.path.join(OUT, f'{name}.json'), 'w'), ensure_ascii=False)
    t = json.loads(json.dumps(sp)); t['tts'] = False; durs = []
    for s in t['shots']:
        n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['_sent'] = [.2 + 1.9 * i for i in range(n)]; durs.append(1.9 * n + 1.5)
    t['durs'] = durs
    json.dump(t, open(os.path.join(OUT, f'{name}_t.json'), 'w'), ensure_ascii=False)
    print(name, len(S), 'canh', sum(len(s['say'].split()) for s in S), 'tu')
