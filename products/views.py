from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from .models import Product, ProductCategory, ProductReview, UserProfile, RecommendationLog
from .serializers import (
    ProductSerializer, ProductDetailSerializer, ProductCategorySerializer,
    ProductReviewSerializer
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Product CRUD operations.
    
    Endpoints:
    - GET /api/products/ - List all products (with filtering, search, pagination)
    - GET /api/products/{id}/ - Get product details
    - GET /api/products/{id}/recommendations/ - Get content-based recommendations
    - GET /api/products/personalized/ - Get personalized recommendations (session-based)
    - GET /api/products/categories/ - List all categories
    """
    queryset = Product.objects.filter(status='active').prefetch_related('reviews')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtering options
    filterset_fields = {
        'category': ['exact'],
        'supplement_type': ['exact'],
        'price': ['gte', 'lte'],  # price__gte=100&price__lte=500
        'status': ['exact'],
    }
    
    # Search fields
    search_fields = ['name', 'description', 'ingredients']
    
    # Ordering fields
    ordering_fields = ['price', 'created_at', '-average_rating']
    ordering = ['-created_at']
    
    # Pagination - set in settings.py REST_FRAMEWORK config
    
    def get_serializer_class(self):
        """Use different serializer based on action"""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all product categories"""
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """
        Get content-based recommendations for a product.
        
        Content-based logic:
        - Same category products
        - Similar goals products
        - Similar supplement type products
        
        API: GET /api/products/{id}/recommendations/?limit=5
        """
        product = self.get_object()
        limit = int(request.query_params.get('limit', 5))
        
        # Get recommendations: same category OR similar supplement type OR similar goals
        recommendations = Product.objects.filter(
            status='active'
        ).exclude(
            id=product.id
        ).filter(
            Q(category=product.category) |
            Q(supplement_type=product.supplement_type) |
            Q(suitable_for_goals__icontains=product.suitable_for_goals)
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).distinct()[:limit]
        
        serializer = ProductSerializer(recommendations, many=True)
        
        return Response({
            'count': len(serializer.data),
            'current_product': ProductSerializer(product).data,
            'recommendations': serializer.data,
            'reason': 'Content-based: Similar category, supplement type, or fitness goals'
        })
    
    @action(detail=False, methods=['get'])
    def personalized(self, request):
        """
        Get personalized recommendations based on user profile.
        
        Session-based logic:
        - Get or create user profile from session_id
        - Get products matching user's fitness goal
        - Filter by user's dietary restrictions if any
        - Sort by highest rating and popularity
        
        API: GET /api/products/personalized/?goal=muscle_gain&limit=5
        """
        # Get session_id from request
        session_id = request.session.session_key
        goal = request.query_params.get('goal', None)
        limit = int(request.query_params.get('limit', 5))
        
        if not session_id:
            return Response({
                'error': 'Session not initialized',
                'message': 'Please visit a page to initialize session first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(
            session_id=session_id,
            defaults={'goal': goal or 'general_fitness'}
        )
        
        # Build recommendation query
        query = Q(status='active')
        
        # Filter by goal if specified
        if goal:
            query &= Q(suitable_for_goals__icontains=goal)
        else:
            # Use user's goal from profile
            query &= Q(suitable_for_goals__icontains=user_profile.goal)
        
        # Filter by dietary restrictions if user has any
        if user_profile.dietary_restrictions:
            # Exclude products that don't match user's dietary restrictions
            restrictions = user_profile.dietary_restrictions.split(',')
            for restriction in restrictions:
                query &= ~Q(suitable_for_goals__icontains=restriction.strip())
        
        # Get products with annotations
        recommendations = Product.objects.filter(query).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews', filter=Q(reviews__is_approved=True))
        ).order_by('-review_count', '-avg_rating')[:limit]
        
        serializer = ProductSerializer(recommendations, many=True)
        
        # Log recommendation event
        for product in recommendations:
            RecommendationLog.objects.create(
                user_profile=user_profile,
                recommended_product=product,
                recommendation_type='personalized',
                score=0.0,  # Will be set if user interacts
                reason=f'Personalized for goal: {goal or user_profile.goal}'
            )
        
        return Response({
            'count': len(serializer.data),
            'user_profile': {
                'session_id': user_profile.session_id,
                'goal': user_profile.goal,
                'dietary_restrictions': user_profile.dietary_restrictions,
            },
            'recommendations': serializer.data,
            'reason': f'Personalized recommendations for goal: {goal or user_profile.goal}'
        })


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for ProductCategory"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductReviewViewSet(viewsets.ModelViewSet):
    """API ViewSet for ProductReview"""
    queryset = ProductReview.objects.filter(is_approved=True).order_by('-created_at')
    serializer_class = ProductReviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['rating', '-created_at']
    ordering = ['-created_at']
    
    def create(self, request, *args, **kwargs):
        """Create a new review"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """
        Increase helpful_count for a review
        POST /api/reviews/{id}/mark_helpful/
        """
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        return Response({
            'status': 'success',
            'helpful_count': review.helpful_count
        }, status=status.HTTP_200_OK)


# ===== FRONTEND VIEWS (HTML RENDERING) =====

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator


def product_list(request):
    """
    Display product listing page with filtering, search, and pagination
    
    Features:
    - Pagination (10 products per page)
    - Category filtering
    - Search functionality
    - Sorting by price and rating
    - Display reviews count and average rating
    """
    products = Product.objects.filter(status='active').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    )
    
    # Filtering by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Filtering by supplement type
    supplement_type = request.GET.get('supplement_type')
    if supplement_type:
        products = products.filter(supplement_type=supplement_type)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(ingredients__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['price', '-price', 'avg_rating', '-avg_rating', '-created_at', 'created_at']
    if sort_by in valid_sorts:
        products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    
    # Get all categories for filter sidebar
    categories = ProductCategory.objects.all()
    supplement_types = Product.objects.filter(status='active').values_list(
        'supplement_type', flat=True
    ).distinct()
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'supplement_types': supplement_types,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_supplement': supplement_type,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Display product detail page with full information and reviews
    
    Features:
    - Product information (nutrition, pricing, description)
    - Customer reviews
    - Rating and review count
    - Recommended similar products
    - Handle review submission via POST
    """
    product = get_object_or_404(Product, slug=slug, status='active')
    
    # Handle review submission
    message = None
    if request.method == 'POST':
        try:
            review = ProductReview.objects.create(
                product=product,
                author_name=request.POST.get('author_name'),
                author_email=request.POST.get('author_email'),
                rating=int(request.POST.get('rating')),
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                is_verified_purchase=request.POST.get('is_verified_purchase') == 'on',
                is_approved=False,  # Cần admin phê duyệt
            )
            message = 'Cảm ơn! Đánh giá của bạn đã được gửi. Admin sẽ phê duyệt trong thời gian sớm nhất.'
        except Exception as e:
            message = f'Lỗi: {str(e)}'
    
    # Get approved reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Get recommendations (similar products)
    recommendations = Product.objects.filter(
        status='active'
    ).exclude(
        id=product.id
    ).filter(
        Q(category=product.category) |
        Q(supplement_type=product.supplement_type) |
        Q(suitable_for_goals__icontains=product.suitable_for_goals)
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    ).distinct()[:6]
    
    # Calculate averages
    avg_rating = product.get_average_rating()
    review_count = product.get_review_count()
    
    context = {
        'product': product,
        'reviews': reviews,
        'recommendations': recommendations,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'rating_range': range(1, 6),  # For star display
        'message': message,
    }
    
    return render(request, 'products/product_detail.html', context)
