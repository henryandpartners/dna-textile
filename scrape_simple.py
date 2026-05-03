#!/usr/bin/env python3
"""
Simple Thai Hill Tribes Image Scraper
Downloads images from Wikimedia Commons
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import time
import ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create SSL context
ctx = ssl.create_default_context()

# Tribes to scrape
TRIBES = [
    ("Karen", "กะเหรี่ยง", ["Karen_people", "Sgaw_Karen", "Pwo_Karen"]),
    ("Hmong", "ม้ง", ["Hmong", "White_Hmong", "Green_Hmong"]),
    ("Akha", "อาข่า", ["Akha"]),
    ("Lisu", "ลีซอ", ["Lisu_people"]),
    ("Mien", "เย้า", ["Iu_Mien_people"]),
    ("Lahu", "ลาหู่", ["Lahu_people"]),
    ("Lawa", "ละว้า", ["Lawá_people"]),
    ("Wa", "ว้า", ["Wa_people"]),
    ("Mlabri", "มละบรี", ["Mlabri_people"]),
    ("Khamu", "ขมุ", ["Khmu_people"]),
    ("Shan", "ฉาน", ["Shan_people"]),
    ("Palong", "ปォลำผี่", ["Palaung_people"]),
]

def get_category_images(category, max_images=20):
    """Get images from Wikimedia Commons category"""
    images = []
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
                    if "imageinfo" in page and len(images) < max_images:
                        for info in page["imageinfo"]:
                            img_url = info.get("url")
                            if img_url and "image" in info.get("mime", ""):
                                images.append({
                                    "url": img_url,
                                    "name": page["title"].replace("File:", ""),
                                    "size": info.get("size", 0)
                                })
    except Exception as e:
        print(f"    Error fetching {category}: {e}")
    
    return images

def download_image(url, filepath):
    """Download image"""
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
        return False

def main():
    print("=" * 60)
    print("Thai Hill Tribes Visual Reference Scraper")
    print("=" * 60)
    
    total = 0
    
    for tribe_name, thai_name, categories in TRIBES:
        print(f"\n📁 {tribe_name} ({thai_name})")
        
        # Create folder
        tribe_dir = os.path.join(BASE_DIR, tribe_name)
        os.makedirs(tribe_dir, exist_ok=True)
        
        # Collect images from all categories
        all_images = []
        for cat in categories:
            print(f"  🔍 Category: {cat}")
            imgs = get_category_images(cat, max_images=15)
            all_images.extend(imgs)
            print(f"    Found: {len(imgs)} images")
            time.sleep(0.5)
        
        # Remove duplicates
        seen = set()
        unique = []
        for img in all_images:
            if img["url"] not in seen:
                seen.add(img["url"])
                unique.append(img)
        
        print(f"  📊 Total unique: {len(unique)}")
        
        # Download (top 10)
        downloaded = 0
        for i, img in enumerate(unique[:10]):
            # Sanitize filename
            safe_name = img["name"].replace("/", "_").replace("\\", "_")
            if not safe_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                safe_name += ".jpg"
            
            filepath = os.path.join(tribe_dir, safe_name)
            
            if os.path.exists(filepath):
                print(f"  [{i+1}] SKIP: {safe_name}")
                downloaded += 1
                continue
            
            if download_image(img["url"], filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"  [{i+1}] ✓ {safe_name} ({size_kb:.0f}KB)")
                downloaded += 1
                total += 1
            else:
                print(f"  [{i+1}] ✗ {safe_name}")
            
            time.sleep(0.3)
        
        print(f"  ✅ Downloaded: {downloaded} images")
    
    print(f"\n{'='*60}")
    print(f"🎉 DONE! Total images: {total}")
    print(f"📂 Location: {BASE_DIR}")
    print(f"{'='*60}")
    
    # Summary
    print("\n📁 Folder Summary:")
    for tribe_name, thai_name, _ in TRIBES:
        tribe_dir = os.path.join(BASE_DIR, tribe_name)
        if os.path.exists(tribe_dir):
            files = [f for f in os.listdir(tribe_dir) if os.path.isfile(os.path.join(tribe_dir, f))]
            print(f"  {tribe_name} ({thai_name}): {len(files)} images")

if __name__ == "__main__":
    main()
