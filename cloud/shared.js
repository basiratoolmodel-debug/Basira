/**
 * shared.js — Basira Shared UI Controller
 *
 * Responsibilities:
 *  1. Inject header_web.html and footer_web.html into the page
 *  2. Language toggle: Arabic (RTL) ↔ English (LTR) + brand text swap
 *  3. Theme toggle: Light ↔ Dark
 *  4. Persist preferences in localStorage
 *  5. Mobile drawer open/close
 *  6. Mark active nav link
 */

(function () {
  "use strict";

  /* ─── i18n Strings ───────────────────────────────────────────── */
  const STRINGS = {
    ar: {
      "nav.what":       "ما هي بصيرة",
      "nav.features":   "المميزات",
      "nav.start":      "كيف تبدأ",
      "nav.docs":       "التوثيق",
      "nav.login":      "تسجيل الدخول",
      "nav.register":   "إنشاء حساب",
      "footer.tagline": "منصة تحليل البيانات المصممة للسوق السعودي مع التزام كامل بالخصوصية والحوكمة.",
      "footer.col.product":  "المنتج",
      "footer.col.company":  "الشركة",
      "footer.col.legal":    "القانونية",
      "footer.features":     "المميزات",
      "footer.docs":         "التوثيق",
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
      "nav.docs":       "Docs",
      "nav.login":      "Sign In",
      "nav.register":   "Create Account",
      "footer.tagline": "A data analytics platform built for Saudi Arabia, with full commitment to privacy and governance.",
      "footer.col.product":  "Product",
      "footer.col.company":  "Company",
      "footer.col.legal":    "Legal",
      "footer.features":     "Features",
      "footer.docs":         "Documentation",
      "footer.register":     "Get Started",
      "footer.login":        "Sign In",
      "footer.about":        "About Us",
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

  /* ─── State ─────────────────────────────────────────────────── */
  let currentLang  = localStorage.getItem("basira_lang")  || "ar";
  let currentTheme = localStorage.getItem("basira_theme") || "light";

  /* ─── Helpers ───────────────────────────────────────────────── */
  const $ = (id) => document.getElementById(id);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ─── Apply language to entire document ─────────────────────── */
  function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem("basira_lang", lang);

    const html = document.documentElement;
    html.setAttribute("lang", lang);
    html.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");
    html.setAttribute("data-lang", lang);

    const strings = STRINGS[lang] || STRINGS.ar;

    /* Brand text — Arabic uses Noto Sans Arabic, larger */
    const brandEl = $("navBrandText");
    if (brandEl) {
      brandEl.textContent = lang === "ar" ? "بصيرة" : "BASIRA";
    }

    /* Footer brand text */
    const footerBrand = $("footerBrandText");
    if (footerBrand) {
      footerBrand.textContent = lang === "ar" ? "بصيرة" : "BASIRA";
    }

    /* Footer copyright */
    const footerCopy = $("footerCopy");
    if (footerCopy) {
      footerCopy.textContent = strings["footer.copy"];
    }

    /* Lang button label */
    const labelEl = $("langLabel");
    if (labelEl) labelEl.textContent = lang === "ar" ? "EN" : "AR";

    /* i18n all elements with data-i18n */
    $$("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (strings[key] !== undefined) el.textContent = strings[key];
    });

    /* Page-level i18n hook — pages can override */
    if (typeof window.__basiraApplyPageI18n === "function") {
      window.__basiraApplyPageI18n(lang, strings);
    }
  }

  /* ─── Apply theme ────────────────────────────────────────────── */
  function applyTheme(theme) {
    currentTheme = theme;
    localStorage.setItem("basira_theme", theme);
    document.documentElement.setAttribute("data-theme", theme);

    const icon = $("themeIcon");
    if (icon) icon.textContent = theme === "dark" ? "☀️" : "🌙";
  }

  /* ─── Inject HTML fragment from file ────────────────────────── */
  async function injectFragment(url, targetSelector, position = "afterbegin") {
    try {
      const res = await fetch(url);
      if (!res.ok) return;
      const html = await res.text();
      const target = document.querySelector(targetSelector);
      if (!target) return;
      target.insertAdjacentHTML(position, html);
    } catch (e) {
      /* silently fail — page still works without fragment */
      console.warn("[shared.js] Could not load fragment:", url, e);
    }
  }

  /* ─── Wire up events (after header/footer are injected) ──────── */
  function bindEvents() {
    /* Theme toggle */
    const themeBtn = $("themeToggleBtn");
    if (themeBtn) {
      themeBtn.addEventListener("click", () => {
        applyTheme(currentTheme === "dark" ? "light" : "dark");
      });
    }

    /* Language toggle */
    const langBtn = $("langToggleBtn");
    if (langBtn) {
      langBtn.addEventListener("click", () => {
        applyLanguage(currentLang === "ar" ? "en" : "ar");
      });
    }

    /* Also support legacy #langBtn IDs on standalone pages */
    const legacyLangBtn = $("langBtn");
    if (legacyLangBtn && legacyLangBtn !== langBtn) {
      legacyLangBtn.addEventListener("click", () => {
        applyLanguage(currentLang === "ar" ? "en" : "ar");
        /* sync legacy label if present */
        const ll = $("langLabel");
        if (ll) ll.textContent = currentLang === "ar" ? "EN" : "AR";
      });
    }

    /* Mobile drawer */
    const menuBtn    = $("menuToggleBtn");
    const drawer     = $("navDrawer");
    const overlay    = $("navOverlay");

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

    menuBtn?.addEventListener("click", () => {
      const isOpen = drawer?.classList.contains("open");
      isOpen ? closeDrawer() : openDrawer();
    });
    overlay?.addEventListener("click", closeDrawer);
    drawer?.querySelectorAll("a").forEach((a) => a.addEventListener("click", closeDrawer));

    /* Mark active nav link based on current page */
    const currentPath = window.location.pathname.split("/").pop() || "index.html";
    $$(".nav-links__item, .nav-drawer .nav-links__item").forEach((link) => {
      const href = (link.getAttribute("href") || "").split("#")[0].split("/").pop();
      if (href && href === currentPath) {
        link.classList.add("nav-links__item--active");
      }
    });

    /* Sticky header scroll shadow */
    const header = $("siteHeader");
    if (header) {
      window.addEventListener("scroll", () => {
        header.style.boxShadow = window.scrollY > 10 ? "var(--shadow-md)" : "var(--shadow-sm)";
      }, { passive: true });
    }
  }

  /* ─── Boot ───────────────────────────────────────────────────── */
  async function boot() {
    /* 1. Apply saved preferences immediately (before paint) */
    applyTheme(currentTheme);

    /* 2. Wait for DOM */
    if (document.readyState === "loading") {
      await new Promise((r) => document.addEventListener("DOMContentLoaded", r));
    }

    /* 3. Inject shared header and footer if placeholders exist */
    const hasHeaderPlaceholder  = document.querySelector("#header-placeholder");
    const hasFooterPlaceholder  = document.querySelector("#footer-placeholder");

    /* Resolve base path (works regardless of subdirectory depth) */
    const scriptSrc  = document.currentScript?.src || "";
    const basePath   = scriptSrc.substring(0, scriptSrc.lastIndexOf("/") + 1) || "./";

    if (hasHeaderPlaceholder) {
      await injectFragment(basePath + "header_web.html", "#header-placeholder", "afterbegin");
    }
    if (hasFooterPlaceholder) {
      await injectFragment(basePath + "footer_web.html", "#footer-placeholder", "afterbegin");
    }

    /* 4. Apply language (populates all i18n strings) */
    applyLanguage(currentLang);

    /* 5. Bind interactive events */
    bindEvents();
  }

  /* Kick off */
  boot();

})();
