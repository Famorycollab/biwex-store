"""
╔══════════════════════════════════════════════════════════════╗
║                 APP.PY — BIWEX STORE                        ║
║                                                              ║
║  Point d'entrée principal de l'application e-commerce       ║
║                                                              ║
║  Framework : Flask (micro-framework web Python)             ║
║  Base de données : SQLite (dev) / PostgreSQL (prod)         ║
║  ORM : SQLAlchemy (mapping objets Python ↔ tables SQL)      ║
║  Authentification : Flask-Login (sessions + cookies)        ║
║  Sécurité : Werkzeug (hachage des mots de passe)            ║
║  Serveur prod : Gunicorn (WSGI)                             ║
║                                                              ║
║  Routes principales :                                       ║
║    /              → Page d'accueil (catalogue produits)     ║
║    /product/<id>  → Détail d'un produit                     ║
║    /cart          → Panier d'achat                          ║
║    /checkout      → Passage de commande                     ║
║    /login         → Connexion                               ║
║    /register      → Inscription                             ║
║    /admin         → Dashboard administrateur                ║
║                                                              ║
║  Auteurs : Famory TOURE & Abdoul TRAORE                     ║
║  Projet  : DevOps 3LIG — ISG Sousse 2026/2027              ║
╚══════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════
#  IMPORTS
# ═══════════════════════════════════════════════════════════════

# Flask : framework web qui gère les routes HTTP, les templates
#         et les sessions (cookies côté serveur)
from flask import (
    Flask,              # Classe principale de l'application
    render_template,    # Rendu des fichiers HTML (Jinja2)
    redirect,           # Redirection HTTP (302)
    url_for,            # Génère une URL à partir du nom de la route
    request,            # Accès aux données de la requête (GET, POST)
    session,            # Données de session (panier, etc.)
    flash,              # Messages temporaires affichés une seule fois
    jsonify             # Convertit un dict Python en réponse JSON
)

# SQLAlchemy : ORM pour manipuler la base de données via des objets
from flask_sqlalchemy import SQLAlchemy

# Flask-Login : gestion de l'authentification (connexion/déconnexion)
from flask_login import (
    LoginManager,       # Gestionnaire de sessions d'authentification
    login_user,         # Connecte un utilisateur (crée une session)
    logout_user,        # Déconnecte un utilisateur (détruit la session)
    login_required,     # Décorateur : route accessible uniquement si connecté
    current_user        # Accès à l'utilisateur actuellement connecté
)

# Werkzeug : sécurité des mots de passe
# generate_password_hash : "admin123" → "pbkdf2:sha256:260000$..."
# check_password_hash    : vérifie si un mot de passe correspond au hash
from werkzeug.security import generate_password_hash, check_password_hash

# Modèles de données définis dans database.py
from database import db, User, Product, Order, OrderItem, Review, Wishlist, Newsletter

# functools.wraps : préserve le nom de la fonction décorée
# (nécessaire pour le décorateur admin_required)
from functools import wraps

# os : accès aux variables d'environnement
import os


# ═══════════════════════════════════════════════════════════════
#  CRÉATION ET CONFIGURATION DE L'APPLICATION FLASK
# ═══════════════════════════════════════════════════════════════

# Création de l'instance Flask
# __name__ dit à Flask où trouver les templates et fichiers statiques
app = Flask(__name__)

# ── CONFIGURATION ────────────────────────────────────────────────

# SECRET_KEY : clé secrète utilisée par Flask pour :
#   1. Signer les cookies de session (empêche la falsification)
#   2. Protéger contre les attaques CSRF
# → En production, cette clé DOIT être définie via variable d'environnement
# → Jamais en dur dans le code (sauf pour le développement local)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'biwex_ultra_secret_2025_xK9mP!')

# DATABASE_URL : URL de connexion à la base de données
# → SQLite par défaut (fichier local biwex.db)
# → PostgreSQL en production (variable d'environnement DATABASE_URL)
db_url = os.environ.get('DATABASE_URL', 'sqlite:///biwex.db')

# Correction de compatibilité : certains hébergeurs utilisent "postgres://"
# au lieu de "postgresql://" (ancien format), SQLAlchemy exige le nouveau
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url

# Désactive le suivi des modifications (économise de la mémoire)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ── CONFIGURATION WHATSAPP ───────────────────────────────────────
# Numéro de téléphone WhatsApp pour les notifications de commande
# → Utilisé pour générer un lien wa.me/<numéro>
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '21654360846')


# ═══════════════════════════════════════════════════════════════
#  INITIALISATION DES EXTENSIONS FLASK
# ═══════════════════════════════════════════════════════════════

# Connexion de SQLAlchemy à l'application Flask
# → À partir d'ici, db.session permet d'interagir avec la BDD
db.init_app(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Si un utilisateur non-connecté tente d'accéder à une route @login_required,
# il sera redirigé vers la page de connexion
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'


# ═══════════════════════════════════════════════════════════════
#  FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════

@login_manager.user_loader
def load_user(user_id):
    """
    Callback Flask-Login : charge l'utilisateur depuis la BDD
    à chaque requête HTTP (via le cookie de session).

    Appelé automatiquement par Flask-Login pour reconstituer
    l'objet current_user à chaque page visitée.

    Args:
        user_id (str) : ID de l'utilisateur stocké dans la session

    Returns:
        User | None : L'utilisateur ou None si non trouvé
    """
    return User.query.get(int(user_id))


def admin_required(f):
    """
    Décorateur personnalisé : restreint l'accès aux administrateurs.

    Usage :
        @app.route('/admin')
        @login_required        ← Doit être connecté
        @admin_required        ← Doit être admin
        def admin():
            ...

    Si l'utilisateur n'est pas admin → redirigé vers la page d'accueil
    avec un message d'erreur.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Vérifie que l'utilisateur est connecté ET administrateur
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════
#  FILTRE JINJA2 PERSONNALISÉ
# ═══════════════════════════════════════════════════════════════

