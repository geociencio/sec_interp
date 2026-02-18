import os
import json
import re
from pathlib import Path


def load_master_data(locale):
    """Load translation master data for a given locale."""
    json_path = Path(f"scripts/i18n/master_data/{locale}.json")
    if not json_path.exists():
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def translate_po_file(po_path, master_data):
    """Update a .po file with translations from master_data."""
    if not master_data:
        return False

    print(f"📖 Processing {po_path}...")
    with open(po_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    translated_count = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("msgid "):
            # Extract msgid (handle multi-line msgid)
            msgid = re.search(r'msgid "(.*)"', line).group(1)
            msgid_lines = [msgid]
            i += 1
            while i < len(lines) and lines[i].startswith('"'):
                msgid_lines.append(re.search(r'"(.*)"', lines[i]).group(1))
                i += 1
            full_msgid = "".join(msgid_lines)

            # Find next msgstr
            while i < len(lines) and not lines[i].startswith("msgstr "):
                new_lines.append(lines[i - 1])  # This is tricky, let's simplify logic
                i += 1

            # This logic above is a bit broken for re-ordering.
            # Let's use a more robust approach.
            pass
        # Resetting logic for simpler line-by-line with state machine
        i += 1

    # RE-IMPLEMENTING ROBUST PO PARSER
    content = "".join(lines)
    parts = re.split(r'(msgid ".*?"(?:\n".*?")*)', content, flags=re.DOTALL)

    # This is also getting complex. Let's use a simple key-value replacement
    # since we know the format is msgid followed by msgstr

    new_content = ""
    current_msgid = None

    for line in lines:
        if line.startswith("msgid "):
            current_msgid = re.search(r'msgid "(.*)"', line).group(1)
            new_content += line
        elif line.startswith("msgstr "):
            if current_msgid in master_data and line.strip() == 'msgstr ""':
                translation = master_data[current_msgid]
                new_content += f'msgstr "{translation}"\n'
                translated_count += 1
            else:
                new_content += line
            current_msgid = None
        else:
            new_content += line

    if translated_count > 0:
        with open(po_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  ✅ Translated {translated_count} strings.")
        return True
    return False


def translate_all():
    locales_dir = Path("docs/locales")
    for locale_path in locales_dir.iterdir():
        if not locale_path.is_dir():
            continue

        locale = locale_path.name
        if locale == "en":
            continue

        master_data = load_master_data(locale)
        po_files = list(locale_path.glob("**/LC_MESSAGES/*.po"))

        for po_file in po_files:
            translate_po_file(po_file, master_data)


if __name__ == "__main__":
    translate_all()
