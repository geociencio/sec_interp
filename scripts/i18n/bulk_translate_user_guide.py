import os  # noqa: F401
import re
from pathlib import Path

# Core translations for the User Guide intro and main headers
CORE_TRANSLATIONS = {
    "pt_BR": {
        "SecInterp User Guide": "Guia do Usuário SecInterp",
        "1. Introduction": "1. Introdução",
        "Welcome to the SecInterp plugin! This guide will help you get started with creating geological cross-sections from your QGIS layers.": "Bem-vindo ao plugin SecInterp! Este guia o ajudará a começar a criar seções geológicas transversais a partir de suas camadas do QGIS.",
        "SecInterp allows you to:": "O SecInterp permite que você:",
        "Create a topographic profile from a Digital Elevation Model (DEM).": "Criar um perfil topográfico a partir de um Modelo Digital de Elevação (DEM).",
        "Project geological units from a polygon layer onto the profile.": "Projetar unidades geológicas de uma camada de polígonos no perfil.",
    },
    "ru": {
        "SecInterp User Guide": "Руководство пользователя SecInterp",
        "1. Introduction": "1. Введение",
        "Welcome to the SecInterp plugin! This guide will help you get started with creating geological cross-sections from your QGIS layers.": "Добро пожаловать в плагин SecInterp! Это руководство поможет вам начать создавать геологические разрезы из ваших слоев QGIS.",
        "SecInterp allows you to:": "SecInterp позволяет вам:",
        "Create a topographic profile from a Digital Elevation Model (DEM).": "Создавать топографический профиль на основе цифровой модели рельефа (ЦМР/DEM).",
        "Project geological units from a polygon layer onto the profile.": "Проецировать геологические единицы из полигонального слоя на профиль.",
    },
    "zh_CN": {
        "SecInterp User Guide": "SecInterp 用户指南",
        "1. Introduction": "1. 简介",
        "Welcome to the SecInterp plugin! This guide will help you get started with creating geological cross-sections from your QGIS layers.": "欢迎使用 SecInterp 插件！本指南将帮助您开始从 QGIS 图层创建地质剖面图。",
        "SecInterp allows you to:": "SecInterp 允许您：",
        "Create a topographic profile from a Digital Elevation Model (DEM).": "根据数字高程模型 (DEM) 创建地形剖面。",
        "Project geological units from a polygon layer onto the profile.": "将面图层中的地质单元投影到剖面上。",
    },
    "ja": {
        "SecInterp User Guide": "SecInterp ユーザーガイド",
        "1. Introduction": "1. はじめに",
        "Welcome to the SecInterp plugin! This guide will help you get started with creating geological cross-sections from your QGIS layers.": "SecInterpプラグインへようこそ！このガイドでは、QGISレイヤーから地質断面図を作成する方法を説明します。",
        "SecInterp allows you to:": "SecInterpでは以下のことが可能です：",
        "Create a topographic profile from a Digital Elevation Model (DEM).": "数値標高モデル（DEM）から地形プロファイルを作成する。",
        "Project geological units from a polygon layer onto the profile.": "ポリゴンレイヤーから地質ユニットをプロファイルに投影する。",
    },
    "pl": {
        "SecInterp User Guide": "Podręcznik użytkownika SecInterp",
        "1. Introduction": "1. Wstęp",
        "Welcome to the SecInterp plugin! This guide will help you get started with creating geological cross-sections from your QGIS layers.": "Witaj w wtyczce SecInterp! Ten przewodnik pomoże Ci zacząć tworzyć geologiczne przekroje poprzeczne z Twoich warstw QGIS.",
        "SecInterp allows you to:": "SecInterp umożliwia:",
        "Create a topographic profile from a Digital Elevation Model (DEM).": "Tworzenie profilu topograficznego z Cyfrowego Modelu Wysokości (DEM).",
        "Project geological units from a polygon layer onto the profile.": "Projektowanie jednostek geologicznych z warstwy poligonowej na profil.",
    },
}


def apply_translations():
    locales_dir = Path("docs/locales")
    for locale, trans in CORE_TRANSLATIONS.items():
        po_path = locales_dir / locale / "LC_MESSAGES" / "USER_GUIDE.po"
        if not po_path.exists():
            continue

        print(f"🌍 Applying bulk core translations to {po_path}...")
        with open(po_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_content = ""
        current_msgid = None  # noqa: F841
        translated_count = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("msgid "):
                # Extract full msgid (handle potential multiline)
                m = re.search(r'msgid "(.*)"', line)
                if m:
                    full_msgid = m.group(1)
                    # Check for simple multiline support (documentation often has it)
                    next_idx = i + 1
                    while next_idx < len(lines) and lines[next_idx].startswith('"'):
                        full_msgid += re.search(r'"(.*)"', lines[next_idx]).group(1)
                        next_idx += 1

                    new_content += line
                    i += 1
                    while i < next_idx:
                        new_content += lines[i]
                        i += 1

                    # Now handle msgstr
                    if i < len(lines) and lines[i].startswith("msgstr "):
                        if full_msgid in trans and lines[i].strip() == 'msgstr ""':
                            new_content += f'msgstr "{trans[full_msgid]}"\n'
                            translated_count += 1
                        else:
                            new_content += lines[i]
                        i += 1
                    continue
            new_content += line
            i += 1

        if translated_count > 0:
            with open(po_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ Applied {translated_count} translations for {locale}.")


if __name__ == "__main__":
    apply_translations()
