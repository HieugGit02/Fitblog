#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create 12 test products to demonstrate recommendation algorithm

Recommendation Algorithm:
1. Content-based: Same category, supplement type, or suitable goals
2. Personalized: Based on user profile goal
3. Scoring: Sorted by review count + average rating

Product Test Data:
- 3 Whey Protein products (muscle-gain focus)
- 3 Pre-workout products (strength focus)
- 3 Fat-loss products (fat-loss focus)
- 3 Vitamins products (general-health focus)

Usage:
    python manage.py shell < create_test_products.py
    OR
    python create_test_products.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitblog_config.settings')
django.setup()

from products.models import ProductCategory, Product
from django.db.models import Q

# ============================================================================
# TEST DATA
# ============================================================================

TEST_PRODUCTS = [
    # ===== WHEY PROTEIN (Muscle Gain) =====
    {
        'name': 'Gold Standard Whey Protein',
        'slug': 'gold-standard-whey-protein',
        'category_name': 'Whey Protein',
        'supplement_type': 'Whey Protein',
        'price': 29.99,
        'suitable_for_goals': 'muscle-gain,strength,athletic',
        'description': 'Premium whey protein isolate with 24g protein per serving. Supports muscle growth and recovery.',
        'short_description': '24g protein per serving | Fast absorption',
    },
    {
        'name': 'MuscleTech Nitro-Tech',
        'slug': 'muscletech-nitro-tech',
        'category_name': 'Whey Protein',
        'supplement_type': 'Whey Protein',
        'price': 39.99,
        'suitable_for_goals': 'muscle-gain,strength,athletic',
        'description': 'Advanced whey protein blend with creatine and amino acids for maximum muscle growth.',
        'short_description': '30g protein + Creatine + BCAAs',
    },
    {
        'name': 'Optimum Nutrition Whey',
        'slug': 'optimum-nutrition-whey',
        'category_name': 'Whey Protein',
        'supplement_type': 'Whey Protein',
        'price': 25.99,
        'suitable_for_goals': 'muscle-gain,strength,general-health',
        'description': 'Classic ON whey protein trusted by athletes worldwide for muscle building.',
        'short_description': '21g protein | Most popular',
    },
    
    # ===== PRE-WORKOUT (Strength) =====
    {
        'name': 'C4 Original Pre-Workout',
        'slug': 'c4-original-pre-workout',
        'category_name': 'Pre-workout',
        'supplement_type': 'Pre-workout',
        'price': 34.99,
        'suitable_for_goals': 'strength,athletic,muscle-gain',
        'description': 'High-energy pre-workout with caffeine and beta-alanine for intense training.',
        'short_description': '200mg caffeine | Explosive energy',
    },
    {
        'name': 'Mr. Hyde Pre-Workout',
        'slug': 'mr-hyde-pre-workout',
        'category_name': 'Pre-workout',
        'supplement_type': 'Pre-workout',
        'price': 44.99,
        'suitable_for_goals': 'strength,athletic,muscle-gain',
        'description': 'Extreme pre-workout formula designed for maximum pump and strength gains.',
        'short_description': '300mg caffeine | Most powerful',
    },
    {
        'name': 'BCAA + Energy Pre-Workout',
        'slug': 'bcaa-energy-pre-workout',
        'category_name': 'Pre-workout',
        'supplement_type': 'Pre-workout',
        'price': 24.99,
        'suitable_for_goals': 'strength,endurance,general-health',
        'description': 'Beginner-friendly pre-workout with BCAAs and moderate caffeine.',
        'short_description': '150mg caffeine | BCAA blend',
    },
    
    # ===== FAT LOSS (Weight Loss) =====
    {
        'name': 'Leanbean Fat Burner',
        'slug': 'leanbean-fat-burner',
        'category_name': 'Fat Burner',
        'supplement_type': 'Fat Burner',
        'price': 59.99,
        'suitable_for_goals': 'fat-loss,general-health',
        'description': 'Premium fat burner specifically formulated for women to support weight loss.',
        'short_description': 'Women-focused | Appetite suppressor',
    },
    {
        'name': 'Instant Knockout Fat Burner',
        'slug': 'instant-knockout-fat-burner',
        'category_name': 'Fat Burner',
        'supplement_type': 'Fat Burner',
        'price': 79.99,
        'suitable_for_goals': 'fat-loss,general-health,athletic',
        'description': 'Professional-grade fat burner used by fighters and athletes worldwide.',
        'short_description': 'Metabolic booster | Professional grade',
    },
    {
        'name': 'Green Tea Extract Fat Burner',
        'slug': 'green-tea-extract-fat-burner',
        'category_name': 'Fat Burner',
        'supplement_type': 'Fat Burner',
        'price': 19.99,
        'suitable_for_goals': 'fat-loss,general-health,endurance',
        'description': 'Natural green tea extract to support metabolism and fat oxidation.',
        'short_description': 'Natural | Gentle metabolism support',
    },
    
    # ===== VITAMINS (General Health) =====
    {
        'name': 'Multivitamin Complete Complex',
        'slug': 'multivitamin-complete-complex',
        'category_name': 'Vitamins',
        'supplement_type': 'Multivitamin',
        'price': 14.99,
        'suitable_for_goals': 'general-health,muscle-gain,endurance',
        'description': 'Complete daily multivitamin covering all essential vitamins and minerals.',
        'short_description': '30+ nutrients | Daily coverage',
    },
    {
        'name': 'Vitamin D3 + K2',
        'slug': 'vitamin-d3-k2',
        'category_name': 'Vitamins',
        'supplement_type': 'Vitamins',
        'price': 12.99,
        'suitable_for_goals': 'general-health,athletic,muscle-gain',
        'description': 'Vitamin D3 + K2 for bone health, immune support, and athletic performance.',
        'short_description': '4000 IU D3 | K2 for absorption',
    },
    {
        'name': 'BioCell Collagen',
        'slug': 'biocell-collagen',
        'category_name': 'Vitamins',
        'supplement_type': 'Collagen',
        'price': 34.99,
        'suitable_for_goals': 'general-health,athletic,endurance',
        'description': 'Collagen peptides for joint health, skin, and recovery support.',
        'short_description': 'Joint recovery | Skin health',
    },
]

