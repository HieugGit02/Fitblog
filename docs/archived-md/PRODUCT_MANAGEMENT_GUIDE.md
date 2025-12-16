# 📦 Hướng Dẫn Quản Lý Sản Phẩm - Fitblog Shop

## 🎯 Tổng Quan

Fitblog Shop cung cấp một hệ thống quản lý sản phẩm supplement hoàn chỉnh. Bạn có thể dễ dàng thêm, sửa, xóa sản phẩm thông qua:
- **Django Admin Panel** (Quản trị viên)
- **Frontend Web Interface** (Hiển thị khách hàng)

---

## 🔐 Truy Cập Django Admin

### 1. Đăng Nhập Admin Panel
```
URL: http://localhost:8001/admin/
Username: (admin username)
Password: (admin password)
```

### 2. Menu Admin
Sau khi đăng nhập, bạn sẽ thấy các mục:
- **Products** - Quản lý sản phẩm
- **Product Categories** - Quản lý danh mục
- **Product Reviews** - Quản lý đánh giá khách hàng

---

## 📂 Tạo Danh Mục Sản Phẩm (Categories)

Trước khi thêm sản phẩm, bạn cần tạo danh mục (ví dụ: Protein, Vitamin, BCAA, etc.)

### Bước 1: Vào Product Categories

1. Admin Panel → **Product Categories**
2. Click **"Add Product Category"**

### Bước 2: Điền Thông Tin Danh Mục

| Trường | Ví Dụ | Hướng Dẫn |
|--------|-------|---------|
| **Name** | Whey Protein | Tên danh mục |
| **Description** | Protein từ whey... | Mô tả chi tiết |
| **Icon** | 💪 | Emoji (copy từ 😀 emojidb.org) |
| **Color** | #FF6B6B | Màu hex (https://htmlcolorcodes.com) |

**Ví dụ danh mục:**
```
1. Protein (💪 màu xanh: #4CAF50)
2. Vitamin (🏥 màu cam: #FF9800)
3. BCAA & Amino (⚡ màu vàng: #FFC107)
4. Pre-Workout (🔥 màu đỏ: #F44336)
5. Weight Gainer (📈 màu tím: #9C27B0)
```

### Bước 3: Lưu

- Slug sẽ tự tạo từ Name
- Click **"Save"** để lưu danh mục

---

## 💊 Thêm Sản Phẩm

### Bước 1: Vào Product Admin

1. Admin Panel → **Products**
2. Click **"Add Product"** (nút màu xanh ở góc trên phải)

### Bước 2: Điền Thông Tin Cơ Bản

#### 📦 Thông Tin Cơ Bản (Required)
```
Name:           Whey Protein Concentrate 80%
Slug:           whey-protein-concentrate-80 (tự tạo)
Category:       Protein (chọn từ dropdown)
Supplement Type: protein (chọn: protein, vitamin, bcaa, pre-workout, weight-gainer, etc.)
Status:         active (Có sẵn / Không có sẵn / Ngừng bán)
```

#### 💬 Mô Tả & Hình Ảnh
```
Short Description: Whey protein chất lượng cao, hỗ trợ xây dựng cơ bắp
Description:       [Nhập mô tả chi tiết - có thể dài]
Image:            [Upload hình ảnh sản phẩm] (nếu có)
```

#### 💰 Giá & Tồn Kho
```
Price:           450000 (giá gốc, tính bằng VND)
Discount %:      10 (nếu có giảm giá, để trống = không giảm)
Stock:           25 (số lượng tồn kho)
```

**Công thức giá:**
- Giá cuối = Price × (1 - Discount/100)
- Ví dụ: 450000 × (1 - 10/100) = 405000 VND

#### 🥗 Dinh Dưỡng (Mỗi khẩu phần)
```
Serving Size:       30g (kích cỡ 1 khẩu phần)
Protein:           25g
Carbs:             2g
Fat:               1.5g
Calories:          110 kcal
```
*(Nếu không biết, để trống - hiển thị "—" trên web)*

#### 🍫 Thành Phần
```
Flavor:            Chocolate, Vanilla, Strawberry
Ingredients:       Whey protein concentrate, cocoa powder, sucralose...
```

#### 🎯 Tags & Mục Tiêu (Cho hệ thống gợi ý)

**Tags** (tách bằng dấu phẩy):
```
muscle-gain, lean, vegan, natural
```

**Suitable For Goals** (mục tiêu người dùng):
```
muscle-gain, strength, recovery
```

### Bước 3: Tùy chọn Nâng Cao

#### 🔍 SEO (Có thể bỏ qua)
```
SEO Title:       Whey Protein Concentrate 80% - Xây dựng cơ bắp
SEO Description: Whey protein chất lượng cao, giá rẻ, hỗ trợ tăng cơ...
```

