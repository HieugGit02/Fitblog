# 🚀 Railway Scheduled Task - Cleanup Expired Sessions

## 📋 Mục Đích
Tự động xóa expired sessions và UserProfiles cũ hàng ngày trên Railway để tiết kiệm dung lượng database.

## ✅ Cách 1: Dùng Railway Dashboard (Khuyến nghị)

1. **Truy cập Railway Dashboard:**
   - Vào https://railway.app
   - Chọn project `Fitblog`
   - Vào tab `Settings`

2. **Tạo Scheduled Job:**
   - Chọn `Crons` hoặc `Scheduled Jobs`
   - Click `+ New Cron Job`
   - **Name:** `cleanup-expired-sessions`
   - **Schedule:** `0 0 * * *` (mỗi ngày lúc 0:00 UTC = 7:00 sáng Việt Nam)
   - **Command:** `python manage.py cleanup_expired_sessions`
   - Click `Deploy`

## ✅ Cách 2: Dùng File Config (Alternative)

Railway hỗ trợ `railway.toml` hoặc `railway.json`:

**Đã tạo sẵn: `railway.toml` và `railway.json` trong project**

Push code lên, Railway sẽ tự động đọc config và tạo scheduled task.

## 🔍 Kiểm Tra Hoạt Động

1. Vào Railway Dashboard → Logs
2. Tìm dòng: `✓ Đã xóa X expired sessions + Y orphan profiles`
3. Nếu thấy = cleanup chạy thành công ✅

## 🧹 Xóa Thủ Công (Nếu cần ngay)

```bash
# SSH vào Railway (nếu có access)
railway run python manage.py cleanup_expired_sessions

# Hoặc chạy local:
python manage.py cleanup_expired_sessions
```

## ⚠️ Lưu Ý
- Sessions expire sau **14 ngày** (SESSION_COOKIE_AGE trong settings.py)
- Cleanup chạy hàng ngày lúc **0:00 UTC** (7:00 sáng Việt Nam)
- Nếu vô tình xóa nhầm, có thể restore từ database backups
