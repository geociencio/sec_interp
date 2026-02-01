import configparser
from pathlib import Path


def test_metadata_parsing():
    metadata_path = Path("metadata.txt")
    if not metadata_path.exists():
        print("Error: metadata.txt not found")
        return

    try:
        # Intento 1: ConfigParser estándar (como probablemente lo hace ai-ctx)
        config = configparser.ConfigParser(strict=False)
        # configparser requiere una sección headers, pero metadata.txt de QGIS lo tiene en [general]
        # o a veces sin sección. Nuestro archivo tiene [general].

        config.read(metadata_path, encoding="utf-8")

        print("--- ConfigParser Sections ---")
        print(config.sections())

        if "general" in config:
            print("\n--- [general] Section Keys ---")
            for key in config["general"]:
                print(f"{key}: {config['general'][key]}")
        else:
            print("\nError: 'general' section not found via ConfigParser")

    except Exception as e:
        print(f"\nException during parsing: {e}")


if __name__ == "__main__":
    test_metadata_parsing()
