import os
import re
import json
import sys


def apply_translations(ts_file, lang_code, translations_map):
    """
    Applies translations to a .ts file.
    translations_map: dict where key is the source string.
    """
    if not os.path.exists(ts_file):
        print(f"File not found: {ts_file}")
        return

    with open(ts_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find <message> blocks
    # We need to be careful with multi-line messages and tags
    pattern = re.compile(
        r"(<message>.*?(?:<location[^>]*/>\s*)*<source>(.*?)</source>.*?<translation[^>]*>).*?(</translation>.*?) </message>",
        re.DOTALL,
    )

    def replacer(match):
        prefix = match.group(1)
        source = match.group(2).strip()
        suffix = match.group(3)

        # Clean prefix from unfinished marker if we have a translation
        if source in translations_map:
            translation = translations_map[source]
            # Remove type="unfinished" if present
            new_prefix = re.sub(r' type="unfinished"', "", prefix)
            return f"{new_prefix}{translation}{suffix} </message>"
        return match.group(0)

    new_content = pattern.sub(replacer, content)

    with open(ts_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Applied translations to {ts_file} for {lang_code}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 apply_full.py <lang_code> <json_file>")
        sys.exit(1)

    lang = sys.argv[1]
    json_path = sys.argv[2]
    ts_path = f"i18n/SecInterp_{lang}.ts"

    with open(json_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    apply_translations(ts_path, lang, mapping)
