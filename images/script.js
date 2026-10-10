/* TildeDev — tistory skin script */
(function () {
  'use strict';

  var root = document.documentElement;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------- Theme ---------- */
  function initTheme() {
    var btn = $('#theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('mono-theme', next); } catch (e) {}
    });
  }

  /* ---------- Drawer ---------- */
  function initDrawer() {
    var drawer = $('#drawer');
    var overlay = $('#drawer-overlay');
    var openBtn = $('#drawer-open');
    var closeBtn = $('#drawer-close');
    if (!drawer || !openBtn) return;

    function open() {
      overlay.hidden = false;
      requestAnimationFrame(function () { document.body.classList.add('drawer-open'); });
      drawer.setAttribute('aria-hidden', 'false');
      openBtn.setAttribute('aria-expanded', 'true');
      closeBtn && closeBtn.focus();
    }
    function close() {
      document.body.classList.remove('drawer-open');
      drawer.setAttribute('aria-hidden', 'true');
      openBtn.setAttribute('aria-expanded', 'false');
      setTimeout(function () { overlay.hidden = true; }, 200);
    }
    function isOpen() { return document.body.classList.contains('drawer-open'); }

    openBtn.addEventListener('click', open);
    closeBtn && closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', close);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) { close(); openBtn.focus(); return; }
      // '/' 로 검색 열기 (입력 중이면 무시)
      var tag = (e.target.tagName || '').toLowerCase();
      if (e.key === '/' && tag !== 'input' && tag !== 'textarea' && !e.target.isContentEditable) {
        var input = $('.search-box input', drawer);
        if (!input) return;
        e.preventDefault();
        open();
        setTimeout(function () { input.focus(); }, 50);
      }
    });
  }

  /* ---------- Code block ---------- */
  var LANG_ALIAS = { js: 'javascript', ts: 'typescript', py: 'python', sh: 'bash', shell: 'bash', yml: 'yaml', kt: 'kotlin', html: 'xml' };
  var LANG_LABEL = { javascript: 'JavaScript', typescript: 'TypeScript', python: 'Python', java: 'Java', kotlin: 'Kotlin', bash: 'Shell', sql: 'SQL', json: 'JSON', yaml: 'YAML', xml: 'HTML', css: 'CSS', go: 'Go', rust: 'Rust', cpp: 'C++', c: 'C', csharp: 'C#', plaintext: 'Text' };

  function detectLang(pre, code) {
    var lang = pre.getAttribute('data-ke-language') || '';
    if (!lang) {
      var m = ((code && code.className) || '').match(/(?:language|lang)-([\w#+-]+)/);
      lang = m ? m[1] : (pre.classList[0] || '');
    }
    lang = lang.toLowerCase();
    return LANG_ALIAS[lang] || lang;
  }

  function initCodeBlocks() {
    var body = $('#post-body');
    if (!body) return;

    $$('pre', body).forEach(function (pre) {
      if (pre.closest('.code-block')) return;
      var code = $('code', pre);
      if (!code) {
        code = document.createElement('code');
        code.textContent = pre.textContent;
        pre.textContent = '';
        pre.appendChild(code);
      }

      var lang = detectLang(pre, code);
      var hljs = window.hljs;
      if (hljs && !code.classList.contains('hljs')) {
        if (lang && lang !== 'plaintext' && hljs.getLanguage(lang)) {
          code.classList.add('language-' + lang);
          hljs.highlightElement(code);
        } else if (!lang) {
          var res = hljs.highlightAuto(code.textContent);
          if (res.relevance > 5) { code.innerHTML = res.value; code.classList.add('hljs'); lang = res.language; }
        }
      }

      var wrap = document.createElement('div');
      wrap.className = 'code-block';
      var head = document.createElement('div');
      head.className = 'code-head';
      var label = document.createElement('span');
      label.textContent = LANG_LABEL[lang] || lang || 'code';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'code-copy';
      btn.textContent = 'Copy';
      btn.addEventListener('click', function () {
        copyText(code.innerText).then(function () {
          btn.textContent = 'Copied!';
          btn.classList.add('copied');
          setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
        });
      });
      head.appendChild(label);
      head.appendChild(btn);

      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(head);
      wrap.appendChild(pre);
    });
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta);
      resolve();
    });
  }

  /* ---------- Table: 넓은 표만 가로 스크롤 ---------- */
  function initTables() {
    var body = $('#post-body');
    if (!body) return;
    $$('table', body).forEach(function (table) {
      if (table.closest('.another_category') || table.parentNode.classList.contains('table-wrap')) return;
      var wrap = document.createElement('div');
      wrap.className = 'table-wrap';
      table.parentNode.insertBefore(wrap, table);
      wrap.appendChild(table);
    });
  }

  /* ---------- TOC ---------- */
  function initToc() {
    var body = $('#post-body');
    var toc = $('#toc');
    var list = $('#toc-list');
    if (!body || !toc || !list) return;

    // 티스토리가 본문 끝에 자동으로 붙이는 '카테고리의 다른 글' 제목은 제외
    var heads = $$('h2, h3, h4', body).filter(function (h) {
      return h.textContent.trim() && !h.closest('.another_category');
    });
    if (heads.length < 2) return;

    var links = heads.map(function (h, i) {
      if (!h.id) h.id = 'h-' + (i + 1);
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent.trim();
      a.className = 'lv-' + h.tagName.charAt(1);
      li.appendChild(a);
      list.appendChild(li);
      return a;
    });
    toc.hidden = false;

    var active = -1;
    function update() {
      var offset = parseInt(getComputedStyle(root).scrollPaddingTop, 10) || 80;
      var idx = 0;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top - offset <= 1) idx = i; else break;
      }
      if (idx === active) return;
      if (active >= 0) links[active].classList.remove('active');
      links[idx].classList.add('active');
      active = idx;
    }
    window.addEventListener('scroll', throttle(update), { passive: true });
    update();
  }

  /* ---------- Scroll: progress / header / to-top ---------- */
  function initScroll() {
    var bar = $('#progress-bar');
    var header = $('#site-header');
    var toTop = $('#to-top');
    var body = $('#post-body');

    function update() {
      var y = window.scrollY;
      header && header.classList.toggle('scrolled', y > 4);
      toTop && toTop.classList.toggle('show', y > 600);
      if (bar && body) {
        var rect = body.getBoundingClientRect();
        var total = rect.height - window.innerHeight * 0.6;
        var p = total > 0 ? Math.min(Math.max(-rect.top / total, 0), 1) : 1;
        bar.style.width = (p * 100) + '%';
      }
    }
    window.addEventListener('scroll', throttle(update), { passive: true });
    window.addEventListener('resize', throttle(update));
    update();

    toTop && toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ---------- Reading time ---------- */
  function initReadingTime() {
    var body = $('#post-body');
    var el = $('#reading-time');
    if (!body || !el) return;
    var chars = body.innerText.replace(/\s+/g, '').length;
    el.textContent = '⏱ ' + Math.max(1, Math.round(chars / 500)) + ' min read';
  }

  /* ---------- Footer year ---------- */
  function initYear() {
    var el = $('#copyright-year');
    if (el) el.textContent = new Date().getFullYear();
  }

  function throttle(fn) {
    var ticking = false;
    return function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { fn(); ticking = false; });
    };
  }

  function init() {
    initTheme();
    initDrawer();
    initCodeBlocks();
    initTables();
    initToc();
    initScroll();
    initReadingTime();
    initYear();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
