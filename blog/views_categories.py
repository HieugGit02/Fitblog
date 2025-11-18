# This snippet shows the new CategoriesView to add to blog/views.py
# Insert this code after CategoryDetailView class and before HomeView class

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
