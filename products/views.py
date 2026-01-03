from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
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

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import UserProfileForm, QuickProfileForm


def user_profile_setup(request):
    """
    Setup user profile - người dùng điền thông tin cá nhân (tuổi, cân, cao, mục tiêu)
    
    GET: Hiển thị form
    POST: Lưu thông tin và redirect về trang chủ
    
    Features:
    - Auto-calculate BMI & TDEE
    - Session-based (không cần login)
    - Validation input
    - Tạo UserProfile chỉ khi submit form (không tự động tạo trống)
    
    URL: /products/setup/
    Template: products/user_profile_setup.html
    """
    # Lấy session_id từ request
    session_id = request.session.session_key
    
    if not session_id:
        # Nếu chưa có session, tạo mới
        request.session.create()
        session_id = request.session.session_key
    
    # Get existing UserProfile hoặc None
    user_profile = UserProfile.objects.filter(session_id=session_id).first()
    
    if request.method == 'POST':
        # Nếu profile chưa tồn tại, tạo mới (không save ngay)
        if not user_profile:
            user_profile = UserProfile(session_id=session_id)
        
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Thông tin của bạn đã được lưu!')
            return redirect('products:product_list')
        else:
            messages.error(request, '❌ Vui lòng kiểm tra lại thông tin!')
    else:
        form = UserProfileForm(instance=user_profile) if user_profile else UserProfileForm()
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'title': 'Thiết Lập Thông Tin Cá Nhân',
    }
    
    return render(request, 'products/user_profile_setup.html', context)


def user_profile_quick_setup(request):
    """
    Quick setup - form rút gọn chỉ hỏi thông tin thiết yếu
    
    Dùng khi:
    - User muốn setup nhanh
    - User lần đầu vào website
    - Sidebar widget
    
    URL: /products/quick-setup/
    Template: products/user_profile_quick_setup.html
    """
    session_id = request.session.session_key
    
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    # Get existing UserProfile hoặc None
    user_profile = UserProfile.objects.filter(session_id=session_id).first()
    
    if request.method == 'POST':
        # Tạo profile nếu chưa tồn tại
        if not user_profile:
            user_profile = UserProfile(session_id=session_id)
        
        form = QuickProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Setup xong! Hãy xem gợi ý sản phẩm cho bạn.')
            return redirect('products:product_list')
    else:
        form = QuickProfileForm(instance=user_profile) if user_profile else QuickProfileForm()
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'title': 'Quick Setup',
    }
    
    return render(request, 'products/user_profile_quick_setup.html', context)


def user_profile_view(request):
    """
    Xem & chỉnh sửa profile của user
    
    GET: Hiển thị thông tin profile (với metrics tính toán)
    POST: Update profile
    
    URL: /products/profile/
    Template: products/user_profile_view.html
    
    Note: Chỉ show profile nếu user đã setup (có data)
    """
    session_id = request.session.session_key
    
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    # Get UserProfile nếu tồn tại, không tạo mới
    user_profile = UserProfile.objects.filter(session_id=session_id).first()
    
    # Lấy recommendation logs (nếu profile tồn tại)
    personalized_products = []
    all_logs = []
    
    if user_profile:
        # Lấy personalized (phù hợp) products để hiển thị dạng card
        personalized_products = RecommendationLog.objects.filter(
            user_profile=user_profile,
            recommendation_type='personalized'
        ).order_by('-created_at')[:6]  # 6 sản phẩm (2 columns x 3 rows)
        
        # Lấy tất cả logs để hiển thị dạng table history
        all_logs = RecommendationLog.objects.filter(
            user_profile=user_profile
        ).order_by('-created_at')[:20]  # 20 logs gần nhất
    
    context = {
        'user_profile': user_profile,
        'personalized_products': personalized_products,
        'all_logs': all_logs,
        'bmi_status': get_bmi_status(user_profile.bmi) if user_profile and user_profile.bmi else None,
        'tdee_info': get_tdee_info(user_profile.tdee) if user_profile and user_profile.tdee else None,
    }
    
    return render(request, 'products/user_profile_view.html', context)