@app.template_filter('format_dt')
def format_dt(value):
    """
    Filtre Jinja2 : formate un nombre en prix tunisien (DT).

    Usage dans les templates HTML :
        {{ product.price | format_dt }}
        → "1 299,000 DT"

    Le format suit la convention tunisienne :
        - Séparateur de milliers : espace
        - Séparateur décimal : virgule
        - 3 décimales
        - Suffixe "DT" (Dinar Tunisien)
    """
    try:
        val = float(value)
        formatted = f"{val:,.3f}".replace(',', ' ').replace('.', ',')
        return f"{formatted} DT"
    except (ValueError, TypeError):
        return f"{value} DT"


# ═══════════════════════════════════════════════════════════════
#  CONTEXT PROCESSOR (Variables globales pour les templates)
# ═══════════════════════════════════════════════════════════════

@app.context_processor
def inject_global_vars():
    """
    Injecte des variables disponibles dans TOUS les templates HTML.

    Appelé automatiquement par Flask avant chaque rendu de template.
    Permet d'avoir accès à ces variables sans les passer
    explicitement dans chaque render_template().

    Variables injectées :
        - global_categories : Liste des catégories de produits
        - global_cart_count : Nombre d'articles dans le panier
        - global_cart_total : Montant total du panier
        - WHATSAPP_NUMBER   : Numéro WhatsApp pour les commandes
    """
    # Récupère la liste des catégories distinctes
    cats = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in cats if c[0]]

    # Calcul du panier depuis la session
    # Le panier est stocké comme un dict : {"1": 2, "5": 1}
    # → Clé = ID produit, Valeur = quantité
    cart = session.get('cart', {})
    cart_count = 0
    cart_total = 0.0
    if isinstance(cart, dict):
        for pid, qty in cart.items():
            p = Product.query.get(int(pid))
            if p:
                cart_count += qty
                cart_total += p.price * qty

    return {
        'global_categories': categories,
        'global_cart_count': cart_count,
        'global_cart_total': cart_total,
        'WHATSAPP_NUMBER': WHATSAPP_NUMBER
    }


# ═══════════════════════════════════════════════════════════════
#  DONNÉES INITIALES (Seed)
# ═══════════════════════════════════════════════════════════════

