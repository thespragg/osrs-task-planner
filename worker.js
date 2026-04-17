const UPSTREAM = "https://sync.runescape.wiki/runelite/player";
const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default {
  async fetch(request) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    // Expect path: /<username>/<league>
    const match = url.pathname.match(/^\/([^/]+)\/([^/]+)$/);
    if (!match) {
      return new Response("Not found", { status: 404, headers: CORS_HEADERS });
    }

    const [, username, league] = match;
    const upstream = `${UPSTREAM}/${encodeURIComponent(username)}/${encodeURIComponent(league)}`;

    const response = await fetch(upstream, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://oldschool.runescape.com/",
      },
    });

    const body = await response.text();
    return new Response(body, {
      status: response.status,
      headers: {
        ...CORS_HEADERS,
        "Content-Type": response.headers.get("Content-Type") || "application/json",
      },
    });
  },
};
