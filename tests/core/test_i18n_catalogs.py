"""Quality gates for the shipped Qt translation catalogs."""

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_I18N = _ROOT / "i18n"
_LOCALES = [
    "de", "es", "fi", "fr", "hi", "id", "it",
    "ja", "nl", "pl", "pt_BR", "ru", "zh_CN",
]
_PLACEHOLDER = re.compile(r"(\{[^}]*\}|%[sd])")
_TAGS = ("<b>", "</b>", "<i>", "</i>")


def _messages(locale):
    root = ET.parse(_I18N / f"SecInterp_{locale}.ts").getroot()
    for context in root.findall("context"):
        for message in context.findall("message"):
            yield message


class TestTranslationCatalogs(unittest.TestCase):
    """Every supported locale must be complete and safe to render."""

    def test_all_locales_have_no_unfinished_messages(self):
        offenders = {}
        for locale in _LOCALES:
            unfinished = [
                message.findtext("source")
                for message in _messages(locale)
                if message.find("translation") is not None
                and message.find("translation").get("type") == "unfinished"
            ]
            if unfinished:
                offenders[locale] = unfinished
        self.assertEqual(offenders, {}, f"Unfinished translations: {offenders}")

    def test_all_messages_have_translation_text(self):
        offenders = {}
        for locale in _LOCALES:
            missing = [
                message.findtext("source")
                for message in _messages(locale)
                if not (message.findtext("translation") or "").strip()
            ]
            if missing:
                offenders[locale] = missing
        self.assertEqual(offenders, {}, f"Empty translations: {offenders}")

    def test_placeholders_are_preserved(self):
        offenders = []
        for locale in _LOCALES:
            for message in _messages(locale):
                source = message.findtext("source") or ""
                translation = message.findtext("translation") or ""
                if set(_PLACEHOLDER.findall(source)) != set(_PLACEHOLDER.findall(translation)):
                    offenders.append(f"{locale}: {source!r} -> {translation!r}")
        self.assertEqual(offenders, [], f"Placeholder mismatch: {offenders}")

    def test_html_tags_are_preserved(self):
        offenders = []
        for locale in _LOCALES:
            for message in _messages(locale):
                source = message.findtext("source") or ""
                translation = message.findtext("translation") or ""
                if any((tag in source) != (tag in translation) for tag in _TAGS):
                    offenders.append(f"{locale}: {source!r} -> {translation!r}")
        self.assertEqual(offenders, [], f"HTML tag mismatch: {offenders}")

    def test_new_v311_strings_are_translated(self):
        required = ("Reset unit styles", "Symbology", "Drillhole lithologies")
        offenders = []
        for locale in _LOCALES:
            root = ET.parse(_I18N / f"SecInterp_{locale}.ts").getroot()
            pairs = {}
            for context in root.findall("context"):
                for message in context.findall("message"):
                    source = message.findtext("source")
                    if source in required:
                        pairs[source] = message.findtext("translation") or ""
            for source in required:
                if not pairs.get(source) or pairs[source] == source:
                    offenders.append(f"{locale}: {source!r}")
        self.assertEqual(offenders, [], f"New strings not translated: {offenders}")

    def test_compiled_catalogs_exist(self):
        missing = [
            locale for locale in _LOCALES
            if not (_I18N / f"SecInterp_{locale}.qm").is_file()
            or (_I18N / f"SecInterp_{locale}.qm").stat().st_size == 0
        ]
        self.assertEqual(missing, [], f"Missing/empty .qm catalogs: {missing}")


if __name__ == "__main__":
    unittest.main()
