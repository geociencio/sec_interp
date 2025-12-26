import json
from dataclasses import asdict
from pathlib import Path

from sec_interp.core.types import InterpretationPolygon
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class CacheHandler:
    """Handles cache and session persistence for the dialog."""

    def __init__(self, dialog: "sec_interp.gui.main_dialog.SecInterpDialog"):
        """Initialize cache handler.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance
        """
        self.dialog = dialog

    def save_session(self):
        """Save active interpretations to a JSON sidecar file."""
        if not self.dialog.interpretations:
            return

        try:
            values = self.dialog.get_selected_values()
            output_path_str = values.get("output_path")
            if not output_path_str:
                return

            output_dir = Path(output_path_str)
            if not output_dir.exists():
                return

            session_file = output_dir / "sec_interp_session.json"

            data = {
                "version": "1.0",
                "interpretations": [
                    asdict(interp) for interp in self.dialog.interpretations
                ],
            }

            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            logger.info(f"Interpretations session saved to {session_file}")
        except Exception as e:
            logger.error(f"Failed to save interpretations session: {e}")

    def load_session(self):
        """Load interpretations from a JSON sidecar file."""
        try:
            values = self.dialog.get_selected_values()
            output_path_str = values.get("output_path")
            if not output_path_str:
                return

            output_dir = Path(output_path_str)
            session_file = output_dir / "sec_interp_session.json"

            if not session_file.exists():
                return

            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "interpretations" not in data:
                return

            self.dialog.interpretations = []
            for interp_dict in data["interpretations"]:
                # Reconstruct dataclass
                self.dialog.interpretations.append(InterpretationPolygon(**interp_dict))

            logger.info(
                f"Loaded {len(self.dialog.interpretations)} interpretations from {session_file}"
            )
        except Exception as e:
            logger.error(f"Failed to load interpretations session: {e}")
