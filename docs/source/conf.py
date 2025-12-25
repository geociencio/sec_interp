from datetime import datetime
import os
import sys


# Path setup: add parent of project root to sys.path
# This allows Sphinx to find the 'sec_interp' package correctly
sys.path.insert(0, os.path.abspath("../../.."))

# Project information
project = "SecInterp"
copyright = f"{datetime.now().year}, Juan M Bernales"
author = "Juan M Bernales"
release = "2.2.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "myst_parser",
    "sphinxcontrib.mermaid",
]

# MyST Parser configuration
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3

autodoc_mock_imports = ["qgis", "PyQt5", "qgis.core", "qgis.gui", "qgis.utils"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output options
html_theme = "alabaster"
html_static_path = ["_static"]

# Autodoc options
autodoc_member_order = "bysource"
autoclass_content = "both"
