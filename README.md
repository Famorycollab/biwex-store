# 🛒 Biwex Store — Plateforme E-Commerce DevOps

> **Projet DevOps — 3LIG — ISG Sousse**
> **Binôme :** Famory TOURE & Abdoul TRAORE
> **Enseignante :** Mme Zaineb SAKHRAWI

---

## 📌 Description du Projet

**Biwex Store** est une application e-commerce moderne développée avec **Python Flask**, déployée via un pipeline **CI/CD complet** utilisant **Git/GitHub**, **Jenkins** et **Docker**.

Le projet implémente **3 pipelines Jenkins** distincts couvrant l'intégralité du workflow DevOps, de la feature branch jusqu'à la release de production.

---

## 🏗️ Architecture DevOps

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW GIT & PIPELINES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  feature/xxx  ──PR──▶  dev  ──push──▶  [Pipeline 2]           │
│       │                 │                                       │
│       │                 │  tag vX.Y.Z ──▶  [Pipeline 3]        │
│       │                 │                                       │
│  [Pipeline 1]        main (protégé)                            │
│  (sur PR)                                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔱 Branches Git

| Branche | Rôle | Protection |
|---------|------|------------|
| `main` | Code stable, prêt pour la production | ✅ Protégée — merge uniquement via PR |
| `dev` | Intégration des features, branche de travail principale | ✅ Protégée — merge via PR uniquement |
| `feature/*` | Développement de nouvelles fonctionnalités | ❌ Libres |

---

## 🚦 Les 3 Pipelines Jenkins

### Pipeline 1 — Build & Smoke sur PR (`Jenkinsfile-PR`)

**Déclencheur :** Ouverture d'une Pull Request vers la branche `dev`

| Stage | Description | Résultat |
|-------|-------------|----------|
| 1 - Checkout | Récupère le code de la branche feature | ✅/❌ |
| 2 - Setup | Valide que la PR cible `dev` + vérifie les fichiers | ✅/❌ |
| 3 - Build Docker | Construit l'image `biwex-store:pr-<N>` (Python 3.11) | ✅/❌ |
| 4 - Run Docker | Démarre le conteneur de test | ✅/❌ |
| 5 - Smoke Test | Vérifie HTTP 200 sur `/` (15 tentatives) | PASSED/FAILED |
| 6 - Archive | Génère et archive logs + rapport PR | ✅/❌ |

> **Résultat :** Si PASSED → PR peut être mergée / Si FAILED → merge bloqué

---

### Pipeline 2 — Build Complet sur Push (`Jenkinsfile`)

**Déclencheur :** Push sur la branche `dev`

| Stage | Description | Résultat |
|-------|-------------|----------|
| 1 - Checkout | Récupère le code de `dev` | ✅/❌ |
| 2 - Setup | Vérifie Docker et les fichiers du projet | ✅/❌ |
| 3 - Build Parallèle | **Construit en parallèle** Python 3.11 ET 3.12 | ✅/❌ |
| 4 - Run Docker | Démarre le conteneur (image Python 3.11) | ✅/❌ |
| 5 - Smoke Test | Vérifie HTTP 200 sur `/` (15 tentatives) | PASSED/FAILED |
| 6 - Archive | Génère et archive tous les logs + rapport | ✅/❌ |
| Cleanup (post) | Supprime le conteneur et les images temporaires | Auto |

> **Particularité :** La **parallélisation** du stage 3 réduit le temps de build.

---

### Pipeline 3 — Build Versionné sur Tag (`Jenkinsfile-Tag`)

**Déclencheur :** Création d'un tag Git au format `vX.Y.Z`

```bash
git tag v1.0.0
git push origin v1.0.0
```

| Stage | Description | Résultat |
|-------|-------------|----------|
| 1 - Checkout | Récupère le code au commit du tag | ✅/❌ |
| 2 - Setup | Valide le format `vX.Y.Z` (versioning sémantique) | ✅/❌ |
| 3 - Build Parallèle | Construit Python 3.11 (`latest`) + 3.12 | ✅/❌ |
| 4 - Run Docker | Démarre le conteneur de validation release | ✅/❌ |
| 5 - Smoke Test | Vérifie HTTP 200 (20 tentatives) | PASSED/FAILED |
| 6 - Archive | Génère manifeste + rapport de release + archive | ✅/❌ |

