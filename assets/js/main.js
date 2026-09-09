/* =========================================================
   강담태권도 — main.js
   ========================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. 헤더 스크롤 상태 + 스크롤스파이 ---------- */
  var header = document.getElementById('header');
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.gnb a'));
  var sections = navLinks
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('is-stuck', y > 10);

    var current = null;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].offsetTop - 140 <= y) current = sections[i];
    }
    navLinks.forEach(function (a) {
      a.classList.toggle('is-active', !!current && a.getAttribute('href') === '#' + current.id);
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- 2. 모바일 네비게이션 ---------- */
  var navToggle = document.getElementById('navToggle');
  var gnb = document.getElementById('gnb');

  if (navToggle && gnb) {
    navToggle.addEventListener('click', function () {
      var open = gnb.classList.toggle('is-open');
      navToggle.classList.toggle('is-open', open);
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
    });

    gnb.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        gnb.classList.remove('is-open');
        navToggle.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && gnb.classList.contains('is-open')) {
        gnb.classList.remove('is-open');
        navToggle.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.focus();
      }
    });
  }

  /* ---------- 3. 스크롤 등장 애니메이션 ---------- */
  var revealEls = document.querySelectorAll('[data-reveal]');

  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealEls.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, idx) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var siblings = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : idx;
        el.style.transitionDelay = Math.min(siblings, 5) * 80 + 'ms';
        el.classList.add('is-in');
        io.unobserve(el);
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -60px 0px' });

    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 4. 숫자 카운트업 ---------- */
  var counters = document.querySelectorAll('[data-count]');

  function runCount(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    var suffix = el.getAttribute('data-suffix') || '';
    if (reduceMotion) { el.textContent = target.toLocaleString('ko-KR') + suffix; return; }

    var start = null;
    var duration = 1400;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased).toLocaleString('ko-KR') + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        runCount(entry.target);
        cio.unobserve(entry.target);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(runCount);
  }

  /* ---------- 5. FAQ 아코디언 ---------- */
  var faqItems = document.querySelectorAll('.faq__item');

  faqItems.forEach(function (item) {
    var q = item.querySelector('.faq__q');
    var a = item.querySelector('.faq__a');
    if (!q || !a) return;

    q.addEventListener('click', function () {
      var willOpen = !item.classList.contains('is-open');

      faqItems.forEach(function (other) {
        other.classList.remove('is-open');
        var oa = other.querySelector('.faq__a');
        var oq = other.querySelector('.faq__q');
        if (oa) oa.style.maxHeight = null;
        if (oq) oq.setAttribute('aria-expanded', 'false');
      });

      if (willOpen) {
        item.classList.add('is-open');
        a.style.maxHeight = a.scrollHeight + 'px';
        q.setAttribute('aria-expanded', 'true');
      }
    });
  });

  window.addEventListener('resize', function () {
    document.querySelectorAll('.faq__item.is-open .faq__a').forEach(function (a) {
      a.style.maxHeight = a.scrollHeight + 'px';
    });
  });

  /* ---------- 6. 전화번호 (PC에서는 번호 복사) ---------- */
  var telLinks = document.querySelectorAll('.js-tel');
  var canDial = window.matchMedia('(hover: none) and (pointer: coarse)').matches;
  var toast;

  function showToast(text) {
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast';
      toast.setAttribute('role', 'status');
      document.body.appendChild(toast);
    }
    toast.textContent = text;
    toast.classList.add('is-on');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(function () { toast.classList.remove('is-on'); }, 2400);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // file:// 이나 http 환경 폴백
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:-1000px;opacity:0;';
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      ok ? resolve() : reject();
    });
  }

  telLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (canDial) return;               // 휴대폰·태블릿은 그대로 전화 연결
      e.preventDefault();
      var num = link.getAttribute('data-tel') || link.getAttribute('href').replace('tel:', '');
      copyText(num).then(function () {
        showToast('전화번호가 복사되었습니다  ' + num);
      }, function () {
        showToast('전화번호  ' + num);
      });
    });
  });

  /* ---------- 7. 맨 위로 ---------- */
  var toTop = document.getElementById('toTop');
  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }
})();
