# ent/ – máy dựng video AVF (chuyển từ repo riêng avf-editor ngày 27/11/2026)

Repo riêng hết phút GitHub Actions → toàn bộ việc dựng (ent.yml, tin.yml) chạy ở đây (repo công khai, không giới hạn phút).
- Sửa code máy dựng ở `ent/editor/` của repo NÀY, không sửa avf-editor nữa.
- Không ghi địa chỉ n8n / Supabase / khoá vào code: dùng biến môi trường từ secrets (AVF_TTS_URL, AVF_KEY, TIN_CLIP_KEY, AVF_MEDIA_BASE).
- Kết quả: GitHub Release `ent-<job_id>` của repo này (n8n W73 lấy link).
