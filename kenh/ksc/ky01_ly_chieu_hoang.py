import json, re
NAMES = ['Lý Huệ Tông','Huệ Tông','Trần Thủ Độ','Thủ Độ','Lý Chiêu Hoàng','Chiêu Hoàng','Phật Kim','Trần Cảnh','Cảnh','Chân Giáo','Thái Đường','Ngô Sĩ Liên','Mông Cổ','Đại Việt','Lê Thái Tông','Lệ Chi','Nguyễn Trãi','Trần Thái Tông']
NUM = {'1237':'một nghìn hai trăm ba mươi bảy','1224':'một nghìn hai trăm hai mươi tư','1225':'một nghìn hai trăm hai mươi lăm','1258':'một nghìn hai trăm năm mươi tám','1232':'một nghìn hai trăm ba mươi hai'}
def tts(x):
    for k,v in NUM.items(): x = x.replace(k, v)
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    x = re.sub(r'\[\[([^\]]*)\[\[([^\]]*)\]\]([^\]]*)\]\]', r'[[\1\2\3]]', x)
    return x
S = [
 dict(type='child_throne', label='', say='Năm 1224, ngai vàng Đại Việt có một vị vua mới bảy tuổi. Là con gái. Và đứng sau cái ngai ấy… là một người đàn ông họ Trần.', shadow_at=2),
 dict(type='ke', label='AI VIẾT CHIẾU?', board='AI VIẾT|TỜ CHIẾU?', expr='normal', ask=True, gap=1.2, say='Một năm sau, cô bé xuống chiếu nhường ngôi cho chồng. Chồng cô cũng mới tám tuổi. Anh em thử nghĩ xem. Hai đứa trẻ, ai thật sự cầm bút viết tờ chiếu đó?'),
 dict(type='sick_king', label='NHÀ LÝ SUY', enter=2, say='Lùi lại một chút. Vua Lý Huệ Tông lúc ấy ốm nặng, lúc tỉnh lúc mê. Quyền thật nằm trong tay Điện tiền chỉ huy sứ Trần Thủ Độ.'),
 dict(type='child_throne', label='NỮ VƯƠNG DUY NHẤT', shadow=False, expr='happy', say='Huệ Tông không có con trai. Thế là ngôi vua trao cho cô con gái nhỏ, Phật Kim. Sử gọi là Lý Chiêu Hoàng. Nữ vương đầu tiên, và duy nhất, của nước ta.'),
 dict(type='pages', label='NGƯỜI HẦU HỌ TRẦN', say='Người hầu quanh nữ vương, Thủ Độ chọn hết. Trong đó có một cậu bé tám tuổi, cháu ông. Tên là Trần Cảnh.'),
 dict(type='towel', label='CHIẾC KHĂN TRẦU', throw_at=2, say='Sử chép lại một chuyện rất trẻ con. Cô bé hay trêu cậu hầu. Một hôm, cô ném chiếc khăn trầu vào người Cảnh.'),
 dict(type='whisper', label='MÁCH CHÚ', say='Cảnh sợ, chạy về mách chú. Thủ Độ nghe xong, chỉ hỏi lại một câu.'),
 dict(type='whisper', label='', fork=True, gap=1.0, say='Nếu đúng thế… thì họ ta thành họ nhà vua. Hay là cả họ bị giết sạch?'),
 dict(type='wedding', label='BỆ HẠ CÓ CHỒNG', say='Ông không chờ ai trả lời. Ông báo luôn cho cả triều: bệ hạ đã có chồng. Mấy ông quan đứng dưới… chỉ biết cúi đầu.'),
 dict(type='swap', label='CUỐI NĂM 1225', say='Cuối năm 1225, Chiêu Hoàng xuống chiếu nhường ngôi cho chồng. Nhà Lý hơn hai trăm năm, hết. Không một giọt máu nào đổ trên điện.'),
 dict(type='ke', label='CHƯA HẾT', board='CÒN MỘT|NGƯỜI NỮA', expr='scared', say='Nhưng chuyện chưa dừng ở cái ngai đâu. Vì vẫn còn một người. Vua cha.'),
 dict(type='pagoda', label='CHÙA CHÂN GIÁO', arrive=2, say='Huệ Tông lúc này đã đi tu ở chùa Chân Giáo. Một hôm, ông đang ngồi nhổ cỏ trong vườn. Thủ Độ đi ngang qua.'),
 dict(type='pagoda', label='NHỔ CẢ RỄ', present=True, root=1, expr='scared', gap=.8, say='Ông đứng lại, buông đúng một câu. Nhổ cỏ thì phải nhổ cả rễ sâu.'),
 dict(type='empty_garden', label='NĂM 1226', say='Huệ Tông nghe, hiểu. Ít lâu sau, ông tự vẫn ở vườn sau chùa. Năm ấy ông mới ngoài ba mươi.'),
 dict(type='collapse', label='THÁI ĐƯỜNG 1232', say='Sáu năm sau, sử còn chép một chuyện rợn hơn. Tôn thất họ Lý về Thái Đường cúng tổ. Và căn nhà… sập xuống.'),
 dict(type='doubt', label='CÓ THẬT KHÔNG?', say='Nhưng khoan tin vội. Chính sử gia Ngô Sĩ Liên cũng nghi chuyện này. Vì mấy chục năm sau, vẫn có người họ Lý làm tướng nhà Trần.'),
 dict(type='ke', label='NĂM 1237', board='BỎ VỢ|CƯỚI CHỊ DÂU', expr='surprised', say='Rồi năm 1237, Chiêu Hoàng mãi chưa có con trai. Thủ Độ ép vua bỏ vợ. Cưới luôn chị dâu, cũng là chị ruột của vợ, đang mang thai ba tháng.'),
 dict(type='mongol', label='NĂM 1258', lift=4, say='Rồi năm 1258, quân Mông Cổ tràn sang. Vua lúc này chính là cậu bé Trần Cảnh năm nào. Cả triều hoảng. Vua hỏi Thủ Độ tính sao. Ông đáp: đầu thần chưa rơi xuống đất, xin bệ hạ đừng lo.'),
 dict(type='scales', label='GIAN THẦN HAY CÔNG THẦN?', ask=True, gap=1.2, say='Một người ép vua cũ đến chết. Cũng là người đứng mũi chịu sào giữ nước. Nếu anh em là người chép sử, anh em ghi ông là gian thần, hay công thần?'),
 dict(type='ke', label='KỲ SAU', board='LỆ CHI VIÊN|1442', expr='happy', say='Viết câu trả lời dưới bình luận nhé. Kỳ sau: vua Lê Thái Tông chết đột ngột ở vườn vải Lệ Chi. Và người bị đổ tội… là Nguyễn Trãi.'),
]
for s in S: s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='KÝ SỬ CHIẾN – BÍ ẨN LỊCH SỬ', badge='KỲ 1', hook_text='VUA 7 TUỔI. AI CẦM QUYỀN?',
          next='Kỳ sau: Vụ án Lệ Chi Viên', cta='THEO DÕI KÝ SỬ CHIẾN', tts=True, speed=0.9, tag='ksc-bian1', shots=S)
json.dump(sp, open('spec.json', 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = len([x for x in re.split(r'(?<=[.?!])\s+', s['say']) if x]); s['dur'] = 1.8 * n + 1.5
json.dump(t, open('spec_t.json', 'w'), ensure_ascii=False)
print(len(S), sum(len(s['say'].split()) for s in S), 'tu')
print(S[2]['tts']); print(S[16]['tts'])
