"""
============================================================
 SCRIPT DE SMOKE TEST (TEST DE FUMÉE)
 Projet : Biwex Store - 3LIG ISG Sousse
 Binôme : Famory TOURE & Abdoul TRAORE

 NOTION FACILE DU COURS À EXPLIQUER À LA PROF :
 Un "Smoke Test" est le test le plus simple et le plus rapide au monde.
 Analogie : Quand on branche une télévision neuve pour la première fois,
 on vérifie juste que le voyant rouge s'allume et qu'il n'y a pas de fumée.
 Ici, c'est pareil : on envoie une requête HTTP sur la page d'accueil.
 - Si le serveur répond avec le code HTTP 200 (OK) ➔ C'est PASSED (Réussi).
 - Si le serveur ne répond pas ou renvoie une erreur ➔ C'est FAILED (Échoué).
"""

import sys
import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# 1. Adresse du site à tester (par défaut http://127.0.0.1:5000/)
url_a_tester = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000/"

# 2. Temps d'attente maximum : si le site ne répond pas en 10 secondes, on arrête
TEMPS_MAXIMUM = 10

print("=" * 55)
print("  TEST DE FONCTIONNEMENT RAPIDE (SMOKE TEST)")
print(f"  Site testé : {url_a_tester}")
print("=" * 55)

try:
    # 3. On tente d'ouvrir l'adresse du site comme le ferait un navigateur web
    with urlopen(url_a_tester, timeout=TEMPS_MAXIMUM) as reponse:
        # Code HTTP renvoyé par le serveur (200 = Tout fonctionne bien)
        code_recu = reponse.status
        print(f"[Succès] Connexion établie avec le serveur")
        print(f"[Code HTTP] Code de statut reçu : {code_recu}")

        # On lit les premiers caractères pour vérifier qu'il y a bien du code HTML de notre site
        debut_page = reponse.read(300).decode('utf-8', errors='ignore')
        if "<html" in debut_page.lower() or "<!doctype" in debut_page.lower():
            print("[Contenu] Page web HTML valide détectée.")

        # VERDICT DU TEST :
        if code_recu == 200:
            print("\n--> RÉSULTAT : PASSED (TEST RÉUSSI) ✅")
            print("L'application fonctionne parfaitement !")
            # sys.exit(0) signale à Jenkins que l'étape est VERTE
            sys.exit(0)
        else:
            print("\n--> RÉSULTAT : FAILED (TEST ÉCHOUÉ) ❌")
            # sys.exit(1) signale à Jenkins que l'étape est ROUGE
            sys.exit(1)

except HTTPError as erreur:
    print(f"[Erreur Serveur] Le serveur a renvoyé l'erreur : {erreur.code}")
    print("\n--> RÉSULTAT : FAILED ❌")
    sys.exit(1)

except URLError as erreur:
    print(f"[Erreur Connexion] Impossible de joindre le site : {erreur.reason}")
    print("\n--> RÉSULTAT : FAILED ❌")
    sys.exit(1)

except Exception as autre_erreur:
    print(f"[Erreur Imprévue] : {autre_erreur}")
    print("\n--> RÉSULTAT : FAILED ❌")
    sys.exit(1)
