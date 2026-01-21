# 📊 Fitblog Database Schema - Eraser.io Format

## Database Diagram (Eraser.io/Draw.io Format)

```
// ====== AUTH MODULE (Django Built-in) ======

auth_user [icon: key, color: darkgray]{
  id int pk
  username string uk
  email string uk
  password string
  is_active boolean
  is_staff boolean
  date_joined datetime
  last_login datetime
}

// ====== PRODUCTS APP (8 Models) ======

product_category [icon: tag, color: orange]{
  id int pk
  name string uk
  slug string uk
  description text
  icon_image string
  color string "hex"
  created_at datetime
}

product [icon: package, color: yellow]{
  id int pk
  name string
  slug string uk
  category_id int fk "FK → product_category"
  supplement_type string "whey,isolate,casein,pre-workout,bcaa,vitamins,etc"
  description text
  short_description string
  image string
  price decimal
  discount_percent int
  serving_size string
  protein_per_serving float
  carbs_per_serving float
  fat_per_serving float
  calories_per_serving float
  ingredients text
  flavor string
  status string "active,inactive,outofstock"
  stock int
  tags string "comma-separated"
  suitable_for_goals string "muscle-gain,fat-loss,strength,etc"
  embedding_vector json
  seo_title string
  seo_description string
  created_at datetime
  updated_at datetime
}

product_flavor [icon: droplet, color: pink]{
  id int pk
  product_id int fk "FK → product"
  flavor_name string
  stock int
  created_at datetime
}

product_review [icon: star, color: lightyellow]{
  id int pk
  product_id int fk "FK → product"
  user_id int fk "FK → auth_user (nullable)"
  author_name string
  author_email string
  rating int "1-5 stars"
  title string
  content text
  is_verified_purchase boolean
  is_approved boolean
  helpful_count int
  created_at datetime
  updated_at datetime
  "UNIQUE (user_id, product_id) for Collaborative Filtering"
}

user_profile [icon: user, color: blue]{
  id int pk
  user_id int fk "FK → auth_user (OneToOne)"
  age int
  weight_kg float
  height_cm float
  gender string "male,female"
  bmi float
  tdee float
  goal string "muscle-gain,fat-loss,strength,endurance,general-health,athletic"
  activity_level string "sedentary,light,moderate,active,intense"
  session_id string uk "Legacy: session-based tracking"
  created_at datetime
  updated_at datetime
}

password_reset_token [icon: shield, color: red]{
  id int pk
  user_id int fk "FK → auth_user"
  token string uk
  created_at datetime
  expires_at datetime
  is_used boolean
}

recommendation_log [icon: activity, color: green]{
  id int pk
  user_id int fk "FK → auth_user (nullable)"
  product_id int fk "FK → product"
  algorithm_type string "content-based,collab-filtering,goal-based"
  similarity_score float
  predicted_rating float
  event_type string "view,click"
  score float
  created_at datetime
  "Track recommendation events for analytics"
}

system_log [icon: alert-triangle, color: red]{
  id int pk
  level string "DEBUG,INFO,WARNING,ERROR,CRITICAL"
  logger_name string
  message text
  traceback text
  created_at datetime
}

// ====== BLOG APP (5 Models) ======

blog_category [icon: folder, color: purple]{
  id int pk
  name string uk
  slug string uk
  description text
  created_at datetime
}

blog_post [icon: file-text, color: lavender]{
  id int pk
  category_id int fk "FK → blog_category"
  author_id int fk "FK → auth_user"
  title string
  slug string uk
  content text
  status string "draft,published,archived"
  excerpt text
  featured_image string
  views int
  likes int
  published_at datetime
  created_at datetime
  updated_at datetime
}

// ====== CHATBOT APP (2 Models) ======

ngrok_config [icon: cloud, color: gray]{
  id int pk
  name string
  ngrok_api_url string
  is_active boolean
  description text
  created_at datetime
  updated_at datetime
}

chat_message [icon: message-square, color: teal]{
  id int pk
  user_message text
  bot_response text
  created_at datetime
}

// ====== RELATIONSHIPS ======

// Products relationships
product_category.id < product.category_id
product.id < product_flavor.product_id
product.id < product_review.product_id
product.id < recommendation_log.product_id

// Users relationships
auth_user.id < user_profile.user_id
auth_user.id < product_review.user_id
auth_user.id < password_reset_token.user_id
auth_user.id < recommendation_log.user_id
auth_user.id < blog_post.author_id

// Blog relationships
blog_category.id < blog_post.category_id

// Recommendations
user_profile.id > recommendation_log
product.id > recommendation_log
```

