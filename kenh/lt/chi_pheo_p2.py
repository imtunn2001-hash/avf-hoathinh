"""LIÊN THIÊN – Chí Phèo (Nam Cao), PHẦN 2/3: cổng nhà Bá Kiến -> tay sai -> Thị Nở bên bờ sông, bát cháo hành.
python3 chi_pheo_p2.py <thu_muc_ra> -> spec.json + spec_t.json (bản soát). Số viết bằng chữ số trong 'say' (máy tự đọc).
Ngoài lề (≥ 2 nguồn): nhà Bá Kiến có thật ở làng Đại Hoàng, nguyên mẫu ông Chánh Bính, chánh tổng Đại Hoàng
(Tiền Phong 15/3/2008 – bài của con gái Nam Cao; VnExpress 28/8/2020; Báo Văn Hóa 4/8/2025; Đại Đoàn Kết 10/7/2025);
phim "Làng Vũ Đại ngày ấy" quay năm 1982, Bùi Cường đóng Chí Phèo, Đức Lưu đóng Thị Nở (VnExpress 2020; VTC News; Báo Pháp luật).
"""
import json, os, re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
NAMES = ['Chí Phèo', 'Bá Kiến', 'Thị Nở', 'Đội Tảo', 'Vũ Đại', 'Đại Hoàng', 'Nam Cao', 'Đức Lưu', 'Bùi Cường', 'Chánh Bính']
def tts(x):
    for n in sorted(NAMES, key=len, reverse=True):
        x = re.sub(r'(?<!\[\[)(?<![\wÀ-ỹ])' + re.escape(n) + r'(?![\wÀ-ỹ])(?!\]\])', '[[' + n + ']]', x)
    return x
