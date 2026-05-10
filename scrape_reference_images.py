#!/usr/bin/env python3
"""
DNA Textile — Reference Image Scraper v2
Multi-source scraper for tribal textile/costume/pattern references.
Sources: Wikimedia Commons.
Filters out landscapes/architecture — prioritizes textiles, costumes, patterns.
"""

import os, json, re, time, ssl
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(BASE_DIR, "reference_images")
ctx = ssl.create_default_context()

# ── Image relevance filter ──
GOOD_KEYWORDS = [
    "costume", "textile", "weaving", "embroidery", "pattern", "cloth",
    "fabric", "dress", "clothing", "garment", "hat", "headdress",
    "neckring", "neck ring", "jewelry", "jewellery", "ornament",
    "shawl", "skirt", "jacket", "tunic", "wrap", "scarf",
    "embroider", "applique", "batik", "ikat", "tie-dye", "dye",
    "loom", "thread", "yarn", "cotton", "silk", "hemp",
    "motif", "design", "decoration", "decorative", "ornamental",
    "traditional", "ceremonial", "ritual", "festival",
    "ผ้า", "ปัก", "ทอ", "เสื้อผ้า", "เครื่องแต่ง", "ลวดลาย",
    "เครื่องประดับ",
]

BAD_KEYWORDS = [
    "panorama", "landscape", "aerial", "map", "satellite",
    "river", "mountain", "village overview", "rice field",
    "church", "temple", "pagoda", "building", "architecture",
    "logo", "flag", "coat of arms",
    "portrait of", "photo of group", "group photo",
    "tsai ing", "yeh chu", "hong kong", "wan chai",
    "clergy from iran", "magasin d", "american forestry",
    "finland", "masquerade", "national museum", "costume parade",
    "costume collection", "costumes in a", "best costumes",
    "the truth about china", "harvard classics", "korea (1905)",
    "daughter of heaven", "histoi", "revue blanche",
    "gautier, loti", "ny times", "new york times",
    "audibert hist", "peladan", "renne-dunan",
    "the history of korea",
    "berita industri",
]

# Tribe name patterns (regex) for strict matching
TRIBE_PATTERNS = {
    "tai lue": [r"tai\s*l[üu]e", r"l[üu]e\s+(woman|man|girl|textile|costume|people|dress)", r"ไทลื้อ"],
    "tai dam": [r"tai\s*dam", r"black\s*tai", r"ไทดำ"],
    "hmong": [r"\bhmong\b", r"\bmiao\b", r"\bม้ง\b"],
    "karen": [r"\bkaren\b", r"\bกะเหรี่ยง\b", r"\bsgaw\b", r"\bpwo\b"],
    "mien": [r"\bmien\b", r"\byao\b", r"\biu\s*mien\b", r"\bเมี่ยน\b"],
    "akha": [r"\bakha\b", r"\baka\s+(people|woman|man)\b", r"\bอาข่า\b"],
    "lahu": [r"\blahu\b", r"\bลาหู่\b"],
    "lisu": [r"\blisu\b", r"\bลีซอ\b"],
    "khamu": [r"\bkhamu\b", r"\bkhmu\b", r"\bขมุ\b"],
    "palaung": [r"\bpalaung\b", r"\bde['']ang\b", r"\bปะหล่อง\b"],
    "lua": [r"\blua\b", r"\blawa\b", r"\bลัวะ\b"],
    "mani": [r"\bmani\s+(people|tribe)\b", r"\bมานิ\b"],
    "mlabri": [r"\bmlabri\b", r"\bมละบรี\b", r"yellow\s*leaves"],
    "moklen": [r"\bmoklen\b", r"\bmoken\b", r"\bมอแกน\b", r"sea\s*gyps"],
    "urak lawoi": [r"\burak\s*lawoi\b", r"\buraklawoi\b", r"\bอูรัก\b"],
}


def is_relevant(filename, description="", category="", tribe_name=""):
    """Check if an image is relevant to textile/costume research."""
    # For tribe matching, ONLY use filename + description (NOT the search query)
    # Otherwise search queries like "Black Tai costume" will match any result
    text_for_tribe = f"{filename} {description}".lower()
    text_all = f"{filename} {description} {category}".lower()

    # Reject bad keywords
    for kw in BAD_KEYWORDS:
        if kw in text_all:
            return False

    # Must have at least one good keyword
    if not any(kw in text_all for kw in GOOD_KEYWORDS):
        return False

    # If tribe specified, require tribe name match in filename/description only
    if tribe_name:
        tribe_lower = tribe_name.lower().strip()
        patterns = TRIBE_PATTERNS.get(tribe_lower, [r"\b" + re.escape(tribe_lower) + r"\b"])
        if not any(re.search(p, text_for_tribe) for p in patterns):
            return False

    return True


