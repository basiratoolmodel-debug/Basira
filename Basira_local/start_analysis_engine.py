"""
Analysis Engine Startup Script with Diagnostics
================================================
Checks all requirements before starting the server.
"""

import sys
from pathlib import Path

print("=" * 70)
print("  BASIRA ANALYSIS ENGINE - STARTUP DIAGNOSTICS")
print("=" * 70)
print()

# ─── Check 1: Python version ──────────────────────────────────────────
print("[1] Checking Python version...")
if sys.version_info < (3, 8):
    print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} is too old!")
    print("   Required: Python 3.8+")
    sys.exit(1)
print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print()

# ─── Check 2: Required Python files ──────────────────────────────────
print("[2] Checking required Python modules...")
BASE_DIR = Path(__file__).resolve().parent
required_files = [
    "basira_bridge_orchestrator.py",
    "supervised_engine_F.py",
    "unsupervised_engine_F.py",
    "rca_engine_F.py",
    "insight_engine_F.py",
    "charts_engine.py",
]

missing = []
for filename in required_files:
    filepath = BASE_DIR / filename
    if filepath.exists():
        print(f"✅ {filename}")
    else:
        print(f"❌ {filename} NOT FOUND")
        missing.append(filename)

if missing:
    print()
    print(f"⚠️  Missing {len(missing)} required file(s)!")
    print("   Cannot start Analysis Engine without these files.")
    sys.exit(1)
print()

# ─── Check 3: Required HTML templates ────────────────────────────────
print("[3] Checking HTML templates...")
required_html = [
    "basira_analysis_engine.html",
    "chart_management.html",
]

missing_html = []
for filename in required_html:
    filepath = BASE_DIR / filename
    if filepath.exists():
        print(f"✅ {filename}")
    else:
        print(f"⚠️  {filename} NOT FOUND (will cause 404 errors)")
        missing_html.append(filename)

if missing_html:
    print()
    print("⚠️  Some HTML files are missing.")
    print("   Server will start but routes may fail.")
    print()
print()

# ─── Check 4: Required Python packages ───────────────────────────────
print("[4] Checking Python packages...")
required_packages = [
    "flask",
    "flask_cors",
    "pandas",
    "numpy",
    "sklearn",
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} NOT INSTALLED")
        missing_packages.append(package)

if missing_packages:
    print()
    print(f"❌ Missing {len(missing_packages)} package(s)!")
    print("   Install them with:")
    print(f"   pip install {' '.join(missing_packages)}")
    sys.exit(1)
print()

# ─── Check 5: Port availability ──────────────────────────────────────
print("[5] Checking port 5055...")
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    result = s.connect_ex(("127.0.0.1", 5055))
    if result == 0:
        print("⚠️  Port 5055 is ALREADY IN USE!")
        print("   Another instance might be running.")
        print("   Kill it first or it will conflict.")
        print()
    else:
        print("✅ Port 5055 is available")
print()

# ─── All checks passed ────────────────────────────────────────────────
print("=" * 70)
print("✅ ALL CHECKS PASSED - Starting Analysis Engine...")
print("=" * 70)
print()

# ─── Start the server ─────────────────────────────────────────────────
try:
    import basira_bridge_orchestrator
    # The module's __main__ block will run the Flask app
except Exception as e:
    print()
    print("=" * 70)
    print("❌ SERVER FAILED TO START")
    print("=" * 70)
    print(f"Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
