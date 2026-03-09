#!/usr/bin/env python3
"""
🌕 ZeroIA - Compatibilité reason_loop.py
---------------------------------------

Ce module est un *shim* de compatibilité pour l'ancien chemin
``modules.zeroia.reason_loop`` / ``reason_loop.py``.

Il réexporte simplement la version améliorée depuis
``modules.zeroia.reason_loop_enhanced`` afin de :
- préserver les anciens scripts (`ark-zeroia-run`, `ark-zeroia-check.sh`, etc.) ;
- éviter les erreurs de fichier manquant ;
- garantir que la logique moderne (ReasonLoopEnhanced) est utilisée.
"""

from __future__ import annotations

from .reason_loop_enhanced import *  # noqa: F401,F403