def wiki_api(params):
    base = "https://commons.wikimedia.org/w/api.php"
    query = urllib.parse.urlencode(params)
    url = f"{base}?{query}"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'DNATextileScraper/2.0 (henry@artlevers.com)'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def get_images_from_category(category, limit=50, tribe_name=""):
    images = []
    params = {
        "action": "query", "generator": "categorymembers",
        "gcmtitle": f"Category:{category}", "gcmlimit": min(limit, 50),
        "gcmtype": "file", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200", "format": "json"
    }
    for _ in range(5):
        data = wiki_api(params)
        if not data or "query" not in data:
            break
        for page in data["query"].get("pages", {}).values():
            if "imageinfo" in page:
                for info in page["imageinfo"]:
                    url = info.get("url", "")
                    mime = info.get("mime", "")
                    if url and mime.startswith("image/"):
                        desc = ""
                        if "extmetadata" in info:
                            desc = info["extmetadata"].get("ImageDescription", {}).get("value", "")
                        if is_relevant(page["title"], desc, category, tribe_name):
                            images.append({
                                "url": url,
                                "filename": page["title"].replace("File:", ""),
                                "description": desc,
                                "size": info.get("size", 0),
                                "width": info.get("width", 0),
                                "height": info.get("height", 0),
                                "category": category
                            })
        cont = data.get("continue")
        if not cont:
            break
        params.update(cont)
        time.sleep(0.3)
    return images


def search_images(query, limit=30, tribe_name=""):
    images = []
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": 6,
        "gsrlimit": min(limit, 50), "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200", "format": "json"
    }
    for _ in range(3):
        data = wiki_api(params)
        if not data or "query" not in data:
            break
        for page in data["query"].get("pages", {}).values():
            if "imageinfo" in page:
                for info in page["imageinfo"]:
                    url = info.get("url", "")
                    mime = info.get("mime", "")
                    if url and mime.startswith("image/"):
                        desc = ""
                        if "extmetadata" in info:
                            desc = info["extmetadata"].get("ImageDescription", {}).get("value", "")
                        if is_relevant(page["title"], desc, query, tribe_name):
                            images.append({
                                "url": url,
                                "filename": page["title"].replace("File:", ""),
                                "description": desc,
                                "size": info.get("size", 0),
                                "width": info.get("width", 0),
                                "height": info.get("height", 0),
                                "query": query
                            })
        cont = data.get("continue")
        if not cont:
            break
        params.update(cont)
        time.sleep(0.3)
    return images


def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'DNATextileScraper/2.0 (henry@artlevers.com)'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = resp.read()
            if len(data) < 10_000:
                return -1  # too small
            with open(filepath, 'wb') as f:
                f.write(data)
            return len(data)
    except Exception:
        return 0


def sanitize(name):
    return re.sub(r'[\/\\:*?"<>|]', '_', name)[:120]


