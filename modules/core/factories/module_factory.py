#!/usr/bin/env python3
"""
🏭 ModuleFactory - Factory SOLID pour modules du Core
🎯 Création dynamique de modules compatibles IModule
"""


from ..interfaces.module_interface import IModule


class ModuleFactory:
    """
    🏭 Factory pour créer des modules compatibles IModule
    """

    def __init__(self):
        self.self._registry: dict[str, type[IModule]] = {}
        self._register_default_modules()

    def _register_default_modules(self) -> None:
        """Enregistre les modules par défaut"""
        try:
            # Enregistrer les adaptateurs
            from ..adapters import (
                create_reflexia_adapter,
                create_sandozia_adapter,
                create_taskia_adapter,
                create_zeroia_adapter,
            )

            # Créer des instances pour obtenir les classes
            zeroia_adapter = create_zeroia_adapter()
            taskia_adapter = create_taskia_adapter()
            reflexia_adapter = create_reflexia_adapter()
            sandozia_adapter = create_sandozia_adapter()

            self.register_module_class("zeroia", type(zeroia_adapter))
            self.register_module_class("taskia", type(taskia_adapter))
            self.register_module_class("reflexia", type(reflexia_adapter))
            self.register_module_class("sandozia", type(sandozia_adapter))

            self.ark_logger.info(
                "✅ Modules par défaut enregistrés", extra={"arkalia_module": "core"}
            )

        except Exception as e:
            self.ark_logger.error(
                f"❌ Erreur enregistrement modules par défaut: {e}",
                extra={"arkalia_module": "core"},
            )

    def register_module_class(self, name: str, module_cls: type[IModule]) -> bool:
        if name in self._registry:
            self.ark_logger.warning(
                f"Classe module déjà enregistrée : {name}", extra={"arkalia_module": "core"}
            )
            return False
        self._registry[name] = module_cls
        self.ark_logger.info(
            f"Classe module enregistrée : {name}", extra={"arkalia_module": "core"}
        )
        return True

    def unregister_module_class(self, name: str) -> bool:
        if name in self._registry:
            del self._registry[name]
            self.ark_logger.info(
                f"Classe module désenregistrée : {name}", extra={"arkalia_module": "core"}
            )
            return True
        return False

    def create_module(self, name: str, **kwargs) -> IModule | None:
        if name not in self._registry:
            self.ark_logger.error(
                f"Classe module inconnue : {name}", extra={"arkalia_module": "core"}
            )
            return None
        try:
            module = self._registry[name](**kwargs)
            self.ark_logger.info(
                f"Instance module créée : {name}", extra={"arkalia_module": "core"}
            )
            return module
        except Exception as e:
            self.ark_logger.error(
                f"Erreur création module {name} : {e}", extra={"arkalia_module": "core"}
            )
            return None
