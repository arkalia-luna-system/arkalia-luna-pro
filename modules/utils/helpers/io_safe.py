# 🛡️ IO Sécurisé Arkalia-LUNA
# Module d'écriture atomique et lecture thread-safe
# Supprime les corruptions silencieuses TOML/JSON

import fcntl
import hashlib
import json
import os
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import toml

from core.ark_logger import ark_logger


class AtomicWriteError(Exception):
    """Exception pour les erreurs d'écriture atomique"""

    pass


class LockedReadError(Exception):
    """Exception pour les erreurs de lecture verrouillée"""

    pass


# Thread lock global pour la sécurité
_file_locks: dict[str, threading.Lock] = {}
_locks_mutex = threading.Lock()

# Cache TOML simple (thread-safe)
_TOML_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_TIMESTAMPS: dict[str, float] = {}
_CACHE_TTL: float = 30.0  # 30 secondes par défaut
_cache_lock = threading.Lock()

# Garde-fou anti-accumulation de fichiers temporaires d'écriture atomique.
_TMP_RETENTION_SECONDS = 60 * 60  # 1h
_TMP_MAX_KEEP = 16


def _get_file_lock(file_path: Path) -> threading.Lock:
    """Obtient un verrou spécifique à un fichier"""
    str_path = str(file_path.absolute())

    with _locks_mutex:
        if str_path not in _file_locks:
            _file_locks[str_path] = threading.Lock()
        return _file_locks[str_path]


def _cleanup_stale_atomic_tmp(file_path: Path) -> None:
    """
    Nettoie les temporaires atomiques orphelins.

    Un arrêt brutal peut laisser des `.tmp.*.arkalia`. On purge d'abord ceux
    trop anciens, puis on limite le nombre restant pour éviter la croissance.
    """
    parent = file_path.parent
    if not parent.exists():
        return

    pattern = f".{file_path.name}.tmp.*.arkalia"
    now = time.time()
    tmp_candidates: list[Path] = []

    for tmp in parent.glob(pattern):
        if not tmp.is_file():
            continue
        tmp_candidates.append(tmp)
        try:
            if now - tmp.stat().st_mtime > _TMP_RETENTION_SECONDS:
                tmp.unlink()
        except OSError:
            # Best effort: ne jamais bloquer l'écriture principale.
            continue

    # Garder uniquement les plus récents si la quantité explose.
    if len(tmp_candidates) <= _TMP_MAX_KEEP:
        return

    try:
        existing = [p for p in parent.glob(pattern) if p.is_file()]
        existing.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for stale in existing[_TMP_MAX_KEEP:]:
            try:
                stale.unlink()
            except OSError:
                continue
    except OSError:
        return


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
        tmp_path: str | None = None
        try:
            # Crée le répertoire parent si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)
            _cleanup_stale_atomic_tmp(file_path)

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
            if tmp_path is not None and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError as cleanup_error:
                    ark_logger.warning(
                        f"Failed to cleanup temporary file {tmp_path}: {cleanup_error}",
                        extra={"arkalia_module": "utils"},
                    )

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
                content: str | bytes = f.read()

                # Parse automatique pour JSON/TOML
                if isinstance(content, str) and content.strip():
                    if file_path.suffix.lower() == ".json":
                        parsed = json.loads(content)
                        if isinstance(parsed, dict):
                            return parsed
                        return content
                    elif file_path.suffix.lower() == ".toml":
                        parsed = toml.loads(content)
                        if isinstance(parsed, dict):
                            return parsed
                        return content

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


def load_toml_cached(file_path: str | Path, cache_ttl: float = 30.0) -> dict[str, Any]:
    """
    Charge un fichier TOML avec cache thread-safe

    Args:
        file_path: Chemin vers le fichier TOML
        cache_ttl: Durée de vie du cache en secondes (défaut: 30.0)

    Returns:
        dict: Données du fichier TOML (depuis cache si valide, sinon depuis disque)
    """
    file_path = Path(file_path)
    str_path = str(file_path.absolute())
    current_time = time.time()

    # Vérifier cache valide
    with _cache_lock:
        if (
            str_path in _TOML_CACHE
            and str_path in _CACHE_TIMESTAMPS
            and current_time - _CACHE_TIMESTAMPS[str_path] < cache_ttl
        ):
            return _TOML_CACHE[str_path]

    # Cache invalide ou inexistant, charger depuis disque
    try:
        data = locked_read(file_path)
        if isinstance(data, dict):
            # Mettre à jour le cache
            with _cache_lock:
                _TOML_CACHE[str_path] = data
                _CACHE_TIMESTAMPS[str_path] = current_time
            return data
        return {}
    except (FileNotFoundError, LockedReadError, toml.TomlDecodeError) as e:
        ark_logger.warning(
            f"Erreur chargement TOML {file_path}: {e}", extra={"arkalia_module": "utils"}
        )
        return {}


