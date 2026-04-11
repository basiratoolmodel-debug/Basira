/**
 * local-setup.js — Basira On-Premise Setup
 *
 * KEY FIX — Single-tab navigation:
 * ===================================
 * When "Open Basira Now" is clicked, we navigate the CURRENT tab to the
 * local app URL using window.location.href (or location.replace).
 * This closes/replaces the setup page so no multiple tabs accumulate.
 *
 * HOW SESSION WORKS (correct method):
 * =====================================
 * 1. User logs in via Supabase on the cloud site
 * 2. Supabase stores tokens internally (NOT in localStorage)
 * 3. We read tokens via supabaseClient.auth.getSession()
 * 4. When ready, we navigate current tab to:
 *      http://127.0.0.1:5000/login?token=XXX&user_id=YYY
 * 5. Flask sets a real session cookie (same-origin GET = works perfectly)
 * 6. Flask redirects to / — basira_app.html loads authenticated ✓
 *
 * No CORS. No localStorage bridge. No multiple tabs. No cookie issues.
 */

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const LOCAL_BOOTSTRAP = "http://127.0.0.1:5001";
const LOCAL_APP       = "http://127.0.0.1:5000";
const CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew";
const INACTIVITY_MS   = 20 * 60 * 1000; // 20 minutes


// ─── State ──────────────────────────────────────────────────────────────────
let _supaSession    = null;
let startupState    = null;
let inactivityTimer = null;
let dlStartTime     = null;


// ─── DOM helpers ────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const ALL_CARDS = [
  "checkingCard", "notInstalledCard", "pickFolderCard",
  "downloadingCard", "recoveryCard", "subscriptionCard", "readyCard"
];

function showCard(id) {
  ALL_CARDS.forEach(c => { const el = $(c); if (el) el.classList.add("isHidden"); });
  const target = $(id);
  if (target) target.classList.remove("isHidden");
}

function setStep(idx) {
  document.querySelectorAll(".setup-step").forEach((s, i) => {
    s.classList.remove("isActive", "isDone");
    if (i < idx)  s.classList.add("isDone");
    if (i === idx) s.classList.add("isActive");
  });
}

function setProgress(pct, text) {
  const fill  = $("progressFill");
  const pctEl = $("progressPct");
  const txtEl = $("progressText");
  if (fill)  fill.style.width  = `${Math.min(100, pct)}%`;
  if (pctEl) pctEl.textContent = `${Math.round(pct)}%`;
  if (txtEl) txtEl.textContent = text || "";
}

function setDlStatus(text, speed = "") {
  const s  = $("dlStatus");  if (s)  s.textContent = text;
  const sp = $("dlSpeed");   if (sp) sp.textContent = speed;
}

function showNote(type, msg) {
  const el = $("setupNote");
  if (!el) return;
  el.innerHTML  = msg || "";
  el.className  = "note " + (type === "ok" ? "isOk" : "isErr");
}

function showSavedFolder(dir) {
  const box = $("savedFolderBox");
  const lbl = $("savedFolderLabel");
  if (box) box.style.display = "block";
  if (lbl) lbl.textContent = dir;
}

function showChosenFolder(dir) {
  const el = $("chosenFolderDisplay");
  if (!el) return;
  el.classList.remove("isHidden");
  el.textContent = dir;
}


// ─── API calls to local bootstrap (:5001) ───────────────────────────────────
async function apiGet(path, ms = 10000) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  try {
    const r = await fetch(`${LOCAL_BOOTSTRAP}${path}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: c.signal
    });
    clearTimeout(t);
    return r.json();
  } catch (e) {
    clearTimeout(t);
    throw e;
  }
}

async function apiPost(path, body = {}, ms = 180000) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  try {
    const r = await fetch(`${LOCAL_BOOTSTRAP}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: c.signal
    });
    clearTimeout(t);
    return r.json();
  } catch (e) {
    clearTimeout(t);
    throw e;
  }
}

async function isBootstrapReachable() {
  try {
    const c = new AbortController();
    setTimeout(() => c.abort(), 3000);
    const r = await fetch(`${LOCAL_BOOTSTRAP}/health`, { signal: c.signal });
    return r.ok;
  } catch {
    return false;
  }
}


// ─── Supabase session ────────────────────────────────────────────────────────
async function loadSupabaseSession() {
  try {
    const { data: { session } } = await supabaseClient.auth.getSession();
    _supaSession = session;
    return session;
  } catch {
    return null;
  }
}

