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
# Automatic discovery of all Python source files excluding virtual environments and hidden dirs
SOURCES = $(shell find . -maxdepth 4 -name "*.py" \
	-not -path "./.*" \
	-not -path "./tests/*" \
	-not -path "./scripts/*" \
	-not -path "./.venv/*" \
	-not -path "./build/*" \
	-not -path "./research/*" | sed 's@^\./@@')

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
QGIS_VERSION ?= 4
# Parallel Qt compilation (translations/resources). Override with `make compile COMPILE_JOBS=1`.
COMPILE_JOBS ?= 4
# Plugin code shipped in the ZIP; the QGIS portal checker runs flake8 on this scope.
FLAKE8_TARGETS = core gui exporters plugin __init__.py logger_config.py sec_interp_plugin.py
QGISDIR=.local/share/QGIS/QGIS$(QGIS_VERSION)/profiles/default
PLUGIN_DEPLOY_DIR=$(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

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
	@# 0.12.0 repeats --type correctly and writes compile output atomically, but
	@# the committed rcc output was produced by a different pyrcc build (quote
	@# style + embedded mtimes), so a fresh compile never matches byte-for-byte.
	@# Rebuild resources only when their inputs changed; keep resources.py clean
	@# otherwise (it is tracked and required by CI packaging).
	@if [ ! -f resources/resources.py ] || ! git rev-parse --git-dir >/dev/null 2>&1 || \
		! git diff --quiet HEAD -- resources/resources.qrc icon.png; then \
		uv run qgis-manage compile --type resources --type translations --jobs $(COMPILE_JOBS); \
	else \
		echo "⏭️  resources/resources.py is up to date"; \
		uv run qgis-manage compile --type translations --jobs $(COMPILE_JOBS); \
	fi

%.qm : %.ts
	uv run qgis-manage compile --type translations --jobs $(COMPILE_JOBS)

test: compile
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

deploy: docs compile
	@echo "🚀 Deploying to QGIS $(QGIS_VERSION)..."
	uv run qgis-manage deploy --no-compile --qgis-version $(QGIS_VERSION)
	@echo "✨ Deployment to QGIS $(QGIS_VERSION) complete."

# The dclean target removes compiled python files from plugin directory

zip: docs compile
	uv run qgis-manage package --repo-check
	@$(MAKE) --no-print-directory portal-check

package: zip

# QGIS portal hard requirements for the newest ZIP in dist/ (see qgis-release skill).
PORTAL_ZIP ?= $(shell ls -t dist/sec_interp.*.zip 2>/dev/null | head -1)
.PHONY: portal-check
portal-check:
	@test -n "$(PORTAL_ZIP)" || (echo "❌ No dist/sec_interp.*.zip found; run 'make zip' first."; exit 1)
	uv run --frozen qgis-manage validate --zip "$(PORTAL_ZIP)"

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

.PHONY: i18n-check
i18n-check:
	@echo
	@echo "----------------------------------------"
	@echo "Checking translation catalogs..."
	@echo "----------------------------------------"
	@uv run python3 -m unittest tests.core.test_i18n_catalogs

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@# Deliberately NOT `qgis-manage clean`: it deletes every *.cpg/*.qpj and the
	@# generated .py next to each .qrc, and this repo tracks sample-data sidecars
	@# (examples/sample_data/*.cpg) plus resources/resources.py. Keep tracked
	@# files intact and clean only caches/build output.
	@echo "🧹 Cleaning caches and build output (tracked files preserved)..."
	find . \( -path ./.venv -o -path ./.git -o -path ./node_modules \) -prune -o \
		-name "__pycache__" -type d -prune -exec rm -rf {} +
	find . \( -path ./.venv -o -path ./.git -o -path ./node_modules \) -prune -o \
		-name "*.pyc" -type f -exec rm -f {} +
	rm -rf .pytest_cache .ruff_cache help/html help/build .qgis-manage

# Docker targets
docker-build:
	DOCKER_BUILDKIT=1 docker build -t sec_interp_test .

docker-test: docker-build
	docker run --rm -v $(CURDIR):/app/sec_interp sec_interp_test
	uv run python scripts/sync_metrics.py --testing-status

# --- Context & architecture tooling (ai-context-core) ----------------------
# Refresh ground-truth metrics (qgis-plugin-analyzer) and re-render the ai-ctx
# context bundle. Run at the start of a session so AI_CONTEXT.md is never stale.
.PHONY: context context-deps context-git context-roadmap context-graph context-health
context:
	uv run qgis-analyzer analyze . --max-cc 10
	uv run ai-ctx context --path . --source external --check

context-deps:
	uv run ai-ctx deps --path . --cycles --metrics

context-git:
	uv run ai-ctx git --path .

context-roadmap:
	uv run ai-ctx roadmap --path .

context-graph:
	uv run ai-ctx graph --path . -o docs/structure/architecture.mmd

context-health:
	uv run ai-ctx health --path .

.PHONY: apidoc docs docs-check docs-version docs-i18n docs-i18n-update docs-clean
apidoc:
	@chmod +x scripts/build_docs.sh
	./scripts/build_docs.sh

docs: apidoc

docs-check:
	uv run python scripts/check_docs.py

docs-version:
	uv run python scripts/sync_docs_version.py

docs-i18n:
	uv run python scripts/docs_i18n_status.py

docs-i18n-update:
	uv run python scripts/i18n/translate_docs.py update

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
.PHONY: flake8 pep8
flake8:
	@echo
	@echo "-----------"
	@echo "Flake8 (QGIS portal scope: $(FLAKE8_TARGETS))"
	@echo "-----------"
	uv run --frozen flake8 $(FLAKE8_TARGETS) --config .flake8 --format=default --output-file=/dev/stdout
	@echo "-----------"

# QGIS convention: `make pep8` runs the portal-compatible flake8 gate.
pep8: flake8

# Security scanning (QGIS Portal compatible)
.PHONY: security-scan
security-scan:
	@echo
	@echo "-------------------------------------------------------"
	@echo "Running QGIS Portal-compatible security scan..."
	@echo "Tools: Bandit, detect-secrets, Flake8"
	@echo "-------------------------------------------------------"
	@uv run python scripts/security_scan.py

# Qt6 / QGIS 4 enum check (same tool plugins.qgis.org runs on upload)
.PHONY: qt6-check
qt6-check:
	@echo
	@echo "-------------------------------------------------------"
	@echo "Running Qt6 / QGIS 4 compatibility check (pyqgis4-checker)..."
	@echo "-------------------------------------------------------"
	docker run --rm --pull always --user $(shell id -u):$(shell id -g) \
		--workdir /workspace/ -v $(CURDIR):/workspace/ \
		ghcr.io/qgis/pyqgis4-checker:main-ubuntu \
		pyqt5_to_pyqt6.py --dry_run --logfile /workspace/pyqt6_checker.log .

# Auto-migrate enums to scoped Qt6 form (edits files in place; use with a clean tree)
.PHONY: qt6-fix
qt6-fix:
	@echo
	@echo "-------------------------------------------------------"
	@echo "Auto-migrating enums to Qt6 scoped form (pyqgis4-checker)..."
	@echo "WARNING: edits files in place. Commit first to allow revert."
	@echo "-------------------------------------------------------"
	docker run --rm --pull always --user $(shell id -u):$(shell id -g) \
		--workdir /workspace/ -v $(CURDIR):/workspace/ \
		ghcr.io/qgis/pyqgis4-checker:main-ubuntu \
		pyqt5_to_pyqt6.py --logfile /workspace/pyqt6_checker.log .

# Static type checking (strict scope: core + exporters).
# mypy needs the parent directory as the package base to resolve ``sec_interp.*``;
# run it from there while keeping the project environment.
.PHONY: mypy
mypy:
	@echo
	@echo "-------------------------------------"
	@echo "Type check (mypy): core + exporters"
	@echo "-------------------------------------"
	@cd $(CURDIR)/.. && PYTHONPATH=. uv run --project $(CURDIR) mypy \
		--config-file $(CURDIR)/pyproject.toml \
		--explicit-package-bases sec_interp/core sec_interp/exporters
	@echo "-------------------------------------"

.PHONY: analyzer
analyzer:
	@echo
	@echo "-------------------------------------"
	@echo "Static analysis (qgis-analyzer, CC gate)"
	@echo "-------------------------------------"
	@uv run qgis-analyzer analyze . --max-cc 10

# Pre-release validation (type check + analyzer + i18n + security + Qt6 + tests)
.PHONY: pre-release
.PHONY: qgis-validate
qgis-validate:
	@echo
	@echo "-----------"
	@echo "qgis-manage validate --strict --repo (metadata/structure/LICENSE)"
	@echo "-----------"
	uv run --frozen qgis-manage validate --strict --repo

pre-release: qgis-validate mypy analyzer i18n-check qt6-check flake8 security-scan docker-test
	@echo "✅ Pre-release validation complete"
