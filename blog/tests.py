from django.test import TestCase, Client
from django.urls import reverse
from blog.models import Category, Post
from django.utils import timezone

class BlogTests(TestCase):
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        
        # Create category
        self.category = Category.objects.create(
            name="Dinh Dưỡng",
            slug="dinh-duong",
            icon="🥗",
            description="Bài viết về dinh dưỡng"
        )
        
        # Create post
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            category=self.category,
            content="This is test content",
            status="published",
            published_at=timezone.now()
        )
    
    def test_home_view(self):
        """Test home page loads"""
        response = self.client.get(reverse('blog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/home.html')
    
    def test_post_list(self):
        """Test blog list page"""
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post, response.context['posts'])
    
    def test_post_detail(self):
        """Test post detail page"""
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)
    
    def test_category_detail(self):
        """Test category page"""
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post, response.context['posts'])
    
    def test_post_view_increment(self):
        """Test view counter increments"""
        initial_views = self.post.views
        self.client.get(self.post.get_absolute_url())
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, initial_views + 1)

class ChatbotTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_health_check(self):
        """Test health endpoint"""
        response = self.client.get(reverse('chatbot:health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # May be offline, but endpoint should work
        self.assertIn('status', data)
