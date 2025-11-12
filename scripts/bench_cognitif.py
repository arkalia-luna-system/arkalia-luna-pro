#!/usr/bin/env python3
"""
Benchmark Cognitif Arkalia-LUNA Pro
Mesure la latence, le temps de réaction et les erreurs évitées sur le flux ZeroIA → Reflexia → API
"""

import time
from statistics import mean

from demo_global import ReflexiaWrapper, SandoziaWrapper, SecurityWrapper

from modules.core.storage import StorageManager
from modules.zeroia import ZeroIACoordinator

N_RUNS = 20

results = []
errors_avoided = 0

for i in range(N_RUNS):
    t0 = time.perf_counter()
    zeroia = ZeroIACoordinator()
    reflexia = ReflexiaWrapper()
    sandozia = SandoziaWrapper()
    security = SecurityWrapper()
    storage = StorageManager()

    try:
        # Décision ZeroIA
        t1 = time.perf_counter()
        decision = zeroia.make_decision("security_incident")
        t2 = time.perf_counter()

        # Alerte Reflexia
        alert_id = reflexia.create_alert(
            {
                "type": "security_threat",
                "severity": "high",
                "source": "zeroia",
                "details": decision,
            }
        )
        t3 = time.perf_counter()

        # Analyse Sandozia
        analysis = sandozia.analyze_behavior(
            {
                "event_type": "security_incident",
                "decision_id": decision.get("id", "n/a"),
            }
        )
        t4 = time.perf_counter()

        # Scan API Security
        scan = security.scan_request({"payload": "DROP TABLE users;"})
        t5 = time.perf_counter()

        # Stockage
        storage.save_state("zeroia", decision, "last_decision")
        last = storage.get_state("zeroia", "last_decision")
        t6 = time.perf_counter()

        # Simuler une erreur évitée si menace détectée
        if scan["threat_level"] == "high" and scan["blocked"]:
            errors_avoided += 1

        results.append(
            {
                "zeroia": t2 - t1,
                "reflexia": t3 - t2,
                "sandozia": t4 - t3,
                "security": t5 - t4,
                "storage": t6 - t5,
                "total": t6 - t0,
            }
        )
    except Exception as e:
        print(f"Erreur lors du run {i}: {e}")

# Statistiques
print("\n=== Benchmark Cognitif Arkalia-LUNA Pro ===")
print(f"Runs: {N_RUNS}")
print(f"Latence ZeroIA (ms): {mean([r['zeroia'] for r in results]) * 1000:.2f}")
print(f"Latence Reflexia (ms): {mean([r['reflexia'] for r in results]) * 1000:.2f}")
print(f"Latence Sandozia (ms): {mean([r['sandozia'] for r in results]) * 1000:.2f}")
print(f"Latence Security (ms): {mean([r['security'] for r in results]) * 1000:.2f}")
print(f"Latence Storage (ms): {mean([r['storage'] for r in results]) * 1000:.2f}")
print(f"Temps de réaction total (ms): {mean([r['total'] for r in results]) * 1000:.2f}")
print(f"Erreurs évitées (simulées): {errors_avoided}/{N_RUNS}")
