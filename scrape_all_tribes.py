#!/usr/bin/env python3
"""
DNA Textile — Reference Image Scraper (All Communities)
Downloads textile/costume/pattern reference images from Wikimedia Commons
for every community in the motif library.
"""

import os
import json
import urllib.request
import urllib.parse
import time
import ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOTIF_DIR = os.path.join(BASE_DIR, "motif_library")
REF_DIR = os.path.join(BASE_DIR, "reference_images")

# Wikimedia API helper
ctx = ssl.create_default_context()

def wiki_api(params):
    base = "https://commons.wikimedia.org/w/api.php"
    query = urllib.parse.urlencode(params)
    url = f"{base}?{query}"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'DNATextileScraper/1.0 (henry@artlevers.com)'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  API error: {e}")
        return None

def get_images_from_category(category, limit=30):
    """Get image URLs from a Wikimedia Commons category"""
    images = []
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": f"Category:{category}",
        "gcmlimit": min(limit, 50),
        "gcmtype": "file",
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    seen_continue = set()
    while True:
        data = wiki_api(params)
        if not data or "query" not in data:
            break
        pages = data["query"].get("pages", {})
        for page in pages.values():
            if "imageinfo" in page:
                for info in page["imageinfo"]:
                    url = info.get("url")
                    mime = info.get("mime", "")
                    if url and mime.startswith("image/"):
                        images.append({
                            "url": url,
                            "filename": page["title"].replace("File:", ""),
                            "size": info.get("size", 0),
                            "width": info.get("width", 0),
                            "height": info.get("height", 0),
                            "category": category
                        })
        cont = data.get("continue")
        if not cont:
            break
        cont_key = json.dumps(cont, sort_keys=True)
        if cont_key in seen_continue:
            break
        seen_continue.add(cont_key)
        params.update(cont)
        time.sleep(0.3)
    return images

def search_images(query, limit=20):
    """Search Wikimedia Commons for images"""
    images = []
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,  # File namespace
        "gsrlimit": min(limit, 50),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    seen_continue = set()
    while True:
        data = wiki_api(params)
        if not data or "query" not in data:
            break
        pages = data["query"].get("pages", {})
        for page in pages.values():
            if "imageinfo" in page:
                for info in page["imageinfo"]:
                    url = info.get("url")
                    mime = info.get("mime", "")
                    if url and mime.startswith("image/"):
                        images.append({
                            "url": url,
                            "filename": page["title"].replace("File:", ""),
                            "size": info.get("size", 0),
                            "width": info.get("width", 0),
                            "height": info.get("height", 0),
                            "query": query
                        })
        cont = data.get("continue")
        if not cont:
            break
        cont_key = json.dumps(cont, sort_keys=True)
        if cont_key in seen_continue:
            break
        seen_continue.add(cont_key)
        params.update(cont)
        time.sleep(0.3)
    return images

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'DNATextileScraper/1.0 (henry@artlevers.com)'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = resp.read()
            with open(filepath, 'wb') as f:
                f.write(data)
            return len(data)
    except Exception as e:
        print(f"  Download error: {e}")
        return 0

def sanitize(name):
    return name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "").replace("*", "")

