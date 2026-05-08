// Put this function inside the main Basira index.html file.
// Replace the URL after deploying the Cloudflare Pages frontend.

function launchScraper(prefilledUrl = "") {
  const SCRAPER_CLOUD_URL = "https://basira-web-scraping.pages.dev";

  const finalUrl = prefilledUrl
    ? SCRAPER_CLOUD_URL + "?url=" + encodeURIComponent(prefilledUrl)
    : SCRAPER_CLOUD_URL;

  window.location.href = finalUrl;
}
