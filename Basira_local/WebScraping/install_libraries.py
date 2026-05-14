#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install Basira dependencies using the current Python interpreter.
This NO-CHROMIUM edition installs only lightweight HTTP scraping libraries.
"""
import subprocess
import sys
from pathlib import Path

requirements = Path(__file__).with_name("requirements.txt")
if not requirements.exists():
    raise SystemExit("requirements.txt was not found next to this file.")

def run(cmd, label):
    print(label)
    subprocess.check_call(cmd)

run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip...")
run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], "Installing required Python libraries...")

print("Done. This edition does not install Playwright or Chromium.")
print("Now run: python run.py")