def seed_products():
    """
    Peuple la base de données avec des produits de démonstration.

    Appelé une seule fois au premier démarrage de l'application
    (si la table Product est vide).

    Catégories : Smartphones, Laptops, Audio, Tablettes, TV,
                 Gaming, Accessoires
    """
    products = [
        # ── SMARTPHONES ──────────────────────────────────────
        Product(name='iPhone 15 Pro', price=3299.00, original_price=3599.00,
                description='Puce A17 Pro, écran Super Retina XDR 6.1", caméra 48MP, titane naturel. La révolution pro.',
                category='Smartphones', stock=20,
                image='https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=85',
                rating=4.8, review_count=124),
        Product(name='iPhone 15', price=2599.00, original_price=0,
                description='Puce A16 Bionic, Dynamic Island, charge USB-C, caméra 48MP. Le meilleur iPhone standard.',
                category='Smartphones', stock=18,
                image='https://images.unsplash.com/photo-1696446701796-da61225697cc?w=800&auto=format&fit=crop&q=85',
                rating=4.6, review_count=89),
        Product(name='Samsung Galaxy S24 Ultra', price=2999.00, original_price=3299.00,
                description='S Pen intégré, écran AMOLED 6.8" 120Hz, zoom 200x, Snapdragon 8 Gen 3. La perfection Android.',
                category='Smartphones', stock=15,
                image='https://images.unsplash.com/photo-1707233657290-8aab88fd6d3a?w=800&auto=format&fit=crop&q=85',
                rating=4.7, review_count=203),
        Product(name='Samsung Galaxy A55', price=1199.00, original_price=0,
                description='Écran AMOLED 6.6" 120Hz, triple caméra 50MP, batterie 5000mAh. Rapport qualité/prix imbattable.',
                category='Smartphones', stock=25,
                image='https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&auto=format&fit=crop&q=85',
                rating=4.3, review_count=56),
        Product(name='Xiaomi 14 Pro', price=1899.00, original_price=2199.00,
                description='Snapdragon 8 Gen 3, caméra Leica, charge 120W, écran AMOLED 6.73". Puissance brute.',
                category='Smartphones', stock=10,
                image='https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&auto=format&fit=crop&q=85',
                rating=4.5, review_count=72),
        Product(name='Google Pixel 8 Pro', price=1999.00, original_price=0,
                description='IA Google Tensor G3, caméra pro 50MP, 7 ans de mises à jour garanties.',
                category='Smartphones', stock=12,
                image='https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=800&auto=format&fit=crop&q=85',
                rating=4.4, review_count=44),

        # ── LAPTOPS ──────────────────────────────────────────
        Product(name='MacBook Pro M3', price=6299.00, original_price=6799.00,
                description='Puce M3, écran Liquid Retina 14", 18h autonomie, 8GB RAM. La machine des créatifs.',
                category='Laptops', stock=8,
                image='https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=85',
                rating=4.9, review_count=317),
        Product(name='MacBook Air M2', price=4299.00, original_price=0,
                description='Ultra-fin, puce M2, écran 13.6" Liquid Retina, 18h autonomie. Légèreté absolue.',
                category='Laptops', stock=10,
                image='https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&auto=format&fit=crop&q=85',
                rating=4.8, review_count=251),
        Product(name='Dell XPS 15', price=4599.00, original_price=4999.00,
                description='Écran OLED 4K, Intel Core i9, RTX 4060, 32GB RAM, 1TB SSD. Powerhouse portable.',
                category='Laptops', stock=6,
                image='https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=800&auto=format&fit=crop&q=85',
                rating=4.6, review_count=98),
        Product(name='HP Omen 16', price=3199.00, original_price=3599.00,
                description='RTX 4070, écran 16" 165Hz, AMD Ryzen 9, 16GB RAM. Gaming sans compromis.',
                category='Laptops', stock=12,
                image='https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800&auto=format&fit=crop&q=85',
                rating=4.4, review_count=67),
        Product(name='Asus ROG Zephyrus G14', price=3499.00, original_price=0,
                description='Gaming 14" compact, RTX 4060, AMD Ryzen 9, 144Hz, 1TB SSD. Puissance nomade.',
                category='Laptops', stock=9,
                image='https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&auto=format&fit=crop&q=85',
                rating=4.5, review_count=83),

        # ── AUDIO ────────────────────────────────────────────
        Product(name='Sony WH-1000XM5', price=899.00, original_price=1099.00,
                description='Meilleur ANC du marché, 30h autonomie, charge rapide 3min=3h. Le casque ultime.',
                category='Audio', stock=30,
                image='https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&auto=format&fit=crop&q=85',
                rating=4.9, review_count=892),
        Product(name='AirPods Pro 2', price=699.00, original_price=0,
                description="ANC adaptatif, audio spatial, USB-C, puce H2 Apple. L'expérience sonore Apple.",
                category='Audio', stock=25,
                image='https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&auto=format&fit=crop&q=85',
                rating=4.7, review_count=445),
        Product(name='Bose QuietComfort 45', price=799.00, original_price=899.00,
                description='ANC légendaire Bose, 24h autonomie, coussinets mémoire de forme. Confort exceptionnel.',
                category='Audio', stock=20,
                image='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=85',
                rating=4.6, review_count=321),
        Product(name='JBL Charge 5', price=349.00, original_price=0,
                description='Enceinte portable waterproof IP67, 20h autonomie, powerbank intégrée. La fête partout.',
                category='Audio', stock=35,
                image='https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&auto=format&fit=crop&q=85',
                rating=4.5, review_count=178),

        # ── TABLETTES ────────────────────────────────────────
        Product(name='iPad Pro 12.9"', price=2799.00, original_price=3099.00,
                description='Puce M2, écran Liquid Retina XDR, Apple Pencil 2, Face ID. La tablette suprême.',
                category='Tablettes', stock=10,
                image='https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&auto=format&fit=crop&q=85',
                rating=4.8, review_count=267),
        Product(name='iPad Air M1', price=1799.00, original_price=0,
                description='Puce M1, écran 10.9" True Tone, Touch ID, USB-C, 5G. Polyvalence absolue.',
                category='Tablettes', stock=14,
                image='https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&auto=format&fit=crop&q=85',
                rating=4.6, review_count=134),
        Product(name='Samsung Galaxy Tab S9', price=1999.00, original_price=2199.00,
                description='S Pen inclus, écran AMOLED 11" 120Hz, IP68, Snapdragon 8 Gen 2. Android premium.',
                category='Tablettes', stock=8,
                image='https://images.unsplash.com/photo-1632163191365-4b5b83aeea19?w=800&auto=format&fit=crop&q=85',
                rating=4.5, review_count=89),

        # ── TV ───────────────────────────────────────────────
        Product(name='Samsung QLED 55"', price=1999.00, original_price=2499.00,
                description='QLED 4K, HDR10+, Smart TV Tizen, 120Hz, Dolby Atmos, Gaming Mode.',
                category='TV', stock=5,
                image='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=85',
                rating=4.5, review_count=112),
        Product(name='LG OLED C3 65"', price=3499.00, original_price=3999.00,
                description='OLED evo 4K, 120Hz, G-Sync, Dolby Vision IQ, webOS 23, 4 HDMI 2.1. Le meilleur TV.',
                category='TV', stock=4,
                image='https://images.unsplash.com/photo-1567690187548-f07b1d7bf5a9?w=800&auto=format&fit=crop&q=85',
                rating=4.9, review_count=456),

        # ── GAMING ───────────────────────────────────────────
        Product(name='PlayStation 5', price=1799.00, original_price=0,
                description='SSD ultra-rapide, ray tracing, 4K 120fps, DualSense haptique. La next-gen est là.',
                category='Gaming', stock=7,
                image='https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=800&auto=format&fit=crop&q=85',
                rating=4.8, review_count=1203),
        Product(name='Xbox Series X', price=1699.00, original_price=1899.00,
                description='12 téraflops, 4K 120fps, 1TB SSD, rétrocompatibilité totale. La puissance Xbox.',
                category='Gaming', stock=9,
                image='https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=800&auto=format&fit=crop&q=85',
                rating=4.7, review_count=876),
        Product(name='Nintendo Switch OLED', price=899.00, original_price=0,
                description='Écran OLED 7", dock TV inclus, Joy-Con détachables, 9h autonomie. Jouez partout.',
                category='Gaming', stock=15,
                image='https://images.unsplash.com/photo-1585620385456-4759f9b5c7d9?w=800&auto=format&fit=crop&q=85',
                rating=4.6, review_count=654),

        # ── ACCESSOIRES ──────────────────────────────────────
        Product(name='Logitech MX Master 3S', price=349.00, original_price=399.00,
                description='Souris pro 8000 DPI, MagSpeed scroll silencieux, USB-C, multi-appareils. Précision absolue.',
                category='Accessoires', stock=40,
                image='https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop&q=85',
                rating=4.7, review_count=389),
        Product(name='Dell UltraSharp 27" 4K', price=1299.00, original_price=1499.00,
                description='Écran 4K IPS, 60Hz, USB-C 90W, calibré usine, Delta E < 2. Couleurs parfaites.',
                category='Accessoires', stock=12,
                image='https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=85',
                rating=4.6, review_count=156),
        Product(name='Anker PowerBank 26800mAh', price=249.00, original_price=0,
                description='26800mAh, charge rapide 65W, 3 ports USB-C, compatible laptops. Ne tombez plus à plat.',
                category='Accessoires', stock=50,
                image='https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&auto=format&fit=crop&q=85',
                rating=4.4, review_count=234),

        # ── NOUVELLE COLLECTION HIGH-TECH ────────────────────
        Product(name='Apple Watch Series 9 GPS', price=1599.00, original_price=1799.00,
                description='Puce S9 SiP, geste Toucher deux fois magique, écran deux fois plus lumineux, boîtier aluminium 45mm.',
                category='Accessoires', stock=16,
                image='https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&auto=format&fit=crop&q=85',
                rating=4.8, review_count=142),
        Product(name='Sony PlayStation VR2', price=2199.00, original_price=2499.00,
                description='Casque réalité virtuelle 4K HDR, suivi des yeux, retour haptique et gâchettes adaptatives Sense.',
                category='Gaming', stock=8,
                image='https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=800&auto=format&fit=crop&q=85',
                rating=4.7, review_count=98),
        Product(name='Asus ROG Ally Z1 Extreme', price=2599.00, original_price=2899.00,
                description='Console portable Windows 11, écran FHD 120Hz 7", processeur AMD Ryzen Z1 Extreme, 512GB SSD.',
                category='Gaming', stock=11,
                image='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=85',
                rating=4.6, review_count=76),
        Product(name='Samsung Galaxy Watch 6 Classic', price=1199.00, original_price=1399.00,
                description='Cadran rotatif emblématique en acier, suivi du sommeil avancé, capteur BioActive et écran sapphire.',
                category='Accessoires', stock=20,
                image='https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=85',
                rating=4.5, review_count=88),
        Product(name='Ecran Gaming Samsung Odyssey G9 49"', price=4199.00, original_price=4799.00,
                description='Écran incurvé Dual QHD 240Hz 1ms, technologie QLED Quantum Dot, immersion totale gaming.',
                category='Accessoires', stock=5,
                image='https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=85',
                rating=4.9, review_count=64),
        Product(name='Marshall Stanmore III Bluetooth', price=1299.00, original_price=1450.00,
                description='Enceinte vintage stéréo Bluetooth 5.2, son puissant et immersif, boutons de contrôle en laiton.',
                category='Audio', stock=14,
                image='https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=85',
                rating=4.8, review_count=189),
    ]

    # bulk_save_objects : insère tous les produits en une seule transaction
    # (plus performant que db.session.add() en boucle)
    db.session.bulk_save_objects(products)
    db.session.commit()


