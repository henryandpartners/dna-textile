#!/usr/bin/env python3
"""
Final museum image scraper — uses Met Museum (Southeast Asian collection) + Europeana.
Acknowledges gaps for tribes with no museum coverage.
"""
import json, os, time, urllib.request, ssl, re

OUTPUT_DIR = "reference_images"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_json(url):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return json.loads(r.read())
    except:
        return None

def download(url, path):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            data = r.read()
        if len(data) < 2000:
            return False
        with open(path, 'wb') as f:
            f.write(data)
        return True
    except:
        return False

def sanitize(name):
    name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)[:60].strip()
    return name or 'image'

def get_dir(tribe):
    d = os.path.join(OUTPUT_DIR, tribe)
    os.makedirs(d, exist_ok=True)
    return d

def load_manifest(tribe):
    p = os.path.join(get_dir(tribe), 'manifest.json')
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {"tribe": tribe, "images": []}

def save_manifest(tribe, m):
    with open(os.path.join(get_dir(tribe), 'manifest.json'), 'w') as f:
        json.dump(m, f, indent=2)

def met_search(query, limit=20):
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={urllib.request.quote(query)}&hasImages=True"
    data = fetch_json(url)
    if not data:
        return []
    ids = (data.get('objectIDs') or [])[:limit]
    results = []
    for oid in ids:
        obj = fetch_json(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        if obj and obj.get('primaryImage'):
            results.append({
                'title': obj.get('title', ''),
                'image': obj['primaryImage'],
                'culture': obj.get('culture', ''),
                'department': obj.get('department', ''),
                'source': 'Met Museum'
            })
        time.sleep(0.15)
    return results

def eu_search(query, limit=8):
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
                'source': 'Europeana'
            })
        time.sleep(0.15)
    return results

# Strategy: Broad Southeast Asian searches, then filter by culture/department
# Met Museum has a "Asian Art" department with Southeast Asian objects
MET_QUERIES = [
    ("Southeast Asian textile", ["textile", "fabric", "cloth", "weaving", "embroidery", "costume", "garment", "dress"]),
    ("Southeast Asian costume", ["costume", "garment", "dress", "clothing", "textile"]),
    ("Thai textile", ["textile", "fabric", "weaving"]),
    ("Burmese textile", ["textile", "costume"]),
    ("Lao textile", ["textile", "costume"]),
    ("Vietnamese textile", ["textile", "costume", "embroidery"]),
    ("Southeast Asian art", ["textile", "costume", "weaving"]),
]

# Europeana queries — broader
EU_QUERIES = [
    "Southeast Asian textile",
    "Thai traditional costume",
    "hill tribe embroidery",
    "Burmese traditional costume",
    "Lao traditional textile",
    "Southeast Asian ethnic costume",
]

