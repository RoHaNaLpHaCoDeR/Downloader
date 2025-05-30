import os
import instaloader
from pathlib import Path
import shutil

# Initialize Instaloader and login
L = instaloader.Instaloader(download_comments=False, save_metadata=False, post_metadata_txt_pattern="")
USERNAME = 'jhonybhai_5'
PASSWORD = 'jhonybhai@#@#19996'
L.login(USERNAME, PASSWORD)

# Input reel URLs
reel_urls = [
    "https://www.instagram.com/foodandstreett/reel/CMZGS77lavt/",
    "https://www.instagram.com/foodandstreett/reel/Cj-L5HTjU8G/",
    "https://www.instagram.com/foodandstreett/reel/CkxVQ6XDkC4/",
    "https://www.instagram.com/foodandstreett/reel/ClG85-GjoUe/"
]

# Make download directory
download_dir = Path("downloads")
download_dir.mkdir(exist_ok=True)

# Download loop
for idx, url in enumerate(reel_urls, start=1):
    shortcode = url.strip("/").split("/")[-1]
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    temp_folder = Path(f"temp_{shortcode}")
    temp_folder.mkdir(exist_ok=True)

    # Download into temporary folder
    L.download_post(post, target=temp_folder)

    # Find video file
    video_file = next(temp_folder.glob("*.mp4"), None)
    if video_file:
        dest_video = download_dir / f"Video_{idx}.mp4"
        shutil.move(str(video_file), dest_video)
        print(f"Downloaded video: {dest_video}")
    else:
        print(f"[!] No video found for {shortcode}")

    # Save caption
    caption_file = download_dir / f"Video_{idx}.txt"
    with open(caption_file, "w", encoding="utf-8") as f:
        f.write(post.caption or "")
        print(f"Saved caption: {caption_file}")

    # Cleanup temporary folder
    shutil.rmtree(temp_folder)

print("\n✅ All downloads complete.")
