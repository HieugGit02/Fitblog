# 📚 FITBLOG PRODUCTS API - COMPLETE REFERENCE

**API Base URL**: `http://localhost:8001/api`  
**Status**: ✅ **FULLY FUNCTIONAL**  
**Version**: 1.0  
**Last Updated**: 2025-12-13

---

## 🚀 Quick Start

```bash
# List all products
curl http://localhost:8001/api/products/

# Get product details
curl http://localhost:8001/api/products/1/

# Get recommendations for a product
curl http://localhost:8001/api/products/1/recommendations/

# List categories
curl http://localhost:8001/api/categories/
```

---

## 📋 API ENDPOINTS

### 1. Products

#### List Products
```
GET /api/products/
```

**Query Parameters:**
- `page` (int) - Page number for pagination (default: 1)
- `search` (string) - Search in name, description, ingredients
- `supplement_type` (string) - Filter by type (whey, creatine, preworkout, bcaa, eaa, vitamins)
- `category` (int) - Filter by category ID
- `price__gte` (decimal) - Minimum price
- `price__lte` (decimal) - Maximum price
- `status` (string) - Filter by status (active, inactive)
- `ordering` (string) - Sort by field (price, created_at, -average_rating)

**Response:**
```json
{
  "count": 13,
  "next": "http://localhost:8001/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Whey Protein Gold 100%",
      "slug": "whey-protein-gold-100%",
      "category_name": "Whey Protein",
      "category_icon": "🥚",
      "supplement_type": "whey",
      "price": "450000.00",
      "discount_percent": 0,
      "discounted_price": 450000.0,
      "serving_size": "30g",
      "image": null,
      "average_rating": 4.8,
      "review_count": 4,
      "status": "active",
      "created_at": "2025-12-13T12:38:59.813890+07:00"
    }
  ]
}
```

**Examples:**
```bash
# Search for whey products
curl 'http://localhost:8001/api/products/?search=whey'

# Filter by creatine
curl 'http://localhost:8001/api/products/?supplement_type=creatine'

# Price range filtering
curl 'http://localhost:8001/api/products/?price__gte=200000&price__lte=400000'

# Sort by price (ascending)
curl 'http://localhost:8001/api/products/?ordering=price'

# Sort by price (descending)
curl 'http://localhost:8001/api/products/?ordering=-price'

# Pagination
curl 'http://localhost:8001/api/products/?page=2'
```

---

#### Get Product Detail
```
GET /api/products/{id}/
```

**Parameters:**
- `id` (int, required) - Product ID

**Response:**
```json
{
  "id": 1,
  "name": "Whey Protein Gold 100%",
  "slug": "whey-protein-gold-100%",
  "description": "Whey Protein Gold 100% là sản phẩm whey protein cao cấp...",
  "category_name": "Whey Protein",
  "category_icon": "🥚",
  "supplement_type": "whey",
  "price": "450000.00",
  "discount_percent": 0,
  "discounted_price": 450000.0,
  "serving_size": "30g",
  "protein_per_serving": 25.0,
  "carbs_per_serving": 2.0,
  "fat_per_serving": 1.5,
  "calories_per_serving": 110.0,
  "ingredients": "",
  "flavor": "Chocolate, Vanilla",
  "image": null,
  "average_rating": 4.8,
  "review_count": 4,
  "reviews": [
    {
      "id": 4,
      "author_name": "Gym User",
      "rating": 5,
      "title": "Protein gain nhanh quá!",
      "content": "Uống whey này kết hợp tập gym, tôi thấy muscle gain nhanh hơn trước...",
      "is_verified_purchase": true,
      "helpful_count": 0,
      "created_at": "2025-12-13T12:38:59.954135+07:00"
    }
  ],
  "tags_list": ["muscle-gain", "lean", "high-protein"],
  "goals_list": ["muscle-gain", "strength", "athletic"],
  "status": "active",
  "created_at": "2025-12-13T12:38:59.813890+07:00"
}
```

**Examples:**
```bash
# Get product 1
curl 'http://localhost:8001/api/products/1/'

# Get product 5
curl 'http://localhost:8001/api/products/5/'
```

---