# ═══════════════════════════════════════════════════════════════
#  INITIALISATION DE LA BASE DE DONNÉES
#
#  Exécuté une seule fois au démarrage de l'application.
#  app.app_context() : nécessaire pour accéder à db en dehors
#  d'une requête HTTP (Flask exige un contexte d'application).
# ═══════════════════════════════════════════════════════════════
with app.app_context():
    # Crée toutes les tables définies dans database.py
    # (ne fait rien si les tables existent déjà)
    db.create_all()

    # Si aucun produit n'existe → peupler avec les données de demo
    if not Product.query.first():
        seed_products()

    # Créer un compte administrateur par défaut s'il n'existe pas
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username='Admin Biwex',
            email='admin@biwex.tn',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()


# ═══════════════════════════════════════════════════════════════
#                       ROUTES PUBLIQUES
# ═══════════════════════════════════════════════════════════════


# ── PAGE D'ACCUEIL (Catalogue) ────────────────────────────────
@app.route('/')
def index():
    """
    Page d'accueil : affiche le catalogue des produits avec
    filtrage, recherche, tri et ventes flash.

    Paramètres GET (optionnels) :
        ?category=Smartphones  → Filtre par catégorie
        ?search=iPhone         → Recherche par nom
        ?sort=price_asc        → Tri par prix croissant
        ?min_price=100         → Prix minimum
        ?max_price=5000        → Prix maximum
        ?in_stock=1            → Uniquement produits en stock
        ?brand=Samsung         → Filtre par marque
    """
    # Récupération des paramètres de filtrage
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock = request.args.get('in_stock', '')
    selected_brand = request.args.get('brand', '')

    # Construction de la requête SQL avec filtres
    query = Product.query

    # Filtrage par catégorie
    if category:
        query = query.filter_by(category=category)

    # Recherche par nom (LIKE %search%)
    # ilike = case-insensitive LIKE
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    # Filtrage par marque
    if selected_brand:
        query = query.filter(Product.name.ilike(f'%{selected_brand}%'))

    # Filtrage par prix (fourchette)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Uniquement produits en stock
    if in_stock == '1':
        query = query.filter(Product.stock > 0)

    # Tri des résultats
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())       # Moins cher d'abord
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())      # Plus cher d'abord
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())     # Mieux notés
    elif sort == 'new':
        query = query.order_by(Product.id.desc())         # Plus récents
    else:
        query = query.order_by(Product.rating.desc(), Product.id.asc())  # Par défaut

    products = query.all()

    # Comptage des produits par catégorie (pour la sidebar)
    all_prods = Product.query.all()
    category_counts = {}
    for p in all_prods:
        if p.category:
            category_counts[p.category] = category_counts.get(p.category, 0) + 1

    categories = list(category_counts.keys())

    # Ventes Flash : produits avec remise (original_price > price)
    flash_products = [p for p in all_prods if p.original_price and p.original_price > p.price]
    flash_products.sort(key=lambda x: (x.original_price - x.price), reverse=True)

    # Wishlist de l'utilisateur connecté (pour afficher les cœurs remplis)
    wishlist_ids = []
    if current_user.is_authenticated:
        wishlist_ids = [w.product_id for w in Wishlist.query.filter_by(user_id=current_user.id).all()]

    return render_template('index.html',
                           products=products,
                           categories=categories,
                           category_counts=category_counts,
                           flash_products=flash_products[:6],
                           selected_category=category,
                           search=search,
                           sort=sort,
                           in_stock=in_stock,
                           selected_brand=selected_brand,
                           wishlist_ids=wishlist_ids)


