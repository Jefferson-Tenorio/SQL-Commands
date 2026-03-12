-- Inserindo Categorias Base
INSERT INTO categories (name) VALUES 
('Electronics'), 
('Books'), 
('Home & Garden'), 
('Fashion'), 
('Toys'), 
('Sports');

-- Inserindo Canais de Marketing
INSERT INTO marketing_channels (name) VALUES 
('Organic Search'), 
('Paid Social (FB/IG)'), 
('Google Ads'), 
('Email Newsletter'), 
('Direct Traffic'), 
('Referral');

-- Inserindo alguns Vendedores "Parceiros" fixos
-- (O Python pode criar mais vendedores randomicos depois, se quiser)
INSERT INTO sellers (name, commission_rate) VALUES 
('Tech World Inc', 0.10),
('Best Books Ltda', 0.15),
('Fashion Nova', 0.20);

-- OBS: NÃO inserimos Customers, Orders ou Products aqui.
-- Quem vai fazer isso é o seu script Python (Faker) para gerar milhares deles.