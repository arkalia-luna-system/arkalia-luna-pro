# 🛡️ IO Sécurisé Arkalia-LUNA
# Module d'écriture atomique et lecture thread-safe
# Supprime les corruptions silencieuses TOML/JSON

import fcntl
import json
import logging
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Optional

import toml

logger = logging.getLogger(__name__)


class AtomicWriteError(Exception):
    """Exception pour les erreurs d'écriture atomique"""

    pass


class LockedReadError(Exception):
    """Exception pour les erreurs de lecture verrouillée"""

    pass


# Thread lock global pour la sécurité
_file_locks: dict[str, Any] = {}
_locks_mutex = threading.Lock()


def _get_file_lock(file_path: Path) -> threading.Lock:
    """Obtient un verrou spécifique à un fichier"""
    str_path = str(file_path.absolute())

    with _locks_mutex:
        if str_path not in _file_locks:
            _file_locks[str_path] = threading.Lock()
        return _file_locks[str_path]


def atomic_write(
    file_path: str | Path,
    data: str | bytes | dict[str, Any],
    encoding: str = "utf-8",
    mode: str = "w",
) -> bool:
    """
    Écriture atomique sécurisée d'un fichier

    Args:
        file_path: Chemin du fichier à écrire
        data: Données à écrire (str, bytes, ou dict pour JSON/TOML)
        encoding: Encodage du fichier (défaut: utf-8)
        mode: Mode d'écriture (défaut: w)

    Returns:
        bool: True si succès, False sinon

    Raises:
        AtomicWriteError: En cas d'erreur d'écriture
    """
    file_path = Path(file_path)

    # Obtient le verrou pour ce fichier
    file_lock = _get_file_lock(file_path)

    with file_lock:
        try:
            # Crée le répertoire parent si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Fichier temporaire dans le même répertoire (même système de fichiers)
            with tempfile.NamedTemporaryFile(
                mode=mode,
                encoding=encoding if "b" not in mode else None,
                dir=file_path.parent,
                delete=False,
                prefix=f".{file_path.name}.tmp.",
                suffix=".arkalia",
            ) as tmp_file:
                # Écrit les données selon le type
                if isinstance(data, dict):
                    if file_path.suffix.lower() == ".json":
                        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
                    elif file_path.suffix.lower() == ".toml":
                        toml.dump(data, tmp_file)
                    else:
                        # Assume JSON par défaut pour les dicts
                        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
                else:
                    tmp_file.write(data)

                # Force l'écriture sur disque
                tmp_file.flush()
                os.fsync(tmp_file.fileno())

                tmp_path = tmp_file.name

            # Déplacement atomique (renommage)
            os.rename(tmp_path, file_path)

            # Vérifie que le fichier a bien été créé
            if not file_path.exists():
                raise AtomicWriteError(f"Échec de création du fichier {file_path}")

            return True

        except Exception as e:
            # Nettoie le fichier temporaire en cas d'erreur
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError as cleanup_error:
                    logger.warning(
                        f"Failed to cleanup temporary file {tmp_path}: {cleanup_error}"
                    )  # nosec B110

            raise AtomicWriteError(f"Erreur écriture atomique {file_path}: {e}") from e


def locked_read(
    file_path: str | Path,
    encoding: str = "utf-8",
    timeout: float = 5.0,
    mode: str = "r",
) -> str | bytes | dict[str, Any]:
    """
    Lecture thread-safe avec verrou et timeout

    Args:
        file_path: Chemin du fichier à lire
        encoding: Encodage du fichier (défaut: utf-8)
        timeout: Timeout en secondes (défaut: 5.0)
        mode: Mode de lecture (défaut: r)

    Returns:
        Contenu du fichier (str, bytes, ou dict pour JSON/TOML)

    Raises:
        LockedReadError: En cas d'erreur de lecture
        FileNotFoundError: Si le fichier n'existe pas
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Fichier inexistant: {file_path}")

    # Obtient le verrou pour ce fichier
    file_lock = _get_file_lock(file_path)

    if not file_lock.acquire(timeout=timeout):
        raise LockedReadError(f"Timeout lors de l'acquisition du verrou: {file_path}")

    try:
        with open(file_path, mode, encoding=encoding if "b" not in mode else None) as f:
            # Verrou système pour éviter les lectures pendant l'écriture
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
            except OSError:
                # Fichier verrouillé, attend un peu et réessaie
                time.sleep(0.1)
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)

            try:
                content = f.read()

                # Parse automatique pour JSON/TOML
                if isinstance(content, str) and content.strip():
                    if file_path.suffix.lower() == ".json":
                        return json.loads(content)
                    elif file_path.suffix.lower() == ".toml":
                        return toml.loads(content)

                return content

            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    except Exception as e:
        raise LockedReadError(f"Erreur lecture {file_path}: {e}") from e

    finally:
        file_lock.release()


def save_toml_safe(data: dict[str, Any], file_path: str | Path) -> bool:
    """
    Sauvegarde TOML sécurisée avec validation

    Args:
        data: Dictionnaire à sauvegarder
        file_path: Chemin du fichier TOML

    Returns:
        bool: True si succès

    Raises:
        AtomicWriteError: En cas d'erreur
    """
    if not isinstance(data, dict):
        raise AtomicWriteError(f"Les données doivent être un dictionnaire, reçu: {type(data)}")

    # Validation TOML avant écriture
    try:
        toml.dumps(data)
    except Exception as e:
        raise AtomicWriteError(f"Données non-sérialisables en TOML: {e}") from e

    return atomic_write(file_path, data)


def save_json_safe(data: dict[str, Any], file_path: str | Path) -> bool:
    """
    Sauvegarde JSON sécurisée avec validation

    Args:
        data: Dictionnaire à sauvegarder
        file_path: Chemin du fichier JSON

    Returns:
        bool: True si succès

    Raises:
        AtomicWriteError: En cas d'erreur
    """
    if not isinstance(data, dict):
        raise AtomicWriteError(f"Les données doivent être un dictionnaire, reçu: {type(data)}")

    # Validation JSON avant écriture
    try:
        json.dumps(data, ensure_ascii=False)
    except Exception as e:
        raise AtomicWriteError(f"Données non-sérialisables en JSON: {e}") from e

    return atomic_write(file_path, data)


def read_state_safe(file_path: str | Path) -> dict[str, Any]:
    """
    Lecture sécurisée d'un fichier d'état (JSON/TOML)

    Args:
        file_path: Chemin du fichier d'état

    Returns:
        dict: État chargé ou {} si erreur
    """
    try:
        result = locked_read(file_path)
        if isinstance(result, dict):
            return result
        return {}
    except (
        FileNotFoundError,
        LockedReadError,
        json.JSONDecodeError,
        toml.TomlDecodeError,
    ):
        return {}


# Alias pour compatibilité
atomic_save = atomic_write
safe_read = locked_read
