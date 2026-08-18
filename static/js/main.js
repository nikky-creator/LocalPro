document.addEventListener('DOMContentLoaded', function () {

  /* Sticky navbar: solid on inner pages, transparent-over-hero on home ---*/
  var navbar = document.querySelector('.navbar-lp');
  var hasDarkHero = document.body.classList.contains('has-dark-hero');

  function updateNavbar() {
    if (!navbar) return;
    if (!hasDarkHero || window.scrollY > 40) {
      navbar.classList.add('is-solid');
    } else {
      navbar.classList.remove('is-solid');
    }
  }
  updateNavbar();
  window.addEventListener('scroll', updateNavbar, { passive: true });

  /* Auto-show + auto-dismiss server-rendered toasts ----------------------*/
  document.querySelectorAll('.toast').forEach(function (el) {
    var toast = new bootstrap.Toast(el, { delay: 5500 });
    toast.show();
  });

  /* Scroll-reveal animation for elements marked .reveal ------------------*/
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.01, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { observer.observe(el); });

    // Safety net: if anything is still hidden shortly after full load (e.g. a
    // slow observer callback, or the page was opened mid-scroll/via anchor),
    // reveal everything so content is never stuck invisible.
    window.addEventListener('load', function () {
      setTimeout(function () {
        document.querySelectorAll('.reveal:not(.is-visible)').forEach(function (el) {
          el.classList.add('is-visible');
        });
      }, 1800);
    });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* Live image preview for file inputs -----------------------------------*/
  document.querySelectorAll('input[type=file][data-preview-target]').forEach(function (input) {
    input.addEventListener('change', function () {
      var target = document.querySelector(input.getAttribute('data-preview-target'));
      if (target && input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) { target.setAttribute('src', e.target.result); };
        reader.readAsDataURL(input.files[0]);
      }
    });
  });

  /* Auto-close mobile navbar collapse after a link is tapped -------------*/
  document.querySelectorAll('.navbar-collapse .nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
      var collapseEl = document.querySelector('.navbar-collapse.show');
      if (collapseEl && window.bootstrap) {
        window.bootstrap.Collapse.getOrCreateInstance(collapseEl).hide();
      }
    });
  });

  /* Simple confirm-before-submit for destructive actions ------------------*/
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!window.confirm(form.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  /* Live password-match hint on registration forms ------------------------*/
  var pw1 = document.getElementById('id_password1');
  var pw2 = document.getElementById('id_password2');
  var hint = document.getElementById('password-match-hint');
  if (pw1 && pw2 && hint) {
    var checkMatch = function () {
      if (!pw2.value) { hint.textContent = ''; return; }
      if (pw1.value === pw2.value) {
        hint.textContent = '✓ Passwords match';
        hint.className = 'form-text text-success';
      } else {
        hint.textContent = '✗ Passwords do not match';
        hint.className = 'form-text text-danger';
      }
    };
    pw1.addEventListener('input', checkMatch);
    pw2.addEventListener('input', checkMatch);
  }

  /* Dark mode toggle -------------------------------------------------------*/
  var themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-bs-theme') || 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-bs-theme', next);
      localStorage.setItem('localpro-theme', next);
    });
  }

  /* Bootstrap tooltips (if any) --------------------------------------------*/
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

});
