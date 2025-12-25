# Guía de Publicación de Plugins QGIS

## 📋 Checklist Pre-Publicación

Antes de generar el paquete ZIP, asegúrate de que tu plugin cumple con estos requisitos:

### ✅ Requisitos Obligatorios

1. **Archivo LICENSE**
   - ⚠️ **CRÍTICO**: El repositorio de QGIS requiere un archivo `LICENSE` en la raíz del plugin
   - Incluir también las licencias completas si usas GPL: `LICENSE-GPL-2.0.txt`, `LICENSE-GPL-3.0.txt`
   - Ubicación: Raíz del directorio del plugin

2. **Metadata Completo** (`metadata.txt`)
   - Versión actualizada
   - Changelog detallado (recomendado)
   - Campos obligatorios: name, qgisMinimumVersion, description, version, author, email
   - Repository y tracker URLs

3. **Sin Archivos de Caché**
   - ⚠️ **CRÍTICO**: NO incluir directorios `__pycache__`
   - NO incluir archivos `.pyc`
   - Estos archivos causan rechazo por razones de seguridad

4. **Icono del Plugin**
   - Archivo `icon.png` en la raíz
   - Tamaño recomendado: 128x128 px

## 🔧 Proceso de Generación del Paquete ZIP

### Opción 1: Usando Makefile (Recomendado)

```bash
# 1. Limpiar archivos compilados
make clean

# 2. Compilar traducciones
make compile

# 3. Generar el ZIP
make zip
```

### Opción 2: Manual (Más Control)

```bash
# 1. Ir al directorio de plugins desplegado
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins

# 2. Limpiar archivos no deseados
find sec_interp -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find sec_interp -name "*.pyc" -delete

# 3. Copiar archivos de licencia (si no están)
cp /ruta/al/proyecto/LICENSE sec_interp/
cp /ruta/al/proyecto/LICENSE-GPL-*.txt sec_interp/

# 4. Crear el ZIP excluyendo archivos no deseados
zip -9r sec_interp-VERSION.zip sec_interp \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.git*" \
    -x "*test*" \
    -x "*__pycache__/*"
```

## ✅ Verificación del Paquete

Antes de subir, verifica que el paquete cumple con todos los requisitos:

```bash
# 1. Verificar que NO contiene __pycache__
unzip -l sec_interp-VERSION.zip | grep -i pycache
# Debe devolver: exit code 1 (sin resultados)

# 2. Verificar que contiene LICENSE
unzip -l sec_interp-VERSION.zip | grep LICENSE
# Debe mostrar: LICENSE, LICENSE-GPL-2.0.txt, LICENSE-GPL-3.0.txt

# 3. Verificar integridad del ZIP
unzip -t sec_interp-VERSION.zip
# Debe mostrar: "No errors detected"

# 4. Listar contenido completo
unzip -l sec_interp-VERSION.zip

# 5. Generar checksum (opcional, para verificación)
sha256sum sec_interp-VERSION.zip
```

## 📤 Proceso de Publicación

### 1. Preparación en Git

```bash
# Actualizar versión en metadata.txt
# Agregar changelog

# Commit de cambios
git add metadata.txt
git commit -m "Bump version to X.Y and add changelog"

# Crear tag
git tag -a vX.Y -m "Release version X.Y - [descripción breve]"

# Push a GitHub
git push origin main
git push origin vX.Y
```

### 2. Generar Paquete ZIP

```bash
# Usar uno de los métodos descritos arriba
make zip
# O el método manual
```

### 3. Subir a QGIS Plugin Repository

1. **Acceder al portal:**
   - URL: https://plugins.qgis.org/
   - Iniciar sesión con tu cuenta

2. **Subir el plugin:**
   - Ir a "My Plugins" → "Upload a plugin"
   - Seleccionar el archivo ZIP
   - El sistema validará automáticamente el paquete

3. **Verificar errores:**
   - Si hay errores, corregirlos y regenerar el ZIP
   - Errores comunes:
     - `Cannot find LICENSE` → Agregar archivo LICENSE
     - `cannot contain '__pycache__'` → Eliminar y regenerar ZIP
     - Metadata inválido → Revisar formato de metadata.txt

4. **Completar información:**
   - Revisar que toda la información del metadata se muestre correctamente
   - Agregar screenshots si es necesario
   - Publicar

## 🚫 Errores Comunes y Soluciones

### Error 1: "Cannot find LICENSE"
**Causa:** Falta el archivo LICENSE en el paquete
**Solución:**
```bash
cp LICENSE ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/sec_interp/
# Regenerar ZIP
```

### Error 2: "cannot contain '__pycache__'"
**Causa:** El ZIP incluye directorios de caché de Python
**Solución:**
```bash
# Eliminar __pycache__
find ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/sec_interp \
    -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Regenerar ZIP con exclusiones
zip -9r sec_interp.zip sec_interp -x "*.pyc" -x "*__pycache__*"
```

### Error 3: Metadata inválido
**Causa:** Formato incorrecto en metadata.txt
**Solución:**
- Verificar que todos los campos obligatorios estén presentes
- No usar comillas en los valores
- Usar formato correcto para changelog (indentación con espacios)

## 📝 Template de Changelog

```ini
changelog=
    X.Y (YYYY-MM-DD)
    * Categoría 1:
      - Cambio 1
      - Cambio 2
    * Categoría 2:
      - Cambio 3

    X.Y-1 (Versión anterior)
    - Cambio anterior 1
    - Cambio anterior 2
```

## 🔍 Checklist Final Pre-Publicación

- [ ] Versión actualizada en `metadata.txt`
- [ ] Changelog agregado y formateado correctamente
- [ ] Archivo `LICENSE` incluido en el paquete
- [ ] Archivos GPL de licencia incluidos (si aplica)
- [ ] Sin directorios `__pycache__` en el ZIP
- [ ] Sin archivos `.pyc` en el ZIP
- [ ] ZIP verificado con `unzip -t`
- [ ] Código commiteado y pusheado a GitHub
- [ ] Tag de versión creado y publicado
- [ ] Checksum SHA256 generado (opcional)

## 💡 Mejores Prácticas

1. **Automatización:** Usa el Makefile para evitar errores manuales
2. **Versionado semántico:** Usa versionado semántico (MAJOR.MINOR.PATCH)
3. **Changelog detallado:** Facilita a los usuarios entender los cambios
4. **Testing:** Prueba el plugin antes de publicar
5. **Backup:** Guarda copias de versiones anteriores
6. **Documentación:** Mantén README.md actualizado en GitHub

## 📚 Referencias

- QGIS Plugin Repository: https://plugins.qgis.org/
- Documentación oficial: https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/
- Metadata specification: https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/metadata.html
