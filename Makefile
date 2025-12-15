.PHONY: help build build-dev build-prod up up-dev up-prod down down-dev down-prod logs shell migrate seed createsuperuser backup restore clean dev prod tunnel tunnel-down

# Default target
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║           André Bellemare - Commandes disponibles            ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║  make setup        - Configuration initiale complète         ║"
	@echo "║  make build-dev    - Construire l'image Docker (dev)         ║"
	@echo "║  make build-prod   - Construire l'image Docker (prod)        ║"
	@echo "║  make dev          - Démarrer en mode développement          ║"
	@echo "║  make prod         - Démarrer en mode production             ║"
	@echo "║  make down-dev     - Arrêter les conteneurs (dev)            ║"
	@echo "║  make down-prod    - Arrêter les conteneurs (prod)           ║"
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

# Initial setup (dev)
setup: env build-dev dev migrate seed
	@echo "✅ Configuration initiale terminée (dev)!"
	@echo "📍 Base de données: prête"
	@echo "📍 Conteneur web: en attente (sleep infinity)"
	@echo "💡 Utilisez: docker-compose -f docker-compose.dev.yml exec web runserver 0.0.0.0:8000"
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
build-dev: env dirs
	docker-compose -f docker-compose.dev.yml build
	@echo "✅ Image Docker (dev) construite"

build-prod: env dirs
	docker-compose -f docker-compose.prod.yml build
	@echo "✅ Image Docker (prod) construite"

# Start in development mode
dev: env dirs
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Conteneurs de développement démarrés"
	@echo "📍 Base de données: prête"
	@echo "📍 Conteneur web: en attente (sleep infinity)"
	@echo "💡 Utilisez: docker-compose -f docker-compose.dev.yml exec web runserver 0.0.0.0:8000"

# Start in production mode
prod: env dirs
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Conteneurs de production démarrés"
	@echo "📍 Site: http://localhost:8000"

# Stop containers
down-dev:
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Conteneurs de développement arrêtés"

down-prod:
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Conteneurs de production arrêtés"

# Legacy aliases
build: build-dev
up: dev
down: down-dev

# View logs
logs:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml logs -f; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml logs -f; \
	else \
		echo "❌ Aucun conteneur en cours d'exécution"; \
	fi

# View logs for specific service
logs-web:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml logs -f web; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml logs -f web; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

logs-db:
	@if docker-compose -f docker-compose.dev.yml ps db 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml logs -f db; \
	elif docker-compose -f docker-compose.prod.yml ps db 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml logs -f db; \
	else \
		echo "❌ Aucun conteneur db en cours d'exécution"; \
	fi

# Open Django shell
shell:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web shell; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web shell; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Open bash shell in container
bash:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web bash; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web bash; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Database operations
migrate:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web migrate; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web migrate; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

makemigrations:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web makemigrations; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web makemigrations; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Seed database with demo data
seed:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web python manage.py seed; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web python manage.py seed; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Seed with clear (remove existing data first)
seed-fresh:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web python manage.py seed --clear; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web python manage.py seed --clear; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Create superuser
createsuperuser:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Collect static files
collectstatic:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Backup database
backup:
	@mkdir -p volumes/postgres/backup
	@BACKUP_FILE="volumes/postgres/backup/backup_$$(date +%Y%m%d_%H%M%S).sql"; \
	if docker-compose -f docker-compose.dev.yml ps db 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec db pg_dump -U andrebellemare andrebellemare > $$BACKUP_FILE; \
	elif docker-compose -f docker-compose.prod.yml ps db 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec db pg_dump -U andrebellemare andrebellemare > $$BACKUP_FILE; \
	else \
		echo "❌ Aucun conteneur db en cours d'exécution"; \
		exit 1; \
	fi; \
	echo "✅ Sauvegarde créée: $$BACKUP_FILE"

# Restore database (usage: make restore FILE=backup_file.sql)
restore:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Erreur: Spécifiez le fichier avec FILE=nom_du_fichier.sql"; \
		echo "   Exemple: make restore FILE=volumes/postgres/backup/backup_20240101_120000.sql"; \
		exit 1; \
	fi
	@if docker-compose -f docker-compose.dev.yml ps db 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec -T db psql -U andrebellemare andrebellemare < $(FILE); \
	elif docker-compose -f docker-compose.prod.yml ps db 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec -T db psql -U andrebellemare andrebellemare < $(FILE); \
	else \
		echo "❌ Aucun conteneur db en cours d'exécution"; \
		exit 1; \
	fi
	@echo "✅ Base de données restaurée depuis $(FILE)"

# List available backups
backups:
	@echo "📦 Sauvegardes disponibles:"
	@ls -la volumes/postgres/backup/*.sql 2>/dev/null || echo "   Aucune sauvegarde trouvée"

# Clean everything
clean:
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans 2>/dev/null || true
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
	@echo "✅ Conteneurs et volumes supprimés"

# Clean and rebuild
rebuild-dev: clean build-dev dev migrate
	@echo "✅ Reconstruction terminée (dev)"

rebuild-prod: clean build-prod prod
	@echo "✅ Reconstruction terminée (prod)"

# Check status
status:
	@echo "=== Conteneurs DEV ==="
	@docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "Aucun conteneur dev en cours"
	@echo ""
	@echo "=== Conteneurs PROD ==="
	@docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "Aucun conteneur prod en cours"

# Run tests (if any)
test:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web python manage.py test; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web python manage.py test; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Check Django configuration
check:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web python manage.py check; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web python manage.py check; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Show Django URLs
urls:
	@if docker-compose -f docker-compose.dev.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.dev.yml exec web python manage.py show_urls 2>/dev/null || echo "Installez django-extensions pour cette commande"; \
	elif docker-compose -f docker-compose.prod.yml ps web 2>/dev/null | grep -q Up; then \
		docker-compose -f docker-compose.prod.yml exec web python manage.py show_urls 2>/dev/null || echo "Installez django-extensions pour cette commande"; \
	else \
		echo "❌ Aucun conteneur web en cours d'exécution"; \
	fi

# Cloudflare Tunnel
tunnel: env dirs
	@if [ -z "$$(grep CLOUDFLARE_TUNNEL_TOKEN .env | cut -d= -f2)" ]; then \
		echo "❌ Erreur: CLOUDFLARE_TUNNEL_TOKEN n'est pas défini dans .env"; \
		echo "   1. Créez un tunnel sur https://one.dash.cloudflare.com/"; \
		echo "   2. Copiez le token et ajoutez-le dans .env"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml --profile tunnel up -d
	@echo "✅ Cloudflare Tunnel démarré"
	@echo "📍 Votre site est accessible via votre domaine Cloudflare"

tunnel-down:
	docker-compose -f docker-compose.prod.yml --profile tunnel down
	@echo "✅ Cloudflare Tunnel arrêté"

tunnel-logs:
	docker-compose -f docker-compose.prod.yml logs -f cloudflared

