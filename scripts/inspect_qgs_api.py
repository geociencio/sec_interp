from qgis.core import QgsPalLayerSettings

print("Attributes containing 'Quad':")
found = False
for x in dir(QgsPalLayerSettings):
    if "Quad" in x:
        print(f"  QgsPalLayerSettings.{x}")
        found = True

if hasattr(QgsPalLayerSettings, "Property"):
    for x in dir(QgsPalLayerSettings.Property):
        if "Quad" in x:
            print(f"  QgsPalLayerSettings.Property.{x}")
            found = True

if not found:
    print("No attributes containing 'Quad' found.")
