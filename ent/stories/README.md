# Chuyện Đêm – kịch bản từng series

Mỗi truyện một file `<pack>.json` (pack = bộ cảnh `ent/editor/dem_<pack>.py`):
`{pack, title, source, parts: [ {job, speed, provider, voice_code, hook, cover, kicker, pack, text, scenes}, ... ]}`.
Mỗi phần chính là body gửi W110. Tác vụ hằng ngày đọc file này để biết tập tiếp theo.
Quy tắc viết: skill `chuyen-dem-truyen-ma` (không `{...}`, chỉ `[nghỉ x]`, ít dấu phẩy, scenes = cụm đầu câu nguyên văn).
