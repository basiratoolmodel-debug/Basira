/**
 * _worker.js  — place this in the ROOT of your GitHub repo
 * Cloudflare Pages/Workers picks this up automatically.
 *
 * After adding this file and committing:
 *   1. Cloudflare redeploys automatically
 *   2. Go to Settings → Variables and Secrets → Add GITHUB_TOKEN as Secret
 *   3. The download routes will work for your private repo
 */

const GITHUB_USER   = "basiratoolmodel-debug";
const GITHUB_REPO   = "Basira";
const GITHUB_BRANCH = "main";

export default {
  async fetch(request, env) {
    const url  = new URL(request.url);
    const path = url.pathname;

    // ── Download Install_Basira.bat ───────────────────────────
    if (path === "/download/Install_Basira.bat") {
      return serveFile("Install_Basira.bat", "application/octet-stream",
                       "Install_Basira.bat", env);
    }

    // ── Download any file from Basira_local/ folder ───────────
    if (path.startsWith("/download/Basira_local/")) {
      const file = path.replace("/download/Basira_local/", "");
      return serveFile(`Basira_local/${file}`, "text/plain", file, env);
    }

    // ── Everything else: serve normally (your cloud HTML pages) ─
    return env.ASSETS.fetch(request);
  }
};

async function serveFile(filePath, contentType, downloadName, env) {
  const token = env.GITHUB_TOKEN;

  const apiUrl = `https://api.github.com/repos/${GITHUB_USER}/${GITHUB_REPO}/contents/${filePath}?ref=${GITHUB_BRANCH}`;

  const res = await fetch(apiUrl, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept":        "application/vnd.github.raw",
      "User-Agent":    "Basira-Worker/1.0",
    }
  });

  if (!res.ok) {
    return new Response(
      `File not found: ${filePath} (${res.status})`, { status: res.status }
    );
  }

  return new Response(res.body, {
    headers: {
      "Content-Type":                contentType,
      "Content-Disposition":         `attachment; filename="${downloadName}"`,
      "Access-Control-Allow-Origin": "*",
      "Cache-Control":               "no-cache",
    }
  });
}
