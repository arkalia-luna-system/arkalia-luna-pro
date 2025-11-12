#!/usr/bin/env python3
"""
🏭 ServiceFactory - Factory SOLID pour services du Core
🎯 Injection de dépendances et création de services
"""

from typing import Any


class ServiceFactory:
    """
    🏭 Factory pour créer et injecter des services du Core
    """

    def __init__(self):
        self._services: dict[str, Any] = {}
        self._registry: dict[str, type] = {}

    def register_service_class(self, name: str, service_cls: type) -> bool:
        if name in self._registry:
            self.ark_logger.warning(
                f"Classe service déjà enregistrée : {name}", extra={"arkalia_module": "core"}
            )
            return False
        self._registry[name] = service_cls
        self.ark_logger.info(
            f"Classe service enregistrée : {name}", extra={"arkalia_module": "core"}
        )
        return True

    def unregister_service_class(self, name: str) -> bool:
        if name in self._registry:
            del self._registry[name]
            self.ark_logger.info(
                f"Classe service désenregistrée : {name}", extra={"arkalia_module": "core"}
            )
            return True
        return False

    def get_service(self, name: str) -> Any | None:
        return self._services.get(name)

    def create_service(self, name: str, **kwargs) -> Any | None:
        if name not in self._registry:
            self.ark_logger.error(
                f"Classe service inconnue : {name}", extra={"arkalia_module": "core"}
            )
            return None
        try:
            service = self._registry[name](**kwargs)
            self._services[name] = service
            self.ark_logger.info(
                f"Instance service créée : {name}", extra={"arkalia_module": "core"}
            )
            return service
        except Exception as e:
            self.ark_logger.error(
                f"Erreur création service {name} : {e}", extra={"arkalia_module": "core"}
            )
            return None
