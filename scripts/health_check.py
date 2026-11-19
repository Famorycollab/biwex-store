"""
============================================================
 SCRIPT DE HEALTHCHECK — BIWEX STORE
 Auteur : Abdoul TRAORE (a21traore06@gmail.com)
 Compte GitHub : a21traore06-creator
 Branche : feature/abdoul-traore

 Ce script interroge l'endpoint /health de l'application Flask
 pour vérifier la santé du service, le temps de réponse et la
 conformité du payload JSON. Utilisable en conteneur Docker
 et dans les pipelines Jenkins (Build & Smoke sur PR).
============================================================
"""

import sys
import json
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

DEFAULT_URL = "http://127.0.0.1:5000/health"
TIMEOUT_SECONDS = 5


def check_health(url=DEFAULT_URL):
    print("=" * 60)
    print("  HEALTHCHECK DE L'APPLICATION — BIWEX STORE")
    print(f"  Auteur : Abdoul TRAORE | Cible : {url}")
    print("=" * 60)

    start_time = time.time()
    try:
        req = Request(url, headers={'User-Agent': 'Jenkins-HealthCheck/1.0'})
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            status_code = response.status

            if status_code != 200:
                print(f"[ERREUR] Code HTTP anormal : {status_code}")
                return False

            raw_data = response.read().decode('utf-8')
            payload = json.loads(raw_data)

            print(f"[OK] Connexion réussie en {latency_ms} ms")
            print(f"[OK] Statut rapporté : {payload.get('status', 'inconnu')}")
            print(f"[OK] Application      : {payload.get('app', 'inconnu')}")
            print(f"[OK] Version          : {payload.get('version', 'inconnu')}")

            if payload.get('status') == 'healthy':
                print("\n--> RESULTAT : HEALTHY (PASSED) ✅")
                return True
            else:
                print("\n--> RESULTAT : UNHEALTHY (FAILED) ❌")
                return False

    except HTTPError as e:
        print(f"[ERREUR] Erreur HTTP {e.code} : {e.reason}")
        return False
    except URLError as e:
        print(f"[ERREUR] Impossible de joindre l'application : {e.reason}")
        return False
    except Exception as e:
        print(f"[ERREUR] Exception inattendue : {e}")
        return False


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    success = check_health(target)
    sys.exit(0 if success else 1)
