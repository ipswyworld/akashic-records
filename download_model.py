import os
import requests
import sys

def download_file(url, dest):
    print(f"Downloading {url} to {dest}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if int(downloaded / (1024 * 1024)) % 50 == 0: # Log every 50MB
                            print(f"Progress: {percent:.2f}% ({downloaded / (1024 * 1024):.0f}/{total_size / (1024 * 1024):.0f} MB)")
        print(f"✅ Download complete: {dest}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        if os.path.exists(dest):
            os.remove(dest)

if __name__ == "__main__":
    MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    DEST_PATH = "mobile_node/tinyllama.gguf"
    
    if not os.path.exists("mobile_node"):
        os.makedirs("mobile_node")
        
    if os.path.exists(DEST_PATH):
        print(f"Model already exists at {DEST_PATH}")
    else:
        # Re-check for any existing files to avoid duplicates
        download_file(MODEL_URL, DEST_PATH)
