# 📋 EVENTLOG QUICK REFERENCE - CHEAT SHEET

## ✅ What Changed

```
❌ RecommendationLog (DELETED)
✅ EventLog (CREATED)
```

---

## 🏗️ EventLog Model Structure

```python
EventLog.objects.create(
    user_profile=user_profile,      # User who triggered event
    product=product,                 # Related product (optional)
    event_type='product_view',       # Type of event
    metadata={                       # Any flexible context
        'page': 'product_list',
        'score': 0.95,
        'reason': 'personalized'
    }
)
# timestamp is auto-set to now()
```

---

## 📊 Event Types Cheat Sheet

| Event Type | Meaning | Example |
|-----------|---------|---------|
| `product_view` | User viewed product detail | Clicked on "Whey Gold" |
| `product_click` | User clicked product | Clicked product card |
| `review_submit` | User submitted review | Posted 5-star review |
| `review_helpful` | Review marked helpful | Clicked "Helpful" button |
| `rec_shown` | Recommendation displayed | "Similar products" shown |
| `rec_clicked` | User clicked recommendation | Clicked recommended product |
| `rec_purchased` | Bought recommended product | Purchased recommendation |
| `search` | User searched | Search for "Protein" |
| `filter_apply` | Applied product filter | Filter by "Price < 500k" |
| `sort_applied` | Changed sort order | Sorted by "Price (Low→High)" |
| `login` | User logged in | Successfully authenticated |
| `logout` | User logged out | Clicked logout button |
| `register` | New user registered | Created account |
| `profile_setup` | Setup fitness profile | Set goal + BMI |
| `profile_update` | Updated profile | Changed fitness goal |

---

## 💻 Code Examples

### Log a product view
```python
EventLog.objects.create(
    user_profile=user_profile,
    product=product,
    event_type='product_view',
    metadata={'page': 'product_detail', 'from_rec': False}
)
```

### Log a recommendation click
```python
EventLog.objects.create(
    user_profile=user_profile,
    product=recommended_product,
    event_type='rec_clicked',
    metadata={
        'recommendation_type': 'personalized',
        'recommendation_score': 0.95
    }
)
```

### Log a review submission
```python
EventLog.objects.create(
    user_profile=user_profile,
    product=product,
    event_type='review_submit',
    metadata={
        'rating': 5,
        'title': 'Great product!',
        'is_verified_purchase': True
    }
)
```

---

## 🔍 Query Examples

### Get recent events for a user
```python
user_events = EventLog.objects.filter(
    user_profile=user_profile
).order_by('-timestamp')[:20]
```

### Get all product views
```python
views = EventLog.objects.filter(
    event_type='product_view'
)
```

### Get recommendation effectiveness
```python
from django.db.models import Count

rec_shown = EventLog.objects.filter(
    event_type='rec_shown'
).count()

rec_clicked = EventLog.objects.filter(
    event_type='rec_clicked'
).count()

click_through_rate = rec_clicked / rec_shown if rec_shown > 0 else 0
```

### Get most viewed products
```python
from django.db.models import Count

popular = EventLog.objects.filter(
    event_type='product_view'
).values('product__name').annotate(
    views=Count('id')
).order_by('-views')[:10]
```

### Get user's event history
```python
EventLog.objects.filter(
    user_profile__user=request.user
).select_related('product', 'user_profile').order_by('-timestamp')
```

---

## 🎛️ Admin Interface

```
Django Admin: /admin/products/eventlog/
```

**Features**:
- ✓ View all events with timestamps
- ✓ Filter by event_type
- ✓ Search by product name or username
- ✓ Color-coded display:
  - 🔵 Blue: product_view
  - 🟢 Green: rec_clicked, rec_purchased
  - 🔴 Red: review_submit
  - 🟠 Orange: other events

---

## 🚀 Key Differences: Before vs After

### Before (RecommendationLog)
```python
# Could fail with MultipleObjectsReturned ❌
try:
    log, created = RecommendationLog.objects.get_or_create(
        user_profile=user_profile,
        recommended_product=product,
        recommendation_type='personalized',
        defaults={'score': 0.95}
    )
    if not created:
        log.score = 0.95
        log.save()
except RecommendationLog.MultipleObjectsReturned:
    # Error! Multiple records found
    pass
```

### After (EventLog)
```python
# Simple, reliable ✅
EventLog.objects.create(
    user_profile=user_profile,
    product=product,
    event_type='rec_shown',
    metadata={'score': 0.95}
)
```

---

## 📈 Benefits

| Aspect | Benefit |
|--------|---------|
| **Simplicity** | `.create()` instead of `.get_or_create()` |
| **Reliability** | No MultipleObjectsReturned errors |
| **Flexibility** | JSON metadata for any context |
| **Coverage** | Track ANY event, not just recommendations |
| **History** | Keep duplicate events for comprehensive data |
| **Analytics** | Rich data for user behavior analysis |
| **Scalability** | Easy to add new event types |

---

## 🎓 For Your Thesis

**Section**: Architecture / Event Tracking

**Can write**:
> "The system implements EventLog model for comprehensive event tracking. Every user interaction—including product views, clicks, reviews, recommendations, and purchases—is logged with timestamp and flexible metadata. This approach enables detailed user behavior analysis and supports future machine learning applications for recommendation optimization."

**Figure Caption**:
> "EventLog tracks 12+ event types across product, recommendation, search, and authentication interactions, enabling comprehensive user behavior analysis."

---

## ✅ Checklist

- ✅ EventLog model created
- ✅ RecommendationLog model deleted
- ✅ All views updated
- ✅ Admin interface working
- ✅ Migration applied
- ✅ No errors
- ✅ Production ready

---

## 📞 Quick Links

| Resource | Location |
|----------|----------|
| **Model** | `products/models.py` (line ~611) |
| **Admin** | `products/admin.py` (line ~623) |
| **Views** | `products/views.py` (multiple places) |
| **Migration** | `products/migrations/0010_*.py` |
| **Docs** | `docs/EVENTLOG_*.md` |
| **Thesis** | `docs/THESIS_WEBSITE_IMPLEMENTATION.md` |

---

**Last Updated**: January 21, 2026  
**Status**: ✅ Production Ready

