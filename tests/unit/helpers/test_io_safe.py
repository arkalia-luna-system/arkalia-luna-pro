# 🧪 Tests pour utils/io_safe.py - IO Sécurisé Arkalia-LUNA
import json
import threading
import time
from unittest.mock import patch

import pytest
import toml

from modules.utils.helpers.io_safe import (
    AtomicWriteError,
    LockedReadError,
    atomic_write,
    locked_read,
    read_state_safe,
    save_json_if_changed,
    save_json_safe,
    save_toml_if_changed,
    save_toml_safe,
)


class TestAtomicWrite:
    """Tests pour l'écriture atomique"""

    def test_atomic_write_string(self, tmp_path) -> None:
        """🧠 Test écriture atomique d'une chaîne"""
        test_file = tmp_path / "test.txt"
        test_data = "Hello Arkalia-LUNA!"

        result = atomic_write(test_file, test_data)

        assert result is True
        assert test_file.exists()
        assert test_file.read_text() == test_data

    def test_atomic_write_json(self, tmp_path) -> None:
        """🧠 Test écriture atomique JSON"""
        test_file = tmp_path / "test.json"
        test_data = {"status": "active", "modules": ["zeroia", "reflexia"]}

        result = atomic_write(test_file, test_data)

        assert result is True
        assert test_file.exists()
        loaded_data = json.loads(test_file.read_text())
        assert loaded_data == test_data

    def test_atomic_write_toml(self, tmp_path) -> None:
        """🧠 Test écriture atomique TOML"""
        test_file = tmp_path / "test.toml"
        test_data = {"arkalia": {"version": "2.5.0", "active": True}}

        result = atomic_write(test_file, test_data)

        assert result is True
        assert test_file.exists()
        loaded_data = toml.loads(test_file.read_text())
        assert loaded_data == test_data

    def test_atomic_write_creates_parent_dirs(self, tmp_path) -> None:
        """🧠 Test création automatique des répertoires parents"""
        nested_file = tmp_path / "deep" / "nested" / "test.txt"
        test_data = "Arkalia creates dirs!"

        result = atomic_write(nested_file, test_data)

        assert result is True
        assert nested_file.exists()
        assert nested_file.read_text() == test_data

    def test_atomic_write_concurrent_access(self, tmp_path) -> None:
        """🧠 Test écriture concurrent (thread-safe)"""
        test_file = tmp_path / "concurrent.txt"
        results = []

        def write_data(data) -> None:
            try:
                result = atomic_write(test_file, f"Thread-{data}")
                results.append(result)
            except Exception as e:
                results.append(str(e))

        # Lance 5 threads simultanés
        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_data, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Tous les threads doivent réussir
        assert all(r is True for r in results)
        assert test_file.exists()

    def test_atomic_write_error_handling(self, tmp_path) -> None:
        """🧠 Test gestion d'erreurs"""
        # Fichier dans un répertoire sans permissions (simulation)
        with patch("tempfile.NamedTemporaryFile", side_effect=OSError("Permission denied")):
            with pytest.raises(AtomicWriteError, match="Erreur écriture atomique"):
                atomic_write(tmp_path / "test.txt", "data")


class TestLockedRead:
    """Tests pour la lecture verrouillée"""

    def test_locked_read_string(self, tmp_path) -> None:
        """🧠 Test lecture verrouillée d'une chaîne"""
        test_file = tmp_path / "test.txt"
        test_data = "Arkalia-LUNA is secure!"
        test_file.write_text(test_data)

        result = locked_read(test_file)

        assert result == test_data

    def test_locked_read_json(self, tmp_path) -> None:
        """🧠 Test lecture verrouillée JSON avec parsing automatique"""
        test_file = tmp_path / "test.json"
        test_data = {"security": "high", "version": "2.5.0"}
        test_file.write_text(json.dumps(test_data))

        result = locked_read(test_file)

        assert result == test_data

    def test_locked_read_toml(self, tmp_path) -> None:
        """🧠 Test lecture verrouillée TOML avec parsing automatique"""
        test_file = tmp_path / "test.toml"
        test_data = {"arkalia": {"secure": True}}
        test_file.write_text(toml.dumps(test_data))

        result = locked_read(test_file)

        assert result == test_data

    def test_locked_read_nonexistent_file(self, tmp_path) -> None:
        """🧠 Test lecture d'un fichier inexistant"""
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            locked_read(nonexistent)

    def test_locked_read_concurrent_access(self, tmp_path) -> None:
        """🧠 Test lecture concurrent"""
        test_file = tmp_path / "concurrent.txt"
        test_data = "Concurrent reading test"
        test_file.write_text(test_data)

        results = []

        def read_data() -> None:
            try:
                result = locked_read(test_file)
                results.append(result)
            except Exception as e:
                results.append(str(e))

        # Lance 10 threads de lecture simultanés
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=read_data)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Toutes les lectures doivent réussir avec la même valeur
        assert all(r == test_data for r in results)
        assert len(results) == 10

    def test_locked_read_timeout(self, tmp_path) -> None:
        """🧠 Test timeout lors de l'acquisition du verrou"""
        test_file = tmp_path / "timeout.txt"
        test_file.write_text("test data")

        # Simule un timeout en prenant le verrou
        from modules.utils.helpers.io_safe import _get_file_lock

        file_lock = _get_file_lock(test_file)
        file_lock.acquire()

        try:
            with pytest.raises(LockedReadError, match="Timeout lors de l'acquisition"):
                locked_read(test_file, timeout=0.1)
        except Exception as e:
            raise AssertionError(f"Erreur inattendue: {e}") from e
        finally:
            file_lock.release()


