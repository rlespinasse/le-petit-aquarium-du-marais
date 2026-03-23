#!/usr/bin/env python3
"""Sync the images/ directory with the fish divs in index.html.

Scans images/ for image files, groups png/webp pairs into <picture>
elements, and replaces everything between the FISH:START and FISH:END
markers in index.html.
"""

import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
FISH_DIR = SITE_DIR / "images"
INDEX = SITE_DIR / "index.html"

SW_FILE = SITE_DIR / "sw.js"

EXTENSIONS = {".svg", ".png", ".webp"}

START_MARKER = "<!-- FISH:START"
END_MARKER = "<!-- FISH:END -->"

FISHLIST_START = "<!-- FISHLIST:START"
FISHLIST_END = "<!-- FISHLIST:END -->"

SW_ASSETS_START = "// ASSETS_START"
SW_ASSETS_END = "// ASSETS_END"


def _capitalize_name(raw: str) -> str:
    """Capitalize a hyphenated name: jean-luc -> Jean-Luc."""
    return "-".join(part.capitalize() for part in raw.split("-"))


def names_from_stem(stem: str) -> tuple[str, str | None]:
    """Derive child name and optional fish name from a fish stem.

    fish-emma            -> ("Emma", None)
    fish-jean-luc        -> ("Jean-Luc", None)
    fish-abel--paillette -> ("Abel", "Paillette")
    fish-louis--nemo     -> ("Louis", "Némo")

    The '--' separator distinguishes child name from fish name
    (single '-' is reserved for compound names like Jean-Luc).
    """
    if stem.lower().startswith("fish-"):
        stem = stem[5:]
    if "--" in stem:
        child_raw, fish_raw = stem.split("--", 1)
        return _capitalize_name(child_raw), _capitalize_name(fish_raw)
    return _capitalize_name(stem), None


def collect_fish() -> list[dict]:
    """Group image files by stem, pairing png/webp together."""
    files_by_stem: dict[str, dict[str, pathlib.Path]] = {}

    for f in FISH_DIR.iterdir():
        if f.suffix.lower() not in EXTENSIONS or f.name.startswith("."):
            continue
        files_by_stem.setdefault(f.stem, {})[f.suffix.lower()] = f

    fish_list = []
    for stem in sorted(files_by_stem):
        entry = files_by_stem[stem]
        child_name, fish_name = names_from_stem(stem)
        fish_list.append({"child_name": child_name, "fish_name": fish_name, "files": entry})

    return fish_list


def _fish_alt(child_name: str, fish_name: str | None) -> str:
    """Build the alt text for a fish image."""
    if fish_name:
        return f"{fish_name}, poisson de {child_name}"
    return f"Poisson de {child_name}"


def _fish_data_attrs(fish_name: str | None) -> str:
    """Build extra data attributes for the fish div."""
    if fish_name:
        return f' data-fish-name="{fish_name}"'
    return ""


def build_divs(fish_list: list[dict]) -> str:
    lines = []
    for i, fish in enumerate(fish_list, start=1):
        child_name = fish["child_name"]
        fish_name = fish["fish_name"]
        files = fish["files"]
        webp = files.get(".webp")
        png = files.get(".png")
        svg = files.get(".svg")
        alt = _fish_alt(child_name, fish_name)
        data = _fish_data_attrs(fish_name)

        if webp and png:
            lines.append(
                f'    <div class="fish fish-{i}"{data}>\n'
                f"      <picture>\n"
                f'        <source srcset="images/{webp.name}" type="image/webp">\n'
                f'        <img src="images/{png.name}" alt="{alt}">\n'
                f"      </picture>\n"
                f"    </div>"
            )
        elif png:
            lines.append(
                f'    <div class="fish fish-{i}"{data}>\n'
                f'      <img src="images/{png.name}" alt="{alt}">\n'
                f"    </div>"
            )
        elif svg:
            lines.append(
                f'    <div class="fish fish-{i}"{data}>\n'
                f'      <img src="images/{svg.name}" alt="{alt}">\n'
                f"    </div>"
            )
        elif webp:
            lines.append(
                f'    <div class="fish fish-{i}"{data}>\n'
                f'      <img src="images/{webp.name}" alt="{alt}">\n'
                f"    </div>"
            )

    return "\n".join(lines)


