# avf-hoathinh

Máy dựng hoạt hình 2D vẽ bằng code (Python → SVG → rsvg-convert → ffmpeg) cho các kênh kể chuyện.

- `editor/ksc_svg.py` – khung dựng (bố cục 9:16, phụ đề, giọng, âm thanh).
- `editor/ksc_chars.py` – thư viện nhân vật (đơn vị D, 6 biểu cảm, bảng tên).
- `editor/vh_svg.py` – bộ cảnh văn học (làng quê, gia đình, sơ đồ quan hệ).
- `.github/workflows/dung.yml` – dựng theo lệnh; địa chỉ dịch vụ và khoá nằm trong GitHub Secrets.
