"""Create an offline Windows runtime using only the project's private interpreter.

Run with .venv/Scripts/python.exe after installing the hash-locked runtime set.
The target is an explicitly supplied frontend checkout, never a system folder.
"""
import argparse
import importlib.metadata as metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def copy_tree(source, target):
    shutil.copytree(source, target, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git", ".DS_Store"))


def stage(frontend):
    frontend = frontend.resolve()
    if not (frontend / "electron-builder.yml").is_file():
        raise ValueError("Expected a frontend source checkout")
    staging = frontend / ".runtime"
    if staging.exists():
        # Only discard this tool's reproducible staging output inside the selected checkout.
        if staging.resolve().parent != frontend or staging.name != ".runtime":
            raise ValueError("Unsafe staging path")
        shutil.rmtree(staging)
    staging.mkdir(exist_ok=True)
    python = staging / "python"
    # uv's standalone distribution is relocatable; a venv alone is not.
    base = Path(sys.base_prefix)
    if base == Path(sys.prefix) or not (base / "python.exe").is_file():
        raise RuntimeError("Run from a Windows venv based on the private standalone Python")
    copy_tree(base, python)
    copy_tree(Path(sys.prefix) / "Lib/site-packages", python / "Lib/site-packages")
    backend = staging / "backend"
    backend.mkdir(exist_ok=True)
    for name in ("src", "config_templates", "live2d-models", "avatars", "backgrounds",
                 "characters", "prompts", "web_tool", "packaging", "docs/TR"):
        copy_tree(ROOT / name, backend / name)
    for name in ("model_dict.json", "LICENSE", "LICENSE-Live2D.md",
                 "NOTICE-TR.md", "UPSTREAM.json"):
        shutil.copyfile(ROOT / name, backend / name)
    # Desktop ships MCP disabled; never package a developer's server credentials.
    (backend / "mcp_servers.json").write_text("{}", "utf-8")
    (backend / "scripts").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "scripts/desktop_server.py", backend / "scripts/desktop_server.py")
    notices = staging / "licenses"
    notices.mkdir(exist_ok=True)
    for name in ("LICENSE", "LICENSE-Live2D.md", "NOTICE-TR.md"):
        shutil.copyfile(ROOT / name, notices / name)
    shutil.copyfile(frontend / "LICENSE", notices / "FRONTEND-LICENSE.txt")
    copy_tree(frontend / "src/renderer/WebSDK/Core", notices / "Live2D-Core")
    # The Core's redistributable list permits core JS and declarations, not its map.
    for item in (notices / "Live2D-Core").rglob("*"):
        if item.is_file() and item.suffix.lower() not in (".md", ".txt"):
            item.unlink()
    for folder in ("WebSDK/Framework", "MotionSync/Framework"):
        for item in (frontend / "src/renderer" / folder).glob("*LICENSE*"):
            shutil.copyfile(item, notices / (folder.replace("/", "-") + "-" + item.name))
    copy_tree(ROOT / "packaging/licenses", notices / "additional")
    inventory = []
    for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
        name = dist.metadata["Name"]
        files = []
        for entry in dist.files or []:
            if any(word in str(entry).lower() for word in ("license", "copying", "notice")):
                source = Path(dist.locate_file(entry)).resolve()
                if not source.is_file() or source.suffix.lower() in (".py", ".pyc", ".exe", ".dll"):
                    continue
                target = notices / "python" / name / str(entry).replace("..", "_")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                files.append(str(target.relative_to(notices)).replace("\\", "/"))
        supplement = notices / "additional" / (name.lower() + "-LICENSE.txt")
        if not files and supplement.is_file():
            files.append(str(supplement.relative_to(notices)).replace("\\", "/"))
        inventory.append({"name": name, "version": dist.version,
                          "license": dist.metadata.get("License-Expression") or dist.metadata.get("License"),
                          "files": files})
    (notices / "python-packages.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), "utf-8")
    # Include Python's complete bundled dependency notices and build metadata.
    shutil.copyfile(base / "LICENSE.txt", notices / "PYTHON-LICENSE.txt")
    subprocess.run([str(python / "python.exe"), "-I", "-c",
                    "import av, faster_whisper, fastapi, edge_tts; print('private-runtime-imports: PASS')"], check=True)
    print(json.dumps({"packages": len(inventory), "missing_license_files": [d["name"] for d in inventory if not d["files"]]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend", type=Path, required=True)
    stage(parser.parse_args().frontend)
