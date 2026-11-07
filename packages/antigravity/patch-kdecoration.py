#!/usr/bin/env python3
"""
patch-kdecoration.py - In-place byte-for-byte patch for Antigravity app.asar.

Disables titleBarOverlay on Linux to resolve button collision in KDE Plasma 6
with left-hand window buttons (ButtonsOnLeft=XAI).
Updates the SHA-256 integrity block hash in the ASAR pickle header while
preserving exact byte offsets and lengths.
"""

import hashlib
import json
import os
import struct
import sys


def patch_asar(asar_path: str) -> None:
    if not os.path.isfile(asar_path):
        print(f"Error: File not found: {asar_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading ASAR archive: {asar_path}")
    with open(asar_path, "rb") as f:
        content = bytearray(f.read())

    # ASAR Header Format:
    # 0..4:   Pickle size (4 bytes uint32)
    # 4..8:   Payload size (4 bytes uint32)
    # 8..12:  Pickle inner size (4 bytes uint32)
    # 12..16: Header JSON length (4 bytes uint32)
    # 16..16+header_len: Header JSON string (UTF-8)
    if len(content) < 16:
        print(
            f"Error: Invalid or corrupt ASAR file (file size {len(content)} < 16 bytes): {asar_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    header_len = struct.unpack("<I", content[12:16])[0]
    if len(content) < 16 + header_len:
        print(
            f"Error: Truncated ASAR file (needs {16 + header_len} bytes for header, got {len(content)}): {asar_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    header_bytes = content[16 : 16 + header_len]
    try:
        header = json.loads(header_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error: Failed to parse ASAR JSON header: {e}", file=sys.stderr)
        sys.exit(1)

    data_offset = 16 + header_len

    try:
        utils_info = header["files"]["dist"]["files"]["utils.js"]
        u_offset = data_offset + int(utils_info["offset"])
        u_size = int(utils_info["size"])
        old_hash = utils_info["integrity"]["hash"]
    except KeyError as e:
        print(
            f"Error: Missing expected key in ASAR header for dist/utils.js: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    except (ValueError, TypeError) as e:
        print(
            f"Error: Invalid offset or size format in ASAR header: {e}", file=sys.stderr
        )
        sys.exit(1)

    if len(content) < u_offset + u_size:
        print(
            f"Error: Truncated ASAR payload (file ends before utils.js payload ends): {asar_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    utils_bytes = content[u_offset : u_offset + u_size]

    target = (
        b"        titleBarOverlay: isMacOS()\n"
        b"            ? false\n"
        b"            : {\n"
        b"                color: backgroundColor,\n"
        b"                symbolColor: foregroundColor,\n"
        b"                height: 30,\n"
        b"            },"
    )

    # Pad with spaces inside a JS comment to keep the exact length (199 bytes)
    replacement = b"        titleBarOverlay: false, /*" + b" " * 163 + b"*/"
    assert len(target) == len(replacement), (
        f"Length mismatch: {len(target)} != {len(replacement)}"
    )

    if target not in utils_bytes:
        print(
            "Warning/Error: Target string not found in utils.js. May already be patched or upstream changed.",
            file=sys.stderr,
        )
        sys.exit(1)

    idx = utils_bytes.find(target)
    new_utils_bytes = utils_bytes[:idx] + replacement + utils_bytes[idx + len(target) :]

    # Compute new SHA-256 block hash
    new_hash = hashlib.sha256(new_utils_bytes).hexdigest()

    # Update utils.js content in place
    content[u_offset : u_offset + u_size] = new_utils_bytes

    # Update SHA-256 hash inside the JSON header
    new_header_bytes = header_bytes.replace(
        old_hash.encode("utf-8"), new_hash.encode("utf-8")
    )
    assert len(new_header_bytes) == len(header_bytes), (
        "Header length shifted unexpectedly"
    )
    content[16 : 16 + header_len] = new_header_bytes

    with open(asar_path, "wb") as f:
        f.write(content)

    print(f"Successfully patched {asar_path}")
    print(f"  Old SHA256: {old_hash}")
    print(f"  New SHA256: {new_hash}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "resources/app.asar"
    patch_asar(path)
