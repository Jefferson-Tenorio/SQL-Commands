import os
from IPython import get_ipython

ipython = get_ipython()
if ipython:
    print("🚀 Conectando ao banco...")
    try:
        ipython.run_line_magic('load_ext', 'sql')
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            ipython.run_line_magic('sql', db_url)
            print("✅ Conectado com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")