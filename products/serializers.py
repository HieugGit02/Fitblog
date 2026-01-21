from rest_framework import serializers
from .models import ProductCategory, Product, ProductReview, UserProfile, EventLog


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for ProductCategory"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'icon', 'color', 'product_count']
    
    def get_product_count(self, obj):
        """Get number of products in category"""
        return obj.products.filter(status='active').count()


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductReview
    
    Includes user_id & product_id để dùng cho Collaborative Filtering:
    - user_id: User đã đánh giá sản phẩm
    - product_id: Sản phẩm được đánh giá
    - rating: Điểm đánh giá (1-5 sao) - tạo user-item matrix
    """
    username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True, allow_null=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'user_id', 'username', 'product_id',
            'author_name', 'rating', 'title', 'content',
            'is_verified_purchase', 'is_approved', 'helpful_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'helpful_count', 'user_id', 'username', 'product_id']


class ProductSerializer(serializers.ModelSerializer):
    """Simple serializer for product list view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 'category_icon',
            'supplement_type', 'price', 'discount_percent', 'discounted_price',
            'serving_size', 'image',
            'average_rating', 'review_count', 'status', 'created_at'
        ]
    
    def get_average_rating(self, obj):
        """Get average rating"""
        rating = obj.get_average_rating()
        return round(rating, 1) if rating else None
    
    def get_review_count(self, obj):
        """Get review count"""
        return obj.get_review_count()
    
    def get_discounted_price(self, obj):
        """Get discounted price"""
        return round(obj.get_discounted_price(), 0)


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product detail view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    goals_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category_name', 'category_icon',
            'supplement_type', 'price', 'discount_percent', 'discounted_price',
            'serving_size',
            'protein_per_serving', 'carbs_per_serving', 'fat_per_serving',
            'calories_per_serving', 'ingredients', 'flavor',
            'image', 'average_rating', 'review_count',
            'reviews', 'tags_list', 'goals_list', 'status', 'created_at'
        ]
    
    def get_average_rating(self, obj):
        rating = obj.get_average_rating()
        return round(rating, 1) if rating else None
    
    def get_review_count(self, obj):
        return obj.get_review_count()
    
    def get_discounted_price(self, obj):
        return round(obj.get_discounted_price(), 0)
    
    def get_reviews(self, obj):
        """Get approved reviews"""
        reviews = ProductReview.objects.filter(product=obj, is_approved=True).order_by('-created_at')[:5]
        return ProductReviewSerializer(reviews, many=True).data
    
    def get_tags_list(self, obj):
        """Get tags as list"""
        return obj.get_tags_list()
    
    def get_goals_list(self, obj):
        """Get suitable goals as list"""
        return obj.get_goals_list()
