#!/usr/bin/env python3
"""
🔗 Interface IHealthCheck - Principe SOLID SRP
🎯 Contrat pour le monitoring de santé
🛡️ Responsabilité unique : Surveillance de santé
"""

from abc import ABC, abstractmethod
from typing import Any


class IHealthCheck(ABC):
    """
    🎯 Interface pour la vérification de santé
    🛡️ Principe SRP : Single Responsibility Principle
    """

    @abstractmethod
    def check_health(self) -> dict[str, Any]:
        """
        🏥 Vérification de santé générale
        :return: Dictionnaire avec statut et métriques
        """
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """
        ✅ État de santé global
        :return: True si le système est en bonne santé
        """
        pass

    @abstractmethod
    def get_health_score(self) -> float:
        """
        📊 Score de santé (0.0 à 1.0)
        :return: Score numérique de santé
        """
        pass


class IHealthCheckWithMetrics(IHealthCheck):
    """
    📊 Interface étendue pour métriques détaillées
    🎯 Monitoring avec métriques spécifiques
    """

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """
        📊 Récupération des métriques de santé
        :return: Métriques détaillées
        """
        pass

    @abstractmethod
    def get_metric(self, name: str) -> Any | None:
        """
        📊 Récupération d'une métrique spécifique
        :param name: Nom de la métrique
        :return: Valeur de la métrique ou None
        """
        pass

    @abstractmethod
    def set_metric(self, name: str, value: Any) -> bool:
        """
        📊 Définition d'une métrique
        :param name: Nom de la métrique
        :param value: Valeur de la métrique
        :return: True si définition réussie
        """
        pass


class IHealthCheckWithAlerts(IHealthCheck):
    """
    🚨 Interface étendue pour alertes
    🎯 Monitoring avec système d'alertes
    """

    @abstractmethod
    def add_alert(self, alert: dict[str, Any]) -> bool:
        """
        🚨 Ajout d'une alerte
        :param alert: Dictionnaire d'alerte
        :return: True si ajout réussi
        """
        pass

    @abstractmethod
    def get_alerts(self) -> list[dict[str, Any]]:
        """
        🚨 Récupération des alertes actives
        :return: Liste des alertes
        """
        pass

    @abstractmethod
    def clear_alerts(self) -> bool:
        """
        🧹 Nettoyage des alertes
        :return: True si nettoyage réussi
        """
        pass

    @abstractmethod
    def set_alert_threshold(self, metric: str, threshold: float) -> bool:
        """
        🚨 Configuration d'un seuil d'alerte
        :param metric: Nom de la métrique
        :param threshold: Seuil d'alerte
        :return: True si configuration réussie
        """
        pass


class IHealthCheckWithWatchdogs(IHealthCheck):
    """
    🛡️ Interface étendue pour watchdogs
    🎯 Monitoring avec mécanismes de surveillance critique
    """

    @abstractmethod
    def register_watchdog(self, name: str, watchdog) -> bool:
        """
        🛡️ Enregistrement d'un watchdog
        :param name: Nom du watchdog
        :param watchdog: Fonction de surveillance
        :return: True si enregistrement réussi
        """
        pass

    @abstractmethod
    def unregister_watchdog(self, name: str) -> bool:
        """
        🗑️ Désenregistrement d'un watchdog
        :param name: Nom du watchdog
        :return: True si désenregistrement réussi
        """
        pass

    @abstractmethod
    def run_watchdogs(self) -> dict[str, dict[str, Any]]:
        """
        🛡️ Exécution de tous les watchdogs
        :return: Résultats des watchdogs
        """
        pass

    @abstractmethod
    def get_watchdog_status(self, name: str) -> dict[str, Any] | None:
        """
        📊 Statut d'un watchdog spécifique
        :param name: Nom du watchdog
        :return: Statut du watchdog ou None
        """
        pass


class IHealthCheckWithHistory(IHealthCheck):
    """
    📈 Interface étendue pour historique
    🎯 Monitoring avec historique des métriques
    """

    @abstractmethod
    def save_health_snapshot(self) -> bool:
        """
        📸 Sauvegarde d'un snapshot de santé
        :return: True si sauvegarde réussie
        """
        pass

    @abstractmethod
    def get_health_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        📈 Récupération de l'historique de santé
        :param limit: Nombre maximum d'entrées
        :return: Liste des snapshots historiques
        """
        pass

    @abstractmethod
    def get_health_trend(self, metric: str, duration: str = "1h") -> list[float]:
        """
        📈 Tendance d'une métrique sur une période
        :param metric: Nom de la métrique
        :param duration: Durée (ex: "1h", "24h", "7d")
        :return: Liste des valeurs historiques
        """
        pass
