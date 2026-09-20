"""Plugin information (read-only) settings tab."""

from __future__ import annotations

from collections.abc import Callable

from qgis.PyQt.QtWidgets import QLabel, QVBoxLayout, QWidget

from sec_interp.core.utils.metadata_reader import read_plugin_metadata
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def build_info_tab(translate: Callable[[str], str], parent: QWidget | None = None) -> QWidget:
    """Build the read-only plugin information tab.

    Args:
        translate: Callable used to translate user-facing strings.
        parent: Optional parent widget.

    Returns:
        A QWidget containing plugin metadata labels.

    """
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)

    try:
        metadata = read_plugin_metadata()
        layout.addWidget(QLabel(translate("<b>Plugin Information</b>")))
        layout.addWidget(QLabel(translate(f"{metadata['name']} v{metadata['version']}")))
        layout.addWidget(QLabel(translate(f"Developed by {metadata['author']}")))
        layout.addWidget(QLabel(translate(f"Contact: {metadata['email']}")))

        if metadata.get("homepage"):
            doc_label = QLabel(f"<a href='{metadata['homepage']}'>{translate('Documentation')}</a>")
            doc_label.setOpenExternalLinks(True)
            layout.addWidget(doc_label)

    except (FileNotFoundError, ValueError) as e:
        logger.warning(f"Metadata read error: {e}")
        layout.addWidget(QLabel(translate("<b>Plugin Information</b>")))
        layout.addWidget(QLabel(translate("Sec Interp (version unavailable)")))
        layout.addWidget(QLabel(translate("Metadata missing")))

    layout.addStretch()
    return widget
