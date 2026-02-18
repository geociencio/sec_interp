"""Sphinx documentation configuration."""

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../../"))


# -- Project information -----------------------------------------------------

project = "SecInterp"
copyright = "2026, Juan M Bernales"
author = "Juan M Bernales"

# The full version, including alpha/beta/rc tags
release = "2.9.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "myst_parser",
    "sphinxcontrib.mermaid",
]

# Mock imports for modules that are not available in the build environment
autodoc_mock_imports = ["qgis", "PyQt5", "qgis.core", "qgis.gui", "qgis.utils"]

# MyST Configuration
myst_fence_as_directive = ["mermaid"]
myst_enable_extensions = ["colon_fence"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for i18n --------------------------------------------------------

# Path to the message catalogs (.po files)
locale_dirs = ["../locales/"]
# Keep translation catalogs organized by source file
gettext_compact = False
language = "en"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Napoleon settings -------------------------------------------------------
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
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True


# -- Warnings suppression ----------------------------------------------------
# Suppress duplicate object warnings (common when re-exporting in __init__.py)
suppress_warnings = ["ref.python", "toc.not_included"]


def setup(app):
    """Register custom handlers."""

    def skip_imported_members(app, what, name, obj, skip, options):
        """Skip members that are imported from other modules to avoid duplication."""
        if what == "module":
            # Check if the member is imported (has a different __module__ than the current one)
            # This is tricky because we need to know the current module being documented.
            # A simpler way is to skip everything in __init__.py if it's already in a submodule.
            pass
        return skip

    # app.connect("autodoc-skip-member", skip_imported_members)
