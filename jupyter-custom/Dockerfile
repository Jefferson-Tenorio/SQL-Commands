FROM jupyter/scipy-notebook:latest

USER root

# Instala dependências de sistema para psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

# Instala stack Python para SQL + Pandas
RUN pip install --no-cache-dir \
    ipython-sql==0.5.0 \
    prettytable==3.6.0 \
    sqlalchemy==2.0.0 \
    psycopg2-binary==2.9.9 \
    pandas==2.1.0 \
    numpy==1.24.4 \
    matplotlib==3.8.0 \
    seaborn==0.13.0 \
    faker==20.0.0 \
    python-dotenv==1.0.0

# Configuração padrão para conexão automática
RUN

# ... (todo o resto do seu Dockerfile que já fizemos) ...

# Cria o diretório de configuração do IPython se não existir
RUN mkdir -p /home/jovyan/.ipython/profile_default/startup/

# Copia o script de automação para a pasta de startup
COPY 00-startup.py /home/jovyan/.ipython/profile_default/startup/

# Garante que as permissões estão certas
USER root
RUN chown jovyan:users /home/jovyan/.ipython/profile_default/startup/00-startup.py
USER jovyan