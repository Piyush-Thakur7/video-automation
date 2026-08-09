import os
import requests
import random
import urllib.parse
import urllib.request
import json
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

DEFAULT_PEXELS_KEY = "f9pRnqk0T38aFRraTo5NugtO8ow9AJ1u6TBBoBAtqv4yrlv3Sz5g4CyU"

class AssetManager:
    def __init__(self, pexels_key: str = None, pixabay_key: str = None, storage_dir: str = "storage/assets"):
        self.pexels_key = pexels_key or os.getenv("PEXELS_API_KEY", DEFAULT_PEXELS_KEY)
        self.pixabay_key = pixabay_key or os.getenv("PIXABAY_API_KEY", "")
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def fetch_scene_media(self, search_term: str, is_shorts: bool = True, scene_idx: int = 1) -> str:
        """
        Attempts to fetch stock media from Pexels/Pixabay, Wikimedia Commons, or falls back to procedural graphics.
        """
        resolution = (1080, 1920) if is_shorts else (1920, 1080)
        file_prefix = f"scene_{scene_idx}_{'shorts' if is_shorts else 'landscape'}"

        # 1. Try Pexels API if key available
        if self.pexels_key:
            try:
                headers = {"Authorization": self.pexels_key}
                orientation = "portrait" if is_shorts else "landscape"
                url = f"https://api.pexels.com/videos/search?query={search_term}&orientation={orientation}&per_page=3"
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("videos"):
                        video = random.choice(data["videos"])
                        video_files = video.get("video_files", [])
                        hd_files = [f for f in video_files if f.get("width") and f["width"] >= 720]
                        target = hd_files[0] if hd_files else video_files[0]
                        
                        out_path = os.path.join(self.storage_dir, f"{file_prefix}_pexels.mp4")
                        v_data = requests.get(target["link"], timeout=10).content
                        with open(out_path, "wb") as f:
                            f.write(v_data)
                        return out_path
            except Exception as e:
                print(f"[AssetManager] Pexels fetch warning: {e}")

        # 2. Try Pixabay API if key available
        if self.pixabay_key:
            try:
                url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={search_term}&per_page=3"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("hits"):
                        hit = random.choice(data["hits"])
                        v_url = hit["videos"]["medium"]["url"]
                        out_path = os.path.join(self.storage_dir, f"{file_prefix}_pixabay.mp4")
                        v_data = requests.get(v_url, timeout=10).content
                        with open(out_path, "wb") as f:
                            f.write(v_data)
                        return out_path
            except Exception as e:
                print(f"[AssetManager] Pixabay fetch warning: {e}")

        # 3. Try NASA Official Public Domain Media Library
        try:
            nasa_url = self._fetch_nasa_media(search_term)
            if nasa_url:
                out_path = os.path.join(self.storage_dir, f"{file_prefix}_nasa.jpg")
                headers = {'User-Agent': 'AutoTubeBot/1.0'}
                req = urllib.request.Request(nasa_url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp, open(out_path, 'wb') as f:
                    f.write(resp.read())
                return out_path
        except Exception as e:
            print(f"[AssetManager] NASA fetch warning: {e}")

        # 4. Try Wikimedia Commons Public Stock Image Engine
        try:
            wiki_url = self._fetch_wikimedia_image(search_term)
            if wiki_url:
                out_path = os.path.join(self.storage_dir, f"{file_prefix}_wikimedia.jpg")
                headers = {'User-Agent': 'AutoTubeBot/1.0 (contact@autotube.ai)'}
                req = urllib.request.Request(wiki_url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp, open(out_path, 'wb') as f:
                    f.write(resp.read())
                return out_path
        except Exception as e:
            print(f"[AssetManager] Wikimedia fetch warning: {e}")

        # 5. Fallback: Generate custom high-end procedural gradient background image
        return self._generate_procedural_background(search_term, resolution, file_prefix)

    def _fetch_nasa_media(self, search_term: str) -> str:
        url = f"https://images-api.nasa.gov/search?q={urllib.parse.quote(search_term)}&media_type=image"
        req = urllib.request.Request(url, headers={'User-Agent': 'AutoTubeBot/1.0'})
        res = json.loads(urllib.request.urlopen(req, timeout=5).read())
        items = res.get('collection', {}).get('items', [])
        if items:
            item = random.choice(items[:5])
            links = item.get('links', [])
            if links:
                return links[0]['href']
        return None

    def _fetch_wikimedia_image(self, search_term: str) -> str:
        url1 = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_term)}&srnamespace=6&format=json"
        req1 = urllib.request.Request(url1, headers={'User-Agent': 'AutoTubeBot/1.0'})
        res1 = json.loads(urllib.request.urlopen(req1, timeout=5).read())
        items = res1.get('query', {}).get('search', [])

        for item in items:
            title = item['title']
            if title.lower().endswith(('.jpg', '.jpeg', '.png')):
                url2 = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&format=json"
                req2 = urllib.request.Request(url2, headers={'User-Agent': 'AutoTubeBot/1.0'})
                res2 = json.loads(urllib.request.urlopen(req2, timeout=5).read())
                pages = res2.get('query', {}).get('pages', {})
                for p in pages.values():
                    if 'imageinfo' in p and p['imageinfo']:
                        return p['imageinfo'][0]['url']
        return None

    def _generate_procedural_background(self, search_term: str, size: tuple, prefix: str) -> str:
        width, height = size
        img = Image.new("RGB", size)
        draw = ImageDraw.Draw(img)

        palette_pairs = [
            ((15, 23, 42), (88, 28, 135)),
            ((10, 10, 20), (225, 29, 72)),
            ((6, 78, 59), (15, 23, 42)),
            ((30, 27, 75), (6, 182, 212)),
            ((24, 24, 27), (217, 119, 6))
        ]

        c1, c2 = random.choice(palette_pairs)

        for y in range(height):
            ratio = y / height
            r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
            g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
            b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        grid_step = 80
        for x in range(0, width, grid_step):
            draw.line([(x, 0), (x, height)], fill=(255, 255, 255, 8), width=1)
        for y in range(0, height, grid_step):
            draw.line([(0, y), (width, y)], fill=(255, 255, 255, 8), width=1)

        center_x, center_y = width // 2, height // 2
        for radius in range(300, 0, -20):
            alpha = int(25 * (1 - radius / 300))
            draw.ellipse(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                outline=(255, 255, 255, alpha),
                width=2
            )

        out_path = os.path.join(self.storage_dir, f"{prefix}_procedural.jpg")
        img.save(out_path, quality=95)
        return out_path

asset_manager = AssetManager()
