"""Fail on credential formats and personal Windows paths in added source lines."""
import re
import subprocess
from pathlib import Path

PATTERNS = [
    re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{24,})"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+(?!Public\b|Default\b|<)[^\\/\s]+", re.I),
]


def check(root):
    root = Path(root)
    diff = subprocess.check_output(["git", "diff", "--no-ext-diff", "--unified=0", "HEAD"],
                                   cwd=root).decode("utf-8", "replace")
    text = "\n".join(line[1:] for line in diff.splitlines()
                     if line.startswith("+") and not line.startswith("+++"))
    files = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"],
                                    cwd=root).decode().split("\0")
    for name in filter(None, files):
        path = root / name
        if path.is_file() and path.stat().st_size < 5_000_000:
            text += "\n" + path.read_bytes().decode("utf-8", "replace")
    matches = sum(len(pattern.findall(text)) for pattern in PATTERNS)
    if matches:
        raise SystemExit(f"Secret/path scan: {matches} findings; inspect locally before publishing")
    print("Secret/path scan: PASS")


if __name__ == "__main__":
    import sys
    check(sys.argv[1] if len(sys.argv) > 1 else ".")
