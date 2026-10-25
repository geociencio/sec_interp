"""Tests for the injectable core translation port."""

from __future__ import annotations

from sec_interp.core.data_cache import DataCache
from sec_interp.core.services.export.orchestrator import ExportService
from sec_interp.core.utils.i18n import TranslatableMixin, set_translator, translate
from tests.base_test import BaseTestCase


class TestTranslationPort(BaseTestCase):
    """Core translations work with identity fallback and injected backends."""

    def tearDown(self) -> None:
        set_translator(None)
        super().tearDown()

    def test_identity_without_backend(self) -> None:
        self.assertEqual(translate("Context", "Hello"), "Hello")

    def test_injected_backend_receives_context_and_message(self) -> None:
        calls: list[tuple[str, str]] = []
        set_translator(lambda context, message: calls.append((context, message)) or "T")
        self.assertEqual(translate("Context", "Hello"), "T")
        self.assertEqual(calls, [("Context", "Hello")])

    def test_mixin_uses_class_name_context(self) -> None:
        calls: list[tuple[str, str]] = []
        set_translator(lambda context, message: calls.append((context, message)) or message)

        class Example(TranslatableMixin):
            pass

        self.assertEqual(Example().tr("Message"), "Message")
        self.assertEqual(calls, [("Example", "Message")])

    def test_core_services_keep_their_contexts(self) -> None:
        calls: list[tuple[str, str]] = []
        set_translator(lambda context, message: calls.append((context, message)) or message)
        DataCache().tr("Cache message")
        ExportService().tr("Export message")
        self.assertEqual(
            calls,
            [("DataCache", "Cache message"), ("ExportService", "Export message")],
        )

    def test_reset_to_identity(self) -> None:
        set_translator(lambda context, message: "translated")
        set_translator(None)
        self.assertEqual(translate("Context", "Hello"), "Hello")
