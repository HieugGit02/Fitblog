"""
Script tạo dữ liệu mẫu cho testing Recommendation System
Chạy: python manage.py shell < products/management/commands/create_sample_data.py
"""

from products.models import ProductCategory, Product, ProductReview, UserProfile
from django.utils import timezone

print("=" * 80)
print("🚀 CREATING SAMPLE DATA FOR RECOMMENDATION SYSTEM")
print("=" * 80)

# ============================================================================
# 1. CREATE CATEGORIES
# ============================================================================
print("\n📂 Creating Categories...")

categories_data = [
    {
        'name': 'Whey Protein',
        'slug': 'whey-protein',
        'description': 'Whey protein isolate, concentrate, and blends',
        'color': '#FF6B6B'
    },
    {
        'name': 'Creatine',
        'slug': 'creatine',
        'description': 'Creatine monohydrate and derivatives',
        'color': '#4ECDC4'
    },
    {
        'name': 'Pre-Workout',
        'slug': 'pre-workout',
        'description': 'Pre-workout supplements for energy and focus',
        'color': '#FFE66D'
    },
    {
        'name': 'BCAA / EAA',
        'slug': 'bcaa-eaa',
        'description': 'Branched and Essential Amino Acids',
        'color': '#95E1D3'
    },
    {
        'name': 'Vitamins & Minerals',
        'slug': 'vitamins-minerals',
        'description': 'Multivitamins, minerals, and micronutrients',
        'color': '#F38181'
    },
    {
        'name': 'Fat Burners',
        'slug': 'fat-burners',
        'description': 'Thermogenic supplements for fat loss',
        'color': '#AA96DA'
    },
]

categories = {}
for cat_data in categories_data:
    cat, created = ProductCategory.objects.get_or_create(
        slug=cat_data['slug'],
        defaults={
            'name': cat_data['name'],
            'description': cat_data['description'],
            'color': cat_data['color']
        }
    )
    categories[cat_data['slug']] = cat
    status = "✅ Created" if created else "⏭️  Already exists"
    print(f"  {status}: {cat.name}")

# ============================================================================
# 2. CREATE PRODUCTS
# ============================================================================
print("\n🏋️ Creating Products...")

