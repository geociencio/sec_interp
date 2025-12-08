from pathlib import Path
import re


files = [
    "core/types.py",
    "core/validation.py",
    "exporters/base_exporter.py",
    "exporters/csv_exporter.py",
    "exporters/image_exporter.py",
    "exporters/pdf_exporter.py",
    "exporters/profile_exporters.py",
    "exporters/shp_exporter.py",
    "exporters/svg_exporter.py",
    "gui/main_dialog.py",
    "gui/main_dialog_config.py",
    "gui/main_dialog_export.py",
    "gui/main_dialog_preview.py",
    "gui/main_dialog_validation.py",
    "gui/preview_renderer.py",
]

base_dir = Path()

for file_path in files:
    path = base_dir / file_path
    if not path.exists():
        print(f"Skipping {path} (not found)")
        continue

    content = path.read_text()

    # Remove List, Dict, Tuple from typing imports
    # Pattern looks for "from typing import ... List ..."

    lines = content.splitlines()
    new_lines = []

    for line in lines:
        if line.strip().startswith("from typing import"):
            # Remove deprecated types
            for type_name in ["List", "Dict", "Tuple"]:
                # Remove with comma after
                line = re.sub(rf"\b{type_name},\s*", "", line)
                # Remove with comma before
                line = re.sub(rf",\s*\b{type_name}\b", "", line)
                # Remove solitary
                line = re.sub(rf"\b{type_name}\b", "", line)

            # Clean up empty import
            line = line.strip()
            if line.endswith("import"):
                continue  # Skip empty import line

            # Clean up trailing comma if any (from naive regex)
            line = line.rstrip(", ")

            # Clean up double commas
            line = re.sub(r",\s*,", ",", line)

            # If line ends with "import ", remove it (empty import)
            if line.strip() == "from typing import":
                continue

        new_lines.append(line)

    path.write_text("\n".join(new_lines) + "\n")
    print(f"Processed {path}")
