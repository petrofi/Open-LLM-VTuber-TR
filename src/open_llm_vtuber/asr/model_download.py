"""Download the pinned desktop ASR model over HTTPS with per-file SHA-256 checks."""
import hashlib
from pathlib import Path
from urllib.parse import quote
import requests


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_model(folder, manifest, progress=lambda value: None):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    total = sum(item["size"] for item in manifest["files"])
    done = 0
    for item in manifest["files"]:
        name = item["name"]
        if Path(name).name != name or name.startswith("."):
            raise ValueError("Invalid model manifest filename")
        target = folder / name
        if target.is_file() and target.stat().st_size == item["size"] and file_digest(target) == item["sha256"]:
            done += item["size"]
            progress(done * 100 // total)
            continue
        temporary = target.with_name(name + ".partial")
        url = f"https://huggingface.co/{manifest['repo']}/resolve/{manifest['revision']}/{quote(name)}"
        try:
            # The public model needs no token and does not use the user's HF account.
            with requests.get(url, stream=True, timeout=(15, 60)) as response:
                response.raise_for_status()
                digest = hashlib.sha256()
                received = 0
                with temporary.open("wb") as stream:
                    for block in response.iter_content(1024 * 1024):
                        if not block:
                            continue
                        stream.write(block)
                        digest.update(block)
                        received += len(block)
                        if received > item["size"]:
                            raise ValueError("Model file exceeds declared size")
                        progress((done + received) * 100 // total)
                if received != item["size"] or digest.hexdigest() != item["sha256"]:
                    raise ValueError("Model checksum mismatch")
            temporary.replace(target)
            done += received
        finally:
            temporary.unlink(missing_ok=True)
