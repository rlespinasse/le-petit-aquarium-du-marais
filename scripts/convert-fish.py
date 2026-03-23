#!/usr/bin/env python3
"""Convert fish drawings from dessins/ to web-ready images in images/.

For each image file found in dessins/, generates:
  - images/fish-{stem}.png
  - images/fish-{stem}.webp

File naming convention:
  - prenom.ext              → fish drawn by child "Prenom"
  - prenom--poisson.ext     → fish named "Poisson" drawn by child "Prenom"

Requires ImageMagick (magick) to be installed.
"""

import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "dessins"
DST_DIR = ROOT / "site" / "images"

EXTENSIONS = {".jpg", ".jpeg", ".png", ".svg", ".webp", ".bmp", ".tiff", ".tif", ".heic"}
CACHE_DIR = ROOT / ".cache"
HASH_FILE = CACHE_DIR / "checksums.json"


def file_hash(path: pathlib.Path) -> str:
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_checksums() -> dict[str, str]:
    if HASH_FILE.exists():
        return json.loads(HASH_FILE.read_text(encoding="utf-8"))
    return {}


def save_checksums(checksums: dict[str, str]):
    CACHE_DIR.mkdir(exist_ok=True)
    HASH_FILE.write_text(json.dumps(checksums, indent=2) + "\n", encoding="utf-8")


def get_magick_cmd() -> list[str]:
    """Return the ImageMagick convert command, supporting v6 and v7."""
    if shutil.which("magick"):
        return ["magick"]
    if shutil.which("convert"):
        return ["convert"]
    print("ERROR: ImageMagick is required. Install it with: brew install imagemagick (macOS) or apt install imagemagick (Linux)", file=sys.stderr)
    sys.exit(1)


def main():
    magick = get_magick_cmd()

    if not SRC_DIR.is_dir():
        print(f"ERROR: {SRC_DIR} not found", file=sys.stderr)
        sys.exit(1)

    DST_DIR.mkdir(exist_ok=True)

    source_files = sorted(
        f for f in SRC_DIR.iterdir()
        if f.suffix.lower() in EXTENSIONS and not f.name.startswith(".")
    )

    if not source_files:
        print("No images found in dessins/")
        return

    checksums = load_checksums()
    converted = 0
    skipped = 0

    for src in source_files:
        name = src.stem.lower()
        png_out = DST_DIR / f"fish-{name}.png"
        webp_out = DST_DIR / f"fish-{name}.webp"

        # Skip if outputs exist and source content hasn't changed
        src_hash = file_hash(src)
        if png_out.exists() and webp_out.exists() and checksums.get(src.name) == src_hash:
            print(f"  skip {src.name} (already up to date)")
            skipped += 1
            continue

        print(f"  convert {src.name} → fish-{name}.png + fish-{name}.webp")

        # Convert to PNG
        result = subprocess.run(
            [*magick, str(src), "-strip", "-resize", "800x800>", str(png_out)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"    ERROR (png): {result.stderr.strip()}", file=sys.stderr)
            continue

        # Convert to WebP
        result = subprocess.run(
            [*magick, str(src), "-strip", "-resize", "800x800>", "-quality", "80", str(webp_out)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"    ERROR (webp): {result.stderr.strip()}", file=sys.stderr)
            continue

        checksums[src.name] = src_hash
        converted += 1

    # Clean up orphaned files in images/
    expected_names = {src.stem.lower() for src in source_files}
    removed = 0
    for f in DST_DIR.iterdir():
        if f.name.startswith(".") or f.suffix.lower() not in {".png", ".webp"}:
            continue
        # fish-prenom.png → prenom
        stem = f.stem
        if stem.startswith("fish-"):
            stem = stem[5:]
        if stem not in expected_names:
            f.unlink()
            print(f"  remove {f.name} (orphaned)")
            removed += 1

    # Clean up stale checksums
    current_source_names = {src.name for src in source_files}
    checksums = {k: v for k, v in checksums.items() if k in current_source_names}

    save_checksums(checksums)
    print(f"\nDone — {converted} converted, {skipped} skipped, {removed} removed.")


if __name__ == "__main__":
    main()
