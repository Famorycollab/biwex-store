# ============================================================
#  DOCKERFILE - BIWEX STORE
#  Application e-commerce Flask
#
#  Architecture MULTI-STAGE :
#  ┌─────────────────────────────────────────────────────┐
#  │  Stage 1 (builder) : Installation des dépendances  │
#  │    → python:3.11-slim                               │
#  │    → Crée un environnement virtuel Python isolé     │
#  │    → pip install -r requirements.txt                │
#  │                                                     │
#  │  Stage 2 (runtime) : Image finale de production     │
#  │    → python:3.11-slim (image propre et légère)      │
#  │    → Copie UNIQUEMENT le venv (pas pip, pas les     │
#  │      caches de build) → image plus petite           │
#  │    → Copie le code source de l'application          │
#  │    → Utilisateur non-root pour la sécurité          │
#  └─────────────────────────────────────────────────────┘
#
#  Avantages du multi-stage :
#    1. Image finale plus légère (pas d'outils de build)
#    2. Surface d'attaque réduite (sécurité)
#    3. Séparation claire build vs runtime
#
#  Usage :
#    docker build -t biwex-store:v1.0.0 .
#    docker build --build-arg PYTHON_VERSION=3.12 -t biwex-store:py312 .
#    docker run -d -p 5000:5000 -e SECRET_KEY=mysecret biwex-store:v1.0.0
# ============================================================

# ── ARGUMENT DE BUILD ────────────────────────────────────────────
# Permet de choisir la version Python au moment du build
# Utilisé par Jenkins pour les builds parallèles (3.11 et 3.12)
# Valeur par défaut : 3.11 (version LTS recommandée)
ARG PYTHON_VERSION=3.11

# ════════════════════════════════════════════════════════════════
#  STAGE 1 : BUILDER
#  But : installer toutes les dépendances Python dans un venv
#  Cette étape produit un environnement virtuel complet
#  mais ne sera PAS incluse dans l'image finale
# ════════════════════════════════════════════════════════════════
FROM python:${PYTHON_VERSION}-slim AS builder

# Métadonnées de l'image (bonnes pratiques)
LABEL maintainer="Famory TOURE & Abdoul TRAORE"
LABEL description="Biwex Store - Application e-commerce Flask"
LABEL stage="builder"

# Répertoire de travail pour le build
WORKDIR /build

# Création d'un environnement virtuel Python
# → Isole les dépendances du projet du système Python global
# → Portable (peut être copié dans l'image finale)
RUN python -m venv /opt/venv

# Activation du venv pour les commandes suivantes
ENV PATH="/opt/venv/bin:$PATH"

# Copie UNIQUEMENT requirements.txt (pas tout le code source)
# → Optimisation du cache Docker : si requirements.txt ne change pas,
#   Docker réutilise la couche cachée (pas de re-install)
COPY requirements.txt .

# Installation des dépendances Python
# Options :
#   --no-cache-dir : ne pas stocker le cache pip (image plus légère)
#   --retries 10   : réessayer 10 fois si erreur réseau
#   --timeout 180  : timeout de 3 minutes par paquet
RUN pip install --no-cache-dir --retries 10 --timeout 180 -r requirements.txt


# ════════════════════════════════════════════════════════════════
#  STAGE 2 : RUNTIME (image finale de production)
#  But : construire l'image légère qui sera exécutée
#  On repart d'une image Python propre (sans les outils de build)
# ════════════════════════════════════════════════════════════════
FROM python:${PYTHON_VERSION}-slim

# Métadonnées de l'image finale
LABEL maintainer="Famory TOURE & Abdoul TRAORE"
LABEL description="Biwex Store - Application e-commerce Flask (Production)"
LABEL stage="runtime"

# Variables d'environnement Python
# PYTHONDONTWRITEBYTECODE=1 : pas de fichiers .pyc (inutiles en prod)
# PYTHONUNBUFFERED=1         : logs en temps réel (stdin stdout non bufferisés)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Ajout du venv au PATH (rend python et gunicorn accessibles directement)
ENV PATH="/opt/venv/bin:$PATH"

# Répertoire de l'application dans le conteneur
WORKDIR /app

# ── Copie du venv depuis le stage builder ────────────────────────
# Multi-stage : on prend UNIQUEMENT le venv (packages installés)
# et on laisse de côté pip, setuptools, et les caches de build
COPY --from=builder /opt/venv /opt/venv

# ── Copie du code source ─────────────────────────────────────────
# .dockerignore exclut les fichiers inutiles (.git, __pycache__, etc.)
COPY . .

# ── Création d'un utilisateur non-root ──────────────────────────
# SÉCURITÉ : ne jamais exécuter une application web en root !
# Si l'application est compromise, l'attaquant n'a pas les droits root
RUN useradd --create-home appuser \
    && mkdir -p /app/instance \
    && chown -R appuser:appuser /app

# Passage à l'utilisateur non-root
USER appuser

# ── Port exposé ──────────────────────────────────────────────────
# Informe Docker que le conteneur écoute sur le port 5000
# (Gunicorn sera configuré pour écouter sur 0.0.0.0:5000)
EXPOSE 5000

# ── Commande de démarrage ────────────────────────────────────────
# Gunicorn : serveur WSGI de production (remplace le serveur de dev Flask)
# Options :
#   --bind 0.0.0.0:5000 : écoute sur toutes les interfaces réseau
#   --workers 1          : 1 worker (suffisant pour test/CI)
#                          → En prod réelle : 2*CPU + 1
#   app:app             : module "app", variable Flask "app"
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
