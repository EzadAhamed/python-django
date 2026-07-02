// ============================================
// ZAVI LUXE — Main JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function () {

  // ---- Navbar scroll effect ----
  const navbar = document.getElementById('navbar');
  const announcementBar = document.querySelector('.announcement-bar');
  window.addEventListener('scroll', function () {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // ---- Mobile menu ----
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileClose = document.getElementById('mobileClose');

  if (hamburger) {
    hamburger.addEventListener('click', () => mobileMenu.classList.add('open'));
  }
  if (mobileClose) {
    mobileClose.addEventListener('click', () => mobileMenu.classList.remove('open'));
  }

  // ---- Auto-dismiss messages ----
  const messages = document.querySelectorAll('.message');
  messages.forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(20px)';
      msg.style.transition = 'all 0.3s ease';
      setTimeout(() => msg.remove(), 300);
    }, 4000);
  });

  // ---- Product detail tabs ----
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const target = this.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      this.classList.add('active');
      const content = document.getElementById(target);
      if (content) content.classList.add('active');
    });
  });

  // ---- Size selector ----
  const sizeBtns = document.querySelectorAll('.size-btn');
  const sizeInput = document.getElementById('selectedSize');

  sizeBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      sizeBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      if (sizeInput) sizeInput.value = this.dataset.size;
    });
  });

  // ---- Quantity control ----
  const qtyInput = document.querySelector('.qty-input');
  const qtyMinus = document.querySelector('.qty-minus');
  const qtyPlus = document.querySelector('.qty-plus');

  if (qtyMinus && qtyPlus && qtyInput) {
    qtyMinus.addEventListener('click', () => {
      const val = parseInt(qtyInput.value);
      if (val > 1) qtyInput.value = val - 1;
    });
    qtyPlus.addEventListener('click', () => {
      qtyInput.value = parseInt(qtyInput.value) + 1;
    });
  }

  // ---- Image gallery ----
  const thumbs = document.querySelectorAll('.thumb-img');
  const mainImg = document.querySelector('.detail-main-image');

  thumbs.forEach(thumb => {
    thumb.addEventListener('click', function () {
      if (mainImg) mainImg.src = this.src;
      thumbs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // ---- Scroll reveal ----
  const reveals = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  reveals.forEach(el => revealObserver.observe(el));

  // ---- Product image hover zoom ----
  const productImgs = document.querySelectorAll('.product-image-wrap');
  productImgs.forEach(wrap => {
    wrap.addEventListener('mousemove', function (e) {
      const rect = this.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      const img = this.querySelector('img');
      if (img) img.style.transformOrigin = `${x}% ${y}%`;
    });
    wrap.addEventListener('mouseleave', function () {
      const img = this.querySelector('img');
      if (img) img.style.transformOrigin = 'center center';
    });
  });

  // ---- Search form (enter key) ----
  const searchInput = document.querySelector('.search-input');
  if (searchInput) {
    searchInput.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        const query = this.value.trim();
        if (query) window.location.href = '/search/?q=' + encodeURIComponent(query);
      }
    });
  }

});
