import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/121.0",
]

async def fetch_free_proxies():
    url = "https://free-proxy-list.net/en/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            html = await r.text()

    soup = BeautifulSoup(html, "html.parser")

    wrapper = soup.find("div", class_="table-responsive")
    if not wrapper:
        print("No proxy table found (wrapper missing)")
        return []

    table = wrapper.find("table")
    if not table:
        print("No table found inside .table-responsive")
        return []

    proxies = []
    rows = table.tbody.find_all("tr")

    for row in rows:
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) < 8:
            continue

        ip, port, code, country, anonymity, google, https, last_checked = cols

        # Filter criteria:
        # Only include HTTPS proxies that are anonymous or elite
        if https.lower() != "yes":
            continue

        if anonymity.lower() not in ("anonymous", "elite proxy"):
            continue

        proxy = f"http://{ip}:{port}"
        proxies.append(proxy)

    return proxies

async def getHTML(link, retries=5, base_delay=1.0):
    proxies = await fetch_free_proxies()

    if not proxies:
        print("⚠️ No proxies found — scraping without proxy.")
        proxies = [None]  # fallback

    timeout = aiohttp.ClientTimeout(total=15)

    for attempt in range(retries):
        proxy = random.choice(proxies)
        user_agent = random.choice(USER_AGENTS)

        headers = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            try:
                async with session.get(link, proxy=proxy) as r:

                    # Temporary block or overloaded
                    if r.status in (429, 500, 502, 503, 504):
                        if attempt < retries - 1:
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.3)
                            print(f"[Retry {attempt+1}] Status {r.status} — switching proxy → {proxy}")
                            await asyncio.sleep(delay)
                            continue

                    if r.status == 200:
                        print(f"✔ Success with proxy {proxy}")
                        return BeautifulSoup(await r.text(), "html.parser")

                    r.raise_for_status()

            except Exception as e:
                if attempt < retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.3)
                    print(f"[Retry {attempt+1}] Proxy failed: {proxy} → {e}. Sleeping {delay:.2f}s")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise

    return None