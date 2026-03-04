from faker import Faker 
fake = Faker("pt_BR")

import os
import psycopg2
import json

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cur = conn.cursor()

print("Conectado ao banco")

 
import random

# 2️⃣ Confirmar no banco
conn.commit()

# 3️⃣ Buscar IDs reais do banco
cur.execute("SELECT seller_id FROM sellers;")
seller_ids = [row[0] for row in cur.fetchall()]

# 4️⃣ Agora sim gerar products
products = []

for i in range(30):
    category_id = random.randint(1,4)

    if category_id == 1:
        price = round(random.uniform(500, 5000), 2)
    elif category_id == 2:
        price = round(random.uniform(50, 300), 2)
    else:
        price = round(random.uniform(80, 1000), 2)

    products.append({
        "name": fake.word().capitalize(),
        "price": price,
        "status": random.choice(["active", "Out of Stock"]),
        "category_id": category_id,
        "seller_id": random.choice(seller_ids),  # ✅ agora existe
        "specs": {
            "brand": fake.company(),
            "color": random.choice(["Red", "Blue", "Green", "Black", "White"]),
        }
    })

for product in products:
    cur.execute(
        """
        INSERT INTO products (name, price, status, category_id, seller_id, specs)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            product["name"],
            product["price"],
            product["status"],
            product["category_id"],
            product["seller_id"],
            json.dumps(product["specs"])
        )
    )

customers = []

for i in range(100):
    channel_id = random.choices([1,2,3,4,5,6], weights=[0.3, 0.2, 0.15, 0.15, 0.1, 0.1])[0]

    customers.append({
        "name": fake.name(),
        "email": fake.unique.email(),
        "city": fake.city(),
        "state": fake.estado_sigla(),
        "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "channel_id": channel_id
    })

for customer in customers:
    cur.execute(
        """
        INSERT INTO customers (name, email, city, state, birth_date, channel_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            customer["name"],
            customer["email"],
            customer["city"],
            customer["state"],
            customer["birth_date"],
            customer["channel_id"]
        )
    )


orders = []
order_id = 1

for customer_id in range(1, 101):
    num_orders = random.choices([0,1,2,3], weights=[0.4,0.3,0.2,0.1])[0]

    for _ in range(num_orders):
        order_date = fake.date_between(start_date="-6m", end_date="now")

        status = random.choices(
            ["Paid", "Shipped", "Cancelled"],
            weights=[0.6, 0.3, 0.1]
        )[0]

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "status": status,
            "order_date": order_date,
            "total_amount": 0.0   # ✅ ADICIONE ISSO
        })

        order_id += 1

for order in orders:
    cur.execute(
        """
        INSERT INTO orders (customer_id, order_status, order_date, total_amount)
        VALUES (%s, %s, %s, %s)
        """,
        (
            order["customer_id"],
            order["status"],
            order["order_date"],
            order["total_amount"]
        )
    )

order_items = []

for order in orders:
    num_items = random.randint(1, 3)

    chosen_products = random.sample(products, num_items)

    total = 0

    for product in chosen_products:
        quantity = random.randint(1, 2)
        total += product["price"] * quantity

        order_items.append({
            "order_id": order["order_id"],
            "product_id": products.index(product) + 1,
            "quantity": quantity,
            "unit_price": product["price"]
        })

    order["total_amount"] = round(total, 2)


for item in order_items:
    cur.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (%s, %s, %s, %s)
        """,
        (
            item["order_id"],
            item["product_id"],
            item["quantity"],
            item["unit_price"]
        )
    )


conn.commit()
cur.close()
conn.close()

print("Dados inseridos com sucesso!")