# ── FICHE PRODUIT ─────────────────────────────────────────────
@app.route('/product/<int:id>')
def product(id):
    """
    Page de détail d'un produit.
    Affiche les informations, les produits similaires et les avis.

    Args:
        id (int) : ID du produit (passé dans l'URL)
    """
    # get_or_404 : retourne le produit ou une erreur 404 si non trouvé
    p = Product.query.get_or_404(id)

    # Produits similaires (même catégorie, différent du courant)
    related = Product.query.filter_by(category=p.category).filter(Product.id != id).limit(4).all()

    # Avis triés du plus récent au plus ancien
    reviews = Review.query.filter_by(product_id=id).order_by(Review.created_at.desc()).all()

    # Vérification pour l'utilisateur connecté
    in_wishlist = False
    user_reviewed = False
    if current_user.is_authenticated:
        in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first() is not None
        user_reviewed = Review.query.filter_by(user_id=current_user.id, product_id=id).first() is not None

    return render_template('product.html',
                           product=p,
                           related=related,
                           reviews=reviews,
                           in_wishlist=in_wishlist,
                           user_reviewed=user_reviewed)


# ── AJOUTER UN AVIS ──────────────────────────────────────────
@app.route('/product/<int:id>/review', methods=['POST'])
@login_required
def add_review(id):
    """
    Ajoute un avis sur un produit (POST uniquement).
    Un utilisateur ne peut laisser qu'un seul avis par produit.
    La note moyenne du produit est automatiquement recalculée.
    """
    p = Product.query.get_or_404(id)

    # Vérifie si l'utilisateur a déjà laissé un avis
    existing = Review.query.filter_by(user_id=current_user.id, product_id=id).first()
    if existing:
        flash('Vous avez déjà laissé un avis pour ce produit.', 'info')
        return redirect(url_for('product', id=id))

    # Création du nouvel avis
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '').strip()
    review = Review(user_id=current_user.id, product_id=id, rating=rating, comment=comment)
    db.session.add(review)

    # Recalcul de la note moyenne du produit
    all_reviews = Review.query.filter_by(product_id=id).all()
    total = sum(r.rating for r in all_reviews) + rating
    count = len(all_reviews) + 1
    p.rating = round(total / count, 1)
    p.review_count = count
    db.session.commit()

    flash('Merci pour votre avis ! ⭐', 'success')
    return redirect(url_for('product', id=id))


# ═══════════════════════════════════════════════════════════════
#                     ROUTES WISHLIST
# ═══════════════════════════════════════════════════════════════

@app.route('/wishlist/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_wishlist(id):
    """
    Ajoute ou retire un produit de la wishlist (toggle).
    Appelé en AJAX depuis le frontend (retourne du JSON).

    Returns :
        JSON : {"status": "added"} ou {"status": "removed"}
    """
    Product.query.get_or_404(id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed'})
    else:
        w = Wishlist(user_id=current_user.id, product_id=id)
        db.session.add(w)
        db.session.commit()
        return jsonify({'status': 'added'})


@app.route('/wishlist')
@login_required
def wishlist():
    """Page de la liste de souhaits de l'utilisateur connecté."""
    items = Wishlist.query.filter_by(user_id=current_user.id).order_by(Wishlist.created_at.desc()).all()
    return render_template('wishlist.html', items=items)


# ═══════════════════════════════════════════════════════════════
#                     ROUTES PROFIL
# ═══════════════════════════════════════════════════════════════

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Page de profil utilisateur (GET = affiche, POST = mise à jour).
    Permet de modifier : nom, téléphone, adresse, ville, mot de passe.
    Affiche aussi l'historique des commandes.
    """
    if request.method == 'POST':
        # Mise à jour des informations personnelles
        current_user.username = request.form.get('username', current_user.username)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.address = request.form.get('address', current_user.address)
        current_user.city = request.form.get('city', current_user.city)

        # Changement de mot de passe (optionnel)
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash('Profil mis à jour avec succès !', 'success')
        return redirect(url_for('profile'))

    # Historique des commandes (GET)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)


# ═══════════════════════════════════════════════════════════════
#                     ROUTES NEWSLETTER
# ═══════════════════════════════════════════════════════════════

@app.route('/newsletter', methods=['POST'])
def newsletter():
    """
    Inscription à la newsletter (POST).
    Vérifie si l'email est déjà inscrit pour éviter les doublons.
    """
    email = request.form.get('email', '').strip()
    if email:
        existing = Newsletter.query.filter_by(email=email).first()
        if not existing:
            db.session.add(Newsletter(email=email))
            db.session.commit()
            flash('Merci ! Vous êtes inscrit à notre newsletter. 🎉', 'success')
        else:
            flash('Vous êtes déjà inscrit à notre newsletter.', 'info')
    return redirect(request.referrer or url_for('index'))


# ═══════════════════════════════════════════════════════════════
#               ROUTES AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════════

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Page d'inscription (GET = formulaire, POST = création du compte).

    Sécurité :
      - Le mot de passe est HACHÉ avant stockage (generate_password_hash)
      - L'email doit être unique (vérifié avant insertion)
      - L'utilisateur est automatiquement connecté après l'inscription
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Vérification de l'unicité de l'email
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('register'))

        # Création du compte avec mot de passe haché
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        # Connexion automatique après inscription
        login_user(user)
        flash(f'Bienvenue {username} ! Votre compte a été créé. 🎉', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Page de connexion (GET = formulaire, POST = authentification).

    Processus d'authentification :
      1. Cherche l'utilisateur par email
      2. Vérifie le mot de passe avec check_password_hash()
      3. Si OK → crée une session Flask-Login
      4. Si KO → affiche un message d'erreur

    Sécurité :
      - Le mot de passe n'est JAMAIS comparé en clair
      - check_password_hash compare le hash stocké avec le hash
        du mot de passe saisi
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Recherche de l'utilisateur par email
        user = User.query.filter_by(email=email).first()

        # Vérification du mot de passe haché
        if user and check_password_hash(user.password, password):
            login_user(user)  # Crée la session d'authentification
            flash(f'Bon retour {user.username} ! 👋', 'success')

            # Redirige vers la page demandée (si passée en paramètre ?next=)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))

        flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Déconnexion : détruit la session Flask-Login."""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))


# ═══════════════════════════════════════════════════════════════
#                     ROUTES PANIER ET CODES PROMO
# ═══════════════════════════════════════════════════════════════

