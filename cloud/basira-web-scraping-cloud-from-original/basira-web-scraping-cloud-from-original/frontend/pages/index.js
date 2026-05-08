import { useEffect, useMemo, useState } from 'react';

const DESIGN_CSS = `
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&family=Noto+Sans+Arabic:wght@300;400;600;700&display=swap');

:root{
  --bg:#f0f4f8;--surface:#ffffff;--surface-2:#f8fafc;
  --surface-glass:rgba(255,255,255,0.88);
  --accent:#0ea5e9;--accent-2:#6366f1;
  --accent-dim:rgba(14,165,233,0.10);--accent-glow:rgba(14,165,233,0.20);
  --success:#22c55e;--warning:#f59e0b;--danger:#ef4444;--purple:#8b5cf6;
  --text:#0f172a;--text-2:#334155;--text-dim:#64748b;--text-muted:#94a3b8;
  --border:#e2e8f0;--border-2:#cbd5e1;
  --mono:'JetBrains Mono',monospace;
  --sans:'Plus Jakarta Sans','Noto Sans Arabic',system-ui,sans-serif;
  --r:14px;--r-lg:20px;--r-xl:26px;
  --shadow:0 1px 3px rgba(0,0,0,.06),0 2px 8px rgba(0,0,0,.04);
  --shadow-md:0 4px 16px rgba(0,0,0,.07);
  --shadow-lg:0 12px 40px rgba(0,0,0,.10);
  --tr:.18s cubic-bezier(.4,0,.2,1);
}
[data-theme="dark"]{
  --bg:#080e1a;--surface:#111827;--surface-2:#1a2332;
  --surface-glass:rgba(17,24,39,0.92);
  --accent:#38bdf8;--accent-dim:rgba(56,189,248,0.12);--accent-glow:rgba(56,189,248,0.22);
  --text:#f1f5f9;--text-2:#e2e8f0;--text-dim:#94a3b8;--text-muted:#64748b;
  --border:rgba(255,255,255,0.07);--border-2:rgba(255,255,255,0.13);
  --shadow:0 1px 3px rgba(0,0,0,.3),0 2px 8px rgba(0,0,0,.2);
  --shadow-md:0 4px 20px rgba(0,0,0,.35);--shadow-lg:0 12px 48px rgba(0,0,0,.45);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;outline:none;}
html{font-size:16px;-webkit-font-smoothing:antialiased;}
body{font-family:var(--sans);background:var(--bg);color:var(--text);transition:background var(--tr),color var(--tr);}

/* Nav */
.bs-nav{
  height:64px;display:flex;align-items:center;justify-content:space-between;
  padding:0 5%;background:var(--surface-glass);backdrop-filter:blur(28px);
  border-bottom:1px solid var(--border);position:sticky;top:0;z-index:1000;gap:16px;
}
.bs-brand{font-weight:800;color:var(--accent);font-size:1.45rem;letter-spacing:-1px;font-family:var(--mono);}
[dir="rtl"] .bs-brand{font-size:1.55rem;letter-spacing:0;font-family:'Noto Sans Arabic',var(--sans);}
.bs-nav-actions{display:flex;align-items:center;gap:8px;}
.bs-icon-btn{
  width:36px;height:36px;border-radius:10px;border:1px solid var(--border);
  background:transparent;color:var(--text-dim);cursor:pointer;
  display:flex;align-items:center;justify-content:center;transition:var(--tr);
  font-size:15px;
}
.bs-icon-btn:hover{background:var(--accent-dim);color:var(--accent);border-color:var(--accent);}

/* Page */
.bs-page{min-height:calc(100vh - 64px);padding:36px 5% 48px;display:flex;flex-direction:column;gap:24px;}

/* Cards */
.bs-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:24px 28px;box-shadow:var(--shadow);
}

/* Buttons */
.bs-btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  padding:11px 22px;border-radius:var(--r);font-family:var(--sans);
  font-weight:700;font-size:.9rem;cursor:pointer;
  border:1.5px solid transparent;transition:var(--tr);white-space:nowrap;
}
.bs-btn-primary{background:var(--accent);color:#fff;border-color:var(--accent);}
.bs-btn-primary:hover{filter:brightness(1.08);}
.bs-btn-primary:active{transform:scale(.98);}
.bs-btn-ghost{background:var(--surface-2);border-color:var(--border-2);color:var(--text-dim);}
.bs-btn-ghost:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim);}
.bs-btn-full{width:100%;}

/* Inputs */
.bs-input{
  width:100%;padding:12px 16px;border-radius:var(--r);
  background:var(--surface-2);border:1.5px solid var(--border);
  color:var(--text);font-family:var(--sans);font-size:.95rem;transition:var(--tr);
}
.bs-input:focus{border-color:var(--accent);}
.bs-input.error{border-color:var(--danger);}
.bs-input-sm{padding:10px 14px;font-size:.86rem;}

/* Error banner */
.bs-error-banner{
  display:flex;align-items:center;gap:10px;
  padding:11px 16px;background:rgba(239,68,68,.07);
  border:1px solid rgba(239,68,68,.22);border-radius:var(--r);
  font-size:.83rem;color:var(--danger);font-weight:600;
}

/* Toggle */
.bs-toggle{
  width:42px;height:24px;border-radius:99px;cursor:pointer;
  position:relative;transition:background var(--tr);flex-shrink:0;border:none;
}
.bs-toggle-thumb{
  position:absolute;top:3px;width:18px;height:18px;
  border-radius:50%;background:white;transition:left var(--tr);
}

/* Feature cards */
.bs-feat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
.bs-feat-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:18px;box-shadow:var(--shadow);transition:var(--tr);
}
.bs-feat-card:hover{transform:translateY(-3px);box-shadow:var(--shadow-md);border-color:var(--accent);}
.bs-feat-label{font-size:1.1rem;font-weight:800;color:var(--accent);font-family:var(--mono);margin-bottom:4px;}
.bs-feat-desc{font-size:.75rem;color:var(--text-muted);}

/* History */
.bs-history-item{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:16px 18px;
  display:flex;align-items:center;gap:14px;
  transition:var(--tr);box-shadow:var(--shadow);
}
.bs-history-item:hover{border-color:var(--accent);box-shadow:var(--shadow-md);}
.bs-history-icon{
  width:42px;height:42px;border-radius:12px;
  background:var(--accent-dim);border:1px solid var(--border);
  display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;
}
.bs-history-meta{font-size:.75rem;color:var(--text-dim);margin-top:2px;}

/* Sidebar */
.bs-sidebar{
  width:220px;min-width:220px;background:var(--surface);
  border-inline-end:1px solid var(--border);
  padding:20px 16px;display:flex;flex-direction:column;gap:18px;overflow-y:auto;
}
.bs-sidebar-section-title{
  font-size:.65rem;font-weight:800;color:var(--text-muted);
  letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;
}
.bs-stat-row{
  display:flex;justify-content:space-between;align-items:center;
  padding:9px 12px;background:var(--surface-2);
  border-radius:10px;border:1px solid var(--border);
}
.bs-stat-label{font-size:.75rem;color:var(--text-dim);}
.bs-stat-value{font-size:.88rem;font-weight:800;font-family:var(--mono);}
.bs-field-chip{
  padding:8px 12px;background:var(--surface-2);border-radius:10px;
  border:1px solid var(--border);font-size:.78rem;color:var(--text);
  display:flex;align-items:center;gap:8px;
}

/* Results table */
.bs-table-wrap{border-radius:var(--r-lg);border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);}
.bs-table{width:100%;border-collapse:collapse;font-size:.8rem;}
.bs-table th{
  color:var(--accent);text-align:start;padding:11px 14px;
  border-bottom:2px solid var(--border);font-family:var(--mono);font-size:.72rem;
  background:var(--accent-dim);white-space:nowrap;cursor:pointer;user-select:none;
}
.bs-table th:hover{background:var(--accent-glow);}
.bs-table td{padding:10px 14px;border-bottom:1px solid var(--border);vertical-align:middle;}
.bs-table tr:hover td{background:var(--accent-dim);}
.bs-table tr:last-child td{border-bottom:none;}

/* Spinner */
.bs-spinner{
  width:56px;height:56px;border-radius:50%;
  border:3px solid var(--border);border-top-color:var(--accent);
  animation:bs-spin 1s linear infinite;
}
@keyframes bs-spin{to{transform:rotate(360deg)}}
@keyframes bs-pulse{0%,100%{opacity:1}50%{opacity:.5}}

/* Progress bar */
.bs-progress-track{height:6px;background:var(--border);border-radius:99px;overflow:hidden;}
.bs-progress-fill{
  height:100%;border-radius:99px;
  background:linear-gradient(to right,var(--accent),var(--success));
  animation:bs-pulse 2s ease-in-out infinite;
  transition:width .8s ease;
}

/* Status badge */
.bs-badge{
  display:inline-flex;align-items:center;gap:5px;
  padding:3px 10px;border-radius:18px;
  font-size:.66rem;font-weight:800;letter-spacing:.5px;
  background:var(--accent-dim);color:var(--accent);border:1px solid rgba(14,165,233,.2);
}

/* Advanced panel */
.bs-advanced-panel{
  margin-top:14px;display:flex;flex-direction:column;gap:10px;
  padding:16px;background:var(--surface-2);border-radius:var(--r-lg);border:1px solid var(--border);
}
.bs-toggle-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 16px;background:var(--surface);border-radius:var(--r);
  border:1.5px solid var(--border);transition:var(--tr);
}
.bs-toggle-row.active{border-color:var(--accent);background:var(--accent-dim);}
.bs-toggle-row-label{font-size:.86rem;font-weight:700;color:var(--text);}
.bs-toggle-row-desc{font-size:.72rem;color:var(--text-dim);margin-top:2px;}

/* Proxy inputs */
.bs-proxy-grid{display:flex;flex-direction:column;gap:8px;margin-top:10px;}
.bs-input-row{display:flex;gap:8px;}
select.bs-input{cursor:pointer;}

/* Section header */
.bs-section-head{
  display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;
}
.bs-section-title{
  font-size:.72rem;font-weight:800;color:var(--text-muted);
  letter-spacing:1.2px;text-transform:uppercase;
}

/* Loading center */
.bs-center{min-height:calc(100vh - 64px);display:flex;flex-direction:column;}
.bs-loading-box{
  flex:1;display:flex;align-items:center;justify-content:center;
}
.bs-loading-inner{text-align:center;max-width:420px;padding:48px 24px;}
.bs-loading-title{font-size:1.3rem;font-weight:800;color:var(--text);margin-bottom:10px;}
.bs-loading-sub{font-size:.86rem;color:var(--text-dim);line-height:1.7;}
.bs-status-card{
  background:var(--surface-2);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:20px;margin-top:24px;text-align:left;
}
.bs-selecting-hint{
  padding:12px 18px;background:var(--accent-dim);
  border:1px solid rgba(14,165,233,.2);border-radius:var(--r);
  color:var(--accent);font-size:.84rem;margin-top:18px;
}

/* Results layout */
.bs-results-layout{display:flex;flex:1;overflow:hidden;height:calc(100vh - 64px);}
.bs-results-main{flex:1;overflow:auto;padding:24px 28px;}

/* Search bar */
.bs-search-row{display:flex;align-items:center;gap:12px;margin-bottom:14px;}
.bs-count-badge{font-size:.75rem;color:var(--text-muted);font-family:var(--mono);flex-shrink:0;}

/* Empty state */
.bs-empty{padding:40px;text-align:center;color:var(--text-muted);font-size:.86rem;}

/* Scrollbar */
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border-2);border-radius:10px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent);}

@media(max-width:640px){
  .bs-feat-grid{grid-template-columns:1fr 1fr;}
  .bs-page{padding:20px 4% 32px;}
}
`;

