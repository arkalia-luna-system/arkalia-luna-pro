# Compliance & Certifications

Cadre minimal de conformite pour l'exploitation Arkalia.

## Cibles de conformite

- ISO 27001 (SMSI)
- RGPD/CNIL (donnees personnelles)
- SOC 2 (controles operationnels)
- AI Act EU (transparence et gouvernance)

## Exigences non negociables

- Journalisation securite activee.
- Controle d'acces principe du moindre privilege.
- Chiffrement en transit et au repos pour donnees sensibles.
- Retention logs/documentation definie et appliquee.
- Processus d'incident-response documente et teste.

## Controles operationnels

### Revue securite

```bash
./scripts/ark-sec-check.sh --full-validation
```

### Points de verification

- Integrite des dependances et images.
- Secrets hors code et rotation reguliere.
- Audit des droits Docker/systeme.
- Traçabilite des changements critiques.

## RGPD (minimum)

- Finalite explicite des traitements.
- Limitation de conservation.
- Droit d'acces/suppression traite via procedure support.
- Anonymisation des logs quand necessaire.

## Evidence d'audit a conserver

- Rapports de scan securite.
- Historique incidents + post-mortem.
- Resultats des tests de restauration.
- Journaux de changement infra/app.

## Frequence recommandee

- Hebdomadaire: revue securite operationnelle.
- Mensuelle: revue conformite + ecarts.
- Trimestrielle: audit complet et plan de remediation.
