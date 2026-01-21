# -*- coding: utf-8 -*-
"""
Utility functions for recommendation system.

Includes:
- Deduplication of product recommendations from multiple engines
- Event log deduplication (no spam)
- Session-based tracking helpers
"""

from django.db.models import Max
from django.utils import timezone
from datetime import timedelta
from .models import EventLog, Product
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ISSUE 1: PRODUCT DEDUPLICATION
# ============================================================================

def deduplicate_recommendations(recommendations_dict):
    """
    Merge multiple recommendation lists and remove duplicates.
    
    Prevents the same product appearing in multiple recommendation sections.
    
    Example:
        recs = {
            'content_based': [Product1, Product2, Product3],
            'personalized': [Product1, Product4, Product5],
            'collaborative': [Product2, Product6, Product7]
        }
        
        result = deduplicate_recommendations(recs)
        # Returns:
        # {
        #     'content_based': [Product1, Product2, Product3],
        #     'personalized': [Product4, Product5],  # Product1 removed (in content)
        #     'collaborative': [Product6, Product7]  # Product2 removed (in content)
        # }
    
    Args:
        recommendations_dict: {
            'content_based': [Product, ...],
            'personalized': [Product, ...],
            'collaborative': [Product, ...]
        }
    
    Returns:
        deduplicated_dict with duplicates removed from personalized & collaborative
    """
    
    # Get IDs from content-based (keep all)
    content_products = recommendations_dict.get('content_based', [])
    content_ids = {p.id for p in content_products}
    
    # Get IDs from personalized (remove those in content)
    personal_products = [
        p for p in recommendations_dict.get('personalized', [])
        if p.id not in content_ids
    ]
    personal_ids = {p.id for p in personal_products}
    
    # Get IDs from collaborative (remove those in content OR personalized)
    collab_products = [
        p for p in recommendations_dict.get('collaborative', [])
        if p.id not in (content_ids | personal_ids)
    ]
    
    result = {
        'content_based': content_products,
        'personalized': personal_products,
        'collaborative': collab_products
    }
    
    logger.info(
        f"✅ Deduplicated recommendations: "
        f"content={len(content_products)}, "
        f"personal={len(personal_products)}, "
        f"collab={len(collab_products)}"
    )
    
    return result


def get_product_ids_from_recommendations(recommendations_dict):
    """
    Extract all product IDs from recommendation dict (for filtering).
    
    Useful for template context to prevent duplicate rendering.
    
    Example:
        all_ids = get_product_ids_from_recommendations(recs)
        # Returns: {1, 2, 3, 4, 5, 6, 7}
    """
    all_ids = set()
    
    for key in ['content_based', 'personalized', 'collaborative']:
        products = recommendations_dict.get(key, [])
        all_ids.update({p.id for p in products})
    
    return all_ids


# ============================================================================
# ISSUE 2: EVENT LOG DEDUPLICATION
# ============================================================================

def get_deduped_rec_shown_events(user_profile, days=7):
    """
    Get latest rec_shown events per product (no duplicates).
    
    Prevents EventLog spam by returning only the LATEST event for each product.
    
    Example:
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Without dedup: 24 events (same product logged 24 times)
        all_events = EventLog.objects.filter(
            user_profile=user_profile,
            event_type='rec_shown'
        )
        # all_events.count() = 24 (spam!)
        
        # With dedup: 1 event per product
        deduped = get_deduped_rec_shown_events(user_profile)
        # deduped.count() = 5 (clean!)
    
    Args:
        user_profile: UserProfile instance
        days: Look back period (default 7 days)
    
    Returns:
        QuerySet of deduplicated EventLog records
    """
    cutoff = timezone.now() - timedelta(days=days)
    
    # Get MAX(id) for each product (most recent event)
    latest_ids = EventLog.objects.filter(
        user_profile=user_profile,
        event_type='rec_shown',
        timestamp__gte=cutoff
    ).values('product').annotate(
        latest_id=Max('id')
    ).values_list('latest_id', flat=True)
    
    # Fetch those specific events
    deduped_events = EventLog.objects.filter(
        id__in=latest_ids
    ).order_by('-timestamp').select_related('product')
    
    logger.info(
        f"✅ Got {deduped_events.count()} deduplicated rec_shown events "
        f"for user {user_profile.user.username} (lookback: {days} days)"
    )
    
    return deduped_events


def get_deduped_all_events(user_profile, days=30):
    """
    Get ALL event types deduplicated (latest per product).
    
    Useful for user history/profile page.
    
    Args:
        user_profile: UserProfile instance
        days: Look back period (default 30 days)
    
    Returns:
        QuerySet of deduplicated EventLog records (ordered by timestamp)
    """
    cutoff = timezone.now() - timedelta(days=days)
    
    # Get MAX(id) for each (product, event_type) combination
    latest_ids = EventLog.objects.filter(
        user_profile=user_profile,
        timestamp__gte=cutoff
    ).values('product', 'event_type').annotate(
        latest_id=Max('id')
    ).values_list('latest_id', flat=True)
    
    # Fetch those specific events
    deduped_events = EventLog.objects.filter(
        id__in=latest_ids
    ).order_by('-timestamp').select_related('product')
    
    logger.info(
        f"✅ Got {deduped_events.count()} deduplicated events "
        f"for user {user_profile.user.username} (lookback: {days} days)"
    )
    
    return deduped_events