# ── Community scraping config ──
# Each community: {
#   "wikimedia_category": primary category name,
#   "subcategories": [extra categories to try],
#   "search_terms": [list of search queries],
#   "thai_name": for Thai-language search
# }
COMMUNITIES = {
    "Akha": {
        "thai": "อาข่า",
        "wikimedia_category": "Akha",
        "subcategories": ["Akha_costume", "Akha_culture"],
        "search_terms": [
            "Akha Thailand traditional costume",
            "Akha textile embroidery pattern",
            "อาข่า เสื้อผ้า",
        ]
    },
    "Hmong": {
        "thai": "ม้ง",
        "wikimedia_category": "Hmong",
        "subcategories": ["Hmong_costume", "Hmong_textiles", "Hmong_embroidery", "Paj ntaub"],
        "search_terms": [
            "Hmong Thailand traditional costume textile",
            "Hmong embroidery pattern paj ntaub",
            "ม้ง ผ้าปัก",
        ]
    },
    "Karen": {
        "thai": "กะเหรี่ยง",
        "wikimedia_category": "Karen_people",
        "subcategories": ["Sgaw_Karen", "Pwo_Karen", "Karen_costume", "Karen_textiles"],
        "search_terms": [
            "Karen Thailand traditional costume textile",
            "Karen weaving pattern",
            "กะเหรี่ยง ผ้าทอ",
        ]
    },
    "Khamu": {
        "thai": "ขมุ",
        "wikimedia_category": "Khmu_people",
        "subcategories": [],
        "search_terms": [
            "Khmu traditional costume textile",
            "Khmu weaving pattern",
            "ขมุ ผ้าทอ",
        ]
    },
    "Lahu": {
        "thai": "ลาหู่",
        "wikimedia_category": "Lahu_people",
        "subcategories": ["Lahu_costume"],
        "search_terms": [
            "Lahu Thailand traditional costume textile",
            "Lahu weaving pattern",
            "ลาหู่ ผ้าทอ",
        ]
    },
    "Lisu": {
        "thai": "ลีซอ",
        "wikimedia_category": "Lisu_people",
        "subcategories": ["Lisu_costume", "Lisu_textile"],
        "search_terms": [
            "Lisu Thailand traditional costume textile",
            "Lisu embroidery pattern",
            "ลีซอ ผ้าปัก",
        ]
    },
    "Lua": {
        "thai": "ลัวะ",
        "wikimedia_category": "Lua_people",
        "subcategories": [],
        "search_terms": [
            "Lua Thailand traditional costume textile",
            "Lua weaving pattern",
            "ลัวะ ผ้าทอ",
            "Lawa Thailand textile",  # Lua also known as Lawa
        ]
    },
    "Mani": {
        "thai": "มานิ",
        "wikimedia_category": "Mani_people",
        "subcategories": [],
        "search_terms": [
            "Mani Thailand traditional",
            "Mani Negrito Thailand",
            "มานิ",
        ]
    },
    "Mien": {
        "thai": "เย้า/เมี่ยน",
        "wikimedia_category": "Iu_Mien_people",
        "subcategories": ["Iu_Mien_costume", "Iu_Mien_textile", "Yao_people"],
        "search_terms": [
            "Iu Mien Thailand traditional costume textile",
            "Yao embroidery pattern",
            "เมี่ยน ผ้าปัก",
        ]
    },
    "Mlabri": {
        "thai": "มละบรี",
        "wikimedia_category": "Mlabri_people",
        "subcategories": [],
        "search_terms": [
            "Mlabri Thailand traditional",
            "Mlabri spirit of the yellow leaves",
            "มละบรี",
        ]
    },
    "Moklen": {
        "thai": "มอแกน",
        "wikimedia_category": "Moken_people",
        "subcategories": [],
        "search_terms": [
            "Moken sea gypsy Thailand",
            "Moklen traditional",
            "มอแกน",
            "Mergui archipelago sea gypsy",
        ]
    },
    "Palaung": {
        "thai": "ปะหล่อง",
        "wikimedia_category": "Palaung_people",
        "subcategories": ["Palaung_costume"],
        "search_terms": [
            "Palaung traditional costume textile",
            "Palaung weaving pattern",
            "ปะหล่อง ผ้าทอ",
        ]
    },
    "Tai Dam": {
        "thai": "ไทดำ",
        "wikimedia_category": "Tai_Dam",
        "subcategories": ["Tai_Dam_textile"],
        "search_terms": [
            "Tai Dam traditional costume textile",
            "Tai Dam weaving pattern",
            "ไทดำ ผ้าทอ",
        ]
    },
    "Tai Lue": {
        "thai": "ไทลื้อ",
        "wikimedia_category": "Tai_Lue",
        "subcategories": ["Tai_Lue_textile"],
        "search_terms": [
            "Tai Lue traditional costume textile",
            "Tai Lue weaving pattern",
            "ไทลื้อ ผ้าทอ",
        ]
    },
    "Urak Lawoi": {
        "thai": "อูรักลาโว้ย",
        "wikimedia_category": "Urak_Lawoi",
        "subcategories": [],
        "search_terms": [
            "Urak Lawoi sea gypsy Thailand",
            "Urak Lawoi traditional",
            "อูรักลาโว้ย",
        ]
    },
}


