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
