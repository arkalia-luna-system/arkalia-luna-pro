#!/usr/bin/env python3

"""
🎛️ Lancement direct de la boucle ReflexIA

Ce script exécute la boucle réflexive complète (collecte des métriques,
décision adaptative, sauvegarde du snapshot) via le cœur du module `reflexia`.

💡 Usage :
    python -m scripts.run.run_reflexia
"""

from modules.reflexia.core import launch_reflexia_loop

if __name__ == "__main__":
    launch_reflexia_loop()
