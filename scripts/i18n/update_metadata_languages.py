#!/usr/bin/env python3
"""
Update metadata.txt with the list of supported languages.
Ensures QGIS configparser compatibility by escaping % signs.
"""

import os  # noqa: F401
import re  # noqa: F401
from pathlib import Path

# ISO codes to names mapping
ISO_MAP = {
    "es": "Spanish",
    "fr": "French",
    "pt_BR": "Portuguese (Brazil)",
    "de": "German",
    "ru": "Russian",
    "zh_CN": "Chinese (Simplified)",
    "id": "Indonesian",
    "it": "Italian",
    "pl": "Polish",
    "nl": "Dutch",
    "fi": "Finnish",
    "hi": "Hindi",
    "ja": "Japanese",
}


def get_supported_languages():
    """Detect translation files in i18n/ directory."""
    i18n_dir = Path("i18n")
    if not i18n_dir.exists():
        return []

    codes = set()
    # Support both .ts and .qm
    for f in i18n_dir.glob("SecInterp_*.ts"):
        code = f.stem.replace("SecInterp_", "")
        codes.add(code)

    # Sort codes to ensure deterministic output
    sorted_codes = sorted(list(codes))

    languages = ["English"]  # Always support English
    for code in sorted_codes:
        name = ISO_MAP.get(code, code)
        if name not in languages:
            languages.append(name)

    return languages


def escape_percent(text):
    """
    Escape % as %% for QGIS metadata.txt (configparser compatibility).
    Wait, the rule says escape % as %%%% if it's already a percentage or just %%?
    Actually, configparser needs doubling. If it's used in metadata, QGIS handles it.
    Reference from update_metadata_rule.py says escape %% as %%%%.
    """
    return text.replace("%", "%%")


def update_metadata():
    """Update metadata.txt with supported languages."""
    metadata_file = Path("metadata.txt")
    if not metadata_file.exists():
        print("Error: metadata.txt not found.")
        return

    languages = get_supported_languages()
    lang_str = ", ".join(languages)
    description_line = f"Supported languages: {lang_str}"

    with open(metadata_file, "r") as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if line.startswith("general_description="):
            new_lines.append(
                f"general_description={escape_percent(description_line)}\n"
            )
            found = True
        else:
            new_lines.append(line)

    if not found:
        # Insert after description if not found
        for i, line in enumerate(new_lines):
            if line.startswith("description="):
                new_lines.insert(
                    i + 1, f"general_description={escape_percent(description_line)}\n"
                )
                found = True
                break

    if not found:
        # Append to [general] section if still not found
        for i, line in enumerate(new_lines):
            if line.strip() == "[general]":
                new_lines.insert(
                    i + 1, f"general_description={escape_percent(description_line)}\n"
                )
                found = True
                break

    with open(metadata_file, "w") as f:
        f.writelines(new_lines)

    print(f"Updated metadata.txt with languages: {lang_str}")


if __name__ == "__main__":
    update_metadata()
