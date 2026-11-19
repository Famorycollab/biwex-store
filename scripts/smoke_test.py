"""
╔══════════════════════════════════════════════════════╗
║          SMOKE TEST - BIWEX STORE                   ║
║                                                      ║
║  Rôle : Vérification rapide "go/no-go" de l'appli   ║
║  Principe : Envoie une requête HTTP GET et vérifie   ║
║             que le code de retour est 200 (OK)       ║
║                                                      ║
║  Résultat : PASSED (exit 0) ou FAILED (exit 1)       ║
║                                                      ║
║  Usage :                                             ║
║    python smoke_test.py http://127.0.0.1:5000/       ║
║    python smoke_test.py http://localhost:5000/        ║
╚══════════════════════════════════════════════════════╝

Qu'est-ce qu'un Smoke Test ?
  Un "smoke test" (test de fumée) est le test le plus basique qu'on
  puisse faire sur une application : on vérifie qu'elle "ne prend pas
  feu" dès le démarrage. Si ce test échoue, inutile de lancer des
  tests plus complexes.

  Dans notre pipeline CI/CD :
  - Smoke PASSED → le build peut continuer / la PR peut être mergée
  - Smoke FAILED  → le build est bloqué, le développeur doit corriger
"""

import sys
import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# ── CONFIGURATION ───────────────────────────────────────────────
# URL par défaut si aucun argument n'est fourni
DEFAULT_URL = "http://127.0.0.1:5000/"

# Timeout de la requête HTTP en secondes
# (au-delà, on considère que l'application ne répond pas)
HTTP_TIMEOUT = 10

# Codes HTTP considérés comme "succès" (l'application fonctionne)
# 200 = OK, 301/302 = Redirect (acceptable pour une homepage)
SUCCESS_CODES = [200, 301, 302]

# ── RÉCUPÉRATION DE L'URL ────────────────────────────────────────
# L'URL est passée en argument de la ligne de commande
# Exemple : python smoke_test.py http://127.0.0.1:5000/
url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

# ── EN-TÊTE DU RAPPORT ───────────────────────────────────────────
print("=" * 55)
print("  BIWEX STORE - SMOKE TEST")
print("=" * 55)
print(f"  URL testée    : {url}")
print(f"  Timeout HTTP  : {HTTP_TIMEOUT}s")
print(f"  Heure de test : {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 55)
print()

# ── EXÉCUTION DU TEST ────────────────────────────────────────────
try:
    # Envoi de la requête HTTP GET vers l'application
    # Si le serveur Flask/Gunicorn répond → connexion établie
    with urlopen(url, timeout=HTTP_TIMEOUT) as response:
        status = response.status
        content_type = response.headers.get('Content-Type', 'inconnu')
        content_length = response.headers.get('Content-Length', 'inconnu')

        print(f"[HTTP] Connexion établie")
        print(f"[HTTP] Code de statut    : {status}")
        print(f"[HTTP] Content-Type      : {content_type}")
        print(f"[HTTP] Content-Length    : {content_length}")
        print()

        # Vérification du contenu minimal de la page
        # On lit les 500 premiers octets pour vérifier que Flask répond
        body_preview = response.read(500).decode('utf-8', errors='ignore')

        # Vérification : la réponse doit contenir du HTML
        if '<html' in body_preview.lower() or '<!doctype' in body_preview.lower():
            print("[HTML] Contenu HTML détecté dans la réponse  ✓")
        else:
            print("[HTML] Avertissement : pas de balise HTML détectée")
            print(f"[HTML] Aperçu contenu : {body_preview[:100]!r}")

        print()

        # ── VERDICT ─────────────────────────────────────────
        if status in SUCCESS_CODES:
            print("=" * 55)
            print(f"  RÉSULTAT : PASSED  ✅")
            print(f"  Code HTTP {status} → Application opérationnelle")
            print("=" * 55)
            sys.exit(0)   # Code 0 = succès → Jenkins marque le stage vert
        else:
            print("=" * 55)
            print(f"  RÉSULTAT : FAILED  ❌")
            print(f"  Code HTTP {status} non attendu")
            print("=" * 55)
            sys.exit(1)   # Code 1 = échec → Jenkins marque le stage rouge

except HTTPError as e:
    # Le serveur a répondu mais avec une erreur HTTP (4xx, 5xx)
    print(f"[ERREUR] Erreur HTTP : {e.code} {e.reason}")
    print(f"[INFO]  L application répond mais retourne une erreur serveur")
    print()
    print("=" * 55)
    print("  RÉSULTAT : FAILED  ❌")
    print(f"  Erreur HTTP {e.code}: {e.reason}")
    print("=" * 55)
    sys.exit(1)

except URLError as e:
    # Impossible de se connecter (application non démarrée, mauvais port...)
    print(f"[ERREUR] Connexion impossible : {e.reason}")
    print(f"[INFO]  L application n est peut-etre pas encore démarrée")
    print()
    print("=" * 55)
    print("  RÉSULTAT : FAILED  ❌")
    print(f"  Connexion refusée ou timeout")
    print("=" * 55)
    sys.exit(1)

except TimeoutError:
    # Le serveur n'a pas répondu dans le délai imparti
    print(f"[ERREUR] Timeout après {HTTP_TIMEOUT} secondes")
    print("[INFO]  L application est trop lente ou ne répond pas")
    print()
    print("=" * 55)
    print("  RÉSULTAT : FAILED  ❌")
    print(f"  Timeout ({HTTP_TIMEOUT}s dépassé)")
    print("=" * 55)
    sys.exit(1)

except Exception as e:
    # Toute autre erreur imprévue
    print(f"[ERREUR] Erreur inattendue : {type(e).__name__}: {e}")
    print()
    print("=" * 55)
    print("  RÉSULTAT : FAILED  ❌")
    print(f"  Erreur inattendue : {e}")
    print("=" * 55)
    sys.exit(1)
