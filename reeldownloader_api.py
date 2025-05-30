import os
import instaloader
from pathlib import Path
import shutil

# === CONFIGURATION ===
USERNAME = 'jhonybhai_5'
PASSWORD = 'jhonybhai@#@#19996'

# Input reel URLs
reel_urls = [
    "https://www.instagram.com/foodandstreett/reel/CMZGS77lavt/",
    "https://www.instagram.com/foodandstreett/reel/Cj-L5HTjU8G/",
    "https://www.instagram.com/foodandstreett/reel/CkxVQ6XDkC4/",
    "https://www.instagram.com/foodandstreett/reel/ClG85-GjoUe/"
]

# === SETUP ===
L = instaloader.Instaloader(download_comments=False, save_metadata=False, post_metadata_txt_pattern="")
session_file = f"{USERNAME}.session"

# Try to load session or login and save session
try:
    L.load_session_from_file(USERNAME)
    print(f"✅ Session loaded for {USERNAME}")
except FileNotFoundError:
    print(f"🔐 No session found. Logging in as {USERNAME}...")
    L.login(USERNAME, PASSWORD)
    L.save_session_to_file()
    print("💾 Session saved!")

# Create download folder
download_dir = Path("downloads")
download_dir.mkdir(exist_ok=True)
caption_log = download_dir / "captions.txt"

# === DOWNLOAD LOOP ===
for idx, url in enumerate(reel_urls, start=1):
    shortcode = url.strip("/").split("/")[-1]
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    temp_folder = Path(f"temp_{shortcode}")
    temp_folder.mkdir(exist_ok=True)

    print(f"\n⬇️ Downloading Reel: {shortcode}")
    try:
        L.download_post(post, target=temp_folder)
    except Exception as e:
        print(f"❌ Error downloading {shortcode}: {e}")
        shutil.rmtree(temp_folder)
        continue

    # Move video
    video_file = next(temp_folder.glob("*.mp4"), None)
    if video_file:
        dest_video = download_dir / f"Video_{idx}.mp4"
        shutil.move(str(video_file), dest_video)
        print(f"🎬 Saved video as {dest_video}")
    else:
        print(f"⚠️ No video found for {shortcode}")

    # Append caption to single file
    with open(caption_log, "a", encoding="utf-8") as f:
        clean_caption = (post.caption or "").replace("\n", " ").replace(",", " ")  # Clean commas and newlines
        f.write(f"{idx},{clean_caption.strip()}\n")
        print(f"📝 Appended caption for Video_{idx} to captions.txt")

    shutil.rmtree(temp_folder)

print("\n✅ All reels downloaded. Captions saved in downloads/captions.txt.")
