-- Garante que começamos limpo
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS sellers;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS marketing_channels;

-- 1. Categorias (Hierarquia simples)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

-- 2. Canais de Marketing (De onde o cliente veio?)
CREATE TABLE marketing_channels (
    channel_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL -- 'Google Ads', 'Organic', 'Instagram'
);

-- 3. Clientes (Tabela Mestre)
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE, -- Ótimo para testar tratamento de duplicatas no Python antes de inserir
    city VARCHAR(100),
    state CHAR(2),
    birth_date DATE,
    channel_id INT REFERENCES marketing_channels(channel_id), -- FK para análise de atribuição
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Vendedores (Para cenário de Marketplace)
CREATE TABLE sellers (
    seller_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    commission_rate DECIMAL(4,2) -- Ex: 0.10 para 10%
);

-- 5. Produtos
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    price DECIMAL(10,2),
    status VARCHAR(20), -- 'Active', 'Out of Stock', 'Discontinued'
    category_id INT REFERENCES categories(category_id),
    seller_id INT REFERENCES sellers(seller_id),
    specs JSONB -- <--- O OURO! Coluna JSON para treinar extração de dados semi-estruturados
);

-- 6. Pedidos (Tabela de Fatos - Cabeçalho)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_status VARCHAR(20), -- 'Pending', 'Paid', 'Shipped', 'Cancelled'
    order_date TIMESTAMP,
    delivery_date TIMESTAMP, -- Pode ser NULL (ótimo para IS NULL queries)
    total_amount DECIMAL(10,2)
);

-- 7. Itens do Pedido (Tabela de Fatos - Detalhe)
CREATE TABLE order_items (
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT,
    unit_price DECIMAL(10,2), -- Preço no momento da compra (pode ser diferente do cadastro)
    PRIMARY KEY (order_id, product_id)
);