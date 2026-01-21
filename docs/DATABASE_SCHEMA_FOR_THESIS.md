# 📊 Fitblog Database Schema - Tối Ưu Cho Luận Văn

## 🎯 Chiến Lược Trình Bày

### ❌ **Không Nên** (ảnh to, khó nhìn)
- Đưa toàn bộ ảnh ERD vào luận văn
- Ảnh to làm tăng dung lượng PDF
- Khó đọc trên trang giấy A4

### ✅ **Nên Làm** (tách nhỏ, cô đọng)
1. **Chia thành 3 ảnh nhỏ** (Module riêng)
2. **Viết mô tả từng module** (1-2 paragraph)
3. **Sử dụng bảng so sánh** thay vì chi tiết
4. **Đưa SQL DDL** vào Appendix

---

## 📋 Cấu Trúc Đề Xuất Cho Luận Văn

### **I. Kiến Trúc Database (Trang 1-2)**

#### 1.1 Tổng Quan (Đưa ảnh này)
```
[ERD Đầy đủ nhưng nhỏ hơn]
- Hiển thị tất cả 13 tables
- Tất cả relationships
- Export từ Eraser với chất lượng cao
- Kích thước: 15cm x 20cm max
```

#### 1.2 Mô Tả Module
Dùng bảng thay vì text dài:

| Module | Tables | Mục Đích |
|--------|--------|---------|
| **Auth** | 1 | Xác thực Django |
| **Products** | 7 | Quản lý sản phẩm + recommendations |
| **Blog** | 2 | Quản lý bài viết |
| **Chatbot** | 2 | Chatbot AI |
| **Logs** | 1 | Ghi chép hệ thống |

---

### **II. Chi Tiết Từng Module (Trang 3-5)**

#### **2.1 Module Products (7 Tables) - Ảnh riêng**
```
[ERD nhỏ - chỉ tables Products]
- product_category
- product
- product_flavor
- product_review (★ Quan trọng cho CF)
- user_profile
- password_reset_token
- recommendation_log
```

**Mô tả:**
- ProductCategory: Phân loại supplement (Whey, Pre-workout, Vitamins)
- Product: Sản phẩm chính với thông tin dinh dưỡng + embedding vector
- ProductReview: Đánh giá sản phẩm - ★ Dùng để xây dựng user-item matrix cho Collaborative Filtering
- Recommendation_log: Ghi log mỗi recommendation

#### **2.2 Module Users/Auth (2 Tables)**
```
[ERD nhỏ - User relationships]
- auth_user
- user_profile
- password_reset_token
```

**Mô tả:**
- auth_user: Django built-in, quản lý login
- UserProfile: Lưu fitness goals (BMI, TDEE, mục tiêu)
- PasswordResetToken: Xác minh đặt lại mật khẩu

#### **2.3 Module Blog + Chatbot (4 Tables)**
```
[ERD nhỏ - Blog & Chatbot]
- blog_category
- blog_post
- ngrok_config
- chat_message
```

---

### **III. Tầm Quan Trọng Của ProductReview (Trang 5-6)**

#### **3.1 User-Item Matrix Cho Collaborative Filtering**
```
Bảng so sánh:

           Product1  Product2  Product3  Product4
User1        5        3        -         4
User2        4        -        5         2
User3        -        2        4         5
User4        3        5        -         -

(-) = chưa đánh giá
Dữ liệu từ: products_productreview table
```

**Mô tả:**
```
Collaborative Filtering sử dụng đánh giá từ table ProductReview:
- Mỗi user chỉ có 1 rating cho 1 product (UNIQUE constraint)
- Rating từ 1-5 sao
- Được phê duyệt (is_approved=True) trước khi dùng
- Index (user_id, product_id) để tìm nhanh
```

---

### **IV. Schema SQL (Appendix - Trang 20+)**

#### **Chỉ giữ lại phần quan trọng:**

```sql
-- ====== PRODUCT REVIEW (Cho Collaborative Filtering) ======
CREATE TABLE products_productreview (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    user_id INTEGER,
    rating INTEGER (1-5),  -- ★ Dùng cho CF algorithm
    title VARCHAR(200),
    content TEXT,
    is_approved BOOLEAN,
    created_at DATETIME,
    FOREIGN KEY (product_id) REFERENCES products_product(id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    UNIQUE (user_id, product_id)  -- ★ Mỗi user 1 rating/product
);

-- ====== USER PROFILE (Fitness Data) ======
CREATE TABLE products_userprofile (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,
    age INTEGER,
    weight_kg FLOAT,
    height_cm FLOAT,
    goal VARCHAR(50),  -- muscle-gain, fat-loss, strength, etc
    activity_level VARCHAR(50),
    bmi FLOAT,
    tdee FLOAT
);

-- ====== RECOMMENDATION LOG (Tracking) ======
CREATE TABLE products_recommendationlog (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER,
    algorithm_type VARCHAR(50),  -- content-based, collab-filtering
    predicted_rating FLOAT,
    created_at DATETIME
);
```

---

## 📐 Kích Thước Ảnh Đề Xuất

| Ảnh | Kích Thước | Mục Đích |
|-----|-----------|---------|
| ERD Đầy Đủ | 12cm × 16cm | Trang 3-4 (Tổng quan) |
| Products Module | 10cm × 14cm | Trang 5-6 (Chi tiết) |
| Users Module | 8cm × 10cm | Trang 6-7 (Compact) |
| User-Item Matrix | Bảng ASCII | Trang 7-8 (Dễ hiểu) |

