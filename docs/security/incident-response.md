# Incident Response

Procedure concise de reponse aux incidents securite.

## Niveaux de severite

- `P1` critique: systeme compromis ou indisponible.
- `P2` eleve: service fortement degrade.
- `P3` modere: anomalie a investiguer.

## Flux standard

1. Detecter et qualifier (`P1`/`P2`/`P3`).
2. Contenir (isoler, stopper propagation).
3. Preserver les preuves (logs, etats, contexte).
4. Corriger et restaurer.
5. Verifier et suivre sur 24h/72h.
6. Post-mortem sous 48h.

## Playbook P1 (critique)

```bash
# 1) Stopper les services si compromission suspectee
docker compose down

# 2) Sauvegarder etats + logs pour forensic
TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p "/tmp/incident_${TS}"
cp -r state global_state logs "/tmp/incident_${TS}" 2>/dev/null

# 3) Validation securite avant reprise
./scripts/ops/ark-sec-check.sh --paranoid-mode
```

## Cas frequents

### Corruption d'etat ZeroIA

```bash
python scripts/_zeroia_rollback.py
./scripts/ops/ark-sec-check.sh --full-validation
```

### Degradation API / monitoring

```bash
./scripts/ops/health_check.sh --full-validation
curl -fsS http://localhost:8000/health
```

### Suspicion prompt injection

- Isoler le module concerne.
- Sauvegarder les logs de session.
- Redemarrer le service apres validation.

## Checklist post-incident

- [ ] Services stables.
- [ ] Metriques revenues a la normale.
- [ ] Aucun log critique residuel.
- [ ] Verification securite passee.
- [ ] Correctif preventif planifie.
- [ ] Post-mortem publie.

## Gabarit post-mortem

- Incident ID:
- Date/heure:
- Impact:
- Cause racine:
- Correctif applique:
- Actions preventives:
- Owner + date cible:
