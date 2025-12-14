.PHONY: help build up down logs shell migrate seed createsuperuser backup restore clean dev tunnel tunnel-down

# Default target
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║           André Bellemare - Commandes disponibles            ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║  make setup        - Configuration initiale complète         ║"
	@echo "║  make build        - Construire les images Docker            ║"
	@echo "║  make up           - Démarrer les conteneurs                 ║"
	@echo "║  make down         - Arrêter les conteneurs                  ║"
	@echo "║  make dev          - Démarrer en mode développement          ║"
	@echo "║  make logs         - Afficher les logs                       ║"
	@echo "║  make shell        - Ouvrir un shell Django                  ║"
	@echo "║  make migrate      - Appliquer les migrations                ║"
	@echo "║  make makemigrations - Créer les migrations                  ║"
	@echo "║  make seed         - Peupler la base de données              ║"
	@echo "║  make createsuperuser - Créer un superutilisateur            ║"
	@echo "║  make backup       - Sauvegarder la base de données          ║"
	@echo "║  make restore      - Restaurer une sauvegarde                ║"
	@echo "║  make clean        - Nettoyer les conteneurs et volumes      ║"
	@echo "║  make collectstatic - Collecter les fichiers statiques       ║"
	@echo "║  make tunnel       - Démarrer avec Cloudflare Tunnel         ║"
	@echo "║  make tunnel-down  - Arrêter le tunnel                       ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"

# Initial setup
setup: env build up migrate seed
	@echo "✅ Configuration initiale terminée!"
	@echo "📍 Site: http://localhost:8000"
	@echo "📍 Admin: http://localhost:8000/alexandre/"
	@echo "👤 Créez un superutilisateur avec: make createsuperuser"

# Create .env file if it doesn't exist
env:
	@if [ ! -f .env ]; then \
		echo "📝 Création du fichier .env..."; \
		cp env.example .env; \
		echo "✅ Fichier .env créé. Pensez à modifier les valeurs!"; \
	else \
		echo "ℹ️  Le fichier .env existe déjà."; \
	fi

# Create necessary directories
dirs:
	@mkdir -p volumes/postgres/data volumes/postgres/backup volumes/django/media
	@echo "✅ Dossiers créés"

# Build Docker images
build: env dirs
	docker-compose build

# Start containers
up: env dirs
	docker-compose up -d
	@echo "✅ Conteneurs démarrés"
	@echo "📍 Site: http://localhost:8000"

# Start in development mode
dev: env dirs
	docker-compose --profile dev up web-dev

# Stop containers
down:
	docker-compose down
	@echo "✅ Conteneurs arrêtés"

# View logs
logs:
	docker-compose logs -f

# View logs for specific service
logs-web:
	docker-compose logs -f web

logs-db:
	docker-compose logs -f db

# Open Django shell
shell:
	docker-compose exec web python manage.py shell

# Open bash shell in container
bash:
	docker-compose exec web bash

# Database operations
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

# Seed database with demo data
seed:
	docker-compose exec web python manage.py seed

# Seed with clear (remove existing data first)
seed-fresh:
	docker-compose exec web python manage.py seed --clear

# Create superuser
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Backup database
backup:
	@mkdir -p volumes/postgres/backup
	@BACKUP_FILE="volumes/postgres/backup/backup_$$(date +%Y%m%d_%H%M%S).sql"; \
	docker-compose exec db pg_dump -U andrebellemare andrebellemare > $$BACKUP_FILE; \
	echo "✅ Sauvegarde créée: $$BACKUP_FILE"

# Restore database (usage: make restore FILE=backup_file.sql)
restore:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Erreur: Spécifiez le fichier avec FILE=nom_du_fichier.sql"; \
		echo "   Exemple: make restore FILE=volumes/postgres/backup/backup_20240101_120000.sql"; \
		exit 1; \
	fi
	@docker-compose exec -T db psql -U andrebellemare andrebellemare < $(FILE)
	@echo "✅ Base de données restaurée depuis $(FILE)"

# List available backups
backups:
	@echo "📦 Sauvegardes disponibles:"
	@ls -la volumes/postgres/backup/*.sql 2>/dev/null || echo "   Aucune sauvegarde trouvée"

# Clean everything
clean:
	docker-compose down -v --remove-orphans
	@echo "✅ Conteneurs et volumes supprimés"

# Clean and rebuild
rebuild: clean build up migrate
	@echo "✅ Reconstruction terminée"

# Check status
status:
	docker-compose ps

# Run tests (if any)
test:
	docker-compose exec web python manage.py test

# Check Django configuration
check:
	docker-compose exec web python manage.py check

# Show Django URLs
urls:
	docker-compose exec web python manage.py show_urls 2>/dev/null || echo "Installez django-extensions pour cette commande"

# Cloudflare Tunnel
tunnel: env dirs
	@if [ -z "$$(grep CLOUDFLARE_TUNNEL_TOKEN .env | cut -d= -f2)" ]; then \
		echo "❌ Erreur: CLOUDFLARE_TUNNEL_TOKEN n'est pas défini dans .env"; \
		echo "   1. Créez un tunnel sur https://one.dash.cloudflare.com/"; \
		echo "   2. Copiez le token et ajoutez-le dans .env"; \
		exit 1; \
	fi
	docker-compose --profile tunnel up -d
	@echo "✅ Cloudflare Tunnel démarré"
	@echo "📍 Votre site est accessible via votre domaine Cloudflare"

tunnel-down:
	docker-compose --profile tunnel down
	@echo "✅ Cloudflare Tunnel arrêté"

tunnel-logs:
	docker-compose logs -f cloudflared