class TestSafeWrappers:
    """Tests pour les wrappers sécurisés"""

    def test_save_toml_safe(self, tmp_path) -> None:
        """🧠 Test sauvegarde TOML sécurisée"""
        test_file = tmp_path / "test.toml"
        test_data = {"zeroia": {"active": True, "version": "1.0"}}

        result = save_toml_safe(test_data, test_file)

        assert result is True
        assert test_file.exists()
        loaded = toml.loads(test_file.read_text())
        assert loaded == test_data

    def test_save_toml_if_changed_cleans_comparison_tmp(self, tmp_path) -> None:
        """Nettoie le fichier temporaire de comparaison après écriture."""
        test_file = tmp_path / "state.toml"
        payload = {"status": "ok"}

        changed = save_toml_if_changed(payload, test_file, add_timestamp=False)

        assert changed is True
        assert test_file.exists()
        assert not list(tmp_path.glob(".state.toml.tmp.*.arkalia"))

    def test_save_json_if_changed_cleans_comparison_tmp(self, tmp_path) -> None:
        """Nettoie le fichier temporaire de comparaison après écriture."""
        test_file = tmp_path / "state.json"
        payload = {"status": "ok"}

        changed = save_json_if_changed(payload, test_file, add_timestamp=False)

        assert changed is True
        assert test_file.exists()
        assert not list(tmp_path.glob(".state.json.tmp.*.arkalia"))

    def test_save_toml_safe_invalid_data(self, tmp_path) -> None:
        """🧠 Test sauvegarde TOML avec données invalides"""
        test_file = tmp_path / "invalid.toml"

        with pytest.raises(AtomicWriteError, match="Les données doivent être un dictionnaire"):
            save_toml_safe("not a dict", test_file)  # type: ignore

    def test_save_json_safe(self, tmp_path) -> None:
        """🧠 Test sauvegarde JSON sécurisée"""
        test_file = tmp_path / "test.json"
        test_data = {"assistantia": {"secure": True}}

        result = save_json_safe(test_data, test_file)

        assert result is True
        assert test_file.exists()
        loaded = json.loads(test_file.read_text())
        assert loaded == test_data

    def test_read_state_safe_existing_file(self, tmp_path) -> None:
        """🧠 Test lecture sécurisée d'état existant"""
        test_file = tmp_path / "state.json"
        test_data = {"status": "healthy", "modules": 4}
        test_file.write_text(json.dumps(test_data))

        result = read_state_safe(test_file)

        assert result == test_data

    def test_read_state_safe_nonexistent_file(self, tmp_path) -> None:
        """🧠 Test lecture sécurisée d'état inexistant"""
        nonexistent = tmp_path / "nonexistent.json"

        result = read_state_safe(nonexistent)

        assert result == {}

    def test_read_state_safe_corrupted_file(self, tmp_path) -> None:
        """🧠 Test lecture sécurisée de fichier corrompu"""
        test_file = tmp_path / "corrupted.json"
        test_file.write_text("{invalid json content")

        result = read_state_safe(test_file)

        assert result == {}


class TestIntegration:
    """Tests d'intégration pour les opérations combinées"""

    def test_write_read_cycle(self, tmp_path) -> None:
        """🧠 Test cycle complet écriture-lecture"""
        test_file = tmp_path / "cycle.json"
        original_data = {
            "arkalia": {
                "version": "2.5.0",
                "modules": ["zeroia", "reflexia", "assistantia"],
                "secure": True,
            }
        }

        # Écriture atomique
        write_result = atomic_write(test_file, original_data)
        assert write_result is True

        # Lecture verrouillée
        read_result = locked_read(test_file)
        assert read_result == original_data

    def test_concurrent_write_read_operations(self, tmp_path) -> None:
        """🧠 Test opérations concurrent écriture-lecture"""
        test_file = tmp_path / "concurrent_ops.json"

        def writer_thread(data_id) -> None:
            data = {"thread_id": data_id, "timestamp": time.time()}
            atomic_write(test_file, data)

        def reader_thread() -> None:
            try:
                return locked_read(test_file)
            except FileNotFoundError:
                return None

        # Lance 3 écrivains et 5 lecteurs simultanés
        writers = [threading.Thread(target=writer_thread, args=(i,)) for i in range(3)]
        readers = [threading.Thread(target=reader_thread) for _ in range(5)]

        all_threads = writers + readers

        for thread in all_threads:
            thread.start()

        for thread in all_threads:
            thread.join()

        # Le fichier doit exister à la fin
        assert test_file.exists()
        final_data = locked_read(test_file)
        assert isinstance(final_data, dict)
        assert "thread_id" in final_data

    def test_state_persistence(self, tmp_path) -> None:
        """🧠 Test persistance d'état robuste"""
        state_file = tmp_path / "arkalia_state.toml"

        # États successifs
        states = [
            {"step": 1, "status": "initializing"},
            {"step": 2, "status": "loading_modules"},
            {"step": 3, "status": "ready", "modules_loaded": 4},
        ]

        for state in states:
            save_toml_safe(state, state_file)
            loaded_state = read_state_safe(state_file)
            assert loaded_state == state

        # Vérification finale
        final_state = read_state_safe(state_file)
        assert final_state["step"] == 3
        assert final_state["status"] == "ready"
