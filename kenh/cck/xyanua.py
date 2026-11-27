"""CCK series VỤ ÁN VIỆT NAM: Nha sĩ giả và gói hóa chất màu vàng – vụ Lê Thanh Vân (1998–2001) (3 phần, rối nước).
python3 xyanua.py <thu_muc_ra> -> p1.json p2.json p3.json (+ _t bản soát, _sach.txt bản bỏ ký hiệu gửi W53).
Tư liệu: VnExpress 30/3/2004 "Chưa thể kết luận điều tra vụ nữ sát thủ Lê Thanh Vân", 25/8/2004 "Nữ 'sát thủ' giết 13 người bằng chất độc xyanua",
1/9/2004 "Tử hình 'sát thủ' Lê Thanh Vân", 10/9/2004 (kháng cáo), 7/5/2003 (theo Tuổi Trẻ, khai 6 người), 17/7/2003 (theo Tiền Phong, khai thêm 7),
1–3/2/2005 (phúc thẩm, y án); Tuổi Trẻ 5/9/2004 "Vụ án chấn động nhân tâm"; VietNamNet 17/5/2014 (thi hành án 26/10/2005, Thủ Dầu Một).
TAND tỉnh Bình Dương xử 25/8–1/9/2004: tử hình; Tòa phúc thẩm TANDTC tại TP.HCM 1/2/2005: y án; đã thi hành 26/10/2005.
Không vẽ nạn nhân, không tả cách đầu độc; trọng tâm: những cái chết rời rạc ghi là bệnh, gói hóa chất màu vàng, lời khai "nước nấu", ghép hồ sơ bốn tỉnh.
Số tài sản các báo lệch nhau (242/250/286 triệu) -> nói theo Tuổi Trẻ. Số viết bằng chữ số trong 'say'. Ký hiệu nhịp chỉ đặt SAU dấu câu (W87 v3.1).
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CAST = {
    'van': dict(tag='LÊ THANH VÂN', skin='#e6b48a', hair='#1a1410', hair_style='bun', outfit='#f2f2ee', outfit2='#cfcfc8', trim='#6a3a5a', mark='mole'),
    'bong': dict(tag='?', skin='#e6b48a', hair='#1a1410', hair_style='bun', outfit='#f2f2ee', outfit2='#cfcfc8', trim='#6a3a5a', mark='mole'),
    'quang': dict(tag='DÌU DÃNH QUANG', skin='#d6a272', hair='#1a1410', hair_style='side', outfit='#5a5a62', outfit2='#3e3e46', trim='#7a1f1a', mark='brow'),
    'kham': dict(tag='ANH ĐINH VĂN KHẢM', skin='#e0aa7c', hair='#1a1410', hair_style='side', outfit='#2e6ab0', outfit2='#22508a', trim='#e8e2d2'),
    'dtv': dict(tag='ĐIỀU TRA VIÊN', skin='#e0aa7c', hair='#1a1410', hair_style='cap', hat='#3a5a3a', outfit='#4a6a44', outfit2='#36502f', trim='#d8a93a', mark='glasses'),
    'giamdinh': dict(tag='GIÁM ĐỊNH VIÊN', skin='#e0aa7c', hair='#3a3430', hair_style='side', outfit='#e8e8e2', outfit2='#c8c8c0', trim='#2e6ab0', mark='glasses'),
    'bacsi': dict(tag='BÁC SĨ', skin='#ecc09a', hair='#8a8a8a', hair_style='side', outfit='#f2f2ee', outfit2='#cfcfc8', trim='#5a8aa8'),
    'me': dict(tag='MẸ CỦA VÂN', skin='#d29a6a', hair='#b8b2a6', hair_style='bun', outfit='#5a4a6a', outfit2='#42364e', trim='#3a2a1a'),
    'toa': dict(tag='TÒA ÁN', skin='#e0aa7c', hair='#5a5a5a', hair_style='side', outfit='#8a2a1e', outfit2='#6a1e14', trim='#d8a93a', mark='glasses'),
}
P1 = [
 dict(type='stage', label='', bg='hospital', icons=[dict(icon='cross', x=540, y=1000, s=1.9, at=0)], cards=[dict(t='13 NGƯỜI CHẾT', x=540, y=1240, at=1, col='#c4281f', tc='#fff')],
      say='Kẻ đầu độc đưa nạn nhân đi viện. /// Gần 4 năm, 13 người đã chết. // {chậm: Giấy tờ của họ ghi đủ thứ bệnh, trừ chữ đầu độc.}'),
 dict(type='ke', label='CHUYỆN CHƯA KỂ', board='NHA SĨ|GIẢ', expr='normal',
      say='Đây là một vụ án có thật, trải qua bốn tỉnh, thành phía Nam. Tòa đã xử phúc thẩm, bản án đã thi hành. Chuyện dài, mình chia làm ba phần. Anh em để ý kỹ một gói hóa chất màu vàng nhé.'),
 dict(type='stage', label='NHA SĨ "HỌC Ở ĐỨC"', bg='dentist', cast=[dict(c='van', x=540, D=175, expr='happy', **{'from': -220})], icons=[dict(icon='tooth', x=820, y=760, s=1.0, at=1)],
      say='Người phụ nữ ấy tên là Lê Thanh Vân, sinh năm 1956, nhà ở quận 10, Sài Gòn. Bà ta tự giới thiệu là nha sĩ từng học ở Đức. Bà ta còn nói mình biết 7 ngoại ngữ. Ai nghe cũng thấy nể.'),
 dict(type='items', label='HAI TIỀN ÁN', items=[dict(icon='paper', t='1990: 18 THÁNG TÙ', at=1), dict(icon='paper', t='1993: 4 NĂM TÙ', at=2), dict(icon='tooth', t='LẠI MẶC ÁO TRẮNG', at=3)],
      say='Thật ra, Vân đã hai lần ra tòa vì lừa đảo. Năm 1990, Tòa án quận 5 phạt bà ta 18 tháng tù. Năm 1993, Tòa án quận 10 phạt thêm 4 năm tù. Ra tù, Vân lại khoác áo trắng. {hạ: Lần này, bà ta không chỉ lừa tiền.}'),
 dict(type='stage', label='PHÒNG NHA LONG KHÁNH', bg='dentist', cast=[dict(c='kham', x=330, D=170, expr='happy'), dict(c='van', x=780, D=165, face=-1, expr='happy', at=1, **{'from': 1300})],
      say='Ở Long Khánh, Đồng Nai, anh Đinh Văn Khảm làm một phòng nha. Anh mời Vân về làm cùng. Đi theo Vân là Dìu Dãnh Quang, người mà báo chí gọi là chồng hờ. Quang sinh năm 1973, kém Vân 17 tuổi.'),
 dict(type='stage', label='TỐI 3/1/1998', bg='hospital', cast=[dict(c='van', x=330, D=170, expr='sad'), dict(c='quang', x=780, D=165, face=-1, expr='normal', at=1)], icons=[dict(icon='cross', x=560, y=720, s=.8, at=0)],
      say='Tối 3/1/1998, mẹ anh Khảm là bà Võ Thị Lý đột ngột trở bệnh. Vân và Quang đưa bà đi cấp cứu. Bà mất tại Bệnh viện Long Khánh. {hạ: Không ai nghĩ người đưa bà đi viện lại là kẻ đầu độc.}'),
 dict(type='items', label='MỘT CÁCH LÀM', items=[dict(icon='tooth', t='NHA SĨ GIẢ', at=1), dict(icon='cup', t='MỜI ĂN UỐNG', at=2), dict(icon='motorbike', t='TIỀN, XE, ĐẤT', at=3)],
      say='Theo báo chí, Vân có một cách làm lặp đi lặp lại. Bà ta làm quen, có khi nhận làm con nuôi, ăn ở chung nhà. Rồi bà ta mời đi ăn uống, đi khám bệnh. Sau đó, tiền, xe máy, đất đai của nạn nhân về tay Vân.'),
 dict(type='stage', label='THÁNG 6/1998', bg='hospital', cast=[dict(c='bacsi', x=330, D=170, expr='normal', hands=[(.6, -.3, 'pen')], **{'from': -220})], icons=[dict(icon='paper', x=780, y=840, s=1.4, at=1)],
      cards=[dict(t='XUẤT HUYẾT NÃO?', x=740, y=1060, at=2, col='#f2dc8a')],
      say='Tháng 6/1998, đến lượt mẹ chồng của Vân. Bà cụ mất ở Bệnh viện Trưng Vương. Bệnh viện chẩn đoán nghi xuất huyết não. Theo VnExpress, Vân lấy của bà 2,8 triệu đồng.'),
 dict(type='stage', label='NĂM 1999', bg='room', icons=[dict(icon='banknote', x=540, y=860, s=1.6, at=0)], cards=[dict(t='NỢ 12,5 TRIỆU', x=540, y=1080, at=1, col='#c4281f', tc='#fff')],
      say='Năm 1999, người em rể của Vân là anh Lê Văn Cẩm cũng chết. Theo Tiền Phong, Vân đang nợ anh 12,5 triệu đồng. {chậm: Món nợ ấy từ đó không còn ai đòi.}'),
 dict(type='stage', label='VÌ SAO KHÔNG AI NGHI?', bg='lab', cast=[dict(c='giamdinh', x=330, D=170, expr='normal', hands=[(.6, -.3, 'magnifier')], **{'from': -220})], icons=[dict(icon='testtube', x=780, y=860, s=1.5, at=1)],
      say='Vì sao suốt nhiều năm, những cái chết ấy trôi qua lặng lẽ? Thứ Vân dùng là xyanua. Đại tá Phạm Ngọc Hiền, Phân viện Khoa học hình sự miền Nam, đã nói rõ. Rất khó phát hiện chất này trên tử thi.'),
 dict(type='items', label='MỖI NƠI MỘT HỒ SƠ', items=[dict(icon='paper', t='CHƯA RÕ NGUYÊN NHÂN', at=1), dict(icon='paper', t='CHẾT NÃO', at=2), dict(icon='map', t='MỖI TỈNH MỘT NƠI', at=3)],
      say='Các bác sĩ đưa ra những kết luận rất khác nhau. Có ca ghi chưa rõ nguyên nhân, có ca ghi chết não. Mỗi cái chết lại nằm ở một bệnh viện, một tỉnh khác nhau. Đứng riêng, cái chết nào trông cũng như một ca bệnh. {chậm: Chỉ khi đặt cạnh nhau, chúng mới lộ ra một cái tên.}'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='MỔ TỬ THI|HAY KHÔNG?', expr='normal', ask=True, gap=1.2,
      say='Anh em thử đặt mình vào chỗ gia đình nạn nhân. Người thân vừa mất, giấy tờ ghi một căn bệnh. Đề nghị mổ tử thi thì cả nhà phải chịu thêm một lần đau. Không đề nghị thì một kẻ giết người có thể lọt lưới. {cao: Anh em sẽ chọn thế nào?} [nghỉ 1.2]'),
 dict(type='stage', label='1998 – 2001', bg='street', cast=[dict(c='bong', x=330, D=170, expr='normal', tag=False)], icons=[dict(icon='map', x=770, y=860, s=1.2, at=1)],
      say='Từ năm 1998 đến tháng 8/2001, những cái chết cứ nối nhau. Đồng Nai, Bình Dương, Bình Phước, rồi Thành phố Hồ Chí Minh. Có người là người thân, có người là người quen. Điểm chung là họ đều từng ăn uống cùng một người.'),
 dict(type='stage', label='CHIẾC GIỎ XÁCH', bg='room', cast=[dict(c='dtv', x=330, D=175, expr='normal', **{'from': -220})], icons=[dict(icon='handbag', x=780, y=880, s=1.5, at=1)],
      say='Rồi có lần, công an mời Vân lên làm việc. Họ khám chiếc giỏ xách bà ta mang theo. {hạ: Trong đó có một gói hóa chất màu vàng.}'),
 dict(type='stage', label='GIÁM ĐỊNH', bg='lab', cast=[dict(c='giamdinh', x=330, D=170, expr='surprised')], icons=[dict(icon='packet_y', x=780, y=840, s=1.5, at=0)],
      cards=[dict(t='KỊCH ĐỘC', x=780, y=1060, at=1, col='#c4281f', tc='#fff')],
      say='Gói hóa chất được gửi đi giám định. {chậm: Kết quả: đó là chất kịch độc.} // Một nha sĩ mang chất kịch độc trong giỏ xách. Bằng chứng tưởng đã nằm gọn trong tay công an.'),
 dict(type='ke', label='PHẦN 2', board='VÌ SAO|ĐƯỢC THẢ?', expr='surprised',
      say='Nhưng chỉ ít lâu sau, Vân lại bước ra khỏi đồn công an. /// {hạ: Có chất độc trong tay, mà vẫn chưa thể buộc tội.} // Vì sao vậy? Phần 2 nhé.'),
]
P2 = [
 dict(type='stage', label='', bg='lab', icons=[dict(icon='handbag', x=420, y=1010, s=1.5, at=0), dict(icon='packet_y', x=690, y=1000, s=1.2, at=0)],
      cards=[dict(t='KỊCH ĐỘC', x=540, y=1240, at=1, col='#c4281f', tc='#fff')],
      say='Gói hóa chất vàng trong giỏ xách. /// Giám định nói đó là chất kịch độc. {chậm: Vậy mà người mang nó vẫn được thả ra.}'),
 dict(type='ke', label='PHẦN TRƯỚC', board='GÓI BỘT|MÀU VÀNG', expr='normal',
      say='{nhanh: Phần trước, nhiều người chết sau khi ăn uống cùng một nha sĩ giả tên Lê Thanh Vân.} // Công an đã tìm thấy chất kịch độc trong giỏ xách của bà ta. Giờ là câu hỏi: vì sao vẫn chưa buộc tội được?'),
 dict(type='stage', label='CÓ ĐỘC ≠ ĐÃ GIẾT', bg='lab', cast=[dict(c='dtv', x=330, D=170, expr='normal', **{'from': -220})], icons=[dict(icon='packet_y', x=780, y=860, s=1.2, at=1)],
      say='Có chất độc trong tay, chưa có nghĩa là đã giết người. Muốn buộc tội, phải nối được gói hóa chất với từng cái chết. Tức là phải tìm ra chất độc trong cơ thể nạn nhân.'),
 dict(type='items', label='DẤU VẾT MỜ', items=[dict(icon='testtube', t='KHÔNG THẤY CHẤT ĐỘC', at=1), dict(icon='clock', t='ĐÃ QUA NHIỀU NGÀY', at=2), dict(icon='paper', t='GIẤY GHI LÀ BỆNH', at=3)],
      say='Theo VnExpress, công an không tìm thấy chất độc trong tử thi nạn nhân. Như lời Đại tá Phạm Ngọc Hiền, xyanua rất khó phát hiện trên tử thi. Giấy tờ ở bệnh viện lại ghi những căn bệnh khác nhau. {hạ: Thứ giết người nhanh nhất lại là thứ khó chứng minh nhất.}'),
 dict(type='stage', label='ĐƯỢC TẠI NGOẠI', bg='street', cast=[dict(c='van', x=540, D=170, expr='happy', **{'from': -220})], icons=[dict(icon='handbag', x=800, y=1010, s=.9, at=1)],
      say='Thời hạn điều tra hết. Công an tỉnh Bình Dương chưa làm rõ được Vân có liên quan tới hai cái chết. Vân được cho tại ngoại. {chậm: Bà ta bước ra, mang theo bí mật của mình.}'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='GIỮ LẠI|HAY THẢ?', expr='normal', ask=True, gap=1.2,
      say='Anh em thử ngồi vào ghế điều tra viên. Trong tay có chất kịch độc, nhưng không nối được với cái chết nào. Giữ người khi chưa đủ chứng cứ là làm trái luật. Thả ra thì có thể sẽ có thêm người chết. {cao: Anh em sẽ chọn bên nào?} [nghỉ 1.2]'),
 dict(type='stage', label='ĐẾN THÁNG 8/2001', bg='street', cast=[dict(c='bong', x=330, D=170, expr='normal', tag=False)], icons=[dict(icon='cup', x=770, y=880, s=1.2, at=1)],
      say='Sự thật là những cái chết vẫn chưa dừng lại. Theo cáo trạng, chuỗi đầu độc kéo dài tới tháng 8/2001. Có những người được cứu sống kịp. Có những người không may mắn như vậy.'),
 dict(type='stage', label='CHIẾC XE MÁY', bg='street', cast=[dict(c='quang', x=330, D=170, expr='angry')], icons=[dict(icon='motorbike', x=780, y=880, s=1.4, at=1)],
      say='Một trong những nạn nhân là anh Trần Văn Khôi. Anh bị đầu độc để Vân chiếm chiếc xe máy. Lần này, Dìu Dãnh Quang cũng nhúng tay. {hạ: Một mạng người, đổi lấy một chiếc xe máy.}'),
 dict(type='board', label='BỐN TỈNH, BỐN HỒ SƠ', cards=['ĐỒNG NAI', 'BÌNH DƯƠNG', 'BÌNH PHƯỚC', 'TP.HCM', 'MỘT CÁI TÊN?'], at=[0, 1, 2, 3, 4], links=[[0, 4], [1, 4], [2, 4], [3, 4]],
      say='Mỗi tỉnh giữ một vài hồ sơ. Ở từng nơi, mỗi cái chết trông giống một ca bệnh lẻ. Nhưng một ca bệnh lẻ thì không có chung người đi cùng. Đặt các hồ sơ cạnh nhau, cái tên Lê Thanh Vân cứ lặp đi lặp lại.'),
 dict(type='stage', label='BỘ CÔNG AN VÀO CUỘC', bg='room', cast=[dict(c='dtv', x=330, D=175, expr='angry', **{'from': -220})], icons=[dict(icon='paper', x=760, y=820, s=1.3, at=1)],
      cards=[dict(t='GHÉP HỒ SƠ', x=760, y=1040, at=2, col='#f2dc8a')],
      say='Công an các tỉnh chuyển hồ sơ lên Cơ quan Cảnh sát điều tra Bộ Công an. Từ đây, những cái chết rời rạc được xem xét cùng nhau. {chậm: Một bệnh nhân lẻ thì có thể là bệnh, mười bệnh nhân lẻ thì là một vụ án.}'),
 dict(type='stage', label='"TỪNG BỊ BÁC BỎ"', bg='room', cast=[dict(c='dtv', x=330, D=170, expr='normal')], icons=[dict(icon='paper', x=780, y=840, s=1.2, at=1)],
      say='Đại tá Nguyễn Thế Bình là Phó thủ trưởng Cơ quan điều tra Bộ Công an. Ông cho biết công an nhiều tỉnh từng bác bỏ nghi vấn, vì không tìm thấy chứng cứ. Lần này, họ đi từ một hướng khác: chính gói hóa chất.'),
 dict(type='stage', label='"NƯỚC NẤU"', bg='room', cast=[dict(c='van', x=780, D=170, face=-1, expr='normal'), dict(c='dtv', x=330, D=165, expr='normal', at=1)], icons=[dict(icon='tooth', x=560, y=760, s=.8, at=0)],
      say='Vân không chịu nhận. Bà ta khai thứ trong gói chỉ là "nước nấu". Theo Tuổi Trẻ, đó là một loại hóa chất dùng để làm răng giả. Lời khai ấy nghe rất hợp với một nha sĩ.'),
 dict(type='stage', label='LỜI KHAI ĐẦU TIÊN SỤP', bg='lab', cast=[dict(c='giamdinh', x=330, D=170, expr='surprised', hands=[(.6, -.3, 'magnifier')])], icons=[dict(icon='testtube', x=780, y=860, s=1.3, at=1)],
      cards=[dict(t='KHÔNG ĐỘC', x=780, y=1060, at=2, col='#2e6ab0', tc='#fff')],
      say='Nhưng ngành y tế kiểm tra và xác định chất "nước nấu" không hề độc. Vậy thứ kịch độc trong giỏ xách là gì? {chậm: Lời nói dối đầu tiên đã sụp.}'),
 dict(type='items', label='XÁC ĐỊNH ĐỘC CHẤT', items=[dict(icon='testtube', t='THỰC NGHIỆM', at=1), dict(icon='paper', t='CÁO TRẠNG', at=2), dict(icon='packet_y', t='XYANUA', at=3)],
      say='Cơ quan điều tra làm thực nghiệm để xác định đúng loại độc chất. Theo Tuổi Trẻ, kết quả ấy đã củng cố chặt chẽ bản cáo trạng. Thứ trong gói màu vàng là xyanua.'),
 dict(type='stage', label='BẮT GIỮ', bg='room', cast=[dict(c='dtv', x=330, D=175, expr='angry'), dict(c='van', x=780, D=165, face=-1, expr='scared', at=1)],
      say='Khi đã xác định đúng loại độc chất, công an bắt giữ Lê Thanh Vân. Người chồng hờ Dìu Dãnh Quang cũng phải ra trước pháp luật.'),
 dict(type='stage', label='Ở QUẬN 10', bg='village', cast=[dict(c='me', x=540, D=170, expr='sad', **{'from': 1300})],
      say='Ở quận 10, có một người mẹ không hiểu nổi chuyện gì đang xảy ra. Bà nói với Tuổi Trẻ rằng bà không hiểu vì sao con gái mình thành kẻ giết người. Vân còn hai con trai đang học phổ thông.'),
 dict(type='ke', label='LẦN KHAI ĐẦU: 6 NGƯỜI', board='CHƯA|HẾT?', expr='surprised',
      say='Trong phòng hỏi cung, Vân bắt đầu khai. /// {hạ: Lần khai đầu, bà ta nhận đã giết 6 người.} // Nhưng đó vẫn chưa phải con số cuối cùng. Phần 3 nhé.'),
]
P3 = [
 dict(type='stage', label='', bg='room', icons=[dict(icon='paper', x=540, y=1000, s=1.8, at=0)],
      cards=[dict(t='6 + 7', x=540, y=1240, at=1, col='#c4281f', tc='#fff')],
      say='Lần khai sau, thêm 7 cái tên. /// Tổng cộng 21 người bị đầu độc. {chậm: Chỉ 8 người sống sót.}'),
 dict(type='ke', label='HAI PHẦN TRƯỚC', board='GÓI BỘT|→ VÂN', expr='normal',
      say='{nhanh: Hai phần trước, một gói hóa chất màu vàng dẫn công an tới Lê Thanh Vân.} // Giờ là phần cuối: những lời khai, và hai phiên tòa.'),
 dict(type='stage', label='THÁNG 5/2003', bg='room', cast=[dict(c='van', x=540, D=175, expr='sad')], icons=[dict(icon='paper', x=820, y=780, s=1.0, at=1)],
      say='Tháng 5/2003, báo chí đưa tin Vân thú nhận đã giết 6 người bằng xyanua. Tháng 7/2003, Vân khai thêm 7 người nữa. Những cái chết từng được ghi là bệnh, giờ có một lời giải khác.'),
 dict(type='items', label='VÌ SAO?', items=[dict(icon='cross', t='56 TRIỆU MỔ TIM', at=1), dict(icon='book', t='HỌC PHÍ HAI CON', at=2), dict(icon='banknote', t='NỢ NẦN', at=3)],
      say='Vì sao? Theo Tiền Phong, Vân khai cần 56 triệu đồng để mổ tim. Bà ta còn khai túng thiếu, không có tiền đóng học cho hai con. {chậm: Không lý do nào trả lại được mạng sống cho 13 người.}'),
 dict(type='stage', label='THỨ VÂN LẤY ĐƯỢC', bg='market', icons=[dict(icon='motorbike', x=330, y=860, s=1.3, at=0), dict(icon='banknote', x=780, y=860, s=1.3, at=1)],
      cards=[dict(t='HƠN 286 TRIỆU', x=540, y=1100, at=2, col='#f2dc8a')],
      say='Thứ Vân lấy được là tiền mặt, xe máy, đất đai, cả một sạp tạp hóa. Theo Tuổi Trẻ, tổng cộng hơn 286 triệu đồng. Có người bị đổi mạng lấy 2,8 triệu đồng, có người vì một chiếc xe máy.'),
 dict(type='stage', label='NGÀY 25/8/2004', bg='court', cast=[dict(c='toa', x=330, D=170, expr='normal', hands=[(.6, -.3, 'scroll')])], icons=[dict(icon='scale', x=780, y=820, s=1.2, at=1)],
      say='Ngày 25/8/2004, Tòa án nhân dân tỉnh Bình Dương mở phiên xét xử. Đại diện gia đình các nạn nhân có mặt ở phiên tòa. Phiên tòa kéo dài suốt 8 ngày.'),
 dict(type='stage', label='KÊU OAN', bg='court', cast=[dict(c='van', x=540, D=175, expr='scared')],
      say='Giữa phiên tòa, Vân ngất xỉu. Tỉnh lại, bà ta kêu oan. Vân nói mình không đầu độc ai, chỉ có lỗi là giữ tài sản của nạn nhân. Bà ta còn nói mình bị ép cung.'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='ĐỦ ĐỂ|KẾT TỘI?', expr='normal', ask=True, gap=1.2,
      say='Chỗ này mới khó. Xyanua gần như không để lại dấu vết trên tử thi. Thứ còn lại là lời khai, thực nghiệm, và những tài sản bị chiếm. Mà lời khai thì người khai có thể rút lại. {cao: Theo anh em, chừng ấy đã đủ để kết tội chưa?} [nghỉ 1.2]'),
 dict(type='stage', label='NGÀY 1/9/2004', bg='court', cast=[dict(c='toa', x=330, D=170, expr='normal', hands=[(.6, -.3, 'scroll')])],
      cards=[dict(t='TỬ HÌNH', x=760, y=820, at=2, col='#c4281f', tc='#fff')],
      say='Tòa không chỉ dựa vào lời khai. Kết quả thực nghiệm và những tài sản bị chiếm cũng được đặt lên bàn. Ngày 1/9/2004, Lê Thanh Vân bị tuyên tử hình. Tòa nêu rõ Vân có hai tiền án và không hối cải.'),
 dict(type='stage', label='DÌU DÃNH QUANG', bg='court', cast=[dict(c='quang', x=540, D=170, expr='sad')], cards=[dict(t='21 NĂM TÙ', x=540, y=760, at=1, col='#f2dc8a')],
      say='Dìu Dãnh Quang bị phạt 21 năm tù. Quang đã cùng Vân đầu độc anh Trần Văn Khôi để chiếm chiếc xe máy.'),
 dict(type='stage', label='PHÚC THẨM 1/2/2005', bg='court', cast=[dict(c='toa', x=330, D=170, expr='normal'), dict(c='van', x=780, D=160, face=-1, expr='angry', at=1)],
      say='Cả hai kháng cáo. Ngày 1/2/2005, Tòa phúc thẩm Tòa án nhân dân tối cao xử lại vụ án. Tại tòa, Vân chỉ nhận tội tàng trữ chất độc. Bà ta vẫn chối hai tội giết người và cướp tài sản.'),
 dict(type='stage', label='Y ÁN', bg='court', cast=[dict(c='toa', x=330, D=175, expr='angry', hands=[(.6, -.3, 'scroll')])],
      cards=[dict(t='Y ÁN TỬ HÌNH', x=750, y=780, at=1, col='#c4281f', tc='#fff', fs=34), dict(t='QUANG: 17 NĂM', x=750, y=930, at=2, col='#f2dc8a', fs=34)],
      say='Tòa bác kháng cáo, giữ nguyên án tử hình với Vân. Hội đồng xét xử gọi hành vi của bà ta là tàn nhẫn, mất hết nhân tính. Quang khai báo thành khẩn, được giảm xuống còn 17 năm tù.'),
 dict(type='stage', label='NGÀY 26/10/2005', bg='prison', cast=[dict(c='van', x=540, D=170, expr='sad')],
      say='Ngày 26/10/2005, bản án được thi hành tại Thủ Dầu Một, Bình Dương. Từ cái chết đầu tiên ở Long Khánh, gần 8 năm đã trôi qua.'),
 dict(type='stage', label='NGƯỜI MẸ', bg='prison', cast=[dict(c='me', x=540, D=170, expr='sad', **{'from': 1300})],
      say='Người mẹ ở quận 10 từng vào trại giam thăm con. Khi ấy, Vân nói sẽ cố gắng tìm cách để được ra sớm. {hạ: Lời ấy không bao giờ thành.}'),
 dict(type='stage', label='NHỮNG GIA ĐÌNH Ở LẠI', bg='hospital', icons=[dict(icon='cross', x=540, y=860, s=1.3, at=0)],
      say='Ở nhiều gia đình khác, người thân mất đi mà nhiều năm không biết vì sao. Họ từng tin đó là bệnh, như giấy tờ đã ghi. Phải tới phiên tòa, họ mới biết sự thật.'),
 dict(type='stage', label='GÓI HÓA CHẤT MÀU VÀNG', bg='lab', icons=[dict(icon='handbag', x=450, y=880, s=1.1, at=0), dict(icon='packet_y', x=650, y=880, s=1.0, at=1)],
      say='Một gói hóa chất màu vàng. Một lời khai "nước nấu" bị lật. Và bốn tỉnh chịu đặt hồ sơ cạnh nhau. {rất chậm: Kẻ từng đưa nạn nhân đi cấp cứu, cuối cùng phải trả lời trước tòa.}'),
 dict(type='ke', label='BẠN CHỌN GÌ?', board='MẤU CHỐT|LÀ GÌ?', expr='normal', ask=True,
      say='Gói hóa chất trong giỏ xách, lời khai "nước nấu", hay việc ghép hồ sơ bốn tỉnh. {cao: Theo anh em, đâu là mấu chốt làm lộ Lê Thanh Vân?} [nghỉ 1.0] Bình luận cho mình biết nhé. Và theo dõi Chuyện Chưa Kể để xem vụ tiếp theo.'),
]
EP = [('p1', P1, 'PHẦN 1/3', 'KẺ ĐẦU ĐỘC ĐƯA ĐI VIỆN', 'Phần 2: Vì sao Vân được thả?'),
      ('p2', P2, 'PHẦN 2/3', 'GÓI HÓA CHẤT MÀU VÀNG', 'Phần 3: Lời khai thứ hai'),
      ('p3', P3, 'PHẦN 3/3', 'THÊM 7 CÁI TÊN', 'Theo dõi để xem vụ tiếp theo')]
KH = re.compile(r'\s*(///|//|\[nghỉ\s*[\d.,]+\s*\])\s*|\{(?:nhanh|chậm|rất chậm|hạ|cao|nhấn):\s*|\}')
for name, S, badge, hook, nxt in EP:
    sp = dict(engine='vh', chars='roinuoc', format='vertical', series='NHA SĨ GIẢ VÀ GÓI HÓA CHẤT VÀNG', badge=badge, hook_text=hook, next=nxt,
              cta='THEO DÕI CHUYỆN CHƯA KỂ', tts=True, dao_dien=True, speed=0.92, tag=f'cck-xyanua-{name}', cast=CAST, shots=S)
    json.dump(sp, open(os.path.join(OUT, f'{name}.json'), 'w'), ensure_ascii=False)
    t = json.loads(json.dumps(sp)); t['tts'] = False; durs = []
    for s in t['shots']:
        n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['_sent'] = [.2 + 1.9 * i for i in range(n)]; durs.append(1.9 * n + 1.5)
    t['durs'] = durs
    json.dump(t, open(os.path.join(OUT, f'{name}_t.json'), 'w'), ensure_ascii=False)
    sach = [re.sub(r'\s+', ' ', KH.sub(' ', s['say'])).strip() for s in S]
    open(os.path.join(OUT, f'{name}_sach.txt'), 'w').write('\n'.join(sach))
    print(name, len(S), 'canh', sum(len(x.split()) for x in sach), 'tu', 'cau dai:', [x for x in sach for x in re.split(r'(?<=[.?!…])\s+', x) if len(x.split()) > 18])
