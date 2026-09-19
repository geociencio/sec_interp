"""GUI adapters (Extract phase).

Adapters bridge the QGIS object world and the QGIS-agnostic core layer.
They perform the "Extract" step of the Extract-then-Compute pattern: resolving
layers, reading features, transforming CRS, and buffering — everything that
needs live QGIS objects — so the core never has to.
"""