# ============================================================================
# CREATE PRODUCTS
# ============================================================================

def create_test_products():
    """Create 12 test products for recommendation algorithm testing"""
    
    print("\n" + "=" * 70)
    print("🧪 Creating 12 Test Products for Recommendation Algorithm")
    print("=" * 70)
    
    created_count = 0
    
    for product_data in TEST_PRODUCTS:
        category_name = product_data.pop('category_name')
        
        # Get or create category
        category, _ = ProductCategory.objects.get_or_create(
            name=category_name,
            defaults={'slug': category_name.lower().replace(' ', '-')}
        )
        
        # Create product
        product, created = Product.objects.get_or_create(
            slug=product_data['slug'],
            defaults={
                'category': category,
                'status': 'active',
                **product_data
            }
        )
        
        status_icon = '✅ Created' if created else '⏭️  Exists'
        print(f"{status_icon}: {product.name}")
        
        if created:
            created_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Summary: {created_count} new products created")
    print("=" * 70)
    
    # Show products by category
    print("\n📦 Products by Category:")
    for category in ProductCategory.objects.filter(
        product__in=Product.objects.filter(status='active')
    ).distinct():
        count = category.product_set.filter(status='active').count()
        print(f"   • {category.name}: {count} products")
    
    # Show products by goal
    print("\n🎯 Products by Goal:")
    goals = {}
    for product in Product.objects.filter(status='active'):
        for goal in product.suitable_for_goals.split(','):
            goal = goal.strip()
            if goal not in goals:
                goals[goal] = 0
            goals[goal] += 1
    
    for goal, count in sorted(goals.items()):
        print(f"   • {goal}: {count} products")
    
    print("\n" + "=" * 70)
    print("✅ Test products ready for recommendation testing!")
    print("=" * 70)
    
    # Show recommendation test examples
    print("\n🧪 Testing Recommendations:")
    print("   1. Content-based: GET /api/products/1/recommendations/")
    print("   2. Personalized (auth required): GET /api/products/personalized/")
    print("   3. By goal: GET /api/products/personalized/?goal=muscle-gain")


if __name__ == '__main__':
    create_test_products()
