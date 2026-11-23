#!/usr/bin/env python3
"""Test the entry: run main.py twice, check determinism and limits."""

import hashlib
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run_once(out_dir):
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = out_dir
    subprocess.run([sys.executable, "main.py"], cwd=HERE, env=env,
                   check=True)
    with open(os.path.join(out_dir, "entry.png"), "rb") as f:
        return f.read()


def main():
    a = run_once(os.path.join(HERE, "test-out-a"))
    b = run_once(os.path.join(HERE, "test-out-b"))
    assert a == b, "two runs differ"
    assert len(a) <= 1048576, f"too big: {len(a)} bytes"
    assert a[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    w, h = struct.unpack(">II", a[16:24])
    assert (w, h) == (1024, 1024), f"wrong size: {w}x{h}"
    print(f"PASS: byte-identical, {len(a)} bytes, 1024x1024 PNG")
    print("sha256:", hashlib.sha256(a).hexdigest())


if __name__ == "__main__":
    main()
