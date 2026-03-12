from faker import Faker
import random
import psycopg2
from psycopg2.extras import execute_batch
import json
import datetime
from decimal import Decimal
import os

# Configuração
fake = Faker("pt_BR")
# Configuração (Novo - Lendo do Docker)
NUM_SELLERS = int(os.getenv("NUM_SELLERS", 10))
NUM_PRODUCTS = int(os.getenv("NUM_PRODUCTS", 200))
NUM_CUSTOMERS = int(os.getenv("NUM_CUSTOMERS", 1000))
NUM_ORDERS = int(os.getenv("NUM_ORDERS", 3500))


def require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Variável de ambiente obrigatória não definida: {key}")
    return value

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = require_env("POSTGRES_DB")
DB_USER = require_env("POSTGRES_USER")
DB_PASS = require_env("POSTGRES_PASSWORD")

try:
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    print("🔌 Conectado ao banco de dados.")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit()

def introduce_noise(text, probability=0.1):
    """Adiciona sujeira em strings (espaços, casing errado)"""
    if random.random() > probability:
        return text
    
    scenarios = [
        lambda t: t.upper(),            # CAIXA ALTA
        lambda t: t.lower(),            # caixa baixa
        lambda t: f" {t}",              # Espaço no inicio
        lambda t: f"{t} ",              # Espaço no fim
        lambda t: t.replace("a", "@")   # Caractere estranho
    ]
    return random.choice(scenarios)(text)

# ==============================================================================
# 1. DADOS DE REFERÊNCIA (Channels, Categories, Sellers)
# ==============================================================================
print("1️⃣ Gerando Dados de Referência...")

# Canais de Marketing
channels = ['Google Ads', 'Organic', 'Instagram', 'Facebook', 'Email', 'Affiliates', 'Direct']
cur.execute("TRUNCATE TABLE marketing_channels RESTART IDENTITY CASCADE;")
execute_batch(cur, "INSERT INTO marketing_channels (name) VALUES (%s)", [(c,) for c in channels])

# Categorias
categories = ['Eletrônicos', 'Móveis', 'Roupas', 'Livros', 'Beleza', 'Brinquedos']
cur.execute("TRUNCATE TABLE categories RESTART IDENTITY CASCADE;")
execute_batch(cur, "INSERT INTO categories (name) VALUES (%s)", [(c,) for c in categories])

# Vendedores
sellers_data = []
for _ in range(NUM_SELLERS):
    # Simula erro: Comissão negativa ou maior que 100% (Bug de sistema)
    commission = round(random.uniform(0.05, 0.20), 2)
    if random.random() < 0.02: commission = 1.50 # Erro: 150% de comissão
    
    sellers_data.append((fake.company(), commission))

cur.execute("TRUNCATE TABLE sellers RESTART IDENTITY CASCADE;")
execute_batch(cur, "INSERT INTO sellers (name, commission_rate) VALUES (%s, %s)", sellers_data)

conn.commit()

# Recuperar IDs gerados para usar nas FKs
cur.execute("SELECT category_id FROM categories")
cat_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT seller_id FROM sellers")
sel_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT channel_id FROM marketing_channels")
chan_ids = [r[0] for r in cur.fetchall()]

# ==============================================================================
# 2. PRODUTOS (Com JSONB sujo e Preços estranhos)
# ==============================================================================
print("2️⃣ Gerando Produtos...")
products_data = []

for _ in range(NUM_PRODUCTS):
    price = round(random.uniform(10, 2000), 2)
    
    # 🐛 CAOS: Preço Negativo ou Zero (Erro de cadastro)
    if random.random() < 0.01: price = 0.00
    if random.random() < 0.005: price = -50.00 

    status = random.choices(['Active', 'Out of Stock', 'Discontinued'], weights=[0.8, 0.15, 0.05])[0]
    
    # JSONB Specs: Alguns produtos terão chaves faltando ou formatos diferentes
    specs = {
        "brand": fake.company(),
        "weight_kg": round(random.uniform(0.1, 5.0), 2)
    }
    
    # 🐛 CAOS: Schema Drift no JSON (chaves inesperadas)
    if random.random() < 0.1:
        specs["legacy_code"] = fake.ean() # Campo que só existe em 10% dos produtos
    if random.random() < 0.05:
        specs["weight_kg"] = "Unknown" # Tipo de dado errado (String ao invés de Float)

    products_data.append((
        fake.product_name() if hasattr(fake, 'product_name') else f"Produto {fake.word().capitalize()}",
        price,
        status,
        random.choice(cat_ids),
        random.choice(sel_ids),
        json.dumps(specs)
    ))

execute_batch(cur, """
    INSERT INTO products (name, price, status, category_id, seller_id, specs)
    VALUES (%s, %s, %s, %s, %s, %s)
""", products_data)
conn.commit()

# Recuperar IDs de produtos e preços para os pedidos
cur.execute("SELECT product_id, price FROM products")
product_lookup = {r[0]: r[1] for r in cur.fetchall()} # Dict {id: price}
prod_ids = list(product_lookup.keys())

# ==============================================================================
# 3. CLIENTES (Duplicatas e Dirty Data)
# ==============================================================================
print("3️⃣ Gerando Clientes...")
customers_data = []
emails_generated = set()

