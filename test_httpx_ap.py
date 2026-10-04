import httpx
import asyncio
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def test():
    url = "https://cars.autopartner.by/v/1FTEW1E55KFB29513"
    print("Testing httpx GET", url)
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False, http2=False) as client:
            r = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            print("Status:", r.status_code)
            print("Length:", len(r.text))
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'html.parser')
            imgs = [img.get('src') for img in soup.find_all('img') if img.get('src') and 'image.autopartner' in img.get('src')]
            print("Found images:", len(imgs))
            for im in imgs[:3]:
                print("  ", im)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
