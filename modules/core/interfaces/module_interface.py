#!/usr/bin/env python3
"""
🔗 Interface IModule - Principe SOLID ISP
🎯 Contrat pour tous les modules du système
🛡️ Séparation des responsabilités
"""

from abc import ABC, abstractmethod
from typing import Any


class IModule(ABC):
    """
    🎯 Interface pour tous les modules du système
    🛡️ Principe ISP : Interface Segregation Principle
    """

    @abstractmethod
    def initialize(self) -> bool:
        """
        🚀 Initialisation du module
        :return: True si initialisation réussie
        """
        pass

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """
        🏥 Vérification de santé du module
        :return: Dictionnaire avec statut et métriques
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        📝 Nom du module
        :return: Nom unique du module
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        📦 Version du module
        :return: Version semver
        """
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """
        ✅ État d'activation du module
        :return: True si le module est actif
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        🔌 Arrêt propre du module
        :return: True si arrêt réussi
        """
        pass


class IModuleWithProcessing(IModule):
    """
    🔄 Interface étendue pour modules avec traitement
    🎯 Modules qui traitent des données
    """

    @abstractmethod
    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        🔄 Traitement de données
        :param data: Données d'entrée
        :return: Données traitées
        """
        pass

    @abstractmethod
    def get_processing_stats(self) -> dict[str, Any]:
        """
        📊 Statistiques de traitement
        :return: Métriques de performance
        """
        pass


class IModuleWithMonitoring(IModule):
    """
    📊 Interface étendue pour modules avec monitoring
    🎯 Modules qui surveillent le système
    """

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """
        📊 Récupération des métriques
        :return: Métriques actuelles
        """
        pass

    @abstractmethod
    def set_alert_threshold(self, metric: str, threshold: float) -> bool:
        """
        🚨 Configuration des seuils d'alerte
        :param metric: Nom de la métrique
        :param threshold: Seuil d'alerte
        :return: True si configuration réussie
        """
        pass


class IModuleWithDependencies(IModule):
    """
    🔗 Interface étendue pour modules avec dépendances
    🎯 Modules qui dépendent d'autres modules
    """

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """
        🔗 Liste des dépendances
        :return: Liste des noms de modules requis
        """
        pass

    @abstractmethod
    def set_dependency(self, name: str, module: IModule) -> bool:
        """
        🔗 Injection d'une dépendance
        :param name: Nom de la dépendance
        :param module: Instance du module
        :return: True si injection réussie
        """
        pass

    @abstractmethod
    def validate_dependencies(self) -> bool:
        """
        ✅ Validation des dépendances
        :return: True si toutes les dépendances sont satisfaites
        """
        pass
