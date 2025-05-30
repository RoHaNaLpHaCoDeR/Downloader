import os
import instaloader
from pathlib import Path
import shutil
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === CONFIGURATION ===
USERNAME = 'jhonybhai_5'
PASSWORD = 'jhonybhai@#@#19996'

# Read counter from file
with open("counter.txt", "r", encoding="utf-8") as cfile:
    counter = int(cfile.read().strip())

# Read reel URLs from file
with open("links.txt", "r", encoding="utf-8") as lfile:
    reel_urls = [line.strip() for line in lfile.readlines()]

# === SETUP ===
L = instaloader.Instaloader(download_comments=False, save_metadata=False, post_metadata_txt_pattern="")
session_path = Path(__file__).parent / f"session-{USERNAME}"

try:
    L.load_session_from_file(USERNAME, str(session_path))
    print(f"Session loaded for {USERNAME}")
except FileNotFoundError:
    print(f"No session found. Logging in as {USERNAME}...")
    L.login(USERNAME, PASSWORD)
    L.save_session_to_file(str(session_path))
    print("Session saved!")


# Create download folder
download_dir = Path("VIDEOS")
download_dir.mkdir(exist_ok=True)
caption_log = download_dir / "captions.txt"

# === DOWNLOAD LOOP ===
updated_links = []
for i in range(counter - 1, len(reel_urls)):
    idx = counter
    url = reel_urls[i]
    shortcode = url.strip("/").split("/")[-1]
    print(f"\nDownloading Reel {idx}: {url}")
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        temp_folder = Path(f"temp_{shortcode}")
        temp_folder.mkdir(exist_ok=True)

        L.download_post(post, target=temp_folder)
        video_file = next(temp_folder.glob("*.mp4"), None)

        if video_file:
            size_mb = os.path.getsize(video_file) / (1024 * 1024)
            if size_mb > 100:
                print(f"Skipping Video_{idx}: File size {size_mb:.2f} MB > 100 MB")
                updated_links.append(f"{url} - large file")
                shutil.rmtree(temp_folder)
                continue

            dest_video = download_dir / f"Video_{idx}.mp4"
            shutil.move(str(video_file), dest_video)
            print(f"🎬 Saved video as {dest_video}")

            with open(caption_log, "a", encoding="utf-8") as f:
                clean_caption = (post.caption or "").replace("\n", " ").replace(",", " ")
                f.write(f"{idx},{clean_caption.strip()}\n")
                print(f"Appended caption for Video_{idx} to captions.txt")

            counter += 1
            updated_links.append(url)
        else:
            print(f"No video found for {shortcode}")
            updated_links.append(url + " - no video found")

        shutil.rmtree(temp_folder)

    except Exception as e:
        if "login_required" in str(e):
            print(f"Login required error for {url}, skipping this reel.")
            updated_links.append(f"{url} - login_required error")
            continue
        else:
            print(f"Error with {url}: {e}")
            updated_links.append(url + " - error")
            continue

# Save updated counter
with open("counter.txt", "w", encoding="utf-8") as cfile:
    cfile.write(str(counter))

# Overwrite links.txt with updated status
with open("links.txt", "w", encoding="utf-8") as lfile:
    for link in updated_links:
        lfile.write(link + "\n")

print("\nAll reels processed up to counter:", counter - 1)
