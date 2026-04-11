/**
 * shared.js — Basira Shared UI Controller  v2
 *
 * Changes from v1:
 *  • Scroll progress bar (two-color gradient, fixed at top)
 *  • Theme toggle is now a CSS checkbox switch (#themeToggleInput)
 *  • "Docs" → "Resources" in i18n strings
 *  • Nav-drawer fixed (display:none in CSS; JS only toggles .open)
 *  • Works on auth pages too (no header/footer injection when no placeholders)
 */

(function () {
  "use strict";

  /* ─── i18n Strings ─────────────────────────────────────────────── */
  const STRINGS = {
    ar: {
      "nav.what":       "ما هي بصيرة",
      "nav.features":   "المميزات",
      "nav.start":      "كيف تبدأ",
      "nav.docs":       "المصادر",           /* Resources */
      "nav.login":      "تسجيل الدخول",
      "nav.register":   "إنشاء حساب",
      "footer.tagline": "منصة تحليل البيانات المصممة للسوق السعودي مع التزام كامل بالخصوصية والحوكمة.",
      "footer.col.product":  "المنتج",
      "footer.col.company":  "الشركة",
      "footer.col.legal":    "القانونية",
      "footer.features":     "المميزات",
      "footer.docs":         "المصادر",
      "footer.register":     "ابدأ الآن",
      "footer.login":        "تسجيل الدخول",
      "footer.about":        "من نحن",
      "footer.blog":         "المدونة",
      "footer.careers":      "الوظائف",
      "footer.contact":      "تواصل معنا",
      "footer.privacy":      "الخصوصية",
      "footer.terms":        "الشروط",
      "footer.security":     "الأمان",
      "footer.compliance":   "الامتثال",
      "footer.copy":         "© 2026 بصيرة. جميع الحقوق محفوظة",
    },
    en: {
      "nav.what":       "What is Basira",
      "nav.features":   "Features",
      "nav.start":      "Get Started",
      "nav.docs":       "Resources",          /* "Docs" renamed to "Resources" */
      "nav.login":      "Sign in",
      "nav.register":   "Create account",
      "footer.tagline": "A data analytics platform built for Saudi Arabia, with full commitment to privacy and governance.",
      "footer.col.product":  "Product",
      "footer.col.company":  "Company",
      "footer.col.legal":    "Legal",
      "footer.features":     "Features",
      "footer.docs":         "Resources",
      "footer.register":     "Get started",
      "footer.login":        "Sign in",
      "footer.about":        "About us",
      "footer.blog":         "Blog",
      "footer.careers":      "Careers",
      "footer.contact":      "Contact",
      "footer.privacy":      "Privacy",
      "footer.terms":        "Terms",
      "footer.security":     "Security",
      "footer.compliance":   "Compliance",
      "footer.copy":         "© 2026 Basira. All rights reserved.",
    }
  };

  /* ─── State ─────────────────────────────────────────────────────── */
  let currentLang  = localStorage.getItem("basira_lang")  || "ar";
  let currentTheme = localStorage.getItem("basira_theme") || "light";

  /* ─── Helpers ────────────────────────────────────────────────────── */
  const $  = (id)  => document.getElementById(id);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ─── Scroll Progress Bar ────────────────────────────────────────── */
  function createScrollProgress() {
    if ($("scrollProgress")) return;  // already exists
    const bar = document.createElement("div");
    bar.id = "scrollProgress";
    document.body.insertAdjacentElement("afterbegin", bar);

    function update() {
      const scrollTop  = window.scrollY;
      const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
      bar.style.width  = pct + "%";
    }

    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  /* ─── Apply Language ─────────────────────────────────────────────── */
  function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem("basira_lang", lang);

    const html = document.documentElement;
    html.setAttribute("lang",      lang);
    html.setAttribute("dir",       lang === "ar" ? "rtl" : "ltr");
    html.setAttribute("data-lang", lang);

    const strings = STRINGS[lang] || STRINGS.ar;

    /* Brand text */
    const brandEl = $("navBrandText");
    if (brandEl) brandEl.textContent = lang === "ar" ? "بصيرة" : "BASIRA";

    const footerBrand = $("footerBrandText");
    if (footerBrand) footerBrand.textContent = lang === "ar" ? "بصيرة" : "BASIRA";

    const footerCopy = $("footerCopy");
    if (footerCopy) footerCopy.textContent = strings["footer.copy"];

    /* Lang label (shared header + auth pages) */
    $$("[id='langLabel']").forEach(el => {
      el.textContent = lang === "ar" ? "EN" : "AR";
    });

    /* i18n all data-i18n elements */
    $$("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      if (strings[key] !== undefined) el.textContent = strings[key];
    });

    /* Page-specific hook */
    if (typeof window.__basiraApplyPageI18n === "function") {
      window.__basiraApplyPageI18n(lang, strings);
    }
  }

  /* ─── Apply Theme ────────────────────────────────────────────────── */
  function applyTheme(theme) {
    currentTheme = theme;
    localStorage.setItem("basira_theme", theme);
    document.documentElement.setAttribute("data-theme", theme);

    /* Sync the CSS checkbox switch */
    const toggle = $("themeToggleInput");
    if (toggle) toggle.checked = (theme === "dark");
  }

  /* ─── Inject HTML Fragment ───────────────────────────────────────── */
  async function injectFragment(url, targetSelector, position = "afterbegin") {
    try {
      const res  = await fetch(url);
      if (!res.ok) return;
      const html   = await res.text();
      const target = document.querySelector(targetSelector);
      if (!target) return;
      target.insertAdjacentHTML(position, html);
    } catch (e) {
      console.warn("[shared.js] Could not load fragment:", url, e);
    }
  }

  /* ─── Bind Events ────────────────────────────────────────────────── */
  function bindEvents() {

    /* Theme switch (checkbox) */
    const themeInput = $("themeToggleInput");
    if (themeInput) {
      themeInput.addEventListener("change", () => {
        applyTheme(themeInput.checked ? "dark" : "light");
      });
    }

    /* Language toggle (shared header) */
    const langBtn = $("langToggleBtn");
    if (langBtn) {
      langBtn.addEventListener("click", () => {
        applyLanguage(currentLang === "ar" ? "en" : "ar");
      });
    }

    /* Legacy #langBtn used on auth pages */
    const legacyBtn = $("langBtn");
    if (legacyBtn && legacyBtn !== langBtn) {
      legacyBtn.addEventListener("click", () => {
        applyLanguage(currentLang === "ar" ? "en" : "ar");
      });
    }

    /* Auth-page theme switch */
    const authThemeInput = $("authThemeToggle");
    if (authThemeInput) {
      authThemeInput.addEventListener("change", () => {
        applyTheme(authThemeInput.checked ? "dark" : "light");
        /* keep shared header checkbox in sync if both exist */
        const main = $("themeToggleInput");
        if (main) main.checked = authThemeInput.checked;
      });
    }

    /* Mobile drawer */
    const menuBtn = $("menuToggleBtn");
    const drawer  = $("navDrawer");
    const overlay = $("navOverlay");

    function openDrawer() {
      drawer?.classList.add("open");
      overlay?.classList.add("active");
      menuBtn?.setAttribute("aria-expanded", "true");
    }
    function closeDrawer() {
      drawer?.classList.remove("open");
      overlay?.classList.remove("active");
      menuBtn?.setAttribute("aria-expanded", "false");
    }

    if (menuBtn) {
      menuBtn.addEventListener("click", () => {
        drawer?.classList.contains("open") ? closeDrawer() : openDrawer();
      });
    }
    overlay?.addEventListener("click", closeDrawer);
    drawer?.querySelectorAll("a").forEach(a => a.addEventListener("click", closeDrawer));

    /* Active nav link */
    const currentPath = window.location.pathname.split("/").pop() || "index.html";
    $$(".nav-links__item").forEach(link => {
      const href = (link.getAttribute("href") || "").split("#")[0].split("/").pop();
      if (href && href === currentPath) link.classList.add("nav-links__item--active");
    });

    /* Sticky header shadow on scroll */
    const header = $("siteHeader");
    if (header) {
      window.addEventListener("scroll", () => {
        header.style.boxShadow = window.scrollY > 10
          ? "var(--shadow-md)"
          : "var(--shadow-sm)";
      }, { passive: true });
    }
  }

  /* ─── Boot ───────────────────────────────────────────────────────── */
  async function boot() {
    /* 1. Apply saved theme immediately — before first paint to avoid flash */
    applyTheme(currentTheme);

    /* 2. Wait for DOM */
    if (document.readyState === "loading") {
      await new Promise(r => document.addEventListener("DOMContentLoaded", r));
    }

    /* 3. Create scroll progress bar */
    createScrollProgress();

    /* 4. Inject shared header / footer if placeholders exist */
    const headerPlaceholder = document.querySelector("#header-placeholder");
    const footerPlaceholder = document.querySelector("#footer-placeholder");

    const src      = document.currentScript?.src || "";
    const basePath = src.substring(0, src.lastIndexOf("/") + 1) || "./";

    if (headerPlaceholder) {
      await injectFragment(basePath + "header_web.html", "#header-placeholder", "afterbegin");
    }
    if (footerPlaceholder) {
      await injectFragment(basePath + "footer_web.html", "#footer-placeholder", "afterbegin");
    }

    /* 5. Apply language (populates all i18n strings, updates dir/lang) */
    applyLanguage(currentLang);

    /* 6. Bind interactive events */
    bindEvents();
  }

  boot();

})();
