#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo script: Tạo fake reviews từ các users khác nhau
để test Collaborative Filtering recommendation algorithm

Usage:
    python manage.py shell < create_demo_reviews.py
"""

from django.contrib.auth.models import User
from products.models import Product, ProductReview
import random

print("=" * 70)
print("📊 CREATING DEMO REVIEWS FOR COLLABORATIVE FILTERING TEST")
print("=" * 70)

# Lấy các users
users = list(User.objects.all()[:5])  # Lấy 5 users đầu tiên
products = list(Product.objects.all()[:8])  # Lấy 8 sản phẩm đầu tiên

if not users or not products:
    print("❌ Không đủ users hoặc products. Vui lòng tạo trước!")
    exit()

print(f"\n👥 Users: {len(users)}")
for u in users:
    print(f"   - {u.username} (id={u.id})")

print(f"\n📦 Products: {len(products)}")
for p in products:
    print(f"   - {p.name} (id={p.id})")

# Tạo reviews ngẫu nhiên
print(f"\n🔄 Tạo reviews...")
reviews_created = 0
skipped = 0

for user in users:
    # Mỗi user review 4-6 sản phẩm
    sampled_products = random.sample(products, random.randint(4, 6))
    
    for product in sampled_products:
        rating = random.randint(3, 5)  # Rating từ 3-5 sao
        
        # Kiểm tra đã có review này chưa
        if ProductReview.objects.filter(user=user, product=product).exists():
            skipped += 1
            continue
        
        review = ProductReview.objects.create(
            user=user,
            product=product,
            rating=rating,
            title=f"{'Rất' if rating >= 4 else 'Khá'} tốt!",
            content=f"Sản phẩm {product.name} {'rất' if rating >= 4 else 'khá'} tốt. Rating: {rating}/5",
            author_name=user.username,
            author_email=user.email or f"{user.username}@example.com",
            is_verified_purchase=True,
            is_approved=True
        )
        reviews_created += 1
        print(f"   ✅ {user.username} → {product.name}: {rating}⭐")

print(f"\n📈 Results:")
print(f"   ✅ Created: {reviews_created} reviews")
print(f"   ⏭️  Skipped: {skipped} (already exists)")

# Hiển thị user-item matrix
print(f"\n📊 User-Item Rating Matrix:")
print(f"   {'User':<15} | Product Reviews")
print(f"   {'-' * 60}")

for user in users:
    reviews = ProductReview.objects.filter(user=user).select_related('product')
    rating_str = ", ".join([f"{r.product.name}({r.rating}⭐)" for r in reviews])
    print(f"   {user.username:<15} | {rating_str}")

# Ví dụ: Tìm users tương tự
print(f"\n🤝 Tìm Users Tương Tự (đánh giá cùng products):")
from django.db.models import Q, Count

# SQL query để tìm pairs of users đánh giá cùng sản phẩm
user_pairs = ProductReview.objects.values(
    'user_id'
).annotate(
    product_count=Count('product')
).filter(
    product_count__gte=2
)

print(f"   Total user reviews: {ProductReview.objects.filter(is_approved=True).count()}")

# Lấy products được reviewed nhiều nhất
print(f"\n🔥 Top Products (Most Reviews):")
top_products = Product.objects.annotate(
    review_count=Count('reviews', filter=Q(reviews__is_approved=True))
).filter(
    review_count__gt=0
).order_by('-review_count')[:5]

for prod in top_products:
    reviews = ProductReview.objects.filter(product=prod, is_approved=True)
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    print(f"   {prod.name}: {reviews.count()} reviews, avg {avg_rating:.1f}⭐")

print(f"\n✅ Demo Complete!")
print(f"=" * 70)