# Dictionnaire des codes promotionnels actifs sur Biwex Store
# Notion facile : clé = code à taper, valeur = détails de la réduction
COUPONS_DISPONIBLES = {
    'DEVOPS20': {'remise_pourcent': 20, 'description': 'Remise spéciale DevOps (-20%)'},
    'ISGS10':   {'remise_pourcent': 10, 'description': 'Remise étudiante ISG Sousse (-10%)'},
    'BIWEX5':   {'remise_fixe': 5.0,    'description': 'Bon d\'achat de bienvenue (-5 DT)'}
}

@app.route('/cart/apply-coupon', methods=['POST'])
def apply_coupon():
    """
    Applique un code promo sur le panier en cours.
    Vérifie l'existence du code et le stocke dans la session Flask.
    """
    code = request.form.get('coupon_code', '').strip().upper()
    if not code:
        flash('Veuillez saisir un code promo.', 'warning')
        return redirect(url_for('cart'))

    if code in COUPONS_DISPONIBLES:
        session['coupon'] = {
            'code': code,
            **COUPONS_DISPONIBLES[code]
        }
        flash(f'Code promo "{code}" activé avec succès ! 🎉', 'success')
    else:
        flash(f'Le code promo "{code}" est invalide ou expiré.', 'danger')

    return redirect(url_for('cart'))


@app.route('/cart/remove-coupon')
def remove_coupon():
    """Retire le code promo actuellement appliqué."""
    session.pop('coupon', None)
    flash('Le code promotionnel a été retiré.', 'info')
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    """
    Page du panier d'achat.

    Le panier est stocké dans la SESSION Flask (côté serveur).
    Structure : {"product_id": quantity, ...}
    Exemple   : {"1": 2, "5": 1} → 2x produit #1, 1x produit #5

    Prend en compte les codes promo et nettoie les produits épuisés.
    """
    cart = session.get('cart', {})
    clean_cart = {}
    items = []
    total = 0

    for pid, qty in cart.items():
        p = Product.query.get(int(pid))
        if p and p.stock > 0:
            # Ajuste la quantité si elle dépasse le stock
            qty = min(qty, p.stock)
            subtotal = p.price * qty
            total += subtotal
            items.append({'product': p, 'qty': qty, 'subtotal': subtotal})
            clean_cart[pid] = qty

    # Mise à jour du panier nettoyé dans la session
    session['cart'] = clean_cart

    # Calcul de la réduction si un code promo est actif
    coupon = session.get('coupon')
    discount = 0.0
    if coupon and total > 0:
        if 'remise_pourcent' in coupon:
            discount = round(total * (coupon['remise_pourcent'] / 100.0), 3)
        elif 'remise_fixe' in coupon:
            discount = min(total, float(coupon['remise_fixe']))

    final_total = max(0.0, total - discount)

    return render_template('cart.html', items=items, total=total, discount=discount,
                           final_total=final_total, coupon=coupon)


