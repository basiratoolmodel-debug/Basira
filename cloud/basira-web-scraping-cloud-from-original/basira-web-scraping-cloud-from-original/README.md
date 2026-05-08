# Basira Web Scraping Cloud

هذه النسخة مبنية على مشروع `basira-scraper` الأصلي، لكن تم تحويل التشغيل إلى Cloudflare.

## الهيكلة

```text
frontend/  واجهة الويب سكرابينق المبنية من نفس تصميم Basira Scraper
worker/    Cloudflare Worker API الذي يشغل Playwright Browser Run
```

## النشر

### 1. نشر Worker

```bash
cd worker
npm install
npx wrangler login
npm run deploy
```

بعد النشر خذي رابط Worker، مثال:

```text
https://basira-scraper-api.YOUR_SUBDOMAIN.workers.dev
```

### 2. ربط الواجهة بالـ Worker

في Cloudflare Pages، أضيفي Environment Variable:

```text
NEXT_PUBLIC_SCRAPER_API_URL=https://basira-scraper-api.YOUR_SUBDOMAIN.workers.dev
```

### 3. نشر الواجهة

```bash
cd frontend
npm install
npm run build
npx wrangler pages deploy out --project-name basira-web-scraping
```

بعد النشر، زر Web Scraping في مشروع بصيرة يفتح رابط الواجهة، مثل:

```text
https://basira-web-scraping.pages.dev
```

## ملاحظة مهمة

النسخة المحلية القديمة كانت تفتح متصفح مرئي وتستخدم selection overlay. هذا لا يعمل بنفس الطريقة على Cloudflare لأن التشغيل يكون headless داخل Worker. لذلك تم الحفاظ على تصميم المشروع ونظام النتائج والتصدير، مع تحويل الإدخال إلى URL و CSS selectors.