function getSessionPayload(supaSession) {
  if (!supaSession?.user) return null;
  return {
    user_id:             supaSession.user.id,
    access_token:        supaSession.access_token,
    refresh_token:       supaSession.refresh_token || "",
    expires_at:          supaSession.expires_at
                           ? new Date(supaSession.expires_at * 1000).toISOString()
                           : "",
    subscription_status: "active",
  };
}

async function readCloudUser() {
  const session = await loadSupabaseSession();
  if (!session?.user) {
    if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = "Not logged in";
    if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "—";
    return null;
  }
  const name = session.user.user_metadata?.full_name
             || session.user.email
             || session.user.id;
  if ($("cloudUserLabel"))    $("cloudUserLabel").textContent    = name;
  if ($("subscriptionLabel")) $("subscriptionLabel").textContent = "active";
  return session;
}

async function pushSession() {
  const session = _supaSession || await loadSupabaseSession();
  const p = getSessionPayload(session);
  if (!p) return;
  try { await apiPost("/api/setup/login-complete", p, 10000); } catch {}
}


// ─── CORE FIX: Open local app in the SAME TAB ───────────────────────────────
/**
 * openLocalAppWithSession()
 *
 * BEFORE (broken):  window.open(url, "_blank")
 *   → Opens a new tab every time. Setup page stays open.
 *   → Multiple tabs accumulate on repeated clicks.
 *
 * AFTER (fixed):    window.location.href = url
 *   → Navigates the current tab to the local app URL.
 *   → The setup / popup page is replaced — no extra tabs.
 *   → Single, clean flow: setup page → local app.
 *
 * If no session is available, we still navigate (Flask shows login overlay).
 */
async function openLocalAppWithSession() {
  const session = _supaSession || await loadSupabaseSession();
  const p = getSessionPayload(session);

  if (!p) {
    // No active session — navigate to app anyway; it will show login overlay
    window.location.href = LOCAL_APP;
    return;
  }

  const params = new URLSearchParams({
    token:   p.access_token,
    user_id: p.user_id,
    sub:     "active",
    refresh: p.refresh_token || "",
  });

  // Navigate CURRENT TAB to Flask /login endpoint.
  // Flask sets session cookie → redirects to basira_app.html (authenticated).
  // The setup page is replaced — no new tab, no lingering window.
  window.location.href = `${LOCAL_APP}/login?${params.toString()}`;
}


// ─── Folder picker ───────────────────────────────────────────────────────────
async function browseFolder(inputId) {
  try {
    const r = await apiGet("/api/system/pick-data-dir", 30000);
    if (r?.status === "ok" && r.path) {
      const el = $(inputId);
      if (el) el.value = r.path;
    }
  } catch {
    showNote("err", "Could not open folder picker.");
  }
}


// ─── Setup flow ──────────────────────────────────────────────────────────────
async function runSetup(dataDir) {
  showCard("downloadingCard");
  setStep(2);
  dlStartTime = Date.now();

  showChosenFolder(dataDir);

  const steps = [
    {
      pct: 12, status: "Connecting to local server...",
      fn: async () => {
        const alive = await isBootstrapReachable();
        if (!alive) throw new Error("Local server not reachable. Is Basira installed?");
      }
    },
    {
      pct: 25, status: "Pushing session to local server...",
      fn: async () => { await pushSession(); }
    },
    {
      pct: 40, status: "Initialising data directory...",
      fn: async () => {
        const r = await apiPost("/api/setup/init", { data_dir: dataDir }, 30000);
        if (!r || r.status !== "ok") throw new Error(r?.message || "Directory init failed.");
      }
    },
    {
      pct: 55, status: "Downloading files from GitHub...",
      fn: async () => {
        // Animate speed indicator while downloading
        let kb = 0;
        const si = setInterval(() => {
          kb += Math.floor(Math.random() * 800 + 200);
          setDlStatus(
            `Downloading files from GitHub...`,
            `${(kb / 1024).toFixed(1)} MB received`
          );
        }, 600);
        try {
          const r = await apiPost("/api/setup/download", { data_dir: dataDir }, 600000);
          clearInterval(si);
          if ($("dlSpeed")) $("dlSpeed").textContent = "";
          if (!r || r.status !== "ok") throw new Error(r?.message || "Download failed.");
        } catch (e) {
          clearInterval(si);
          if ($("dlSpeed")) $("dlSpeed").textContent = "";
          throw e;
        }
      }
    },
    {
      pct: 80, status: "Verifying files...",
      fn: async () => {
        const r = await apiGet("/api/setup/verify", 15000);
        if (!r || r.status !== "ok") throw new Error("File verification failed.");
      }
    },
    {
      pct: 93, status: "Saving configuration...",
      fn: async () => {
        const r = await apiPost("/api/setup/finalize", {}, 10000);
        if (!r || r.status !== "ok") throw new Error("Failed to finalise setup.");
      }
    },
  ];

  try {
    for (const step of steps) {
      setDlStatus(step.status, step.speed || "");
      setProgress(step.pct, step.status);
      await step.fn();
    }

    setProgress(100, "Setup complete ✓");
    setDlStatus("All files downloaded and configured ✓");
    const elapsed = ((Date.now() - dlStartTime) / 1000).toFixed(0);
    if ($("dlSpeed")) $("dlSpeed").textContent = `Completed in ${elapsed}s`;

    await new Promise(r => setTimeout(r, 800));

    setStep(3);
    showCard("readyCard");
    const rf = $("readyFolderDisplay");
    if (rf) { rf.classList.remove("isHidden"); rf.textContent = dataDir; }
    showNote("ok", "✓ Basira setup complete. Click the button to open.");

    // Automatically navigate to local app after short delay
    setTimeout(() => { openLocalAppWithSession(); }, 1200);

  } catch (err) {
    console.error("[setup]", err);
    showCard("recoveryCard");
    const rt = $("recoveryText");
    if (rt) rt.textContent = err.message || "Setup failed.";
    const rb = $("repairBtn");
    if (rb) { rb.textContent = "Retry"; rb.dataset.mode = "retry"; }
    showNote("err", err.message || "Setup failed. Click Retry.");
  }
}