def scrape_community(name, config, max_images=20, dry_run=False):
    """Scrape all reference images for one community."""
    print(f"\n{'='*60}")
    print(f"🏘️  {name} ({config['thai']})")
    print(f"{'='*60}")

    tribe_dir = os.path.join(REF_DIR, name)
    os.makedirs(tribe_dir, exist_ok=True)

    all_images = []
    seen_urls = set()

    # 1. Main Wikimedia category
    cat = config["wikimedia_category"]
    print(f"  📂 Category: {cat}")
    imgs = get_images_from_category(cat, limit=30)
    for img in imgs:
        if img["url"] not in seen_urls:
            seen_urls.add(img["url"])
            all_images.append(img)
    print(f"    → {len(imgs)} images")

    # 2. Subcategories
    for subcat in config.get("subcategories", []):
        print(f"  📂 Subcategory: {subcat}")
        imgs = get_images_from_category(subcat, limit=20)
        for img in imgs:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                all_images.append(img)
        print(f"    → {len(imgs)} images")

    # 3. Search queries
    for query in config.get("search_terms", []):
        print(f"  🔍 Search: {query}")
        imgs = search_images(query, limit=15)
        for img in imgs:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                all_images.append(img)
        print(f"    → {len(imgs)} images")

    print(f"\n  📊 Total unique: {len(all_images)}")

    # 4. Download
    downloaded = 0
    errors = 0
    manifest = []

    for i, img in enumerate(all_images[:max_images]):
        ext = ".jpg"
        url_lower = img["url"].lower()
        if "png" in url_lower: ext = ".png"
        elif "tif" in url_lower: ext = ".tiff"
        elif "gif" in url_lower: ext = ".gif"

        safe = sanitize(img["filename"])
        if not safe.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.svg')):
            safe += ext

        filepath = os.path.join(tribe_dir, safe)
        rel = os.path.join(name, safe)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"  ⏭️  [{i+1}] SKIP {rel}")
            downloaded += 1
            manifest.append({**img, "local_path": rel, "status": "exists"})
            continue

        if dry_run:
            print(f"  🏃 DRY RUN: {rel}")
            manifest.append({**img, "local_path": rel, "status": "dry_run"})
            continue

        size = download_image(img["url"], filepath)
        if size > 0:
            print(f"  ✅ [{i+1}] {rel} ({size/1024:.0f}KB)")
            downloaded += 1
            manifest.append({**img, "local_path": rel, "status": "ok", "bytes": size})
        else:
            print(f"  ❌ [{i+1}] FAIL {rel}")
            errors += 1
            manifest.append({**img, "local_path": rel, "status": "failed"})

        time.sleep(0.5)

    # Save manifest
    manifest_path = os.path.join(tribe_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "community": name,
            "thai": config["thai"],
            "total_found": len(all_images),
            "downloaded": downloaded,
            "errors": errors,
            "max_images": max_images,
            "images": manifest
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  📦 Downloaded: {downloaded} | Errors: {errors}")
    return downloaded, errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DNA Textile Reference Image Scraper")
    parser.add_argument("--all", action="store_true", help="Scrape all communities")
    parser.add_argument("--tribe", type=str, help="Scrape specific tribe only")
    parser.add_argument("--list", action="store_true", help="List all communities and status")
    parser.add_argument("--max", type=int, default=20, help="Max images per tribe (default 20)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be downloaded")
    args = parser.parse_args()

    os.makedirs(REF_DIR, exist_ok=True)

    if args.list:
        print("Community         | Thai       | Images | Manifest")
        print("-" * 65)
        for name, cfg in sorted(COMMUNITIES.items()):
            d = os.path.join(REF_DIR, name)
            exists = os.path.isdir(d)
            count = 0
            has_manifest = False
            if exists:
                count = len([f for f in os.listdir(d)
                             if os.path.isfile(os.path.join(d, f))
                             and not f.endswith('.json')])
                has_manifest = os.path.exists(os.path.join(d, "manifest.json"))
            status = f"✅ {count}" if count > 0 else ("📁 empty" if exists else "❌ none")
            manifest_icon = "📋" if has_manifest else "  "
            print(f"{name:18s} | {cfg['thai']:10s} | {status:10s} | {manifest_icon}")
        return

    if args.tribe:
        if args.tribe not in COMMUNITIES:
            print(f"❌ Unknown tribe: {args.tribe}")
            print(f"Available: {', '.join(sorted(COMMUNITIES.keys()))}")
            return
        scrape_community(args.tribe, COMMUNITIES[args.tribe], args.max, args.dry_run)
        return

    if args.all:
        total_dl = 0
        total_err = 0
        for name, cfg in sorted(COMMUNITIES.items()):
            dl, err = scrape_community(name, cfg, args.max, args.dry_run)
            total_dl += dl
            total_err += err
            time.sleep(1)  # Rate limiting between tribes

        print(f"\n{'='*60}")
        print(f"🎉 COMPLETE!")
        print(f"Total downloaded: {total_dl}")
        print(f"Total errors: {total_err}")
        print(f"Location: {REF_DIR}")
        print(f"{'='*60}")
        return

    # Default: show usage
    parser.print_help()
    print(f"\nExample: python3 {os.path.basename(__file__)} --all --max 15")
    print(f"         python3 {os.path.basename(__file__)} --tribe 'Tai Lue' --max 20")
    print(f"         python3 {os.path.basename(__file__)} --list")


if __name__ == "__main__":
    main()
