FROM python:3.10-slim

# 1. Instalar dependencias de sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar herramientas de Python
RUN pip install uv

# 3. Configurar el entorno para que 'sec_interp' sea importable
# Montaremos el código en /app/sec_interp, así que /app debe estar en el PATH
WORKDIR /app/sec_interp
ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV UV_LINK_MODE=copy

# 4. Comando para ejecutar tests
CMD ["uv", "run", "python", "-m", "unittest", "discover", "tests"]
