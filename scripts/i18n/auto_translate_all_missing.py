import os
import sys
import json
import xml.etree.ElementTree as ET
import time
import re
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError  # noqa: F401

# Mapping from SecInterp language code to Google Translate language code
LANG_MAP = {
    "de": "de",
    "es": "es",
    "fi": "fi",
    "fr": "fr",
    "hi": "hi",
    "id": "id",
    "it": "it",
    "ja": "ja",
    "nl": "nl",
    "pl": "pl",
    "pt_BR": "pt",
    "ru": "ru",
    "zh_CN": "zh-CN",
}


def extract_missing(ts_file):
    tree = ET.parse(ts_file)
    root = tree.getroot()
    missing_strings = {}

    for context in root.findall("context"):
        for message in context.findall("message"):
            translation = message.find("translation")
            if translation is not None and translation.get("type") == "unfinished":
                source = message.find("source")
                if source is not None and source.text:
                    missing_strings[source.text] = ""
    return missing_strings


import concurrent.futures  # noqa: E402


def translate_strings(strings_dict, target_lang):
    translated_dict = {}

    def translate_single(k):
        try:
            # Protect placeholders from being translated/mangled
            placeholders = re.findall(r"(\{[^}]+\})", k)
            k_protected = k
            for i, ph in enumerate(placeholders):
                k_protected = k_protected.replace(ph, f" _PH{i}_ ")

            translator = GoogleTranslator(source="en", target=target_lang)
            # Retries to avoid rate limit issues
            for _ in range(3):
                try:
                    res = translator.translate(k_protected)
                    if res:
                        # Restore placeholders
                        for i, ph in enumerate(placeholders):
                            res = re.sub(rf" _PH{i}_ ", ph, res, flags=re.IGNORECASE)
                            res = res.replace(f"_PH{i}_", ph)  # Fallback
                        return k, res
                except Exception:
                    time.sleep(1)
            return k, ""
        except Exception as e:  # noqa: F841
            return k, ""

    keys = list(strings_dict.keys())
    print(f"    Translating {len(keys)} strings in parallel for {target_lang}...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(translate_single, k): k for k in keys}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            k, v = future.result()
            translated_dict[k] = v
            if (i + 1) % 20 == 0:
                print(f"      {i+1}/{len(keys)} done...")  # noqa: E226

    return translated_dict


def update_master_data(lang):
    ts_file = f"i18n/SecInterp_{lang}.ts"
    master_file = f"scripts/i18n/master_data/{lang}.json"

    if not os.path.exists(ts_file):
        print(f"File {ts_file} not found, skipping.")
        return

    google_lang = LANG_MAP.get(lang, lang)

    print(f"Processing {lang} to {google_lang}...")

    missing = extract_missing(ts_file)
    if not missing:
        print(f"  No missing translations found for {lang}.")
        return

    print(f"  Found {len(missing)} missing translations.")

    # Load existing master data
    master_data = {}
    if os.path.exists(master_file):
        with open(master_file, "r", encoding="utf-8") as f:
            try:
                master_data = json.load(f)
            except json.JSONDecodeError:
                pass

    # Filter out ones that are already translated in master data
    to_translate = {}
    for k in missing:
        if k not in master_data or not master_data[k]:
            to_translate[k] = ""

    if not to_translate:
        print(
            f"  All {len(missing)} missing translations are already mapped in {master_file}."
        )
        return

    print(f"  Translating {len(to_translate)} strings using Google Translate...")
    translated = translate_strings(to_translate, google_lang)

    for k, v in translated.items():
        if v:
            master_data[k] = v

    with open(master_file, "w", encoding="utf-8") as f:
        json.dump(master_data, f, indent=4, ensure_ascii=False, sort_keys=True)

    print(f"  Successfully updated {master_file} with {len(translated)} translations.")


if __name__ == "__main__":
    langs = sys.argv[1:]
    if not langs:
        langs = [lang for lang in LANG_MAP.keys()]

    for lang in langs:
        update_master_data(lang)
