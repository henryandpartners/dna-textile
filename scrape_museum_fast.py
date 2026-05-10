#!/usr/bin/env python3
"""
Scrape reference images from working museum APIs: Met Museum + Europeana.
"""
import json
import os
import time
import urllib.request
import ssl
import re

OUTPUT_DIR = "reference_images"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_json(url, headers=None):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"    ⚠️ {e}")
        return None

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            data = resp.read()
        if len(data) < 1000:
            return False
        with open(filepath, 'wb') as f:
            f.write(data)
        return True
    except:
        return False

def sanitize(name):
    name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)[:70].strip()
    if not name:
        return 'image'
    return name

def get_tribe_dir(tribe):
    d = os.path.join(OUTPUT_DIR, tribe)
    os.makedirs(d, exist_ok=True)
    return d

def load_manifest(tribe):
    path = os.path.join(get_tribe_dir(tribe), 'manifest.json')
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"tribe": tribe, "images": []}

def save_manifest(tribe, m):
    with open(os.path.join(get_tribe_dir(tribe), 'manifest.json'), 'w') as f:
        json.dump(m, f, indent=2)

def search_met(query, limit=15):
    """Met Museum API."""
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={urllib.request.quote(query)}&hasImages=True"
    data = fetch_json(url)
    if not data:
        return []
    ids = data.get('objectIDs') or []
    ids = ids[:limit]
    results = []
    for oid in ids:
        obj = fetch_json(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        if obj and obj.get('primaryImage'):
            results.append({
                'title': obj.get('title', ''),
                'image': obj['primaryImage'],
                'culture': obj.get('culture', ''),
                'source': 'Met Museum'
            })
        time.sleep(0.2)
    return results

def search_europeana(query, limit=10):
    """Europeana API."""
    url = f"https://api.europeana.eu/record/v2/search.json?wskey=apidemo&query={urllib.request.quote(query)}&reusability=open&media=true&rows={limit}"
    data = fetch_json(url)
    if not data:
        return []
    results = []
    for item in data.get('items', [])[:limit]:
        previews = item.get('edmPreview', [])
        if isinstance(previews, str):
            previews = [previews]
        if previews:
            title = item.get('title', [''])[0] if isinstance(item.get('title'), list) else item.get('title', '')
            results.append({
                'title': str(title),
                'image': previews[0],
                'culture': str(item.get('dataProvider', '')),
                'source': 'Europeana'
            })
        time.sleep(0.2)
    return results

# Tribe → search queries (broader terms for better coverage)
QUERIES = {
    "Khamu": ["Khmu textile", "Khmu costume", "Kammu clothing", "Lao textile traditional", "Laos traditional costume"],
    "Lisu": ["Lisu textile", "Lisu embroidery", "Lisu costume", "Lisu clothing traditional", "Yao Lisu textile"],
    "Palaung": ["Palaung textile", "Palaung costume", "Taung Yo textile", "Burmese textile traditional", "Shan State costume"],
    "Tai Dam": ["Tai Dam textile", "Thai Dam weaving", "Black Tai textile", "Tai textile traditional", "Vietnam ethnic costume Tai"],
    "Tai Lue": ["Tai Lue textile", "Lue weaving", "Lue textile traditional", "Xishuangbanna textile", "Lanna textile"],
    "Lua": ["Lawa textile", "Lua costume", "Northern Thai tribal costume", "Karen Lawa textile", "H'tin costume"],
    "Mani": ["Semang costume", "Negrito traditional", "Maniq Thailand", "Orang Asli costume", "Malay indigenous clothing"],
    "Mlabri": ["Mlabri", "Mabri costume", "Phi Tong Luang", "Thai hill tribe costume", "Northern Thailand indigenous"],
    "Moklen": ["Moken textile", "Moken costume", "sea nomad costume", "Andaman sea nomad", "Thai sea gypsy costume"],
    "Urak Lawoi": ["Urak Lawoi", "sea nomad Thailand", "Orang Laut costume", "Phuket sea gypsy", "Andaman indigenous costume"],
}

def scrape_tribe(tribe, queries, max_total=8):
    print(f"\n🔍 {tribe}")
    m = load_manifest(tribe)
    existing_urls = {img['url'] for img in m.get('images', [])}
    existing_files = set(os.listdir(get_tribe_dir(tribe)))
    downloaded = 0
    
    for query in queries:
        if downloaded >= max_total:
            break
        print(f"  Query: '{query}'")
        
        # Europeana (reliable)
        results = search_europeana(query, 8)
        print(f"    Europeana: {len(results)}")
        
        # Met Museum
        met_results = search_met(query, 8)
        print(f"    Met Museum: {len(met_results)}")
        results.extend(met_results)
        
        for r in results:
            if downloaded >= max_total:
                break
            url = r.get('image', '')
            if not url or url in existing_urls:
                continue
            fn = sanitize(r.get('title', f'{tribe}_{downloaded}'))
            fp = os.path.join(get_tribe_dir(tribe), f"{fn}.jpg")
            if os.path.exists(fp) or f"{fn}.jpg" in existing_files:
                continue
            if download_image(url, fp):
                m['images'].append({'url': url, 'title': r.get('title', ''), 'source': r.get('source', ''), 'query': query})
                existing_urls.add(url)
                downloaded += 1
                print(f"    ✅ {r.get('title', '')[:50]}")
            time.sleep(0.3)
        time.sleep(0.5)
    
    save_manifest(tribe, m)
    imgs = [f for f in os.listdir(get_tribe_dir(tribe)) if f.endswith(('.jpg', '.png', '.jpeg'))]
    print(f"  📸 {tribe}: {len(imgs)} total ({downloaded} new)")

if __name__ == '__main__':
    print("🏛️  Museum API Scraper (Met Museum + Europeana)")
    total_new = 0
    for tribe, queries in QUERIES.items():
        d = get_tribe_dir(tribe)
        imgs = [f for f in os.listdir(d) if f.endswith(('.jpg', '.png', '.jpeg'))]
        if len(imgs) >= 5:
            print(f"⏭️  {tribe}: already has {len(imgs)} images")
            continue
        scrape_tribe(tribe, queries)
        total_new += 1
        time.sleep(1)
    
    print(f"\n📊 Summary:")
    for d in sorted(os.listdir(OUTPUT_DIR)):
        p = os.path.join(OUTPUT_DIR, d)
        if os.path.isdir(p):
            imgs = [f for f in os.listdir(p) if f.endswith(('.jpg', '.png', '.jpeg'))]
            print(f"  {'✅' if imgs else '❌'} {d}: {len(imgs)}")
