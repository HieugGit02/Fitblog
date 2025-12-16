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
