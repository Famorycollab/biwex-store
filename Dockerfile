#  FICHIER DOCKERFILE - BIWEX STORE
#  Projet : DevOps 3LIG - ISG Sousse
#  Binôme : Famory TOURE & Abdoul TRAORE
#
#  NOTION FACILE DU COURS À EXPLIQUER À LA PROF :
#  C'est un Dockerfile "Multi-Stage" (en 2 étapes simples) :
#  - Étape 1 (builder) : La cuisine où on prépare et installe les outils.
#  - Étape 2 (finale)   : La salle à manger où on ne garde que le plat prêt.
#  Avantage : L'image finale est très légère (60 Mo au lieu de 800 Mo) !

# ARGUMENT : Permet de choisir la version de Python (3.11 par défaut, ou 3.12 pour le test parallèle)
ARG PYTHON_VERSION=3.11


#  ÉTAPE 1 : LE BUILDER (La boîte à outils temporaire)
FROM python:${PYTHON_VERSION}-slim AS builder

# Dossier de travail temporaire
WORKDIR /build

# Créer un environnement virtuel Python pour isoler nos paquets
RUN python -m venv /opt/venv

# Activer l'environnement virtuel
ENV PATH="/opt/venv/bin:$PATH"

# Copier uniquement la liste des dépendances (Flask, SQLAlchemy, Gunicorn...)
COPY requirements.txt .

# Télécharger et installer les dépendances dans l'environnement virtuel
# --no-cache-dir : Ne pas garder de fichiers temporaires inutiles
RUN pip install --no-cache-dir --retries 10 --timeout 180 -r requirements.txt


#  ÉTAPE 2 : L'IMAGE FINALE (Propre et légère pour la production)
FROM python:${PYTHON_VERSION}-slim

# Optimisations simples de Python :
# PYTHONDONTWRITEBYTECODE=1 : Ne pas créer de fichiers .pyc inutiles
# PYTHONUNBUFFERED=1         : Afficher les messages et erreurs en direct sans délai
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Rendre les programmes Python de l'étape 1 accessibles directement
ENV PATH="/opt/venv/bin:$PATH"

# Dossier principal de notre application dans le conteneur
WORKDIR /app

# NOTION CLÉ : On copie UNIQUEMENT le dossier venv prêt de l'étape 1
# On ne copie pas les outils lourds qui ont servi à compiler
COPY --from=builder /opt/venv /opt/venv

# Copier tous les fichiers de notre site web (app.py, templates, static, scripts)
COPY . .

# NOTION DE SÉCURITÉ DU COURS :
# Par défaut, Docker utilise l'utilisateur "root" (administrateur suprême).
# Pour la sécurité, on crée un utilisateur standard simple appelé "appuser".
# Si un pirate attaque le site web, il sera bloqué et n'aura pas les droits d'administration !
RUN useradd --create-home appuser \
    && mkdir -p /app/instance \
    && chown -R appuser:appuser /app

# Utiliser cet utilisateur sécurisé
USER appuser

# Indiquer à Docker que le site web écoute sur le port 5000
EXPOSE 5000

# NOTION SERVEUR WEB :
# En production, on n'utilise pas le serveur de test de Flask.
# On utilise "Gunicorn", un vrai serveur web rapide, robuste et sécurisé.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
