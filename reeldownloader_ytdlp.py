import yt_dlp
import os

DOWNLOAD_DIR = "downloads"
LINKS_FILE = "links.txt"
COUNTER_FILE = "counter.txt"
CAPTION_FILE = os.path.join(DOWNLOAD_DIR, "captions.txt")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Load all reel URLs
with open(LINKS_FILE, "r", encoding="utf-8") as f:
    reel_urls = [line.strip() for line in f.readlines()]

# Load counter
if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "r") as f:
        counter = int(f.read().strip())
else:
    counter = 0

updated = False

for i in range(counter, len(reel_urls)):
    url = reel_urls[i]
    print(f"⬇️ Downloading Reel {i + 1}: {url}")

    output_template = os.path.join(DOWNLOAD_DIR, f"Video_{i + 1}.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "quiet": True,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "writeinfojson": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            video_file = os.path.join(DOWNLOAD_DIR, f"Video_{i + 1}.mp4")
            if not os.path.exists(video_file):
                raise Exception("Download failed: file not found.")

            file_size = os.path.getsize(video_file) / (1024 * 1024)  # MB
            if file_size > 100:
                os.remove(video_file)
                reel_urls[i] = f"{url} - large file"
                print(f"⚠️ Skipped Reel {i + 1}: File > 100MB")
            else:
                caption = info.get("description", "").replace("\n", " ").strip()
                with open(CAPTION_FILE, "a", encoding="utf-8") as fcap:
                    fcap.write(f"{i + 1},{caption}\n")
                print(f"✅ Saved Video_{i + 1}.mp4 and caption.")

    except Exception as e:
        print(f"❌ Error with Reel {i + 1}: {e}")

    # Always increment counter
    counter = i + 1
    updated = True

# Save updated links.txt
with open(LINKS_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(reel_urls))

# Save new counter
with open(COUNTER_FILE, "w", encoding="utf-8") as f:
    f.write(str(counter))

if updated:
    print(f"✅ All reels processed up to counter: {counter}")
else:
    print("🚫 Nothing new to process.")
