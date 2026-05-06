"""Download BERT, HuBERT, and STT models with retry and resume support."""
import os
import sys
import subprocess
import time
import json
from pathlib import Path

ROOT = Path(__file__).parent
PRETRAINED = ROOT / "GPT-SoVITS" / "GPT_SoVITS" / "pretrained_models"
STT_DIR = ROOT / "models" / "stt" / "sensevoice"

# Set HF mirror
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def download_bert():
    """Download chinese-roberta-wwm-ext-large from hf-mirror."""
    from huggingface_hub import snapshot_download

    target = PRETRAINED / "chinese-roberta-wwm-ext-large"
    target.mkdir(parents=True, exist_ok=True)

    log("Downloading BERT model (chinese-roberta-wwm-ext-large)...")
    try:
        snapshot_download(
            repo_id="hfl/chinese-roberta-wwm-ext-large",
            local_dir=str(target),
            local_dir_use_symlinks=False,
            resume_download=True,
            ignore_patterns=[".cache*", ".gitattributes"],
        )
        log("BERT model download complete!")
        return True
    except Exception as e:
        log(f"BERT download failed: {e}")
        return False


def download_hubert():
    """Download chinese-hubert-base from hf-mirror."""
    from huggingface_hub import snapshot_download

    target = PRETRAINED / "chinese-hubert-base"
    target.mkdir(parents=True, exist_ok=True)

    log("Downloading HuBERT model (chinese-hubert-base)...")
    try:
        snapshot_download(
            repo_id="TencentGameMate/chinese-hubert-base",
            local_dir=str(target),
            local_dir_use_symlinks=False,
            resume_download=True,
            ignore_patterns=[".cache*", ".gitattributes"],
        )
        log("HuBERT model download complete!")
        return True
    except Exception as e:
        log(f"HuBERT download failed: {e}")
        return False


def download_stt():
    """Download STT model from GitHub with curl resume."""
    stt_dir = STT_DIR
    stt_dir.mkdir(parents=True, exist_ok=True)

    url = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2"
    output = stt_dir / "model.tar.bz2"
    log_file = stt_dir / "download.log"

    log(f"Downloading STT model from GitHub (resuming if partial)...")

    with open(log_file, "w") as lf:
        result = subprocess.run(
            ["curl", "-L", "-C", "-", "--retry", "5",
             "--speed-time", "60", "--speed-limit", "1000",
             "-o", str(output), url],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=72000  # 20 hours max
        )
        lf.write(result.stdout.decode("utf-8", errors="replace"))

    if output.exists() and output.stat().st_size > 150_000_000:
        log(f"STT model downloaded! Size: {output.stat().st_size} bytes")
        # Extract
        log("Extracting STT model...")
        import tarfile
        try:
            import bz2
            with tarfile.open(str(output), "r:bz2") as tar:
                tar.extractall(path=str(stt_dir))
            log("STT model extracted!")
            # Move files from subdirectory if needed
            for item in stt_dir.iterdir():
                if item.is_dir() and item != stt_dir:
                    for sub in item.iterdir():
                        sub.rename(stt_dir / sub.name)
            return True
        except Exception as e:
            log(f"STT extraction failed: {e}")
            return False
    else:
        size = output.stat().st_size if output.exists() else 0
        log(f"STT download incomplete: {size} bytes (need 155MB)")
        return False


if __name__ == "__main__":
    tasks = []

    # BERT
    if not any((PRETRAINED / "chinese-roberta-wwm-ext-large" / f).exists()
               for f in ["pytorch_model.bin", "model.safetensors"]):
        tasks.append(("BERT", download_bert))
    else:
        log("BERT model already exists, skipping")

    # HuBERT
    if not any((PRETRAINED / "chinese-hubert-base" / f).exists()
               for f in ["pytorch_model.bin", "model.safetensors"]):
        tasks.append(("HuBERT", download_hubert))
    else:
        log("HuBERT model already exists, skipping")

    # STT
    if not any(STT_DIR.glob("*.onnx")):
        tasks.append(("STT", download_stt))
    else:
        log("STT model already exists, skipping")

    for name, func in tasks:
        log(f"Starting {name} download...")
        success = func()
        log(f"{name}: {'SUCCESS' if success else 'FAILED'}")

    log("All downloads attempted. Check STT extraction.")

    # Check final state
    print("\n=== Final State ===")
    for f in (PRETRAINED / "chinese-roberta-wwm-ext-large").iterdir():
        print(f"  BERT: {f.name} ({f.stat().st_size} bytes)")
    for f in (PRETRAINED / "chinese-hubert-base").iterdir():
        print(f"  HuBERT: {f.name} ({f.stat().st_size} bytes)")
    for f in STT_DIR.iterdir():
        print(f"  STT: {f.name} ({f.stat().st_size} bytes)" if f.is_file() else f"  STT: {f.name}/")
