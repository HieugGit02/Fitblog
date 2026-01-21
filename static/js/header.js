// Navbar fade effect on scroll
let lastScrollTop = 0;
let isScrolling = false;

window.addEventListener('scroll', function () {
  const header = document.querySelector('header');
  const navContainer = document.querySelector('nav.main-nav.container');
  const navLinks = document.querySelectorAll('nav.main-nav.container a');
  if (!header) return;

  let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const maxScroll = 300; // Header will be fully transparent after scrolling 300px

  // Calculate opacity: 1 (fully visible) to 0 (transparent)
  let opacity = Math.max(0, 1 - (scrollTop / maxScroll));
  
  // Only fade the header, not the nav
  header.style.opacity = opacity;
  
  // Nav container (background) - change alpha from 1 to 0
  if (navContainer) {
    let bgAlpha = Math.max(0, 1 - (scrollTop / maxScroll));
    navContainer.style.backgroundColor = `rgba(255, 255, 255, ${bgAlpha})`;
  }
  
  // Nav links (tags) chỉ hơi mờ - giữ 85% độ sáng tối thiểu
  navLinks.forEach(link => {
    link.style.opacity = Math.max(0.85, 1 - (scrollTop / maxScroll * 0.15));
  });

  // Optional: hide header pointer events when fully transparent
  if (opacity === 0) {
    header.style.pointerEvents = 'none';
  } else {
    header.style.pointerEvents = 'auto';
  }

  lastScrollTop = scrollTop;
});

// Simple nav toggle for small screens
document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('nav-toggle');
  const nav = document.getElementById('main-nav');
  if (!btn || !nav) return;

  btn.addEventListener('click', function () {
    const isOpen = nav.classList.toggle('open');
    btn.classList.toggle('open', isOpen);
    btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    // overlay visibility
    const overlay = document.getElementById('nav-overlay');
    if (overlay) overlay.classList.toggle('visible', isOpen);
  });
  // Close mobile nav when a link is clicked (improves UX)
  nav.querySelectorAll('a').forEach(function(link) {
    link.addEventListener('click', function() {
      if (nav.classList.contains('open')) {
        nav.classList.remove('open');
        btn.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        const overlay = document.getElementById('nav-overlay');
        if (overlay) overlay.classList.remove('visible');
      }
    });
  });
  // Close when clicking overlay
  const overlay = document.getElementById('nav-overlay');
  if (overlay) {
    overlay.addEventListener('click', function() {
      if (nav.classList.contains('open')) {
        nav.classList.remove('open');
        btn.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        overlay.classList.remove('visible');
      }
    });
  }
});

// ============================================================================
// PRODUCT CLICK TRACKING
// ============================================================================
// Track when user clicks on a product link to record "product_click" event
document.addEventListener('DOMContentLoaded', function() {
  // Find all product click links (added data-product-id attribute)
  const productLinks = document.querySelectorAll('a.product-click-link');
  
  productLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const productId = this.getAttribute('data-product-id');
      
      if (productId) {
        // Use sendBeacon when possible (reliable during navigation), fall back to fetch
        const payload = { product_id: productId, event_type: 'click' };
        const url = '/products/api/track-click/';

        try {
          if (navigator.sendBeacon) {
            const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
            navigator.sendBeacon(url, blob);
          } else {
            // Send async tracking request (don't block navigation)
            fetch(url, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
              },
              body: JSON.stringify(payload),
              keepalive: true
            }).catch(() => {
              // Silently fail - don't block user navigation
            });
          }
        } catch (err) {
          // Ignore tracking errors
          console.debug('Product click tracking error', err);
        }
      }
    });
  });
});

// Helper function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
