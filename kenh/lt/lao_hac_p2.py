"""LIÊN THIÊN – Lão Hạc (Nam Cao), PHẦN 2/2: gửi vườn (văn tự đứng tên ông giáo) + tiền ma chay -> ăn củ chuối, từ chối giúp
-> Binh Tư kể lão xin bả chó -> ông giáo nghĩ sai -> lão mất (kể nhẹ) -> "Không! Cuộc đời chưa hẳn đã đáng buồn" -> ngoài lề Trùm Luông.
python3 lao_hac_p2.py <thu_muc_ra> -> spec.json + spec_t.json. Số viết bằng chữ số; ký hiệu nhịp chỉ sau dấu câu hoặc bọc cả câu (W87 v3.1).
6 hook đã viết (≥ 3 khuôn): (1) chi tiết ngoài lề "Ngoài đời, nguyên mẫu lão Hạc cũng đã đi xin bả chó" – (2) câu hỏi thẳng
"Một ông lão đói tới ăn củ chuối, sao không tiêu đồng nào trong bọc tiền?" – (3) gọi tên kiểu người "Kiểu ông bố thà nhịn đói
chứ không đụng một đồng của con" – (4) hành động "Lão Hạc gửi hết tiền cho hàng xóm, rồi về nhà ăn củ chuối" – (5) lật
"Ai cũng tưởng lão Hạc đã hóa người xấu. Thật ra…" – (6) chi tiết lạ + lật "Nhà lão Hạc đã hết chó. Vậy mà lão đi xin bả chó.
Ông giáo tưởng lão đã hóa người xấu." [CHỌN – khuôn chi tiết lạ + lật nghĩa "tưởng… thật ra…"; P1 đã dùng chi tiết lạ + câu hỏi].
Ngoài lề (2 nguồn): nguyên mẫu thứ hai ông Trùm Luông (Trần Quý Đào), nhà gần Trùm San, nghèo, sống cô đơn, xin bả chó của một người
cùng làng Đại Hoàng (VTC News 04/12/2023 "Chuyện 2 ông trùm là nguyên mẫu nhân vật lão Hạc ở làng Vũ Đại" – Báo Lạng Sơn đăng lại
05/12/2023; Tiền Phong 17/12/2023 "Chuyện Lão Hạc, cậu Vàng, Chí Phèo, Thị Nở vẫn còn tiếp…"). Văn tự nhượng vườn cho ông giáo
"để không ai còn tơ tưởng, dòm ngó đến" (VTC dẫn nguyên tác). Không dùng số sào/số đồng (chưa đối chiếu bản gốc).
Trích nguyên văn duy nhất: "Không! Cuộc đời chưa hẳn đã đáng buồn" (7 từ).
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CAST = {
    'laohac': dict(tag='LÃO HẠC', skin='#d9a070', hair='#e8e4da', hair_style='bald', outfit='#7a5a3a', outfit2='#5a4028', trim='#3a2a1a', mark='brow'),
    'onggiao': dict(tag='ÔNG GIÁO', skin='#e6b48a', hair='#140f0c', hair_style='khan', hat='#2a2a2a', outfit='#efe6cf', outfit2='#cfc3a3', trim='#7a5a2a', mark='mustache'),
    'contrai': dict(tag='CON TRAI LÃO', skin='#e0a878', hair='#140f0c', hair_style='band', outfit='#4a6a4a', outfit2='#36503a', trim='#c8a24a'),
    'muc': dict(tag='THẰNG MỤC', skin='#d8a070', hair='#140f0c', hair_style='khan', hat='#3a3a2a', outfit='#5a5a4a', outfit2='#44443a', trim='#2a2a2a', mark='scar'),
    'xien': dict(tag='THẰNG XIÊN', skin='#e0aa7c', hair='#140f0c', hair_style='nonla', outfit='#6a4a3a', outfit2='#4e362a', trim='#2a2a2a', mark='mole'),
    'trumsan': dict(tag='ÔNG TRÙM SAN', skin='#d9a070', hair='#e8e4da', hair_style='khan', hat='#4a3a2a', outfit='#6a5a4a', outfit2='#4e4236', trim='#3a2a1a', mark='pale'),
    'binhtu': dict(tag='BINH TƯ', skin='#d8a070', hair='#140f0c', hair_style='khan', hat='#2a2a24', outfit='#3e4a5a', outfit2='#2e3846', trim='#1a1a1a', mark='scar'),
    'trumluong': dict(tag='ÔNG TRÙM LUÔNG', skin='#d4a070', hair='#e8e4da', hair_style='bald', outfit='#5a5048', outfit2='#443c36', trim='#2a2420', mark='bigface'),
}
S = [
 dict(type='stage', label='', bg='village',
      cast=[dict(c='laohac', x=330, D=175, expr='normal', at=1)],
      icons=[dict(icon='packet', x=760, y=1150, s=1.5, at=0)],
      cards=[dict(t='XIN BẢ CHÓ', x=540, y=1250, at=1, col='#c4281f', tc='#fff', fs=30)],
      say='{cao: Nhà lão Hạc đã hết chó.} Vậy mà lão lại đi xin bả chó. /// {chậm: Ông giáo nghe xong, tưởng lão đã hóa người xấu.}'),
 dict(type='ke', label='LIÊN THIÊN', board='LÃO HẠC|PHẦN CUỐI', expr='normal',
      say='Phần trước, lão bán cậu Vàng. // Phần này, ta đi tìm xem gói bả ấy để dành cho ai.'),
 dict(type='stage', label='HAI VIỆC NHỜ', bg='room',
      cast=[dict(c='onggiao', x=320, D=175, expr='surprised'), dict(c='laohac', x=780, D=175, face=-1, expr='sad', at=0, **{'from': 1300})],
      cards=[dict(t='GIỮ HỘ MẢNH VƯỜN', x=540, y=1150, at=1, col='#2e5a46', tc='#fff', fs=30)],
      say='Khóc xong, lão nhờ ông giáo hai việc. // Việc thứ nhất, giữ hộ mảnh vườn, để con trai về có đất mà làm ăn.'),
 dict(type='stage', label='VĂN TỰ', bg='room',
      cast=[dict(c='laohac', x=540, D=185, expr='normal', hands=[[.6, -.15, 'scroll']])],
      cards=[dict(t='ĐỨNG TÊN ÔNG GIÁO', x=540, y=1150, at=1, col='#4a4038', tc='#fff', fs=30)],
      say='Mà lão không gửi bằng miệng. Lão làm văn tự, cho vườn đứng tên ông giáo. /// {hạ: Có vậy, không ai còn dòm ngó mảnh đất của con lão.}'),
 dict(type='stage', label='TIỀN MA CHAY', bg='room',
      cast=[dict(c='laohac', x=330, D=175, expr='sad')],
      icons=[dict(icon='coin', x=720, y=1100, s=1.2, at=0), dict(icon='coin', x=800, y=1150, s=1.0, at=0)],
      say='Việc thứ hai, lão gửi ông giáo chỗ tiền dành dụm, có cả tiền bán cậu Vàng. // Lão dặn, lỡ lão chết thì nhờ ông lo ma chay, đừng để hàng xóm phải tốn.'),
 dict(type='stage', label='ĂN CỦ CHUỐI', bg='village',
      cast=[dict(c='laohac', x=540, D=185, expr='sad')],
      icons=[dict(icon='bowl', x=780, y=1225, s=.8, at=1)],
      say='Gửi xong, trong nhà lão hết sạch. // Lão kiếm được gì thì ăn nấy: củ chuối, sung luộc, rau má. /// {hạ: Tiền thì có, nhưng lão không đụng vào một đồng.}'),
 dict(type='stage', label='TỪ CHỐI', bg='room',
      cast=[dict(c='onggiao', x=320, D=175, expr='sad', hands=[[.6, -.15, 'bowl']]), dict(c='laohac', x=780, D=175, face=-1, expr='angry')],
      say='Ông giáo thương, lén giúp lão. Lão từ chối, gần như là hách dịch. // Rồi lão tránh mặt luôn cả ông giáo.'),
 dict(type='stage', label='BINH TƯ', bg='village',
      cast=[dict(c='onggiao', x=320, D=175, expr='normal'), dict(c='binhtu', x=780, D=170, face=-1, expr='happy', at=0, **{'from': 1350})],
      say='Một hôm, ông giáo than chuyện lão với Binh Tư, tay ăn trộm có nghề trong làng. /// {hạ: Binh Tư bĩu môi: lão làm bộ đấy, lão vừa xin tôi ít bả chó.}'),
 dict(type='stage', label='CON CHÓ HAY SANG VƯỜN', bg='village',
      cast=[dict(c='binhtu', x=330, D=175, expr='happy')],
      icons=[dict(icon='packet', x=760, y=1150, s=1.3, at=0), dict(icon='bottle', x=760, y=960, s=1.0, at=1)],
      say='Lão bảo có con chó lạ hay sang vườn, lão định cho nó xơi một bữa. // Trúng thì lão với Binh Tư uống rượu.'),
 dict(type='ke', label='ANH EM TIN AI?', board='TIN LÃO HẠC|HAY BINH TƯ?', expr='normal', ask=True, gap=1.2,
      say='Một ông lão hiền như đất, nay đi xin bả chó của tay ăn trộm. {cao: Nếu anh em là ông giáo, anh em tin lão Hạc, hay tin lời Binh Tư?} [nghỉ 1.2] Tin lão thì có thể bị lừa. Nghi lão thì có thể oan một người tốt.'),
 dict(type='stage', label='ĐÁNG BUỒN', bg='room',
      cast=[dict(c='onggiao', x=540, D=190, expr='sad')],
      say='Ông giáo tin Binh Tư. Người tử tế như lão, cuối cùng cũng hóa ra thế. /// {chậm: Ông thấy cuộc đời mỗi ngày lại thêm đáng buồn.}'),
 dict(type='stage', label='ÔNG GIÁO ĐÃ SAI', bg='village_night',
      cast=[dict(c='onggiao', x=320, D=175, expr='surprised'), dict(c='binhtu', x=780, D=170, face=-1, expr='sad')],
      say='Nhưng ông giáo đã đoán sai. /// {hạ: Gói bả ấy không dành cho con chó nào cả.} // Lão Hạc mất sau một cơn vật vã. Cả làng không ai hiểu, chỉ ông giáo với Binh Tư hiểu.'),
 dict(type='stage', label='CÁI CHẾT LÃO CHỌN', bg='riverbank_dawn',
      icons=[dict(icon='dog_sad', x=540, y=1170, s=1.4, at=0)],
      say='Lão từng gọi cậu Vàng về ăn bữa cơm cuối, để người ta bắt nó. // Giờ lão chọn đúng cái chết của một con chó, như tự phạt mình. /// {hạ: Thà vậy, còn hơn bán đi mảnh vườn của con, hay tiêu vào món tiền lo hậu sự.}'),
 dict(type='stage', label='"KHÔNG!"', bg='room',
      cast=[dict(c='onggiao', x=540, D=195, expr='sad')],
      cards=[dict(t='"KHÔNG!"', x=540, y=1150, at=0, col='#c4281f', tc='#fff', fs=30)],
      say='Ông giáo nghĩ lại. /// {nhấn: Không! Cuộc đời chưa hẳn đã đáng buồn.} // Hay vẫn đáng buồn, nhưng theo nghĩa khác: người tốt vẫn còn, chỉ là cái nghèo dồn họ tới đường cùng. // Và mảnh vườn ấy, ông sẽ cố giữ cho con lão.'),
 dict(type='stage', label='NGOÀI SÁCH: ÔNG TRÙM LUÔNG', bg='village',
      cast=[dict(c='trumluong', x=360, D=175, expr='sad')],
      icons=[dict(icon='packet', x=790, y=1150, s=1.2, at=1)],
      say='Chuyện ngoài sách. Phần trước ta nói nguyên mẫu lão Hạc là ông Trùm San. // Nhưng người làng Đại Hoàng kể còn một ông nữa, ông Trùm Luông, nhà ngay gần đó. /// {hạ: Ông nghèo, sống một mình, và cũng từng xin bả chó của một người cùng làng.}'),
 dict(type='stage', label='HAI ÔNG LÃO THẬT', bg='village',
      cast=[dict(c='trumsan', x=320, D=170, expr='sad'), dict(c='trumluong', x=780, D=170, face=-1, expr='sad')],
      say='Theo lời người làng, một ông cho lão Hạc con chó vàng và đứa con đi cao su. Một ông cho lão gói bả. // {chậm: Người làng tin, Nam Cao đã ghép hai ông lão hàng xóm thành một lão Hạc.}'),
 dict(type='ke', label='TẬP SAU', board='TẬP SAU|VỢ NHẶT', expr='normal',
      say='{cao: Nếu con trai lão về, nhận lại mảnh vườn, anh có biết cha đã đổi gì để giữ nó không?} [nghỉ 1.0] Bình luận nhé. // Tập sau, Liên Thiên kể Vợ nhặt: một anh nghèo nhặt được vợ chỉ sau bốn bát bánh đúc. Theo dõi Liên Thiên để xem nhé.'),
]
NAMES = ['Lão Hạc', 'Nam Cao', 'Liên Thiên', 'Đại Hoàng', 'Trùm San', 'Trùm Luông', 'Binh Tư', 'cậu Vàng', 'Vợ nhặt']
def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    return x
for s in S: s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='LIÊN THIÊN – LÃO HẠC', badge='PHẦN 2/2', hook_text='HẾT CHÓ, SAO XIN BẢ CHÓ?',
          next='Tập sau: Vợ nhặt', cta='THEO DÕI LIÊN THIÊN', tts=True, speed=0.9, tag='lt-lh2', cast=CAST, shots=S)
json.dump(sp, open(os.path.join(OUT, 'spec.json'), 'w'), ensure_ascii=False)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'editor'))
t = json.loads(json.dumps(sp)); t['tts'] = False
B = lambda x: re.sub(r'\s+', ' ', re.sub(r'(^|\s)/{1,3}(?=\s|$)', ' ', re.sub(r'\{(?:chậm|rất chậm|nhấn|hạ|nhanh|cao)\s*:\s*', '', re.sub(r'\[nghỉ\s*[\d.,]+\s*\]', ' ', x)).replace('}', ''))).strip()
for s in t['shots']:
    n = [x for x in re.split(r'(?<=[.?!…])\s+', B(s['say'])) if x]; d = 0.0; se = []
    for x in n: se.append(round(d, 2)); d += .32 * len(x.split()) + .3
    s['dur'] = d + 1.0; s['_sent'] = se
t['durs'] = [s['dur'] for s in t['shots']]
json.dump(t, open(os.path.join(OUT, 'spec_t.json'), 'w'), ensure_ascii=False)
print(len(S), 'canh', sum(len(B(s['say']).split()) for s in S), 'tu', round(sum(t['durs']) / .9), 's')