const FIELD_TYPES = [
  { value: 'text', label: 'Text' },
  { value: 'link', label: 'Link' },
  { value: 'image', label: 'Image' },
  { value: 'price', label: 'Price' },
];

const LOADING_METHODS = [
  { value: 'none', label: 'Single page' },
  { value: 'auto-scroll', label: 'Auto scroll' },
  { value: 'load-more', label: 'Load more button' },
  { value: 'pagination', label: 'Pagination button' },
];

function createDefaultFields() {
  return [
    { name: 'title', selector: '.title', type: 'text' },
    { name: 'price', selector: '.price', type: 'price' },
    { name: 'link', selector: 'a', type: 'link' },
  ];
}

function normalizeUrl(raw) {
  const value = (raw || '').trim();
  if (!value) return '';
  if (/^https?:\/\//i.test(value)) return value;
  return 'https://' + value;
}

function getApiUrl() {
  return process.env.NEXT_PUBLIC_SCRAPER_API_URL || '';
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function csvEscape(value) {
  return '"' + String(value ?? '').replace(/"/g, '""') + '"';
}

export default function Home() {
  const [theme, setTheme] = useState('dark');
  const [lang, setLang] = useState('en');
  const [url, setUrl] = useState('');
  const [parentSelector, setParentSelector] = useState('');
  const [itemSelector, setItemSelector] = useState('');
  const [rowLimit, setRowLimit] = useState('50');
  const [loadingMethod, setLoadingMethod] = useState('none');
  const [paginationSelector, setPaginationSelector] = useState('');
  const [loadMoreSelector, setLoadMoreSelector] = useState('');
  const [fields, setFields] = useState(createDefaultFields);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState(null);
  const [search, setSearch] = useState('');
  const [sortCol, setSortCol] = useState('');
  const [sortDir, setSortDir] = useState('asc');

  const isAR = lang === 'ar';
  const apiUrl = getApiUrl();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('dir', isAR ? 'rtl' : 'ltr');
  }, [theme, isAR]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const prefilled = params.get('url');
    if (prefilled) setUrl(prefilled);
  }, []);

  const hostname = useMemo(() => {
    try { return new URL(normalizeUrl(url)).hostname || 'Target website'; }
    catch { return 'Target website'; }
  }, [url]);

  const visibleRows = useMemo(() => {
    let data = rows.filter(row => {
      if (!search) return true;
      return Object.values(row).some(value => String(value ?? '').toLowerCase().includes(search.toLowerCase()));
    });
    if (sortCol) {
      data = [...data].sort((a, b) => {
        const av = String(a[sortCol] ?? '').toLowerCase();
        const bv = String(b[sortCol] ?? '').toLowerCase();
        const an = parseFloat(av.replace(/[^0-9.-]/g, ''));
        const bn = parseFloat(bv.replace(/[^0-9.-]/g, ''));
        const cmp = !Number.isNaN(an) && !Number.isNaN(bn) ? an - bn : av.localeCompare(bv);
        return sortDir === 'asc' ? cmp : -cmp;
      });
    }
    return data;
  }, [rows, search, sortCol, sortDir]);

  const validFields = fields.filter(field => field.name.trim() && field.selector.trim());

  function updateField(index, key, value) {
    setFields(current => current.map((field, i) => i === index ? { ...field, [key]: value } : field));
  }

  function addField() {
    setFields(current => [...current, { name: '', selector: '', type: 'text' }]);
  }

  function removeField(index) {
    setFields(current => current.filter((_, i) => i !== index));
  }

  async function startScrape() {
    setError('');
    setMeta(null);
    setRows([]);

    const targetUrl = normalizeUrl(url);
    if (!targetUrl) {
      setError(isAR ? 'اكتبي رابط الموقع أولاً.' : 'Enter the website URL first.');
      return;
    }
    if (!itemSelector.trim()) {
      setError(isAR ? 'اكتبي Item Selector.' : 'Enter the item selector.');
      return;
    }
    if (!validFields.length) {
      setError(isAR ? 'أضيفي حقل واحد على الأقل.' : 'Add at least one field.');
      return;
    }
    if (!apiUrl) {
      setError(isAR ? 'رابط API غير مضبوط. أضيفي NEXT_PUBLIC_SCRAPER_API_URL في Cloudflare Pages.' : 'API URL is missing. Set NEXT_PUBLIC_SCRAPER_API_URL in Cloudflare Pages.');
      return;
    }

    setStatus('running');
    try {
      const response = await fetch(apiUrl.replace(/\/$/, '') + '/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          targetUrl,
          parentSelector: parentSelector.trim(),
          itemSelector: itemSelector.trim(),
          rowLimit: Math.max(1, Number(rowLimit || 50)),
          loadingMethod,
          paginationSelector: paginationSelector.trim(),
          loadMoreSelector: loadMoreSelector.trim(),
          fields: validFields,
        }),
      });
      const result = await response.json();
      if (!response.ok || !result.success) throw new Error(result.error || 'Scraping failed.');
      setRows(result.data || []);
      setMeta(result.meta || { count: result.count || 0 });
      setStatus('done');
    } catch (err) {
      setError(err.message || 'Scraping failed.');
      setStatus('error');
    }
  }

  function exportCSV() {
    if (!visibleRows.length) return;
    const headers = Object.keys(visibleRows[0]);
    const csv = [headers.map(csvEscape).join(','), ...visibleRows.map(row => headers.map(header => csvEscape(row[header])).join(','))].join('
');
    downloadBlob(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }), 'basira-scraping-results.csv');
  }

  function exportJSON() {
    if (!visibleRows.length) return;
    downloadBlob(new Blob([JSON.stringify(visibleRows, null, 2)], { type: 'application/json;charset=utf-8' }), 'basira-scraping-results.json');
  }

  function renderCell(field, value) {
    if (!value) return <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>—</span>;
    if (field?.type === 'image') return <a href={value} target="_blank" rel="noreferrer"><img src={value} alt="" style={{ width: 48, height: 48, objectFit: 'cover', borderRadius: 8 }} /></a>;
    if (field?.type === 'link') return <a href={value} target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', textDecoration: 'none', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 280 }}>{String(value).replace(/^https?:\/\//, '')}</a>;
    if (field?.type === 'price') return <span style={{ color: 'var(--success)', fontWeight: 800, fontFamily: 'var(--mono)' }}>{value}</span>;
    return <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block' }}>{value}</span>;
  }

  const headerText = isAR ? {
    subtitle: 'استخرج بيانات منظمة من صفحات الويب عبر Cloudflare، ثم نزّل النتائج على جهازك.',
    url: 'رابط الموقع', parent: 'Parent Selector', item: 'Item Selector', rows: 'عدد الصفوف', fields: 'الحقول', add: 'إضافة حقل', start: 'Start Scraping', csv: 'Download CSV', json: 'Download JSON', results: 'النتائج', config: 'إعدادات الاستخراج', loading: 'جاري الاستخراج من الكلاود...', complete: 'اكتمل الاستخراج', search: 'بحث في النتائج', noResults: 'لا توجد نتائج حتى الآن.', advanced: 'طريقة التحميل', method: 'Loading method', pagination: 'Pagination selector', loadMore: 'Load more selector', name: 'اسم الحقل', selector: 'CSS selector', type: 'النوع', back: 'Back to Basira'
  } : {
    subtitle: 'Extract structured data from websites through Cloudflare, then download the results locally.',
    url: 'Website URL', parent: 'Parent selector', item: 'Item selector', rows: 'Row limit', fields: 'Fields', add: 'Add field', start: 'Start Scraping', csv: 'Download CSV', json: 'Download JSON', results: 'Results', config: 'Scraping configuration', loading: 'Extracting data in the cloud...', complete: 'Extraction complete', search: 'Search results', noResults: 'No results yet.', advanced: 'Loading behavior', method: 'Loading method', pagination: 'Pagination selector', loadMore: 'Load more selector', name: 'Field name', selector: 'CSS selector', type: 'Type', back: 'Back to Basira'
  };

  if (rows.length > 0) return (
    <>
      <style dangerouslySetInnerHTML={{ __html: DESIGN_CSS }} />
      <nav className="bs-nav">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <img src="/basira-logo.png" style={{ width: 32, height: 32, objectFit: 'contain' }} alt="Basira" />
          <span className="bs-brand" style={{ fontSize: '1.1rem' }}>Basira Scraper</span>
          <span style={{ color: 'var(--text-muted)', fontSize: '.75rem' }}>· {hostname}</span>
        </div>
        <div className="bs-nav-actions">
          <button className="bs-btn bs-btn-ghost" onClick={exportCSV} style={{ padding: '8px 14px', fontSize: '.8rem', color: 'var(--success)', borderColor: 'rgba(34,197,94,.25)', background: 'rgba(34,197,94,.07)' }}>{headerText.csv}</button>
          <button className="bs-btn bs-btn-ghost" onClick={exportJSON} style={{ padding: '8px 14px', fontSize: '.8rem' }}>{headerText.json}</button>
          <button className="bs-btn bs-btn-ghost" onClick={() => setRows([])} style={{ padding: '8px 14px', fontSize: '.8rem' }}>{headerText.start}</button>
        </div>
      </nav>

      <div className="bs-results-layout">
        <aside className="bs-sidebar">
          <div style={{ background: 'rgba(34,197,94,.08)', border: '1px solid rgba(34,197,94,.2)', borderRadius: 12, padding: '14px', textAlign: 'center' }}>
            <div style={{ fontSize: '.72rem', fontWeight: 800, color: 'var(--success)', letterSpacing: '.5px' }}>{headerText.complete}</div>
          </div>
          <div>
            <div className="bs-sidebar-section-title">Summary</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <div className="bs-stat-row"><span className="bs-stat-label">Rows</span><span className="bs-stat-value" style={{ color: 'var(--accent)' }}>{visibleRows.length}</span></div>
              <div className="bs-stat-row"><span className="bs-stat-label">Fields</span><span className="bs-stat-value" style={{ color: 'var(--purple)' }}>{validFields.length}</span></div>
              <div className="bs-stat-row"><span className="bs-stat-label">Method</span><span className="bs-stat-value" style={{ color: 'var(--success)', fontSize: '.72rem' }}>{loadingMethod}</span></div>
            </div>
          </div>
          <div>
            <div className="bs-sidebar-section-title">Fields</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              {validFields.map((f, i) => <div key={i} className="bs-field-chip"><span>{f.type}</span>{f.name}</div>)}
            </div>
          </div>
          <div style={{ marginTop: 'auto' }}>
            <div className="bs-sidebar-section-title">Export</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
              <button className="bs-btn bs-btn-primary bs-btn-full" onClick={exportCSV}>{headerText.csv}</button>
              <button className="bs-btn bs-btn-ghost bs-btn-full" onClick={exportJSON}>{headerText.json}</button>
            </div>
          </div>
        </aside>

        <main className="bs-results-main">
          <div className="bs-search-row">
            <input className="bs-input bs-input-sm" type="text" placeholder={headerText.search} value={search} onChange={e => setSearch(e.target.value)} style={{ direction: 'ltr' }} />
            <span className="bs-count-badge">{visibleRows.length} / {rows.length}</span>
          </div>
          <div className="bs-table-wrap">
            <table className="bs-table">
              <thead>
                <tr>
                  <th>#</th>
                  {validFields.map((f, i) => <th key={i} onClick={() => { setSortCol(f.name); setSortDir(sortCol === f.name && sortDir === 'asc' ? 'desc' : 'asc'); }}>{f.name} {sortCol === f.name ? (sortDir === 'asc' ? '↑' : '↓') : '↕'}</th>)}
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((row, ri) => <tr key={ri}><td style={{ color: 'var(--text-muted)', fontFamily: 'var(--mono)', fontSize: '.72rem' }}>{ri + 1}</td>{validFields.map((f, fi) => <td key={fi} style={{ maxWidth: 260 }}>{renderCell(f, row[f.name])}</td>)}</tr>)}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </>
  );

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: DESIGN_CSS }} />
      <nav className="bs-nav">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <img src="/basira-logo.png" style={{ width: 34, height: 34, objectFit: 'contain' }} alt="Basira" />
          <span className="bs-brand">Basira Scraper</span>
        </div>
        <div className="bs-nav-actions">
          <button className="bs-icon-btn" onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}>{lang.toUpperCase()}</button>
          <button className="bs-icon-btn" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>{theme === 'dark' ? 'Light' : 'Dark'}</button>
        </div>
      </nav>
      <main className="bs-page">
        <section className="bs-card" style={{ display: 'grid', gridTemplateColumns: '1.2fr .8fr', gap: 24, alignItems: 'center' }}>
          <div>
            <div className="bs-badge" style={{ marginBottom: 14 }}>Cloudflare Web Scraping</div>
            <h1 style={{ fontSize: '2rem', lineHeight: 1.25, marginBottom: 10 }}>Basira Web Scraping</h1>
            <p style={{ color: 'var(--text-dim)', lineHeight: 1.8, fontSize: '.95rem' }}>{headerText.subtitle}</p>
          </div>
          <div className="bs-feat-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="bs-feat-card"><div className="bs-feat-label">01</div><div className="bs-feat-desc">Cloud worker</div></div>
            <div className="bs-feat-card"><div className="bs-feat-label">02</div><div className="bs-feat-desc">Selectors</div></div>
            <div className="bs-feat-card"><div className="bs-feat-label">03</div><div className="bs-feat-desc">CSV JSON</div></div>
            <div className="bs-feat-card"><div className="bs-feat-label">04</div><div className="bs-feat-desc">No local launcher</div></div>
          </div>
        </section>

        <section className="bs-card">
          <div className="bs-section-head"><div className="bs-section-title">{headerText.config}</div></div>
          {error && <div className="bs-error-banner" style={{ marginBottom: 14 }}>{error}</div>}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.8rem', fontWeight: 700 }}>{headerText.url}<input className="bs-input" value={url} onChange={e => setUrl(e.target.value)} placeholder="https://example.com/products" style={{ direction: 'ltr' }} /></label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.8rem', fontWeight: 700 }}>{headerText.rows}<input className="bs-input" value={rowLimit} onChange={e => setRowLimit(e.target.value)} type="number" min="1" max="300" /></label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.8rem', fontWeight: 700 }}>{headerText.parent}<input className="bs-input" value={parentSelector} onChange={e => setParentSelector(e.target.value)} placeholder=".products" style={{ direction: 'ltr' }} /></label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.8rem', fontWeight: 700 }}>{headerText.item}<input className="bs-input" value={itemSelector} onChange={e => setItemSelector(e.target.value)} placeholder=".product-card" style={{ direction: 'ltr' }} /></label>
          </div>

          <div className="bs-advanced-panel">
            <div className="bs-section-title">{headerText.advanced}</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10 }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.8rem', fontWeight: 700 }}>{headerText.method}<select className="bs-input" value={loadingMethod} onChange={e => setLoadingMethod(e.target.value)}>{LOADING_METHODS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}</select></label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.8rem', fontWeight: 700 }}>{headerText.pagination}<input className="bs-input" value={paginationSelector} onChange={e => setPaginationSelector(e.target.value)} placeholder=".next" style={{ direction: 'ltr' }} /></label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.8rem', fontWeight: 700 }}>{headerText.loadMore}<input className="bs-input" value={loadMoreSelector} onChange={e => setLoadMoreSelector(e.target.value)} placeholder=".load-more" style={{ direction: 'ltr' }} /></label>
            </div>
          </div>
        </section>

        <section className="bs-card">
          <div className="bs-section-head"><div className="bs-section-title">{headerText.fields}</div><button className="bs-btn bs-btn-ghost" onClick={addField} style={{ padding: '8px 14px', fontSize: '.8rem' }}>{headerText.add}</button></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {fields.map((field, index) => <div key={index} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 160px 44px', gap: 8 }}>
              <input className="bs-input bs-input-sm" value={field.name} onChange={e => updateField(index, 'name', e.target.value)} placeholder={headerText.name} />
              <input className="bs-input bs-input-sm" value={field.selector} onChange={e => updateField(index, 'selector', e.target.value)} placeholder={headerText.selector} style={{ direction: 'ltr' }} />
              <select className="bs-input bs-input-sm" value={field.type} onChange={e => updateField(index, 'type', e.target.value)}>{FIELD_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}</select>
              <button className="bs-icon-btn" onClick={() => removeField(index)} disabled={fields.length <= 1}>×</button>
            </div>)}
          </div>
        </section>

        <section className="bs-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
          <div style={{ color: 'var(--text-dim)', fontSize: '.86rem' }}>{status === 'running' ? headerText.loading : hostname}</div>
          <button className="bs-btn bs-btn-primary" onClick={startScrape} disabled={status === 'running'}>{status === 'running' ? headerText.loading : headerText.start}</button>
        </section>
      </main>
    </>
  );
}
