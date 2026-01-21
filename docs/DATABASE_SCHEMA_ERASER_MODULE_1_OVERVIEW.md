# 📊 Fitblog Database - Module 1: Tổng Quan (Eraser.io Format)

**Description:** Tổng quan đầy đủ 13 bảng dữ liệu và các relationship

```
section Authentication
  table auth_user {
    color: "#FFE5E5"
    icon: "🔐"
    
    id: int [primary key]
    username: varchar(150) [unique]
    email: varchar(254) [unique]
    password: varchar(128)
    is_active: boolean [default: true]
    is_staff: boolean
    is_superuser: boolean
    first_name: varchar(150)
    last_name: varchar(150)
    date_joined: datetime
    last_login: datetime
  }

section Products Core
  table products_product {
    color: "#E3F2FD"
    icon: "💪"
    
    id: int [primary key]
    name: varchar(200) [unique]
    slug: varchar(200) [unique, index]
    description: text
    price: decimal(10, 2)
    stock: int
    category_id: int [foreign key → products_productcategory]
    status: varchar(50) [choices: active, inactive, discontinued]
    nutrition_protein: float
    nutrition_carbs: float
    nutrition_fat: float
    nutrition_calories: float
    embedding_vector: vector [for recommendations]
    created_at: datetime [auto_now_add]
    updated_at: datetime [auto_now]
  }

  table products_productcategory {
    color: "#E3F2FD"
    icon: "📂"
    
    id: int [primary key]
    name: varchar(100) [unique]
    slug: varchar(100) [unique, index]
    description: text
    icon: varchar(200)
    icon_image: image
    color: varchar(7)
  }

  table products_productflavor {
    color: "#E3F2FD"
    icon: "🎯"
    
    id: int [primary key]
    product_id: int [foreign key → products_product]
    flavor_name: varchar(100)
    stock: int
  }

section Product Reviews & Recommendations
  table products_productreview {
    color: "#FFF9C4"
    icon: "⭐"
    
    id: int [primary key]
    product_id: int [foreign key → products_product, index]
    user_id: int [foreign key → auth_user, index]
    rating: int [1-5, index]
    title: varchar(200)
    content: text
    is_approved: boolean [default: false]
    created_at: datetime [index]
    updated_at: datetime
    
    constraint unique(user_id, product_id)
  }

  table products_recommendationlog {
    color: "#F3E5F5"
    icon: "🎁"
    
    id: int [primary key]
    user_id: int [foreign key → auth_user]
    product_id: int [foreign key → products_product]
    algorithm_type: varchar(50) [choices: content-based, collab-filtering, hybrid]
    predicted_rating: float
    created_at: datetime [index]
  }

section User Profile
  table products_userprofile {
    color: "#F1F8E9"
    icon: "👤"
    
    id: int [primary key]
    user_id: int [foreign key → auth_user, unique]
    age: int
    weight_kg: float
    height_cm: float
    goal: varchar(50) [choices: muscle-gain, fat-loss, strength, maintenance]
    activity_level: varchar(50) [choices: sedentary, light, moderate, very-active]
    gender: varchar(10) [choices: M, F, Other]
    session_id: varchar(100)
    bmi: float
    tdee: float
  }

  table products_passwordresettoken {
    color: "#F1F8E9"
    icon: "🔑"
    
    id: int [primary key]
    user_id: int [foreign key → auth_user]
    token: varchar(255) [unique, index]
    expires_at: datetime
    is_used: boolean [default: false]
    created_at: datetime
  }

section Blog
  table blog_category {
    color: "#FCE4EC"
    icon: "📚"
    
    id: int [primary key]
    name: varchar(200) [unique]
    slug: varchar(200) [unique, index]
    description: text
    icon: varchar(200)
    icon_image: image
  }

  table blog_post {
    color: "#FCE4EC"
    icon: "📝"
    
    id: int [primary key]
    title: varchar(300) [unique]
    slug: varchar(300) [unique, index]
    content: text
    category_id: int [foreign key → blog_category]
    excerpt: text
    status: varchar(50) [choices: draft, published]
    published_at: datetime [index]
    created_at: datetime [auto_now_add]
    updated_at: datetime [auto_now]
  }

section Chatbot
  table chatbot_chatmessage {
    color: "#E0F2F1"
    icon: "💬"
    
    id: int [primary key]
    user_message: text
    bot_response: text
    created_at: datetime [index]
  }

  table chatbot_ngrokconfiguration {
    color: "#E0F2F1"
    icon: "⚙️"
    
    id: int [primary key]
    ngrok_api_url: text
    is_active: boolean [default: true]
  }

section Logging
  table blog_systemlog {
    color: "#EEEEEE"
    icon: "📋"
    
    id: int [primary key]
    level: varchar(50) [choices: DEBUG, INFO, WARNING, ERROR, CRITICAL]
    message: text
    logger_name: varchar(255)
    created_at: datetime [index]
    extra_data: json
  }
```

## 🔗 Relationships

```
Relationships (Eraser format):

auth_user ||--o{ products_userprofile : "has"
auth_user ||--o{ products_productreview : "writes"
auth_user ||--o{ products_recommendationlog : "receives"
auth_user ||--o{ products_passwordresettoken : "requests"

products_productcategory ||--o{ products_product : "contains"
products_product ||--o{ products_productflavor : "has"
products_product ||--o{ products_productreview : "receives"
products_product ||--o{ products_recommendationlog : "recommended"

blog_category ||--o{ blog_post : "contains"
```

---

## 📋 Mô Tả Module

### **Module 1: Authentication & Profiles**
- **auth_user**: Django built-in authentication system
- **products_userprofile**: Fitness profile (age, weight, height, goals, BMI, TDEE)
- **products_passwordresettoken**: Token-based password reset mechanism

### **Module 2: Products & Reviews** ⭐
- **products_productcategory**: Product categories (Whey, Pre-workout, etc.)
- **products_product**: Main product information with nutrition data
- **products_productflavor**: Product variants and stock management
- **products_productreview**: User ratings (1-5 stars) - ★ Critical for Collaborative Filtering
- **products_recommendationlog**: Tracks recommendation algorithm outputs

### **Module 3: Blog & Chatbot**
- **blog_category**: Blog categories
- **blog_post**: Blog articles
- **chatbot_chatmessage**: Chat conversations
- **chatbot_ngrokconfiguration**: Ngrok webhook configuration

### **Module 4: Logging**
- **blog_systemlog**: System event logging

---

## 💾 Export Instructions

**For Eraser.io Import:**
1. Copy the tables section above
2. Go to Eraser.io → New Document
3. Click **"+" → "Add Table"** or paste content
4. Adjust colors and positioning
5. Export as **PNG** (300 DPI, white background)

**Colors Used:**
- 🔐 Auth: `#FFE5E5` (light red)
- 💪 Products: `#E3F2FD` (light blue)
- ⭐ Reviews: `#FFF9C4` (light yellow)
- 👤 Profiles: `#F1F8E9` (light green)
- 📚 Blog: `#FCE4EC` (light pink)
- 💬 Chatbot: `#E0F2F1` (light cyan)
- 📋 Logging: `#EEEEEE` (light gray)
