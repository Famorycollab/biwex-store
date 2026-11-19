"""
╔══════════════════════════════════════════════════════════════╗
║               DATABASE.PY — BIWEX STORE                     ║
║                                                              ║
║  Définition des MODÈLES de données (ORM SQLAlchemy)         ║
║                                                              ║
║  Qu'est-ce qu'un ORM ?                                      ║
║    ORM = Object-Relational Mapping                          ║
║    → Au lieu d'écrire du SQL brut, on manipule des objets    ║
║      Python qui représentent les tables de la base.          ║
║    → SQLAlchemy traduit automatiquement en requêtes SQL.     ║
║                                                              ║
║  Exemple : User.query.filter_by(email='x').first()          ║
║            → SELECT * FROM user WHERE email='x' LIMIT 1     ║
║                                                              ║
║  Modèles définis ici :                                      ║
║    1. User       — Utilisateurs (clients + admins)          ║
║    2. Product    — Produits du catalogue                     ║
║    3. Order      — Commandes des clients                    ║
║    4. OrderItem  — Ligne de détail d'une commande           ║
║    5. Review     — Avis et notes sur les produits           ║
║    6. Wishlist   — Liste de souhaits par utilisateur        ║
║    7. Newsletter — Emails inscrits à la newsletter          ║
║                                                              ║
║  Auteurs : Famory TOURE & Abdoul TRAORE                     ║
║  Projet  : DevOps 3LIG — ISG Sousse 2026/2027              ║
╚══════════════════════════════════════════════════════════════╝
"""

# ── IMPORTS ──────────────────────────────────────────────────────
# SQLAlchemy  : ORM pour Python (mapping objets ↔ tables SQL)
# UserMixin   : Fournit les méthodes standard pour Flask-Login
#               (is_authenticated, is_active, is_anonymous, get_id)
# datetime    : Pour horodater les créations (created_at)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# ── INITIALISATION DE L'ORM ──────────────────────────────────────
# Cette instance sera connectée à l'application Flask dans app.py
# via db.init_app(app)
db = SQLAlchemy()


# ════════════════════════════════════════════════════════════════
#  MODÈLE : USER (Utilisateur)
#
#  Table SQL générée :
#    CREATE TABLE user (
#        id INTEGER PRIMARY KEY,
#        username VARCHAR(80) NOT NULL,
#        email VARCHAR(120) UNIQUE NOT NULL,
#        password VARCHAR(200) NOT NULL,
#        phone VARCHAR(20) DEFAULT '',
#        address VARCHAR(300) DEFAULT '',
#        city VARCHAR(100) DEFAULT '',
#        is_admin BOOLEAN DEFAULT FALSE,
#        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#    );
#
#  UserMixin : Hérite de UserMixin pour l'authentification
#    → is_authenticated : True si l'utilisateur est connecté
#    → is_active        : True si le compte est actif
#    → get_id()         : Retourne l'ID pour la session Flask
# ════════════════════════════════════════════════════════════════
class User(UserMixin, db.Model):
    # Clé primaire auto-incrémentée (1, 2, 3, ...)
    id = db.Column(db.Integer, primary_key=True)

    # Nom d'affichage (ex: "Famory TOURE")
    username = db.Column(db.String(80), nullable=False)

    # Email unique — sert d'identifiant de connexion
    # unique=True → deux utilisateurs ne peuvent pas avoir le même email
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Mot de passe HACHÉ (jamais en clair !)
    # Le hachage est fait avec werkzeug.security.generate_password_hash()
    # Exemple : "admin123" → "pbkdf2:sha256:260000$..."
    password = db.Column(db.String(200), nullable=False)

    # Informations de livraison (optionnelles)
    phone = db.Column(db.String(20), default='')
    address = db.Column(db.String(300), default='')
    city = db.Column(db.String(100), default='')

    # Rôle : True = administrateur, False = client standard
    is_admin = db.Column(db.Boolean, default=False)

    # Date de création du compte (automatique)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ── RELATIONS ORM ────────────────────────────────────────
    # backref='user' : permet d'accéder à l'utilisateur depuis
    # une commande : order.user → retourne l'objet User
    # lazy=True : charge les données à la demande (optimisation)
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)


