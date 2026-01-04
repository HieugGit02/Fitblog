# 📊 Diagram: UserProfile - Trước vs Sau

## ❌ TRƯỚC (Có Vấn Đề)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Đăng Kí                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
   Signal #1                   Signal #2/Middleware
   create_user_profile         create_session_profile
   │                           │
   ▼                           ▼
┌─────────────────────┐  ┌─────────────────────┐
│ UserProfile #1      │  │ UserProfile #2      │
├─────────────────────┤  ├─────────────────────┤
│ • user_id = 1       │  │ • user_id = NULL    │
│ • session_id = NULL │  │ • session_id = abc  │
│ • goal = None       │  │ • goal = None       │
│ • age = NULL        │  │ • age = NULL        │
└─────────────────────┘  └─────────────────────┘
      ✅ Linked                 ❌ Orphaned
      với User                  (không user)

RESULT: Admin hiển thị 2 profiles cho 1 user ❌
```

---

## ✅ SAU (Đã Fix)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Đăng Kí                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              Signal: create_or_update_user_profile
              (dùng get_or_create)
              │
              ▼
      ┌───────────────────────┐
      │ UserProfile tồn tại?  │
      └───┬───────────────────┘
          │
    ┌─────┴─────┐
    NO          YES
    │           │
    ▼           ▼
  Tạo         Skip
  mới         (không duplicate)

         ▼
   ┌─────────────────────┐
   │ UserProfile #1      │
   ├─────────────────────┤
   │ • user_id = 1       │
   │ • session_id = NULL │
   │ • goal = general    │
   │ • age = NULL        │
   └─────────────────────┘
        ✅ 1 Profile
        ✅ Linked với User
        ✅ Không orphaned

RESULT: Admin hiển thị 1 profile cho 1 user ✅
```

---

## 📈 Data Comparison

### ❌ Cũ (Trước Fix)
```
Total Users:        4
Total Profiles:     9 (DUPLICATE!)
├─ With User:       4 ✅
└─ Orphaned:        5 ❌

Issue: 4 users có 9 profiles!
```

### ✅ Mới (Sau Fix)
```
Total Users:        4
Total Profiles:     4 (Perfect 1:1!)
├─ With User:       4 ✅
└─ Orphaned:        0 ✅

Result: 4 users có 4 profiles!
```

---

## 🔄 Process Flow: New User Registration

### ❌ Cũ (Lỗi)
```
1. User clicks "Register" 
   └─> POST /auth/register/
       └─> form.save() [creates User]
           ├─> Signal: create_user_profile() 
           │   └─> Creates Profile #1 (user_id=1, session_id=NULL)
           ├─> Signal: save_user_profile()
           │   └─> Updates Profile #1
           └─> Middleware: on_page_load()
               └─> Creates Profile #2 (user_id=NULL, session_id=xyz) ❌

2. Admin check /admin/products/userprofile/
   └─> Sees: 2 profiles per user ❌ (WRONG!)
```

### ✅ Mới (Fix)
```
1. User clicks "Register" 
   └─> POST /auth/register/
       └─> form.save() [creates User]
           └─> Signal: create_or_update_user_profile() 
               └─> get_or_create(user=1)
                   └─> Creates Profile #1 (user_id=1, session_id=NULL) ✅
                   └─> No duplicates even if signal runs 2x

2. Admin check /admin/products/userprofile/
   └─> Sees: 1 profile per user ✅ (CORRECT!)
```

---

## 🛠️ Fix Applied

| Component | Change | Impact |
|-----------|--------|--------|
| **signals.py** | ✅ `objects.create()` → `get_or_create()` | No more duplicate profiles |
| **DB Cleanup** | ✅ Deleted 5 orphaned profiles | Clean data |
| **Management Cmd** | ✅ Added cleanup command | Regular monitoring |
| **Middleware** | ✓ Disabled (deprecated) | No session-based creation |

---

## ✔️ Verification

```python
from django.contrib.auth.models import User
from products.models import UserProfile

# Before cleanup
users = User.objects.count()          # 4
profiles = UserProfile.objects.count() # 9 ❌

# After cleanup
users = User.objects.count()          # 4
profiles = UserProfile.objects.count() # 4 ✅

# Check each user has exactly 1 profile
for user in User.objects.all():
    profile_count = UserProfile.objects.filter(user=user).count()
    assert profile_count == 1  # ✅ Pass
```
