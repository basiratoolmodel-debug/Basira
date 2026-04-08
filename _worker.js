// /**
//  * _worker.js — Basira Cloudflare Worker
//  * Place this in the ROOT of your GitHub repo.
//  * Repo is PUBLIC — no token needed.
//  * Forces .bat files to download instead of showing as text in browser.
//  */

// const GITHUB_USER   = "basiratoolmodel-debug";
// const GITHUB_REPO   = "Basira";
// const GITHUB_BRANCH = "main";
// const RAW_BASE      = `https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}`;

// export default {
//   async fetch(request, env) {
//     const url  = new URL(request.url);
//     const path = url.pathname;

//     // Force-download Install_Basira.bat
//     if (path === "/download/Install_Basira.bat") {
//       return forceDownload(`${RAW_BASE}/Install_Basira.bat`, "Install_Basira.bat");
//     }

//     // Force-download any file from Basira_local/
//     if (path.startsWith("/download/Basira_local/")) {
//       const file = path.replace("/download/Basira_local/", "");
//       return forceDownload(`${RAW_BASE}/Basira_local/${file}`, file);
//     }

//     // Everything else: serve your cloud pages normally
//     return env.ASSETS.fetch(request);
//   }
// };

// async function forceDownload(rawUrl, filename) {
//   const res = await fetch(rawUrl, {
//     headers: { "User-Agent": "Basira-Worker/1.0" }
//   });

//   if (!res.ok) {
//     return new Response(`File not found: ${filename}`, { status: 404 });
//   }

//   return new Response(res.body, {
//     status: 200,
//     headers: {
//       "Content-Type":                "application/octet-stream",
//       "Content-Disposition":         `attachment; filename="${filename}"`,
//       "Access-Control-Allow-Origin": "*",
//       "Cache-Control":               "no-cache",
//     }
//   });
// }
/**
 * _worker.js — Basira Cloudflare Worker
 * Place this in the ROOT of your GitHub repo.
 * Repo is PUBLIC — no token needed.
 * Forces .bat files to download instead of showing as text in browser.
 */

const GITHUB_USER   = "basiratoolmodel-debug";
const GITHUB_REPO   = "Basira";
const GITHUB_BRANCH = "main";
const RAW_BASE      = `https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}`;

export default {
  async fetch(request, env) {
    const url  = new URL(request.url);
    const path = url.pathname;

    // Force-download Install_Basira.bat
    if (path === "/download/Install_Basira.bat") {
      return forceDownload(`${RAW_BASE}/Install_Basira.bat`, "Install_Basira.bat");
    }

    // Force-download any file from Basira_local/
    if (path.startsWith("/download/Basira_local/")) {
      const file = path.replace("/download/Basira_local/", "");
      return forceDownload(`${RAW_BASE}/Basira_local/${file}`, file);
    }

    // Everything else: serve your cloud pages normally
    return env.ASSETS.fetch(request);
  }
};

async function forceDownload(rawUrl, filename) {
  const res = await fetch(rawUrl, {
    headers: { "User-Agent": "Basira-Worker/1.0" }
  });

  if (!res.ok) {
    return new Response(`File not found: ${filename}`, { status: 404 });
  }

  return new Response(res.body, {
    status: 200,
    headers: {
      "Content-Type":                "application/octet-stream",
      "Content-Disposition":         `attachment; filename="${filename}"`,
      "Access-Control-Allow-Origin": "*",
      "Cache-Control":               "no-cache",
    }
  });
  
}

