// ═══════════════════════════════════════════════════════════════════
// BIWEX STORE - SCRIPT PRINCIPAL STYLE MYTEK
// Sliders, Compte à rebours Ventes Flash, AJAX Panier & Favoris
// ═══════════════════════════════════════════════════════════════════

// ── SLIDER HERO ─────────────────────────────────────────────
let currentSlide = 0;
const totalSlides = 3;

function updateSlider() {
  const track = document.getElementById('sliderTrack');
  if (!track) return;
  track.style.transform = `translateX(-${currentSlide * 100}%)`;
  document.querySelectorAll('.dot').forEach((d, i) => {
    d.classList.toggle('active', i === currentSlide);
  });
}

function changeSlide(dir) {
  currentSlide = (currentSlide + dir + totalSlides) % totalSlides;
  updateSlider();
}

function goSlide(n) {
  currentSlide = n;
  updateSlider();
}

let autoSlide = setInterval(() => changeSlide(1), 5500);

// ── MENU MOBILE DRAWER ──────────────────────────────────────
function toggleMobileNav() {
  const drawer = document.getElementById('mobileDrawer');
  const overlay = document.getElementById('drawerOverlay');
  if (drawer && overlay) {
    drawer.classList.toggle('open');
    overlay.classList.toggle('open');
  }
}

// ── FAVORIS / WISHLIST AJAX ─────────────────────────────────
function toggleWishlist(productId, event) {
  if (event) event.preventDefault();
  const btn = event.currentTarget;

  fetch(`/wishlist/toggle/${productId}`, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'added') {
        btn.classList.add('active');
        showToast('Produit ajouté à vos favoris ❤️', 'success');
      } else if (data.status === 'removed') {
        btn.classList.remove('active');
        showToast('Produit retiré de vos favoris', 'info');
      }
    })
    .catch(() => {
      window.location.href = '/login';
    });
}

// ── TOAST NOTIFICATION LÉGÈRE ──────────────────────────────
function showToast(message, type = 'success') {
  let toast = document.getElementById('biwexToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'biwexToast';
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: #1d252c;
      color: #fff;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 13.5px;
      font-weight: 700;
      box-shadow: 0 10px 30px rgba(0,0,0,0.25);
      z-index: 10000;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      border-left: 4px solid #e01e22;
    `;
    document.body.appendChild(toast);
  }

  if (type === 'success') {
    toast.style.borderLeftColor = '#22c55e';
  } else if (type === 'info') {
    toast.style.borderLeftColor = '#0284c7';
  } else {
    toast.style.borderLeftColor = '#e01e22';
  }

  toast.innerHTML = `<i class="bi bi-info-circle-fill"></i> ${message}`;
  toast.style.transform = 'translateX(-50%) translateY(0)';

  setTimeout(() => {
    toast.style.transform = 'translateX(-50%) translateY(100px)';
  }, 3000);
}

// ── COMPTE À REBOURS VENTES FLASH ───────────────────────────
function initFlashCountdown() {
  const daysEl = document.getElementById('days');
  const hoursEl = document.getElementById('hours');
  const minsEl = document.getElementById('mins');
  const secsEl = document.getElementById('secs');

  if (!daysEl || !hoursEl || !minsEl || !secsEl) return;

  // Cible : dans 2 jours, 14 heures, 35 minutes
  const now = new Date().getTime();
  let targetDate = localStorage.getItem('biwex_flash_end');
  
  if (!targetDate || parseInt(targetDate) <= now) {
    targetDate = now + (2 * 24 * 60 * 60 * 1000) + (14 * 60 * 60 * 1000);
    localStorage.setItem('biwex_flash_end', targetDate);
  } else {
    targetDate = parseInt(targetDate);
  }

  function updateTimer() {
    const current = new Date().getTime();
    const distance = targetDate - current;

    if (distance <= 0) {
      daysEl.textContent = '00';
      hoursEl.textContent = '00';
      minsEl.textContent = '00';
      secsEl.textContent = '00';
      return;
    }

    const d = Math.floor(distance / (1000 * 60 * 60 * 24));
    const h = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const m = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const s = Math.floor((distance % (1000 * 60)) / 1000);

    daysEl.textContent = d < 10 ? '0' + d : d;
    hoursEl.textContent = h < 10 ? '0' + h : h;
    minsEl.textContent = m < 10 ? '0' + m : m;
    secsEl.textContent = s < 10 ? '0' + s : s;
  }

  updateTimer();
  setInterval(updateTimer, 1000);
}

// ── AU CHARGEMENT DU DOM ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  
  // Démarrer le compte à rebours Ventes Flash
  initFlashCountdown();

  // Pause au survol du slider
  const slider = document.querySelector('.mytek-hero-slider');
  if (slider) {
    slider.addEventListener('mouseenter', () => clearInterval(autoSlide));
    slider.addEventListener('mouseleave', () => {
      autoSlide = setInterval(() => changeSlide(1), 5500);
    });
  }

  // Bouton Retour en Haut
  const backBtn = document.getElementById('backToTop');
  if (backBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) {
        backBtn.classList.add('show');
      } else {
        backBtn.classList.remove('show');
      }
    });
  }

  // Disparition automatique des alertes flash
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'all 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 4500);
  });

  // Interception AJAX pour l'ajout au panier
  document.querySelectorAll('.add-to-cart-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const url = this.action;
      const formData = new FormData(this);

      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'ok') {
            const badge = document.getElementById('cartBadge');
            if (badge) {
              badge.textContent = data.count;
              badge.classList.add('pulse');
              setTimeout(() => badge.classList.remove('pulse'), 600);
            }
            showToast('Produit ajouté au panier avec succès ! 🛒', 'success');
          } else if (data.status === 'error') {
            showToast(data.message || 'Stock insuffisant.', 'error');
          }
        })
        .catch(() => {
          // Fallback formulaire classique
          this.submit();
        });
    });
  });

});