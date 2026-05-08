/**
 * Basira Cloud — Cloudflare Worker
 * Scraping engine powered by Cloudflare Browser Rendering (@cloudflare/playwright)
 *
 * Routes:
 *   POST /api/scrape        — run a full scrape job (headless, returns data)
 *   GET  /api/job/:jobId    — retrieve stored job result from KV
 *   DELETE /api/job/:jobId  — delete a job from KV
 *   GET  /api/history       — list recent jobs from KV
 *   DELETE /api/history     — clear all history from KV
 *   OPTIONS *               — CORS preflight
 */

import { chromium } from '@cloudflare/playwright';

// ── CORS headers ───────────────────────────────────────────────────────────
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

// ── USER AGENT POOL ────────────────────────────────────────────────────────
const USER_AGENTS = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
];
const randomUA = () => USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];

// ── MAIN HANDLER ──────────────────────────────────────────────────────────
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const { pathname } = url;

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    // ── POST /api/scrape ──────────────────────────────────────────────
    if (pathname === '/api/scrape' && request.method === 'POST') {
      return handleScrape(request, env);
    }

    // ── GET /api/job/:jobId ───────────────────────────────────────────
    const jobMatch = pathname.match(/^\/api\/job\/([^/]+)$/);
    if (jobMatch && request.method === 'GET') {
      return handleGetJob(jobMatch[1], env);
    }
    if (jobMatch && request.method === 'DELETE') {
      return handleDeleteJob(jobMatch[1], env);
    }

    // ── GET /api/history ──────────────────────────────────────────────
    if (pathname === '/api/history' && request.method === 'GET') {
      return handleHistory(env);
    }
    if (pathname === '/api/history' && request.method === 'DELETE') {
      return handleClearHistory(env);
    }

    return json({ error: 'Not found' }, 404);
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// SCRAPE HANDLER
// ─────────────────────────────────────────────────────────────────────────────
async function handleScrape(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Invalid JSON body' }, 400);
  }

  const {
    url,
    parentSelector,
    itemSelector,
    fields = [],
    loadingMethod = 'auto-scroll',
    paginationSelector = '',
    loadMoreSelector = '',
    rowLimit = 0,
    stealth = true,
    proxy = null,
  } = body;

  if (!url || !parentSelector || !itemSelector || fields.length === 0) {
    return json({ error: 'Missing required fields: url, parentSelector, itemSelector, fields' }, 400);
  }

  const jobId = 'job-' + Date.now();
  const startTime = Date.now();

  let browser;
  try {
    // ── Launch via Cloudflare Browser Rendering ──────────────────────
    const launchOptions = {};
    if (proxy && proxy.host) {
      launchOptions.proxy = {
        server: `${proxy.protocol || 'http'}://${proxy.host}:${proxy.port || 8080}`,
        ...(proxy.username ? { username: proxy.username } : {}),
        ...(proxy.password ? { password: proxy.password } : {}),
      };
    }

    browser = await chromium.launch(env.MYBROWSER, launchOptions);

    const contextOptions = {};
    if (stealth) {
      contextOptions.userAgent = randomUA();
      contextOptions.locale = 'en-US';
      contextOptions.timezoneId = 'America/New_York';
      contextOptions.extraHTTPHeaders = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
      };
    }

    const context = await browser.newContext(contextOptions);

    if (stealth) {
      await context.addInitScript(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        window.chrome = { runtime: {} };
      });
    }

    const page = await context.newPage();
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

    const maxRows = rowLimit && rowLimit > 0 ? rowLimit : Infinity;
    let data = [];
    let validItemIndex = 0;
    let failedItems = 0;

    // ── Loading Strategy ─────────────────────────────────────────────
    if (loadingMethod === 'pagination') {
      const result = await paginationLoad(page, parentSelector, itemSelector, paginationSelector, fields, maxRows);
      data = result.allData;
      validItemIndex = result.totalLoaded;
      failedItems = result.failedItems;
    } else {
      if (loadingMethod === 'auto-scroll') {
        await autoScroll(page, parentSelector, itemSelector, maxRows);
      } else if (loadingMethod === 'load-more') {
        await loadMoreLoad(page, parentSelector, itemSelector, loadMoreSelector, maxRows);
      }

      const items = await page.$$(`${parentSelector} ${itemSelector}`);
      const limited = maxRows < Infinity ? items.slice(0, maxRows) : items;

      for (let i = 0; i < limited.length; i++) {
        const { rowData, hasData } = await extractItemWithRetry(limited[i], fields, page, 3);
        if (hasData) {
          for (const field of fields) {
            data.push({ item_index: validItemIndex, field_name: field.name, value: rowData[field.name] || 'N/A' });
          }
          validItemIndex++;
        } else {
          failedItems++;
        }
      }
    }

    const duration = Math.round((Date.now() - startTime) / 1000);

    const result = { jobId, url, fields, data, meta: { itemsScraped: validItemIndex, failedItems, loadingMethod, duration, timestamp: new Date().toISOString() } };

    // ── Save to KV ───────────────────────────────────────────────────
    if (env.SCRAPER_KV) {
      // Store job data (TTL: 7 days)
      await env.SCRAPER_KV.put(`job:${jobId}`, JSON.stringify(result), { expirationTtl: 604800 });

      // Update history list
      let history = [];
      try { history = JSON.parse(await env.SCRAPER_KV.get('history') || '[]'); } catch {}
      const entry = {
        id: jobId, url,
        hostname: (() => { try { return new URL(url).hostname; } catch { return url; } })(),
        timestamp: new Date().toISOString(),
        rows: validItemIndex, failedItems, fields, loadingMethod, duration,
      };
      history.unshift(entry);
      if (history.length > 50) history.splice(50);
      await env.SCRAPER_KV.put('history', JSON.stringify(history));
    }

    await browser.close();
    return json({ success: true, jobId, itemsScraped: validItemIndex, failedItems, fields, data });

  } catch (error) {
    if (browser) { try { await browser.close(); } catch {} }
    console.error('Scrape error:', error);
    return json({ error: error.message || 'Scrape failed' }, 500);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
async function handleGetJob(jobId, env) {
  if (!env.SCRAPER_KV) return json({ error: 'KV not configured' }, 503);
  const raw = await env.SCRAPER_KV.get(`job:${jobId}`);
  if (!raw) return json({ error: 'Job not found' }, 404);
  return json(JSON.parse(raw));
}

async function handleDeleteJob(jobId, env) {
  if (!env.SCRAPER_KV) return json({ error: 'KV not configured' }, 503);
  await env.SCRAPER_KV.delete(`job:${jobId}`);
  let history = [];
  try { history = JSON.parse(await env.SCRAPER_KV.get('history') || '[]'); } catch {}
  history = history.filter(e => e.id !== jobId);
  await env.SCRAPER_KV.put('history', JSON.stringify(history));
  return json({ success: true });
}

async function handleHistory(env) {
  if (!env.SCRAPER_KV) return json({ history: [] });
  const raw = await env.SCRAPER_KV.get('history');
  return json({ history: raw ? JSON.parse(raw) : [] });
}

async function handleClearHistory(env) {
  if (!env.SCRAPER_KV) return json({ success: true });
  const raw = await env.SCRAPER_KV.get('history');
  const history = raw ? JSON.parse(raw) : [];
  // Delete each job's data
  for (const entry of history) {
    await env.SCRAPER_KV.delete(`job:${entry.id}`);
  }
  await env.SCRAPER_KV.put('history', JSON.stringify([]));
  return json({ success: true });
}

// ─────────────────────────────────────────────────────────────────────────────
// FIELD EXTRACTION
// ─────────────────────────────────────────────────────────────────────────────
async function extractFieldValue(element, field, pageUrl) {
  if (field.type === 'image') {
    const src = await element.getAttribute('src') || await element.getAttribute('data-src') || await element.getAttribute('data-lazy') || '';
    try { return src ? new URL(src, pageUrl).href : ''; } catch { return src; }
  }
  if (field.type === 'link') {
    const href = await element.getAttribute('href') || '';
    try { return href ? new URL(href, pageUrl).href : ''; } catch { return href; }
  }
  if (field.type === 'price') {
    const raw = await element.textContent();
    return (raw || '').replace(/[£$€¥₹,\s]/g, '').trim();
  }
  const className = await element.getAttribute('class') || '';
  const starMatch = className.match(/\b(One|Two|Three|Four|Five)\b/i);
  if (starMatch) {
    const map = { one: '1', two: '2', three: '3', four: '4', five: '5' };
    return map[starMatch[1].toLowerCase()] || starMatch[1];
  }
  return (await element.textContent() || '').trim();
}

async function extractItemWithRetry(item, fields, page, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const rowData = {};
      let hasData = false;
      const pageUrl = page.url();
      for (const field of fields) {
        try {
          const el = await item.$(field.selector);
          if (el) {
            const value = await extractFieldValue(el, field, pageUrl);
            if (value) { rowData[field.name] = value; hasData = true; }
          }
        } catch {}
      }
      return { rowData, hasData };
    } catch {
      if (attempt < maxRetries) await new Promise(r => setTimeout(r, 500 * attempt));
    }
  }
  return { rowData: {}, hasData: false };
}