---

## How to Use in Eraser.io

1. **Go to**: https://www.eraser.io/
2. **Create New Diagram**
3. **Select**: Database/ER Diagram
4. **Copy-Paste** the code above
5. **Customize colors & layout** as needed

---

## How to Use in Draw.io

1. **Go to**: https://app.diagrams.net/
2. **Create New Diagram**
3. **Use File → Import from** → Paste code as text
4. OR manually create boxes using **Database** template

---

## Database Statistics

| Module | Models | Tables | Purpose |
|--------|--------|--------|---------|
| **Auth** | - | 1 | Django built-in authentication |
| **Products** | 8 | 8 | Products, categories, reviews, recommendations |
| **Blog** | 2 | 2 | Blog posts & categories |
| **Chatbot** | 2 | 2 | Chatbot configuration & messages |
| **TOTAL** | 12 | 13 | Complete system |

---

## Key Features by Table

### 🔐 Auth & User Management
- **auth_user** - Django authentication
- **user_profile** - Fitness profile (BMI, TDEE, goals)
- **password_reset_token** - Secure password reset

### 📦 Product Management
- **product_category** - Supplement categories with emoji/colors
- **product** - Full product info + nutrition + embedding
- **product_flavor** - Variant tracking
- **product_review** - Reviews + ratings (for Collaborative Filtering)

### 🤖 Recommendations
- **recommendation_log** - Track all recommendation events
  - Algorithm type: content-based, collab-filtering, goal-based
  - Predicted ratings
  - Click/view tracking

### 📝 Blog & Content
- **blog_category** - Blog categories
- **blog_post** - Blog articles with author tracking

### 💬 Chatbot
- **ngrok_config** - Ngrok tunnel configuration
- **chat_message** - User-bot conversation history

### 📊 Analytics
- **system_log** - Application logs for debugging

---

## Collaborative Filtering Key

**ProductReview table is crucial for CF**:
- Unique constraint: (user_id, product_id)
- Each user rates each product max once
- Rating matrix: Users × Products
- Index on (user_id, rating) for fast CF queries

Example:
```
           P1(Whey)  P2(Pre)  P3(BCAA)  P4(Creatine)
User1        5        3        -         4
User2        4        -        5         2
User3        -        2        4         5
User4        3        5        -         -

(-) = not rated (NULL)
```

---

## Import to Draw.io

**Option 1: Direct Paste**
1. Open draw.io
2. File → Import from → Paste (Ctrl+V)
3. Select "Mermaid"
4. Paste the ERD section

**Option 2: Create Manually**
1. Insert → More Shapes → Database
2. Drag tables to canvas
3. Connect with lines
4. Add labels

**Option 3: Use SQLAlchemy**
```bash
# Generate from models.py
pip install sadisplay
python manage.py shell
>>> import sadisplay
>>> import sys
>>> from products.models import *
>>> from blog.models import *
>>> graph = sadisplay.describe([Product, ProductCategory, ProductReview, UserProfile, BlogPost, BlogCategory])
>>> print(sadisplay.dot.dot_graph(graph))
```

---

## Export from Draw.io

1. **Save as image**: File → Export as → PNG/SVG
2. **Save as XML**: File → Export as → XML
3. **Share link**: File → Share → Get shareable link
4. **Embed in docs**: Copy embed code

---

## Notes
- ✅ All relationships are included
- ✅ Primary keys (pk) marked
- ✅ Foreign keys (fk) labeled
- ✅ Unique constraints (uk) shown
- ✅ Color-coded by module
- ✅ Icons for visual clarity
- ✅ Ready for Eraser.io, Draw.io, Lucidchart
