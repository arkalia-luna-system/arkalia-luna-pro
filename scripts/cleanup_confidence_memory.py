#!/usr/bin/env python3
"""
🧹 Script de nettoyage pour confidence_memory.toml
Réduit la taille du fichier en gardant seulement les entrées récentes.
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import toml

from core.ark_logger import ark_logger


def cleanup_confidence_memory(
    file_path: str | Path,
    days_to_keep: int = 30,
    max_entries: int = 1000,
    backup: bool = True,
) -> tuple[int, float, float]:
    """
    Nettoie le fichier confidence_memory.toml en gardant seulement les entrées récentes.

    Args:
        file_path: Chemin vers confidence_memory.toml
        days_to_keep: Nombre de jours à garder (défaut: 30)
        max_entries: Nombre maximum d'entrées à garder (défaut: 1000)
        backup: Créer une sauvegarde avant nettoyage (défaut: True)

    Returns:
        Tuple (nombre_entrées_supprimées, taille_avant_MB, taille_après_MB)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        ark_logger.warning(
            f"⚠️ Fichier non trouvé: {file_path}", extra={"arkalia_module": "scripts"}
        )
        return 0, 0.0, 0.0

    # Taille avant
    size_before_mb = file_path.stat().st_size / (1024 * 1024)

    # Créer backup si demandé
    if backup:
        backup_path = file_path.with_suffix(
            f".toml.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        import shutil

        shutil.copy2(file_path, backup_path)
        ark_logger.info(f"📦 Backup créé: {backup_path}", extra={"arkalia_module": "scripts"})

    # Charger le fichier
    try:
        data = toml.load(file_path)
    except Exception as e:
        ark_logger.error(f"❌ Erreur chargement TOML: {e}", extra={"arkalia_module": "scripts"})
        return 0, size_before_mb, size_before_mb

    # Filtrer les métriques de performance
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    performance_metrics = data.get("performance_metrics", [])

    if not performance_metrics:
        ark_logger.info(
            "ℹ️ Aucune métrique de performance trouvée", extra={"arkalia_module": "scripts"}
        )
        return 0, size_before_mb, size_before_mb

    # Filtrer par date
    filtered_metrics: list[dict[str, Any]] = []
    for metric in performance_metrics:
        try:
            timestamp_str = metric.get("timestamp", "")
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                if timestamp.replace(tzinfo=None) >= cutoff_date:
                    filtered_metrics.append(metric)
        except Exception:
            # Garder les entrées sans timestamp valide (anciennes)
            continue

    # Limiter le nombre d'entrées (garder les plus récentes)
    if len(filtered_metrics) > max_entries:
        # Trier par timestamp (plus récent en premier)
        filtered_metrics.sort(
            key=lambda metric: str(metric.get("timestamp", "")),
            reverse=True,
        )
        filtered_metrics = filtered_metrics[:max_entries]

    # Mettre à jour les données
    data["performance_metrics"] = filtered_metrics
    entries_removed = len(performance_metrics) - len(filtered_metrics)

    # Sauvegarder
    try:
        with open(file_path, "w") as f:
            toml.dump(data, f)
    except Exception as e:
        ark_logger.error(f"❌ Erreur sauvegarde TOML: {e}", extra={"arkalia_module": "scripts"})
        return 0, size_before_mb, size_before_mb

    # Taille après
    size_after_mb = file_path.stat().st_size / (1024 * 1024)
    size_freed_mb = size_before_mb - size_after_mb

    ark_logger.info(
        f"✅ Nettoyage terminé: {entries_removed} entrées supprimées, "
        f"{size_freed_mb:.2f}MB libérés ({size_before_mb:.2f}MB → {size_after_mb:.2f}MB)",
        extra={"arkalia_module": "scripts"},
    )

    return entries_removed, size_before_mb, size_after_mb


def main() -> None:
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Nettoie confidence_memory.toml en gardant seulement les entrées récentes"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="state/confidence_memory.toml",
        help="Chemin vers confidence_memory.toml",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Nombre de jours à garder (défaut: 30)",
    )
    parser.add_argument(
        "--max-entries",
        type=int,
        default=1000,
        help="Nombre maximum d'entrées à garder (défaut: 1000)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Ne pas créer de backup",
    )

    args = parser.parse_args()

    # Trouver le fichier depuis la racine du projet
    project_root = Path(__file__).parent.parent
    file_path = project_root / args.file

    if not file_path.exists():
        ark_logger.error(f"❌ Fichier non trouvé: {file_path}", extra={"arkalia_module": "scripts"})
        return

    entries_removed, size_before, size_after = cleanup_confidence_memory(
        file_path,
        days_to_keep=args.days,
        max_entries=args.max_entries,
        backup=not args.no_backup,
    )

    print("\n✅ Nettoyage terminé !")
    print(f"   Entrées supprimées: {entries_removed}")
    print(f"   Taille avant: {size_before:.2f}MB")
    print(f"   Taille après: {size_after:.2f}MB")
    print(f"   Espace libéré: {size_before - size_after:.2f}MB")


if __name__ == "__main__":
    main()