def user_profile_delete(request):
    """
    Xóa hồ sơ người dùng
    
    GET: Hiển thị confirmation dialog
    POST: Xóa profile + recommendation logs + session
    
    URL: /products/profile/delete/
    Template: products/user_profile_delete.html
    """
    session_id = request.session.session_key
    
    if not session_id:
        return redirect('products:user_profile_view')
    
    # Kiểm tra user profile tồn tại
    try:
        user_profile = UserProfile.objects.get(session_id=session_id)
    except UserProfile.DoesNotExist:
        messages.error(request, '❌ Không tìm thấy hồ sơ để xóa')
        return redirect('products:user_profile_view')
    
    if request.method == 'POST':
        # Xóa toàn bộ recommendation logs
        RecommendationLog.objects.filter(user_profile=user_profile).delete()
        
        # Xóa profile
        profile_name = str(user_profile)
        user_profile.delete()
        
        # Xóa session
        request.session.flush()
        
        messages.success(request, '✅ Hồ sơ đã được xóa. Session được reset.')
        return redirect('products:product_list')
    
    # GET: Show confirmation
    context = {
        'user_profile': user_profile,
        'recommendation_count': RecommendationLog.objects.filter(user_profile=user_profile).count()
    }
    
    return render(request, 'products/user_profile_delete.html', context)


def user_profile_reset(request):
    """
    Reset profile data nhưng giữ session_id
    (Xóa: age, weight, height, bmi, tdee, goal, activity_level)
    
    GET: Confirmation
    POST: Reset data
    
    URL: /products/profile/reset/
    """
    session_id = request.session.session_key
    
    if not session_id:
        return redirect('products:user_profile_view')
    
    try:
        user_profile = UserProfile.objects.get(session_id=session_id)
    except UserProfile.DoesNotExist:
        messages.error(request, '❌ Không tìm thấy hồ sơ')
        return redirect('products:user_profile_view')
    
    if request.method == 'POST':
        # Reset data nhưng giữ session_id
        user_profile.age = None
        user_profile.weight_kg = None
        user_profile.height_cm = None
        user_profile.bmi = None
        user_profile.tdee = None
        user_profile.goal = None
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
    session_id = request.session.session_key
    if session_id:
        user_profile = UserProfile.objects.filter(session_id=session_id).first()
        if user_profile and user_profile.goal:  # Only log if user has setup profile with goal
            # Filter products that match user's goal (true recommendations)
            recommended_products = Product.objects.filter(
                status='active',
                suitable_for_goals__icontains=user_profile.goal
            )
            
            # Log ONLY matching products as "personalized" recommendations
            for product in page_obj.object_list:
                if product in recommended_products:
                    # Match user's goal → "personalized" recommendation
                    RecommendationLog.objects.get_or_create(
                        user_profile=user_profile,
                        recommended_product=product,
                        defaults={
                            'recommendation_type': 'personalized',
                            'score': 0.95,  # High score for goal match
                        }
                    )
                # Don't log non-matching products
    
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
    session_id = request.session.session_key
    if session_id:
        user_profile = UserProfile.objects.filter(session_id=session_id).first()
        if user_profile and user_profile.goal:  # Only log if user has setup profile with goal
            # Check if main product matches user's goal
            if user_profile.goal in product.suitable_for_goals:
                # Log the main product as "personalized" (matches goal)
                RecommendationLog.objects.get_or_create(
                    user_profile=user_profile,
                    recommended_product=product,
                    defaults={
                        'recommendation_type': 'personalized',
                        'score': 0.95,
                    }
                )
            else:
                # Log as "content-based" (same category but different goal)
                RecommendationLog.objects.get_or_create(
                    user_profile=user_profile,
                    recommended_product=product,
                    defaults={
                        'recommendation_type': 'content-based',
                        'score': 0.5,
                    }
                )
            
            # Log recommended products (only if match goal)
            for rec_product in recommendations:
                if user_profile.goal in rec_product.suitable_for_goals:
                    RecommendationLog.objects.get_or_create(
                        user_profile=user_profile,
                        recommended_product=rec_product,
                        defaults={
                            'recommendation_type': 'personalized',
                            'score': 0.95,
                        }
                    )
    
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


