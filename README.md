# Projet Microservices E-Commerce

Projet de TP microservices développé avec FastAPI, PostgreSQL et RabbitMQ.

## Architecture

6 microservices:
- **Product Service** (port 8001) - Gestion des produits
- **Customer Service** (port 8002) - Gestion des clients
- **Inventory Service** (port 8003) - Gestion des stocks
- **Pricing Service** (port 8004) - Gestion des prix
- **Order Service** (port 8005) - Gestion des commandes
- **Gateway Service** (port 8000) - API Gateway centralisée

## Technologies

- **FastAPI** - Framework REST API
- **PostgreSQL** - Base de données (5 DB isolées)
- **RabbitMQ** - Message broker pour événements
- **SQLAlchemy** - ORM
- **Pydantic** - Validation des données
- **Docker** - Containerisation

## Gestion des dépendances avec uv

Le projet utilise **uv** avec `pyproject.toml`.

### Installer uv
```bash
pip install uv
```

### Installer les dépendances
```bash
uv venv
uv sync
```

### Ajouter une dépendance
```bash
uv add <package>
```

### Générer requirements.txt (pour Docker)
```bash
uv pip compile pyproject.toml -o requirements.txt
```

## Lancement Rapide

### 1. Démarrer tous les services
```bash
docker compose up -d
```

### 2. Vérifier le statut
```bash
docker compose ps
```

### 3. Voir les logs
```bash
docker compose logs -f
```

### 4. Tester l'API
Accéder à la documentation Swagger:
- Gateway: http://localhost:8000/docs
- Product Service: http://localhost:8001/docs
- Customer Service: http://localhost:8002/docs
- Inventory Service: http://localhost:8003/docs
- Pricing Service: http://localhost:8004/docs
- Order Service: http://localhost:8005/docs

### 5. Arrêter les services
```bash
docker compose down
```

## Page Web de Test (branche web)

Une page web simple est disponible pour tester l’API via le navigateur.

### Lancer la page web
```bash
cd web
python3 -m http.server 8080
```

### Accès
- Page web: http://localhost:8080/web/
- L’API doit être démarrée via `docker compose up -d`
## Structure du Projet

```
.
├── docker-compose.yml       # Orchestration des services
├── requirements.txt         # Dépendances Python
├── init-db.sql             # Initialisation des bases de données
└── services/
    ├── shared/             # Modules partagés (DB, RabbitMQ)
    ├── product_service/    # Service produits
    ├── customer_service/   # Service clients
    ├── inventory_service/  # Service stocks
    ├── pricing_service/    # Service prix
    ├── order_service/      # Service commandes
    └── gateway_service/    # API Gateway
```

Chaque service suit l'architecture Clean Architecture:
- `domain/` - Entités et événements métier
- `application/` - DTOs et logique applicative
- `infrastructure/` - Base de données et messaging

## Tests Rapides

### Créer un produit
```bash
curl -X POST http://localhost:8000/product \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "Dell XPS 15", "sku": "DELL-001", "base_price": 1299.99}'
```

### Lister les produits
```bash
curl http://localhost:8000/products
```

### Créer un client
```bash
curl -X POST http://localhost:8000/customer \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "type": "individual"}'
```

### Créer une commande
```bash
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "customer_pk": 1,
    "lines": [
      {"product_pk": 1, "quantity": 2, "unit_price": 999.99}
    ]
  }'
```

## Événements Asynchrones

Le système utilise RabbitMQ pour la communication asynchrone:

- **product.created** → Inventory & Pricing créent automatiquement les enregistrements
- **order.created** → Déclenche le traitement de commande
- **orderline.created** → Inventory met à jour le stock

## RabbitMQ Management

Interface web disponible sur: http://localhost:15672
- User: `guest`
- Password: `guest`

## Dépannage

### Les services ne démarrent pas
```bash
docker compose logs <service-name>
docker compose down -v  # Supprimer les volumes
docker compose up -d --build  # Reconstruire
```

### Réinitialiser complètement
```bash
docker compose down -v
docker system prune -f
docker compose up -d --build
```

### Accéder à la base de données
```bash
docker exec -it postgres psql -U postgres
\l  # Lister les bases
\c product_db  # Se connecter
\dt  # Lister les tables
```

## Développement

### Structure d'un service
```
service_name/
├── main.py                 # Point d'entrée FastAPI
├── Dockerfile             # Image Docker
├── domain/
│   ├── entities.py        # Modèles SQLAlchemy
│   └── events.py          # Événements métier
├── application/
│   ├── dtos.py           # Pydantic models
│   └── services/
│       └── crud_services.py
└── infrastructure/
    ├── db/               # Repositories, UoW
    └── messaging/        # Pub/Sub RabbitMQ
```

### Ajouter une dépendance
1. Ajouter via `uv add <package>`
2. Générer `requirements.txt`: `uv pip compile pyproject.toml -o requirements.txt`
3. Reconstruire: `docker compose up -d --build`

## Ports Utilisés

- 8000: Gateway
- 8001: Product Service
- 8002: Customer Service
- 8003: Inventory Service
- 8004: Pricing Service
- 8005: Order Service
- 5432: PostgreSQL
- 5672: RabbitMQ (AMQP)
- 15672: RabbitMQ Management UI

## Variables d'Environnement

Configurées dans `docker-compose.yml`:
- `*_DB_HOST`, `*_DB_PORT`, `*_DB_NAME`, `*_DB_USER`, `*_DB_PASSWORD`
- `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`

---

**Auteur:** Projet TP Microservices - IMT Mines Alès
**Date:** Février 2026
