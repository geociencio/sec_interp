#!/bin/bash
UI_FILE="gui/ui/main_dialog_base.py"
sed -i 's/QtCore.Qt.Qt::Orientation::Horizontal/QtCore.Qt.Horizontal/g' $UI_FILE
sed -i 's/QtCore.Qt.QDialogButtonBox::StandardButton::/QtWidgets.QDialogButtonBox./g' $UI_FILE
sed -i 's/QtCore.Qt.Qt::AlignmentFlag::AlignCenter/QtCore.Qt.AlignCenter/g' $UI_FILE
sed -i 's/import resources_rc/from sec_interp.resources import resources/g' $UI_FILE