async function startSetupFromCard() {
  const dir = $("dataDirectory")?.value.trim() || "C:\\BasiraData";
  await runSetup(dir);
}


// ─── Main state machine ──────────────────────────────────────────────────────
async function initialize() {
  setStep(0);
  showCard("checkingCard");
  showNote("ok", "");

  await readCloudUser();

  const alive = await isBootstrapReachable();
  if (!alive) {
    showCard("notInstalledCard");
    showNote("err", "Basira is not installed on this device.");
    return;
  }

  let state, reason;
  try {
    startupState = await apiGet("/api/startup-status", 10000);
    state  = startupState?.state  || "unknown";
    reason = startupState?.reason || "";
  } catch {
    showCard("notInstalledCard");
    showNote("err", "Could not connect to local server.");
    return;
  }

  switch (state) {

    case "healthy":
    case "healthy_with_optional_update": {
      setStep(3);
      try {
        const cfg = await apiGet("/api/config", 5000);
        if (cfg?.data_dir) showSavedFolder(cfg.data_dir);
      } catch {}
      showCard("readyCard");
      if ($("readySub")) $("readySub").textContent = "Basira is ready. Opening now...";
      showNote("ok", "Environment ready. Opening Basira in this window...");
      // Navigate current tab to local app — no new window
      setTimeout(() => { openLocalAppWithSession(); }, 700);
      break;
    }

    case "new_user":
    case "setup_incomplete":
      setStep(1);
      showCard("pickFolderCard");
      showNote("ok", "First time on this device. Choose a data folder to begin.");
      break;

    case "login_required":
      await pushSession();
      try {
        startupState = await apiGet("/api/startup-status", 8000);
        const ns = startupState?.state;
        if (ns === "healthy" || ns === "healthy_with_optional_update") {
          setStep(3);
          showCard("readyCard");
          showNote("ok", "Session refreshed. Opening Basira...");
          setTimeout(() => { openLocalAppWithSession(); }, 700);
        } else {
          setStep(1);
          showCard("pickFolderCard");
        }
      } catch {
        setStep(1);
        showCard("pickFolderCard");
      }
      break;

    case "recovery_required": {
      showCard("recoveryCard");
      setStep(1);
      const rt = $("recoveryText");
      const rb = $("repairBtn");
      const rf = $("recoveryPathField");
      if (reason === "data_dir_missing") {
        if (rt) rt.textContent = "Data folder not found. Choose a new location.";
        if (rf) rf.classList.remove("isHidden");
        if (rb) { rb.textContent = "Choose new folder & re-download"; rb.dataset.mode = "reselect"; }
      } else {
        if (rt) rt.textContent = "Some files are missing. They will be re-downloaded from GitHub.";
        if (rf) rf.classList.add("isHidden");
        if (rb) { rb.textContent = "Re-download files"; rb.dataset.mode = "repair-files"; }
      }
      showNote("err", "Local environment needs repair.");
      break;
    }

    case "subscription_required":
      showCard("subscriptionCard");
      showNote("err", "Subscription is not active.");
      break;

    case "update_required": {
      showCard("recoveryCard");
      const rt2 = $("recoveryText");
      const rb2 = $("repairBtn");
      if (rt2) rt2.textContent = "A mandatory update is required before continuing.";
      if (rb2) { rb2.textContent = "Open update page"; rb2.dataset.mode = "update"; }
      break;
    }

    default:
      showNote("err", "Unknown state: " + state);
  }
}


