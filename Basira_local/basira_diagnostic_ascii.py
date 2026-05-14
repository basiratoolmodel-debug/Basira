"""
basira_diagnostic.py - Basira Diagnostic Tool (ASCII Version)
=============================================================
This script checks:
1. Required files exist
2. Python and Flask are installed  
3. Attempts to start servers and shows errors
4. Gives you a clear report

Usage:
------
Put this file in the same folder as launcher.py, then run:

    python basira_diagnostic.py

It will give you a complete report.
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("  BASIRA DIAGNOSTIC TOOL")
print("=" * 70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

# =========================================================================
# 1. Check Folders and Paths
# =========================================================================
print("[ 1 ] Checking folders and paths...")
print("-" * 70)

SCRIPT_DIR = Path(__file__).resolve().parent
print(f"[OK] Current script directory: {SCRIPT_DIR}")

# Check templates folder
TEMPLATES_DIR = SCRIPT_DIR / "templates"
if TEMPLATES_DIR.exists():
    print(f"[OK] templates folder exists: {TEMPLATES_DIR}")
else:
    print(f"[!]  templates folder NOT found: {TEMPLATES_DIR}")
    print("     -> Will check in current directory instead")
    TEMPLATES_DIR = SCRIPT_DIR

print()

# =========================================================================
# 2. Check Required Files
# =========================================================================
print("[ 2 ] Checking required files...")
print("-" * 70)

REQUIRED_FILES = {
    "Preprocessor (Port 5050)": [
        "basira_app.py",
        "launcher_preprocessor.py"
    ],
    "Analysis Engine (Port 5055)": [
        "basira_bridge_orchestrator.py",
        "charts_engine.py",
        "insight_engine_F.py",
        "rca_engine_F.py",
        "supervised_engine_F.py",
        "unsupervised_engine_F.py",
        "launch_analysis.py"
    ],
    "HTML Files": [
        "basira_preprocessor.html",
        "basira_analysis_engine.html",
        "chart_management.html"
    ]
}

missing_files = []
found_files = []

for category, files in REQUIRED_FILES.items():
    print(f"\n{category}:")
    for filename in files:
        # Check in templates or current dir
        file_path = None
        for check_dir in [TEMPLATES_DIR, SCRIPT_DIR]:
            potential_path = check_dir / filename
            if potential_path.exists():
                file_path = potential_path
                break
        
        if file_path:
            size = file_path.stat().st_size / 1024  # KB
            location = file_path.parent.name + "/"
            print(f"  [OK] {filename:<35} ({size:>6.1f} KB) in {location}")
            found_files.append(file_path)
        else:
            print(f"  [X]  {filename:<35} NOT FOUND")
            missing_files.append(filename)

print()
if missing_files:
    print(f"[!] Missing files ({len(missing_files)}):")
    for f in missing_files:
        print(f"    - {f}")
else:
    print(f"[OK] All files found ({len(found_files)} files)")

print()

# =========================================================================
# 3. Check Python and Dependencies
# =========================================================================
print("[ 3 ] Checking Python and required libraries...")
print("-" * 70)

print(f"[OK] Python Version: {sys.version}")
print(f"[OK] Python Path: {sys.executable}")
print()

# Check required packages
REQUIRED_PACKAGES = [
    "flask",
    "flask_cors",
    "pandas",
    "numpy",
    "sklearn",
    "scipy"
]

missing_packages = []
for package in REQUIRED_PACKAGES:
    try:
        __import__(package.replace("_", "-").replace("-", "_"))
        print(f"  [OK] {package:<20} installed")
    except ImportError:
        print(f"  [X]  {package:<20} NOT installed")
        missing_packages.append(package)

print()
if missing_packages:
    print(f"[!] Missing packages ({len(missing_packages)}):")
    for pkg in missing_packages:
        print(f"    - {pkg}")
    print()
    print("To install missing packages, run:")
    print(f"   pip install {' '.join(missing_packages)}")
else:
    print("[OK] All required packages are installed")

print()

# =========================================================================
# 4. Check Ports (Are they active?)
# =========================================================================
print("[ 4 ] Checking port status...")
print("-" * 70)

def read_scraper_port():
    for name in ("scraper.port", "templates/scraper.port"):
        try:
            return int((BASE_DIR / name).read_text(encoding="utf-8").strip())
        except Exception:
            pass
    return None

SCRAPER_PORT = read_scraper_port()
PORTS_TO_CHECK = {
    5001: "Bootstrap API",
    5000: "Main App",
    5050: "Preprocessor",
    5055: "Analysis Engine",
}
if SCRAPER_PORT:
    PORTS_TO_CHECK[SCRAPER_PORT] = "Web Scraper"

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0

active_ports = []
inactive_ports = []

for port, service in PORTS_TO_CHECK.items():
    if is_port_open(port):
        print(f"  [OK] Port {port:<5} ({service:<20}) ACTIVE")
        active_ports.append(port)
    else:
        print(f"  [X]  Port {port:<5} ({service:<20}) INACTIVE")
        inactive_ports.append(port)

print()
if inactive_ports:
    print(f"[!] Inactive ports: {', '.join(map(str, inactive_ports))}")
    print("    -> These servers have not started yet")
else:
    print("[OK] All servers are running")

print()

# =========================================================================
# 5. Test Preprocessor Startup (Port 5050)
# =========================================================================
if not is_port_open(5050) and "basira_app.py" not in missing_files:
    print("[ 5 ] Testing Preprocessor startup (Port 5050)...")
    print("-" * 70)
    
    basira_app_path = None
    for check_dir in [TEMPLATES_DIR, SCRIPT_DIR]:
        potential = check_dir / "basira_app.py"
        if potential.exists():
            basira_app_path = potential
            break
    
    if basira_app_path:
        print(f"Attempting to start: {basira_app_path}")
        print("Please wait 5 seconds...")
        
        try:
            # Start server in background
            process = subprocess.Popen(
                [sys.executable, str(basira_app_path), "--silent"],
                cwd=str(basira_app_path.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait 5 seconds
            time.sleep(5)
            
            # Check if server is running
            if is_port_open(5050):
                print("[OK] Preprocessor started successfully on port 5050!")
                print("     You can access it at: http://127.0.0.1:5050/health")
                
                # Kill the process
                process.terminate()
                print("     Test completed - server stopped")
            else:
                # Server didn't start - check errors
                stdout, stderr = process.communicate(timeout=2)
                
                print("[X] Failed to start Preprocessor")
                print()
                print("ERRORS:")
                print("-" * 70)
                if stderr:
                    print(stderr[:1000])  # First 1000 chars
                else:
                    print("(no error output)")
                print("-" * 70)
                
                # Check for import errors
                if "ModuleNotFoundError" in stderr or "ImportError" in stderr:
                    print()
                    print("[!] Looks like there's a missing library (ImportError)")
                    print("    Check section [ 3 ] above for missing packages")
        
        except Exception as e:
            print(f"[X] Error during startup attempt: {e}")
    
    print()

# =========================================================================
# 6. Test Analysis Engine Startup (Port 5055)
# =========================================================================
if not is_port_open(5055) and "basira_bridge_orchestrator.py" not in missing_files:
    print("[ 6 ] Testing Analysis Engine startup (Port 5055)...")
    print("-" * 70)
    
    bridge_path = None
    for check_dir in [TEMPLATES_DIR, SCRIPT_DIR]:
        potential = check_dir / "basira_bridge_orchestrator.py"
        if potential.exists():
            bridge_path = potential
            break
    
    if bridge_path:
        print(f"Attempting to start: {bridge_path}")
        print("Please wait 5 seconds...")
        
        try:
            # Start server in background
            process = subprocess.Popen(
                [sys.executable, str(bridge_path)],
                cwd=str(bridge_path.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait 5 seconds
            time.sleep(5)
            
            # Check if server is running
            if is_port_open(5055):
                print("[OK] Analysis Engine started successfully on port 5055!")
                print("     You can access it at: http://127.0.0.1:5055/health")
                
                # Kill the process
                process.terminate()
                print("     Test completed - server stopped")
            else:
                # Server didn't start - check errors
                try:
                    stdout, stderr = process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                
                print("[X] Failed to start Analysis Engine")
                print()
                print("ERRORS:")
                print("-" * 70)
                if stderr:
                    error_lines = stderr.strip().split('\n')
                    # Print last 30 lines of error
                    for line in error_lines[-30:]:
                        print(line)
                else:
                    print("(no error output)")
                print("-" * 70)
                
                # Check for import errors
                if "ModuleNotFoundError" in stderr:
                    import re
                    matches = re.findall(r"No module named '(\w+)'", stderr)
                    if matches:
                        print()
                        print(f"[!] Missing module: {matches[-1]}")
                        if matches[-1] == "charts_engine":
                            print("    >>> charts_engine.py is MISSING!")
                            print("    -> Put charts_engine.py in the same folder as basira_bridge_orchestrator.py")
                        else:
                            print(f"    -> Install it: pip install {matches[-1]}")
        
        except Exception as e:
            print(f"[X] Error during startup attempt: {e}")
    
    print()

# =========================================================================
# 7. Final Report and Recommendations
# =========================================================================
print("=" * 70)
print("  FINAL REPORT AND RECOMMENDATIONS")
print("=" * 70)
print()

issues = []
recommendations = []

# Check missing files
if missing_files:
    issues.append(f"[X] Missing files ({len(missing_files)})")
    recommendations.append(f"[1] Download missing files and put them in: {TEMPLATES_DIR}")
    if "charts_engine.py" in missing_files:
        recommendations.append("[!] charts_engine.py is MISSING - this is the most important file!")

# Check missing packages
if missing_packages:
    issues.append(f"[X] Missing Python packages ({len(missing_packages)})")
    recommendations.append(f"[2] Install packages: pip install {' '.join(missing_packages)}")

# Check ports
if 5050 in inactive_ports:
    issues.append("[X] Preprocessor (5050) not running")
    if "basira_app.py" in missing_files:
        recommendations.append("[3] basira_app.py is missing")
    else:
        recommendations.append("[3] Try starting manually: python basira_app.py")

if 5055 in inactive_ports:
    issues.append("[X] Analysis Engine (5055) not running")
    if "basira_bridge_orchestrator.py" in missing_files:
        recommendations.append("[4] basira_bridge_orchestrator.py is missing")
    elif "charts_engine.py" in missing_files:
        recommendations.append("[!] charts_engine.py is MISSING - main cause!")
    else:
        recommendations.append("[4] Try starting manually: python basira_bridge_orchestrator.py")

# Print issues
if issues:
    print("ISSUES FOUND:")
    print("-" * 70)
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    print()
else:
    print("[OK] No obvious issues found!")
    print()

# Print recommendations
if recommendations:
    print("RECOMMENDATIONS:")
    print("-" * 70)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    print()

# Next steps
print("NEXT STEPS:")
print("-" * 70)
if missing_files or missing_packages:
    print("1. Follow the recommendations above")
    print("2. Run this script again to verify")
    print("3. If issues are resolved, run launcher.py")
elif inactive_ports:
    print("1. Try starting servers manually (see sections 5 & 6 above)")
    print("2. Copy the FULL error message and send it")
    print("3. Make sure all files are in the same folder")
else:
    print("[OK] Everything looks good! Try:")
    print("   python launcher.py")

print()
print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print()
print("COPY THIS ENTIRE OUTPUT AND SEND IT FOR ANALYSIS")
print("=" * 70)
