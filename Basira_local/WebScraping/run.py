#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Start Basira Web Scraping Local using Python only."""
import os
import sys
import webbrowser

from app import app, BASIRA_HOST, BASIRA_PORT, is_port_in_use

if __name__ == "__main__":
    if is_port_in_use(BASIRA_PORT):
        print(f"ERROR: Port {BASIRA_PORT} is already in use.")
        print("Close the other program using this port, or set a different BASIRA_PORT.")
        sys.exit(1)

    url = f"http://{BASIRA_HOST}:{BASIRA_PORT}"
    print("Basira Web Scraping Local")
    print(f"Running at: {url}")
    print("Press Ctrl+C to stop.")

    if os.environ.get("BASIRA_NO_BROWSER") != "1":
        try:
            webbrowser.open(url)
        except Exception:
            pass

    app.run(host=BASIRA_HOST, port=BASIRA_PORT, debug=False)
