"""Fetch hash-verified corresponding codec sources for release redistribution."""
import concurrent.futures
import hashlib
import json
import tarfile
import urllib.request
import ssl
import certifi
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".build/third-party-sources"


def download(item):
    name = item["name"]
    url = item["source_url"]
    suffix = "." + item["format"] if "format" in item else ".tar.bz2" if url.endswith("bz2") else ".tar.xz" if url.endswith("xz") else ".tar.gz"
    target = OUTPUT / (name + suffix)
    if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != item["sha256"]:
        request = urllib.request.Request(url, headers={"User-Agent": "Open-LLM-VTuber-TR-license-audit"})
        with urllib.request.urlopen(request, timeout=180, context=ssl.create_default_context(cafile=certifi.where())) as response, target.open("wb") as output:
            while block := response.read(1024 * 1024):
                output.write(block)
    if hashlib.sha256(target.read_bytes()).hexdigest() != item["sha256"]:
        raise ValueError("Source checksum mismatch: " + name)
    notices = ROOT / "packaging/licenses/media" / name
    notices.mkdir(parents=True, exist_ok=True)
    if target.suffix == ".zip":
        print("verified-source: " + name, flush=True)
        return
    with tarfile.open(target) as archive:
        for member in archive.getmembers():
            leaf = Path(member.name).name
            if member.isfile() and len(Path(member.name).parts) <= 3 and leaf.lower().startswith(("license", "copying", "copyright", "notice")):
                data = archive.extractfile(member).read()
                (notices / leaf).write_bytes(data)
    print("verified-source: " + name, flush=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "packaging/media-sources.json").read_text("utf-8"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(download, manifest))
    bundle = ROOT / ".build/THIRD-PARTY-SOURCES.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED) as archive:
        for file in OUTPUT.rglob("*"):
            if file.is_file():
                archive.write(file, file.relative_to(OUTPUT))
        archive.write(ROOT / "packaging/media-sources.json", "media-sources.json")
    print("source-bundle-ready", len(results), flush=True)


if __name__ == "__main__":
    main()