def build_fish_list(fish_list: list[dict]) -> str:
    """Build an accessible <ul> listing all fish for screen readers."""
    items = []
    for fish in fish_list:
        alt = _fish_alt(fish["child_name"], fish["fish_name"])
        items.append(f"        <li>{alt}</li>")
    return '      <ul id="fishList">\n' + "\n".join(items) + "\n      </ul>"


def update_sw(fish_list: list[dict]) -> bool:
    """Update the service worker asset list and cache version."""
    if not SW_FILE.exists():
        return False

    # Collect all fish image paths
    fish_assets = []
    for fish in fish_list:
        for ext in (".webp", ".png", ".svg"):
            f = fish["files"].get(ext)
            if f:
                fish_assets.append(f"images/{f.name}")

    # Build the asset list block
    base_assets = [
        '  "./"',
        '  "style.css"',
        '  "aquarium.js"',
        '  "manifest.json"',
        '  "favicon.svg"',
    ]
    all_assets = base_assets + [f'  "{a}"' for a in sorted(fish_assets)]
    assets_block = (
        SW_ASSETS_START
        + " \u2014 auto-generated by sync, do not edit manually\n"
        + "const ASSETS = [\n"
        + ",\n".join(all_assets)
        + ",\n];\n"
        + SW_ASSETS_END
    )

    sw_content = SW_FILE.read_text(encoding="utf-8")

    # Replace the assets block
    pattern = re.compile(
        re.escape(SW_ASSETS_START) + r".*?" + re.escape(SW_ASSETS_END),
        re.DOTALL,
    )
    new_sw = pattern.sub(assets_block, sw_content)

    # Compute a short hash of all asset paths for the cache version
    content_hash = hashlib.md5(
        "\n".join(sorted(fish_assets)).encode()
    ).hexdigest()[:8]
    new_sw = re.sub(
        r'const CACHE_VERSION = "aquarium-[^"]*"',
        f'const CACHE_VERSION = "aquarium-{content_hash}"',
        new_sw,
    )

    if new_sw == sw_content:
        return False

    SW_FILE.write_text(new_sw, encoding="utf-8")
    return True


def sync() -> bool:
    """Return True if index.html was changed."""
    if not FISH_DIR.is_dir():
        print(f"error: {FISH_DIR} not found", file=sys.stderr)
        sys.exit(1)

    fish_list = collect_fish()

    if not fish_list:
        print("warning: no fish images found in images/", file=sys.stderr)

    new_block = build_divs(fish_list)
    new_list = build_fish_list(fish_list)

    html = INDEX.read_text(encoding="utf-8")

    # Replace fish divs
    pattern = re.compile(
        r"([ \t]*" + re.escape(START_MARKER) + r"[^\n]*\n)"
        r".*?"
        r"(\n[ \t]*" + re.escape(END_MARKER) + r")",
        re.DOTALL,
    )

    match = pattern.search(html)
    if not match:
        print(f"error: FISH markers not found in {INDEX}", file=sys.stderr)
        sys.exit(1)

    replacement = match.group(1) + new_block + match.group(2)
    new_html = html[: match.start()] + replacement + html[match.end() :]

    # Replace accessible fish list
    list_pattern = re.compile(
        r"([ \t]*" + re.escape(FISHLIST_START) + r"[^\n]*\n)"
        r".*?"
        r"(\n[ \t]*" + re.escape(FISHLIST_END) + r")",
        re.DOTALL,
    )

    list_match = list_pattern.search(new_html)
    if list_match:
        list_replacement = list_match.group(1) + new_list + list_match.group(2)
        new_html = new_html[: list_match.start()] + list_replacement + new_html[list_match.end() :]

    html_changed = new_html != html
    if html_changed:
        INDEX.write_text(new_html, encoding="utf-8")
        count = len(fish_list)
        print(f"index.html updated — {count} fish{'es' if count != 1 else ''} synced.")

    sw_changed = update_sw(fish_list)
    if sw_changed:
        print("sw.js updated — offline cache refreshed.")

    if not html_changed and not sw_changed:
        print("Everything is already in sync.")

    return html_changed or sw_changed


if __name__ == "__main__":
    sync()