// ─────────────────────────────────────────────────────────────────────────────
// AUTO-SCROLL
// ─────────────────────────────────────────────────────────────────────────────
async function autoScroll(page, containerSel, itemSel, maxRows = Infinity) {
  await page.evaluate(async ({ containerSel, itemSel, maxRows }) => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    let prev = 0, noNew = 0, iter = 0;
    while (iter++ < 300) {
      const items = document.querySelectorAll(`${containerSel} ${itemSel}`);
      const cur = items.length;
      if (maxRows < Infinity && cur >= maxRows) break;
      if (cur > prev) { noNew = 0; } else { if (++noNew >= 10) break; }
      prev = cur;
      if (items.length) items[items.length - 1].scrollIntoView({ behavior: 'smooth', block: 'center' });
      await sleep(1200);
    }
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, { containerSel, itemSel, maxRows });
}

// ─────────────────────────────────────────────────────────────────────────────
// PAGINATION
// ─────────────────────────────────────────────────────────────────────────────
async function paginationLoad(page, containerSel, itemSel, buttonSel, fields, maxRows = Infinity) {
  const allData = [];
  let validItemIndex = 0;
  let failedItems = 0;
  let pageNum = 0;
  const maxPages = 100;

  while (pageNum < maxPages) {
    pageNum++;
    let itemsFound = false;
    for (let t = 0; t < 3; t++) {
      try { await page.waitForSelector(`${containerSel} ${itemSel}`, { timeout: 10000 }); itemsFound = true; break; }
      catch { await page.waitForTimeout(2000); }
    }
    if (!itemsFound) break;

    const items = await page.$$(`${containerSel} ${itemSel}`);
    for (const item of items) {
      if (validItemIndex >= maxRows) break;
      const { rowData, hasData } = await extractItemWithRetry(item, fields, page, 3);
      if (hasData) {
        for (const field of fields) {
          allData.push({ item_index: validItemIndex, field_name: field.name, value: rowData[field.name] || 'N/A' });
        }
        validItemIndex++;
      } else { failedItems++; }
    }

    if (validItemIndex >= maxRows) break;

    const buttonReady = await page.evaluate((sel) => {
      const btn = document.querySelector(sel);
      if (!btn || btn.disabled || btn.getAttribute('aria-disabled') === 'true' || btn.offsetParent === null) return false;
      return true;
    }, buttonSel);

    if (!buttonReady) break;

    try {
      const navPromise = page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 8000 }).catch(() => null);
      await page.click(buttonSel, { timeout: 5000 });
      await navPromise;
      await page.waitForTimeout(1500);
    } catch {
      break;
    }
  }

  return { totalLoaded: validItemIndex, allData, failedItems };
}

// ─────────────────────────────────────────────────────────────────────────────
// LOAD MORE
// ─────────────────────────────────────────────────────────────────────────────
async function loadMoreLoad(page, containerSel, itemSel, buttonSel, maxRows = Infinity) {
  await page.evaluate(async ({ containerSel, itemSel, buttonSel, maxRows }) => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    let iter = 0;
    while (iter++ < 100) {
      const items = document.querySelectorAll(`${containerSel} ${itemSel}`);
      if (maxRows < Infinity && items.length >= maxRows) break;
      const btn = document.querySelector(buttonSel);
      if (!btn || btn.offsetParent === null) break;
      btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      await sleep(500);
      btn.click();
      await sleep(2000);
    }
  }, { containerSel, itemSel, buttonSel, maxRows });
}
