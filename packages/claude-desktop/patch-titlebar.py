#!/usr/bin/env python3
"""
patch-titlebar.py - In-place byte-for-byte patch for Claude Desktop app.asar.

Disables titleBarOverlay on Linux to remove unsightly WCO fallback buttons
(Close/Max/Min glyphs) colliding with Claude's top navigation bar.
Preserves exact byte lengths and offsets, updating ASAR integrity hashes.
"""

import hashlib
import json
import os
import shutil
import struct
import sys
from typing import Any


def compute_integrity(
    data: bytes | bytearray, block_size: int = 4194304
) -> dict[str, Any]:
    blocks: list[str] = []
    for i in range(0, len(data), block_size):
        blocks.append(hashlib.sha256(data[i : i + block_size]).hexdigest())
    return {
        "algorithm": "SHA256",
        "hash": hashlib.sha256(data).hexdigest(),
        "blockSize": block_size,
        "blocks": blocks,
    }


def patch_asar(asar_path: str) -> None:
    if not os.path.isfile(asar_path):
        print(f"Error: File not found: {asar_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading ASAR archive: {asar_path}")
    with open(asar_path, "rb") as f:
        content = bytearray(f.read())

    if len(content) < 16:
        print(f"Error: ASAR file too small ({len(content)} bytes)", file=sys.stderr)
        sys.exit(1)

    _p0, p1, _p2, header_len = struct.unpack("<IIII", content[:16])
    header_bytes = bytes(content[16 : 16 + header_len])
    try:
        header: dict[str, Any] = json.loads(header_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error: Failed to parse ASAR JSON header: {e}", file=sys.stderr)
        sys.exit(1)

    data_offset = 8 + p1

    # Locate the build chunk containing titleBarOverlay
    files: dict[str, Any] = (
        header.get("files", {})
        .get(".vite", {})
        .get("files", {})
        .get("build", {})
        .get("files", {})
    )
    target = b'titleBarStyle:"hidden",titleBarOverlay:!0'
    replacement = b'titleBarStyle:"hidden",titleBarOverlay:!1'
    assert len(target) == len(replacement), (
        f"Length mismatch: {len(target)} != {len(replacement)}"
    )

    target_chunk: str | None = None
    target_info: dict[str, Any] | None = None
    for fname, finfo in files.items():
        if fname.startswith("index.chunk-") and fname.endswith(".js"):
            off = data_offset + int(finfo["offset"])
            sz = int(finfo["size"])
            chunk_bytes = content[off : off + sz]
            if target in chunk_bytes:
                target_chunk = fname
                target_info = finfo
                break

    if not target_chunk or not target_info:
        # Check if already patched
        for fname, finfo in files.items():
            if fname.startswith("index.chunk-") and fname.endswith(".js"):
                off = data_offset + int(finfo["offset"])
                sz = int(finfo["size"])
                if replacement in content[off : off + sz]:
                    print(
                        f"Already patched: titleBarOverlay is already set to false in {fname}"
                    )
                    return
        print(
            "Error: Target pattern not found in any .vite/build/index.chunk-*.js",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Found target in: {target_chunk}")
    chunk_off = data_offset + int(target_info["offset"])
    chunk_sz = int(target_info["size"])
    chunk_bytes = content[chunk_off : chunk_off + chunk_sz]

    new_chunk_bytes = chunk_bytes.replace(target, replacement, 1)
    new_integrity = compute_integrity(new_chunk_bytes)
    old_integrity: dict[str, Any] = target_info["integrity"]

    # Backup original before modifying
    backup_path = f"{asar_path}.bak"
    if not os.path.exists(backup_path):
        print(f"Creating backup: {backup_path}")
        shutil.copy2(asar_path, backup_path)

    # Patch chunk payload in place
    content[chunk_off : chunk_off + chunk_sz] = new_chunk_bytes

    # Update hash and blocks in header
    new_header_bytes = header_bytes.replace(
        str(old_integrity["hash"]).encode("utf-8"),
        str(new_integrity["hash"]).encode("utf-8"),
    )
    for old_b, new_b in zip(
        old_integrity["blocks"], new_integrity["blocks"], strict=True
    ):
        new_header_bytes = new_header_bytes.replace(
            str(old_b).encode("utf-8"),
            str(new_b).encode("utf-8"),
        )

    if len(new_header_bytes) != len(header_bytes):
        print("Error: Header length shifted unexpectedly", file=sys.stderr)
        sys.exit(1)

    content[16 : 16 + header_len] = new_header_bytes

    # Write patched ASAR
    with open(asar_path, "wb") as f:
        f.write(content)

    print(f"Successfully patched {asar_path}")
    print(f"  Target: {target.decode('utf-8')} -> {replacement.decode('utf-8')}")
    print(f"  Old SHA256: {old_integrity['hash']}")
    print(f"  New SHA256: {new_integrity['hash']}")


if __name__ == "__main__":
    path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/usr/lib/claude-desktop/resources/app.asar"
    )
    patch_asar(path)
