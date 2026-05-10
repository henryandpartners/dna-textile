#!/usr/bin/env python3
"""
Scrape reference images from open-access museum APIs for DNA Textile project.
Sources: Metropolitan Museum, Cooper Hewitt, Rijksmuseum, Smithsonian
"""
import json
import os
import time
import urllib.request
import ssl
import base64

OUTPUT_DIR = "reference_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Disable SSL verification for museum APIs (some have cert issues)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_json(url, headers=None):
    """Fetch JSON from URL."""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'DNA-Textile-Research/1.0')
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ❌ Fetch failed: {url}: {e}")
        return None

def download_image(url, filepath):
    """Download image to filepath."""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'DNA-Textile-Research/1.0')
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            data = resp.read()
        with open(filepath, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  ❌ Download failed: {url}: {e}")
        return False

def get_tribe_dir(tribe):
    """Get or create tribe directory."""
    d = os.path.join(OUTPUT_DIR, tribe)
    os.makedirs(d, exist_ok=True)
    return d

def load_manifest(tribe):
    """Load existing manifest or create new one."""
    path = os.path.join(get_tribe_dir(tribe), 'manifest.json')
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"tribe": tribe, "images": [], "source": "museum_apis"}

def save_manifest(tribe, manifest):
    """Save manifest."""
    path = os.path.join(get_tribe_dir(tribe), 'manifest.json')
    with open(path, 'w') as f:
        json.dump(manifest, f, indent=2)

def sanitize_filename(name):
    """Make filename safe."""
    import re
    name = re.sub(r'[^\w\s\-\.\(\)]', '', name)[:80]
    return name.strip() + ".jpg"

# =====================================================================
# 1. METROPOLITAN MUSEUM (No API key required)
# =====================================================================
def search_met_museum(query, max_results=20):
    """Search Met Museum API for objects."""
    base = "https://collectionapi.metmuseum.org/public/collection/v1"
    url = f"{base}/search?q={urllib.request.quote(query)}&hasImages=True"
    data = fetch_json(url)
    if not data or 'objectIDs' not in data:
        return []
    
    object_ids = data.get('objectIDs') or []
    object_ids = object_ids[:max_results]
    results = []
    for oid in object_ids:
        obj_url = f"{base}/objects/{oid}"
        obj = fetch_json(obj_url)
        if obj and obj.get('primaryImage'):
            results.append({
                'title': obj.get('title', ''),
                'image': obj.get('primaryImage', ''),
                'culture': obj.get('culture', ''),
                'department': obj.get('department', ''),
                'date': obj.get('objectDate', ''),
                'source': 'Metropolitan Museum of Art'
            })
        time.sleep(0.3)  # Rate limit
    return results

# =====================================================================
# 2. COOPER HEWITT (No API key required for search)
# =====================================================================
def search_cooper_hewitt(query, max_results=20):
    """Search Cooper Hewitt API."""
    # Cooper Hewitt requires API key; use their public endpoint
    base = "https://api.cooperhewitt.org/rest"
    url = f"{base}/objects?q={urllib.request.quote(query)}&format=json&limit={max_results}&image=1"
    data = fetch_json(url)
    if not data or 'objects' not in data:
        return []
    
    results = []
    for obj in data.get('objects', [])[:max_results]:
        if obj.get('images'):
            img = obj['images'][0] if isinstance(obj['images'], list) else obj['images']
            if img.get('web'):
                results.append({
                    'title': obj.get('title', ''),
                    'image': img.get('web', ''),
                    'culture': obj.get('culture', ''),
                    'date': obj.get('date', ''),
                    'source': 'Cooper Hewitt, Smithsonian Design Museum'
                })
        time.sleep(0.3)
    return results

# =====================================================================
# 3. RIJKSMUSEUM (API key not required for basic search)
# =====================================================================
def search_rijksmuseum(query, max_results=20):
    """Search Rijksmuseum API."""
    base = "https://www.rijksmuseum.nl/api/en/collection"
    url = f"{base}?key=I9tJlYKd&q={urllib.request.quote(query)}&ps={max_results}&imgonly=True"
    data = fetch_json(url)
    if not data or 'artObjects' not in data:
        return []
    
    results = []
    for obj in data.get('artObjects', [])[:max_results]:
        img_url = obj.get('webImage', {})
        if img_url and img_url.get('url'):
            results.append({
                'title': obj.get('title', ''),
                'image': img_url['url'],
                'culture': '',
                'date': obj.get('dating', {}).get('year', ''),
                'source': 'Rijksmuseum Amsterdam'
            })
        time.sleep(0.3)
    return results

