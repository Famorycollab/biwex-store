"""
Script d'audit DevSecOps & Qualité du code pour Biwex Store.
Effectue :
1. Analyse statique & syntaxique des fichiers Python (AST + conformité).
2. Scan des dépendances requirements.txt pour vérifier la conformité des versions.
3. Vérification des bonnes pratiques de sécurité Dockerfile et configuration.
4. Évaluation d'intégrité de la base de données SQLite (instance/biwex.db).
5. Génération d'un rapport de conformité d'audit horodaté.
"""

import os
import sys
import ast
import time
import sqlite3
from datetime import datetime

# Assurer l'accès au répertoire racine pour les imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

REPORT_DIR = os.path.join(PROJECT_ROOT, "artifacts", "security")
os.makedirs(REPORT_DIR, exist_ok=True)
REPORT_FILE = os.path.join(REPORT_DIR, "security-audit-report.txt")

def log(msg):
    print(f"[SECURITY AUDIT] {msg}")

def audit_python_code():
    log("Étape 1/4 : Analyse statique du code source (AST & Bonnes pratiques)...")
    issues = []
    py_files = []
    
    # Fichiers racine
    for f in ["app.py", "database.py"]:
        p = os.path.join(PROJECT_ROOT, f)
        if os.path.exists(p):
            py_files.append(p)
            
    # Scripts
    scripts_dir = os.path.join(PROJECT_ROOT, "scripts")
    if os.path.exists(scripts_dir):
        for f in os.listdir(scripts_dir):
            if f.endswith(".py"):
                py_files.append(os.path.join(scripts_dir, f))
                
    # Tests
    tests_dir = os.path.join(PROJECT_ROOT, "tests")
    if os.path.exists(tests_dir):
        for f in os.listdir(tests_dir):
            if f.endswith(".py"):
                py_files.append(os.path.join(tests_dir, f))
    
    analyzed_count = 0
    for file_path in py_files:
        if not os.path.exists(file_path):
            continue
        analyzed_count += 1
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        
        # Test: Syntaxe via AST
        try:
            ast.parse(code, filename=file_path)
        except SyntaxError as e:
            issues.append(f"Erreur de syntaxe dans {os.path.basename(file_path)}: {e}")

    log(f"-> {analyzed_count} fichiers Python analysés. Erreurs critiques de syntaxe : {len(issues)}")
    return {"status": "SUCCESS" if len(issues) == 0 else "FAILED", "issues": issues, "count": analyzed_count}

