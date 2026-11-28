"""LIÊN THIÊN – Vợ nhặt (Kim Lân), PHẦN 1/2: nạn đói 1945 -> Tràng kéo xe thóc -> lần 1 hò bâng quơ, cô gái đẩy xe
-> lần 2 cô gầy rạc, trách, ăn 4 bát bánh đúc -> câu nửa đùa nửa thật, cô theo về -> "Chậc, kệ!" -> mua dầu -> đường về xóm ngụ cư
-> ngoài lề: Kim Lân (Nguyễn Văn Tài) đóng lão Hạc trong phim Làng Vũ Đại ngày ấy. Nhử P2: bà cụ Tứ, nồi cháo cám "chè khoán".
python3 vo_nhat_p1.py <thu_muc_ra> -> spec.json + spec_t.json. Số viết bằng chữ số; ký hiệu nhịp chỉ sau dấu câu hoặc bọc cả câu.
6 hook (≥ 3 khuôn; hook 2 giây ≤ 10 âm tiết): (1) chi tiết lạ/con số "Bốn bát bánh đúc, đổi một cô vợ." [CHỌN, vế 2 lật:
cô theo về mà hết truyện không ai biết tên] – (2) câu hỏi thẳng "Ai lại theo trai vì bốn bát bánh đúc?" – (3) lật nghĩa
"Tràng không cưới vợ. Tràng nhặt vợ." – (4) gọi tên kiểu người "Kiểu đàn ông nói đùa một câu, có luôn vợ." – (5) ngoài lề
"Cô vợ ấy, hết truyện vẫn không có tên." – (6) ngoài lề "Người viết Vợ nhặt từng đóng lão Hạc."
Ngoài lề (≥ 2 nguồn): Kim Lân tên thật Nguyễn Văn Tài, đóng lão Hạc trong "Làng Vũ Đại ngày ấy", đạo diễn Phạm Văn Khoa
(Tuổi Trẻ 22/07/2007 "Cuộc trò chuyện cuối cùng với nhà văn Kim Lân"; VnExpress 17/11/2020 "Giới văn chương tưởng nhớ Kim Lân";
VnExpress 02/04/2005 "Khi các nhà văn đóng phim" – vai lão Hạc làm ông nổi tiếng). Nạn đói 1945 hơn 2 triệu người chết
(VnExpress 17/11/2020 dẫn nhà nghiên cứu Nguyễn Hiếu; Tuyên ngôn Độc lập 1945 "hơn hai triệu đồng bào ta bị chết đói").
Trích nguyên văn duy nhất: "Chậc, kệ!" (2 từ). Không dùng "hai hào dầu", câu hò, câu mời nguyên văn (chưa đối chiếu bản gốc).
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CAST = {
    'trang': dict(tag='TRÀNG', skin='#c99062', hair='#140f0c', hair_style='side', outfit='#6a5236', outfit2='#4e3c28', trim='#2a1e14', mark='bigface'),
    'thi': dict(tag='THỊ', skin='#dcae86', hair='#1a1410', hair_style='bun', outfit='#6e6a5e', outfit2='#545048', trim='#2a2a24', mark='pale'),
    'treem': dict(tag='TRẺ CON XÓM', skin='#e0aa7c', hair='#140f0c', hair_style='band', outfit='#8a7a5a', outfit2='#6a5c44', trim='#3a2a1a'),
    'hangxom': dict(tag='HÀNG XÓM', skin='#d4a070', hair='#e8e4da', hair_style='khan', hat='#3a3228', outfit='#5a5048', outfit2='#443c36', trim='#2a2420', mark='brow'),
    'kimlan': dict(tag='NHÀ VĂN KIM LÂN', skin='#e0ae84', hair='#8a8478', hair_style='side', outfit='#efe6cf', outfit2='#cfc3a3', trim='#5a4a2a'),
    'laohac': dict(tag='VAI LÃO HẠC', skin='#d9a070', hair='#e8e4da', hair_style='bald', outfit='#7a5a3a', outfit2='#5a4028', trim='#3a2a1a', mark='brow'),
}
S = [
 dict(type='stage', label='', bg='market',
      cast=[dict(c='trang', x=340, D=175, expr='happy'), dict(c='thi', x=760, D=165, face=-1, expr='normal')],
      icons=[dict(icon='bowl', x=500, y=1225, s=.7, at=0), dict(icon='bowl', x=580, y=1225, s=.7, at=0), dict(icon='bowl', x=540, y=1180, s=.7, at=0), dict(icon='bowl', x=540, y=1135, s=.7, at=0)],
      say='{cao: Bốn bát bánh đúc, đổi một cô vợ.} // Cô ấy theo anh Tràng về nhà. /// {chậm: Vậy mà hết truyện, vẫn không ai biết tên cô.}'),
 dict(type='ke', label='LIÊN THIÊN', board='VỢ NHẶT|KIM LÂN', expr='normal',
      say='Đây là Vợ nhặt của Kim Lân, phần 1. // Muốn hiểu vì sao cô theo về, phải biết năm ấy đói tới mức nào.'),
 dict(type='stage', label='NĂM 1945', bg='village_night',
      cast=[dict(c='hangxom', x=540, D=170, expr='sad')],
      cards=[dict(t='HƠN 2 TRIỆU NGƯỜI CHẾT ĐÓI', x=540, y=1300, at=0, col='#4a4038', tc='#fff', fs=28)],
      say='Năm 1945, nạn đói làm hơn 2 triệu người chết. // Người đói từ khắp nơi dắt díu nhau đi, ngồi dọc đường. /// {hạ: Cái đói tràn tới cả xóm ngụ cư, nơi Tràng ở.}'),
 dict(type='stage', label='ANH CU TRÀNG', bg='village',
      cast=[dict(c='trang', x=540, D=190, expr='happy')],
      say='Tràng làm nghề kéo xe thóc thuê. // Người to như con gấu, mặt thô, nhà nghèo, lại là dân ngụ cư. /// {hạ: Ngày thường, chẳng cô nào chịu lấy.}'),
 dict(type='stage', label='LẦN GẶP ĐẦU', bg='village',
      cast=[dict(c='trang', x=250, D=165, expr='happy')],
      icons=[dict(icon='cart', x=640, y=1150, s=1.1, at=0)],
      say='Lần gặp đầu, Tràng kéo xe thóc lên dốc tỉnh, mỏi quá, hò bâng quơ mấy câu. // Mấy cô ngồi trước cửa kho cười ồ. /// {nhấn: Một cô chạy ra đẩy xe thật.}'),
 dict(type='stage', label='GẶP LẠI', bg='market',
      cast=[dict(c='thi', x=720, D=170, face=-1, expr='angry'), dict(c='trang', x=320, D=175, expr='surprised', at=0, **{'from': -300})],
      say='Mấy hôm sau gặp lại, Tràng không nhận ra. // Cô gầy hẳn đi, áo rách tả tơi. /// {hạ: Cô sầm mặt trách: hôm ấy hẹn rồi lại để người ta mất mặt.}'),
 dict(type='stage', label='BỐN BÁT', bg='market',
      cast=[dict(c='thi', x=330, D=180, expr='normal', hands=[[.6, -.15, 'bowl']])],
      icons=[dict(icon='bowl', x=720, y=1225, s=.7, at=1), dict(icon='bowl', x=800, y=1225, s=.7, at=1), dict(icon='bowl', x=760, y=1180, s=.7, at=1)],
      cards=[dict(t='4 BÁT BÁNH ĐÚC', x=540, y=1300, at=1, col='#c4281f', tc='#fff', fs=30)],
      say='Tràng cười, bảo ăn gì thì ăn. // Cô ngồi xuống, cắm đầu ăn một mạch 4 bát bánh đúc, không nói câu nào.'),
 dict(type='stage', label='NỬA ĐÙA NỬA THẬT', bg='market',
      cast=[dict(c='trang', x=320, D=175, expr='happy'), dict(c='thi', x=780, D=170, face=-1, expr='normal')],
      say='Ăn xong, Tràng nói nửa đùa nửa thật: có về với tớ thì về. /// {nhấn: Cô về thật.}'),
 dict(type='ke', label='ANH EM CHỌN GÌ?', board='NHẬN THÊM|HAY RÚT LỜI?', expr='normal', ask=True, gap=1.2,
      say='Một mình Tràng còn chưa lo nổi miệng ăn. {cao: Nếu anh em là Tràng, nhận thêm một người, hay bảo chỉ đùa thôi?} [nghỉ 1.2] Nhận thì cả hai có thể cùng đói. Rút lời thì cô quay lại chợ, với cái đói.'),
 dict(type='stage', label='"CHẬC, KỆ!"', bg='market',
      cast=[dict(c='trang', x=440, D=190, expr='surprised')],
      icons=[dict(icon='lamp', x=720, y=1150, s=1.0, at=1)],
      say='Tràng cũng chợn nghĩ một lúc. /// {nhấn: Chậc, kệ!} // Rồi Tràng dẫn cô vào chợ, mua ít dầu về thắp.'),
 dict(type='stage', label='ĐƯỜNG VỀ', bg='village',
      cast=[dict(c='trang', x=330, D=175, expr='happy', **{'from': -300}), dict(c='thi', x=760, D=160, face=1, expr='sad', **{'from': 1350})],
      say='Trên đường về, Tràng đi trước, tủm tỉm cười một mình. // Cô vợ đi sau, cúi mặt, khép nép.'),
 dict(type='stage', label='CẢ XÓM NHÌN', bg='village',
      cast=[dict(c='treem', x=300, D=140, expr='happy'), dict(c='hangxom', x=780, D=170, face=-1, expr='sad')],
      say='Trẻ con trong xóm thấy lạ, chạy theo trêu. // Người lớn đứng ở cửa nhìn ra, thì thầm, có người thở dài. /// {hạ: Đói thế này, lại còn rước thêm người về.}'),
 dict(type='stage', label='CÁI GIÁ MỘT CON NGƯỜI', bg='village_night',
      cast=[dict(c='thi', x=540, D=185, expr='sad')],
      say='Cô theo một người lạ, đâu phải vì yêu. // Ở chợ tỉnh năm ấy, một bữa no đã giống một lời hứa. /// {chậm: Cái tên Vợ nhặt nghe như đùa, mà nói đúng giá một con người năm đói.}'),
 dict(type='stage', label='NGOÀI SÁCH', bg='village',
      cast=[dict(c='kimlan', x=420, D=180, expr='normal')],
      icons=[dict(icon='clapper', x=720, y=1130, s=.85, at=1)],
      say='Chuyện ngoài sách. Kim Lân tên thật là Nguyễn Văn Tài. // Ông không chỉ viết, mà còn đóng phim. /// {nhấn: Ông từng vào vai lão Hạc, trong phim Làng Vũ Đại ngày ấy.}'),
 dict(type='stage', label='NHÀ VĂN THÀNH LÃO HẠC', bg='village',
      cast=[dict(c='laohac', x=380, D=175, expr='sad')],
      icons=[dict(icon='dog_sad', x=690, y=1170, s=1.2, at=1)],
      say='Đạo diễn Phạm Văn Khoa mời ông vào vai. // Vai ấy làm ông nổi tiếng trên màn ảnh. /// {chậm: Người viết anh cu Tràng, lại thành ông lão bán chó mà ta vừa kể.}'),
 dict(type='ke', label='TẬP SAU', board='PHẦN 2|BÀ CỤ TỨ', expr='normal',
      say='Về tới nhà, mẹ Tràng chưa về. {cao: Bà cụ sẽ nói gì, khi thấy một người đàn bà lạ ngồi trong nhà mình?} [nghỉ 1.0] Bình luận nhé. // Phần 2, Liên Thiên kể tiếp, cả nồi cháo cám bà gọi là chè khoán. Theo dõi Liên Thiên để xem nhé.'),
]
NAMES = ['Tràng', 'Kim Lân', 'Nguyễn Văn Tài', 'Liên Thiên', 'Vợ nhặt', 'Lão Hạc', 'lão Hạc', 'Làng Vũ Đại', 'Phạm Văn Khoa']
def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    return x
for s in S: s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='LIÊN THIÊN – VỢ NHẶT', badge='PHẦN 1/2', hook_text='4 BÁT BÁNH ĐÚC, 1 CÔ VỢ',
          next='Phần sau: Bà cụ Tứ', cta='THEO DÕI LIÊN THIÊN', tts=True, speed=0.9, tag='lt-vn1', cast=CAST, shots=S)
json.dump(sp, open(os.path.join(OUT, 'spec.json'), 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
B = lambda x: re.sub(r'\s+', ' ', re.sub(r'(^|\s)/{1,3}(?=\s|$)', ' ', re.sub(r'\{(?:chậm|rất chậm|nhấn|hạ|nhanh|cao)\s*:\s*', '', re.sub(r'\[nghỉ\s*[\d.,]+\s*\]', ' ', x)).replace('}', ''))).strip()
for s in t['shots']:
    n = [x for x in re.split(r'(?<=[.?!…])\s+', B(s['say'])) if x]; d = 0.0; se = []
    for x in n: se.append(round(d, 2)); d += .32 * len(x.split()) + .3
    s['dur'] = d + 1.0; s['_sent'] = se
t['durs'] = [s['dur'] for s in t['shots']]
json.dump(t, open(os.path.join(OUT, 'spec_t.json'), 'w'), ensure_ascii=False)
print(len(S), 'canh', sum(len(B(s['say']).split()) for s in S), 'tu', round(sum(t['durs']) / .9), 's')