# =====================================================================
# 4. SMITHSONIAN OPEN ACCESS (No API key required)
# =====================================================================
def search_smithsonian(query, max_results=20):
    """Search Smithsonian Open Access API."""
    base = "https://api.si.edu/openaccess/api/v1.0/search"
    url = f"{base}?q={urllib.request.quote(query)}&rows={max_results}&fmt=json"
    data = fetch_json(url)
    if not data or 'response' not in data:
        return []
    
    results = []
    for item in data.get('response', {}).get('rows', [])[:max_results]:
        img_urls = item.get('content', {}).get('edanmdm', {}).get('descriptiveNonRepeating', {}).get('online_media', [])
        img_url = None
        for m in img_urls:
            if m.get('mediaType') == 'Images' and m.get('content'):
                img_url = m['content']
                break
        if img_url:
            results.append({
                'title': item.get('title', ''),
                'image': img_url,
                'culture': item.get('content', {}).get('edanmdm', {}).get('descriptiveNonRepeating', {}).get('data_source', ''),
                'date': '',
                'source': 'Smithsonian Open Access'
            })
        time.sleep(0.3)
    return results

# =====================================================================
# 5. EUROPEANA (API key not required for basic search)
# =====================================================================
def search_europeana(query, max_results=15):
    """Search Europeana API."""
    base = "https://api.europeana.eu/record/v2/search.json"
    url = f"{base}?wskey=apidemo&query={urllib.request.quote(query)}&reusability=open&media=true&rows={max_results}"
    data = fetch_json(url)
    if not data or 'items' not in data:
        return []
    
    results = []
    for item in data.get('items', [])[:max_results]:
        img_urls = item.get('edmPreview', [])
        if isinstance(img_urls, str):
            img_urls = [img_urls]
        if img_urls:
            # Get higher resolution if possible            img_url = img_urls[0].replace('/200/', '/400/').replace('w=200', 'w=400')
            results.append({
                'title': item.get('title', [''])[0] if isinstance(item.get('title'), list) else item.get('title', ''),
                'image': img_urls[0],
                'culture': item.get('dataProvider', [''])[0] if isinstance(item.get('dataProvider'), list) else '',
                'date': '',
                'source': 'Europeana'
            })
        time.sleep(0.3)
    return results

# =====================================================================
# MAIN SCRAPING PIPELINE
# =====================================================================
SEARCHES = {
    "Hmong": [
        "Hmong textile", "Hmong embroidery", "Hmong clothing", "Hmong paj ntaub",
        "Hmong costume", "Miao textile", "Miao embroidery"
    ],
    "Karen": [
        "Karen textile", "Karen weaving", "Kayah textile", "Karen costume",
        "Kayaw costume", "Karen traditional dress"
    ],
    "Akha": [
        "Akha textile", "Akha costume", "Akha clothing", "Akha traditional dress",
        "Ha Ni textile"
    ],
    "Lahu": [
        "Lahu textile", "Lahu costume", "Lahu clothing", "Lahu traditional dress",
        "Lahu weaving"
    ],
    "Lisu": [
        "Lisu textile", "Lisu costume", "Lisu clothing", "Lisu traditional dress",
        "Lisu embroidery"
    ],
    "Mien": [
        "Mien textile", "Yao textile", "Mien costume", "Yao embroidery",
        "Mien clothing"
    ],
    "Khamu": [
        "Khamu textile", "Khamu costume", "Kammu textile", "Khamu clothing",
        "Khmu traditional dress"
    ],
    "Palaung": [
        "Palaung textile", "Palaung costume", "Palaung clothing", "Taung Yo textile",
        "Palaung traditional dress"
    ],
    "Tai Dam": [
        "Tai Dam textile", "Tai Dam weaving", "Thai Dam costume", "Tai Dam clothing",
        "Black Tai textile"
    ],
    "Tai Lue": [
        "Tai Lue textile", "Tai Lue weaving", "Lue textile", "Tai Lue costume",
        "Lue clothing"
    ],
    "Lua": [
        "Lua textile", "Lua costume", "Lawa textile", "Lua traditional dress",
        "Lawa clothing"
    ],
    "Mani": [
        "Mani costume", "Maniq clothing", "Semang textile", "Negrito costume",
        "Maniq traditional"
    ],
    "Mlabri": [
        "Mlabri costume", "Mlabri clothing", "Phi Tong Luang", "Mlabri traditional"
    ],
    "Moklen": [
        "Moklen costume", "Moken textile", "sea nomad costume", "Moken clothing",
        "Moken traditional"
    ],
    "Urak Lawoi": [
        "Urak Lawoi costume", "sea nomad costume", "Urak Lawoi clothing",
        "Thai sea nomad", "Orang Laut costume"
    ]
}

