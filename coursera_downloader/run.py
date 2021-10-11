import asyncio
import logging

import aiohttp
from http.cookiejar import MozillaCookieJar
from Crawler import Crawler
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[%(lineno)d] - %(message)s')


async def main():
    cookies_file = 'coursera.org_cookies.txt'
    cj = MozillaCookieJar()
    cj.load(cookies_file)
    cookies = {c.name: c.value for c in cj}
    async with aiohttp.ClientSession(cookies=cookies, trust_env=False) as session:
        c = Crawler(session)
        await c.crawl_course('ruhe-xuexi')


if __name__ == '__main__':
    asyncio.run(main())
