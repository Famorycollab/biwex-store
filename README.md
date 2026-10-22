# 🛒 Biwex Store - Plateforme E-Commerce Moderne

Une application e-commerce moderne, rapide et responsive conçue avec **Python (Flask)**, **SQLAlchemy**, et un design épuré.

---

## ✨ Fonctionnalités Principales

- **Catalogue Produits** : Affichage dynamique par catégories, filtres de prix, recherche en temps réel et tri.
- **Gestion du Panier** : Panier d'achat interactif avec calcul automatique des totaux.
- **Système de Commandes & WhatsApp** : Validation de commande avec notification directe par WhatsApp.
- **Espace Client & Authentification** : Inscription sécurisée (hachage de mots de passe Werkzeug), connexion et profil utilisateur.
- **Liste de Souhaits (Wishlist)** : Ajout / retrait de favoris en un clic.
- **Avis & Notations** : Système d'avis et d'étoiles avec calcul de note moyenne par produit.
- **Espace Administrateur** : Dashboard complet pour gérer les produits (ajout, modification, suppression) et suivre le statut des commandes.
- **Newsletter** : Formulaire de capture d'emails clients.

---

## 🛠️ Stack Technique

- **Backend** : Python 3.x, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug
- **Base de Données** : SQLite (développement) / PostgreSQL (production recommandée)
- **Frontend** : HTML5, CSS3 personnalisé, JavaScript vanilla, FontAwesome
- **Production Server** : Gunicorn

---

## 🚀 Installation & Lancement en Local

### 1. Cloner le dépôt
```bash
git clone https://github.com/Famorycollab/PROJET-GIT.git
cd PROJET-GIT
```

### 2. Créer et activer un environnement virtuel
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
L'application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 🔑 Compte Administrateur par Défaut

- **Email** : `admin@biwex.tn`
- **Mot de passe** : `admin123`
*(Pensez à changer ces identifiants en production)*

---

## 🌐 Déploiement en Production

Pour lancer le site officiellement sur le web :
1. **Render.com** ou **Railway.app** :
   - Connectez votre dépôt GitHub.
   - Commande de démarrage : `gunicorn app:app`
   - Définissez la variable d'environnement `SECRET_KEY`.
2. **Base de données persistante** :
   - Configurez une base PostgreSQL managée (Render, Supabase ou Neon) via la variable `DATABASE_URL`.
