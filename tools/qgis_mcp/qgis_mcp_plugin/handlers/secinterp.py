"""SecInterp fork: commands that drive the SecInterp plugin's dialog.

This module is the *extension* half of the vendored
`nkarasiak/qgis-mcp <https://github.com/nkarasiak/qgis-mcp>`_ fork. The upstream
handlers drive QGIS itself (layers, processing, rendering); these ones drive
**SecInterp** — opening its dialog, running a preview, reading the results text
and exporting — so an agent can smoke-test the plugin against a live QGIS 4
session.

It is deliberately *not* generic: every command reaches the running SecInterp
plugin through ``qgis.utils.plugins["sec_interp"]`` and calls the same
managers the GUI buttons call. No ``execute_code`` is involved.

Keep this module Python 3.9-compatible (QGIS ships 3.9 well past 3.28; see
``tests/test_py39_compat.py``) and reach package-root modules with ``..``
(``tests/test_plugin_structure.py``).
"""

from pathlib import Path

from ..errors import CommandError
from ..registry import command

# Package folder name QGIS registers the plugin under (make deploy -> plugins/sec_interp).
SEC_INTERP_PLUGIN_ID = "sec_interp"


class SecInterpHandlers:
    """Bridge commands to the running SecInterp plugin."""

    @staticmethod
    def _secinterp_plugin():
        """The active SecInterp plugin instance, or raise :class:`CommandError`."""
        from qgis.utils import plugins

        plugin = plugins.get(SEC_INTERP_PLUGIN_ID)
        if plugin is None:
            raise CommandError(
                "SecInterp plugin is not loaded. Enable it in Plugins > Manage and Install Plugins."
            )
        return plugin

    def _secinterp_dialog(self):
        """The SecInterp dialog, or raise when the plugin failed to build it."""
        plugin = self._secinterp_plugin()
        dialog = getattr(plugin, "dlg", None)
        if dialog is None:
            raise CommandError("SecInterp dialog failed to initialize; check the QGIS message log.")
        return plugin, dialog

    @command
    def secinterp_status(self, **kwargs):
        """Report whether SecInterp is loaded and what its dialog is doing."""
        from qgis.utils import plugins

        plugin = plugins.get(SEC_INTERP_PLUGIN_ID)
        status = {
            "loaded": plugin is not None,
            "plugin_id": SEC_INTERP_PLUGIN_ID,
        }
        if plugin is None:
            return status

        dialog = getattr(plugin, "dlg", None)
        status["dialog_ready"] = dialog is not None
        if dialog is None:
            return status

        status["dialog_visible"] = bool(dialog.isVisible())

        preview_manager = getattr(dialog, "preview_manager", None)
        if preview_manager is not None:
            try:
                status["preview_current"] = bool(preview_manager.is_preview_current())
            except Exception:
                status["preview_current"] = None

        widget = getattr(dialog, "preview_widget", None)
        if widget is not None and hasattr(widget, "results_text"):
            status["results_length"] = len(widget.results_text.toPlainText())

        return status

    @command
    def secinterp_open(self, **kwargs):
        """Open the SecInterp dialog *without* blocking the socket server.

        Mirrors ``PluginLifecycleMixin.run`` minus its trailing ``dialog.exec()``.
        ``exec()`` would start a nested Qt event loop and hold this command (and,
        through the server's re-entrancy guard, every later one) until the user
        closed the window — useless for automation. ``show()`` presents the same
        dialog and returns at once.
        """
        plugin, dialog = self._secinterp_dialog()

        if getattr(plugin, "first_start", False):
            plugin.first_start = False
            preview_renderer = getattr(plugin, "preview_renderer", None)
            if preview_renderer is not None:
                preview_renderer.canvas = dialog.preview_widget.canvas
            with_accept = getattr(dialog, "accepted", None)
            if with_accept is not None:
                with_accept.connect(plugin.process_data)

        signal_manager = getattr(dialog, "signal_manager", None)
        if signal_manager is not None:
            signal_manager.connect_all()

        loader = getattr(dialog, "_load_interpretations", None)
        if callable(loader):
            loader()
        loader = getattr(dialog, "_load_user_settings", None)
        if callable(loader):
            loader()

        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        return {"opened": True, "visible": bool(dialog.isVisible())}

    @command
    def secinterp_run_preview(self, **kwargs):
        """Run the dialog's preview pipeline (the 'Preview' button's work)."""
        _plugin, dialog = self._secinterp_dialog()

        manager = getattr(dialog, "preview_manager", None)
        if manager is None:
            raise CommandError("SecInterp preview manager is unavailable.")

        try:
            success, message = manager.generate_preview()
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f"Preview generation failed: {e}") from e

        return {"success": bool(success), "message": str(message)}

    @command
    def secinterp_assert_preview_ready(self, **kwargs):
        """Assert the last preview matches the current inputs (S2 gate)."""
        _plugin, dialog = self._secinterp_dialog()

        manager = getattr(dialog, "preview_manager", None)
        if manager is None:
            raise CommandError("SecInterp preview manager is unavailable.")

        try:
            ready = bool(manager.is_preview_current())
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f"Could not evaluate preview state: {e}") from e

        detail = (
            "Preview matches the current inputs."
            if ready
            else ("No current preview: run secinterp_run_preview first, or the inputs changed.")
        )
        return {"ready": ready, "detail": detail}

    @command
    def secinterp_read_results(self, **kwargs):
        """Return the text SecInterp wrote to its results panel."""
        _plugin, dialog = self._secinterp_dialog()

        widget = getattr(dialog, "preview_widget", None)
        if widget is None or not hasattr(widget, "results_text"):
            raise CommandError("SecInterp results panel is unavailable.")

        text = widget.results_text.toPlainText()
        return {"text": text, "length": len(text)}

    @command
    def secinterp_export_preview(self, path, **kwargs):
        """Export the current preview image to *path*.

        Goes straight to ``ExportManager._execute_preview_export`` with the
        caller's path: ``export_preview()`` would open a modal file dialog and
        block the server. Requires a preview to have been generated first.
        """
        _plugin, dialog = self._secinterp_dialog()

        export_manager = getattr(dialog, "export_manager", None)
        if export_manager is None:
            raise CommandError("SecInterp export manager is unavailable.")

        render_state = getattr(dialog, "render_state", None)
        canvas = getattr(render_state, "canvas", None)
        if canvas is None:
            raise CommandError("No preview canvas yet; run secinterp_run_preview first.")

        layers = canvas.layers()
        if not layers:
            raise CommandError("No preview layers to export; run secinterp_run_preview first.")

        try:
            success = export_manager._execute_preview_export(Path(path), layers)
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f"Preview export failed: {e}") from e

        return {"success": bool(success), "path": str(path)}
