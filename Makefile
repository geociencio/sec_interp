#/***************************************************************************
# SecInterp
#
# Data extraction for geological interpretation
#							 -------------------
#		begin				: 2025-11-15
#		git sha				: $Format:%H$
#		copyright			: (C) 2025 by Juan M Bernales
#		email				: juanbernales@gmail.com
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################


# Add iso code for any locales you want to support here (space separated)
# Supported: es, fr, pt_BR, de, ru, zh_CN, id, it
LOCALES = de es fi fr hi id it ja nl pl pt_BR ru zh_CN

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease
LRELEASE = lrelease
#LRELEASE = lrelease-qt4


# translation
SOURCES = \
	__init__.py sec_interp_plugin.py \
	core/algorithms.py core/config.py core/data_cache.py core/exceptions.py core/types.py core/utils.py core/utils/drillhole.py core/validation.py core/validation/field_validator.py core/validation/layer_validator.py core/validation/path_validator.py core/validation/project_validator.py \
	core/services/geology_service.py core/services/profile_service.py core/services/structure_service.py core/services/drillhole_service.py core/services/export_service.py \
	exporters/base_exporter.py exporters/image_exporter.py exporters/svg_exporter.py exporters/pdf_exporter.py exporters/csv_exporter.py exporters/shp_exporter.py exporters/interpretation_exporters.py \
	gui/main_window.py gui/main_dialog.py gui/main_dialog_signals.py gui/main_dialog_data.py gui/main_dialog_export.py gui/main_dialog_preview.py gui/main_dialog_settings.py gui/main_dialog_status.py gui/main_dialog_tools.py gui/main_dialog_utils.py gui/main_dialog_validation.py gui/preview_renderer.py gui/sidebar.py \
	gui/ui/pages/base_page.py gui/ui/pages/dem_page.py gui/ui/pages/section_page.py gui/ui/pages/geology_page.py gui/ui/pages/structure_page.py gui/ui/pages/preview_page.py gui/ui/pages/drillhole_page.py \
	gui/tools/measure_tool.py gui/tools/interpretation_tool.py

PLUGINNAME = sec_interp

PY_FILES = $(SOURCES)

UI_FILES =
EXTRAS = metadata.txt icon.png

EXTRA_DIRS = help/html

COMPILED_RESOURCE_FILES = resources/resources.py
COMPILED_UI_FILES =

PEP8EXCLUDE=pydev,resources.py,conf.py,third_party,ui,.venv

# QGISDIR points to the location where your plugin should be installed.
# This varies by platform, relative to your HOME directory:
#	* Linux:
#	  .local/share/QGIS/QGIS3/profiles/default/python/plugins/
#	* Mac OS X:
#	  Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins
#	* Windows:
#	  AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins'

## NOTE: Make sure QGISDIR is a path *relative* to your $HOME (do NOT include
## the trailing /python/plugins part if you intend to reuse $(HOME)/$(QGISDIR)/python/plugins
## in targets below). Default is kept relative so Make targets that prefix
## $(HOME)/$(QGISDIR) work as intended.
QGISDIR=.local/share/QGIS/QGIS3/profiles/default

#################################################
# Normally you would not need to edit below here
#################################################

HELP = help/html

PLUGIN_UPLOAD = $(c)/plugin_upload.py

RESOURCE_SRC=$(shell grep '^ *<file' resources/resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

.PHONY: default
default:
	@echo While you can use make to build and deploy your plugin, pb_tool
	@echo is a much better solution.
	@echo A Python script, pb_tool provides platform independent management of
	@echo your plugins and runs anywhere.
	@echo You can install pb_tool using: pip install pb_tool
	@echo See https://g-sherman.github.io/plugin_build_tool/ for info.

compile:
	uv run qgis-manage compile --type resources --type translations
	@# Patch resources.py to use qgis.PyQt instead of PyQt5 (QGIS Policy)
	@sed -i 's/from PyQt5 import QtCore/from qgis.PyQt import QtCore/g' resources/resources.py

%.qm : %.ts
	uv run qgis-manage compile --type translations

test: compile transcompile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=..:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		uv run python3 -m unittest discover tests
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
	@echo "----------------------"

deploy: docs
	uv run qgis-manage deploy --no-compile

# The dclean target removes compiled python files from plugin directory

zip: docs compile
	uv run qgis-manage package

package: zip

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files and applying masters."
	@echo "------------------------------------------------"
	@# 1. Update .ts files from source (efficient single call)
	pylupdate5 -noobsolete $(shell find . -name "*.py" -not -path "*/.*" -not -path "./.venv/*" -not -path "./build/*") -ts $(addprefix i18n/SecInterp_, $(addsuffix .ts, $(LOCALES)))
	@# 2. Apply master translations for all languages
	@for lang in $(LOCALES); do \
		echo "Applying master data for $$lang..."; \
		python3 scripts/i18n/apply_full.py $$lang scripts/i18n/master_data/$$lang.json; \
	done
	@# 3. Update metadata with supported languages
	python3 scripts/i18n/update_metadata_languages.py

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	@uv run qgis-manage compile --type translations

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	uv run qgis-manage clean

# Docker targets
docker-build:
	DOCKER_BUILDKIT=1 docker build -t sec_interp_test .

docker-test: docker-build
	docker run --rm -v $(CURDIR):/app/sec_interp sec_interp_test
	python3 scripts/update_testing_status.py

.PHONY: apidoc docs docs-clean
apidoc:
	@chmod +x scripts/build_docs.sh
	./scripts/build_docs.sh

docs: apidoc

docs-clean:
	rm -rf docs/build
	rm -rf help/html

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@uv run pylint --reports=n . || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues (using ruff)"
	@echo "-----------"
	@uv run ruff check . || true
	@echo "-----------"

# Security scanning (QGIS Portal compatible)
.PHONY: security-scan
security-scan:
	@echo
	@echo "-------------------------------------------------------"
	@echo "Running QGIS Portal-compatible security scan..."
	@echo "Tools: Bandit, detect-secrets, Flake8"
	@echo "-------------------------------------------------------"
	@uv run python scripts/security_scan.py

# Pre-release validation (includes security)
.PHONY: pre-release
pre-release: security-scan docker-test
	@echo "✅ Pre-release validation complete"