for _ in range(NUM_CUSTOMERS):
    name = introduce_noise(fake.name(), 0.15) # 15% de nomes com sujeira
    
    # Lógica para garantir e-mail único base, mas permitir duplicatas de negócio
    base_email = fake.email()
    if base_email in emails_generated:
        base_email = f"dup_{random.randint(1,99)}_{base_email}"
    emails_generated.add(base_email)
    
    email = base_email
    
    # 🐛 CAOS: E-mail com casing misturado para dificultar JOINS sem lower()
    if random.random() < 0.3:
        email = email.upper() if random.random() > 0.5 else email.title()

    city = fake.city()
    # 🐛 CAOS: Estado Nulo (Erro de preenchimento)
    state = fake.estado_sigla() if random.random() > 0.05 else None 
    
    customers_data.append((
        name, email, city, state, 
        fake.date_of_birth(minimum_age=18, maximum_age=80),
        random.choice(chan_ids)
    ))

execute_batch(cur, """
    INSERT INTO customers (name, email, city, state, birth_date, channel_id)
    VALUES (%s, %s, %s, %s, %s, %s)
""", customers_data)
conn.commit()

cur.execute("SELECT customer_id FROM customers")
cust_ids = [r[0] for r in cur.fetchall()]

# ==============================================================================
# 4. PEDIDOS E ITENS (O Coração da Transação)
# ==============================================================================
print("4️⃣ Gerando Pedidos e Itens (Isso pode demorar um pouco)...")

orders_batch = []
order_items_batch = []

# Distribuição Pareto: 20% dos clientes fazem 80% dos pedidos
# Criamos uma lista ponderada de customer_ids
heavy_users = random.sample(cust_ids, int(len(cust_ids) * 0.2))
customer_population = cust_ids + (heavy_users * 10) # Heavy users aparecem 10x mais

for _ in range(NUM_ORDERS):
    cust_id = random.choice(customer_population)
    
    # Datas
    order_date = fake.date_time_between(start_date='-1y', end_date='now')
    
    # 🐛 CAOS: Data de entrega anterior ao pedido (Viagem no tempo / Erro de log)
    if random.random() < 0.01:
        delivery_date = order_date - datetime.timedelta(days=random.randint(1, 5))
    elif random.random() < 0.1:
        delivery_date = None # Ainda não entregue ou extraviado
    else:
        delivery_date = order_date + datetime.timedelta(days=random.randint(1, 15))

    status = random.choices(
        ['Paid', 'Shipped', 'Delivered', 'Cancelled', 'Processing'], 
        weights=[0.1, 0.2, 0.5, 0.1, 0.1]
    )[0]

    # Inserir pedido inicial (sem total ainda)
    # Nota: Em um script real de alta performance, fariamos batch aqui também,
    # mas precisamos do order_id retornado para criar os itens.
    # Para performance + integridade, vamos inserir um por um aqui (ou usar RETURNING em batch complexo).
    # Vamos manter simples: insert one, get id.
    
    cur.execute("""
        INSERT INTO orders (customer_id, order_status, order_date, delivery_date, total_amount)
        VALUES (%s, %s, %s, %s, 0) RETURNING order_id
    """, (cust_id, status, order_date, delivery_date))
    
    order_id = cur.fetchone()[0]
    
    # Gerar Itens do Pedido
    num_items = random.choices([1, 2, 3, 4, 10], weights=[0.5, 0.3, 0.1, 0.05, 0.05])[0]
    
    # 🐛 CAOS: Pedido Fantasma (Sem itens, mas com status 'Shipped')
    if random.random() < 0.005: 
        num_items = 0

    order_total = 0
    selected_products = random.sample(prod_ids, min(num_items, len(prod_ids)))
    
    for prod_id in selected_products:
        base_price = float(product_lookup[prod_id])
        qty = random.randint(1, 5)
        
        # 🐛 CAOS: Variação de preço no momento da compra (Desconto ou Erro)
        # As vezes o unit_price é diferente do cadastro
        unit_price = base_price
        if random.random() < 0.1: # 10% de chance de desconto
            unit_price = round(base_price * 0.9, 2)
            
        line_total = unit_price * qty
        order_total += line_total
        
        order_items_batch.append((order_id, prod_id, qty, unit_price))

    # Atualizar o total do pedido
    # 🐛 CAOS: Total Amount diverge da soma dos itens (Erro de arredondamento ou bug)
    if random.random() < 0.01:
        order_total = order_total + random.choice([-0.01, 0.01, 10.00])

    # Update rápido (não é batch ideal, mas necessário pela lógica sequencial deste script simples)
    cur.execute("UPDATE orders SET total_amount = %s WHERE order_id = %s", (order_total, order_id))

# Batch Insert dos Itens (muito mais rápido que inserir um por um)
print(f"   Inserindo {len(order_items_batch)} itens...")
execute_batch(cur, """
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES (%s, %s, %s, %s)
""", order_items_batch)

conn.commit()
cur.close()
conn.close()

print(f"✅ Concluído! \n- {NUM_CUSTOMERS} Clientes \n- {NUM_PRODUCTS} Produtos \n- {NUM_ORDERS} Pedidos gerados.")
print("⚠️ ATENÇÃO: Os dados contêm erros intencionais para fins de troubleshooting.")