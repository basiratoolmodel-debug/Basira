import { chromium } from '@cloudflare/playwright';

const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
];

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return new Response(null, { headers: corsHeaders() });

    const requestUrl = new URL(request.url);
    if (requestUrl.pathname !== '/api/scrape' || request.method !== 'POST') {
      return json({ success: false, error: 'Not found' }, 404);
    }

    let browser;
    try {
      const body = await request.json();
      const targetUrl = normalizeUrl(body.targetUrl || body.url);
      const parentSelector = String(body.parentSelector || '').trim();
      const itemSelector = String(body.itemSelector || '').trim();
      const fields = Array.isArray(body.fields) ? body.fields.filter(f => f && f.name && f.selector) : [];
      const rowLimit = Math.min(Math.max(Number(body.rowLimit || 50), 1), 300);
      const loadingMethod = body.loadingMethod || 'none';
      const paginationSelector = String(body.paginationSelector || '').trim();
      const loadMoreSelector = String(body.loadMoreSelector || '').trim();

      if (!targetUrl) return json({ success: false, error: 'Missing targetUrl.' }, 400);
      if (!itemSelector) return json({ success: false, error: 'Missing itemSelector.' }, 400);
      if (!fields.length) return json({ success: false, error: 'At least one field is required.' }, 400);

      browser = await chromium.launch(env.MYBROWSER);
      const context = await browser.newContext({
        userAgent: USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)],
        viewport: { width: 1365, height: 900 },
        locale: 'en-US',
        extraHTTPHeaders: {
          'Accept-Language': 'en-US,en;q=0.9',
        },
      });
      const page = await context.newPage();
      await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(1200);

      let allRows = [];

      if (loadingMethod === 'auto-scroll') {
        await autoScroll(page, rowLimit);
        allRows = await collectRows(page, { parentSelector, itemSelector, fields, rowLimit });
      } else if (loadingMethod === 'load-more' && loadMoreSelector) {
        for (let i = 0; i < 8 && allRows.length < rowLimit; i++) {
          allRows = await collectRows(page, { parentSelector, itemSelector, fields, rowLimit });
          const clicked = await clickIfVisible(page, loadMoreSelector);
          if (!clicked) break;
          await page.waitForTimeout(1300);
        }
      } else if (loadingMethod === 'pagination' && paginationSelector) {
        const seen = new Set();
        for (let i = 0; i < 8 && allRows.length < rowLimit; i++) {
          const pageRows = await collectRows(page, { parentSelector, itemSelector, fields, rowLimit });
          for (const row of pageRows) {
            const key = JSON.stringify(row);
            if (!seen.has(key)) { seen.add(key); allRows.push(row); }
            if (allRows.length >= rowLimit) break;
          }
          const clicked = await clickIfVisible(page, paginationSelector);
          if (!clicked) break;
          await page.waitForTimeout(1500);
        }
      } else {
        allRows = await collectRows(page, { parentSelector, itemSelector, fields, rowLimit });
      }

      await browser.close();
      browser = null;

      return json({
        success: true,
        count: allRows.length,
        data: allRows.slice(0, rowLimit),
        meta: { targetUrl, parentSelector, itemSelector, loadingMethod, rowLimit }
      });
    } catch (error) {
      if (browser) { try { await browser.close(); } catch (_) {} }
      return json({ success: false, error: error.message || 'Scraping failed.' }, 500);
    }
  }
};

async function collectRows(page, config) {
  return await page.evaluate(({ parentSelector, itemSelector, fields, rowLimit }) => {
    const absolutize = (value) => {
      if (!value) return '';
      try { return new URL(value, window.location.href).href; } catch { return value; }
    };

    const container = parentSelector ? document.querySelector(parentSelector) : document;
    if (!container) return [];

    const items = Array.from(container.querySelectorAll(itemSelector)).slice(0, rowLimit);
    return items.map((item) => {
      const row = {};
      for (const field of fields) {
        const element = item.querySelector(field.selector);
        if (!element) { row[field.name] = ''; continue; }

        if (field.type === 'image') {
          row[field.name] = absolutize(element.currentSrc || element.src || element.getAttribute('src') || element.getAttribute('data-src') || '');
        } else if (field.type === 'link' || field.type === 'url') {
          row[field.name] = absolutize(element.href || element.getAttribute('href') || '');
        } else {
          row[field.name] = (element.textContent || '').replace(/\s+/g, ' ').trim();
        }
      }
      return row;
    });
  }, config);
}

async function autoScroll(page, rowLimit) {
  for (let i = 0; i < 10; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(700);
  }
}

async function clickIfVisible(page, selector) {
  try {
    const locator = page.locator(selector).first();
    if (await locator.count() === 0) return false;
    await locator.click({ timeout: 3000 });
    return true;
  } catch (_) {
    return false;
  }
}

function normalizeUrl(value) {
  const raw = String(value || '').trim();
  if (!raw) return '';
  if (/^https?:\/\//i.test(raw)) return raw;
  return 'https://' + raw;
}

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders() },
  });
}
