FROM python:3.10-slim

# 1. Instalar dependencias de sistema
RUN apt-get update && apt-get install -y \
    git \
    procps \
    wget \
    curl \
    ca-certificates \
    libgl1 \
    libqt5gui5 \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar herramientas de Python
RUN pip install uv

# 3. Configurar el entorno
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Instalar dependencias (incluyendo dev para tener qgis-analyzer)
# Usamos --no-install-project para no requerir el código fuente aún
RUN uv sync --frozen --group dev --no-install-project

# Añadir el entorno virtual al PATH
ENV PATH="/app/.venv/bin:$PATH"

# 4. Configurar el proyecto
WORKDIR /app/sec_interp
ENV PYTHONPATH="/app/sec_interp:${PYTHONPATH}"

# 5. Comando por defecto (ejemplo)
CMD ["python", "-m", "unittest", "discover", "tests"]
