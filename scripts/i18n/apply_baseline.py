import os
import re

# Dictionaries for baseline terms
# Add more languages and terms here as needed
TRANSLATIONS = {
    "id": {
        "Digital Elevation Model": "Model Elevasi Digital",
        "Raster Layer *": "Lapisan Raster *",
        "Select the raster DEM layer": "Pilih lapisan raster DEM",
        "Band": "Band",
        "Select the raster band": "Pilih band raster",
        "Resolution": "Resolusi",
        "Raster resolution (auto-calculated)": "Resolusi raster (dihitung otomatis)",
        "Profile Settings": "Pengaturan Profil",
        "Scale 1:": "Skala 1:",
        "Vert. Exag.": "Eksag. Vertikal",
        "Drillhole Data": "Data Lubang Bor",
        "Collars": "Collar",
        "Survey": "Survei",
        "Intervals": "Interval",
        "Hole ID:": "ID Lubang:",
        "Depth:": "Kedalaman:",
        "Azimuth:": "Azimut:",
        "Inclination:": "Inklinasi:",
        "From Depth:": "Dari Kedalaman:",
        "To Depth:": "Ke Kedalaman:",
        "Lithology/Attribute:": "Litologi/Atribut:",
        "Geological Outcrops": "Singkapan Geologi",
        "Outcrops Layer": "Lapisan Singkapan",
        "Interpretation Settings": "Pengaturan Interpretasi",
        "Add Field": "Tambah Kolom",
        "Remove Field": "Hapus Kolom",
        "✓ Preview generated!": "✓ Pratinjau dibuat!",
        "Clear Cache": "Bersihkan Cache",
        "&Sec Interp": "&Sec Interp",
        "Sec Interp": "Sec Interp",
    },
    "it": {
        "Digital Elevation Model": "Modello Digitale di Elevazione",
        "Raster Layer *": "Layer Raster *",
        "Select the raster DEM layer": "Seleziona il layer raster DEM",
        "Band": "Banda",
        "Select the raster band": "Seleziona la banda raster",
        "Resolution": "Risoluzione",
        "Raster resolution (auto-calculated)": "Risoluzione raster (calcolo auto)",
        "Profile Settings": "Impostazioni Profilo",
        "Scale 1:": "Scala 1:",
        "Vert. Exag.": "Esag. Vert.",
        "Drillhole Data": "Dati Sondaggio",
        "Collars": "Collari",
        "Survey": "Survey",
        "Intervals": "Intervalli",
        "Hole ID:": "ID Foro:",
        "Depth:": "Profondità:",
        "Azimuth:": "Azimut:",
        "Inclination:": "Inclinazione:",
        "From Depth:": "Dalla Profondità:",
        "To Depth:": "Alla Profondità:",
        "Lithology/Attribute:": "Litologia/Attributo:",
        "Geological Outcrops": "Affioramenti Geologici",
        "Outcrops Layer": "Layer Affioramenti",
        "Interpretation Settings": "Impostazioni Interpretazione",
        "Add Field": "Aggiungi Campo",
        "Remove Field": "Rimuovi Campo",
        "✓ Preview generated!": "✓ Anteprima generata!",
        "Clear Cache": "Pulisci Cache",
        "&Sec Interp": "&Sec Interp",
        "Sec Interp": "Sec Interp",
    },
    "zh_CN": {
        "Digital Elevation Model": "数字高程模型 (DEM)",
        "Raster Layer *": "栅格图层 *",
        "Select the raster DEM layer": "选择 DEM 栅格图层",
        "Band": "波段",
        "Select the raster band": "选择栅格波段",
        "Resolution": "分辨率",
        "Raster resolution (auto-calculated)": "栅格分辨率 (自动计算)",
        "Profile Settings": "剖面设置",
        "Scale 1:": "比例尺 1:",
        "Vert. Exag.": "垂直夸张",
        "Drillhole Data": "钻孔数据",
        "Collars": "井口数据",
        "Survey": "测井数据",
        "Intervals": "分段数据",
        "Hole ID:": "钻孔编号:",
        "Depth:": "深度:",
        "Azimuth:": "方位角:",
        "Inclination:": "倾角:",
        "From Depth:": "起始深度:",
        "To Depth:": "终止深度:",
        "Lithology/Attribute:": "岩性/属性:",
        "Geological Outcrops": "地质露头",
        "Outcrops Layer": "露头图层",
        "Interpretation Settings": "解译设置",
        "Add Field": "添加字段",
        "Remove Field": "删除字段",
        "✓ Preview generated!": "✓ 预览已生成！",
        "Clear Cache": "清除缓存",
        "&Sec Interp": "&Sec Interp",
        "Sec Interp": "Sec Interp",
    },
    "de": {
        "Digital Elevation Model": "Digitales Geländemodell (DGM)",
        "Raster Layer *": "Raster-Layer *",
        "Select the raster DEM layer": "Raster-Layer für DGM auswählen",
        "Band": "Band",
        "Select the raster band": "Rasterband auswählen",
        "Resolution": "Auflösung",
        "Raster resolution (auto-calculated)": "Raster-Auflösung (automatisch berechnet)",
        "Profile Settings": "Profil-Einstellungen",
        "Scale 1:": "Maßstab 1:",
        "Vert. Exag.": "Überhöhung",
        "Drillhole Data": "Bohrlochdaten",
        "Collars": "Bohrlochköpfe",
        "Survey": "Vermessung",
        "Intervals": "Intervalle",
        "Hole ID:": "Bohrloch-ID:",
        "Depth:": "Tiefe:",
        "Azimuth:": "Azimut:",
        "Inclination:": "Inklination:",
        "From Depth:": "Ab Tiefe:",
        "To Depth:": "Bis Tiefe:",
        "Lithology/Attribute:": "Lithologie/Attribut:",
        "Geological Outcrops": "Geologische Aufschlüsse",
        "Outcrops Layer": "Aufschluss-Layer",
        "Interpretation Settings": "Interpretations-Einstellungen",
        "Add Field": "Feld hinzufügen",
        "Remove Field": "Feld entfernen",
        "✓ Preview generated!": "✓ Vorschau generiert!",
        "Clear Cache": "Cache leeren",
        "&Sec Interp": "&Sec Interp",
        "Sec Interp": "Sec Interp",
    },
    "fr": {
        "Digital Elevation Model": "Modèle Numérique d'Élévation (MNE)",
        "Raster Layer *": "Couche Raster *",
        "Select the raster DEM layer": "Sélectionner la couche raster MNE",
        "Band": "Bande",
        "Select the raster band": "Sélectionner la bande raster",
        "Resolution": "Résolution",
        "Raster resolution (auto-calculated)": "Résolution raster (auto-calculée)",
        "Profile Settings": "Paramètres du Profil",
        "Scale 1:": "Échelle 1:",
        "Vert. Exag.": "Exag. Vert.",
        "Drillhole Data": "Données de Sondage",
        "Collars": "Colliers",
        "Survey": "Levés",
        "Intervals": "Intervalles",
        "Hole ID:": "ID Trou:",
        "Depth:": "Profondeur:",
        "Azimuth:": "Azimut:",
        "Inclination:": "Inclinaison:",
        "From Depth:": "De Profondeur:",
        "To Depth:": "À Profondeur:",
        "Lithology/Attribute:": "Lithologie/Attribut:",
        "Geological Outcrops": "Affleurements Géologiques",
        "Outcrops Layer": "Couche d'Affleurements",
        "Interpretation Settings": "Paramètres d'Interprétation",
        "Add Field": "Ajouter Champ",
        "Remove Field": "Supprimer Champ",
        "✓ Preview generated!": "✓ Aperçu généré!",
        "Clear Cache": "Vider le Cache",
        "&Sec Interp": "&Sec Interp",
        "Sec Interp": "Sec Interp",
    },
    "pt_BR": {
        "Digital Elevation Model": "Modelo Digital de Elevação (MDE)",
        "Raster Layer *": "Camada Raster *",
        "Select the raster DEM layer": "Selecionar a camada raster MDE",
        "Band": "Banda",
        "Select the raster band": "Selecionar a banda raster",
        "Resolution": "Resolução",
        "Raster resolution (auto-calculated)": "Resolução raster (auto-calculada)",
        "Profile Settings": "Configurações de Perfil",
        "Scale 1:": "Escala 1:",
        "Vert. Exag.": "Exag. Vert.",
        "Drillhole Data": "Dados de Sondagem",
        "Collars": "Colares",
        "Survey": "Vistoria",
        "Intervals": "Intervalos",
        "Hole ID:": "ID do Furo:",
        "Depth:": "Profundidade:",
        "Azimuth:": "Azimute:",
        "Inclination:": "Inclinação:",
        "From Depth:": "De Profundidade:",
        "To Depth:": "Até Profundidade:",
        "Lithology/Attribute:": "Litologia/Atributo:",
        "Geological Outcrops": "Afloramentos Geológicos",
        "Outcrops Layer": "Camada de Afloramentos",
        "Interpretation Settings": "Configurações de Interpretação",
        "Add Field": "Adicionar Campo",
        "Remove Field": "Remover Campo",
        "✓ Preview generated!": "✓ Prévia gerada!",
        "Clear Cache": "Limpar Cache",
        "&Sec Interp": "&Sec Interp",
        "Sec Interp": "Sec Interp",
    },
    "ru": {
        "Digital Elevation Model": "Цифровая модель рельефа (ЦМР)",
        "Raster Layer *": "Растровый слой *",
        "Select the raster DEM layer": "Выберите растровый слой ЦМР",
        "Band": "Канал",
        "Select the raster band": "Выберите растровый канал",
        "Resolution": "Разрешение",
        "Raster resolution (auto-calculated)": "Разрешение растра (авто)",
        "Profile Settings": "Настройки профиля",
        "Scale 1:": "Масштаб 1:",
        "Vert. Exag.": "Верт. преувеличение",
        "Drillhole Data": "Данные по скважинам",
        "Collars": "Устья скважин",
        "Survey": "Инклинометрия",
        "Intervals": "Интервалы",
        "Hole ID:": "ID скважины:",
        "Depth:": "Глубина:",
        "Azimuth:": "Азимут:",
        "Inclination:": "Угол наклона:",
        "From Depth:": "От глубины:",
        "To Depth:": "До глубины:",
        "Lithology/Attribute:": "Литология/Атрибут:",
        "Geological Outcrops": "Геологические обнажения",
        "Outcrops Layer": "Слой обнажений",
        "Interpretation Settings": "Настройки интерпретации",
        "Add Field": "Добавить поле",
        "Remove Field": "Удалить поле",
        "✓ Preview generated!": "✓ Предварительный просмотр создан!",
        "Clear Cache": "Очистить кэш",
        "&Sec Interp": "&Sec Interp",
        "Sec Interp": "Sec Interp",
    },
}


def apply_baseline(filepath, lang_code):
    """Applies baseline translations from the internal dictionary to a .ts file."""
    if lang_code not in TRANSLATIONS:
        print(f"No translations available for: {lang_code}")
        return

    mapping = TRANSLATIONS[lang_code]

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    translated_count = 0

    while i < len(lines):
        line = lines[i]
        match = re.search(r"<source>(.*)</source>", line)
        if match:
            source_text = match.group(1).strip()
            # If our mapping has the normalized text
            if source_text in mapping:
                # Find next <translation type="unfinished">
                j = i + 1
                while j < len(lines) and j < i + 5 and "<translation" not in lines[j]:
                    j += 1

                if j < len(lines) and 'type="unfinished"' in lines[j]:
                    # Replace with finished translation
                    lines[j] = (
                        lines[j]
                        .replace(' type="unfinished"', "")
                        .replace(
                            "></translation>", f">{mapping[source_text]}</translation>"
                        )
                    )
                    translated_count += 1

        new_lines.append(line)
        i += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Applied {translated_count} baseline translations to {filepath}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 apply_baseline.py <file.ts> <lang_code>")
    else:
        apply_baseline(sys.argv[1], sys.argv[2])
