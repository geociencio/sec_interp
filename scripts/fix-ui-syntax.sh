#!/bin/bash
UI_FILE="ui_sec_interp_dialog_base.py"
sed -i 's/QtCore.Qt.Qt::Orientation::Horizontal/QtCore.Qt.Horizontal/g' $UI_FILE
sed -i 's/QtCore.Qt.QDialogButtonBox::StandardButton::/QtWidgets.QDialogButtonBox./g' $UI_FILE
sed -i 's/QtCore.Qt.Qt::AlignmentFlag::AlignCenter/QtCore.Qt.AlignCenter/g' $UI_FILE
