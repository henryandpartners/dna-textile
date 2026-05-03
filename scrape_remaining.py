#!/usr/bin/env python3
"""
Continue scraping remaining Thai hill tribes
Handles rate limiting with delays
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import time
import ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ctx = ssl.create_default_context()

# Remaining tribes to scrape
TRIBES = [
    ("Lisu", "ลีซอ", ["Lisu_people", "Lisu_costume"]),
    ("Mien", "เย้า", ["Iu_Mien_people", "Iu_Mien_costume"]),
    ("Lahu", "ลาหู่", ["Lahu_people", "Lahu_costume"]),
    ("Lawa", "ละว้า", ["Lawá_people", "Lua_people"]),
    ("Wa", "ว้า", ["Wa_people", "Wa_state"]),
    ("Mlabri", "มละบรี", ["Mlabri_people", "Philippines_indigenous_peoples"]),
    ("Khamu", "ขมุ", ["Khmu_people"]),
    ("Shan", "ฉาน", ["Shan_people", "Shan_state"]),
    ("Palong", "ปォลำผี่", ["Palaung_people", "Taang_people"]),
    ("Karen_Sgaw", "กะเหรี่ยงสะกอ", ["Sgaw_Karen"]),
    ("Karen_Pwo", "กะเหรี่ยงโปว์", ["Pwo_Karen"]),
    ("Hmong_White", "ม้งขาว", ["White_Hmong"]),
    ("Hmong_Green", "ม้งเขียว", ["Green_Hmong"]),
]

def get_images(category, max_imgs=15):
    """Get images from category with retry"""
    images = []
    for attempt in range(3):
        try:
            params = {
                "action": "query",
                "generator": "categorymembers",
                "gcmtitle": f"Category:{category}",
                "gcmlimit": "50",
                "gcmtype": "file",
                "prop": "imageinfo",
                "iiprop": "url|size",
                "iiurlwidth": "1000",
                "format": "json"
            }
            
            url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers={
                'User-Agent': 'ThaiHillTribeScraper/1.0'
            })
            
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                
                if "query" in data:
                    for page_id, page in data["query"].get("pages", {}).items():
                        if "imageinfo" in page and len(images) < max_imgs:
                            for info in page["imageinfo"]:
                                img_url = info.get("url")
                                if img_url and "image" in info.get("mime", ""):
                                    images.append({
                                        "url": img_url,
                                        "name": page["title"].replace("File:", ""),
                                        "size": info.get("size", 0)
                                    })
                return images
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 5
                print(f"    ⏳ Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    ❌ HTTP {e.code}")
                return []
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return []
    
    return images

def download(url, filepath):
    """Download image with retry"""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'ThaiHillTribeScraper/1.0'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                data = resp.read()
                with open(filepath, 'wb') as f:
                    f.write(data)
                return True
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                return False

def main():
    print("=" * 60)
    print("Continuing Thai Hill Tribes Scraping")
    print("=" * 60)
    
    total = 0
    
    for tribe_name, thai_name, categories in TRIBES:
        print(f"\n📁 {tribe_name} ({thai_name})")
        
        tribe_dir = os.path.join(BASE_DIR, tribe_name)
        os.makedirs(tribe_dir, exist_ok=True)
        
        # Check if already has images
        existing = [f for f in os.listdir(tribe_dir) if os.path.isfile(os.path.join(tribe_dir, f))]
        if len(existing) > 5:
            print(f"  ⏭️  Already has {len(existing)} images, skipping")
            continue
        
        all_images = []
        for cat in categories:
            print(f"  🔍 {cat}...")
            imgs = get_images(cat, max_imgs=15)
            all_images.extend(imgs)
            print(f"    Found: {len(imgs)}")
            time.sleep(1)  # Rate limit delay
        
        # Deduplicate
        seen = set()
        unique = []
        for img in all_images:
            if img["url"] not in seen:
                seen.add(img["url"])
                unique.append(img)
        
        print(f"  📊 Unique: {len(unique)}")
        
        # Download
        downloaded = 0
        for i, img in enumerate(unique[:10]):
            safe_name = img["name"].replace("/", "_").replace("\\", "_")
            if not safe_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                safe_name += ".jpg"
            
            filepath = os.path.join(tribe_dir, safe_name)
            
            if os.path.exists(filepath):
                print(f"  [{i+1}] SKIP")
                downloaded += 1
                continue
            
            if download(img["url"], filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"  [{i+1}] ✓ {size_kb:.0f}KB")
                downloaded += 1
                total += 1
            else:
                print(f"  [{i+1}] ✗")
            
            time.sleep(0.5)
        
        print(f"  ✅ Done: {downloaded} images")
        time.sleep(2)  # Longer delay between tribes
    
    print(f"\n{'='*60}")
    print(f"🎉 Complete! New images: {total}")
    print(f"{'='*60}")
    
    # Final summary
    print("\n📁 Final Summary:")
    for tribe_name, thai_name, _ in TRIBES:
        tribe_dir = os.path.join(BASE_DIR, tribe_name)
        if os.path.exists(tribe_dir):
            files = [f for f in os.listdir(tribe_dir) if os.path.isfile(os.path.join(tribe_dir, f))]
            print(f"  {tribe_name} ({thai_name}): {len(files)} images")

if __name__ == "__main__":
    main()
