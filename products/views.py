from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Product, ProductCategory, ProductReview, UserProfile, RecommendationLog
from .serializers import (
    ProductSerializer, ProductDetailSerializer, ProductCategorySerializer,
    ProductReviewSerializer
)
import logging

logger = logging.getLogger(__name__)


# ===== THROTTLE CLASSES =====
class ProductListThrottle(AnonRateThrottle):
    """Limit: 100 requests per hour for anonymous users"""
    scope = 'product_list'


class ProductDetailThrottle(AnonRateThrottle):
    """Limit: 200 requests per hour for product details"""
    scope = 'product_detail'


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
    # ✅ OPTIMIZATION: Added select_related('category') to avoid N+1 queries
    queryset = Product.objects.filter(status='active')\
        .select_related('category')\
        .prefetch_related('reviews')
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    throttle_classes = [ProductListThrottle, ProductDetailThrottle]
    
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
    @method_decorator(cache_page(60 * 5))  # ✅ Cache 5 minutes
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
        
        FIX: Only support authenticated users (linked to User model)
        - Get user profile from authenticated user
        - Get products matching user's fitness goal
        - Filter by user's dietary restrictions if any
        - Sort by highest rating and popularity
        
        API: GET /api/products/personalized/?goal=muscle_gain&limit=5
        
        IMPORTANT: This endpoint ONLY works for authenticated users!
        Anonymous users should use /api/products/ endpoint instead.
        """
        # Get user profile from authenticated user
        if not request.user.is_authenticated:
            return Response({
                'error': 'Authentication required',
                'message': 'Please login to get personalized recommendations'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the user's profile (created by signal when user was created)
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Profile not found',
                'message': 'Please complete your profile setup first'
            }, status=status.HTTP_404_NOT_FOUND)
        
        goal = request.query_params.get('goal', None)
        limit = int(request.query_params.get('limit', 5))
        
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
        
        # ✅ OPTIMIZATION: Use bulk_create instead of loop (50 queries → 1 query)
        logs = [
            RecommendationLog(
                user_profile=user_profile,
                recommended_product=product,
                recommendation_type='personalized',
                score=0.0,
                reason=f'Personalized for goal: {goal or user_profile.goal}'
            )
            for product in recommendations
        ]
        if logs:
            RecommendationLog.objects.bulk_create(logs, ignore_conflicts=True)
        
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
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def collaborative(self, request):
        """
        🤝 Get recommendations using Collaborative Filtering algorithm
        
        User-based collaborative filtering:
        - Finds users with similar rating patterns
        - Recommends products that similar users rated high
        - Only works with authenticated users (need user_id for algorithms)
        
        API: GET /api/products/collaborative/?limit=5&min_rating=3.5
        
        Query params:
        - limit: Number of recommendations (default 5)
        - min_rating: Minimum predicted rating (default 3.5)
        
        Returns:
        - List of products with predicted_rating (1-5)
        - Similar users info
        
        Status: ✅ Ready for testing
        Data requirement: Need at least 10 reviews from different users
        """
        from .recommendation_service import get_collaborative_engine
        
        # Only for authenticated users
        if not request.user.is_authenticated:
            return Response({
                'error': 'Authentication required',
                'message': 'Collaborative filtering requires authentication'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        limit = int(request.query_params.get('limit', 5))
        min_rating = float(request.query_params.get('min_rating', 3.5))
        
        try:
            # Get collaborative filtering engine
            engine = get_collaborative_engine()
            
            # Find similar users
            similar_users = engine.find_similar_users(request.user.id)
            
            if not similar_users:
                return Response({
                    'count': 0,
                    'recommendations': [],
                    'reason': 'Not enough similar users found',
                    'note': 'Collaborative filtering needs more user reviews to work'
                })
            
            # Get recommendations
            recommendations = engine.recommend(
                request.user.id,
                n_recommendations=limit,
                min_predicted_rating=min_rating
            )
            
            if not recommendations:
                return Response({
                    'count': 0,
                    'recommendations': [],
                    'similar_users': len(similar_users),
                    'reason': 'No products with sufficient predicted rating'
                })
            
            # Fetch product details
            product_ids = [prod_id for prod_id, score in recommendations]
            products = Product.objects.filter(id__in=product_ids)
            product_map = {p.id: p for p in products}
            
            # Build response with predicted ratings
            result = []
            for product_id, predicted_rating in recommendations:
                product = product_map.get(product_id)
                if product:
                    result.append({
                        'id': product.id,
                        'name': product.name,
                        'slug': product.slug,
                        'price': float(product.price),
                        'image': product.image.url if product.image else None,
                        'predicted_rating': round(predicted_rating, 2),
                        'actual_rating': float(product.get_average_rating() or 0),
                        'category': product.category.name,
                        'reason': f'Similar users rated this {predicted_rating:.1f}/5'
                    })
            
            # Log similar users info for debugging
            similar_users_info = [
                {
                    'user_id': uid,
                    'similarity_score': round(score, 3)
                }
                for uid, score in similar_users[:3]  # Top 3 similar users
            ]
            
            return Response({
                'count': len(result),
                'recommendations': result,
                'algorithm': 'User-based Collaborative Filtering',
                'similar_users': similar_users_info,
                'parameters': {
                    'k_neighbors': engine.k_neighbors,
                    'min_predicted_rating': min_rating
                },
                'status': '✅ Success',
                'note': 'Recommendations based on users with similar rating patterns'
            })
            
        except Exception as e:
            logger.error(f"❌ Collaborative filtering error: {str(e)}")
            return Response({
                'error': 'Algorithm error',
                'message': str(e),
                'status': '❌ Failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for ProductCategory"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for ProductReview
    
    Dùng cho Collaborative Filtering Recommendation:
    - GET /api/reviews/ → Lấy tất cả approved reviews (kèm user_id, product_id, rating)
    - POST /api/reviews/ → Tạo review mới (tự động gán user nếu authenticated)
    - POST /api/reviews/{id}/mark_helpful/ → Đánh dấu review hữu ích
    """
    queryset = ProductReview.objects.filter(is_approved=True).order_by('-created_at')
    serializer_class = ProductReviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'rating', 'user']  # Thêm user filter
    ordering_fields = ['rating', '-created_at', 'user']
    ordering = ['-created_at']
    
    def create(self, request, *args, **kwargs):
        """
        Create a new review
        Tự động gán user nếu user đã authenticated
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Tự động gán user nếu authenticated
        if request.user.is_authenticated:
            self.perform_create(serializer, user=request.user)
        else:
            self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer, user=None):
        """Override để gán user"""
        if user:
            serializer.save(user=user)
        else:
            serializer.save()
    
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

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import UserProfileForm, QuickProfileForm


def user_profile_setup(request):
    """
    Setup user profile - người dùng điền thông tin cá nhân (tuổi, cân, cao, mục tiêu)
    
    ONLY FOR AUTHENTICATED USERS!
    
    GET: Hiển thị form
    POST: Lưu thông tin và redirect về trang chủ
    
    Features:
    - Auto-calculate BMI & TDEE
    - Require login (cannot use session-based)
    - Validation input
    - Update UserProfile created by signal
    
    URL: /products/setup/
    Template: products/user_profile_setup.html
    """
    # Require login
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để setup hồ sơ')
        return redirect('products:product_list')
    
    # Get the user's profile (created by signal)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Lỗi: Không tìm thấy hồ sơ')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Thông tin của bạn đã được lưu!')
            return redirect('products:user_profile_view')
        else:
            messages.error(request, '❌ Vui lòng kiểm tra lại thông tin!')
    else:
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'title': 'Thiết Lập Thông Tin Cá Nhân',
    }
    
    return render(request, 'products/user_profile_setup.html', context)


def user_profile_quick_setup(request):
    """
    Quick setup - form rút gọn chỉ hỏi thông tin thiết yếu
    
    ONLY FOR AUTHENTICATED USERS!
    
    Dùng khi:
    - User muốn setup nhanh
    - User lần đầu vào website
    - Sidebar widget
    
    URL: /products/quick-setup/
    Template: products/user_profile_quick_setup.html
    """
    # Require login
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập')
        return redirect('products:product_list')
    
    # Get the user's profile (created by signal)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Lỗi: Không tìm thấy hồ sơ')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = QuickProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Setup xong! Hãy xem gợi ý sản phẩm cho bạn.')
            return redirect('products:product_list')
    else:
        form = QuickProfileForm(instance=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'title': 'Quick Setup',
    }
    
    return render(request, 'products/user_profile_quick_setup.html', context)


def user_profile_view(request):
    """
    Xem & chỉnh sửa profile của user
    
    SUPPORTS BOTH:
    1. Authenticated users (linked to User model)
    2. Session-based users (no login required)
    
    GET: Hiển thị thông tin profile (với metrics tính toán)
    POST: Update profile
    
    URL: /products/profile/
    Template: products/user_profile_view.html
    """
    # Try to get UserProfile
    user_profile = None
    
    # Priority 1: Authenticated user
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            messages.error(request, 'Lỗi: Không tìm thấy hồ sơ')
            return redirect('products:product_list')
    
    # Priority 2: Session-based user
    if not user_profile:
        session_id = request.session.session_key
        if session_id:
            try:
                user_profile = UserProfile.objects.get(session_id=session_id)
            except UserProfile.DoesNotExist:
                messages.warning(request, 'Vui lòng điền thông tin profile trước')
                return redirect('products:user_profile_setup')
    
    # If still no profile, redirect to setup
    if not user_profile:
        messages.warning(request, 'Vui lòng điền thông tin profile')
        return redirect('products:user_profile_setup')
    
    # Lấy recommendation logs (personalized)
    personalized_products = RecommendationLog.objects.filter(
        user_profile=user_profile,
        recommendation_type__in=['personalized', 'goal-based']
    ).order_by('-created_at')[:6]
    
    # Lấy tất cả logs
    all_logs = RecommendationLog.objects.filter(
        user_profile=user_profile
    ).order_by('-created_at')[:20]
    
    context = {
        'user_profile': user_profile,
        'personalized_products': personalized_products,
        'all_logs': all_logs,
        'bmi_status': get_bmi_status(user_profile.bmi) if user_profile.bmi else None,
        'tdee_info': get_tdee_info(user_profile.tdee) if user_profile.tdee else None,
        'has_profile_filled': bool(user_profile.goal and user_profile.goal != 'general-health'),
    }
    
    return render(request, 'products/user_profile_view.html', context)


def user_profile_delete(request):
    """
    Xóa hồ sơ người dùng
    
    ONLY FOR AUTHENTICATED USERS!
    
    GET: Hiển thị confirmation dialog
    POST: Xóa profile + recommendation logs
    
    URL: /products/profile/delete/
    Template: products/user_profile_delete.html
    """
    # Require login
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập')
        return redirect('products:product_list')
    
    # Get the user's profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy hồ sơ')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        # Xóa toàn bộ recommendation logs
        RecommendationLog.objects.filter(user_profile=user_profile).delete()
        
        # Reset profile data (keep profile linked to user)
        user_profile.age = None
        user_profile.weight_kg = None
        user_profile.height_cm = None
        user_profile.gender = None
        user_profile.bmi = None
        user_profile.tdee = None
        user_profile.goal = 'general-health'
        user_profile.activity_level = None
        user_profile.preferred_supplement_types = ''
        user_profile.dietary_restrictions = ''
        user_profile.save()
        
        messages.success(request, '✅ Hồ sơ đã được reset. Bạn có thể setup lại!')
        return redirect('products:product_list')
    
    # GET: Show confirmation
    context = {
        'user_profile': user_profile,
        'recommendation_count': RecommendationLog.objects.filter(user_profile=user_profile).count()
    }
    
    return render(request, 'products/user_profile_delete.html', context)


def user_profile_reset(request):
    """
    Reset profile data nhưng giữ user link
    (Xóa: age, weight, height, bmi, tdee, goal, activity_level)
    
    ONLY FOR AUTHENTICATED USERS!
    
    GET: Confirmation
    POST: Reset data
    
    URL: /products/profile/reset/
    """
    # Require login
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập')
        return redirect('products:product_list')
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy hồ sơ')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        # Reset data nhưng giữ user link
        user_profile.age = None
        user_profile.weight_kg = None
        user_profile.height_cm = None
        user_profile.gender = None
        user_profile.bmi = None
        user_profile.tdee = None
        user_profile.goal = 'general-health'
        user_profile.activity_level = None
        user_profile.preferred_supplement_types = ''
        user_profile.dietary_restrictions = ''
        user_profile.save()
        
        messages.success(request, '✅ Hồ sơ đã được reset. Bạn có thể setup lại!')
        return redirect('products:user_profile_view')
    
    # GET: Show confirmation
    context = {
        'user_profile': user_profile,
    }
    
    return render(request, 'products/user_profile_reset.html', context)


def user_profile_change_password(request):
    """
    Đổi mật khẩu cho authenticated user
    
    GET: Show change password form
    POST: Update password
    
    URL: /products/profile/change-password/
    """
    from django.contrib.auth import authenticate, update_session_auth_hash
    from django import forms
    from django.contrib import messages
    
    # Require login
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validate inputs
        if not old_password:
            messages.error(request, 'Vui lòng nhập mật khẩu hiện tại')
            return redirect('products:user_profile_change_password')
        
        if not new_password:
            messages.error(request, 'Vui lòng nhập mật khẩu mới')
            return redirect('products:user_profile_change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp')
            return redirect('products:user_profile_change_password')
        
        if len(new_password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự')
            return redirect('products:user_profile_change_password')
        
        # Verify old password
        if not request.user.check_password(old_password):
            messages.error(request, 'Mật khẩu hiện tại không đúng')
            return redirect('products:user_profile_change_password')
        
        if old_password == new_password:
            messages.warning(request, 'Mật khẩu mới phải khác với mật khẩu cũ')
            return redirect('products:user_profile_change_password')
        
        # Update password
        try:
            request.user.set_password(new_password)
            request.user.save()
            
            # Keep user logged in after password change
            update_session_auth_hash(request, request.user)
            
            messages.success(request, '✅ Mật khẩu đã được thay đổi thành công!')
            return redirect('products:user_profile_view')
        except Exception as e:
            messages.error(request, f'❌ Có lỗi xảy ra: {str(e)}')
            logger.error(f'Error changing password for user {request.user.id}: {str(e)}')
            return redirect('products:user_profile_change_password')
    
    # GET: Show form
    return render(request, 'products/user_profile_change_password.html', {
        'user': request.user
    })


def get_bmi_status(bmi):
    """Helper function: lấy trạng thái BMI"""
    if bmi < 18.5:
        return {'status': 'Gầy', 'color': 'warning', 'class': 'text-warning'}
    elif bmi < 25:
        return {'status': 'Bình thường', 'color': 'success', 'class': 'text-success'}
    elif bmi < 30:
        return {'status': 'Thừa cân', 'color': 'info', 'class': 'text-info'}
    else:
        return {'status': 'Béo phì', 'color': 'danger', 'class': 'text-danger'}


def get_tdee_info(tdee):
    """Helper function: lấy thông tin TDEE"""
    if tdee < 1500:
        return 'Lượng calo thấp - phù hợp với chế độ giảm cân mạnh'
    elif tdee < 2000:
        return 'Lượng calo vừa phải'
    elif tdee < 2500:
        return 'Lượng calo cao - phù hợp với mục tiêu tăng cơ'
    else:
        return 'Lượng calo rất cao - cần intake đủ calo'


def product_list(request):
    """
    Display product listing page with filtering, search, and pagination
    
    Features:
    - Pagination (10 products per page)
    - Category filtering
    - Search functionality
    - Sorting by price and rating
    - Display reviews count and average rating
    - AJAX support for sorting without page reload
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
    paginator = Paginator(products, 8)  # 8 products per page
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    
    # Get all categories for filter sidebar
    categories = ProductCategory.objects.all()
    supplement_types = Product.objects.filter(status='active').values_list(
        'supplement_type', flat=True
    ).distinct()
    
    # Log recommendation views for users with profile
    user_profile = None
    
    # Priority 1: Authenticated user
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass
    
    # Priority 2: Session-based user
    if not user_profile:
        session_id = request.session.session_key
        if session_id:
            user_profile = UserProfile.objects.filter(session_id=session_id).first()
    
    # Log only if user has setup profile with goal
    if user_profile and user_profile.goal and user_profile.goal != 'general-health':
        # Filter products that match user's goal (true recommendations)
        recommended_products = set(Product.objects.filter(
            status='active',
            suitable_for_goals__icontains=user_profile.goal
        ).values_list('id', flat=True))
        
        # Log matching products as "personalized" recommendations
        for product in page_obj.object_list:
            if product.id in recommended_products:
                # Match user's goal → "personalized" recommendation
                # Don't mark as clicked yet (user only saw on list, not detail page)
                RecommendationLog.objects.get_or_create(
                    user_profile=user_profile,
                    recommended_product=product,
                    defaults={
                        'recommendation_type': 'personalized',
                        'score': 0.95,  # High score for goal match
                        'clicked': False,  # Not clicked yet, just shown on list
                    }
                )
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'supplement_types': supplement_types,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_supplement': supplement_type,
        'sort_by': sort_by,
    }
    
    # Check if AJAX request (for partial content update)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        # Return only the products and pagination HTML (not full page)
        from django.template.loader import render_to_string
        products_html = render_to_string('products/_product_list_partial.html', context, request=request)
        pagination_html = render_to_string('products/_pagination_partial.html', context, request=request)
        return JsonResponse({
            'products_html': products_html,
            'pagination_html': pagination_html,
            'success': True
        })
    
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
    
    # Get recommendations (similar products) - only same category, random 3-5
    recommendations = Product.objects.filter(
        status='active',
        category=product.category
    ).exclude(
        id=product.id
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    ).order_by('?')[:5]  # Random order, max 5 products
    
    # Calculate averages
    avg_rating = product.get_average_rating()
    review_count = product.get_review_count()
    
    # Log product view + recommendations for user with profile
    user_profile = None
    
    # Priority 1: Authenticated user
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass
    
    # Priority 2: Session-based user
    if not user_profile:
        session_id = request.session.session_key
        if session_id:
            user_profile = UserProfile.objects.filter(session_id=session_id).first()
    
    # Only log if user has setup profile with goal
    if user_profile and user_profile.goal and user_profile.goal != 'general-health':
        # Check if main product matches user's goal
        if user_profile.goal in product.suitable_for_goals:
            # Log the main product as "personalized" (matches goal)
            log, created = RecommendationLog.objects.get_or_create(
                user_profile=user_profile,
                recommended_product=product,
                defaults={
                    'recommendation_type': 'personalized',
                    'score': 0.95,
                    'clicked': True,  # Mark as clicked when user views product detail
                }
            )
            # If log already existed, mark as clicked
            if not created and not log.clicked:
                log.clicked = True
                log.save()
        else:
            # Log as "content-based" (same category but different goal)
            log, created = RecommendationLog.objects.get_or_create(
                user_profile=user_profile,
                recommended_product=product,
                defaults={
                    'recommendation_type': 'content-based',
                    'score': 0.5,
                    'clicked': True,  # Mark as clicked when user views product detail
                }
            )
            # If log already existed, mark as clicked
            if not created and not log.clicked:
                log.clicked = True
                log.save()
        
        # Log recommended products (only if match goal)
        for rec_product in recommendations:
            if user_profile.goal in rec_product.suitable_for_goals:
                log, created = RecommendationLog.objects.get_or_create(
                    user_profile=user_profile,
                    recommended_product=rec_product,
                    defaults={
                        'recommendation_type': 'personalized',
                        'score': 0.95,
                    }
                )
                # Don't mark rec_product as clicked (user hasn't viewed them yet)
    
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


