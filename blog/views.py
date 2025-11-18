from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.utils import timezone
from .models import Post, Category, Comment, NewsletterSubscriber

class PostListView(ListView):
    """Danh sách bài viết"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = Post.objects.filter(status='published').order_by('-published_at')
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(post_count=Count('posts'))
        context['featured_posts'] = Post.objects.filter(
            status='published'
        ).order_by('-views')[:3]
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PostDetailView(DetailView):
    """Chi tiết bài viết"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'

    def get_queryset(self):
        return Post.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Tăng lượt xem
        post.views += 1
        post.save(update_fields=['views'])
        
        # Bình luận được phê duyệt
        context['comments'] = post.comments.filter(is_approved=True).order_by('-created_at')
        
        # Bài viết liên quan
        context['related_posts'] = Post.objects.filter(
            category=post.category,
            status='published'
        ).exclude(id=post.id)[:3]
        
        context['categories'] = Category.objects.annotate(post_count=Count('posts'))
        
        return context

    def post(self, request, *args, **kwargs):
        """Xử lý thêm bình luận"""
        post = self.get_object()
        
        author = request.POST.get('author')
        email = request.POST.get('email')
        content = request.POST.get('content')
        
        if author and email and content:
            Comment.objects.create(
                post=post,
                author=author,
                email=email,
                content=content,
                is_approved=False  # Chờ phê duyệt
            )
        
        return self.get(request, *args, **kwargs)


class CategoryDetailView(ListView):
    """Danh sách bài viết theo danh mục"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        return Post.objects.filter(
            category__slug=category_slug,
            status='published'
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(post_count=Count('posts'))
        context['current_category'] = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return context



class CategoriesView(View):
    """Danh sách tất cả danh mục với bài viết trong mỗi danh mục"""
    template_name = 'blog/categories.html'

    def get(self, request):
        # Get all categories with post count
        categories = Category.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0).order_by('name')
        
        # Get featured posts from each category
        category_data = []
        for category in categories:
            posts = Post.objects.filter(
                category=category,
                status='published'
            ).order_by('-published_at')[:3]
            category_data.append({
                'category': category,
                'posts': posts
            })
        
        context = {
            'category_data': category_data,
            'categories': categories,
        }
        return render(request, self.template_name, context)


class HomeView(View):
    """Trang chủ"""
    template_name = 'blog/home.html'

    def get(self, request):
        categories = Category.objects.annotate(post_count=Count('posts'))
        featured_posts = Post.objects.filter(status='published').order_by('-views')[:6]
        latest_posts = Post.objects.filter(status='published').order_by('-published_at')[:3]
        
        context = {
            'categories': categories,
            'featured_posts': featured_posts,
            'latest_posts': latest_posts,
        }
        return render(request, self.template_name, context)


class SubscribeView(View):
    """Đăng ký newsletter"""
    def post(self, request):
        email = request.POST.get('email')
        
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            if created:
                message = "✅ Đăng ký thành công!"
            else:
                message = "ℹ️ Email này đã được đăng ký"
        else:
            message = "❌ Vui lòng nhập email"
        
        # Redirect back to previous page
        next_url = request.POST.get('next', '/')
        return render(request, 'blog/subscribe_message.html', {
            'message': message,
            'next_url': next_url
        })
