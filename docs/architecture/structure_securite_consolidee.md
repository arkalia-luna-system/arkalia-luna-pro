# 🛡️ Nouvelle structure du module `security` consolidé (Phase 2)

## Schéma d'architecture

```mermaid
flowchart TD
    S[modules/security/]
    S1[crypto\nVault, tokens, rotation, intégrité]
    S2[sandbox\nEnvironnement sécurisé]
    S3[watchdog\nSurveillance sécurité]
    S --> S1
    S --> S2
    S --> S3
    style S1 fill:#ffe082
    style S2 fill:#b3e5fc
    style S3 fill:#c8e6c9
```

## Description des sous-modules

- **crypto/** :
    - `vault_manager.py` : gestion des secrets, chiffrement, audit, rotation de clé
    - `token_lifecycle.py` : gestion des tokens (JWT, API keys, permissions, révocation)
    - `secret_rotation.py` : rotation automatique des secrets, politiques, notifications
    - `checksum_validator.py` : validation d'intégrité
- **sandbox/** : environnement sécurisé pour l'exécution de code ou d'IA
- **watchdog/** : surveillance sécurité, détection d'anomalies

> **Remarque :** Les fichiers physiques du vault sont dans `security/vault/` (clé, secrets chiffrés, audit log)

---

## Guide d'importation

```python
from modules.security.crypto import ArkaliaVault, TokenManager, RotationManager
from modules.security.sandbox import ...
from modules.security.watchdog import ...
```

---

## Tableau de correspondance anciens/nouveaux modules

| Ancien module/fichier         | Nouveau module/contenu                |
|------------------------------|---------------------------------------|
| modules/security/crypto/     | modules/security/crypto/ (inchangé)   |
| security/vault/              | modules/security/crypto/vault/ (optionnel, ou laissé en l'état) |
| modules/security/sandbox/    | modules/security/sandbox/             |
| modules/security/watchdog/   | modules/security/watchdog/            |

---

## Points clés

- **Centralisation totale** de la sécurité dans `modules/security/`
- **Aucun code critique dispersé** ailleurs dans le projet
- **Architecture SOLID** respectée et extensible
- **Phase 2 du plan de consolidation :** ✅ Terminée et documentée

---

*Document généré automatiquement lors de la consolidation (novembre 2025)*
