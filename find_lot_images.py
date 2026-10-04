import urllib.request
import ssl
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://cars.autopartner.by/v/1FTEW1E55KFB29513"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for image urls
imgs = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', html)
print(f"Total image URLs found: {len(imgs)}")
for im in set(imgs):
    if any(k in im for k in ['copart', 'iaai', 'autopartner', 'lot', 'storage', 'auction']):
        print("  Image:", im)