# ════════════════════════════════════════════════════════════════
#  MODÈLE : PRODUCT (Produit du catalogue)
#
#  Chaque produit a un nom, un prix, une catégorie, etc.
#  Le champ original_price permet d'afficher un prix barré
#  en cas de promotion (Ventes Flash).
# ════════════════════════════════════════════════════════════════
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Nom du produit (ex: "iPhone 15 Pro")
    name = db.Column(db.String(100), nullable=False)

    # Prix actuel en DT (Dinar Tunisien)
    price = db.Column(db.Float, nullable=False)

    # Prix avant promotion (si > price → affiche un prix barré)
    # Si 0 ou égal au prix → pas de promotion
    original_price = db.Column(db.Float, default=0)

    # Description détaillée du produit
    description = db.Column(db.Text)

    # Catégorie (ex: "Smartphones", "Laptops", "Audio", etc.)
    category = db.Column(db.String(50))

    # Quantité en stock (si 0 → "Rupture de stock")
    stock = db.Column(db.Integer, default=0)

    # URL de l'image du produit (hébergée sur Unsplash)
    image = db.Column(db.String(300))

    # Note moyenne (calculée à partir des avis)
    rating = db.Column(db.Float, default=0)

    # Nombre total d'avis
    review_count = db.Column(db.Integer, default=0)

    # Date d'ajout au catalogue
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers les avis de ce produit
    # cascade='all, delete-orphan' : si on supprime un produit,
    # ses avis sont automatiquement supprimés (nettoyage)
    reviews = db.relationship('Review', backref='product', lazy=True,
                              cascade='all, delete-orphan')


# ════════════════════════════════════════════════════════════════
#  MODÈLE : ORDER (Commande d'un client)
#
#  Une commande est créée quand le client valide son panier.
#  Elle contient un total, un statut, et des informations
#  de livraison. Les détails sont dans OrderItem.
#
#  Statuts possibles :
#    "En attente" → "Confirmée" → "Expédiée" → "Livrée"
#    ou "Annulée"
# ════════════════════════════════════════════════════════════════
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Clé étrangère vers l'utilisateur (relation N:1)
    # → Un utilisateur peut avoir plusieurs commandes
    # → Une commande appartient à un seul utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Montant total de la commande en DT
    total = db.Column(db.Float, nullable=False)

    # Statut de suivi de la commande
    status = db.Column(db.String(50), default='En attente')

    # Adresse de livraison
    address = db.Column(db.String(300), default='')
    city = db.Column(db.String(100), default='')
    phone = db.Column(db.String(20), default='')

    # Horodatage de la commande
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Lignes de la commande (détail des produits achetés)
    items = db.relationship('OrderItem', backref='order', lazy=True,
                            cascade='all, delete-orphan')


# ════════════════════════════════════════════════════════════════
#  MODÈLE : ORDERITEM (Ligne de commande)
#
#  Chaque ligne représente UN produit dans une commande,
#  avec sa quantité et son prix au moment de l'achat.
#
#  Pourquoi stocker le prix ici ?
#    → Le prix d'un produit peut changer après la commande.
#    → On garde le prix au moment de l'achat pour l'historique.
# ════════════════════════════════════════════════════════════════
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Clé étrangère vers la commande
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    # Clé étrangère vers le produit
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # Quantité commandée (ex: 2 iPhone)
    quantity = db.Column(db.Integer, nullable=False)

    # Prix UNITAIRE au moment de l'achat (figé, ne change plus)
    price = db.Column(db.Float, nullable=False)

    # Accès direct au produit depuis la ligne de commande
    product = db.relationship('Product')


# ════════════════════════════════════════════════════════════════
#  MODÈLE : REVIEW (Avis client sur un produit)
#
#  Les avis sont liés à un utilisateur ET à un produit.
#  Un utilisateur ne peut laisser qu'un seul avis par produit
#  (vérification dans app.py).
# ════════════════════════════════════════════════════════════════
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Qui a écrit l'avis ?
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Sur quel produit ?
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # Note de 1 à 5 étoiles
    rating = db.Column(db.Integer, nullable=False)

    # Commentaire textuel (optionnel)
    comment = db.Column(db.Text, default='')

    # Date de rédaction de l'avis
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ════════════════════════════════════════════════════════════════
#  MODÈLE : WISHLIST (Liste de souhaits)
#
#  Chaque entrée lie un utilisateur à un produit qu'il "aime".
#  Toggle : cliquer une fois → ajout, cliquer encore → retrait
# ════════════════════════════════════════════════════════════════
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Quel utilisateur a ajouté ce produit en favori ?
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Quel produit est en favori ?
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # Quand a-t-il été ajouté ?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Accès direct au produit
    product = db.relationship('Product')


# ════════════════════════════════════════════════════════════════
#  MODÈLE : NEWSLETTER
#
#  Table simple qui stocke les emails des personnes inscrites
#  à la newsletter. Pas de relation avec User car les visiteurs
#  non-inscrits peuvent aussi s'inscrire.
# ════════════════════════════════════════════════════════════════
class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Email unique (un email ne peut s'inscrire qu'une fois)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Date d'inscription
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
