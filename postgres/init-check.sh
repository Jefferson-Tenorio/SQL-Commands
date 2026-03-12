#!/bin/bash
set -e

echo "PGDATA=$PGDATA"

if [ -d "$PGDATA" ]; then
    if [ -f "$PGDATA/PG_VERSION" ]; then
        echo "Cluster existente encontrado, verificando integridade..."
        # pg_ctl status não funciona antes do postgres iniciar
        # a verificação real é se PG_VERSION é legível e consistente
        PG_VERSION=$(cat "$PGDATA/PG_VERSION" 2>/dev/null)
        if [ -z "$PG_VERSION" ]; then
            echo "PG_VERSION corrompido, removendo cluster..."
            rm -rf "$PGDATA"
        else
            echo "Cluster íntegro, versão: $PG_VERSION"
        fi
    else
        echo "Diretório existe sem PG_VERSION, removendo..."
        rm -rf "$PGDATA"
    fi
else
    echo "Sem cluster existente, postgres vai inicializar..."
fi

exec /usr/local/bin/docker-entrypoint.sh "$@"