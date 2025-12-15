#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Note: Connexion sur root@134.122.37.249 avec clé SSH

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Configuration du droplet DigitalOcean                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Ce script doit être exécuté en tant que root${NC}"
    echo "   Utilisez: sudo bash digitalocean-setup.sh"
    exit 1
fi

# 1. Update system
echo -e "${YELLOW}📦 Mise à jour du système...${NC}"
apt update
apt upgrade -y
echo -e "${GREEN}✅ Système mis à jour${NC}"
echo ""

# 2. Install utilities
echo -e "${YELLOW}📦 Installation des utilitaires (git, htop, curl, wget, make)...${NC}"
apt install -y git htop curl wget make
echo -e "${GREEN}✅ Utilitaires installés${NC}"
echo ""

# 3. Install Docker
echo -e "${YELLOW}🐳 Installation de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    echo -e "${GREEN}✅ Docker installé${NC}"
else
    echo -e "${GREEN}✅ Docker est déjà installé${NC}"
fi

# Verify Docker installation
docker --version
echo ""

# 4. Verify Docker Compose
echo -e "${YELLOW}🐳 Vérification de Docker Compose...${NC}"
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✅ Docker Compose (plugin) est disponible${NC}"
    docker compose version
else
    echo -e "${YELLOW}⚠️  Docker Compose plugin non trouvé, installation...${NC}"
    apt install -y docker-compose-plugin
    docker compose version
fi
echo ""

# 5. Create SSH key for GitHub
echo -e "${YELLOW}🔑 Création de la clé SSH pour GitHub...${NC}"
SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github"
if [ ! -f "$SSH_KEY_PATH" ]; then
    ssh-keygen -t ed25519 -C "github-deploy" -f "$SSH_KEY_PATH" -N ""
    echo -e "${GREEN}✅ Clé SSH créée: $SSH_KEY_PATH${NC}"
else
    echo -e "${GREEN}✅ Clé SSH existe déjà: $SSH_KEY_PATH${NC}"
fi

# Display public key
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔑 CLÉ SSH PUBLIQUE - À AJOUTER À GITHUB                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
cat "$SSH_KEY_PATH.pub"
echo ""
echo -e "${YELLOW}📋 Instructions:${NC}"
echo "   1. Copiez la clé ci-dessus"
echo "   2. Allez sur GitHub → Settings → SSH and GPG keys"
echo "   3. Cliquez sur 'New SSH key'"
echo "   4. Collez la clé et sauvegardez"
echo ""

# Configure SSH config for GitHub
echo -e "${YELLOW}⚙️  Configuration de SSH pour GitHub...${NC}"
mkdir -p ~/.ssh
chmod 700 ~/.ssh

SSH_CONFIG="$HOME/.ssh/config"
if [ ! -f "$SSH_CONFIG" ] || ! grep -q "Host github.com" "$SSH_CONFIG"; then
    cat >> "$SSH_CONFIG" << EOF

# GitHub configuration
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    IdentitiesOnly yes
EOF
    chmod 600 "$SSH_CONFIG"
    echo -e "${GREEN}✅ Configuration SSH créée dans ~/.ssh/config${NC}"
else
    echo -e "${GREEN}✅ Configuration SSH existe déjà${NC}"
fi
echo ""

# 6. Configure swap (2GB for 1GB RAM)
echo -e "${YELLOW}💾 Configuration du swap (2GB)...${NC}"
if [ -z "$(swapon --show)" ] || ! swapon --show | grep -q "/swapfile"; then
    if [ ! -f /swapfile ]; then
        fallocate -l 2G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
        echo -e "${GREEN}✅ Swap de 2GB configuré${NC}"
    else
        echo -e "${YELLOW}⚠️  /swapfile existe déjà, activation...${NC}"
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        if ! grep -q "/swapfile" /etc/fstab; then
            echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
        fi
        echo -e "${GREEN}✅ Swap activé${NC}"
    fi
else
    echo -e "${GREEN}✅ Swap déjà configuré${NC}"
fi
swapon --show
echo ""

# 7. Create docker directory and cd into it
echo -e "${YELLOW}📁 Création du répertoire ~/docker/...${NC}"
mkdir -p ~/docker
cd ~/docker
echo -e "${GREEN}✅ Répertoire créé et navigation effectuée${NC}"
echo -e "${BLUE}📍 Vous êtes maintenant dans: $(pwd)${NC}"
echo ""

# Final summary
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Configuration terminée!                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📋 Prochaines étapes:${NC}"
echo ""
echo "1. Ajoutez la clé SSH à GitHub (voir ci-dessus)"
echo ""
echo "2. Clonez votre projet:"
echo -e "   ${BLUE}cd ~/docker${NC}"
echo -e "   ${BLUE}git clone git@github.com:vincent-cantin-bellemare/andrebellemare.git"
echo ""
echo "3. Commandes utiles:"
echo -e "   ${BLUE}docker --version${NC}          # Vérifier Docker"
echo -e "   ${BLUE}docker compose version${NC}    # Vérifier Docker Compose"
echo -e "   ${BLUE}htop${NC}                      # Monitoring système"
echo -e "   ${BLUE}swapon --show${NC}             # Voir le swap"
echo ""
echo -e "${GREEN}✨ Prêt à déployer!${NC}"
