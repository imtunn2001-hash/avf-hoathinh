"""CCK series VỤ ÁN VIỆT NAM: Án oan Nguyễn Thanh Chấn (3 phần, rối nước). python3 chan.py <thu_muc_ra> -> p1.json p2.json p3.json (+ _t bản soát).
Mẫu cho dạng vụ án Việt Nam đã khép lại: kể theo tư liệu báo chí (Tuổi Trẻ, Tiền Phong, Pháp Luật TP.HCM, Báo Pháp luật VN, VnExpress, Thanh Tra),
không tả cảnh gây án, không vẽ nạn nhân, tôn trọng người đã mất; trọng tâm là dấu vết + hành trình tìm ra sự thật.
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
NUM = {'15/8/2003': 'mười lăm tháng tám năm hai nghìn không trăm linh ba', '26/3/2004': 'hai mươi sáu tháng ba năm hai nghìn không trăm linh bốn',
       '5/7/2013': 'mồng năm tháng bảy năm hai nghìn không trăm mười ba', '25/10/2013': 'hai mươi lăm tháng mười năm hai nghìn không trăm mười ba',
       '4/11/2013': 'mồng bốn tháng mười một năm hai nghìn không trăm mười ba', '6/11/2013': 'mồng sáu tháng mười một năm hai nghìn không trăm mười ba',
       '25/1/2014': 'hai mươi lăm tháng một năm hai nghìn không trăm mười bốn', '23/7/2015': 'hai mươi ba tháng bảy năm hai nghìn không trăm mười lăm',
       '7,2 tỷ': 'bảy phẩy hai tỷ', '1961': 'một nghìn chín trăm sáu mươi mốt', '1988': 'một nghìn chín trăm tám mươi tám',
       '2003': 'hai nghìn không trăm linh ba', '2012': 'hai nghìn không trăm mười hai', '2014': 'hai nghìn không trăm mười bốn'}
def tts(x):
    for k in sorted(NUM, key=len, reverse=True): x = x.replace(k, NUM[k])
    return x
CAST = {
    'chan': dict(tag='ÔNG CHẤN', skin='#d9a070', hair='#1a1410', hair_style='side', outfit='#7a6040', outfit2='#5a462e', trim='#3a2a1a'),
    'chantu': dict(tag='ÔNG CHẤN', skin='#d9a070', hair='#1a1410', hair_style='side', outfit='#5a6a82', outfit2='#44526a', trim='#2a3448', mark='pale'),
    'chien': dict(tag='BÀ CHIẾN', skin='#dca476', hair='#1a1410', hair_style='bun', outfit='#7a3a2a', outfit2='#5a2a1e', trim='#d8a93a'),
    'hoat': dict(tag='ÔNG HOẠT', skin='#d9a070', hair='#8a8478', hair_style='side', outfit='#3a5a4a', outfit2='#2a4436', trim='#d8a93a'),
    'hien': dict(tag='ÔNG HIỀN', skin='#d6a272', hair='#e8e4da', hair_style='side', outfit='#6a6a5a', outfit2='#4e4e42', trim='#3a2a1a', beard=True),
    'lanh': dict(tag='BÀ LÀNH', skin='#dca476', hair='#1a1410', hair_style='bun', outfit='#4a6a8a', outfit2='#36506a', trim='#d8a93a'),
    'chuc': dict(tag='ÔNG CHÚC', skin='#d29a6a', hair='#8a8478', hair_style='side', outfit='#5a4a3a', outfit2='#44382a', trim='#7a1f1a', mark='brow'),
    'chung': dict(tag='LÝ NGUYỄN CHUNG', skin='#dca476', hair='#1a1410', hair_style='side', outfit='#4a4a5a', outfit2='#36364a', trim='#7a1f1a'),
    'dtv': dict(tag='ĐIỀU TRA VIÊN', skin='#e0aa7c', hair='#1a1410', hair_style='cap', hat='#3a5a3a', outfit='#4a6a44', outfit2='#36502f', trim='#d8a93a'),
    'toa': dict(tag='TOÀ ÁN', skin='#e0aa7c', hair='#5a5a5a', hair_style='side', outfit='#8a2a1e', outfit2='#6a1e14', trim='#d8a93a', mark='glasses'),
    'dan': dict(tag='NGƯỜI DÂN', skin='#d9a070', hair='#1a1410', hair_style='bun', outfit='#6a7a4a', outfit2='#4e5a36', trim='#3a2a1a'),
}
P1 = [
 dict(type='stage', label='', bg='village_night', cast=[dict(c='chan', x=330, D=175, expr='normal')], icons=[dict(icon='bike', x=760, y=1130, s=1.6, at=0)],
      say='Đi xin nước về bán hàng, việc ai ở quê cũng từng làm. Vậy sao một buổi tối đi xin nước… lại đổi lấy mười năm tù?'),
 dict(type='ke', label='CHUYỆN CHƯA KỂ', board='VỤ ÁN|BẮC GIANG', expr='normal',
      say='Hôm nay mình kể một vụ án có thật ở Bắc Giang, đã được toà án kết luận. Chuyện dài, mình chia ba phần. Anh em để ý từng dấu vết nhé, vì dấu vết quyết định số phận một con người.'),
 dict(type='stage', label='TỐI 15/8/2003', bg='shop',
      say='Tối 15/8/2003, thôn Me, xã Nghĩa Trung, huyện Việt Yên, tỉnh Bắc Giang. Chị Nguyễn Thị Hoan bán tạp hoá ngay tại nhà. Đêm ấy, chị bị sát hại trong chính căn nhà của mình.'),
 dict(type='items', label='HIỆN TRƯỜNG', items=[dict(icon='footprint', t='DẤU CHÂN', at=0), dict(icon='fingerprint', t='DẤU TAY TRÊN CỬA', at=1), dict(icon='bottle', t='VÂN TAY TRÊN CHAI', at=1), dict(icon='paper', t='HIỆN TRƯỜNG XÁO TRỘN', at=2, x=True)],
      say='Khám nghiệm hiện trường, cơ quan điều tra thu được nhiều dấu chân dưới sàn. Có dấu tay trên cửa, có vân tay trên một vỏ chai bia. Nhưng hồ sơ ghi lại: hiện trường lúc khám nghiệm đã bị xáo trộn.'),
 dict(type='stage', label='NGƯỜI CÙNG THÔN', bg='village_night', cast=[dict(c='chan', x=360, D=175, expr='normal')], icons=[dict(icon='bike', x=800, y=1130, s=1.5, at=0)],
      say='Người bị nghi là ông Nguyễn Thanh Chấn, sinh năm 1961, cùng thôn. Tối hôm ấy, vợ bảo ông đạp xe thồ hai thùng nhựa đi xin nước về bán hàng. Cơ quan điều tra cho rằng trên đường đi, ông đã vào nhà chị Hoan.'),
 dict(type='stage', label='GỌI LÊN LÀM VIỆC', bg='room', cast=[dict(c='dtv', x=320, D=170, expr='normal', hands=[(.6, -.3, 'pen')]), dict(c='chan', x=780, D=170, face=-1, expr='scared', at=1)],
      say='Ông bị gọi lên làm việc nhiều lần, suốt hơn một tháng. Rồi ông bị bắt, bị khởi tố về tội giết người.'),
 dict(type='items', label='HỒ SƠ BUỘC TỘI', items=[dict(icon='footprint', t='DẤU CHÂN: GẦN VỪA', at=1), dict(icon='paper', t='LỜI KHAI NHẬN TỘI', at=2), dict(icon='bottle', t='VÂN TAY: KHÔNG RÕ AI', at=3, x=True)],
      say='Hồ sơ buộc tội dựa vào hai thứ chính. Dấu chân ở hiện trường, ướm chân ông vào thì gần vừa. Và lời khai nhận tội ông đã ký trong lúc điều tra. Còn vân tay trên vỏ chai, không xác định được là của ai.'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='GẦN VỪA|ĐÃ ĐỦ CHƯA?', expr='normal', ask=True, gap=1.2,
      say='Anh em thử nghĩ. Một dấu chân gần vừa, trong khi rất nhiều người có cỡ chân giống nhau. Một lời khai nhận tội, rồi ra toà lại kêu oan. Như thế đã đủ để kết tội một người chưa?'),
 dict(type='stage', label='NGÀY 26/3/2004', bg='court', cast=[dict(c='toa', x=320, D=170, expr='normal', hands=[(.6, -.3, 'scroll')]), dict(c='chantu', x=780, D=165, face=-1, expr='sad')],
      cards=[dict(t='TÙ CHUNG THÂN', x=540, y=700, at=1, col='#c4281f', tc='#fff')],
      say='Ngày 26/3/2004, Toà án nhân dân tỉnh Bắc Giang tuyên ông Chấn phạm tội giết người. Mức án: tù chung thân. Ở phiên sơ thẩm rồi phúc thẩm, ông đều không nhận tội.'),
 dict(type='stage', label='TRẠI GIAM', bg='prison', cast=[dict(c='chantu', x=540, D=175, expr='sad')],
      say='Ông Chấn là con liệt sĩ, ở làng ai cũng bảo ông hiền lành, chịu khó. Từ đó, ông bắt đầu những năm tháng sau song sắt.'),
 dict(type='stage', label='MỘT CÂU HỎI', bg='prison', cast=[dict(c='hoat', x=320, D=170, expr='sad'), dict(c='chantu', x=760, D=160, face=-1, expr='sad', lean=-10)],
      cards=[dict(t='ANH CÓ TIN EM?', x=540, y=700, at=1)],
      say='Một lần người anh rể bên vợ vào thăm, ông Chấn quỳ xuống trước mặt anh. Ông hỏi đúng một câu: anh có tin em làm việc đó không? Rồi ông im lặng suốt buổi.'),
 dict(type='ke', label='PHẦN 2', board='10 NĂM|KÊU OAN', expr='surprised',
      say='Ở nhà, vợ ông bắt đầu một hành trình kéo dài mười năm. Và người tháo nút vụ án lại là… một ông cụ hàng xóm bảy mươi lăm tuổi. Phần hai nhé.'),
]
P2 = [
 dict(type='petition', label='', who='chien', y0=2004, y1=2013,
      say='Viết một lá đơn, ai cũng viết được. Vậy sao có người viết đơn suốt mười năm… mà sự thật vẫn chưa lộ ra?'),
 dict(type='ke', label='PHẦN TRƯỚC', board='ÔNG CHẤN|CHUNG THÂN', expr='normal',
      say='Phần trước, ông Nguyễn Thanh Chấn bị tuyên tù chung thân vì vụ án ở thôn Me, dù ông luôn kêu oan. Hôm nay là câu chuyện của những người ở nhà.'),
 dict(type='petition', label='BÀ CHIẾN', who='chien', y0=2004, y1=2012, title='ĐƠN KÊU OAN',
      say='Vợ ông, bà Nguyễn Thị Chiến, gửi đơn kêu oan từ địa phương lên trung ương. Anh rể của bà là ông Thân Ngọc Hoạt chở bà đi gửi đơn. Nhiều năm liền, gần như không có hồi âm.'),
 dict(type='items', label='CÁI GIÁ', items=[dict(icon='redbook', t='HAI SỔ ĐỎ', at=0), dict(icon='coin', t='VAY 60 TRIỆU', at=0)],
      say='Để có tiền đi kêu oan, gia đình đem hai sổ đỏ đi vay ngân hàng sáu mươi triệu đồng. Họ hàng hai bên mỗi người góp một ít, dựng cho mẹ ông Chấn một căn nhà nhỏ.'),
 dict(type='stage', label='GẦN 10 NĂM', bg='room', cast=[dict(c='chien', x=540, D=175, expr='sad')],
      say='Gần mười năm, bà Chiến suy sụp hoàn toàn. Gia đình phải đưa bà vào viện điều trị.'),
 dict(type='stage', label='CUỐI NĂM 2012', bg='village', cast=[dict(c='lanh', x=330, D=165, expr='scared'), dict(c='chuc', x=780, D=175, face=-1, expr='angry', at=0)],
      say='Cuối năm 2012, trong thôn, nhà ông Lý Văn Chúc lục đục. Bà Nguyễn Thị Lành, vợ hai của ông Chúc, đem chuyện kể với cha đẻ của mình. Chuyện về Lý Nguyễn Chung, con riêng của chồng bà.'),
 dict(type='stage', label='ANH CHẤN OAN QUÁ', bg='village', cast=[dict(c='hien', x=330, D=165, expr='sad'), dict(c='chien', x=780, D=165, face=-1, expr='surprised', at=1)],
      cards=[dict(t='"ANH CHẤN OAN QUÁ"', x=540, y=700, at=1, fs=40)],
      say='Cha bà Lành là ông Nguyễn Văn Hiền, bảy mươi lăm tuổi. Cuối tháng mười hai năm ấy, ông nói với bà Chiến một câu: anh Chấn oan quá. Mấy tháng sau, ông lại nói bóng gió đúng chuyện đó.'),
 dict(type='stage', label='MÁY GHI ÂM', bg='room', cast=[dict(c='hoat', x=330, D=170, expr='normal', hands=[(.6, -.3, 'phone')])], icons=[dict(icon='recorder', x=780, y=880, s=1.6, at=1)],
      say='Nói miệng thì khó ai tin. Ông Hoạt đi mua một chiếc máy ghi âm, ghi lại những câu chuyện liên quan đến Chung. Hai người hàng xóm cũng kể, họ từng nghe chính ông Chúc nhắc chuyện con mình gây án.'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='BIẾT MÀ|IM LẶNG', expr='sad', ask=True, gap=1.2,
      say='Theo báo chí, nhiều người trong nhà ông Chúc biết chuyện từ lâu. Vì thương, và sợ Chung bị án nặng, họ im lặng. Anh em nghĩ sao, thương như vậy là thương… hay là hại?'),
 dict(type='stage', label='NGÀY 5/7/2013', bg='room', cast=[dict(c='chien', x=330, D=170, expr='normal', hands=[(.6, -.3, 'scroll')])],
      cards=[dict(t='LÝ NGUYỄN CHUNG', x=760, y=780, at=1, col='#c4281f', tc='#fff', fs=40)],
      say='Ngày 5/7/2013, bà Chiến gửi đơn tới Cơ quan điều tra Viện kiểm sát nhân dân tối cao. Lần này, lá đơn ghi rõ một cái tên: Lý Nguyễn Chung.'),
 dict(type='stage', label='LỜI ĐE DOẠ', bg='village_night', cast=[dict(c='chuc', x=360, D=175, expr='angry'), dict(c='lanh', x=790, D=160, face=-1, expr='scared')],
      cards=[dict(t='BỊ BẮT KHẨN CẤP', x=540, y=700, at=1, col='#c4281f', tc='#fff')],
      say='Chuyện lộ ra, ông Chúc đe doạ giết bà Lành nếu bà còn kể với ai. Ông bị bắt khẩn cấp vì hành vi đó.'),
 dict(type='board', label='GHÉP LẠI', cards=['DẤU CHÂN GẦN VỪA', 'VÂN TAY KHÔNG RÕ', 'ANH CHẤN OAN QUÁ', 'BĂNG GHI ÂM', 'LÝ NGUYỄN CHUNG'], at=[0, 0, 0, 0, 1], links=[[0, 4], [1, 4], [2, 3], [3, 4]],
      say='Một dấu chân gần vừa, một vân tay không rõ của ai, một câu nói của ông cụ bảy mươi lăm tuổi, một chiếc máy ghi âm. Tất cả cùng chỉ về một cái tên.'),
 dict(type='ke', label='PHẦN 3', board='ĐẮK LẮK|ĐẦU THÚ?', expr='surprised',
      say='Nhưng Chung không còn ở thôn Me. Mười năm nay, cậu sống ở một nơi cách đó hơn một nghìn cây số. Phần ba: ngày người ấy tự bước vào cơ quan điều tra.'),
]
P3 = [
 dict(type='stage', label='', bg='village', cast=[dict(c='chung', x=540, D=180, expr='scared', tag=False)],
      say='Tự đi đến cơ quan điều tra, ai cũng làm được. Vậy sao có người phải mất mười năm… mới bước được vào cửa?'),
 dict(type='ke', label='HAI PHẦN TRƯỚC', board='10 NĂM|1 CÁI TÊN', expr='normal',
      say='Hai phần trước, ông Chấn tù chung thân, vợ ông mười năm kêu oan, và một cái tên bắt đầu lộ ra: Lý Nguyễn Chung. Giờ là phần cuối.'),
 dict(type='stage', label='LÝ NGUYỄN CHUNG', bg='village', cast=[dict(c='chung', x=360, D=175, expr='normal')], cards=[dict(t='SINH 1988', x=780, y=760, at=0), dict(t='VÀO ĐẮK LẮK', x=780, y=920, at=1)],
      say='Lý Nguyễn Chung sinh năm 1988, quê Lộc Bình, Lạng Sơn, từng sống ở thôn Me. Sau vụ án, Chung vào Đắk Lắk sinh sống, ở huyện Ea Kar.'),
 dict(type='stage', label='KHÔNG YÊN', bg='night', cast=[dict(c='chung', x=540, D=175, expr='scared')],
      say='Theo lời Chung khai, suốt mười năm bỏ trốn, cậu không lúc nào yên. Cứ chợp mắt, hình ảnh đêm ấy lại hiện về.'),
 dict(type='stage', label='VẬN ĐỘNG', bg='room', cast=[dict(c='dtv', x=320, D=170, expr='normal'), dict(c='chuc', x=780, D=165, face=-1, expr='sad', at=1)],
      say='Có chứng cứ trong tay, cơ quan điều tra kiên trì vận động gia đình, để đưa Chung ra đầu thú.'),
 dict(type='stage', label='NGÀY 25/10/2013', bg='room', cast=[dict(c='dtv', x=320, D=170, expr='normal', hands=[(.6, -.3, 'pen')]), dict(c='chung', x=780, D=170, face=-1, expr='sad', from_=None)],
      cards=[dict(t='ĐẦU THÚ', x=540, y=700, at=0, col='#c4281f', tc='#fff')],
      say='Ngày 25/10/2013, Lý Nguyễn Chung ra đầu thú. Chung khai nhận đã giết chị Hoan tối 15/8/2003 để cướp tài sản.'),
 dict(type='items', label='CHI TIẾT BỊ BỎ QUA', items=[dict(icon='ring', t='VẾT ĐEO NHẪN', at=1), dict(icon='paper', t='ĐỀ NGHỊ LÀM RÕ', at=1), dict(icon='ring', t='HAI NHẪN VÀNG', at=2)],
      say='Có một chi tiết năm xưa bị bỏ qua. Lúc khám nghiệm, người nhà chị Hoan thấy vết đeo nhẫn trên tay chị, và đề nghị làm rõ tài sản bị mất. Mười năm sau, Chung khai đã lấy đi hai chiếc nhẫn vàng.'),
 dict(type='stage', label='NGÀY 4/11/2013', bg='village', cast=[dict(c='chien', x=250, D=155, expr='happy'), dict(c='chan', x=540, D=175, expr='sad'), dict(c='dan', x=830, D=150, face=-1, expr='happy')],
      say='Ngày 4/11/2013, ông Chấn được đưa về nhà. Hàng trăm người dân đã chờ từ sáng. Ông nghẹn ngào giữa vòng tay người thân và hàng xóm.'),
 dict(type='stage', label='VÔ TỘI', bg='court', cast=[dict(c='toa', x=540, D=170, expr='normal', hands=[(.6, -.3, 'scroll')])],
      cards=[dict(t='HUỶ 2 BẢN ÁN', x=540, y=700, at=0, col='#2a7a4a', tc='#fff'), dict(t='VÔ TỘI: 25/1/2014', x=540, y=1260, at=1, col='#f2dc8a', fs=40)],
      say='Ngày 6/11/2013, Toà án nhân dân tối cao huỷ hai bản án đã kết tội ông Chấn. Ngày 25/1/2014, ông chính thức được công nhận vô tội.'),
 dict(type='items', label='SAU ĐÓ', items=[dict(icon='paper', t='XIN LỖI CÔNG KHAI', at=0), dict(icon='coin', t='BỒI THƯỜNG 7,2 TỶ', at=0), dict(icon='scale', t='CHUNG: 12 NĂM TÙ', at=1)],
      say='Các cơ quan tố tụng xin lỗi công khai, bồi thường cho gia đình ông Chấn 7,2 tỷ đồng. Còn Chung, ngày 23/7/2015, bị toà sơ thẩm tuyên tổng mức án mười hai năm tù, vì phạm tội khi chưa thành niên.'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='NẾU KHÔNG CÓ…', expr='normal', ask=True, gap=1.2,
      say='Anh em thử nghĩ. Nếu không có ông cụ bảy mươi lăm tuổi, không có chiếc máy ghi âm, không có người vợ mười năm gửi đơn… thì giờ này, ông Chấn đang ở đâu?'),
 dict(type='timeline', label='MƯỜI NĂM', points=[dict(y='2003', t='VỤ ÁN', at=0), dict(y='2004', t='CHUNG THÂN', at=0), dict(y='2013', t='ĐẦU THÚ', at=1), dict(y='2014', t='VÔ TỘI', at=2)],
      say='Từ năm 2003 đến năm 2014. Mười năm tù, mười năm kêu oan. Để trả lại cho một người nông dân hai chữ: vô tội.'),
 dict(type='stage', label='BÀI HỌC', bg='village_night', cast=[dict(c='chan', x=330, D=175, expr='sad')], icons=[dict(icon='bike', x=760, y=1130, s=1.6, at=0)], ask=True,
      say='Đi xin nước về bán hàng, việc ai ở quê cũng từng làm. Với ông Chấn, một buổi tối như thế đã đổi lấy mười năm tù. Theo anh em, bài học lớn nhất từ vụ án này là gì? Bình luận cho mình biết nhé.'),
]
for S in (P1, P2, P3):
    for s in S:
        for c in s.get('cast', []): c.pop('from_', None)
EP = [('p1', P1, 'PHẦN 1/3', 'MƯỜI NĂM TÙ VÌ ĐI XIN NƯỚC?', 'Phần 2: Mười năm kêu oan'),
      ('p2', P2, 'PHẦN 2/3', 'MƯỜI NĂM GỬI ĐƠN', 'Phần 3: Người tự ra đầu thú'),
      ('p3', P3, 'PHẦN 3/3', 'NGÀY HUNG THỦ ĐẦU THÚ', 'Theo dõi để xem vụ tiếp theo')]
for name, S, badge, hook, nxt in EP:
    for s in S: s['tts'] = tts(s['say'])
    sp = dict(engine='vh', chars='roinuoc', format='vertical', series='ÁN OAN NGUYỄN THANH CHẤN', badge=badge, hook_text=hook, next=nxt,
              cta='THEO DÕI CHUYỆN CHƯA KỂ', tts=True, speed=1.0, tag=f'cck-chan-{name}', cast=CAST, shots=S)
    json.dump(sp, open(os.path.join(OUT, f'{name}.json'), 'w'), ensure_ascii=False)
    t = json.loads(json.dumps(sp)); t['tts'] = False; durs = []
    for s in t['shots']:
        n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['_sent'] = [.2 + 1.9 * i for i in range(n)]; durs.append(1.9 * n + 1.5)
    t['durs'] = durs
    json.dump(t, open(os.path.join(OUT, f'{name}_t.json'), 'w'), ensure_ascii=False)
    print(name, len(S), 'canh', sum(len(s['say'].split()) for s in S), 'tu')
