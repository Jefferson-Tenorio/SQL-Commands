FROM jupyter/scipy-notebook:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

USER jovyan
RUN pip install --no-cache-dir \
    ipython-sql==0.5.0 \
    prettytable==3.6.0 \
    sqlalchemy==2.0.36 \
    psycopg2==2.9.9 \
    faker==20.0.0 \
    python-dotenv==1.0.0

RUN mkdir -p /home/jovyan/.ipython/profile_default/startup/
COPY 00-startup.py /home/jovyan/.ipython/profile_default/startup/

USER root
RUN chown jovyan:users /home/jovyan/.ipython/profile_default/startup/00-startup.py

USER jovyan