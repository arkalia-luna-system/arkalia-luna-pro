from pathlib import Path
from unittest.mock import patch

from modules.zeroia.snapshot_generator import generate_snapshot, is_valid_toml, load_state


def test_load_state_file_not_found():
    """
    Vérifie que `load_state()` retourne un dict vide si le fichier n'existe pas.
    """
    result = load_state(Path("non_existent_file.toml"))
    assert result == {}, "Le fichier de l'état devrait être vide si le fichier TOML n'existe pas."


def test_is_valid_toml_invalid_data_forced():
    """
    Simule un objet non sérialisable TOML et vérifie que `is_valid_toml()`
    retourne False.
    """
    with patch(
        "modules.zeroia.snapshot_generator.toml.dumps",
        side_effect=TypeError("Invalid TOML"),
    ):
        result = is_valid_toml({"invalid": object()})
        assert result is False, "TOML invalide non détecté comme tel."


def test_generate_snapshot_invalid_toml(tmp_path):
    """
    Vérifie que `generate_snapshot()` retourne False si le fichier TOML est invalide.
    """
    invalid_toml_path = tmp_path / "invalid_state.toml"
    invalid_toml_path.write_text("invalid = [")  # contenu invalide (TOML malformé)

    with patch("modules.zeroia.snapshot_generator.is_valid_toml", return_value=False):
        result = generate_snapshot(input_path=invalid_toml_path, fallback=False)
        assert (
            result is False
        ), "Le snapshot ne devrait pas être généré avec un fichier TOML invalide."


def test_snapshot_generator_returns_valid_path(tmp_path):
    """
    Vérifie que `generate_snapshot()` retourne True sur un fichier TOML valide.
    """
    valid_path = tmp_path / "fake.toml"
    valid_path.write_text("fake = 'value'")

    result = generate_snapshot(input_path=valid_path, fallback=True)
    assert result, "Snapshot non généré malgré fallback=True et un fichier TOML valide."
