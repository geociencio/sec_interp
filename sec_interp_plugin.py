"""Main Plugin Module.

Orchestrates the lifecycle of the SecInterp QGIS plugin.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import (
    QgsMapLayer,
    QgsProject,
)
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QSettings,
    QTranslator,
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from sec_interp.core.controller import ProfileController
from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import SecInterpError
from sec_interp.core.services.export_service import ExportService
from sec_interp.gui.main_dialog import SecInterpDialog
from sec_interp.gui.preview_renderer import PreviewRenderer
from sec_interp.logger_config import get_logger, setup_logging

logger = get_logger(__name__)


# DataCache has been moved to core/data_cache.py


class SecInterp:
    """QGIS Plugin Implementation for Geological Data Extraction.

    This class implements the main logic of the SecInterp plugin, handling
    initialization, UI integration, and orchestration of data processing tasks.
    It connects the QGIS interface with the plugin's dialog and processing algorithms.
    """

    def __init__(self, iface: Any) -> None:
        """Initialize the plugin.

        Args:
            iface (QgsInterface): An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.

        """
        # Initialize logging first
        setup_logging()

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = Path(__file__).resolve().parent
        # initialize locale
        user_locale = QSettings().value("locale/userLocale", "en")

        # Try full locale first (e.g., pt_BR)
        locale_path = self.plugin_dir / f"i18n/SecInterp_{user_locale}.qm"

        MIN_LOCALE_LENGTH = 2
        if (
            not locale_path.exists()
            and user_locale
            and len(user_locale) > MIN_LOCALE_LENGTH
        ):
            # Fallback to language code (e.g., pt)
            locale_short = user_locale[0:2]
            locale_path = self.plugin_dir / f"i18n/SecInterp_{locale_short}.qm"

        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path))
            QCoreApplication.installTranslator(self.translator)

        # Prepare core services BEFORE the dialog (required by PreviewManager)
        # Create preview renderer
        self.preview_renderer = PreviewRenderer()
        # Initialize controller
        self.controller = ProfileController()
        # Initialize export service
        self.export_service = ExportService(self.controller)

        # Create the dialog (after services and translation) and keep reference
        self.dlg = SecInterpDialog(self.iface, self)
        self.dlg.plugin_instance = self
        self.first_start = True

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&Sec Interp")
        # Create custom toolbar and make it visible
        self.toolbar = self.iface.addToolBar(self.tr("Sec Interp"))
        self.toolbar.setObjectName("SecInterp")
        self.toolbar.setVisible(True)  # Ensure toolbar is visible

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        Args:
            message (str): String for translation.

        Returns:
            str: Translated string (or original if no translation found).

        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("SecInterp", message)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Any,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str | None = None,
        whats_this: str | None = None,
        parent: Any = None,
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        Args:
            icon_path (str): Path to the icon for this action.
            text (str): Text that should be shown in menu items for this action.
            callback (function): Function to be called when the action is triggered.
            enabled_flag (bool): A flag indicating if the action should be enabled
                by default. Defaults to True.
            add_to_menu (bool): Flag indicating whether the action should also
                be added to the menu. Defaults to True.
            add_to_toolbar (bool): Flag indicating whether the action should also
                be added to the toolbar. Defaults to True.
            status_tip (str): Optional text to show in a popup when mouse pointer
                hovers over the action.
            whats_this (str): Optional text to show in the status bar when the
                mouse pointer hovers over the action.
            parent (QWidget): Parent widget for the new action. Defaults None.

        Returns:
            QAction: The action that was created. Note that the action is also
                added to self.actions list.

        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Add to custom toolbar
            self.toolbar.addAction(action)
            # Also add to Plugins toolbar for visibility
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self) -> None:  # noqa: N802
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Use absolute path to icon file to ensure it loads in toolbar
        icon_path = str(self.plugin_dir / "icon.png")
        self.add_action(
            icon_path,
            text=self.tr("Geological data extraction"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

    def unload(self) -> None:
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&Sec Interp"), action)
            self.iface.removeToolBarIcon(action)

        # Remove custom toolbar
        if self.toolbar:
            del self.toolbar
            self.toolbar = None

    def run(self) -> None:
        """Run method that performs all the real work."""
        if self.first_start:
            self.first_start = False
            # Dialog is already initialized in __init__
            # Update preview renderer with the dialog's canvas
            self.preview_renderer.canvas = self.dlg.preview_widget.canvas

            # Connect dialog accepted signal to final processing
            self.dlg.accepted.connect(self.process_data)

        # Reload interpretations and UI settings to reflect current project state
        self.dlg._load_interpretations()
        self.dlg._load_user_settings()
        # Show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def _resolve_layer_obj(
        self, value: Any, placeholder_text: str = ""
    ) -> QgsMapLayer | None:
        """Resolve layer object from UI value."""
        if isinstance(value, QgsMapLayer):
            return value
        if isinstance(value, str) and value:
            if placeholder_text and value == placeholder_text:
                return None
            # Try resolving by ID first (most robust)
            layer = QgsProject.instance().mapLayer(value)
            if not layer:
                # Fallback to name search
                for lyr in QgsProject.instance().mapLayers().values():
                    if lyr.name() == value:
                        layer = lyr
                        break
            return layer
        return None

    def _get_and_validate_inputs(self) -> PreviewParams | None:
        """Retrieve and validate inputs from the dialog."""
        values = self.dlg.get_selected_values()
        preview_options = self.dlg.get_preview_options()

        # 1. Get Layer IDs (PreviewParams now expects str)
        def get_id(val):
            if isinstance(val, QgsMapLayer):
                return val.id()
            return str(val) if val else None

        raster_id = get_id(values.get("raster_layer"))
        line_id = get_id(values.get("crossline_layer"))

        try:
            params = PreviewParams(
                raster_layer=raster_id,
                line_layer=line_id,
                band_num=values.get("selected_band", 1),
                buffer_dist=values.get("buffer_distance", 100.0),
                outcrop_layer=get_id(values.get("outcrop_layer")),
                outcrop_name_field=values.get("outcrop_name_field"),
                struct_layer=get_id(values.get("structural_layer")),
                dip_field=values.get("dip_field"),
                strike_field=values.get("strike_field"),
                dip_scale_factor=values.get("dip_scale_factor", 1.0),
                collar_layer=get_id(values.get("collar_layer_obj")),
                collar_id_field=values.get("collar_id_field"),
                collar_use_geometry=values.get("collar_use_geometry", True),
                collar_x_field=values.get("collar_x_field"),
                collar_y_field=values.get("collar_y_field"),
                collar_z_field=values.get("collar_z_field"),
                collar_depth_field=values.get("collar_depth_field"),
                survey_layer=get_id(values.get("survey_layer_obj")),
                survey_id_field=values.get("survey_id_field"),
                survey_depth_field=values.get("survey_depth_field"),
                survey_azim_field=values.get("survey_azim_field"),
                survey_incl_field=values.get("survey_incl_field"),
                interval_layer=get_id(values.get("interval_layer_obj")),
                interval_id_field=values.get("interval_id_field"),
                interval_from_field=values.get("interval_from_field"),
                interval_to_field=values.get("interval_to_field"),
                interval_lith_field=values.get("interval_lith_field"),
                max_points=preview_options.get("max_points", 1000),
                auto_lod=preview_options.get("auto_lod", True),
                canvas_width=self.dlg.preview_widget.canvas.width(),
            )
            params.validate()
        except SecInterpError as e:
            self.dlg.handle_error(e, self.tr("Configuration Error"))
            return None
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            self.dlg.handle_error(e, self.tr("Input Processing Error"))
            return None

        # 3. Connect Layer Notifications
        self.controller.connect_layer_notifications(self._collect_active_layers(params))
        return params

    def _collect_active_layers(self, params: PreviewParams) -> list[QgsMapLayer]:
        """Collect all active layer objects from parameter IDs for monitoring."""
        ids = [
            params.raster_layer,
            params.line_layer,
            params.outcrop_layer,
            params.struct_layer,
            params.collar_layer,
            params.survey_layer,
            params.interval_layer,
        ]
        layers = []
        for lid in ids:
            if not lid:
                continue
            lyr = self._resolve_layer_obj(lid)
            if lyr:
                layers.append(lyr)
        return layers

    def process_data(
        self, inputs: dict[str, Any] | None = None
    ) -> tuple[Any, Any, Any] | None:
        """Process profile data by delegating to the dialog's preview manager.

        Args:
            inputs: Pre-validated inputs (optional)

        Returns:
            Tuple of (profile_data, geol_data, struct_data) or None

        """
        # Simply delegate to the dialog's preview manager if it exists
        if hasattr(self, "dlg") and self.dlg:
            success, message = self.dlg.preview_manager.generate_preview()
            if not success:
                logger.warning(f"Data processing failed: {message}")
                return None

            # Return cached data from manager for backward compatibility if needed
            cache = self.dlg.preview_manager.cached_data
            return cache["topo"], cache["geol"], cache["struct"]

        return None

    def save_profile_line(self) -> None:
        """Save profile data by delegating to the dialog's export manager."""
        if hasattr(self, "dlg") and self.dlg:
            self.dlg.export_manager.export_data()

    def draw_preview(
        self,
        topo_data: list,
        geol_data: list | None = None,
        struct_data: list | None = None,
        drillhole_data: list | None = None,
        max_points: int = 1000,
        **kwargs,
    ) -> None:
        """Draw enhanced interactive preview using native PyQGIS renderer."""
        # 1. State Persistence
        self._store_preview_data(topo_data, geol_data, struct_data, drillhole_data)

        # 2. Parameter Calculation
        options = self.dlg.get_preview_options()
        vert_exag = self.dlg.page_dem.vertexag_spin.value()
        dip_length = self._calculate_dip_length(struct_data)

        # 3. Data Filtering
        filtered = self._get_filtered_preview_data(
            topo_data, geol_data, struct_data, drillhole_data, options
        )

        # 4. Rendering
        canvas, layers = self.preview_renderer.render(
            topo_data=filtered["topo"],
            geol_data=filtered["geol"],
            struct_data=filtered["struct"],
            vert_exag=vert_exag,
            dip_line_length=dip_length,
            max_points=max_points,
            preserve_extent=kwargs.get("preserve_extent", False),
            drillhole_data=filtered["drill"],
            interp_data=filtered["interp"],
            show_legend=options.get("show_legend", True),
        )

        # 5. UI Updates
        self.dlg.current_canvas = canvas
        self.dlg.current_layers = layers

        if hasattr(self.dlg, "legend_widget"):
            self.dlg.legend_widget.update_legend(
                self.preview_renderer, options.get("show_legend", True)
            )

    def _store_preview_data(self, topo, geol, struct, drill) -> None:
        """Store current data in dialog for re-rendering."""
        self.dlg.current_topo_data = topo
        self.dlg.current_geol_data = geol
        self.dlg.current_struct_data = struct
        self.dlg.current_drillhole_data = drill

    def _get_filtered_preview_data(self, topo, geol, struct, drill, options) -> dict:
        """Filter data based on visibility options."""
        return {
            "topo": topo if options.get("show_topo", True) else None,
            "geol": geol if options.get("show_geol", True) else None,
            "struct": struct if options.get("show_struct", True) else None,
            "drill": drill if options.get("show_drillholes", True) else None,
            "interp": (
                self.dlg.interpretations
                if options.get("show_interpretations", True)
                else None
            ),
        }

    def _calculate_dip_length(self, struct_data: list | None) -> float | None:
        """Calculate dip line length based on scale factor and raster resolution."""
        if not struct_data:
            return None

        dip_scale = self.dlg.page_struct.scale_spin.value()
        if dip_scale <= 0:
            return None

        raster_layer = self.dlg.page_dem.raster_combo.currentLayer()
        if raster_layer and raster_layer.isValid():
            res = raster_layer.rasterUnitsPerPixelX()
            if res > 0:
                return res * dip_scale
        return None
