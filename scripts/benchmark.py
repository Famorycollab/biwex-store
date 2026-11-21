"""
============================================================
 SCRIPT DE TEST DE PERFORMANCE & LATENCE (BENCHMARK)
 Auteur  : Abdoul TRAORE (a21traore06@gmail.com)
 Branche : feature/abdoul-traore
 Projet  : DevOps 3LIG — ISG Sousse 2026/2027

 EXPLICATION SIMPLE POUR LA PROFESSEURE :
 Ce script simule des requêtes en rafale vers l'application
 en conteneur Docker afin de mesurer :
   - Le temps de réponse moyen (latence en millisecondes)
   - Le taux de réussite (HTTP 200)
   - Les performances minimales et maximales
============================================================
"""

import urllib.request
import time
import sys


def run_benchmark(target_url="http://127.0.0.1:5000/", total_requests=20):
    print("=" * 60)
    print(" 🚀 BENCHMARK DE PERFORMANCE — BIWEX STORE")
    print(f" Cible   : {target_url}")
    print(f" Volume  : {total_requests} requêtes consécutives")
    print("=" * 60)

    latencies = []
    success_count = 0

    for i in range(1, total_requests + 1):
        start_time = time.time()
        try:
            req = urllib.request.Request(target_url, headers={'User-Agent': 'Biwex-Benchmark-Agent'})
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
                elapsed_ms = (time.time() - start_time) * 1000.0
                latencies.append(elapsed_ms)
                if status_code == 200:
                    success_count += 1
                print(f"  [Req #{i:02d}] HTTP {status_code} - {elapsed_ms:.2f} ms")
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000.0
            print(f"  [Req #{i:02d}] ERREUR: {e} ({elapsed_ms:.2f} ms)")

    print("-" * 60)
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        success_rate = (success_count / total_requests) * 100.0

        print(" 📊 RÉSULTATS DU BENCHMARK :")
        print(f"   • Taux de succès      : {success_rate:.1f}% ({success_count}/{total_requests})")
        print(f"   • Latence moyenne     : {avg_latency:.2f} ms")
        print(f"   • Latence minimale    : {min_latency:.2f} ms")
        print(f"   • Latence maximale    : {max_latency:.2f} ms")
        print("=" * 60)

        if success_rate == 100.0 and avg_latency < 500.0:
            print(" ✅ STATUT : EXCELLENT (Prêt pour la production)")
            return 0
        else:
            print(" ⚠️ STATUT : Performances acceptables")
            return 0
    else:
        print(" ❌ AUCUNE RÉPONSE DU SERVEUR")
        return 1


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000/"
    sys.exit(run_benchmark(url))