def scrape_tribe(tribe, queries, max_per_query=5):
    """Scrape images for one tribe from all APIs."""
    print(f"\n🔍 {tribe}")
    manifest = load_manifest(tribe)
    existing_urls = {img['url'] for img in manifest.get('images', [])}
    existing_files = set(os.listdir(get_tribe_dir(tribe)))
    
    total_downloaded = 0
    
    for query in queries:
        print(f"  Searching: '{query}'")
        
        # Try all APIs
        all_results = []
        
        # Met Museum
        results = search_met_museum(query, max_per_query)
        print(f"    Met Museum: {len(results)} results")
        all_results.extend(results)
        
        # Smithsonian
        results = search_smithsonian(query, max_per_query)
        print(f"    Smithsonian: {len(results)} results")
        all_results.extend(results)
        
        # Europeana
        results = search_europeana(query, max_per_query)
        print(f"    Europeana: {len(results)} results")
        all_results.extend(results)
        
        # Cooper Hewitt
        results = search_cooper_hewitt(query, max_per_query)
        print(f"    Cooper Hewitt: {len(results)} results")
        all_results.extend(results)
        
        # Rijksmuseum
        results = search_rijksmuseum(query, max_per_query)
        print(f"    Rijksmuseum: {len(results)} results")
        all_results.extend(results)
        
        # Download unique images
        for result in all_results:
            img_url = result.get('image', '')
            if not img_url or img_url in existing_urls:
                continue
            
            filename = sanitize_filename(result.get('title', f'{tribe}_{len(manifest["images"])}'))
            filepath = os.path.join(get_tribe_dir(tribe), filename)
            
            if os.path.exists(filepath):
                continue
            
            if download_image(img_url, filepath):
                manifest['images'].append({
                    'url': img_url,
                    'title': result.get('title', ''),
                    'source': result.get('source', ''),
                    'culture': result.get('culture', ''),
                    'date': result.get('date', ''),
                    'query': query
                })
                existing_urls.add(img_url)
                total_downloaded += 1
                print(f"    ✅ Downloaded: {result.get('title', '')[:60]}")
            
            # Limit downloads per tribe
            if total_downloaded >= 10:
                break
        
        if total_downloaded >= 10:
            break
        
        time.sleep(1)
    
    save_manifest(tribe, manifest)
    image_files = [f for f in os.listdir(get_tribe_dir(tribe)) if f.endswith(('.jpg', '.png', '.jpeg'))]
    print(f"  📸 {tribe}: {len(image_files)} total images ({total_downloaded} new)")
    return total_downloaded

if __name__ == '__main__':
    print("🏛️  Museum API Scraper for DNA Textile Reference Images")
    print("=" * 60)
    
    # Only scrape tribes that need images
    tribes_needing_images = []
    for tribe, queries in SEARCHES.items():
        d = get_tribe_dir(tribe)
        if os.path.exists(d):
            imgs = [f for f in os.listdir(d) if f.endswith(('.jpg', '.png', '.jpeg'))]
            if len(imgs) < 5:
                tribes_needing_images.append((tribe, queries))
        else:
            tribes_needing_images.append((tribe, queries))
    
    print(f"📋 Scraping {len(tribes_needing_images)} tribes that need images\n")
    
    total = 0
    for tribe, queries in tribes_needing_images:
        n = scrape_tribe(tribe, queries)
        total += n
        time.sleep(2)  # Be nice to APIs
    
    print(f"\n{'=' * 60}")
    print(f"📊 Done! Downloaded {total} new images")
    
    # Summary
    print("\n📁 Image counts by tribe:")
    for d in sorted(os.listdir(OUTPUT_DIR)):
        p = os.path.join(OUTPUT_DIR, d)
        if os.path.isdir(p):
            imgs = [f for f in os.listdir(p) if f.endswith(('.jpg', '.png', '.jpeg'))]
            status = "✅" if len(imgs) > 0 else "❌"
            print(f"  {status} {d}: {len(imgs)} images")
