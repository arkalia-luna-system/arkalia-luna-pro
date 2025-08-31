"""Tests pour core/core.py"""

from core.core import Core


def test_core_initialization() -> None:
    """Test de l'initialisation de Core"""
    core = Core()
    assert isinstance(core, Core)


def test_basic_functionality() -> None:
    """Test de la fonctionnalité de base"""
    core = Core()
    assert core.basic_functionality() is True
