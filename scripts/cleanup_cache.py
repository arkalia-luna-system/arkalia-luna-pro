#!/usr/bin/env python3
"""
🧹 Script de nettoyage des caches pour libérer de la RAM
Supprime les caches Python, les logs anciens et les fichiers temporaires
"""

import shutil
import time
from pathlib import Path


def cleanup_pycache(root_dir: Path) -> int:
    """Supprime tous les dossiers __pycache__"""
    count = 0
    for pycache_dir in root_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            count += 1
        except Exception:
            pass
    return count


def cleanup_old_logs(logs_dir: Path, max_age_days: int = 7) -> int:
    """Supprime les logs plus anciens que max_age_days"""
    if not logs_dir.exists():
        return 0

    count = 0
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)

    for log_file in logs_dir.rglob("*.log"):
        try:
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                count += 1
        except Exception:
            pass

    return count


def cleanup_state_cache(state_dir: Path, max_size_mb: int = 100) -> tuple[int, int]:
    """
    Nettoie le cache state/ en gardant seulement les fichiers les plus récents
    Retourne (fichiers_supprimés, espace_libéré_mb)
    """
    if not state_dir.exists():
        return 0, 0

    # Calculer la taille totale
    total_size = sum(f.stat().st_size for f in state_dir.rglob("*") if f.is_file())
    max_size_bytes = max_size_mb * 1024 * 1024

    if total_size <= max_size_bytes:
        return 0, 0

    # Trier les fichiers par date de modification (plus anciens en premier)
    files = [(f, f.stat().st_mtime, f.stat().st_size) for f in state_dir.rglob("*") if f.is_file()]
    files.sort(key=lambda x: x[1])  # Trier par date

    deleted_count = 0
    freed_bytes = 0

    for file_path, _, file_size in files:
        if total_size - freed_bytes <= max_size_bytes:
            break

        try:
            file_path.unlink()
            deleted_count += 1
            freed_bytes += file_size
        except Exception:
            pass

    return deleted_count, freed_bytes // (1024 * 1024)


def main():
    """Fonction principale de nettoyage"""
    project_root = Path(__file__).parent.parent

    print("🧹 Nettoyage des caches pour libérer de la RAM...")
    print(f"📁 Répertoire racine: {project_root}\n")

    # 1. Nettoyer __pycache__
    print("1️⃣ Nettoyage des caches Python (__pycache__)...")
    pycache_count = cleanup_pycache(project_root)
    print(f"   ✅ {pycache_count} dossiers __pycache__ supprimés\n")

    # 2. Nettoyer les logs anciens
    print("2️⃣ Nettoyage des logs anciens (>7 jours)...")
    logs_dir = project_root / "logs"
    log_count = cleanup_old_logs(logs_dir)
    print(f"   ✅ {log_count} fichiers de logs supprimés\n")

    # 3. Nettoyer le cache state/
    print("3️⃣ Nettoyage du cache state/ (limite: 100MB)...")
    state_dir = project_root / "state"
    deleted_files, freed_mb = cleanup_state_cache(state_dir, max_size_mb=100)
    print(f"   ✅ {deleted_files} fichiers supprimés, {freed_mb}MB libérés\n")

    print("✨ Nettoyage terminé !")


if __name__ == "__main__":
    main()