// ─── Recovery ────────────────────────────────────────────────────────────────
async function handleRepair() {
  const mode = $("repairBtn")?.dataset.mode || "";

  if (mode === "update") {
    window.open(CLOUD_RENEW_URL, "_blank");
    return;
  }

  if (mode === "retry" || mode === "reselect") {
    const dir = $("recoveryDir")?.value.trim() || "C:\\BasiraData";
    await runSetup(dir);
    return;
  }

  if (mode === "repair-files") {
    showCard("downloadingCard");
    setStep(2);
    setDlStatus("Re-downloading files from GitHub...");
    try {
      const r = await apiPost("/api/recovery/repair-files", {}, 300000);
      if (!r || r.status !== "ok") throw new Error(r?.errors?.join(", ") || "Repair failed.");
      setProgress(80, "Verifying...");
      setDlStatus("Verifying files...");
      const v = await apiGet("/api/setup/verify", 15000);
      if (!v || v.status !== "ok") throw new Error("Verification failed after repair.");
      setProgress(100, "Repaired ✓");
      setStep(3);
      showCard("readyCard");
      showNote("ok", "Repaired. Opening Basira...");
      setTimeout(() => { openLocalAppWithSession(); }, 800);
    } catch (err) {
      showCard("recoveryCard");
      showNote("err", err.message || "Repair failed.");
    }
  }
}

async function retryConnect() {
  const btn = $("retryConnectBtn");
  if (btn) btn.disabled = true;
  showNote("ok", "Connecting...");
  await initialize();
  if (btn) btn.disabled = false;
}

async function renewDemo() {
  try {
    await apiPost("/api/subscription/renew-demo", {}, 10000);
    showNote("ok", "Subscription renewed.");
    setTimeout(initialize, 800);
  } catch (err) {
    showNote("err", err.message || "Could not renew.");
  }
}


// ─── Heartbeat & inactivity ───────────────────────────────────────────────────
async function sendHeartbeat() {
  try {
    const r = await fetch(`${LOCAL_BOOTSTRAP}/api/auth/heartbeat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (r.status === 401) {
      setTimeout(() => { window.location.href = "./login.html"; }, 1500);
    }
  } catch {}
}

function resetInactivity() {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(async () => {
    try {
      await fetch(`${LOCAL_BOOTSTRAP}/api/auth/auto-logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
    } catch {}
    window.location.href = "./login.html";
  }, INACTIVITY_MS);
}

function bindActivity() {
  ["click", "mousemove", "keydown", "scroll", "touchstart"]
    .forEach(ev => window.addEventListener(ev, resetInactivity, { passive: true }));
  resetInactivity();
  setInterval(sendHeartbeat, 60_000);
}


// ─── Boot ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  // Wire up all interactive elements
  $("browseBtn")         ?.addEventListener("click", () => browseFolder("dataDirectory"));
  $("startSetupBtn")     ?.addEventListener("click", startSetupFromCard);
  $("repairBtn")         ?.addEventListener("click", handleRepair);
  $("browseRecoveryBtn") ?.addEventListener("click", () => browseFolder("recoveryDir"));

  // FIX: launchBtn now calls openLocalAppWithSession which uses window.location.href
  // — navigates CURRENT TAB, no new window/tab opened
  $("launchBtn")         ?.addEventListener("click", openLocalAppWithSession);

  $("retryConnectBtn")   ?.addEventListener("click", retryConnect);
  $("renewSubBtn")       ?.addEventListener("click", () => window.open(CLOUD_RENEW_URL, "_blank"));
  $("renewSubBtnReady")  ?.addEventListener("click", () => window.open(CLOUD_RENEW_URL, "_blank"));
  $("renewDemoBtn")      ?.addEventListener("click", renewDemo);

  bindActivity();
  await initialize();
});
