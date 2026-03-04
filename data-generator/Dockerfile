# Usa uma imagem Python leve
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para não gerar arquivos .pyc e logs imediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para compilar o psycopg2
# (O 'slim' vem pelado, então precisamos do gcc e libpq-dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências (vamos criar abaixo)
COPY requirements.txt .

# Instala as bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto dos scripts para dentro do container
COPY scripts/ .

# Comando padrão: executa o script principal
CMD ["python", "generate_data.py"]