def _file_hash(file_path: Path) -> str:
    """
    Calcule le hash SHA256 d'un fichier pour détecter les changements.

    Args:
        file_path: Chemin vers le fichier à hasher

    Returns:
        str: Hash SHA256 du fichier, chaîne vide si fichier inexistant
    """
    if not file_path.exists():
        return ""
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def save_toml_if_changed(
    data: dict[str, Any], file_path: str | Path, add_timestamp: bool = True
) -> bool:
    """
    Sauvegarde un fichier TOML seulement s'il y a des changements (thread-safe).

    Utilise une approche atomique avec fichier temporaire et vérification de hash
    pour éviter les écritures inutiles. Thread-safe grâce à atomic_write.

    Args:
        data: Dictionnaire de données à sauvegarder
        file_path: Chemin de destination du fichier TOML
        add_timestamp: Si True, ajoute un timestamp au dictionnaire

    Returns:
        bool: True si le fichier a été modifié, False s'il était identique

    Raises:
        AtomicWriteError: En cas d'erreur d'écriture
    """
    file_path = Path(file_path)
    _cleanup_stale_atomic_tmp(file_path)
    data_to_hash = data.copy()
    if add_timestamp:
        data_to_hash.pop("timestamp", None)

    # Créer un fichier temporaire pour comparer
    tmp_file_path: Path | None = None
    try:
        # Écrire dans le fichier temporaire
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            delete=False,
            prefix=f".{file_path.name}.tmp.",
            suffix=".arkalia",
        ) as tmp_file:
            toml.dump(data_to_hash, tmp_file)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            tmp_file_path = Path(tmp_file.name)

        # Comparer les hashs
        new_hash = _file_hash(tmp_file_path)
        old_hash = _file_hash(file_path) if file_path.exists() else ""

        if new_hash == old_hash:
            # Pas de changement, supprimer le fichier temporaire
            os.unlink(tmp_file_path)
            return False

        # Il y a des changements, ajouter timestamp si demandé
        if add_timestamp:
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Utiliser atomic_write pour la sauvegarde finale (thread-safe)
        result = atomic_write(file_path, data)
        # Nettoyage du temporaire de comparaison (sinon accumulation sur disque).
        if tmp_file_path is not None and tmp_file_path.exists():
            os.unlink(tmp_file_path)
        return result

    except Exception as e:
        # Nettoyer en cas d'erreur
        if tmp_file_path is not None and tmp_file_path.exists():
            try:
                os.unlink(tmp_file_path)
            except OSError:
                pass
        raise AtomicWriteError(f"Erreur sauvegarde TOML conditionnelle {file_path}: {e}") from e


def save_json_if_changed(
    data: dict[str, Any], file_path: str | Path, add_timestamp: bool = True
) -> bool:
    """
    Sauvegarde un fichier JSON seulement s'il y a des changements (thread-safe).

    Utilise une approche atomique avec fichier temporaire et vérification de hash
    pour éviter les écritures inutiles. Formatage consistant (indent=2, sort_keys=True).

    Args:
        data: Dictionnaire de données à sauvegarder
        file_path: Chemin de destination du fichier JSON
        add_timestamp: Si True, ajoute un timestamp au dictionnaire

    Returns:
        bool: True si le fichier a été modifié, False s'il était identique

    Raises:
        AtomicWriteError: En cas d'erreur d'écriture
    """
    file_path = Path(file_path)
    _cleanup_stale_atomic_tmp(file_path)
    data_to_hash = data.copy()
    if add_timestamp:
        data_to_hash.pop("timestamp", None)

    # Créer un fichier temporaire pour comparer
    tmp_file_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            delete=False,
            prefix=f".{file_path.name}.tmp.",
            suffix=".arkalia",
        ) as tmp_file:
            json.dump(data_to_hash, tmp_file, indent=2, sort_keys=True, ensure_ascii=False)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            tmp_file_path = Path(tmp_file.name)

        # Comparer les hashs
        new_hash = _file_hash(tmp_file_path)
        old_hash = _file_hash(file_path) if file_path.exists() else ""

        if new_hash == old_hash:
            # Pas de changement, supprimer le fichier temporaire
            os.unlink(tmp_file_path)
            return False

        # Il y a des changements, ajouter timestamp si demandé
        if add_timestamp:
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Utiliser atomic_write pour la sauvegarde finale (thread-safe)
        # Note: atomic_write gère déjà le formatage JSON
        result = atomic_write(file_path, data)
        # Nettoyage du temporaire de comparaison (sinon accumulation sur disque).
        if tmp_file_path is not None and tmp_file_path.exists():
            os.unlink(tmp_file_path)
        return result

    except Exception as e:
        # Nettoyer en cas d'erreur
        if tmp_file_path is not None and tmp_file_path.exists():
            try:
                os.unlink(tmp_file_path)
            except OSError:
                pass
        raise AtomicWriteError(f"Erreur sauvegarde JSON conditionnelle {file_path}: {e}") from e


# Alias pour compatibilité
atomic_save = atomic_write
safe_read = locked_read