CAST = {
    'bakien': dict(tag='BÁ KIẾN', skin='#e6b48a', hair='#1b1512', hair_style='khan', hat='#1a1a1a', outfit='#2b2b36', outfit2='#1c1c24', trim='#b8963e', w=1.25, beard=True),
    'doitao': dict(tag='ĐỘI TẢO', skin='#d69a68', hair='#1e1714', hair_style='side', outfit='#6a5a3e', outfit2='#4c402c', trim='#4c402c', mark='mustache'),
    'cothino': dict(tag='BÀ CÔ THỊ NỞ', skin='#d8a87c', hair='#8a8a8a', hair_style='bun', outfit='#4a4038', outfit2='#342c26', trim='#342c26', mark='brow'),
}
S = [
 dict(type='night_gate', label='',
      say='Cả làng Vũ Đại, không ai dám cãi cụ Bá Kiến. Vậy mà một gã say rượu cầm dao đến tận cổng chửi, cụ lại… mời vào nhà uống rượu?'),
 dict(type='ke', label='PHẦN TRƯỚC', board='CHÍ PHÈO|ĐI TÙ VỀ', expr='normal',
      say='Phần trước, Chí Phèo đi tù về, đầu trọc lốc, răng cạo trắng, vừa đi vừa chửi cả làng. Hôm nay, hắn tìm đến đúng người đã đẩy hắn vào tù.'),
 dict(type='stage', label='TRƯỚC CỔNG CỤ BÁ', bg='village',
      cast=[dict(c='chipheo', x=560, D=190, expr='angry', hands=[[.7, -.1, 'sword', 20]]), dict(c='dan1', x=130, D=110, expr='scared', tag=False, at=1), dict(c='dan2', x=980, D=110, face=-1, expr='scared', tag=False, at=1)],
      say='Chí uống say, cầm dao đứng trước cổng nhà cụ Bá, gọi đích danh mà chửi. Rồi hắn lăn ra đất, kêu làng ăn vạ. Hàng xóm ló ra xem, chẳng ai dám lại gần.'),
 dict(type='stage', label='CỤ BÁ RA CỔNG', bg='village',
      cast=[dict(c='chipheo', x=330, D=180, expr='surprised'), dict(c='bakien', x=780, D=185, face=-1, expr='happy', at=1)],
      cards=[dict(t='ANH CHÍ ĐẤY À?', x=760, y=640, at=1)],
      say='Ai cũng nghĩ cụ Bá sẽ gọi lính. Nhưng cụ bước ra, cười xởi lởi, gọi hắn bằng anh. Rồi cụ kéo Chí vào nhà, rót rượu mời.'),
 dict(type='stage', label='MỀM NẮN RẮN BUÔNG', bg='paper',
      cast=[dict(c='bakien', x=300, D=175, expr='happy')],
      cards=[dict(t='MỀM NẮN', x=760, y=760, at=1, col='#f2dc8a'), dict(t='RẮN BUÔNG', x=760, y=960, at=1, col='#c4281f', tc='#fff')],
      say='Cụ Bá có một mẹo làm quan. Gói gọn trong bốn chữ: mềm nắn rắn buông. Kẻ yếu thì bóp, kẻ liều thì vuốt ve, rồi dùng nó làm việc cho mình.'),
 dict(type='stage', label='MỘT ĐỒNG BẠC', bg='room',
      cast=[dict(c='bakien', x=300, D=175, expr='happy'), dict(c='chipheo', x=770, D=180, face=-1, expr='happy')],
      icons=[dict(icon='coin', x=540, y=820, s=1.3, at=1)],
      say='Uống xong, cụ còn dúi cho Chí một đồng bạc. Gã vừa đòi đâm chém lúc nãy cầm tiền ra về, quên luôn mình đến làm gì.'),
 dict(type='stage', label='ĐI ĐÒI NỢ', bg='village',
      cast=[dict(c='chipheo', x=320, D=185, expr='angry', hands=[[.7, -.1, 'sword', 20]]), dict(c='doitao', x=780, D=170, face=-1, expr='scared', at=1)],
      icons=[dict(icon='coin', x=560, y=760, s=1.1, at=2)],
      say='Ít hôm sau, cụ sai Chí đến nhà Đội Tảo đòi nợ. Đội Tảo cũng là tay anh chị, đứa nào sứt đầu thì cụ cũng lợi. Nhưng Chí đòi được tiền về. Cụ Bá thưởng cho hắn năm sào vườn ngoài bãi.'),
 dict(type='drunk', label='TAY SAI',
      say='Từ đó, Chí thành tay sai của nhà cụ Bá. Ai cụ ghét, Chí đến phá. Hắn say triền miên, chẳng còn nhớ nổi mình bao nhiêu tuổi.'),
 dict(type='stage', label='CHUYỆN NGOÀI SÁCH', bg='village',
      cards=[dict(t='NHÀ BÁ KIẾN', x=540, y=640, at=0, col='#c4281f', tc='#fff'), dict(t='CÓ THẬT', x=540, y=780, at=1, col='#f2dc8a')],
      say='Làng Vũ Đại ngoài đời là làng Đại Hoàng, quê Nam Cao. Ở đó vẫn còn một ngôi nhà gỗ ba gian hai chái, dân làng gọi là nhà Bá Kiến. Con gái Nam Cao kể, chủ nhà xưa là ông Chánh Bính, chánh tổng Đại Hoàng. Ông được coi là nguyên mẫu của cụ Bá.'),
 dict(type='stage', label='ĐÊM TRĂNG BỜ SÔNG', bg='riverbank',
      cast=[dict(c='thino', x=700, D=165, face=-1, expr='normal', at=1), dict(c='chipheo', x=260, D=180, expr='normal')],
      say='Rồi một đêm trăng, Chí say khướt, đi ra bờ sông. Dưới gốc chuối, Thị Nở đang ngủ quên. Thị nghèo, xấu, lại dở hơi, ở với bà cô, cả làng chẳng ai đoái hoài.'),
 dict(type='stage', label='NỬA ĐÊM', bg='riverbank',
      cast=[dict(c='chipheo', x=380, D=170, expr='sad'), dict(c='thino', x=700, D=165, face=-1, expr='surprised')],
      say='Đêm ấy, hai con người bị cả làng bỏ rơi ở bên nhau. Nửa đêm, Chí bị cảm, nôn thốc nôn tháo. Thị Nở dìu hắn vào túp lều.'),
 dict(type='stage', label='SÁNG HÔM SAU', bg='riverbank_dawn',
      cast=[dict(c='chipheo', x=520, D=180, expr='surprised')],
      cards=[dict(t='TIẾNG CHIM', x=640, y=650, at=1), dict(t='TIẾNG ĐI CHỢ', x=700, y=780, at=1, col='#f6e6c0')],
      say='Sáng hôm sau, lần đầu sau bao nhiêu năm, Chí tỉnh rượu. Hắn nghe tiếng chim hót, tiếng người đi chợ, tiếng mái chèo gõ vào mạn thuyền. Hắn chợt nhớ ngày xưa mình từng mơ một gia đình nhỏ. Chồng cày thuê, vợ dệt vải.'),
 dict(type='stage', label='BÁT CHÁO HÀNH', bg='room',
      cast=[dict(c='chipheo', x=320, D=175, expr='sad'), dict(c='thinoa', x=760, D=165, face=-1, expr='happy', at=1, hands=[[.6, -.15, 'bowl']])],
      say='Thì Thị Nở bưng vào một nồi cháo hành nóng. Chí ngẩn người. Cả đời, hắn chưa từng được ai cho không thứ gì. Muốn gì cũng phải giật, phải cướp. Ăn bát cháo, mắt hắn ươn ướt.'),
 dict(type='ke', label='ANH EM NGHĨ SAO?', board='BÁT CHÁO|HÀNH', expr='normal', ask=True, gap=1.2,
      say='Anh em thử nghĩ. Một bát cháo hành, món rẻ nhất làng. Sao nó lại làm một kẻ ai cũng sợ muốn làm lại cuộc đời?'),
 dict(type='stage', label='CHUYỆN NGOÀI SÁCH', bg='paper',
      cards=[dict(t='LÀNG VŨ ĐẠI NGÀY ẤY', x=540, y=640, at=0, col='#c4281f', tc='#fff', fs=40), dict(t='NĂM 1982', x=540, y=780, at=0, col='#f2dc8a')],
      cast=[dict(c='chipheo', x=320, D=150, expr='happy', at=1), dict(c='thinoa', x=760, D=150, face=-1, expr='happy', at=1)],
      say='Năm 1982, chuyện này lên phim Làng Vũ Đại ngày ấy. Bùi Cường đóng Chí Phèo, Đức Lưu đóng Thị Nở. Vai diễn ấy gắn với bà suốt mấy chục năm. Nhiều người vẫn gọi bà là Thị Nở.'),
 dict(type='stage', label='Ở VỚI TỚ NHÉ?', bg='room',
      cast=[dict(c='chipheo', x=330, D=175, expr='happy'), dict(c='thino', x=760, D=165, face=-1, expr='happy')],
      say='Không phải vì cháo ngon. Mà lần đầu có người đối xử với hắn như một con người. Chí thấy mình thèm lương thiện. Hắn rủ Thị Nở về ở chung một nhà. Thị Nở bẽn lẽn, bảo phải về hỏi bà cô đã.'),
 dict(type='ke', label='PHẦN 3', board='BÀ CÔ|THỊ NỞ', expr='scared',
      say='Nhưng bà cô Thị Nở sẽ nói gì? Và vì sao câu hỏi của Chí sau đó lại ám ảnh người đọc hơn 80 năm? Theo dõi Liên Thiên để xem phần ba nhé.'),
]
for s in S: s['tts'] = tts(s['say'])
sp = dict(engine='vh', chars='roinuoc', format='vertical', series='LIÊN THIÊN – CHÍ PHÈO', badge='PHẦN 2/3', hook_text='SAO BÁ KIẾN MỜI RƯỢU CHÍ?',
          next='Phần sau: Bà cô Thị Nở', cta='THEO DÕI LIÊN THIÊN', tts=True, speed=0.9, tag='lt-cp2', cast=CAST, shots=S)
json.dump(sp, open(os.path.join(OUT, 'spec.json'), 'w'), ensure_ascii=False)
t = json.loads(json.dumps(sp)); t['tts'] = False
for s in t['shots']:
    n = [x for x in re.split(r'(?<=[.?!…])\s+', s['say']) if x]; d = 0.0; se = []
    for x in n: se.append(round(d, 2)); d += .32 * len(x.split()) + .3
    s['dur'] = d + 1.0; s['_sent'] = se
t['durs'] = [s['dur'] for s in t['shots']]
json.dump(t, open(os.path.join(OUT, 'spec_t.json'), 'w'), ensure_ascii=False)
print(len(S), 'canh', sum(len(s['say'].split()) for s in S), 'tu', round(sum(t['durs']) / .9), 's')