def download_for_tribe(tribe, results, max_per_tribe=5):
    """Download images relevant to a tribe from broad search results."""
    m = load_manifest(tribe)
    existing_urls = {img['url'] for img in m.get('images', [])}
    existing_files = set(os.listdir(get_dir(tribe)))
    downloaded = 0
    
    tribe_lower = tribe.lower()
    
    for r in results:
        if downloaded >= max_per_tribe:
            break
        url = r.get('image', '')
        if not url or url in existing_urls:
            continue
        
        # Check relevance
        title = r.get('title', '').lower()
        culture = r.get('culture', '').lower()
        dept = r.get('department', '').lower()
        text = f"{title} {culture} {dept}"
        
        # Skip if clearly not Southeast Asian
        skip_words = ['european', 'african', 'american', 'chinese porcelain', 'japanese', 'korean', 'indian painting', 'conus textile', 'shell']
        if any(w in text for w in skip_words):
            continue
        
        # Check if somewhat relevant to this tribe or SE Asia generally
        tribe_words = {
            'Karen': ['karen', 'kayah', 'kayaw', 'burma', 'myanmar'],
            'Hmong': ['hmong', 'miao'],
            'Akha': ['akha', 'hani'],
            'Lahu': ['lahu'],
            'Lisu': ['lisu'],
            'Mien': ['mien', 'yao'],
            'Khamu': ['khmu', 'khamu', 'kammu', 'lao'],
            'Palaung': ['palaung', 'burma', 'shan'],
            'Tai Dam': ['tai dam', 'black tai', 'thai dam', 'vietnam'],
            'Tai Lue': ['tai lue', 'lue', 'lanna'],
            'Lua': ['lua', 'lawa', 'lawaa'],
            'Mani': ['mani', 'maniq', 'semang', 'negrito', 'malay'],
            'Mlabri': ['mlabri', 'mabri', 'phi tong'],
            'Moklen': ['moken', 'moklen', 'sea nomad', 'andaman'],
            'Urak Lawoi': ['urak lawoi', 'sea nomad', 'orang laut', 'andaman'],
        }
        
        relevant_words = tribe_words.get(tribe, ['southeast asia', 'thai', 'burma', 'lao', 'vietnam', 'myanmar', 'cambodia'])
        if not any(w in text for w in relevant_words):
            continue
        
        fn = sanitize(r.get('title', f'{tribe}_{downloaded}'))
        fp = os.path.join(get_dir(tribe), f"{fn}.jpg")
        if os.path.exists(fp) or f"{fn}.jpg" in existing_files:
            continue
        
        if download(url, fp):
            m['images'].append({
                'url': url,
                'title': r.get('title', ''),
                'source': r.get('source', ''),
                'culture': r.get('culture', '')
            })
            existing_urls.add(url)
            downloaded += 1
            print(f"  ✅ {tribe}: {r.get('title', '')[:50]}")
    
    save_manifest(tribe, m)
    imgs = [f for f in os.listdir(get_dir(tribe)) if f.endswith(('.jpg', '.png', '.jpeg'))]
    return len(imgs), downloaded

print("🏛️ Museum Image Scraper — Met Museum + Europeana")
print("=" * 60)

# Gather all results first
print("\n📡 Fetching from Met Museum...")
all_met = []
for query, _ in MET_QUERIES:
    results = met_search(query, 15)
    print(f"  '{query}': {len(results)}")
    all_met.extend(results)
    time.sleep(1)

print("\n📡 Fetching from Europeana...")
all_eu = []
for query in EU_QUERIES:
    results = eu_search(query, 8)
    print(f"  '{query}': {len(results)}")
    all_eu.extend(results)
    time.sleep(1)

all_results = all_met + all_eu
print(f"\n📊 Total results gathered: {len(all_results)}")

# Download for each tribe that needs images
print("\n📥 Downloading for tribes with 0 images:")
for tribe in sorted(os.listdir(OUTPUT_DIR)):
    p = os.path.join(OUTPUT_DIR, tribe)
    if not os.path.isdir(p):
        continue
    imgs = [f for f in os.listdir(p) if f.endswith(('.jpg', '.png', '.jpeg'))]
    if len(imgs) >= 3:
        continue
    print(f"\n  🔍 {tribe} ({len(imgs)} existing)")
    total, new = download_for_tribe(tribe, all_results, max_per_tribe=5)
    print(f"  📸 {tribe}: {total} total (+{new} new)")
    time.sleep(0.5)

# Final summary
print(f"\n{'=' * 60}")
print("📊 Final image counts:")
for tribe in sorted(os.listdir(OUTPUT_DIR)):
    p = os.path.join(OUTPUT_DIR, tribe)
    if os.path.isdir(p):
        imgs = [f for f in os.listdir(p) if f.endswith(('.jpg', '.png', '.jpeg'))]
        icon = "✅" if len(imgs) >= 5 else ("⚠️" if len(imgs) > 0 else "❌")
        print(f"  {icon} {tribe}: {len(imgs)} images")
