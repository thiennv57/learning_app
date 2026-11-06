"""
Download player face images from Wikipedia API (freely licensed).
Saves to static/players/{id}.png
"""
import os, sys, urllib.request, urllib.parse, json, ssl

# Bypass SSL verification for school/work networks
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SAVE_DIR = os.path.join(os.path.dirname(__file__), 'static', 'players')
os.makedirs(SAVE_DIR, exist_ok=True)

# Player ID -> Wikipedia article title
PLAYERS = {
    'mbappe':     'Kylian Mbappé',
    'haaland':    'Erling Haaland',
    'yamal':      'Lamine Yamal',
    'kane':       'Harry Kane',
    'bellingham': 'Jude Bellingham',
    'vini':       'Vinícius Júnior',
    'pedri':      'Pedri',
    'kdb':        'Kevin De Bruyne',
    'donna':      'Gianluigi Donnarumma',
    'alvarez':    'Julián Álvarez',
    'courtois':   'Thibaut Courtois',
}

WIKI_API = 'https://en.wikipedia.org/w/api.php'

def get_wiki_image_url(title, thumb_size=250):
    """Get the main image URL for a Wikipedia article."""
    params = urllib.parse.urlencode({
        'action': 'query',
        'titles': title,
        'prop': 'pageimages',
        'format': 'json',
        'pithumbsize': thumb_size,
        'redirects': 1,
    })
    url = f'{WIKI_API}?{params}'
    req = urllib.request.Request(url, headers={'User-Agent': 'LearningApp/1.0'})
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    pages = data.get('query', {}).get('pages', {})
    for page_id, page_data in pages.items():
        thumb = page_data.get('thumbnail', {})
        return thumb.get('source')
    return None

def download_image(url, save_path):
    """Download an image from URL to local path."""
    req = urllib.request.Request(url, headers={'User-Agent': 'LearningApp/1.0'})
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = resp.read()
    with open(save_path, 'wb') as f:
        f.write(data)
    return len(data)

def main():
    print("=== Downloading player face images from Wikipedia ===\n")
    success = 0
    for player_id, wiki_title in PLAYERS.items():
        save_path = os.path.join(SAVE_DIR, f'{player_id}.png')
        if os.path.exists(save_path):
            print(f"  [SKIP] {player_id} - already exists")
            success += 1
            continue
        print(f"  [{player_id}] Searching Wikipedia for '{wiki_title}'...", end=' ')
        try:
            img_url = get_wiki_image_url(wiki_title)
            if not img_url:
                print("NO IMAGE FOUND")
                continue
            size = download_image(img_url, save_path)
            print(f"OK ({size//1024}KB)")
            success += 1
        except Exception as e:
            print(f"ERROR: {e}")
    
    print(f"\n=== Done! {success}/{len(PLAYERS)} images downloaded ===")
    print(f"Saved to: {SAVE_DIR}")

if __name__ == '__main__':
    main()
