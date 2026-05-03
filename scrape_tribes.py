#!/usr/bin/env python3
"""
Thai Hill Tribes Visual Reference Scraper
Downloads images from Wikimedia Commons for each tribe
"""

import os
import json
import urllib.request
import urllib.parse
import time
import ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Thai hill tribes with their Wikimedia Commons category names and Thai names
TRIBES = [
    {"name": "Karen", "thai": "กะเหรี่ยง", "category": "Karen_people", "subcategories": [
        "Sgaw_Karen", "Pwo_Karen", "Kayah_state", "Red_Karen", "Black_Karen"
    ]},
    {"name": "Hmong", "thai": "ม้ง", "category": "Hmong", "subcategories": [
        "Hmong_costume", "Hmong_textiles", "Hmong_embroidery"
    ]},
    {"name": "Akha", "thai": "อาข่า", "category": "Akha", "subcategories": [
        "Akha_costume", "Akha_culture"
    ]},
    {"name": "Lisu", "thai": "ลีซอ", "category": "Lisu_people", "subcategories": [
        "Lisu_costume"
    ]},
    {"name": "Mien", "thai": "เย้า/เมี่ยน", "category": "Iu_Mien_people", "subcategories": [
        "Iu_Mien_costume"
    ]},
    {"name": "Lahu", "thai": "ลาหู่", "category": "Lahu_people", "subcategories": []},
    {"name": "Lawa", "thai": "ละว้า", "category": "Lawá_people", "subcategories": []},
    {"name": "Wa", "thai": "ว้า", "category": "Wa_people", "subcategories": []},
    {"name": "Mlabri", "thai": "มละบรี", "category": "Mlabri_people", "subcategories": []},
    {"name": "Khamu", "thai": "ขมุ", "category": "Khmu_people", "subcategories": []},
    {"name": "Shan", "thai": "ฉาน", "category": "Shan_people", "subcategories": []},
    {"name": "Palong", "thai": "ปォลำผี่/บรู", "category": "Palaung_people", "subcategories": []},
    {"name": "Karen_Sgaw", "thai": "กะเหรี่ยงสะกอ", "category": "Sgaw_Karen", "subcategories": []},
    {"name": "Karen_Pwo", "thai": "กะเหรี่ยงโปว์", "category": "Pwo_Karen", "subcategories": []},
    {"name": "Hmong_White", "thai": "ม้งขาว", "category": "White_Hmong", "subcategories": []},
    {"name": "Hmong_Green", "thai": "ม้งเขียว", "category": "Green_Hmong", "subcategories": []},
]

# SSL context to handle certificate issues
ctx = ssl.create_default_context()

def wikimedia_api(params):
    """Call Wikimedia API and return JSON"""
    base = "https://commons.wikimedia.org/w/api.php"
    query = urllib.parse.urlencode(params)
    url = f"{base}?{query}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ThaiHillTribeScraper/1.0 (henry@artlevers.com)'})
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
    
    while True:
        data = wikimedia_api(params)
        if not data or "query" not in data:
            break
        
        pages = data["query"].get("pages", {})
        for page_id, page in pages.items():
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
        
        if "continue" not in data:
            break
        params.update(data["continue"])
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
    
    while True:
        data = wikimedia_api(params)
        if not data or "query" not in data:
            break
        
        pages = data["query"].get("pages", {})
        for page_id, page in pages.items():
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
                            "category": query
                        })
        
        if "continue" not in data:
            break
        params.update(data["continue"])
        time.sleep(0.3)
    
    return images

