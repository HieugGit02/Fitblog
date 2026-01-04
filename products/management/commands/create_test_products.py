#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django management command to create 12 test products

Usage:
    python manage.py create_test_products
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import ProductCategory, Product
from PIL import Image
from io import BytesIO


class Command(BaseCommand):
    help = 'Create 12 test products to demonstrate recommendation algorithm'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('🧪 Creating 12 Test Products for Recommendation Algorithm'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        TEST_PRODUCTS = [
            # ===== WHEY PROTEIN (Muscle Gain) =====
            {
                'name': 'Gold Standard Whey Protein',
                'slug': 'gold-standard-whey-protein',
                'category': 'Whey Protein',
                'supplement_type': 'whey',
                'price': 29.99,
                'protein_per_serving': 24,
                'carbs_per_serving': 3,
                'fat_per_serving': 1,
                'calories_per_serving': 110,
                'suitable_for_goals': 'muscle-gain,strength,athletic',
                'description': 'Premium whey protein isolate with 24g protein per serving. Supports muscle growth and recovery.',
                'short_description': '24g protein per serving | Fast absorption',
            },
            {
                'name': 'MuscleTech Nitro-Tech',
                'slug': 'muscletech-nitro-tech',
                'category': 'Whey Protein',
                'supplement_type': 'whey',
                'price': 39.99,
                'protein_per_serving': 30,
                'carbs_per_serving': 4,
                'fat_per_serving': 2,
                'calories_per_serving': 150,
                'suitable_for_goals': 'muscle-gain,strength,athletic',
                'description': 'Advanced whey protein blend with creatine and amino acids for maximum muscle growth.',
                'short_description': '30g protein + Creatine + BCAAs',
            },
            {
                'name': 'Optimum Nutrition Whey',
                'slug': 'optimum-nutrition-whey',
                'category': 'Whey Protein',
                'supplement_type': 'whey',
                'price': 25.99,
                'protein_per_serving': 21,
                'carbs_per_serving': 3,
                'fat_per_serving': 1,
                'calories_per_serving': 100,
                'suitable_for_goals': 'muscle-gain,strength,general-health',
                'description': 'Classic ON whey protein trusted by athletes worldwide for muscle building.',
                'short_description': '21g protein | Most popular',
            },

            # ===== PRE-WORKOUT (Strength) =====
            {
                'name': 'C4 Original Pre-Workout',
                'slug': 'c4-original-pre-workout',
                'category': 'Pre-workout',
                'supplement_type': 'preworkout',
                'price': 34.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 3,
                'fat_per_serving': 0,
                'calories_per_serving': 12,
                'suitable_for_goals': 'strength,athletic,muscle-gain',
                'description': 'High-energy pre-workout with caffeine and beta-alanine for intense training.',
                'short_description': '200mg caffeine | Explosive energy',
            },
            {
                'name': 'Mr. Hyde Pre-Workout',
                'slug': 'mr-hyde-pre-workout',
                'category': 'Pre-workout',
                'supplement_type': 'preworkout',
                'price': 44.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 2,
                'fat_per_serving': 0,
                'calories_per_serving': 8,
                'suitable_for_goals': 'strength,athletic,muscle-gain',
                'description': 'Extreme pre-workout formula designed for maximum pump and strength gains.',
                'short_description': '300mg caffeine | Most powerful',
            },
            {
                'name': 'BCAA + Energy Pre-Workout',
                'slug': 'bcaa-energy-pre-workout',
                'category': 'Pre-workout',
                'supplement_type': 'preworkout',
                'price': 24.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 2,
                'fat_per_serving': 0,
                'calories_per_serving': 10,
                'suitable_for_goals': 'strength,endurance,general-health',
                'description': 'Beginner-friendly pre-workout with BCAAs and moderate caffeine.',
                'short_description': '150mg caffeine | BCAA blend',
            },

            # ===== FAT LOSS (Weight Loss) =====
            {
                'name': 'Leanbean Fat Burner',
                'slug': 'leanbean-fat-burner',
                'category': 'Fat Burner',
                'supplement_type': 'fatburner',
                'price': 59.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 1,
                'fat_per_serving': 0,
                'calories_per_serving': 5,
                'suitable_for_goals': 'fat-loss,general-health',
                'description': 'Premium fat burner specifically formulated for women to support weight loss.',
                'short_description': 'Women-focused | Appetite suppressor',
            },
            {
                'name': 'Instant Knockout Fat Burner',
                'slug': 'instant-knockout-fat-burner',
                'category': 'Fat Burner',
                'supplement_type': 'fatburner',
                'price': 79.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 1,
                'fat_per_serving': 0,
                'calories_per_serving': 5,
                'suitable_for_goals': 'fat-loss,general-health,athletic',
                'description': 'Professional-grade fat burner used by fighters and athletes worldwide.',
                'short_description': 'Metabolic booster | Professional grade',
            },
            {
                'name': 'Green Tea Extract Fat Burner',
                'slug': 'green-tea-extract-fat-burner',
                'category': 'Fat Burner',
                'supplement_type': 'fatburner',
                'price': 19.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 0,
                'fat_per_serving': 0,
                'calories_per_serving': 0,
                'suitable_for_goals': 'fat-loss,general-health,endurance',
                'description': 'Natural green tea extract to support metabolism and fat oxidation.',
                'short_description': 'Natural | Gentle metabolism support',
            },

            # ===== VITAMINS (General Health) =====
            {
                'name': 'Multivitamin Complete Complex',
                'slug': 'multivitamin-complete-complex',
                'category': 'Vitamins',
                'supplement_type': 'vitamins',
                'price': 14.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 1,
                'fat_per_serving': 0,
                'calories_per_serving': 5,
                'suitable_for_goals': 'general-health,muscle-gain,endurance',
                'description': 'Complete daily multivitamin covering all essential vitamins and minerals.',
                'short_description': '30+ nutrients | Daily coverage',
            },
            {
                'name': 'Vitamin D3 + K2',
                'slug': 'vitamin-d3-k2',
                'category': 'Vitamins',
                'supplement_type': 'vitamins',
                'price': 12.99,
                'protein_per_serving': 0,
                'carbs_per_serving': 0,
                'fat_per_serving': 0,
                'calories_per_serving': 0,
                'suitable_for_goals': 'general-health,athletic,muscle-gain',
                'description': 'Vitamin D3 + K2 for bone health, immune support, and athletic performance.',
                'short_description': '4000 IU D3 | K2 for absorption',
            },
            {
                'name': 'BioCell Collagen',
                'slug': 'biocell-collagen',
                'category': 'Vitamins',
                'supplement_type': 'vitamins',
                'price': 34.99,
                'protein_per_serving': 8,
                'carbs_per_serving': 1,
                'fat_per_serving': 0,
                'calories_per_serving': 40,
                'suitable_for_goals': 'general-health,athletic,endurance',
                'description': 'Collagen peptides for joint health, skin, and recovery support.',
                'short_description': 'Joint recovery | Skin health',
            },
        ]

        created_count = 0

        for product_data in TEST_PRODUCTS:
            category_name = product_data.pop('category')

            # Get or create category
            category, _ = ProductCategory.objects.get_or_create(
                name=category_name,
                defaults={'slug': category_name.lower().replace(' ', '-')}
            )

            # Create placeholder image
            img = Image.new('RGB', (300, 300), color='#4CAF50')
            img_io = BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)

            # Create product
            product_data['category'] = category
            product_data['status'] = 'active'
            product_data['image'] = ContentFile(img_io.read(), name=f"{product_data['slug']}.png")

            product, created = Product.objects.update_or_create(
                slug=product_data.pop('slug'),
                defaults=product_data
            )

            status_icon = '✅ ' if created else '⏭️  '
            status_text = 'Created' if created else 'Updated'
            self.stdout.write(f"{status_icon}{status_text}: {product.name}")

            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS(f"📊 Summary: {created_count} new products created"))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Show products by category
        self.stdout.write('\n📦 Products by Category:')
        from django.db.models import Count
        categories = ProductCategory.objects.annotate(
            count=Count('products', filter=__import__('django.db.models', fromlist=['Q']).Q(products__status='active'))
        )
        for cat in categories.filter(count__gt=0):
            self.stdout.write(f"   • {cat.name}: {cat.count} products")

        # Show products by goal
        self.stdout.write('\n🎯 Products by Goal:')
        goals = {}
        for product in Product.objects.filter(status='active'):
            for goal in product.suitable_for_goals.split(','):
                goal = goal.strip()
                if goal not in goals:
                    goals[goal] = 0
                goals[goal] += 1

        for goal, count in sorted(goals.items()):
            self.stdout.write(f"   • {goal}: {count} products")

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ Test products ready for recommendation testing!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Show recommendation test examples
        self.stdout.write(self.style.WARNING('\n🧪 Testing Recommendations:'))
        self.stdout.write('   1. Content-based: GET /api/products/1/recommendations/')
        self.stdout.write('   2. Personalized (auth required): GET /api/products/personalized/')
        self.stdout.write('   3. By goal: GET /api/products/personalized/?goal=muscle-gain')
        self.stdout.write('')
