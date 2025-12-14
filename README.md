# André Bellemare - Site Web

Site web de l'artiste peintre **André Bellemare**, basé à Boucherville, Québec.

> *"La vie est belle, même lorsque les temps sont durs. Alors ajoutons-y de la couleur, de la lumière et un peu de joie."*

## Aperçu

Ce site présente les œuvres d'André Bellemare. Chaque toile vendue soutient la **Maison du Père**, un organisme qui vient en aide aux personnes en situation d'itinérance à Montréal.

### Fonctionnalités

- 🎨 Galerie de toiles avec catégories et filtres
- 🔍 Recherche par titre
- 🌙 Mode sombre/clair
- 📱 Design responsive (Tailwind CSS)
- 🖼️ Lightbox plein écran pour les images
- 🔎 Zoom au survol sur les fiches produit
- 🛒 Modal d'achat avec envoi d'email
- 📧 Archivage des messages en base de données
- 📊 SEO optimisé (JSON-LD, sitemap.xml, robots.txt)
- 💬 Témoignages clients
- ❓ FAQ gérable depuis l'admin

## Stack technique

| Technologie | Version |
|-------------|---------|
| Django | 5.0 |
| PostgreSQL | 16 |
| Tailwind CSS | CDN |
| Docker | Compose |
| sorl-thumbnail | Compression images |

## Démarrage rapide

### Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose
- [Make](https://www.gnu.org/software/make/) (optionnel mais recommandé)

### Installation

#### Avec Make (recommandé)

```bash
# Cloner le projet
git clone https://github.com/username/andrebellemare.git
cd andrebellemare

# Configuration complète (crée .env, build, migrate, seed)
make setup

# Créer un superutilisateur
make createsuperuser
```

#### Sans Make

```bash
# Cloner le projet
git clone https://github.com/username/andrebellemare.git
cd andrebellemare

# Copier le fichier d'environnement
cp env.example .env

# Créer les dossiers
mkdir -p volumes/postgres/data volumes/postgres/backup volumes/django/media

# Construire et démarrer
docker-compose up -d --build

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Peupler avec des données de démo
docker-compose exec web python manage.py seed

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser
```

### Accès

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Site public |
| http://localhost:8000/alexandre/ | Administration |

## Commandes Make

```bash
make help           # Afficher l'aide
make setup          # Configuration initiale complète
make up             # Démarrer les conteneurs
make down           # Arrêter les conteneurs
make dev            # Mode développement (hot reload)
make logs           # Afficher les logs
make shell          # Shell Django
make migrate        # Appliquer les migrations
make seed           # Peupler la base de données
make createsuperuser # Créer un admin
make backup         # Sauvegarder la BD
make restore FILE=x # Restaurer une sauvegarde
make clean          # Nettoyer tout
```

## Structure du projet

```
andrebellemare/
├── .devcontainer/          # Configuration VS Code Dev Container
├── apps/
│   ├── core/               # Pages statiques, SEO, sitemap
│   ├── gallery/            # Toiles, catégories, finitions
│   └── contact/            # Messages, FAQ, témoignages
├── config/                 # Configuration Django
├── templates/
│   ├── base.html           # Layout principal
│   ├── components/         # Composants réutilisables
│   ├── emails/             # Templates d'emails
│   └── pages/              # Pages du site
├── static/                 # Fichiers statiques
├── volumes/
│   ├── postgres/data/      # Données PostgreSQL
│   ├── postgres/backup/    # Sauvegardes
│   └── django/media/       # Fichiers uploadés
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
└── env.example
```

## Configuration

### Variables d'environnement

Copiez `env.example` vers `.env` et modifiez les valeurs :

```bash
# Django
SECRET_KEY=votre-cle-secrete-unique
DEBUG=False
ALLOWED_HOSTS=andrebellemare.com,www.andrebellemare.com

# PostgreSQL
POSTGRES_DB=andrebellemare
POSTGRES_USER=andrebellemare
POSTGRES_PASSWORD=mot-de-passe-securise

# Email (Gmail)
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Site
SITE_URL=https://andrebellemare.com

# Cloudflare Tunnel (optionnel)
CLOUDFLARE_TUNNEL_TOKEN=votre-token-tunnel
```

### Configuration Gmail

Pour l'envoi d'emails via Gmail :

1. Activez l'[authentification à 2 facteurs](https://myaccount.google.com/security)
2. Créez un [mot de passe d'application](https://myaccount.google.com/apppasswords)
3. Utilisez ce mot de passe dans `EMAIL_HOST_PASSWORD`

## Développement

### Avec VS Code Dev Container

1. Installez l'extension [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Ouvrez le projet dans VS Code
3. Cliquez sur "Reopen in Container" (ou F1 → "Dev Containers: Reopen in Container")

### Mode développement local

```bash
# Démarrer avec hot reload
make dev

# Ou sans Make
docker-compose --profile dev up web-dev
```

## Seed (données de démo)

Le script de seed crée des données de démonstration :

```bash
# Peupler la base
make seed

# Réinitialiser et repeupler
make seed-fresh
```

### Utiliser vos propres images

Placez vos images dans `/tmp` avant de lancer le seed :

```bash
cp mes-images/*.jpg /tmp/
make seed-fresh
```

Le script utilisera automatiquement les images de `/tmp`. Sinon, il génère des placeholders colorés.

## Administration

L'interface d'administration (`/alexandre/`) permet de gérer :

- **Toiles** : Ajout, modification, images multiples, statut (disponible/vendu)
- **Catégories** : Abstraction, Banlieue, Capsules historiques, etc.
- **Finitions** : Époxy, Encre sur toile, Acrylique, etc.
- **FAQ** : Questions/réponses éditables
- **Témoignages** : Avis clients
- **Messages** : Archive des demandes reçues
- **Paramètres** : URL vidéo, métadonnées SEO

## Sauvegarde et restauration

```bash
# Créer une sauvegarde
make backup

# Lister les sauvegardes
make backups

# Restaurer
make restore FILE=volumes/postgres/backup/backup_20240101_120000.sql
```

## Cloudflare Tunnel

Exposez votre site sur Internet via Cloudflare Tunnel (sans ouvrir de ports).

### Configuration

1. Créez un tunnel sur [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Allez dans **Networks** → **Tunnels** → **Create a tunnel**
3. Choisissez **Cloudflared** et donnez un nom au tunnel
4. Copiez le **token** affiché
5. Ajoutez-le dans votre `.env` :

```bash
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoixxxxxx...
```

6. Configurez le **Public hostname** dans Cloudflare :
   - **Subdomain** : `www` (ou vide pour le domaine racine)
   - **Domain** : votre domaine
   - **Service** : `http://web:8000`

### Commandes

```bash
make tunnel       # Démarrer avec le tunnel
make tunnel-down  # Arrêter le tunnel
make tunnel-logs  # Voir les logs du tunnel
```

## Déploiement en production

1. Modifiez `.env` avec des valeurs sécurisées
2. Désactivez `DEBUG=False`
3. Configurez `ALLOWED_HOSTS` avec votre domaine
4. Utilisez Cloudflare Tunnel (recommandé) ou un reverse proxy (nginx, Traefik)
5. HTTPS est géré automatiquement par Cloudflare

## Contact

- **Artiste** : André Bellemare
- **Adresse** : 987 rue De Nogent, Boucherville, QC
- **Téléphone** : 438-401-1197
- **Facebook** : [@andrebellemareartiste](https://www.facebook.com/andrebellemareartiste)

## Licence

© 2025 André Bellemare. Tous droits réservés.

Les œuvres présentées sur ce site sont protégées par le droit d'auteur.
