import os

rule_es = "\n> [!CAUTION]\n> **REGLA CRÍTICA DE METADATOS**: El repositorio de QGIS usa `configparser`. Debes **escapar todos los signos de porcentaje (%%) como %%%%** en las secciones `changelog` y `about` de `metadata.txt` para evitar errores de interpretación.\n"
rule_en = "\n> [!CAUTION]\n> **CRITICAL METADATA RULE**: The QGIS repository uses `configparser`. You must **escape all percentage signs (%%) as %%%%** in the `changelog` and `about` sections of `metadata.txt` to avoid interpretation errors.\n"

files_to_update = [
    (
        "AI_CONTEXT.md",
        "# CONTEXTO PARA IA - sec_interp",
        "# CONTEXTO PARA IA - sec_interp\n" + rule_es,
    ),
    (
        ".ai-context/project_brain.md",
        "## Visión General",
        "## 🚨 Reglas Críticas (Globales)\n- **ESCAPADO DE METADATOS**: Escapar % como %% en metadata.txt.\n\n## Visión General",
    ),
    (
        ".ai-context/prompt_inicial.md",
        "## RESTRICCIONES:",
        "## RESTRICCIONES:\n- **METADATOS QGIS**: Escapar % como %% en metadata.txt.",
    ),
]

for filepath, target, replacement in files_to_update:
    if os.path.exists(filepath):
        with open(filepath) as f:
            content = f.read()
        if target in content and "REGLA CRÍTICA" not in content and "METADATA RULE" not in content:
            new_content = content.replace(target, replacement)
            with open(filepath, "w") as f:
                f.write(new_content)
            print(f"Updated {filepath}")
        else:
            print(f"Skipped {filepath}")
