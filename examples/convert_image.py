#!/usr/bin/env python3
import sys
import subprocess
import shutil
from pathlib import Path
import sys
import os
import epd_util

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 conver_image.py <input_image.jpg> <output_image.s6>")
        sys.exit(1)

    input_image = Path(sys.argv[1])
    output_image = Path(sys.argv[2])
    if not input_image.exists():
        print("File not found.")
        sys.exit(1)

    if not shutil.which("convert"):
        print("`convert` not found. Please install imagemagick.")
        sys.exit(1)

    try:
        epd_util.convert_image_to_s6(input_image, output_image)
    except Exception as e:
        print(f"convert image failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