@app.route('/cart/add/<int:id>', methods=['POST'])
def add_to_cart(id):
    """
    Ajoute un produit au panier (POST).
    Supporte les requêtes AJAX (retourne du JSON) et les
    requêtes classiques (redirige avec un message flash).

    La quantité est ajoutée à la quantité existante dans le panier,
    mais ne peut pas dépasser le stock disponible.
    """
    p = Product.query.get_or_404(id)
    qty = max(1, int(request.form.get('qty', 1)))

    # Vérification du stock
    if p.stock <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Ce produit est en rupture de stock.'}), 400
        flash('Ce produit est en rupture de stock.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # Ajout au panier dans la session
    cart = session.get('cart', {})
    current_qty = cart.get(str(id), 0)
    new_qty = min(current_qty + qty, p.stock)  # Ne pas dépasser le stock
    cart[str(id)] = new_qty
    session['cart'] = cart

    # Réponse AJAX ou redirection classique
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_count = sum(cart.values())
        return jsonify({'status': 'ok', 'count': total_count})

    flash('Produit ajouté au panier ! 🛒', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/cart/remove/<int:id>')
def remove_from_cart(id):
    """Supprime un produit du panier."""
    cart = session.get('cart', {})
    cart.pop(str(id), None)
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/cart/update', methods=['POST'])
def update_cart():
    """
    Met à jour les quantités du panier (POST).
    Ajuste automatiquement si la quantité demandée > stock.
    Supprime les produits avec quantité <= 0.
    """
    cart = session.get('cart', {})
    stock_adjusted = False

    for key in list(cart.keys()):
        p = Product.query.get(int(key))
        if not p:
            cart.pop(key, None)
            continue

        try:
            qty = int(request.form.get(f'qty_{key}', 1))
        except (ValueError, TypeError):
            qty = 1

        if qty <= 0:
            cart.pop(key, None)
        else:
            if qty > p.stock:
                qty = p.stock
                stock_adjusted = True
            cart[key] = qty

    session['cart'] = cart

    if stock_adjusted:
        flash('Certaines quantités ont été ajustées en fonction du stock disponible.', 'warning')
    else:
        flash('Panier mis à jour.', 'info')
    return redirect(url_for('cart'))


# ═══════════════════════════════════════════════════════════════
#                     ROUTE CHECKOUT
# ═══════════════════════════════════════════════════════════════

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Passage de commande (GET = formulaire, POST = validation).

    Processus :
      1. Vérifie que le panier n'est pas vide
      2. Vérifie les stocks (ajuste si nécessaire)
      3. Crée la commande en BDD (Order + OrderItems)
      4. Décrémente les stocks des produits
      5. Génère un message WhatsApp avec le détail
      6. Redirige vers la confirmation

    Sécurité :
      @login_required : seuls les utilisateurs connectés
      peuvent passer commande
    """
    cart = session.get('cart', {})
    if not cart:
        flash('Votre panier est vide.', 'info')
        return redirect(url_for('cart'))

    # Préparation des articles avec vérification des stocks
    items = []
    total = 0
    clean_cart = {}
    stock_issue = False

    for pid, qty in cart.items():
        p = Product.query.get(int(pid))
        if p and p.stock > 0:
            if qty > p.stock:
                qty = p.stock
                stock_issue = True
            subtotal = p.price * qty
            total += subtotal
            items.append({'product': p, 'qty': qty, 'subtotal': subtotal})
            clean_cart[pid] = qty
        else:
            stock_issue = True

    session['cart'] = clean_cart

    if not items:
        flash('Les produits de votre panier ne sont plus disponibles.', 'danger')
        return redirect(url_for('cart'))

    if stock_issue:
        flash('Le contenu de votre panier a été mis à jour selon les stocks disponibles.', 'warning')

    # Prise en compte du code promo s'il existe
    coupon = session.get('coupon')
    discount = 0.0
    if coupon and total > 0:
        if 'remise_pourcent' in coupon:
            discount = round(total * (coupon['remise_pourcent'] / 100.0), 3)
        elif 'remise_fixe' in coupon:
            discount = min(total, float(coupon['remise_fixe']))
    final_total = max(0.0, total - discount)

    if request.method == 'POST':
        # Récupération des informations de livraison
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        phone = request.form.get('phone', '').strip()

        # Sauvegarde dans le profil si les champs étaient vides
        if address and not current_user.address:
            current_user.address = address
        if city and not current_user.city:
            current_user.city = city
        if phone and not current_user.phone:
            current_user.phone = phone

        # Création de la commande en base de données avec le montant remisé
        order = Order(
            user_id=current_user.id,
            total=final_total,
            status='En attente',
            address=address or current_user.address,
            city=city or current_user.city,
            phone=phone or current_user.phone
        )
        db.session.add(order)
        db.session.flush()  # Flush pour obtenir l'ID de la commande

        # Création des lignes de commande et décrémentation des stocks
        for item in items:
            oi = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['qty'],
                price=item['product'].price
            )
            db.session.add(oi)
            # Décrémentation du stock (jamais en dessous de 0)
            item['product'].stock = max(0, item['product'].stock - item['qty'])

        db.session.commit()

        # Vidage du panier et du code promo après commande réussie
        session['cart'] = {}
        session.pop('coupon', None)

        # ── Génération du message WhatsApp ──────────────────
        import urllib.parse
        lines = []
        lines.append('🛒 *Nouvelle commande Biwex* — Commande #' + str(order.id))
        lines.append('')
        lines.append('👤 *Client :* ' + current_user.username)
        lines.append('📧 *Email :* ' + current_user.email)
        lines.append('📞 *Tél :* ' + (order.phone or 'Non renseigné'))
        lines.append('📍 *Adresse :* ' + (order.address or '') + ', ' + (order.city or ''))
        lines.append('')
        lines.append('🧾 *Articles commandés :*')
        for item in items:
            lines.append(f"  • {item['product'].name} × {item['qty']} — {item['subtotal']:.2f} DT")
        lines.append('')
        if discount > 0:
            lines.append(f'🎟️ *Remise code promo ({coupon["code"]}) : -{discount:.2f} DT*')
        lines.append(f'💰 *Total Final : {final_total:.2f} DT*')
        lines.append('')
        lines.append("✅ Merci de confirmer cette commande et d'indiquer les instructions de paiement.")

        message = '\n'.join(lines)
        whatsapp_url = f'https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}'

        flash('🎉 Commande enregistrée ! Cliquez sur le bouton WhatsApp pour finaliser votre commande.', 'success')
        return redirect(url_for('order_confirmation', id=order.id, wa=whatsapp_url))

    return render_template('checkout.html', items=items, total=total, discount=discount,
                           final_total=final_total, coupon=coupon)


# ── CONFIRMATION DE COMMANDE ──────────────────────────────────
@app.route('/order/<int:id>/confirmation')
@login_required
def order_confirmation(id):
    """
    Page de confirmation après passage de commande.
    Affiche un récapitulatif et un bouton WhatsApp.

    Sécurité : seul le propriétaire ou un admin peut voir
    la confirmation d'une commande.
    """
    order = Order.query.get_or_404(id)

    # Vérification des droits d'accès
    if order.user_id != current_user.id and not current_user.is_admin:
        return redirect(url_for('index'))

    # Récupération ou reconstruction du lien WhatsApp
    import urllib.parse
    whatsapp_url = request.args.get('wa', '')

    if not whatsapp_url:
        lines = []
        lines.append('🛒 *Commande Biwex* — Commande #' + str(order.id))
        lines.append('👤 *Client :* ' + order.user.username)
        lines.append('📞 *Tél :* ' + (order.phone or 'Non renseigné'))
        lines.append('📍 *Adresse :* ' + (order.address or '') + ', ' + (order.city or ''))
        lines.append('')
        for item in order.items:
            if item.product:
                lines.append(f"  • {item.product.name} × {item.quantity} — {item.price * item.quantity:.2f} DT")
        lines.append(f'💰 *Total : {order.total:.2f} DT*')
        message = '\n'.join(lines)
        whatsapp_url = f'https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}'

    return render_template('order_confirmation.html', order=order, whatsapp_url=whatsapp_url)


# ═══════════════════════════════════════════════════════════════
#                   ROUTES ADMINISTRATION
#
#  Toutes ces routes sont protégées par :
#    @login_required  → doit être connecté
#    @admin_required  → doit être administrateur (is_admin=True)
# ═══════════════════════════════════════════════════════════════

@app.route('/admin')
@login_required
@admin_required
def admin():
    """
    Dashboard administrateur.
    Affiche : produits, commandes, utilisateurs, stats newsletter.
    Calcule le chiffre d'affaires total (commandes Payées + Livrées).
    """
    products = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.order_by(Order.id.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    newsletters = Newsletter.query.count()

    # Chiffre d'affaires : uniquement les commandes payées ou livrées
    total_rev = sum(o.total for o in orders if o.status in ('Payée', 'Livrée'))

    return render_template('admin.html',
                           products=products,
                           orders=orders,
                           users=users,
                           newsletters=newsletters,
                           total_rev=total_rev)


@app.route('/admin/product/add', methods=['POST'])
@login_required
@admin_required
def add_product():
    """Ajoute un nouveau produit au catalogue (POST)."""
    p = Product(
        name=request.form['name'],
        price=float(request.form['price']),
        original_price=float(request.form.get('original_price', 0) or 0),
        description=request.form['description'],
        category=request.form['category'],
        stock=int(request.form['stock']),
        image=request.form['image']
    )
    db.session.add(p)
    db.session.commit()
    flash('Produit ajouté avec succès !', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/product/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_product(id):
    """Modifie un produit existant (POST)."""
    p = Product.query.get_or_404(id)
    p.name = request.form.get('name', p.name)
    p.price = float(request.form.get('price', p.price))
    p.original_price = float(request.form.get('original_price', 0) or 0)
    p.stock = int(request.form.get('stock', p.stock))
    p.description = request.form.get('description', p.description)
    db.session.commit()
    flash('Produit modifié.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/product/delete/<int:id>')
@login_required
@admin_required
def delete_product(id):
    """Supprime un produit du catalogue."""
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Produit supprimé.', 'info')
    return redirect(url_for('admin'))


@app.route('/admin/order/status/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(id):
    """Met à jour le statut d'une commande (En attente → Payée → Livrée...)."""
    order = Order.query.get_or_404(id)
    order.status = request.form['status']
    db.session.commit()
    return redirect(url_for('admin'))


# ═══════════════════════════════════════════════════════════════
#  ENDPOINT HEALTH CHECK
#
#  Route spéciale utilisée par Jenkins, Docker et les sondes
#  pour vérifier que l'application est en bonne santé (opérationnelle).
#
#  Retourne un JSON avec :
#    - status : "healthy" si tout fonctionne
#    - app    : nom de l'application
#    - version: version courante
#
#  Usage depuis Jenkins ou curl :
#    curl http://localhost:5000/health → {"status": "healthy", ...}
# ═══════════════════════════════════════════════════════════════
# ── ENDPOINT HEALTH CHECK & STATISTIQUES EN TEMPS RÉEL ─────────
# Route utilisée par Jenkins et les tableaux de bord de supervision
# pour surveiller l'état, la version et le stock de l'application.
@app.route('/health')
def health_check():
    """
    Endpoint de vérification de santé pour le monitoring.
    Utilisé par les smoke tests et les sondes Docker/Kubernetes.
    """
    total_products = Product.query.count()
    in_stock_count = Product.query.filter(Product.stock > 0).count()
    return jsonify({
        'status': 'healthy',
        'app': 'Biwex Store',
        'version': '1.1.0',
        'environment': 'Production (Docker Conteneurise)',
        'metrics': {
            'total_products': total_products,
            'products_in_stock': in_stock_count,
            'database': 'Connectee et operationnelle'
        }
    }), 200


# ═══════════════════════════════════════════════════════════════
#             API REST PUBLIQUE — BIWEX STORE
#  Développée par : Abdoul TRAORE (Branche feature/abdoul-traore)
#  Notion de cours : Interopérabilité des Systèmes d'Information
#  Permet d'échanger des données en JSON avec des applications mobiles,
#  des partenaires commerciaux ou des tableaux de bord décisionnels.
# ═══════════════════════════════════════════════════════════════

@app.route('/api/products', methods=['GET'])
def api_get_products():
    """
    API REST : Retourne la liste des produits en format JSON.
    Supporte les filtres : ?category=Smartphones&search=iphone
    """
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()

    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    products = query.all()
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'original_price': p.original_price,
            'category': p.category,
            'stock': p.stock,
            'in_stock': p.stock > 0,
            'rating': p.rating,
            'review_count': p.review_count,
            'image': p.image
        })

    return jsonify({
        'status': 'success',
        'count': len(results),
        'products': results
    }), 200


