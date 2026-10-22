// ── SLIDER ──────────────────────────────────────────
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

let autoSlide = setInterval(() => changeSlide(1), 5000);

document.addEventListener('DOMContentLoaded', function () {
  // ── PAGE LOADER HIDE ──
  const loader = document.querySelector('.page-loader');
  if (loader) {
    setTimeout(() => {
      loader.classList.add('hidden');
      setTimeout(() => loader.remove(), 500);
    }, 400);
  }

  // ── SCROLL EFFECTS FOR NAVBAR ──
  const navbar = document.querySelector('.navbar-main');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // ── REVEAL ON SCROLL ──
  const reveals = document.querySelectorAll('.reveal');
  const revealOnScroll = () => {
    reveals.forEach(el => {
      const rect = el.getBoundingClientRect();
      const isVisible = rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.85;
      if (isVisible) {
        el.classList.add('visible');
      }
    });
  };
  window.addEventListener('scroll', revealOnScroll);
  revealOnScroll(); // Trigger once on load

  const slider = document.querySelector('.hero-slider');
  if (slider) {
    slider.addEventListener('mouseenter', () => clearInterval(autoSlide));
    slider.addEventListener('mouseleave', () => { autoSlide = setInterval(() => changeSlide(1), 5000); });
  }

  // ── CARD FORMAT (CHECKOUT) ─────────────────────────────────
  const cardInput = document.querySelector('input[name="card_number"]');
  if (cardInput) {
    cardInput.addEventListener('input', function () {
      let val = this.value.replace(/\D/g, '').substring(0, 16);
      this.value = val.replace(/(.{4})/g, '$1 ').trim();
    });
  }
  const expInput = document.querySelector('input[name="expiry"]');
  if (expInput) {
    expInput.addEventListener('input', function () {
      let val = this.value.replace(/\D/g, '').substring(0, 4);
      if (val.length >= 2) val = val.substring(0, 2) + '/' + val.substring(2);
      this.value = val;
    });
  }
  const cvvInput = document.querySelector('input[name="cvv"]');
  if (cvvInput) {
    cvvInput.addEventListener('input', function () {
      this.value = this.value.replace(/\D/g, '').substring(0, 3);
    });
  }

  // ── AUTO DISMISS ALERTS ─────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'all 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });
});