#### Get Product Recommendations
```
GET /api/products/{id}/recommendations/
```

**Parameters:**
- `id` (int, required) - Product ID
- `limit` (int, optional) - Number of recommendations (default: 5)

**Response:**
```json
{
  "count": 3,
  "current_product": {
    "id": 1,
    "name": "Whey Protein Gold 100%",
    "slug": "whey-protein-gold-100%",
    "category_name": "Whey Protein",
    "supplement_type": "whey",
    "price": "450000.00",
    "discounted_price": 450000.0,
    "average_rating": 4.8,
    "review_count": 4
  },
  "recommendations": [
    {
      "id": 2,
      "name": "Whey Protein Isolate Premium",
      "supplement_type": "isolate",
      "price": "550000.00",
      "discounted_price": 495000.0,
      "average_rating": 4.5,
      "review_count": 2
    }
  ],
  "reason": "Content-based: Similar category, supplement type, or fitness goals"
}
```

**Logic:**
- Recommends products from same category OR similar supplement type OR similar fitness goals
- Excludes the current product from recommendations
- Returns products ordered by review count and rating

**Examples:**
```bash
# Get 5 recommendations (default)
curl 'http://localhost:8001/api/products/1/recommendations/'

# Get 3 recommendations
curl 'http://localhost:8001/api/products/1/recommendations/?limit=3'
```

---

### 2. Categories

#### List Categories
```
GET /api/categories/
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 4,
      "name": "BCAA",
      "slug": "bcaa",
      "icon": "🔋",
      "color": "#d1f0e8",
      "product_count": 2
    },
    {
      "id": 2,
      "name": "Creatine",
      "slug": "creatine",
      "icon": "⚡",
      "color": "#7fc0d9",
      "product_count": 2
    }
  ]
}
```

**Examples:**
```bash
# List all categories
curl 'http://localhost:8001/api/categories/'
```

---

### 3. Reviews

#### List Reviews
```
GET /api/reviews/
```

**Query Parameters:**
- `page` (int) - Page number
- `product` (int) - Filter by product ID
- `rating` (int) - Filter by rating (1-5)
- `ordering` (string) - Sort by field (rating, -created_at)

**Response:**
```json
{
  "count": 13,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 4,
      "author_name": "Gym User",
      "rating": 5,
      "title": "Protein gain nhanh quá!",
      "content": "Uống whey này kết hợp tập gym...",
      "is_verified_purchase": true,
      "helpful_count": 0,
      "created_at": "2025-12-13T12:38:59.954135+07:00"
    }
  ]
}
```

**Examples:**
```bash
# List all reviews
curl 'http://localhost:8001/api/reviews/'

# Filter by product
curl 'http://localhost:8001/api/reviews/?product=1'

# Filter by 5-star reviews
curl 'http://localhost:8001/api/reviews/?rating=5'
```

---

#### Create Review
```
POST /api/reviews/
```

**Request Body:**
```json
{
  "product": 1,
  "author_name": "John Doe",
  "author_email": "john@example.com",
  "rating": 5,
  "title": "Excellent product!",
  "content": "This is a great product. Highly recommended!",
  "is_verified_purchase": true
}
```

**Response:** (201 Created)
```json
{
  "id": 14,
  "author_name": "John Doe",
  "rating": 5,
  "title": "Excellent product!",
  "content": "This is a great product. Highly recommended!",
  "is_verified_purchase": true,
  "helpful_count": 0,
  "created_at": "2025-12-13T15:00:00.000000+07:00"
}
```

**Example:**
```bash
# Create a new review
curl -X POST http://localhost:8001/api/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "author_name": "John Doe",
    "author_email": "john@example.com",
    "rating": 5,
    "title": "Excellent product!",
    "content": "This is a great product. Highly recommended!",
    "is_verified_purchase": true
  }'
```

---

## 🔍 Filtering Examples

### Example 1: Find affordable high-protein products
```bash
curl 'http://localhost:8001/api/products/?price__lte=300000&search=protein'
```

### Example 2: Filter by supplement type and price range
```bash
curl 'http://localhost:8001/api/products/?supplement_type=whey&price__gte=400000&price__lte=500000'
```

