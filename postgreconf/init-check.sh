#!/bin/bash
set -e

echo "PGDATA=$PGDATA"

# Se PGDATA existe mas está vazio/corrompido, remove
if [ -d "$PGDATA" ]; then
    if [ -s "$PGDATA/PG_VERSION" ]; then
        echo "Verificando integridade do cluster existente..."
        if ! pg_ctl -D "$PGDATA" status > /dev/null 2>&1; then
            echo "Cluster corrompido, removendo..."
            rm -rf "$PGDATA"
        else
            echo "Cluster existente e saudável, mantendo..."
        fi
    else
        echo "Diretório existe mas sem PG_VERSION, removendo..."
        rm -rf "$PGDATA"
    fi
fi

# Executa o entrypoint original do postgres
exec /usr/local/bin/docker-entrypoint.sh "$@"