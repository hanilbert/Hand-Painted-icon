#!/usr/bin/env python3
"""Generate and validate icon-set subscription files from repository PNGs."""

from __future__ import annotations

import argparse
import json
import struct
import sys
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "iconset.config.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class ValidationError(Exception):
    """Raised when repository inputs cannot produce a valid icon set."""


def load_config() -> dict:
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read {CONFIG_PATH.name}: {exc}") from exc

    required = ("repository", "iconset", "categories", "canvas", "outputs")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValidationError(f"missing config keys: {', '.join(missing)}")
    if not config["categories"] or len(config["categories"]) != len(set(config["categories"])):
        raise ValidationError("categories must be a non-empty list without duplicates")
    return config


def png_metadata(path: Path) -> tuple[int, int, bool]:
    try:
        with path.open("rb") as stream:
            if stream.read(8) != PNG_SIGNATURE:
                raise ValidationError(f"{path.relative_to(ROOT)}: invalid PNG signature")

            length_bytes = stream.read(4)
            chunk_type = stream.read(4)
            if len(length_bytes) != 4 or chunk_type != b"IHDR":
                raise ValidationError(f"{path.relative_to(ROOT)}: missing PNG IHDR")
            length = struct.unpack(">I", length_bytes)[0]
            ihdr = stream.read(length)
            if length != 13 or len(ihdr) != 13:
                raise ValidationError(f"{path.relative_to(ROOT)}: invalid PNG IHDR")
            width, height, _depth, color_type = struct.unpack(">IIBB", ihdr[:10])
            stream.read(4)

            has_alpha = color_type in (4, 6)
            while not has_alpha:
                length_bytes = stream.read(4)
                if len(length_bytes) != 4:
                    break
                chunk_length = struct.unpack(">I", length_bytes)[0]
                chunk_type = stream.read(4)
                if len(chunk_type) != 4:
                    break
                if chunk_type == b"tRNS":
                    has_alpha = True
                stream.seek(chunk_length + 4, 1)
                if chunk_type == b"IEND":
                    break
    except OSError as exc:
        raise ValidationError(f"cannot read {path.relative_to(ROOT)}: {exc}") from exc

    return width, height, has_alpha


def encoded_url(owner: str, repo: str, branch: str, relative_path: Path) -> str:
    path = "/".join(quote(part, safe="") for part in relative_path.parts)
    return f"https://raw.githubusercontent.com/{quote(owner, safe='')}/{quote(repo, safe='')}/{quote(branch, safe='')}/{path}"


def collect_icons(config: dict) -> tuple[list[dict[str, str]], Counter[str]]:
    repository = config["repository"]
    expected_size = (config["canvas"]["width"], config["canvas"]["height"])
    icons: list[dict[str, str]] = []
    counts: Counter[str] = Counter()

    for category in config["categories"]:
        directory = ROOT / category
        if not directory.is_dir():
            raise ValidationError(f"configured category is missing: {category}")

        paths = sorted(directory.rglob("*.png"), key=lambda path: path.as_posix().casefold())
        for path in paths:
            relative = path.relative_to(ROOT)
            if any(part.startswith(".") for part in relative.parts) or ".orig" in path.name:
                raise ValidationError(f"forbidden PNG file: {relative}")

            width, height, has_alpha = png_metadata(path)
            if (width, height) != expected_size:
                raise ValidationError(
                    f"{relative}: expected {expected_size[0]}x{expected_size[1]}, got {width}x{height}"
                )
            if not has_alpha:
                raise ValidationError(f"{relative}: PNG must contain an alpha channel")

            nested_name = " / ".join(part.replace("_", " ") for part in relative.with_suffix("").parts[1:])
            display_name = f"{category.replace('_', ' ')} - {nested_name}"
            icons.append(
                {
                    "name": display_name,
                    "url": encoded_url(
                        repository["owner"], repository["name"], repository["branch"], relative
                    ),
                }
            )
            counts[category] += 1

    names = [icon["name"] for icon in icons]
    urls = [icon["url"] for icon in icons]
    duplicate_names = sorted(name for name, count in Counter(names).items() if count > 1)
    duplicate_urls = sorted(url for url, count in Counter(urls).items() if count > 1)
    if duplicate_names:
        raise ValidationError(f"duplicate display names: {', '.join(duplicate_names)}")
    if duplicate_urls:
        raise ValidationError(f"duplicate URLs: {', '.join(duplicate_urls)}")

    return icons, counts


def rendered_outputs(config: dict, icons: list[dict[str, str]]) -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    for output in config["outputs"]:
        description_key = output["description"]
        data = {
            "name": config["iconset"]["name"],
            "description": config["iconset"][description_key],
            "icons": icons,
        }
        output_path = ROOT / output["path"]
        outputs[output_path] = json.dumps(data, ensure_ascii=False, indent=4) + "\n"
    return outputs


def check_outputs(outputs: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for path, expected in outputs.items():
        try:
            actual = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{path.name} is missing")
            continue
        except OSError as exc:
            errors.append(f"cannot read {path.name}: {exc}")
            continue
        if actual != expected:
            errors.append(f"{path.name} is out of date")
    return errors


def write_outputs(outputs: dict[Path, str]) -> None:
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        temporary_path.replace(path)


def print_counts(config: dict, counts: Counter[str]) -> None:
    for category in config["categories"]:
        print(f"{category}: {counts[category]}")
    print(f"Total: {sum(counts.values())}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated files without writing them")
    args = parser.parse_args()

    try:
        config = load_config()
        icons, counts = collect_icons(config)
        outputs = rendered_outputs(config, icons)
        if args.check:
            errors = check_outputs(outputs)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print("Generated files are up to date.")
        else:
            write_outputs(outputs)
            print("Generated files updated.")
        print_counts(config, counts)
        return 0
    except (KeyError, TypeError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
