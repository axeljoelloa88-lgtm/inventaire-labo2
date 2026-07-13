-- 01_schema.sql
-- Exécuté automatiquement par postgres:15 au premier démarrage
-- si et seulement si le volume de données est vide.

CREATE TABLE IF NOT EXISTS categories (
    id   SERIAL PRIMARY KEY,
    nom  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS articles (
    id            SERIAL PRIMARY KEY,
    reference     VARCHAR(50)    NOT NULL UNIQUE,
    nom           VARCHAR(200)   NOT NULL,
    description   TEXT,
    quantite      INTEGER        NOT NULL DEFAULT 0 CHECK (quantite >= 0),
    prix_unitaire NUMERIC(10,2)  NOT NULL CHECK (prix_unitaire >= 0),
    categorie_id  INTEGER        REFERENCES categories(id) ON DELETE SET NULL,
    actif         BOOLEAN        DEFAULT TRUE,
    cree_le       TIMESTAMP      DEFAULT NOW()
);

-- Données initiales
INSERT INTO categories (nom) VALUES
    ('Electronique'), ('Peripherique'), ('Stockage'), ('Reseau');

INSERT INTO articles (reference, nom, quantite, prix_unitaire, categorie_id)
VALUES
    ('CPU-001', 'Processeur AMD Ryzen 7',  15, 349.99, 1),
    ('RAM-001', 'Barrette RAM 16GB DDR5',  42,  89.99, 1),
    ('SSD-001', 'SSD NVMe 1TB',            28, 129.99, 3),
    ('KBD-001', 'Clavier mecanique TKL',   19,  79.99, 2),
    ('NET-001', 'Switch 24 ports Gigabit',  8, 199.99, 4);