# ── Community configs ──
COMMUNITIES = {
    "Akha": {
        "thai": "อาข่า",
        "categories": ["Akha", "Akha_costume"],
        "searches": [
            "Akha costume Thailand", "Akha headdress", "Akha clothing traditional",
            "อาข่า เสื้อผ้า", "อาข่า เครื่องแต่งกาย",
            "Akha woman costume", "Akha silver jewelry",
        ]
    },
    "Hmong": {
        "thai": "ม้ง",
        "categories": ["Hmong", "Hmong_costume", "Hmong_textiles", "Hmong_embroidery", "Paj_naub"],
        "searches": [
            "Hmong textile embroidery", "Hmong paj ntaub", "Hmong traditional costume Thailand",
            "ม้ง ผ้าปัก", "Hmong indigo batik", "Hmong pleated skirt",
            "Hmong appliqué", "Hmong costume Laos Vietnam",
        ]
    },
    "Karen": {
        "thai": "กะเหรี่ยง",
        "categories": ["Karen_people", "Karen_costume", "Sgaw_Karen", "Pwo_Karen", "Karen_textiles"],
        "searches": [
            "Karen traditional costume Thailand", "Karen weaving", "Karen textile pattern",
            "กะเหรี่ยง ผ้าทอ", "กะเหรี่ยง เสื้อผ้า",
            "Karen backstrap loom", "Karen woven bag",
        ]
    },
    "Khamu": {
        "thai": "ขมุ",
        "categories": ["Khmu_people"],
        "searches": [
            "Khmu traditional costume Laos", "Khmu textile", "Khmu weaving",
            "ขมุ ผ้าทอ", "Khmu clothing", "Khamu traditional dress",
        ]
    },
    "Lahu": {
        "thai": "ลาหู่",
        "categories": ["Lahu_people", "Lahu_costume"],
        "searches": [
            "Lahu traditional costume Thailand", "Lahu textile", "Lahu clothing",
            "ลาหู่ เสื้อผ้า", "Lahu black costume", "Lahu embroidery",
        ]
    },
    "Lisu": {
        "thai": "ลีซอ",
        "categories": ["Lisu_people", "Lisu_costume"],
        "searches": [
            "Lisu traditional costume Thailand", "Lisu textile", "Lisu embroidery",
            "ลีซอ เสื้อผ้า", "Lisu appliqué costume", "Lisu colorful dress",
        ]
    },
    "Lua": {
        "thai": "ลัวะ",
        "categories": ["Lua_people"],
        "searches": [
            "Lua traditional costume Thailand", "Lua textile weaving",
            "ลัวะ ผ้าทอ", "Lua clothing", "Lawa Thailand traditional",
        ]
    },
    "Mani": {
        "thai": "มานิ",
        "categories": [],
        "searches": [
            "Mani people Thailand", "Mani Semang traditional",
            "มานิ", "Mani Negrito clothing",
        ]
    },
    "Mien": {
        "thai": "เย้า/เมี่ยน",
        "categories": ["Iu_Mien_people", "Iu_Mien_costume", "Yao_people"],
        "searches": [
            "Iu Mien traditional costume", "Yao embroidery China Vietnam",
            "เมี่ยน เสื้อผ้า", "Mien textile pattern",
            "Yao traditional dress", "Mien ceremonial costume",
        ]
    },
    "Mlabri": {
        "thai": "มละบรี",
        "categories": [],
        "searches": [
            "Mlabri people Thailand", "Mlabri yellow leaves",
            "มละบรี", "Spirit of the yellow leaves",
        ]
    },
    "Moklen": {
        "thai": "มอแกน",
        "categories": ["Moken_people"],
        "searches": [
            "Moken sea gypsy", "Moken traditional", "Moklen",
            "มอแกน", "Mergui sea gypsy clothing",
        ]
    },
    "Palaung": {
        "thai": "ปะหล่อง",
        "categories": ["Palaung_people", "Palaung_costume"],
        "searches": [
            "Palaung traditional costume", "Palaung textile weaving",
            "ปะหล่อง ผ้าทอ", "Palaung clothing", "De'ang traditional costume",
        ]
    },
    "Tai Dam": {
        "thai": "ไทดำ",
        "categories": ["Tai_Dam"],
        "searches": [
            "Tai Dam traditional costume", "Tai Dam textile",
            "ไทดำ ผ้าทอ", "Black Tai costume", "Tai Dón clothing",
        ]
    },
    "Tai Lue": {
        "thai": "ไทลื้อ",
        "categories": ["Tai_Lue", "Tai_lue_textiles"],
        "searches": [
            "Tai Lue traditional costume", "Tai Lue textile",
            "ไทลื้อ ผ้าทอ", "Tai Lü clothing", "Xishuangbanna Tai Lue",
        ]
    },
    "Urak Lawoi": {
        "thai": "อูรักลาโว้ย",
        "categories": [],
        "searches": [
            "Urak Lawoi sea gypsy", "Urak Lawoi traditional",
            "อูรักลาโว้ย", "Thai sea gypsy clothing",
        ]
    },
}


