FROM python:3.11-slim

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080
ENV PYTHONPATH=/app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expor porta
EXPOSE $PORT

# Comando para iniciar a aplicação FastAPI
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT

