#!/usr/bin/env python3
"""
Scrape open-access museum APIs for Southeast Asian textile reference images.
Sources: Met Museum, Cooper Hewitt, Rijksmuseum
Saves images to reference_images/<Tribe>/ folders and updates manifests.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import time
import ssl
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(BASE_DIR, "reference_images")
ctx = ssl.create_default_context()

# Tribes without reference image folders yet
TRIBES_TO_SCRAPE = [
    "Lua", "Palaung", "Mani", "Urak Lawoi", "Mlabri", "Moklen", "Khamu"
]

# Search queries per tribe
TRIBE_QUERIES = {
    "Lua": ["hill tribe textile", "Lawa textile", "Austroasiatic textile", "indigenous Thailand textile"],
    "Palaung": ["Palaung textile", "Taang textile", "Burma textile", "Myanmar costume"],
    "Mani": ["Maniq textile", "Negrito Thailand", "southern Thailand indigenous", "Mani people"],
    "Urak Lawoi": ["sea nomad textile", "Moken textile", "Andaman textile", "sea gypsy costume", "Thai maritime"],
    "Mlabri": ["Mlabri", "Yellow Leaf people", "Thai hunter gatherer", "Phi Tong Luang"],
    "Moklen": ["Moken textile", "sea nomad Thailand", "Andaman islander", "Moklen costume"],
    "Khamu": ["Khmu textile", "Lao textile", "Laos textile", "Khmu costume", "Austroasiatic textile"]
}

# Global search queries to cast wider net
GLOBAL_QUERIES = [
    "Thai hill tribe textile",
    "Hmong embroidery",
    "Karen weaving", 
    "Lahu textile",
    "Akha costume",
    "Mien textile",
    "Tai Dam weaving",
    "Southeast Asian textile",
    "Lao textile",
    "Burmese textile",
    "sea nomad textile",
    "indigenous Thailand costume",
    "Asian textile traditional",
    "woven textile Southeast Asia"
]

def fetch_json(url, timeout=15):
    """Fetch JSON from URL with retry"""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'DNATextileResearch/1.0 (educational project)'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 10
                print(f"      ⏳ Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif e.code == 404:
                return None
            else:
                print(f"      ❌ HTTP {e.code}")
                return None
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                print(f"      ❌ Error: {e}")
                return None
    return None

def download_image(url, filepath, timeout=20):
    """Download image with retry"""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'DNATextileResearch/1.0 (educational project)'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                data = resp.read()
                if len(data) < 1000:
                    return False
                with open(filepath, 'wb') as f:
                    f.write(data)
                return True
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
    return False

def search_met_museum(query, limit=30):
    """Search Met Museum API for objects"""
    base = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    params = {"q": query, "hasImages": True, "departmentId": "9"}  # Asian Art dept
    url = base + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    if data and "objectIDs" in data:
        ids = data["objectIDs"][:limit]
        results = []
        for obj_id in ids:
            obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
            obj_data = fetch_json(obj_url)
            if obj_data and obj_data.get("primaryImage"):
                results.append({
                    "image_url": obj_data["primaryImage"],
                    "title": obj_data.get("title", "Unknown"),
                    "culture": obj_data.get("culture", ""),
                    "department": obj_data.get("department", ""),
                    "source": "Met Museum"
                })
            time.sleep(0.15)  # Rate limit
        return results
    return []

def search_cooper_hewitt(query, limit=20):
    """Search Cooper Hewitt API"""
    # Cooper Hewitt requires API key, use the open endpoint without key
    # Actually Cooper Hewitt API requires key. Try the alternative:
    # Use their IIIF manifest endpoint or just skip
    # Let's use their public search which works without key via the API v1
    base = "https://api.collection.cooperhewitt.org/v1/search"
    params = {"query": query, "has_images": "true", "per_page": min(limit, 50)}
    url = base + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    if data and "objects" in data:
        results = []
        for obj in data["objects"][:limit]:
            images = obj.get("images", [])
            if images:
                img = images[0]
                results.append({
                    "image_url": img.get("urls", {}).get("medium", img.get("url", "")),
                    "title": obj.get("title", "Unknown"),
                    "culture": obj.get("culture", ""),
                    "source": "Cooper Hewitt"
                })
            time.sleep(0.3)
        return results
    return []

def search_rijksmuseum(query, limit=30):
    """Search Rijksmuseum API"""
    base = "https://www.rijksmuseum.nl/api/nl/collection"
    params = {
        "key": "Nzc1ME5PQk1PcmVxZ0VqT0VqT2lYb1VxQkN0ZGxGQ05kM3Z3dGJ3dA==",  # Public demo key
        "q": query,
        "ps": min(limit, 100),
        "imgonly": True,
        "type": "schilderij"  # paintings only - they have good Asian art
    }
    url = base + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    if data and "artObjects" in data:
        results = []
        for obj in data["artObjects"][:limit]:
            results.append({
                "image_url": obj.get("webImage", {}).get("url", ""),
                "title": obj.get("title", "Unknown"),
                "culture": obj.get("principalOrFirstMaker", ""),
                "source": "Rijksmuseum"
            })
            time.sleep(0.15)
        return results
    return []

def search_rijksmuseum_asian(query, limit=30):
    """Search Rijksmuseum with Asian collection focus"""
    base = "https://www.rijksmuseum.nl/api/nl/collection"
    params = {
        "key": "Nzc1ME5PQk1PcmVxZ0VqT0VqT2lYb1VxQkN0ZGxGQ05kM3Z3dGJ3dA==",
        "q": query,
        "ps": min(limit, 100),
        "imgonly": True,
        "f.normalized32term.sortableLabel": "Aziatische collectie"
    }
    url = base + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    if data and "artObjects" in data:
        results = []
        for obj in data["artObjects"][:limit]:
            img_url = obj.get("webImage", {}).get("url", "")
            if img_url:
                results.append({
                    "image_url": img_url,
                    "title": obj.get("title", "Unknown"),
                    "culture": obj.get("principalOrFirstMaker", ""),
                    "source": "Rijksmuseum"
                })
            time.sleep(0.15)
        return results
    return []

def sanitize_filename(name):
    """Make filename safe"""
    safe = "".join(c if c.isalnum() or c in "._- " else "_" for c in name)
    safe = safe[:150]  # Truncate long names
    return safe

def update_manifest(tribe_dir, source_name, image_name):
    """Update or create manifest.json for tribe"""
    manifest_path = os.path.join(tribe_dir, "manifest.json")
    manifest = {"tribe": tribe_dir.split("/")[-1], "images": [], "source": source_name}
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            try:
                manifest = json.load(f)
            except:
                pass
    if "images" not in manifest:
        manifest["images"] = []
    manifest["source"] = source_name
    manifest_path_resolved = manifest_path
    return manifest_path_resolved

def main():
    print("=" * 70)
    print("Museum API Scraper for DNA Textile Project")
    print("=" * 70)
    
    total_downloaded = 0
    all_results = {}
    
    # Step 1: Search per-tribe queries
    print("\n📋 Step 1: Per-tribe museum searches")
    for tribe in TRIBES_TO_SCRAPE:
        print(f"\n🔍 {tribe}")
        tribe_dir = os.path.join(REF_DIR, tribe)
        os.makedirs(tribe_dir, exist_ok=True)
        
        existing = [f for f in os.listdir(tribe_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
        
        queries = TRIBE_QUERIES.get(tribe, GLOBAL_QUERIES[:3])
        
        for source_name, search_fn in [("Met Museum", search_met_museum), 
                                        ("Rijksmuseum", search_rijksmuseum)]:
            print(f"  🏛️  {source_name}")
            found_images = []
            
            for query in queries[:3]:  # Limit queries per tribe
                print(f"    Query: '{query}'")
                results = search_fn(query, limit=15)
                if results:
                    found_images.extend(results)
                    print(f"    → {len(results)} results")
                time.sleep(1)
            
            # Deduplicate by URL
            seen_urls = set()
            unique = []
            for img in found_images:
                if img["image_url"] not in seen_urls and img["image_url"]:
                    seen_urls.add(img["image_url"])
                    unique.append(img)
            
            print(f"  📊 Unique from {source_name}: {len(unique)}")
            
            # Download
            downloaded = 0
            for i, img in enumerate(unique[:8]):
                safe_name = sanitize_filename(f"{img['title']}")[:100]
                ext = ".jpg"
                filename = f"{source_name.replace(' ', '_')}_{i+1}_{safe_name}{ext}"
                filepath = os.path.join(tribe_dir, filename)
                
                if any(os.path.exists(os.path.join(tribe_dir, f)) and os.path.getsize(os.path.join(tribe_dir, f)) > 5000 
                       for f in os.listdir(tribe_dir) if f.startswith(f"{source_name.replace(' ', '_')}_{i+1}")):
                    downloaded += 1
                    continue
                
                if download_image(img["image_url"], filepath):
                    size_kb = os.path.getsize(filepath) / 1024 if os.path.exists(filepath) else 0
                    if size_kb > 5:
                        print(f"    [{i+1}] ✓ {size_kb:.0f}KB")
                        downloaded += 1
                        total_downloaded += 1
                    else:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        print(f"    [{i+1}] ✗ Too small")
                else:
                    print(f"    [{i+1}] ✗ Download failed")
                
                time.sleep(0.5)
            
            print(f"  ✅ {source_name}: {downloaded} downloaded")
    
    # Step 2: Global searches to fill gaps
    print("\n\n📋 Step 2: Global museum searches")
    global_dir = os.path.join(REF_DIR, "_global")
    os.makedirs(global_dir, exist_ok=True)
    
    for source_name, search_fn in [("Met Museum", search_met_museum),
                                    ("Rijksmuseum", search_rijksmuseum)]:
        print(f"\n🏛️  {source_name} - global search")
        for query in GLOBAL_QUERIES:
            print(f"  Query: '{query}'")
            results = search_fn(query, limit=20)
            if results:
                print(f"  → {len(results)} results")
                # Download a few from each query
                for i, img in enumerate(results[:5]):
                    safe_name = sanitize_filename(f"{query}_{img['title']}")[:100]
                    filename = f"{source_name.replace(' ', '_')}_{safe_name}.jpg"
                    filepath = os.path.join(global_dir, filename)
                    
                    if download_image(img["image_url"], filepath):
                        size_kb = os.path.getsize(filepath) / 1024 if os.path.exists(filepath) else 0
                        if size_kb > 5:
                            print(f"    ✓ {query}: {size_kb:.0f}KB")
                            total_downloaded += 1
                    time.sleep(0.5)
            time.sleep(1)
    
    # Step 3: Update manifests for each tribe
    print("\n\n📋 Step 3: Updating manifests")
    for tribe in TRIBES_TO_SCRAPE:
        tribe_dir = os.path.join(REF_DIR, tribe)
        if os.path.exists(tribe_dir):
            images = [f for f in os.listdir(tribe_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
            manifest = {
                "tribe": tribe,
                "images": images,
                "total": len(images),
                "last_updated": "2026-05-10"
            }
            manifest_path = os.path.join(tribe_dir, "manifest.json")
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            print(f"  {tribe}: {len(images)} images in manifest")
    
    print(f"\n{'='*70}")
    print(f"🎉 Complete! Total new images downloaded: {total_downloaded}")
    print(f"{'='*70}")
    
    # Final summary
    print("\n📁 Final Summary:")
    for tribe in TRIBES_TO_SCRAPE:
        tribe_dir = os.path.join(REF_DIR, tribe)
        if os.path.exists(tribe_dir):
            images = [f for f in os.listdir(tribe_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
            print(f"  {tribe}: {len(images)} images")

if __name__ == "__main__":
    main()