products_data = [
    # Whey Protein
    {
        'name': 'Whey Protein Gold Standard',
        'slug': 'whey-gold-standard',
        'category_slug': 'whey-protein',
        'supplement_type': 'whey',
        'description': 'Premium whey protein isolate with excellent taste',
        'short_description': 'High quality whey protein',
        'price': 5000000,
        'discount_percent': 10,
        'serving_size': '30g',
        'protein_per_serving': 24,
        'carbs_per_serving': 3,
        'fat_per_serving': 1.5,
        'calories_per_serving': 120,
        'ingredients': 'Whey Isolate, Natural Flavors, Stevia',
        'flavor': 'Vanilla',
        'tags': 'whey,isolate,muscle-gain,lean',
        'suitable_for_goals': 'muscle-gain,lean,strength',
    },
    {
        'name': 'Whey Protein Concentrate',
        'slug': 'whey-concentrate-budget',
        'category_slug': 'whey-protein',
        'supplement_type': 'concentrate',
        'description': 'Affordable whey protein concentrate for mass building',
        'short_description': 'Budget-friendly whey protein',
        'price': 3000000,
        'discount_percent': 5,
        'serving_size': '35g',
        'protein_per_serving': 22,
        'carbs_per_serving': 4,
        'fat_per_serving': 2,
        'calories_per_serving': 130,
        'ingredients': 'Whey Concentrate, Maltodextrin, Natural Flavors',
        'flavor': 'Chocolate',
        'tags': 'whey,concentrate,budget,mass-gain',
        'suitable_for_goals': 'muscle-gain,mass-gain',
    },
    # Creatine
    {
        'name': 'Creatine Monohydrate Powder',
        'slug': 'creatine-mono',
        'category_slug': 'creatine',
        'supplement_type': 'creatine',
        'description': 'Pure creatine monohydrate for muscle strength and power',
        'short_description': 'Classic creatine supplement',
        'price': 1200000,
        'discount_percent': 0,
        'serving_size': '5g',
        'protein_per_serving': 0,
        'carbs_per_serving': 0,
        'fat_per_serving': 0,
        'calories_per_serving': 20,
        'ingredients': 'Creatine Monohydrate',
        'flavor': 'Unflavored',
        'tags': 'creatine,strength,power,gains',
        'suitable_for_goals': 'strength,muscle-gain,athletic',
    },
    # Pre-Workout
    {
        'name': 'Pre-Workout Extreme Energy',
        'slug': 'preworkout-extreme',
        'category_slug': 'pre-workout',
        'supplement_type': 'preworkout',
        'description': 'High-stimulant pre-workout with caffeine and beta-alanine',
        'short_description': 'Intense energy and focus',
        'price': 2800000,
        'discount_percent': 15,
        'serving_size': '10g',
        'protein_per_serving': 1,
        'carbs_per_serving': 2,
        'fat_per_serving': 0,
        'calories_per_serving': 15,
        'ingredients': 'Caffeine, Beta-Alanine, Taurine, Citrulline Malate',
        'flavor': 'Blue Raspberry',
        'tags': 'preworkout,caffeine,energy,focus',
        'suitable_for_goals': 'strength,athletic,muscle-gain',
    },
    # BCAA
    {
        'name': 'BCAA 2:1:1 Powder',
        'slug': 'bcaa-2-1-1',
        'category_slug': 'bcaa-eaa',
        'supplement_type': 'bcaa',
        'description': 'BCAA with optimal 2:1:1 ratio for muscle recovery',
        'short_description': 'Essential amino acids for recovery',
        'price': 1800000,
        'discount_percent': 0,
        'serving_size': '5g',
        'protein_per_serving': 5,
        'carbs_per_serving': 0,
        'fat_per_serving': 0,
        'calories_per_serving': 20,
        'ingredients': 'L-Leucine, L-Isoleucine, L-Valine',
        'flavor': 'Lemon',
        'tags': 'bcaa,amino-acids,recovery,intra-workout',
        'suitable_for_goals': 'muscle-gain,endurance,recovery',
    },
    # Vitamins
    {
        'name': 'Complete Multivitamin Stack',
        'slug': 'multivitamin-complete',
        'category_slug': 'vitamins-minerals',
        'supplement_type': 'vitamins',
        'description': 'Complete micronutrient formula for overall health',
        'short_description': 'All-in-one vitamin stack',
        'price': 900000,
        'discount_percent': 0,
        'serving_size': '3 tablets',
        'protein_per_serving': 0,
        'carbs_per_serving': 0,
        'fat_per_serving': 0,
        'calories_per_serving': 5,
        'ingredients': 'Vitamin A, B-Complex, C, D3, E, Zinc, Magnesium',
        'flavor': 'N/A',
        'tags': 'vitamins,health,immune,general',
        'suitable_for_goals': 'general-health,athletic,recovery',
    },
    # Fat Burner
    {
        'name': 'Thermogenic Fat Burner',
        'slug': 'fatburner-thermo',
        'category_slug': 'fat-burners',
        'supplement_type': 'fatburner',
        'description': 'Thermogenic formula to boost metabolism and energy',
        'short_description': 'Metabolism boost for fat loss',
        'price': 1600000,
        'discount_percent': 20,
        'serving_size': '2 capsules',
        'protein_per_serving': 0,
        'carbs_per_serving': 0,
        'fat_per_serving': 0,
        'calories_per_serving': 0,
        'ingredients': 'Green Tea Extract, Caffeine, Capsaicin, CLA',
        'flavor': 'N/A',
        'tags': 'fatburner,weight-loss,metabolism,energy',
        'suitable_for_goals': 'fat-loss,lean,weight-loss',
    },
]

products = {}
for prod_data in products_data:
    category = categories[prod_data.pop('category_slug')]
    prod, created = Product.objects.get_or_create(
        slug=prod_data['slug'],
        defaults={**prod_data, 'category': category}
    )
    products[prod_data['slug']] = prod
    status = "✅ Created" if created else "⏭️  Already exists"
    print(f"  {status}: {prod.name} ({prod.get_goals_list()})")