def download_image(url, filepath):
    """Download an image from URL"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ThaiHillTribeScraper/1.0 (henry@artlevers.com)'})
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = resp.read()
            with open(filepath, 'wb') as f:
                f.write(data)
            return len(data)
    except Exception as e:
        print(f"  Download error: {e}")
        return 0

def sanitize_filename(name):
    """Create safe filename"""
    return name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "").replace("*", "")

def main():
    print("=" * 60)
    print("Thai Hill Tribes Visual Reference Scraper")
    print("=" * 60)
    
    total_downloaded = 0
    total_errors = 0
    
    for tribe in TRIBES:
        tribe_dir = os.path.join(BASE_DIR, tribe["name"])
        os.makedirs(tribe_dir, exist_ok=True)
        
        print(f"\n{'='*50}")
        print(f"Tribe: {tribe['name']} ({tribe['thai']})")
        print(f"{'='*50}")
        
        all_images = []
        
        # Try main category
        print(f"  Searching category: {tribe['category']}...")
        images = get_images_from_category(tribe["category"], limit=30)
        all_images.extend(images)
        print(f"  Found {len(images)} images from main category")
        
        # Try subcategories
        for subcat in tribe.get("subcategories", []):
            print(f"  Searching subcategory: {subcat}...")
            sub_images = get_images_from_category(subcat, limit=20)
            all_images.extend(sub_images)
            print(f"  Found {len(sub_images)} images from {subcat}")
        
        # Try Thai language search
        thai_search = f"{tribe['thai']} costume clothing"
        print(f"  Searching Thai: '{thai_search}'...")
        thai_images = search_images(f"{tribe['thai']} costume OR {tribe['thai']} clothing OR {tribe['thai']} dress", limit=20)
        all_images.extend(thai_images)
        print(f"  Found {len(thai_images)} images from Thai search")
        
        # Try English search
        eng_search = f"{tribe['name']} Thailand traditional costume"
        print(f"  Searching English: '{eng_search}'...")
        eng_images = search_images(f"{tribe['name']} Thailand traditional costume OR {tribe['name']} traditional dress OR {tribe['name']} clothing", limit=20)
        all_images.extend(eng_images)
        print(f"  Found {len(eng_images)} images from English search")
        
        # Remove duplicates by URL
        seen = set()
        unique_images = []
        for img in all_images:
            if img["url"] not in seen:
                seen.add(img["url"])
                unique_images.append(img)
        
        print(f"\n  Total unique images: {len(unique_images)}")
        
        # Download images (limit to top 15 per tribe to avoid excessive downloads)
        downloaded = 0
        for i, img in enumerate(unique_images[:15]):
            ext = ".jpg"
            if "png" in img.get("url", "").lower():
                ext = ".png"
            
            safe_name = sanitize_filename(img["filename"])
            if not safe_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                safe_name += ext
            
            filepath = os.path.join(tribe_dir, safe_name)
            
            # Skip if already exists
            if os.path.exists(filepath):
                print(f"  [{i+1}/{len(unique_images[:15])}] SKIP (exists): {safe_name}")
                downloaded += 1
                continue
            
            size = download_image(img["url"], filepath)
            if size > 0:
                print(f"  [{i+1}/{len(unique_images[:15])}] OK: {safe_name} ({size/1024:.0f}KB)")
                downloaded += 1
                total_downloaded += 1
            else:
                print(f"  [{i+1}/{len(unique_images[:15])}] FAIL: {safe_name}")
                total_errors += 1
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n  Tribe '{tribe['name']}': downloaded {downloaded} images")
    
    print(f"\n{'='*60}")
    print(f"COMPLETE!")
    print(f"Total images downloaded: {total_downloaded}")
    print(f"Total errors: {total_errors}")
    print(f"Location: {BASE_DIR}")
    print(f"{'='*60}")
    
    # List all created folders
    print(f"\nFolder structure:")
    for tribe in TRIBES:
        tribe_dir = os.path.join(BASE_DIR, tribe["name"])
        if os.path.exists(tribe_dir):
            files = [f for f in os.listdir(tribe_dir) if os.path.isfile(os.path.join(tribe_dir, f))]
            print(f"  📁 {tribe['name']} ({tribe['thai']}): {len(files)} images")

if __name__ == "__main__":
    main()
