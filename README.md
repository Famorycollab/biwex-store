# Biwex Store — Projet DevOps (CI/CD)

**Établissement :** ISG Sousse — 3 LIG  
**Année universitaire :** 2026 – 2027  
**Enseignante :** Mme Zaineb SAKHRAWI  
**Binôme :** Famory TOURÉ & Abdoul TRAORÉ  

---

## 1. Présentation du projet

**Biwex Store** est un site e-commerce de matériel informatique développé en **Python (Flask)** avec une base de données SQLite gérée par **SQLAlchemy**.

Dans ce projet, nous avons mis en place une chaîne **CI/CD** (Intégration Continue et Livraison Continue) autour de cette application avec les outils vus en cours : **Git/GitHub**, **Jenkins** et **Docker**.

### Ce que fait l'application
* **Catalogue :** 38 produits classés en 7 catégories (Smartphones, PC Portables, Audio, Gaming, TV, Tablettes, Accessoires), affichés par pages de 12 articles.
* **Recherche et filtres :** recherche par mot-clé et tri par catégorie.
* **Panier :** ajout d'articles, calcul automatique du total et simulation de commande.
* **Comptes utilisateurs :** inscription, connexion et espace admin avec mots de passe hachés.
* **Routes utiles pour le DevOps :**
  * `/api/products` : renvoie la liste des produits au format JSON.
  * `/health` : vérifie que le serveur et la base de données répondent bien (renvoie un code HTTP 200).

---

## 2. Gestion des branches Git

Pour travailler à deux sans casser le code principal, nous avons utilisé plusieurs branches :

* `main` : la branche de production, **protégée** sur GitHub (personne ne peut faire de `push` direct dessus, il faut obligatoirement passer par une Pull Request).
* `dev` : la branche d'intégration où on regroupe notre travail validé.
* `feature/famory-toure` : ma branche de travail (Dockerfile multi-stage, catalogue, Pipeline Dev avec parallélisation).
* `feature/abdoul-traore` : la branche de mon binôme (Pipeline PR, Pipeline Tag, API JSON, Docker Compose).
* **Tags (`vX.Y.Z`) :** pour marquer les versions officielles du projet (`v1.0.0` jusqu'à `v1.6.0`).

---

## 3. Conteneurisation avec Docker

Pour que l'application tourne de la même façon sur n'importe quelle machine, nous avons écrit un **Dockerfile Multi-Stage** (en 2 étapes) :
1. **Étape 1 (`builder`) :** on crée un environnement virtuel et on installe les bibliothèques de `requirements.txt`.
2. **Étape 2 (image finale) :** on repart d'une image `python:3.11-slim` propre et on copie uniquement les bibliothèques prêtes et le code du site.

### Ce que ça apporte
* **Image plus légère :** on passe d'environ **800 Mo à ~180 Mo**.
* **Sécurité :** le conteneur utilise un utilisateur simple `appuser` et jamais `root` (si quelqu'un attaque le site, il n'a pas les droits administrateur).
* **Serveur web de production :** on utilise **Gunicorn** sur le port `5000` au lieu du serveur de test de Flask.

---

## 4. Les 4 Pipelines Jenkins

Nous utilisons le principe **Pipeline-as-Code** : les étapes de Jenkins sont écrites dans des fichiers directement enregistrés dans Git :

| Pipeline | Fichier | Quand il se lance | Ce qu'il fait |
| :--- | :--- | :--- | :--- |
| **Pipeline 1 — PR** | `Jenkinsfile-PR` | À l'ouverture d'une Pull Request vers `dev` | Vérifie que la PR ne va pas vers `main`, construit l'image et lance le smoke test sur le port `5011`. |
| **Pipeline 2 — Dev** | `Jenkinsfile` | À chaque `push` sur `dev` | Construit en **parallèle** sur **Python 3.11** et **Python 3.12**, teste sur le port `5002` et sauvegarde les rapports. |
| **Pipeline 3 — Release** | `Jenkinsfile-Tag` | Quand on pousse un tag `vX.Y.Z` | Vérifie le format du tag (`v1.6.0`...), construit l'image finale et crée le fichier `release-manifest.txt`. |
| **Pipeline 4 — Sécurité** | `Jenkinsfile-Nightly-Security` | Toutes les nuits à 2h (`H 2 * * *`) | Vérifie la syntaxe du code Python, `requirements.txt`, la sécurité du Dockerfile et la base de données. |

Chaque pipeline suit les **6 stages** du sujet :  
`1. Checkout` → `2. Setup` → `3. Build Docker` → `4. Run Docker` → `5. Smoke Test` → `6. Archive Artifacts` + nettoyage automatique du conteneur de test à la fin (`post { always }`), tout en gardant le cache Docker pour que les prochains builds soient rapides (~30 secondes).

---

## 5. Smoke Test et Archivage

* Le script `scripts/smoke_test.py` envoie une requête HTTP sur le conteneur démarré par Jenkins :
  * S'il reçoit le code **HTTP 200** avec du HTML → **PASSED** (`sys.exit(0)`), l'étape devient verte.
  * Sinon → **FAILED** (`sys.exit(1)`), Jenkins arrête le pipeline et bloque la fusion.
* À la fin, Jenkins sauvegarde les rapports (`pipeline-report.txt`, `smoke-test.txt`, `release-manifest.txt`, `security-audit-report.txt`) avec une **empreinte MD5** (`fingerprint: true`) pour prouver qu'ils n'ont pas été modifiés.

---

## 6. Lancer le projet sur son PC

### Avec Docker Compose
```bash
git clone https://github.com/Famorycollab/biwex-store.git
cd biwex-store
docker compose up --build -d
```
Le site s'ouvre sur `http://localhost:5000` (et `/health` sur `http://localhost:5000/health`).

### En Python direct
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Lancer les tests
```bash
pytest tests/
python scripts/smoke_test.py http://127.0.0.1:5000/
```
