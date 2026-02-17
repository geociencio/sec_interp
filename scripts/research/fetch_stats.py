#!/usr/bin/env python3
"""
Fetch QGIS Plugin statistics.
This script scrapes the official QGIS plugin repository to get the latest
download statistics for SecInterp.
"""

import datetime
import re
from pathlib import Path

import requests


def fetch_stats(plugin_name: str = "sec_interp"):
    url = f"https://plugins.qgis.org/plugins/{plugin_name}/"
    proxies = {}  # Add proxies if needed

    print(f"📡 Fetching stats from: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # The plugin repository shows downloads per version in a table
        # We find all occurrences of <td class="downloads">X</td> and sum them
        html = response.text

        matches = re.findall(
            r'<td class="downloads">([\d,.]+)</td>', html, re.IGNORECASE
        )

        if matches:
            total_downloads = 0
            for val in matches:
                clean_val = val.replace(",", "").replace(".", "")
                total_downloads += int(clean_val)
            print(f"✅ Found total downloads across versions: {total_downloads}")
            return total_downloads
        else:
            print("❌ Could not find downloads count in the page.")
            return None

    except Exception as e:
        print(f"💥 Error fetching stats: {e}")
        return None


def log_stats(downloads: int, plugin_name: str = "sec_interp"):
    if downloads is None:
        return

    date_str = datetime.date.today().isoformat()
    log_dir = Path("logs/research")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "download_history.csv"

    # Write header if file doesn't exist
    if not log_file.exists():
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("date,plugin,downloads\n")

    # Append new entry
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{date_str},{plugin_name},{downloads}\n")

    print(f"📝 Statistics logged to: {log_file}")


if __name__ == "__main__":
    count = fetch_stats()
    log_stats(count)