# ============================================================================
# 3. CREATE REVIEWS
# ============================================================================
print("\n⭐ Creating Reviews...")

reviews_data = [
    ('whey-gold-standard', 5, 'Best whey I ever tried', 'Amazing taste and quality!'),
    ('whey-gold-standard', 4, 'Good product', 'Works great, mixes well'),
    ('whey-gold-standard', 5, 'Highly recommend', 'Best for muscle gain'),
    ('whey-concentrate-budget', 4, 'Great value', 'Good protein for the price'),
    ('whey-concentrate-budget', 3, 'OK quality', 'Tastes a bit gritty'),
    ('creatine-mono', 5, 'Works perfectly', 'Pure creatine, highly effective'),
    ('creatine-mono', 5, 'Noticeable gains', 'Strength increased in 2 weeks'),
    ('preworkout-extreme', 5, 'Best energy ever', 'Amazing pump and focus'),
    ('preworkout-extreme', 4, 'Good but strong', 'Very intense, not for beginners'),
    ('bcaa-2-1-1', 4, 'Great for recovery', 'Tastes good, helps with soreness'),
    ('multivitamin-complete', 5, 'Feel much better', 'Energy and health improved'),
    ('fatburner-thermo', 4, 'Effective thermogenic', 'Noticeable boost in metabolism'),
]

for product_slug, rating, title, content in reviews_data:
    product = products[product_slug]
    review, created = ProductReview.objects.get_or_create(
        product=product,
        author_email=f"reviewer_{product_slug}_{rating}@fitblog.vn",
        defaults={
            'author_name': f'User_{rating}Stars',
            'rating': rating,
            'title': title,
            'content': content,
            'is_verified_purchase': True,
            'is_approved': True,
        }
    )
    if created:
        print(f"  ✅ Review added: {product.name} - {rating}⭐")

# ============================================================================
# 4. CREATE USER PROFILES
# ============================================================================
print("\n Creating User Profiles...")

user_profiles_data = [
    {
        'session_id': 'session_muscle_gain_001',
        'goal': 'muscle-gain',
        'age': 25,
        'weight_kg': 75,
        'height_cm': 175,
        'activity_level': 'active',
        'preferred_supplement_types': 'whey,creatine,bcaa',
        'dietary_restrictions': '',
    },
    {
        'session_id': 'session_fat_loss_001',
        'goal': 'fat-loss',
        'age': 30,
        'weight_kg': 85,
        'height_cm': 180,
        'activity_level': 'moderate',
        'preferred_supplement_types': 'fatburner,bcaa,vitamins',
        'dietary_restrictions': '',
    },
    {
        'session_id': 'session_strength_001',
        'goal': 'strength',
        'age': 28,
        'weight_kg': 80,
        'height_cm': 178,
        'activity_level': 'intense',
        'preferred_supplement_types': 'creatine,preworkout,whey',
        'dietary_restrictions': '',
    },
]

for profile_data in user_profiles_data:
    profile, created = UserProfile.objects.get_or_create(
        session_id=profile_data['session_id'],
        defaults=profile_data
    )
    if created:
        profile.calculate_bmi()
        profile.calculate_tdee()
        profile.save()
        print(f"  ✅ User created: {profile.goal} (BMI: {profile.bmi:.1f}, TDEE: {profile.tdee:.0f} kcal)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("✅ SAMPLE DATA CREATION COMPLETED!")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"   Categories: {ProductCategory.objects.count()}")
print(f"   Products: {Product.objects.count()}")
print(f"   Reviews: {ProductReview.objects.count()}")
print(f"   User Profiles: {UserProfile.objects.count()}")
print(f"\n🧪 Test these endpoints:")
print(f"   1. GET /api/products/ - List all products")
print(f"   2. GET /api/products/1/recommendations/?limit=5 - Content-based")
print(f"   3. GET /api/products/personalized/?goal=muscle-gain&limit=5 - Personalized")
print(f"   4. GET /products/ - Frontend product list")
print(f"   5. GET /products/whey-gold-standard/ - Frontend product detail")
print("\n" + "=" * 80)