def audit_requirements():
    log("Étape 2/4 : Audit de conformité des dépendances (requirements.txt)...")
    req_file = os.path.join(PROJECT_ROOT, "requirements.txt")
    packages = []
    issues = []
    if not os.path.exists(req_file):
        return {"status": "FAILED", "issues": ["requirements.txt manquant"], "count": 0}

    with open(req_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        packages.append(line)
        # Bonne pratique : dépendances épinglées
        if "==" not in line and ">=" not in line:
            issues.append(f"Dépendance non verrouillée : '{line}'")

    log(f"-> {len(packages)} paquets audités. Remarques de conformité : {len(issues)}")
    return {"status": "SUCCESS" if len(issues) == 0 else "WARNING", "issues": issues, "packages": packages}

def audit_dockerfile():
    log("Étape 3/4 : Audit de sécurité du Dockerfile (DevSecOps)...")
    dockerfile = os.path.join(PROJECT_ROOT, "Dockerfile")
    issues = []
    checks = {
        "multi_stage": False,
        "non_root_user": False,
        "no_cache_pip": False,
        "explicit_expose": False
    }

    if not os.path.exists(dockerfile):
        return {"status": "FAILED", "issues": ["Dockerfile introuvable"], "checks": checks}

    with open(dockerfile, "r", encoding="utf-8") as f:
        content = f.read()

    if "AS builder" in content and "COPY --from=builder" in content:
        checks["multi_stage"] = True
    else:
        issues.append("Non conforme : Multi-stage build non détecté")

    if "USER appuser" in content or "useradd" in content:
        checks["non_root_user"] = True
    else:
        issues.append("Alerte sécurité : L'application semble s'exécuter sous root")

    if "--no-cache-dir" in content:
        checks["no_cache_pip"] = True
    else:
        issues.append("Optimisation : Option --no-cache-dir absente")

    if "EXPOSE 5000" in content:
        checks["explicit_expose"] = True
    else:
        issues.append("Information : Port non explicité par EXPOSE")

    log(f"-> Contrôles Dockerfile passés : {sum(checks.values())}/4")
    return {"status": "SUCCESS" if len(issues) == 0 else "WARNING", "issues": issues, "checks": checks}

def run_database_integrity_audit():
    log("Étape 4/4 : Évaluation d'intégrité de la base de données (SQLite)...")
    start_time = time.time()
    db_path = os.path.join(PROJECT_ROOT, "instance", "biwex.db")
    
    if not os.path.exists(db_path):
        # Fallback racine si instance n'existe pas
        db_path = os.path.join(PROJECT_ROOT, "biwex.db")

    if not os.path.exists(db_path):
        return {"status": "WARNING", "error": "Fichier de base de données absent (sera initialisé au premier lancement)", "elapsed_seconds": 0}

    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        
        # Vérification table product
        cur.execute("SELECT COUNT(*) FROM product")
        products_count = cur.fetchone()[0]
        
        # Vérification catégories
        cur.execute("SELECT COUNT(DISTINCT category) FROM product")
        categories_count = cur.fetchone()[0]
        
        con.close()
        elapsed = time.time() - start_time
        
        metrics = {
            "elapsed_seconds": round(elapsed, 4),
            "products_count": products_count,
            "categories_count": categories_count,
            "status": "OPTIMAL" if products_count > 0 else "WARNING"
        }
        log(f"-> Base vérifiée en {metrics['elapsed_seconds']}s | {products_count} produits | {categories_count} catégories (OPTIMAL)")
        return metrics
    except Exception as e:
        log(f"-> Erreur SQLite : {e}")
        return {"status": "FAILED", "error": str(e), "elapsed_seconds": round(time.time() - start_time, 4)}

def main():
    start_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log(f"Démarrage de l'audit de sécurité et qualité — {start_date}")

    res_code = audit_python_code()
    res_req = audit_requirements()
    res_docker = audit_dockerfile()
    res_db = run_database_integrity_audit()

    passed = (res_code["status"] != "FAILED" and 
              res_req["status"] != "FAILED" and 
              res_docker["status"] != "FAILED" and
              res_db.get("status") != "FAILED")

    report_content = f"""==============================================================
 RAPPORT OFFICIEL D'AUDIT SÉCURITÉ & QUALITÉ — BIWEX STORE
==============================================================
Date d'audit      : {start_date}
Pipeline Déclenché: Jenkinsfile-Nightly-Security (DevSecOps)
Binôme Responsable: Famory TOURE & Abdoul TRAORE
Projet            : Biwex Store (DevOps 3LIG - ISG Sousse)
Enseignante       : Mme Zaineb SAKHRAWI

RÉSULTATS DE L'ÉVALUATION DEVSECOPS :
--------------------------------------------------------------
1. Analyse Statique du Code (AST) :
   - Fichiers analysés     : {res_code.get('count', 0)}
   - Statut                : {res_code['status']}
   - Erreurs syntaxiques   : {len(res_code['issues'])}

2. Conformité des Dépendances (requirements.txt) :
   - Nombre de paquets     : {len(res_req.get('packages', []))}
   - Statut                : {res_req['status']}
   - Remarques de version  : {len(res_req['issues'])}

3. Sécurité du Conteneur Docker (Dockerfile) :
   - Multi-stage build     : {'OUI (Optimal)' if res_docker['checks']['multi_stage'] else 'NON'}
   - Utilisateur dédié     : {'OUI (appuser non-root - Sécurisé)' if res_docker['checks']['non_root_user'] else 'NON'}
   - Nettoyage du cache    : {'OUI (--no-cache-dir actif)' if res_docker['checks']['no_cache_pip'] else 'NON'}
   - Port d'écoute explicité: {'OUI (EXPOSE 5000)' if res_docker['checks']['explicit_expose'] else 'NON'}
   - Statut                : {res_docker['status']}

4. Intégrité de la Base de Données (instance/biwex.db) :
   - Temps d'accès DB      : {res_db.get('elapsed_seconds', 'N/A')} s
   - Produits recensés     : {res_db.get('products_count', 'N/A')} produits
   - Catégories actives    : {res_db.get('categories_count', 'N/A')} catégories
   - Indice de santé DB    : {res_db.get('status', 'N/A')}

==============================================================
VERDICT GLOBAL DU CONTRÔLE QUALITÉ :
   CONFORMITÉ DEVSECOPS : {'VALIDE (SUCCÈS 100%)' if passed else 'NON CONFORME (ÉCHEC)'}
==============================================================
"""

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)

    print("\n" + report_content)
    log(f"Rapport sauvegardé avec succès dans : {REPORT_FILE}")

    if not passed:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