---

## 📝 Template Đoạn Văn Gợi Ý

### **Heading 1: Kiến Trúc Cơ Sở Dữ Liệu**

"Hệ thống Fitblog sử dụng **13 bảng dữ liệu** được tổ chức thành **5 module chính**:
- Module Auth (1 bảng): Xác thực người dùng
- Module Products (7 bảng): Quản lý sản phẩm & đánh giá
- Module Users (3 bảng): Hồ sơ fitness & reset mật khẩu
- Module Blog (2 bảng): Quản lý bài viết
- Module Chatbot (2 bảng): Cấu hình chatbot

*[Đưa ảnh ERD đầy đủ ở đây]*"

### **Heading 2: Module Sản Phẩm**

"Module Products là trung tâm của hệ thống, bao gồm **7 bảng**:

1. **ProductCategory**: Phân loại supplement (Whey, Pre-workout, Vitamins, Fat Burner)
2. **Product**: Thông tin sản phẩm (giá, dinh dưỡng, embedding vector)
3. **ProductFlavor**: Variant sản phẩm (Chocolate, Vanilla)
4. **ProductReview**: Đánh giá của người dùng (★ Quan trọng)
5. **UserProfile**: Hồ sơ fitness người dùng
6. **RecommendationLog**: Ghi chép các recommendation
7. **PasswordResetToken**: Token reset mật khẩu

*[Đưa ảnh Products Module ở đây]*"

### **Heading 3: Collaborative Filtering - User-Item Matrix**

"Thuật toán Collaborative Filtering cần một **user-item rating matrix**. 
Dữ liệu được lấy từ table **ProductReview**:

*[Đưa bảng User-Item Matrix ở đây]*

Các ưu điểm của thiết kế này:
- ✅ Mỗi user chỉ có 1 rating cho 1 product (UNIQUE constraint)
- ✅ Dễ truy vấn nhanh với INDEX (user_id, product_id)
- ✅ Chỉ dùng review đã phê duyệt (is_approved=True)
- ✅ Theo dõi hành động người dùng (click, purchase)"

---

## 🎨 Export Ảnh Từ Eraser Tối Ưu

### **Cách export cho luận văn:**

1. **Eraser.io** → Diagram
2. **File** → **Export as** → **PNG**
3. **Cấu hình:**
   - ✅ High Quality (300 DPI)
   - ✅ Light background (trắng)
   - ✅ Không watermark
   - ✅ Size: 2000×2800px (sẽ resize còn 12cm)

4. **Tối ưu ảnh:**
   ```bash
   # Dùng ImageMagick để nén
   convert diagram.png -quality 85 -resize 2000x2800 diagram-optimized.png
   # Kích thước sẽ ~200-300KB (OK cho PDF)
   ```

---

## 📊 Bảng Tóm Tắt Cho Luận Văn

```markdown
| Table | Mục Đích | Trường Quan Trọng | Index Chính |
|-------|---------|-----------------|------------|
| auth_user | Xác thực | username, email | (username), (email) |
| user_profile | Hồ sơ fitness | age, weight, height, goal, bmi, tdee | (user_id), (goal) |
| product_category | Phân loại | name, slug, icon, color | (slug) |
| product | Sản phẩm | name, price, nutrition info, embedding_vector | (slug), (status), (category) |
| product_flavor | Variant | flavor_name, stock | (product_id) |
| product_review | Đánh giá ★ | rating, is_approved | (product_id, rating), **(user_id, product_id)** |
| recommendation_log | Ghi chép | algorithm_type, predicted_rating | (user_id, created_at) |
| password_reset_token | Reset pwd | token, expires_at, is_used | (token), (user_id) |
| blog_category | Blog | name, slug | (slug) |
| blog_post | Bài viết | title, status, published_at | (slug), (status) |
| chat_message | Chatbot | user_message, bot_response | (created_at) |
| ngrok_config | Config | ngrok_api_url, is_active | - |
| system_log | Log | level, message | (level), (created_at) |
```

---

## ✅ Checklist Trình Bày Cho Luận Văn

- [ ] **Trang 1**: Mô tả tổng quan + bảng module
- [ ] **Trang 2**: Ảnh ERD đầy đủ (12×16cm)
- [ ] **Trang 3**: Ảnh Products Module (10×14cm)
- [ ] **Trang 4**: Bảng User-Item Matrix (ASCII)
- [ ] **Trang 5**: Bảng tóm tắt tất cả tables
- [ ] **Appendix**: SQL DDL đầy đủ
- [ ] **Total**: ~3-4 trang + Appendix

---

## 🎯 Kết Luận

✅ **NÊN LÀM:**
1. Tách ảnh thành 3 phần (Tổng quan, Products, Users)
2. Dùng bảng so sánh thay vì text dài
3. Highlight ProductReview (quan trọng cho CF)
4. Giữ SQL DDL ở Appendix

❌ **KHÔNG NÊN:**
1. Đưa toàn bộ ảnh to vào luận văn
2. Viết đoạn văn dài mô tả từng field
3. Quên nhấn mạnh tầm quan trọng của ProductReview
4. Không giải thích các index & constraint

**Kết quả:** Luận văn sẽ gọn gàng, chuyên nghiệp, dễ đọc! 📚
