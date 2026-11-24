# 🎓 GUIDE ULTIME DE SOUTENANCE ORALE — QUESTIONS/RÉPONSES DU PROFESSEUR
### Projet : Biwex Store (DevOps 3LIG — ISG Sousse 2026-2027)
### Enseignante : Mme Zaineb SAKHRAWI
### Binôme : Famory TOURE & Abdoul TRAORE

---

## 📌 SOMMAIRE DU GUIDE

1. [DÉTAIL COMPLET 1 : Comment protéger la branche main sur GitHub ?](#1-détail-complet-1--comment-protéger-la-branche-main-sur-github)
2. [DÉTAIL COMPLET 2 : Comment créer et gérer les Tags Git (vX.Y.Z) ?](#2-détail-complet-2--comment-créer-et-gérer-les-tags-git-vxyz)
3. [LES QUESTIONS « QU'EST-CE QUE... ? » (Définitions + Analogies faciles)](#3-les-questions-quest-ce-que-)
4. [LES QUESTIONS « COMMENT... ? » (Mécanismes techniques expliqués simplement)](#4-les-questions-comment-)
5. [DÉMONSTRATION « PASSED / FAILED » DEVANT LA PROF](#5-démonstration-passed--failed-devant-la-prof)
6. [SCÉNARIO CHRONOMÉTRÉ DE SOUTENANCE (10 MINUTES CHRONO)](#6-scénario-chronométré-de-soutenance-10-minutes-chrono)
7. [CONSEILS EN OR POUR OBTENIR LA NOTE MAXIMALE](#7-conseils-en-or-pour-obtenir-la-note-maximale)

---

## 1. DÉTAIL COMPLET 1 : COMMENT PROTÉGER LA BRANCHE MAIN SUR GITHUB ?

### A. Pourquoi la protéger ? (L'analogie à expliquer au professeur)
> 💡 **Analogie simple :**  
> *"Madame, imaginez que la branche `main` soit la vitrine officielle de notre magasin Biwex. Si n'importe quel employé pouvait entrer sans permission et changer les étiquettes de prix ou casser un meuble, le magasin perdrait ses clients. Protéger la branche `main`, c'est installer une serrure électronique à double clé : personne ne peut y toucher directement. Tout changement doit obligatoirement être vérifié dans l'arrière-boutique (la branche `dev`), testé par la machine (Jenkins), et validé par l'autre collègue (Pull Request)."*

---

### B. Procédure étape par étape sur GitHub (Pas à pas ultra-détaillé) :

1. **Se connecter à GitHub** et ouvrir le dépôt du projet :  
   👉 `https://github.com/Famorycollab/biwex-store`
2. En haut de la page, cliquez sur l'onglet **Settings** (la petite roue crantée à droite).
3. Dans la barre latérale gauche (menu vertical), descendez à la section **Code and automation**, puis cliquez sur **Branches**.
4. Vous arrivez sur la page *Branch protection rules*. Cliquez sur le bouton vert **Add branch ruleset** (ou **Add rule** selon la version de GitHub).
5. Dans le champ **Ruleset Name** (ou **Branch name pattern**), tapez exactement :  
   `main`
6. **Cochez les règles indispensables pour le DevOps :**
   - 🔒 **Require a pull request before merging (Obliger une PR avant de fusionner)** :  
     *Ce que ça fait :* Interdit tout `git push origin main` direct. Si un étudiant essaie de pousser son code directement sur `main`, GitHub refuse immédiatement.
   - 👥 **Require approvals (Exiger une approbation)** :  
     *Ce que ça fait :* Réglez le compteur à **1**. Si Famory crée une Pull Request vers `main`, il ne peut pas la valider tout seul : Abdoul doit obligatoirement relire et cliquer sur "Approve" (ou inversement). Cela garantit le travail d'équipe et la relecture de code (*Code Review*).
   - 🧪 **Require status checks to pass before merging (Exiger la réussite des tests)** :  
     *Ce que ça fait :* Vous pouvez lier Jenkins ou GitHub Actions. Si les tests du pipeline sont en rouge (FAILED), le bouton "Merge" de GitHub reste grisé et bloqué.
   - 🛡️ **Do not allow bypassing the above settings (Interdire le contournement, même aux administrateurs)** :  
     *Ce que ça fait :* Même le créateur du dépôt ne peut pas tricher ou forcer un push direct. Tout le monde obéit à la même règle de qualité.
7. Descendez tout en bas de la page et cliquez sur le bouton vert **Create** (ou **Save changes**).

---

### C. Que se passe-t-il concrètement si on essaie de pousser sur main ? (La preuve technique)
Si Famory ou Abdoul tape dans son terminal :
```bash
git checkout main
git commit -m "Test de push direct interdit"
git push origin main
```
GitHub bloque instantanément la commande et affiche ce message d'erreur dans le terminal :
```text
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: At least 1 approving review is required by reviewers with write access.
remote: error: Changes must be made through a pull request.
To https://github.com/Famorycollab/biwex-store.git
 ! [remote rejected] main -> main (protected branch hook declined)
error: failed to push some refs to 'https://github.com/Famorycollab/biwex-store.git'
```
> **Ce qu'il faut dire à la prof si elle demande :**  
> *"Madame, vous voyez que la protection fonctionne au niveau du serveur GitHub lui-même (hook de rejet). Il est techniquement impossible de casser la production par accident."*

---

### D. Quelle est la seule façon légale d'envoyer du code sur main ?
Le chemin officiel et sécurisé est le suivant :
1. Développer sur sa branche personnelle : `feature/famory-toure` ou `feature/abdoul-traore`.
2. Ouvrir une Pull Request vers `dev` (validée par le **Pipeline 1** de Jenkins).
3. Fusionner sur `dev` (qui déclenche le **Pipeline 2** avec les tests complets et la parallélisation).
4. Une fois `dev` 100% stable, ouvrir une Pull Request de `dev` vers `main`.
5. Le binôme valide la PR sur GitHub, le code fusionne sur `main`.
6. On pose un **Tag Git** (ex: `v1.2.0`) qui déclenche le **Pipeline 3 (Release)**.

---

## 2. DÉTAIL COMPLET 2 : COMMENT CRÉER ET GÉRER LES TAGS GIT (vX.Y.Z) ?

### A. Qu'est-ce qu'un Tag Git ? (L'analogie à expliquer au professeur)
> 💡 **Analogie simple :**  
> *"Madame, une branche Git est comme une page de cahier où l'on écrit tous les jours : elle change et avance tout le temps. Un **Tag Git**, c'est comme un coup de tampon officiel ou un diplôme daté : il est posé sur un commit précis et ne bougera plus jamais dans l'histoire du projet. Un tag sert à marquer une **version livrable** que nos clients peuvent télécharger en toute confiance."*

---

### B. Comprendre le Versioning Sémantique (SemVer) : `vMAJEUR.MINEUR.PATCH`
Le sujet exige un tag au format Semantic Versioning (ex: `v1.2.0`). Voici comment expliquer la signification des 3 chiffres :
- **MAJEUR (Le premier chiffre, ex: v1.0.0 → v2.0.0) :**  
  Changement radical de l'application (ex: refonte complète de la base de données, suppression d'anciennes fonctionnalités). Le nouveau code n'est plus compatible avec l'ancien.
- **MINEUR (Le deuxième chiffre, ex: v1.0.0 → v1.1.0 ou v1.2.0) :**  
  Ajout d'une nouvelle fonctionnalité utile sans casser ce qui marchait avant (ex: nous avons ajouté la page de santé `/health` et l'API REST `/api/products` sans casser le panier d'achat).
- **PATCH (Le troisième chiffre, ex: v1.1.0 → v1.1.1) :**  
  Correction rapide d'un petit bug (ex: correction d'une faute de frappe ou d'un prix mal affiché).

---

### C. Méthode 1 : En Ligne de Commande Git (À montrer en direct au prof)

#### 1. Aller sur la branche principale et récupérer la dernière version :
```bash
git checkout main
git pull origin main
```

#### 2. Créer un Tag Annoté (Recommandé en entreprise) :
```bash
# Syntaxe : git tag -a <nom_du_tag> -m "<description_de_la_version>"
git tag -a v1.2.0 -m "Release officielle v1.2.0 - Catalogue 32 produits et API REST"
```
*(L'option `-a` signifie "annoté" : Git enregistre automatiquement qui a créé le tag, le jour, l'heure exacte et le message explicatif).*

#### 3. Pousser le Tag vers GitHub :
```bash
# Pour envoyer un tag précis :
git push origin v1.2.0

# OU pour envoyer tous les tags locaux créés :
git push origin --tags
```

#### 4. Commandes utiles de vérification :
```bash
# Lister tous les tags existants sur la machine :
git tag -l

# Afficher les informations détaillées du tag (auteur, date, commit ciblé) :
git show v1.2.0
```

#### 5. Comment supprimer un tag si on s'est trompé de numéro ?
```bash
# 1. Supprimer le tag sur sa machine locale :
git tag -d v1.2.0

# 2. Supprimer le tag distant sur GitHub :
git push origin --delete v1.2.0
```

---

### D. Méthode 2 : Directement sur le site Web GitHub

1. Ouvrez votre dépôt : `https://github.com/Famorycollab/biwex-store`
2. Dans le menu de droite, cliquez sur **Releases** (ou le lien *Tags*).
3. Cliquez sur le bouton **Draft a new release**.
4. Cliquez sur le menu déroulant **Choose a tag**, écrivez votre tag : `v1.2.0`, puis cliquez sur **Create new tag: v1.2.0 on publish**.
5. Cible (*Target*) : laissez sur la branche `main`.
6. Titre de la release : `Release v1.2.0 — Biwex Store Production`.
7. Dans la zone de texte, résumez les nouveautés du projet.
8. Cliquez sur le bouton vert **Publish release**.
9. **Conséquence immédiate :** GitHub notifie Jenkins, qui déclenche automatiquement le **Pipeline 3 (`Jenkinsfile-Tag`)** !

---

## 3. LES QUESTIONS « QU'EST-CE QUE... ? »

### Q1. Qu'est-ce que le DevOps ?
- **Réponse simple :** C'est la fusion entre le **Développement** (création du code) et les **Opérations** (mise en production et serveurs). Avant, les développeurs écrivaient le code et le jetaient aux administrateurs système sans se soucier du fonctionnement en production. Le DevOps casse ce mur grâce à l'automatisation, aux tests continus et à la collaboration.
- **Analogie :** C'est comme une cuisine de restaurant où les cuisiniers (Dev) et les serveurs (Ops) travaillent ensemble en temps réel avec des commandes automatisées, au lieu de se disputer quand un plat arrive froid.

---

### Q2. Qu'est-ce que l'Intégration Continue (CI) ?
- **Réponse simple :** C'est une pratique où chaque développeur intègre son travail régulièrement dans un dépôt commun (Git). À chaque envoi de code, un serveur automatisé (Jenkins) récupère le code, le compile et exécute des tests automatiques pour détecter les bugs immédiatement.
- **Analogie :** C'est le contrôle technique d'une voiture : dès qu'une nouvelle pièce est fabriquée, on la teste tout de suite pour vérifier qu'elle ne fait pas caler le moteur.

---

### Q3. Quelle est la différence entre Livraison Continue (Continuous Delivery) et Déploiement Continu (Continuous Deployment) ?
- **Réponse simple :**
  - **Livraison Continue :** Le pipeline prépare automatiquement un livrable prêt pour la production (notre image Docker `biwex-store:v1.2.0`), mais un humain doit cliquer sur un bouton pour l'installer en production.
  - **Déploiement Continu :** Dès que les tests sont au vert, l'application est envoyée sur les serveurs de production chez les clients **100% automatiquement**, sans aucune intervention humaine.
  - *Dans notre projet, notre Pipeline 3 réalise la Livraison Continue.*

---

### Q4. Qu'est-ce qu'un Pipeline Jenkins et qu'est-ce qu'un Jenkinsfile ?
- **Réponse simple :**
  - Un **Jenkinsfile** est un fichier texte écrit en langage Groovy qui contient la liste de toutes les instructions à exécuter (télécharger le code, créer le conteneur, tester, archiver).
  - C'est ce qu'on appelle le **Pipeline-as-Code** : au lieu de cliquer dans des menus Jenkins, la recette du déploiement est stockée dans un fichier texte dans Git, versionnée et partagée entre les développeurs.
  - Le **Pipeline** est la chaîne de montage visuelle dans Jenkins où l'on voit chaque étape s'allumer en vert ou en rouge.

---

### Q5. Qu'est-ce que Docker et qu'est-ce qu'un conteneur ?
- **Réponse simple :** Docker est une plateforme qui permet d'emballer une application et tout ce dont elle a besoin pour tourner (Python, bibliothèques, base de données, configuration) dans une boîte virtuelle légère appelée **conteneur**.
- **Avantage clé :** Il élimine la phrase classique des développeurs : *"Mais pourtant, ça marchait sur ma machine !"*. Avec Docker, l'application tourne exactement de la même manière sur l'ordinateur de Famory, sur celui d'Abdoul, sur le serveur Jenkins et sur le serveur de production.

---

### Q6. Quelle est la différence entre une Image Docker et un Conteneur Docker ?
- **Réponse simple :**
  - L'**Image Docker** est le moule passif, le fichier figé (la recette de gâteau ou la classe en programmation orientée objet).
  - Le **Conteneur** est l'instance active en train de tourner en mémoire (le gâteau cuit ou l'objet instancié en mémoire).
  - À partir d'une seule image `biwex-store:latest`, on peut lancer 10 conteneurs sur des ports différents.

---

### Q7. Quelle est la différence entre un Conteneur Docker et une Machine Virtuelle (VM) ?
- **Réponse simple :**
  - Une **Machine Virtuelle** (ex: VirtualBox, VMware) embarque un système d'exploitation complet (plusieurs Go), est lente à démarrer (1 à 2 minutes) et consomme beaucoup de mémoire RAM.
  - Un **Conteneur Docker** partage le noyau Linux de la machine hôte. Il ne pèse que quelques dizaines de Mégaoctets et démarre en moins d'une seconde.

---

### Q8. Qu'est-ce qu'un Dockerfile Multi-Stage ? Pourquoi l'avoir utilisé ?
- **Réponse simple :** C'est un Dockerfile divisé en deux étapes distinctes :
  1. **Stage 1 (Builder) :** On installe les outils lourds de compilation (gcc, pip, cache) pour créer notre environnement virtuel Python dans `/opt/venv`.
  2. **Stage 2 (Runtime) :** On repart d'une image Linux Alpine/Slim propre et vide. On copie uniquement les fichiers nécessaires et le dossier `/opt/venv`.
- **Résultat concret :** La taille de l'image finale passe de **~800 Mo à seulement 60 Mo** ! Elle se télécharge plus vite, consomme moins de disque et est beaucoup plus sécurisée car elle ne contient aucun compilateur inutile qu'un pirate pourrait exploiter.

---

### Q9. Qu'est-ce qu'un Smoke Test ("Test de fumée") ?
- **Réponse simple :** C'est un test rapide de santé minimale. On lance l'application dans un conteneur et on lui envoie une requête HTTP sur sa page d'accueil (`http://localhost:5000/`) :
  - Si le serveur répond avec le code HTTP **200 (OK)** en moins de 10 secondes, le test est **PASSED (Réussi)**.
  - S'il y a une erreur 500 ou si le serveur ne démarre pas, le test est **FAILED (Échoué)**.
- **Origine du nom :** En électronique, quand on répare un circuit, on le branche : s'il n'y a pas de fumée qui s'échappe, on peut passer aux tests plus détaillés !

---

### Q10. Qu'est-ce qu'un Artefact dans Jenkins ? Qu'est-ce que le fingerprinting ?
- **Réponse simple :**
  - Un **Artefact** est un fichier produit pendant le build qu'on décide de sauvegarder définitivement dans Jenkins (ex: nos rapports de test `pipeline-report.txt`, `smoke-test.txt` ou le `release-manifest.txt`).
  - Le **fingerprinting** consiste à calculer une empreinte numérique unique (hachage MD5) sur le fichier. Cela prouve de manière infalsifiable qu'aucun rapport n'a été modifié ou altéré après la fin du build.

---

### Q11. Qu'est-ce que l'utilisateur non-root dans Docker ? (Sécurité)
- **Réponse simple :** Par défaut, Docker exécute l'application avec les privilèges administrateur suprême (`root`). Si notre application web contient une faille de sécurité, un attaquant pourrait prendre le contrôle total du conteneur.
- **Notre solution :** Dans le Dockerfile, nous avons créé un utilisateur ordinaire avec `RUN useradd appuser` et activé `USER appuser`. Si l'application est compromise, l'attaquant ne dispose d'aucun droit système (principe de sécurité du moindre privilège).

---

### Q12. Qu'est-ce qu'une Pull Request (PR) ?
- **Réponse simple :** Une Pull Request (demande d'intégration) est une demande officielle qu'un développeur soumet à son équipe pour dire : *"J'ai terminé ma fonctionnalité sur ma branche personnelle, voici mon code. Relisez-le, vérifiez qu'il passe les tests Jenkins, et si vous êtes d'accord, fusionnez-le dans la branche principale."*

---

### Q13. Qu'est-ce que le fichier `.dockerignore` ?
- **Réponse simple :** C'est un fichier qui fonctionne exactement comme `.gitignore`. Il indique à Docker d'ignorer certains dossiers ou fichiers lors de la commande `COPY . .` (ex: `.git`, `__pycache__`, fichiers `.tmp`, `.env`). Cela évite d'alourdir inutilement l'image Docker et empêche d'envoyer des fichiers secrets dans l'image.

---

### Q14. Qu'est-ce que Docker Compose ?
- **Réponse simple :** C'est un outil qui permet de décrire et de lancer plusieurs conteneurs interconnectés à l'aide d'un seul fichier `docker-compose.yml`. Dans notre projet, nous avons configuré l'application Flask connectée à une base de données PostgreSQL avec un réseau privé virtuel et un volume de persistance des données.

---

### Q15. Qu'est-ce que l'endpoint `/health` dans votre application ?
- **Réponse simple :** C'est une route HTTP dédiée (`http://localhost:5000/health`) qui renvoie un document JSON indiquant l'état de santé en temps réel de notre boutique : temps de fonctionnement, nombre de produits dans la base (32 produits), état de la base de données SQLite/PostgreSQL et mémoire. C'est l'endpoint utilisé par les outils de surveillance professionnels (Prometheus, Kubernetes, Datadog).

---

## 4. LES QUESTIONS « COMMENT... ? »

### Q1. Comment avez-vous structuré vos 3 pipelines Jenkins et pourquoi 3 fichiers distincts ?
- **Réponse :** Nous avons créé 3 pipelines spécialisés pour répondre exactement aux exigences du cycle de vie DevOps :
  1. `Jenkinsfile-PR` (**Pipeline PR**) : Déclenché lorsqu'un développeur ouvre une PR vers `dev`. Il vérifie que la cible est bien `dev`, build l'image et exécute le smoke test pour autoriser ou refuser la fusion.
  2. `Jenkinsfile` (**Pipeline Dev**) : Déclenché lors d'un push sur `dev`. Il effectue la compilation complète, teste en **parallèle** la compatibilité avec Python 3.11 et Python 3.12, et génère les rapports de build.
  3. `Jenkinsfile-Tag` (**Pipeline Release**) : Déclenché uniquement lors de la création d'un tag `vX.Y.Z`. Il vérifie la syntaxe SemVer, produit l'image de release officielle et archive le manifeste de livraison scellé.
  *Pourquoi 3 fichiers ?* Pour respecter le principe de séparation des responsabilités : on ne va pas créer une release officielle à chaque petit commit sur une PR !

---

### Q2. Comment fonctionnent les 6 étapes (Stages) obligatoires dans vos pipelines ?
- **Réponse :** Chaque pipeline respecte scrupuleusement les 6 étapes demandées :
  1. **Stage 1 (Checkout) :** Jenkins clone la branche Git exacte avec ses identifiants.
  2. **Stage 2 (Setup / Prepare) :** Vérification des prérequis (version de Docker, validation des variables d'environnement et de la conformité du tag ou de la PR).
  3. **Stage 3 (Build) :** Construction de l'image Docker avec `docker build` (et parallélisation multi-versions dans le pipeline Dev).
  4. **Stage 4 (Run Container) :** Lancement d'un conteneur temporaire isolé sur un port dédié avec un nom unique incluant `${BUILD_NUMBER}`.
  5. **Stage 5 (Smoke Test) :** Exécution du script Python qui vérifie la réponse HTTP 200 du conteneur en direct.
  6. **Stage 6 (Archive Artifacts) :** Sauvegarde des rapports et manifestes horodatés avec empreinte numérique.
  - **Bloc Post-Action :** Exécution automatique de `docker rm -f` pour détruire le conteneur et libérer le port, quoi qu'il arrive.

---

### Q3. Comment avez-vous implémenté la Parallélisation dans le Pipeline Dev ?
- **Réponse :** Dans le Stage 3 de notre `Jenkinsfile`, nous utilisons la directive déclarative `parallel { ... }` :
  - Une branche exécute la commande : `docker build --build-arg PYTHON_VERSION=3.11 -t biwex-store:dev-py311 .`
  - En même temps, une deuxième branche exécute : `docker build --build-arg PYTHON_VERSION=3.12 -t biwex-store:dev-py312 .`
  *Bénéfice :* On divise le temps d'attente par deux et on garantit que notre application fonctionnera chez un client sous Python 3.11 ou sous Python 3.12.

---

### Q4. Comment évitez-vous qu'un conteneur ne bloque le port pour les builds suivants ?
- **Réponse :** Grâce à deux sécurités :
  1. Chaque conteneur porte un nom unique contenant le numéro du build Jenkins : `biwex-test-${BUILD_NUMBER}`.
  2. Dans le bloc final du Jenkinsfile :
     ```groovy
     post {
         always {
             bat "docker rm -f biwex-test-${BUILD_NUMBER} 2>nul || exit 0"
         }
     }
     ```
     Le mot-clé `always` garantit que même si le test échoue ou que le pipeline plante, Docker nettoie et supprime le conteneur automatiquement.

---

### Q5. Comment le script de Smoke Test gère-t-il le temps de démarrage de l'application ?
- **Réponse :** Un conteneur met entre 1 et 3 secondes pour initialiser Python, charger la base de données et lancer Gunicorn. Si on teste trop tôt, le test échouerait à tort.  
Dans notre script `scripts/smoke_test.py`, nous avons mis une boucle de retry :
```python
max_tentatives = 15
delai_entre_essais = 2  # secondes
# Le script tente jusqu'à 15 fois (30 secondes max). Dès qu'il reçoit HTTP 200, il s'arrête immédiatement avec succès.
```
Si au bout des 15 tentatives le serveur ne répond toujours pas, le script retourne le code d'erreur `sys.exit(1)`, ce qui fait passer le stage Jenkins au rouge.

---

### Q6. Comment avez-vous prouvé la contribution individuelle de Famory et d'Abdoul dans Git ?
- **Réponse :**
  - **Famory TOURE** a développé sur la branche `feature/famory-toure` avec son e-mail GitHub officiel (`tourefamory5@gmail.com`). Il a conçu le Dockerfile multi-stage, le catalogue de 32 produits et le Pipeline 2 avec parallélisation.
  - **Abdoul TRAORE** a développé sur la branche `feature/abdoul-traore` avec son e-mail GitHub officiel (`a21traore06@gmail.com`). Il a conçu le Pipeline 1 (PR), le Pipeline 3 (Tag Release), l'API REST JSON et Docker Compose.
  - La commande `git log --pretty=format:"%h - %an (%ae) : %s"` affiche clairement chaque commit signé par son auteur réel.

---

### Q7. Comment avez-vous configuré les variables d'environnement dans Docker ?
- **Réponse :** Nous utilisons l'instruction `ENV` dans le Dockerfile :
  ```dockerfile
  ENV FLASK_ENV=production
  ENV PORT=5000
  ENV PYTHONUNBUFFERED=1
  ```
  `PYTHONUNBUFFERED=1` est très important en DevOps : il force Python à afficher ses logs immédiatement dans la console Jenkins sans les retenir dans un buffer mémoire.

---

### Q8. Comment vérifier que votre image Docker fait bien ~60 Mo ?
- **Réponse :** Il suffit de taper la commande suivante dans le terminal :
  ```bash
  docker images biwex-store
  ```
  Docker affiche la colonne **SIZE** : l'image pèse environ **63 Mo** grâce à l'image de base `python:3.11-slim` et au multi-stage build.

---

## 5. DÉMONSTRATION « PASSED / FAILED » DEVANT LA PROF

Le sujet d'examen de Mme SAKHRAWI précise formellement :  
*« Démonstration d'un build passed/failed »*. Voici la manipulation exacte à faire le jour J.

### 🔴 SCÉNARIO 1 : Démonstration du Build ÉCHOUÉ (FAILED)

1. Ouvrez le fichier `scripts/smoke_test.py`.
2. À la ligne 20, modifiez l'URL pour pointer vers un faux port (ex: `9999`) :
   ```python
   # AU LIEU DE :
   url = "http://127.0.0.1:5000/"
   # METTEZ VOLONTAIREMENT :
   url = "http://127.0.0.1:9999/"
   ```
3. Sauvegardez le fichier et lancez le build dans Jenkins (ou faites un push sur `dev`).
4. **Ce qui se passe sur l'écran Jenkins :**
   - Stage 1 (Checkout) : 🟢 VERT
   - Stage 2 (Setup) : 🟢 VERT
   - Stage 3 (Build Docker) : 🟢 VERT
   - Stage 4 (Run Container) : 🟢 VERT
   - **Stage 5 (Smoke Test) : 🔴 ROUGE (FAILED)** — Le test boucle pendant 30 secondes, ne trouve rien sur le port 9999, et s'arrête avec le code d'erreur 1.
   - Stage 6 (Archive) : ⚪ Ignoré (SKIPPED).
5. **Ce que vous dites à Mme SAKHRAWI :**  
   *"Madame, voici notre filet de sécurité DevOps en action : le smoke test a détecté qu'un service essentiel ne répondait pas. Jenkins a immédiatement interrompu le pipeline et mis le stage en rouge. Grâce à cela, aucune version défectueuse ne peut être livrée aux utilisateurs !"*

---

### 🟢 SCÉNARIO 2 : Démonstration du Build RÉUSSI (PASSED)

1. Remettez l'URL correcte dans `scripts/smoke_test.py` :
   ```python
   url = "http://127.0.0.1:5000/"
   ```
2. Sauvegardez et relancez le build.
3. **Ce qui se passe sur l'écran Jenkins :**
   - Toutes les 6 étapes s'allument en **VERT (SUCCESS)** l'une après l'autre.
   - Ouvrez la console Jenkins : vous voyez les messages `HTTP 200 OK - Test RÉUSSI`.
   - Cliquez sur **Build Artifacts** à gauche : montrez les fichiers `pipeline-report.txt` et `smoke-test.txt` créés et archivés avec leur empreinte numérique.
4. **Ce que vous dites à Mme SAKHRAWI :**  
   *"Madame, après correction de l'anomalie, le pipeline vérifie à nouveau automatiquement l'intégralité du projet. Tout est validé, les artefacts sont archivés avec leur empreinte MD5, et l'application est prête pour la production."*

---

## 6. SCÉNARIO CHRONOMÉTRÉ DE SOUTENANCE (10 MINUTES CHRONO)

Voici le découpage exact de votre présentation orale pour être parfaitement synchronisés et impressionner le jury :

| Temps | Intervenant | Contenu de la présentation | Support / Écran à montrer |
| :--- | :--- | :--- | :--- |
| **00:00 - 01:30** | **Famory** | • Salutations et présentation du binôme (3LIG ISG Sousse).<br>• Présentation de l'application **Biwex Store** (Flask, e-commerce, catalogue 38 produits, panier, API REST).<br>• Présentation de la stratégie Git : les 3 niveaux de branches (`main` protégée, `dev` d'intégration, branches `feature`). | Diapositive d'accueil + Schéma de l'architecture Git. |
| **01:30 - 03:00** | **Abdoul** | • Présentation du **Dockerfile Multi-Stage** : expliquer pourquoi on a séparé *Builder* et *Runtime* (gain de taille de 800 Mo à 60 Mo).<br>• Explication de la sécurité avec l'utilisateur non-root (`appuser`).<br>• Présentation du **Pipeline 1 (PR)** qui empêche de fusionner sans tests. | Diapositive Dockerfile + Page GitHub avec les 2 branches de feature. |
| **03:00 - 05:00** | **Famory** | • **Démonstration en direct sur Jenkins :** Ouvrir le **Pipeline 2 (Dev)**.<br>• Montrer les 6 stages demandés par le sujet.<br>• Insister sur la **parallélisation** au Stage 3 (build simultané Python 3.11 et Python 3.12).<br>• Montrer les artefacts archivés (`pipeline-report.txt`). | Écran Jenkins en direct sur `http://localhost:8083`. |
| **05:00 - 06:45** | **Abdoul** | • Démonstration du **Pipeline 3 (Release Tag)** : expliquer le Versioning Sémantique (`v1.6.0`).<br>• **Démonstration FAILED vs PASSED** : montrer comment Jenkins détecte l'erreur et protège la production. | Écran Jenkins (Stage rouge puis vert). |
| **06:45 - 08:00** | **Famory** | • **Le 4ème Pipeline — DevSecOps Nightly :** Présenter `Jenkinsfile-Nightly-Security`.<br>• Expliquer les 4 audits : analyse statique AST, scan de conformité `requirements.txt`, sécurité conteneur Dockerfile et intégrité SQLite (38 produits).<br>• Montrer le rapport d'audit archivé (`security-audit-report.txt`). | Écran Jenkins (Pipeline Nightly) + Diapositive 10. |
| **08:00 - 09:15** | **Famory & Abdoul** | • Lancement du conteneur en direct.<br>• Ouverture du site web dans le navigateur (`http://localhost:5000`).<br>• Démonstration de l'endpoint de métriques en direct : `http://localhost:5000/health`. | Navigateur web avec Biwex Store et JSON de santé. |
| **09:15 - 10:00** | **Famory & Abdoul** | • Conclusion : rappel des bénéfices du DevOps & DevSecOps (zéro interruption de service, rapidité de livraison, sécurité continue).<br>• Remerciements à Mme SAKHRAWI et ouverture de la session de questions. | Diapositive finale avec contacts GitHub et remerciements. |

---

## 7. CONSEILS EN OR POUR OBTENIR LA NOTE MAXIMALE

1. **Ne lisez jamais vos diapositives :** Regardez l'enseignante dans les yeux et parlez avec enthousiasme.
2. **Utilisez le bon vocabulaire professionnel :**
   - Dites *"Pipeline-as-Code"* plutôt que *"mon script Jenkins"*.
   - Dites *"Image allégée multi-stage"* plutôt que *"petite image"*.
   - Dites *"Principe du moindre privilège"* pour l'utilisateur non-root.
   - Dites *"Versioning Sémantique"* plutôt que *"le numéro de version"*.
3. **Restez calmes si une question piège arrive :**  
   Si la prof demande quelque chose que vous n'avez pas prévu, commencez par : *"C'est une excellente question, Madame. Dans notre architecture, nous avons privilégié la simplicité et la robustesse..."*.
4. **Montrez que vous êtes un vrai binôme soudé :**  
   Ne coupez pas la parole à votre camarade. Quand Famory parle, Abdoul manipule la souris pour montrer la bonne page, et inversement !