### Example 3: Get top-rated products
```bash
curl 'http://localhost:8001/api/products/?ordering=-average_rating'
```

### Example 4: Get recently added products
```bash
curl 'http://localhost:8001/api/products/?ordering=-created_at'
```

### Example 5: Get products by category
```bash
curl 'http://localhost:8001/api/products/?category=1'
```

---

## 📊 Response Structure

### Paginated Response
```json
{
  "count": <total_items>,
  "next": "<url_to_next_page_or_null>",
  "previous": "<url_to_previous_page_or_null>",
  "results": [
    { /* item 1 */ },
    { /* item 2 */ }
  ]
}
```

### Single Item Response
```json
{
  "id": <int>,
  "name": <string>,
  "price": <decimal_string>,
  ...
}
```

### Error Response
```json
{
  "detail": "Not found."
}
```

---

## ⚙️ Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - New resource created |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error |

---

## 📈 Pagination

Default page size: **10 items per page**

```bash
# Get page 1 (default)
curl 'http://localhost:8001/api/products/'

# Get page 2
curl 'http://localhost:8001/api/products/?page=2'

# Get page 3
curl 'http://localhost:8001/api/products/?page=3'
```

---

## 🔐 Authentication

Currently **NO AUTHENTICATION REQUIRED**

All endpoints are public. Future versions may require token authentication.

---

## 📝 Data Specifications

### Product Types
- `whey` - Whey protein products
- `isolate` - Whey isolate products
- `concentrate` - Whey concentrate products
- `gainer` - Weight gainer products
- `creatine` - Creatine products
- `preworkout` - Pre-workout products
- `bcaa` - BCAA products
- `eaa` - EAA products
- `vitamins` - Vitamin products

### Supplement Categories
1. Whey Protein (4 products)
2. Creatine (2 products)
3. Pre-workout (2 products)
4. BCAA (2 products)
5. Vitamins (3 products)

### Rating Scale
- 1 star ⭐ - Poor
- 2 stars ⭐⭐ - Fair
- 3 stars ⭐⭐⭐ - Good
- 4 stars ⭐⭐⭐⭐ - Very Good
- 5 stars ⭐⭐⭐⭐⭐ - Excellent

### Fitness Goals
- `muscle-gain` - Building muscle mass
- `strength` - Increasing strength
- `athletic` - Athletic performance
- `weight-loss` - Losing weight
- `recovery` - Post-workout recovery
- `endurance` - Building endurance

---

## 💡 Usage Tips

### Best Practices
1. Always paginate when dealing with large datasets
2. Use search for user input, filtering for known categories
3. Sort by rating for user recommendations
4. Cache results on client side for better performance
5. Handle 404s gracefully

### Performance
- Typical response time: < 100ms
- Products are ordered by creation date (newest first)
- Reviews are filtered for approved content only

### Common Use Cases

#### Shopping Cart
```bash
# Get product details for display
curl 'http://localhost:8001/api/products/{id}/'

# Get recommendations to suggest in cart
curl 'http://localhost:8001/api/products/{id}/recommendations/?limit=3'
```

#### Product Listing
```bash
# Search and filter
curl 'http://localhost:8001/api/products/?search=whey&supplement_type=whey'

# Paginate results
curl 'http://localhost:8001/api/products/?page=1'
```

#### Customer Reviews
```bash
# Get reviews for a product
curl 'http://localhost:8001/api/reviews/?product={id}'

# Submit a new review
curl -X POST http://localhost:8001/api/reviews/ \
  -d '{"product": 1, "author_name": "User", ...}'
```

---

## 🚧 Future Enhancements

- [ ] Authentication & authorization
- [ ] Advanced recommendation engine (ML-based)
- [ ] Personalized recommendations (session-based)
- [ ] Shopping cart API
- [ ] Order management
- [ ] Wishlist API
- [ ] User analytics
- [ ] Rate limiting
- [ ] API versioning

---

## 📞 Support

For issues or questions:
1. Check the examples above
2. Verify product IDs exist (1-13)
3. Check server is running on port 8001
4. Review error messages for hints

---

**API Version**: 1.0  
**Last Updated**: 2025-12-13  
**Status**: ✅ Production Ready
