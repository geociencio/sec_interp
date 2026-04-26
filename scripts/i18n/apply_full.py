import os
import json
import sys
import xml.etree.ElementTree as ET
import html  # noqa: F401


def apply_translations(ts_file, lang_code, translations_map):
    """
    Applies translations to a .ts file using ElementTree for XML safety.
    """
    if not os.path.exists(ts_file):
        print(f"File not found: {ts_file}")
        return

    # Parse XML
    try:
        # Register namespace to avoid 'ns0' prefixes
        # Qt TS files usually don't have a namespace URI in the tag itself
        # but sometimes they do. ElementTree handles simple cases well.
        tree = ET.parse(ts_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"XML Parse Error in {ts_file}: {e}")
        return

    count = 0
    for context in root.findall("context"):
        for message in context.findall("message"):
            source = message.find("source")
            if source is None or not source.text:
                continue

            # Verbatim source text as seen by XML parser (unescaped)
            source_text = source.text

            # Lookup strategy: Verbatim, then stripped
            translation_val = translations_map.get(source_text)
            if not translation_val:
                translation_val = translations_map.get(source_text.strip())

            if translation_val:
                translation = message.find("translation")
                if translation is not None:
                    translation.text = translation_val
                    # Remove 'type="unfinished"'
                    if (
                        "type" in translation.attrib
                        and translation.attrib["type"] == "unfinished"
                    ):
                        del translation.attrib["type"]
                    count += 1

    # Native Python 3.9+ XML Beautifier
    if hasattr(ET, "indent"):
        ET.indent(tree, space="    ")

    # Save XML
    tree.write(ts_file, encoding="utf-8", xml_declaration=True)
    print(f"Applied {count} translations to {ts_file} for {lang_code}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 apply_full.py <lang_code> <json_file>")
        sys.exit(1)

    lang = sys.argv[1]
    json_path = sys.argv[2]
    ts_path = f"i18n/SecInterp_{lang}.ts"

    if not os.path.exists(json_path):
        print(f"JSON not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    apply_translations(ts_path, lang, mapping)