@app.route('/api/products/<int:id>', methods=['GET'])
def api_get_product_detail(id):
    """
    API REST : Retourne le détail complet d'un produit par son ID.
    Exemple : /api/products/1
    """
    p = Product.query.get(id)
    if not p:
        return jsonify({
            'status': 'error',
            'message': f"Le produit avec l'identifiant #{id} n'existe pas."
        }), 404

    return jsonify({
        'status': 'success',
        'product': {
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'original_price': p.original_price,
            'description': p.description,
            'category': p.category,
            'stock': p.stock,
            'rating': p.rating,
            'review_count': p.review_count,
            'image': p.image
        }
    }), 200


@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    """
    API REST : Liste de toutes les catégories avec le nombre d'articles associés.
    """
    cats = db.session.query(Product.category).distinct().all()
    category_list = []
    for c in cats:
        if c[0]:
            count = Product.query.filter_by(category=c[0]).count()
            category_list.append({
                'category_name': c[0],
                'product_count': count
            })

    return jsonify({
        'status': 'success',
        'total_categories': len(category_list),
        'categories': category_list
    }), 200


@app.route('/api/stats', methods=['GET'])
def api_get_store_stats():
    """
    API REST Décisionnelle : Indicateurs clés de performance (KPI) pour le management.
    Idéal pour les étudiants en Informatique de Gestion (3LIG).
    """
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    total_newsletter = Newsletter.query.count()

    paid_orders = Order.query.filter(Order.status.in_(['Payée', 'Livrée'])).all()
    chiffre_affaires = sum(o.total for o in paid_orders)

    return jsonify({
        'status': 'success',
        'kpi': {
            'chiffre_affaires_total_dt': round(chiffre_affaires, 3),
            'commandes_total': total_orders,
            'commandes_livrees_payees': len(paid_orders),
            'clients_inscrits': total_users,
            'produits_catalogue': total_products,
            'abonnes_newsletter': total_newsletter
        }
    }), 200


# ═══════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE — Démarrage du serveur de développement
#
#  En DÉVELOPPEMENT : python app.py → serveur Flask (debug=True)
#  En PRODUCTION    : gunicorn app:app → serveur Gunicorn (robuste)
#
#  debug=True active :
#    - Le rechargement automatique à chaque modification du code
#    - Les messages d'erreur détaillés dans le navigateur
#    - Le debugger interactif Werkzeug
#  → JAMAIS en production (faille de sécurité)
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True)