def check_session_logged(user_profile, product, event_type, session_id):
    """
    Check if event already logged in this session (session-based deduplication).
    
    Prevents logging the same event multiple times within same session.
    
    Example:
        session_key = request.session.session_key
        
        already_logged = check_session_logged(
            user_profile=user_profile,
            product=product,
            event_type='rec_shown',
            session_id=session_key
        )
        
        if not already_logged:
            EventLog.objects.create(...)
    
    Args:
        user_profile: UserProfile instance
        product: Product instance
        event_type: String like 'rec_shown', 'product_view', etc.
        session_id: Request session key
    
    Returns:
        Boolean: True if already logged in session, False otherwise
    """
    exists = EventLog.objects.filter(
        user_profile=user_profile,
        product=product,
        event_type=event_type,
        metadata__session_id=session_id
    ).exists()
    
    if exists:
        logger.debug(
            f"⏭️  Skip logging: {event_type} already in session {session_id} "
            f"for {user_profile.user.username} → {product.name}"
        )
    
    return exists


def log_event_if_not_in_session(user_profile, product, event_type, 
                                session_id, metadata=None):
    """
    Log event only if not already in current session.
    
    Combines check + create in one operation.
    
    Example:
        log_event_if_not_in_session(
            user_profile=user_profile,
            product=product,
            event_type='rec_shown',
            session_id=request.session.session_key,
            metadata={
                'recommendation_type': 'personalized',
                'score': 0.95
            }
        )
    
    Args:
        user_profile: UserProfile instance
        product: Product instance
        event_type: String like 'rec_shown'
        session_id: Request session key
        metadata: Optional dict with event context
    
    Returns:
        EventLog instance if created, None if skipped (already logged)
    """
    if metadata is None:
        metadata = {}
    
    # Add session_id to metadata
    metadata['session_id'] = session_id
    
    # Check if already logged
    if check_session_logged(user_profile, product, event_type, session_id):
        return None
    
    # Create event
    event = EventLog.objects.create(
        user_profile=user_profile,
        product=product,
        event_type=event_type,
        metadata=metadata
    )
    
    logger.info(
        f"✅ Logged: {event_type} for {user_profile.user.username} → {product.name}"
    )
    
    return event


def get_event_stats(user_profile, days=30):
    """
    Get event statistics for a user.
    
    Useful for analytics dashboard.
    
    Example:
        stats = get_event_stats(user_profile)
        # Returns:
        # {
        #     'total_events': 150,
        #     'rec_shown_count': 45,
        #     'product_view_count': 60,
        #     'review_submit_count': 3,
        #     'unique_products_viewed': 15,
        #     'last_event': datetime,
        #     'events_by_type': {'rec_shown': 45, 'product_view': 60, ...}
        # }
    """
    cutoff = timezone.now() - timedelta(days=days)
    
    events = EventLog.objects.filter(
        user_profile=user_profile,
        timestamp__gte=cutoff
    )
    
    # Get events by type
    from django.db.models import Count
    events_by_type = dict(
        events.values('event_type').annotate(
            count=Count('id')
        ).values_list('event_type', 'count')
    )
    
    # Get unique products
    unique_products = events.values('product').distinct().count()
    
    stats = {
        'total_events': events.count(),
        'unique_products_viewed': unique_products,
        'last_event': events.order_by('-timestamp').first(),
        'events_by_type': events_by_type,
        'days': days,
    }
    
    # Shorthand counts
    for event_type in ['rec_shown', 'product_view', 'review_submit', 'login']:
        stats[f'{event_type}_count'] = events_by_type.get(event_type, 0)
    
    logger.info(
        f"📊 Event stats for {user_profile.user.username}: "
        f"{stats['total_events']} events, "
        f"{stats['unique_products_viewed']} products (last {days} days)"
    )
    
    return stats


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def bulk_log_recommendations(user_profile, products, recommendation_type, 
                             session_id, event_type='rec_shown'):
    """
    Bulk log multiple recommendations in one session (optimized).
    
    Uses bulk_create for performance instead of individual .create() calls.
    
    Example:
        products = [Product.objects.get(id=1), Product.objects.get(id=2)]
        session_key = request.session.session_key
        
        bulk_log_recommendations(
            user_profile=user_profile,
            products=products,
            recommendation_type='personalized',
            session_id=session_key
        )
    
    Args:
        user_profile: UserProfile instance
        products: List of Product instances
        recommendation_type: 'personalized', 'content-based', 'collaborative'
        session_id: Request session key
        event_type: Default 'rec_shown'
    
    Returns:
        List of created EventLog instances
    """
    logs_to_create = []
    
    for product in products:
        # Skip if already logged in this session
        if check_session_logged(user_profile, product, event_type, session_id):
            continue
        
        logs_to_create.append(
            EventLog(
                user_profile=user_profile,
                product=product,
                event_type=event_type,
                metadata={
                    'recommendation_type': recommendation_type,
                    'session_id': session_id,
                    'score': 0.95
                }
            )
        )
    
    # Bulk create
    if logs_to_create:
        created = EventLog.objects.bulk_create(logs_to_create)
        logger.info(
            f"✅ Bulk logged {len(created)} {event_type} events "
            f"({recommendation_type}) for {user_profile.user.username} "
            f"in session {session_id}"
        )
        return created
    
    logger.info(
        f"⏭️  No new events to log (all already in session {session_id})"
    )
    return []