# ============================================================================
# TRACKING & ANALYTICS VIEWS
# ============================================================================

def track_product_click(request):
    """
    Track product click/view event from frontend JavaScript
    
    POST /api/track-click/
    Body: {
        'product_id': 123,
        'event_type': 'click' or 'purchase'
    }
    
    Response: {'success': True, 'message': 'Event tracked'}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        product_id = data.get('product_id')
        event_type = data.get('event_type', 'click')  # 'click' or 'purchase'
        
        if not product_id:
            return JsonResponse({'error': 'product_id is required'}, status=400)
        
        # Get session and user profile
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get user profile (only update if exists)
        user_profile = UserProfile.objects.filter(session_id=session_id).first()
        if not user_profile:
            return JsonResponse({'error': 'User profile not found'}, status=404)
        
        # Get product
        product = Product.objects.get(id=product_id)
        
        # Update or create recommendation log
        log, created = RecommendationLog.objects.get_or_create(
            user_profile=user_profile,
            recommended_product=product,
            defaults={
                'recommendation_type': 'content-based',
                'clicked': False,
                'purchased': False,
            }
        )
        
        # Update click/purchase status
        if event_type == 'click':
            log.clicked = True
        elif event_type == 'purchase':
            log.purchased = True
            log.clicked = True  # If purchased, also mark as clicked
        
        log.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Event tracked: {event_type}',
            'log_id': log.id
        })
    
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


