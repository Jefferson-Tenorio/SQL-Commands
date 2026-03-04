import os
from IPython import get_ipython

# Obtém a instância atual do IPython
ipython = get_ipython()

# Verifica se estamos rodando dentro do Jupyter/IPython
if ipython:
    print("Inicializando ambiente de dados...")
    
    # 1. Carrega a extensão SQL automaticamente
    try:
        ipython.run_line_magic('load_ext', 'sql')
        print("Extensão SQL carregada.")
    except ImportError:
        print("Extensão ipython-sql não instalada.")

    # 2. Conecta ao banco usando a variável de ambiente
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        try:
            # Executa o comando %sql $DATABASE_URL
            ipython.run_line_magic('sql', db_url)
            # Esconde a string de conexão para não vazar senha na tela, mostrando só o sucesso
            print(f"Conectado ao banco de dados PostgreSQL com sucesso!")
        except Exception as e:
            print(f"Falha ao conectar no banco: {e}")
    else:
        print("Variável DATABASE_URL não encontrada. Conexão automática ignorada.")