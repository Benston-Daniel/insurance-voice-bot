import os
from huggingface_hub import hf_hub_download

# --- Configuration ---
REPO_ID = "abhinand/gemma-2b-it-tamil-v0.1-alpha-GGUF"
FILENAME = "gemma-2b-it-tamil-v0.1-alpha.Q4_K_M.gguf"
TARGET_DIR = "models"
# ---

def download_model():
    """
    Downloads the GGUF model from Hugging Face to the
    specified local directory.
    """
    print(f"Ensuring target directory exists: {TARGET_DIR}")
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    target_path = os.path.join(TARGET_DIR, FILENAME)

    if os.path.exists(target_path):
        print(f"Model already exists at {target_path}. Skipping download.")
        return

    print(f"Downloading model {FILENAME} from {REPO_ID}...")
    try:
        hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=TARGET_DIR,
            local_dir_use_symlinks=False  # Better for Docker
        )
        print(f"Model downloaded successfully to {target_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        raise

if __name__ == "__main__":
    download_model()