def scrape_community(name, config, max_images=15, dry_run=False):
    print(f"\n{'='*55}")
    print(f"  {name} ({config['thai']})")
    print(f"{'='*55}")

    tribe_dir = os.path.join(REF_DIR, name)
    os.makedirs(tribe_dir, exist_ok=True)

    all_images = []
    seen_urls = set()

    # Categories
    for cat in config.get("categories", []):
        print(f"  Category: {cat}")
        imgs = get_images_from_category(cat, limit=50, tribe_name=name)
        for img in imgs:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                all_images.append(img)
        print(f"    -> {len(imgs)} relevant")

    # Searches
    for q in config.get("searches", []):
        print(f"  Search: {q[:50]}")
        imgs = search_images(q, limit=20, tribe_name=name)
        for img in imgs:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                all_images.append(img)
        print(f"    -> {len(imgs)} relevant")

    print(f"\n  Total relevant: {len(all_images)}")

    # Download
    downloaded = 0
    errors = 0
    manifest = []

    for i, img in enumerate(all_images[:max_images]):
        ext = ".jpg"
        ul = img["url"].lower()
        if "png" in ul: ext = ".png"
        elif "tif" in ul: ext = ".tiff"
        elif "gif" in ul: ext = ".gif"
        elif "svg" in ul: ext = ".svg"

        safe = sanitize(img["filename"])
        if not safe.lower().endswith(('.jpg','.jpeg','.png','.gif','.tiff','.svg','.webp')):
            safe += ext

        filepath = os.path.join(tribe_dir, safe)
        rel = os.path.join(name, safe)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 10_000:
            print(f"  SKIP [{i+1}] {rel}")
            downloaded += 1
            manifest.append({**img, "local_path": rel, "status": "exists"})
            continue

        if dry_run:
            print(f"  WOULD [{i+1}] {rel}")
            manifest.append({**img, "local_path": rel, "status": "dry_run"})
            continue

        size = download_image(img["url"], filepath)
        if size > 0:
            print(f"  OK [{i+1}] {rel} ({size//1024}KB)")
            downloaded += 1
            manifest.append({**img, "local_path": rel, "status": "ok", "bytes": size})
        else:
            status = "tiny/skipped" if size == -1 else "fail"
            print(f"  FAIL [{i+1}] {status}")
            errors += 1
            manifest.append({**img, "local_path": rel, "status": status})

        time.sleep(0.5)

    # Manifest
    with open(os.path.join(tribe_dir, "manifest.json"), "w") as f:
        json.dump({
            "community": name, "thai": config["thai"],
            "total_found": len(all_images), "downloaded": downloaded,
            "errors": errors, "max_images": max_images, "images": manifest
        }, f, indent=2, ensure_ascii=False)

    print(f"  Done: {downloaded} downloaded | {errors} errors")
    return downloaded, errors


def main():
    import argparse
    p = argparse.ArgumentParser(description="DNA Textile Reference Image Scraper v2")
    p.add_argument("--all", action="store_true")
    p.add_argument("--tribe", type=str)
    p.add_argument("--list", action="store_true")
    p.add_argument("--max", type=int, default=15)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    os.makedirs(REF_DIR, exist_ok=True)

    if args.list:
        print(f"{'Community':<16} {'Thai':<12} {'Ref Images':<12} {'Manifest'}")
        print("-" * 55)
        for name, cfg in sorted(COMMUNITIES.items()):
            d = os.path.join(REF_DIR, name)
            exists = os.path.isdir(d)
            count = len([f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) and not f.endswith('.json')]) if exists else 0
            has_m = "yes" if exists and os.path.exists(os.path.join(d, "manifest.json")) else ""
            status = f"{count}" if count > 0 else ("empty" if exists else "none")
            print(f"{name:<16} {cfg['thai']:<12} {status:<12} {has_m}")
        return

    if args.tribe:
        if args.tribe not in COMMUNITIES:
            print(f"Unknown: {args.tribe}")
            print(f"Available: {', '.join(sorted(COMMUNITIES.keys()))}")
            return
        scrape_community(args.tribe, COMMUNITIES[args.tribe], args.max, args.dry_run)
        return

    if args.all:
        total_dl = total_err = 0
        for name, cfg in sorted(COMMUNITIES.items()):
            dl, err = scrape_community(name, cfg, args.max, args.dry_run)
            total_dl += dl
            total_err += err
            time.sleep(1)
        print(f"\n{'='*55}")
        print(f"COMPLETE! Downloaded: {total_dl} | Errors: {total_err}")
        print(f"Location: {REF_DIR}")
        print(f"{'='*55}")
        return

    p.print_help()
    print(f"\nExamples:")
    print(f"  python3 {os.path.basename(__file__)} --list")
    print(f"  python3 {os.path.basename(__file__)} --tribe 'Hmong' --max 20")
    print(f"  python3 {os.path.basename(__file__)} --all --max 15")
    print(f"  python3 {os.path.basename(__file__)} --all --dry-run")

if __name__ == "__main__":
    main()