### Bước 4: Lưu

- Click **"Save"** (lưu)
- Hoặc **"Save and Add Another"** (lưu và thêm tiếp)

---

## ✏️ Sửa Sản Phẩm

### Bước 1: Tìm Sản Phẩm
1. Admin → Products
2. Tìm kiếm hoặc lọc sản phẩm
3. Click vào tên sản phẩm

### Bước 2: Chỉnh Sửa
- Sửa các trường muốn thay đổi
- Click **"Save"**

### Bước 3: Cập Nhật Trạng Thái
Có thể thay đổi trạng thái sản phẩm ngay từ danh sách:
1. Chọn sản phẩm (checkbox)
2. Chọn action: "✅ Đánh dấu sản phẩm có sẵn" hoặc "❌ Đánh dấu sản phẩm không có sẵn"
3. Click **"Go"**

---

## 🗑️ Xóa Sản Phẩm

### Cách 1: Xóa Từ Danh Sách
1. Admin → Products
2. Chọn checkbox sản phẩm cần xóa
3. Chọn **"Delete Selected Products"** từ Action dropdown
4. Click **"Go"**
5. Confirm xóa

### Cách 2: Xóa Từ Chi Tiết
1. Mở sản phẩm
2. Click **"Delete"** (nút đỏ ở dưới cùng)
3. Confirm xóa

---

## 📊 Hiển Thị Sản Phẩm Trên Web

### 1. Trang Danh Sách Sản Phẩm
```
URL: http://localhost:8001/products/
```

**Tính năng:**
- 🔄 Xem tất cả sản phẩm
- 📂 Lọc theo danh mục (hiển thị ở dầu trang)
- 🔎 Tìm kiếm theo tên
- 💊 Lọc theo loại supplement
- 💲 Sắp xếp theo giá, đánh giá, ngày
- 📄 Phân trang (12 sản phẩm/trang)

### 2. Trang Chi Tiết Sản Phẩm
```
URL: http://localhost:8001/products/{product-slug}/
```

Ví dụ:
- http://localhost:8001/products/whey-protein-isolate/
- http://localhost:8001/products/vitamin-d3-5000-iu/

**Hiển thị:**
- 🖼️ Hình ảnh sản phẩm
- ⭐ Đánh giá trung bình
- 💰 Giá & Giảm giá
- 🥗 Thông tin dinh dưỡng
- 📝 Mô tả chi tiết
- 💬 Đánh giá khách hàng
- 🔗 Sản phẩm tương tự

---

## 👥 Quản Lý Đánh Giá (Reviews)

### Xem Đánh Giá
1. Admin → Product Reviews
2. Xem danh sách đánh giá từ khách hàng

### Duyệt Đánh Giá
1. Chọn đánh giá cần duyệt
2. Action: "✅ Phê duyệt review"
3. Click **"Go"**

**Lưu ý:** Chỉ các review được duyệt (✅ Duyệt) mới hiển thị trên web

### Từ Chối Đánh Giá
1. Chọn đánh giá cần từ chối
2. Action: "❌ Đã từ chối review"
3. Click **"Go"**

---

## 📋 Checklist Thêm Sản Phẩm

```
☐ Danh mục đã tạo (nếu là danh mục mới)
☐ Tên sản phẩm (bắt buộc)
☐ Danh mục (bắt buộc)
☐ Loại supplement (bắt buộc)
☐ Giá gốc (bắt buộc)
☐ Tồn kho (bắt buộc)
☐ Trạng thái = Active (bắt buộc)
☐ Hình ảnh (nên có)
☐ Mô tả (nên có)
☐ Dinh dưỡng (nếu sản phẩm có)
☐ Thành phần/Hương vị (nếu có)
```

---

## 🔧 Troubleshooting

### Vấn đề: Sản phẩm không hiển thị trên web
**Giải pháp:**
- ✅ Kiểm tra Status = "active"
- ✅ Refresh trang web
- ✅ Kiểm tra category tồn tại

### Vấn đề: Hình ảnh không hiển thị
**Giải pháp:**
- ✅ Kiểm tra định dạng: JPG, PNG, WebP
- ✅ Kích thước < 5MB
- ✅ Upload lại hình ảnh

### Vấn đề: Giá không chính xác
**Giải pháp:**
- ✅ Kiểm tra Public Price = giá gốc
- ✅ Kiểm tra Discount % (nếu có)
- ✅ Công thức: Giá cuối = Price × (1 - Discount/100)

---

## 📞 Hỗ Trợ

Nếu có vấn đề, hãy liên hệ:
- 📧 Email: support@fitblog.com
- 💬 Chat: Messenger (Fitblog)
- 📞 Phone: 0xxx-xxx-xxx

---

**Last Updated:** December 13, 2025
**Version:** 1.0
