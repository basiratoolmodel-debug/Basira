# basira_scraper — Cloudflare Worker

هذا الفولدر هو الـ backend للسكرابر. يُنشر مرة واحدة فقط.

---

## خطوات النشر (مرة واحدة فقط)

```bash
cd basira_scraper

# تثبيت wrangler
npm install

# تسجيل الدخول
npx wrangler login

# إنشاء KV للتخزين
npx wrangler kv namespace create SCRAPER_KV
# انسخ الـ id اللي يظهر

npx wrangler kv namespace create SCRAPER_KV --preview
# انسخ الـ preview_id
```

**عدّل `wrangler.toml`** — ضع الـ IDs:
```toml
[[kv_namespaces]]
binding = "SCRAPER_KV"
id = "ضع_الـ_id_هنا"
preview_id = "ضع_الـ_preview_id_هنا"
```

**انشر:**
```bash
npx wrangler deploy
```

ستحصل على رابط مثل:
```
https://basira-scraper-worker.YOUR_SUBDOMAIN.workers.dev
```

**أخيراً** — افتح `scraper.html` وعدّل هذا السطر:
```js
window.BASIRA_WORKER_URL = 'https://basira-scraper-worker.YOUR_SUBDOMAIN.workers.dev';
```

---

## بعد هذا

- ارفع `scraper.html` لنفس الـ repo في Cloudflare Pages
- افتحه على `yoursite.pages.dev/scraper.html`
- تم ✅
