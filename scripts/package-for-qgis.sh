#!/bin/bash
# Script para empaquetar el plugin Sec Interp para el repositorio de QGIS
# Evita errores comunes: __pycache__, archivos .pyc, falta de LICENSE

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PLUGIN_NAME="sec_interp"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$PLUGIN_NAME"
VERSION=$(grep "^version=" "$PROJECT_DIR/metadata.txt" | cut -d'=' -f2)
OUTPUT_ZIP="$PROJECT_DIR/${PLUGIN_NAME}-${VERSION}.zip"

echo -e "${GREEN}=== Empaquetador de Plugin QGIS ===${NC}"
echo "Plugin: $PLUGIN_NAME"
echo "Versión: $VERSION"
echo "Directorio del proyecto: $PROJECT_DIR"
echo "Directorio de deploy: $DEPLOY_DIR"
echo ""

# 1. Verificar que existe metadata.txt
if [ ! -f "$PROJECT_DIR/metadata.txt" ]; then
    echo -e "${RED}ERROR: No se encuentra metadata.txt${NC}"
    exit 1
fi

# 2. Verificar que existe LICENSE
if [ ! -f "$PROJECT_DIR/LICENSE" ]; then
    echo -e "${RED}ERROR: No se encuentra archivo LICENSE${NC}"
    echo "El repositorio de QGIS requiere un archivo LICENSE"
    exit 1
fi

# 3. Desplegar el plugin
echo -e "${YELLOW}Paso 1: Desplegando plugin...${NC}"
cd "$PROJECT_DIR"
make deploy || {
    echo -e "${RED}ERROR: Fallo al desplegar el plugin${NC}"
    exit 1
}

# 4. Copiar archivos de licencia al directorio de deploy
echo -e "${YELLOW}Paso 2: Copiando archivos de licencia...${NC}"
cp "$PROJECT_DIR/LICENSE" "$DEPLOY_DIR/"
if [ -f "$PROJECT_DIR/LICENSE-GPL-2.0.txt" ]; then
    cp "$PROJECT_DIR/LICENSE-GPL-2.0.txt" "$DEPLOY_DIR/"
fi
if [ -f "$PROJECT_DIR/LICENSE-GPL-3.0.txt" ]; then
    cp "$PROJECT_DIR/LICENSE-GPL-3.0.txt" "$DEPLOY_DIR/"
fi

# 5. Limpiar archivos de caché
echo -e "${YELLOW}Paso 3: Limpiando archivos de caché...${NC}"
find "$DEPLOY_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DEPLOY_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$DEPLOY_DIR" -name "*.pyo" -delete 2>/dev/null || true

# 6. Eliminar ZIP anterior si existe
if [ -f "$OUTPUT_ZIP" ]; then
    echo -e "${YELLOW}Eliminando ZIP anterior...${NC}"
    rm -f "$OUTPUT_ZIP"
fi

# 7. Crear el ZIP
echo -e "${YELLOW}Paso 4: Creando archivo ZIP...${NC}"
cd "$(dirname "$DEPLOY_DIR")"
zip -9rq "$OUTPUT_ZIP" "$PLUGIN_NAME" \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.git*" \
    -x "*test*" \
    -x "*.bak*"

# 8. Verificaciones
echo -e "${YELLOW}Paso 5: Verificando paquete...${NC}"

# Verificar que NO contiene __pycache__
if unzip -l "$OUTPUT_ZIP" | grep -q "__pycache__"; then
    echo -e "${RED}ERROR: El ZIP contiene directorios __pycache__${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Sin directorios __pycache__${NC}"

# Verificar que contiene LICENSE
if ! unzip -l "$OUTPUT_ZIP" | grep -q "LICENSE"; then
    echo -e "${RED}ERROR: El ZIP no contiene archivo LICENSE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Archivo LICENSE incluido${NC}"

# Verificar integridad del ZIP
if ! unzip -t "$OUTPUT_ZIP" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: El ZIP está corrupto${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Integridad del ZIP verificada${NC}"

# 9. Generar checksum
CHECKSUM=$(sha256sum "$OUTPUT_ZIP" | cut -d' ' -f1)

# 10. Resumen final
echo ""
echo -e "${GREEN}=== Paquete creado exitosamente ===${NC}"
echo "Archivo: $OUTPUT_ZIP"
echo "Tamaño: $(du -h "$OUTPUT_ZIP" | cut -f1)"
echo "Archivos: $(unzip -l "$OUTPUT_ZIP" | tail -1 | awk '{print $2}')"
echo "SHA256: $CHECKSUM"
echo ""
echo -e "${GREEN}El paquete está listo para subir a:${NC}"
echo "https://plugins.qgis.org/"
echo ""
echo -e "${YELLOW}Archivos incluidos:${NC}"
unzip -l "$OUTPUT_ZIP" | grep -E "LICENSE|metadata.txt|icon.png|\.py$|\.ui$|\.qm$" | head -20
