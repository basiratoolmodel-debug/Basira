/**
 * functions/download.js
 * Cloudflare Pages Function — handles /download/* routes
 * Place this file in your repo at: functions/download.js
 */

const GITHUB_USER   = "basiratoolmodel-debug";
const GITHUB_REPO   = "Basira";
const GITHUB_BRANCH = "main";
const RAW_BASE      = `https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}`;

export async function onRequest(context) {
  const url      = new URL(context.request.url);
  const filename = url.pathname.replace("/download/", "");

  if (!filename) {
    return new Response("No file specified", { status: 400 });
  }

  // Map requested filename to GitHub path
  let githubPath;
  if (filename === "Install_Basira.bat") {
    githubPath = "Install_Basira.bat";
  } else {
    githubPath = `Basira_local/${filename}`;
  }

  const rawUrl = `${RAW_BASE}/${githubPath}`;
  const res    = await fetch(rawUrl, {
    headers: { "User-Agent": "Basira-Pages/1.0" }
  });

  if (!res.ok) {
    return new Response(`File not found: ${githubPath} (${res.status})`, { status: 404 });
  }

  // Force download — not display as text
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