> **Artefacts produits :**
> - `biwex-store:v1.0.0-py311` → Image de production officielle
> - `biwex-store:v1.0.0-py312` → Image de compatibilité
> - `biwex-store:latest` → Alias vers la dernière release

---

## 🐳 Dockerisation (Multi-Stage)

```dockerfile
# Stage 1 (builder) : Installation des dépendances dans un venv
FROM python:3.11-slim AS builder
# → pip install dans /opt/venv (pas dans l'image finale)

# Stage 2 (runtime) : Image finale légère
FROM python:3.11-slim
# → Copie uniquement le venv (pas pip, pas les caches)
# → Utilisateur non-root (sécurité)
# → gunicorn comme serveur WSGI de production
```

**Avantages du multi-stage :**
1. 🪶 Image finale plus légère (pas d'outils de build)
2. 🔒 Surface d'attaque réduite (sécurité)
3. 🚀 Build plus rapide grâce au cache Docker

---

## 🔬 Smoke Test

Le script `scripts/smoke_test.py` vérifie que l'application répond correctement :

- Envoie une requête **HTTP GET** vers `/`
- Attend un code de statut **200 OK**
- Timeout : **10 secondes**
- Résultat : **PASSED** (exit 0) ou **FAILED** (exit 1)

```
======================================================
  BIWEX STORE - SMOKE TEST
======================================================
  URL testée    : http://127.0.0.1:5000/
  Timeout HTTP  : 10s
  Heure de test : 2026-11-19 01:00:00
======================================================
[HTTP] Code de statut    : 200
[HTML] Contenu HTML détecté dans la réponse  ✓

  RÉSULTAT : PASSED  ✅
======================================================
```

---

## 🏷️ Versioning Sémantique (SemVer)

Le pipeline 3 utilise le **versioning sémantique** `vMAJEUR.MINEUR.PATCH` :

| Composant | Exemple | Signification |
|-----------|---------|---------------|
| MAJEUR | `v2.0.0` | Changement incompatible (breaking change) |
| MINEUR | `v1.1.0` | Nouvelle fonctionnalité compatible |
| PATCH | `v1.0.1` | Correction de bug |

---

## 🛠️ Stack Technique

### Application
- **Backend :** Python 3.11+, Flask 3.0, Flask-SQLAlchemy, Flask-Login
- **Base de données :** SQLite (dev) / PostgreSQL (prod)
- **Frontend :** HTML5, CSS3, JavaScript vanilla
- **Serveur WSGI :** Gunicorn

### DevOps
- **Versionnement :** Git / GitHub
- **CI/CD :** Jenkins (3 pipelines)
- **Containerisation :** Docker (multi-stage)
- **Tests :** Smoke Test Python

---

## 🚀 Installation Locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/Famorycollab/biwex-store.git
cd biwex-store
```

### 2. Créer et activer l'environnement virtuel

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
python app.py
```

Accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🐳 Lancement avec Docker

```bash
# Build de l'image
docker build -t biwex-store:latest .

# Lancement
docker run -d -p 5000:5000 -e SECRET_KEY=mysecret biwex-store:latest

# Smoke test manuel
docker exec <container_id> python /app/scripts/smoke_test.py http://127.0.0.1:5000/
```

---

## 🔑 Compte Administrateur

| Email | Mot de passe |
|-------|-------------|
| `admin@biwex.tn` | `admin123` |

> ⚠️ Changer ces identifiants en production !

---

## 📊 Fonctionnalités de l'Application

| Feature | Description |
|---------|-------------|
| 🛍️ Catalogue | Affichage par catégorie, filtres, recherche, tri |
| 🛒 Panier | Panier interactif avec calcul automatique |
| 📦 Commandes | Validation avec notification WhatsApp |
| 👤 Profil | Authentification sécurisée (hachage Werkzeug) |
| ❤️ Wishlist | Favoris par utilisateur |
| ⭐ Avis | Système de notation avec calcul de moyenne |
| 🔧 Admin | Dashboard complet (produits, commandes, utilisateurs) |
| 📧 Newsletter | Capture d'emails clients |

---

## 👥 Équipe

| Nom | GitHub |
|-----|--------|
| Famory TOURE | [@Famorycollab](https://github.com/Famorycollab) |
| Abdoul TRAORE | [@a21traore06-creator](https://github.com/a21traore06-creator) |

---

*Projet réalisé dans le cadre du cours Introduction au DevOps — ISG Sousse — 3LIG — 2026/2027*
