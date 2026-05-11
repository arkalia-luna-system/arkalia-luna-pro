#!/bin/bash

# Ce script vérifie les hooks avant CI/CD

# Exécutez les hooks de pré-commit pour vérifier les erreurs
pre-commit run --all-files

# Vérifiez le statut de la dernière commande
if [ $? -ne 0 ]; then
    echo "Échec de la validation des hooks. Veuillez corriger les erreurs avant de continuer."
    exit 1
else
    echo "Tous les hooks ont été validés avec succès."
fi
