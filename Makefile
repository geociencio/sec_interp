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


#Add iso code for any locales you want to support here (space separated)
# default is no locales
# LOCALES = af
LOCALES = SecInterp_es

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease
LRELEASE = lrelease
#LRELEASE = lrelease-qt4


# translation
SOURCES = \
	__init__.py sec_interp_plugin.py \
	core/algorithms.py core/utils.py core/utils/drillhole.py core/validation.py core/validation/field_validator.py core/validation/layer_validator.py core/validation/path_validator.py core/validation/project_validator.py \
	core/services/geology_service.py core/services/profile_service.py core/services/structure_service.py core/services/drillhole_service.py \
	exporters/base_exporter.py exporters/image_exporter.py exporters/svg_exporter.py exporters/pdf_exporter.py exporters/csv_exporter.py exporters/shp_exporter.py \
	gui/main_window.py gui/main_dialog.py gui/main_dialog_signals.py gui/main_dialog_data.py gui/preview_renderer.py gui/sidebar.py \
	gui/ui/pages/base_page.py gui/ui/pages/dem_page.py gui/ui/pages/section_page.py gui/ui/pages/geology_page.py gui/ui/pages/structure_page.py gui/ui/pages/preview_page.py \
	gui/tools/measure_tool.py

PLUGINNAME = sec_interp

PY_FILES = $(SOURCES)

UI_FILES = 
EXTRAS = metadata.txt icon.png

EXTRA_DIRS =

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

compile: $(COMPILED_RESOURCE_FILES)

resources/resources.py : resources/resources.qrc $(RESOURCES_SRC)
	pyrcc5 -o $@ $<


%.qm : %.ts
	$(LRELEASE) $<

test: compile transcompile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		pytest -v \
		3>&1 1>&2 2>&3 3>&- || true
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
	@echo "----------------------"

deploy: compile help-integrate transcompile
	./scripts/deploy.sh


# The dclean target removes compiled python files from plugin directory
# also deletes any .git entry
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;


derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

help-integrate: apidocs-html
	@echo "Integrating documentation into help/ folder..."
	rm -rf help/html
	mkdir -p help/html
	cp -r docs/build/html/* help/html/
	rm -rf help/html/_sources
	rm -f help/index.html

zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	# Excludes user/dev specific files
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME) \
		-x "*__pycache__*" \
		-x "*.pyc" \
		-x "*.git*" \
		-x "*.idea*" \
		-x "*.vscode*" \
		-x "$(PLUGINNAME)/docs/*" \
		-x "$(PLUGINNAME)/tests/*" \
		-x "$(PLUGINNAME)/examples/*" \
		-x "$(PLUGINNAME)/.agent/*" \
		-x "$(PLUGINNAME)/.ai-context/*" \
		-x "$(PLUGINNAME)/scripts/*" \
		-x "$(PLUGINNAME)/Makefile" \
		-x "$(PLUGINNAME)/ruff.toml" \
		-x "$(PLUGINNAME)/.pylintrc" \
		-x "$(PLUGINNAME)/pytest.ini" \
		-x "$(PLUGINNAME)/requirements-dev.txt" \
		-x "$(PLUGINNAME)/.analyzerignore" \
		-x "$(PLUGINNAME)/.analyzer_state.json" \
		-x "$(PLUGINNAME)/.ai_workflow.txt" \
		-x "$(PLUGINNAME)/analysis.log" \
		-x "$(PLUGINNAME)/analysis_errors.json" \
		-x "$(PLUGINNAME)/analyze_project_optfixed.py" \
		-x "$(PLUGINNAME)/analyzer_config.json" \
		-x "$(PLUGINNAME)/generate_ai_templates.py" \
		-x "$(PLUGINNAME)/project_context.json" \
		-x "$(PLUGINNAME)/AI_CONTEXT.md" \
		-x "$(PLUGINNAME)/PROJECT_SUMMARY.md" \
		-x "$(PLUGINNAME)/README_DEV.md"

package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	@chmod +x scripts/update-strings.sh
	@scripts/update-strings.sh $(LOCALES) pylupdate5

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	@chmod +x scripts/compile-strings.sh
	@scripts/compile-strings.sh $(LRELEASE) $(LOCALES)

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@echo
	@echo "------------------------------------"
	@echo "Removing uic and rcc generated files"
	@echo "------------------------------------"
	rm $(COMPILED_UI_FILES) $(COMPILED_RESOURCE_FILES)

doc:
	@echo
	@echo "------------------------------------"
	@echo "Checking Native Hybrid documentation."
	@echo "------------------------------------"
	@if [ -f "help/html/index.html" ]; then \
		echo "Documentation found at help/html/index.html"; \
	else \
		echo "Error: help/html/index.html not found!"; \
		exit 1; \
	fi

.PHONY: apidocs apidocs-html
apidocs:
	@echo "Generating API documentation sources..."
	sphinx-apidoc -o docs/source . docs test scripts help build tests --force --separate

apidocs-html: apidocs
	@echo "Building API documentation HTML..."
	uv run sphinx-build -M html docs/source docs/build

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues (using ruff)"
	@echo "-----------"
	@uv run ruff check . || true
	@echo "-----------"
