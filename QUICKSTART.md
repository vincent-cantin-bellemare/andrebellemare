# Guide de démarrage rapide

## 🚀 Installation en 3 étapes

```bash
# 1. Cloner le projet
git clone <repo-url>
cd andrebellemare

# 2. Configuration automatique
make setup

# 3. Créer un admin
make createsuperuser
```

C'est tout ! Le site est accessible sur http://localhost:8000

## 📋 Commandes essentielles

```bash
make up              # Démarrer
make down            # Arrêter
make logs            # Voir les logs
make shell           # Shell Django
make seed            # Données de démo
make backup          # Sauvegarder la BD
```

## 🔧 Configuration

### Email Gmail

1. Activez 2FA sur Google
2. Créez un [mot de passe d'application](https://myaccount.google.com/apppasswords)
3. Ajoutez dans `.env` :
   ```
   EMAIL_HOST_USER=votre-email@gmail.com
   EMAIL_HOST_PASSWORD=votre-app-password
   ```

### Cloudflare Tunnel

1. Créez un tunnel sur [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Copiez le token
3. Ajoutez dans `.env` :
   ```
   CLOUDFLARE_TUNNEL_TOKEN=votre-token
   ```
4. Lancez : `make tunnel`

## 📁 Structure importante

```
.env                 # Variables d'environnement (à configurer)
volumes/            # Données persistantes (BD, media)
/tmp/               # Placez vos images ici pour le seed
```

## 🎨 Ajouter des toiles

### Via l'admin
1. Allez sur http://localhost:8000/alexandre/
2. Galerie → Toiles → Ajouter
3. Uploadez vos images

### Via le seed
1. Placez vos images dans `/tmp/*.jpg`
2. Lancez `make seed-fresh`

## 🆘 Problèmes courants

**Port 8000 déjà utilisé ?**
```bash
# Changez le port dans docker-compose.yml
ports:
  - "8001:8000"  # Au lieu de 8000:8000
```

**Erreur de connexion à la BD ?**
```bash
make down
make clean
make setup
```

**Images ne s'affichent pas ?**
```bash
make collectstatic
docker-compose restart web
```

## 📞 Support

- Documentation complète : `README.md`
- Commandes détaillées : `make help`









