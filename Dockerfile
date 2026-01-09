# Dockerfile optimizado para CI/CD y desarrollo headless de QGIS
FROM qgis/qgis:latest

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar dependencias de sistema mínimas (git para CI, curl para instaladores)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar uv para gestión de paquetes (mucho más rápido que pip)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# 3. Configurar el entorno de trabajo
# Nota: Montaremos el proyecto en /app/sec_interp para que 'import sec_interp' funcione con PYTHONPATH=/app
WORKDIR /app/sec_interp

# Copiar archivos de dependencias primero para aprovechar el cache de Docker
COPY pyproject.toml uv.lock ./

# Crear entorno virtual que hereda los paquetes del sistema (fundamental para QGIS/PyQt)
RUN uv venv --system-site-packages /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Instalar dependencias de Python (sin instalar el proyecto aún)
RUN uv pip install --no-build-isolation -e ".[dev]"

# 4. Copiar el código completo del proyecto
COPY . .

# 5. Configurar variables de entorno críticas
# PYTHONPATH=/app permite importar el paquete 'sec_interp' desde su directorio padre
ENV PYTHONPATH="/app:${PYTHONPATH}"
# QT_QPA_PLATFORM=offscreen permite correr tests de GUI en entornos sin servidor X
ENV QT_QPA_PLATFORM=offscreen

# 6. Comando por defecto: Ejecutar todos los tests usando unittest
CMD ["python3", "-m", "unittest", "discover", "tests"]
