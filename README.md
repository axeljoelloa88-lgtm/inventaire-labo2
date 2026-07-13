# Laboratoire 2 — Inventaire Docker

Application de gestion d'inventaire composée de deux services conteneurisés :
une API REST (Flask) et une base de données (PostgreSQL), orchestrés via
Docker Compose.

## Architecture

```
┌─────────────┐        ┌──────────────┐
│   api       │──────▶ │  postgres    │
│  Flask 3.0  │  5432  │  PostgreSQL 15│
│  port 5000  │        │  volume pgdata│
└─────────────┘        └──────────────┘
        │
        ▼
  réseau bridge "app_net"
```

- **api** : service Flask exposant une API REST CRUD pour gérer des articles
  d'inventaire (voir [services/api/app.py](services/api/app.py)).
- **postgres** : instance PostgreSQL 15, schéma initialisé automatiquement au
  premier démarrage via [services/postgres/init/01_schema.sql](services/postgres/init/01_schema.sql).
- Les deux services communiquent sur le réseau Docker `app_net` et démarrent
  dans l'ordre grâce à `depends_on` + `healthcheck` (l'API attend que Postgres
  soit "healthy" avant de démarrer).
- Les données Postgres sont persistées dans le volume nommé `pgdata`.

## Structure du projet

```
inventaire-labo2/
├── docker-compose.yml
├── .env.example
├── services/
│   ├── api/
│   │   ├── app.py           # API Flask (routes CRUD)
│   │   ├── requirements.txt # flask, psycopg2-binary
│   │   └── Dockerfile       # python:3.11-slim
│   └── postgres/
│       ├── Dockerfile       # postgres:15
│       └── init/
│           └── 01_schema.sql # schéma + données de test
└── README.md
```

## Prérequis
- Docker et Docker Compose installés
- Copier `.env.example` en `.env` et remplir `POSTGRES_PASSWORD`

## Variables d'environnement (`.env`)

| Variable            | Défaut      | Description                                  |
|---------------------|-------------|-----------------------------------------------|
| `POSTGRES_USER`     | `admin`     | Utilisateur PostgreSQL                        |
| `POSTGRES_PASSWORD` | *(vide)*    | Mot de passe PostgreSQL — **à définir**       |
| `POSTGRES_DB`       | `inventaire`| Nom de la base de données                     |
| `POSTGRES_HOST`     | `postgres`  | Nom du service (hostname interne Docker)      |
| `POSTGRES_PORT`     | `5432`      | Port PostgreSQL                               |
| `API_PORT`          | `5000`      | Port exposé sur l'hôte pour l'API             |

## Déploiement depuis le code source

```bash
git clone https://github.com/VOTRE_USER/inventaire-labo2.git
cd inventaire-labo2
cp .env.example .env   # remplir POSTGRES_PASSWORD
docker compose up --build -d
```

Vérifier que les deux services sont démarrés et en bonne santé :

```bash
docker compose ps
```

## Images Docker Hub
- postgres : loajoel88/inventaire-postgres:1.0
- api      : loajoel88/inventaire-api:1.0

## Déploiement depuis Docker Hub (sans code source)
Voir Partie B du laboratoire

## Modèle de données

**categories**

| Colonne | Type          | Contraintes             |
|---------|---------------|--------------------------|
| id      | SERIAL        | PRIMARY KEY              |
| nom     | VARCHAR(100)  | NOT NULL, UNIQUE         |

**articles**

| Colonne        | Type          | Contraintes                                  |
|----------------|---------------|-----------------------------------------------|
| id             | SERIAL        | PRIMARY KEY                                    |
| reference      | VARCHAR(50)   | NOT NULL, UNIQUE                               |
| nom            | VARCHAR(200)  | NOT NULL                                       |
| description    | TEXT          |                                                 |
| quantite       | INTEGER       | NOT NULL, DEFAULT 0, CHECK (quantite >= 0)     |
| prix_unitaire  | NUMERIC(10,2) | NOT NULL, CHECK (prix_unitaire >= 0)           |
| categorie_id   | INTEGER       | REFERENCES categories(id) ON DELETE SET NULL   |
| actif          | BOOLEAN       | DEFAULT TRUE (soft delete)                     |
| cree_le        | TIMESTAMP     | DEFAULT NOW()                                  |

Le schéma est chargé automatiquement au premier démarrage (volume vide) et
insère 4 catégories et 5 articles de démonstration.

## API — Endpoints

Toutes les réponses sont en JSON. Base URL : `http://localhost:5000`

| Méthode | Route              | Description                                  | Codes retour     |
|---------|--------------------|-----------------------------------------------|------------------|
| GET     | `/health`          | Vérifie l'état de l'API et de la connexion DB | 200, 503         |
| GET     | `/articles`        | Liste tous les articles actifs                | 200              |
| GET     | `/articles/<id>`   | Détail d'un article                           | 200, 404         |
| POST    | `/articles`        | Crée un article                               | 201, 400, 409    |
| PATCH   | `/articles/<id>`   | Met à jour un ou plusieurs champs             | 200, 400, 404    |
| DELETE  | `/articles/<id>`   | Suppression logique (`actif = FALSE`)         | 200, 404         |
| GET     | `/stats`           | Statistiques globales (nb, stock, valeur)     | 200              |

Champs modifiables via `PATCH` : `nom`, `description`, `quantite`,
`prix_unitaire`, `actif`.

### Exemples

```bash
# Santé du service
curl http://localhost:5000/health

# Lister les articles actifs
curl http://localhost:5000/articles

# Détail d'un article
curl http://localhost:5000/articles/1

# Créer un article
curl -X POST http://localhost:5000/articles \
  -H "Content-Type: application/json" \
  -d '{"reference":"MON-001","nom":"Moniteur 27\"","quantite":5,"prix_unitaire":249.99,"categorie_id":1}'

# Mettre à jour un article
curl -X PATCH http://localhost:5000/articles/1 \
  -H "Content-Type: application/json" \
  -d '{"quantite":20}'

# Supprimer (logique) un article
curl -X DELETE http://localhost:5000/articles/1

# Statistiques (nombre d'articles, stock total, valeur totale)
curl http://localhost:5000/stats
```

## Tester

```bash
curl http://localhost:5000/health
curl http://localhost:5000/articles
curl http://localhost:5000/stats
```

## Stack technique
- **API** : Python 3.11, Flask 3.0, psycopg2-binary 2.9.9
- **Base de données** : PostgreSQL 15
- **Orchestration** : Docker Compose (réseau bridge `app_net`, volume `pgdata`)
