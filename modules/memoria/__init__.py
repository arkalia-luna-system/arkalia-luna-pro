"""
Memoria - Mémoire vectorielle locale pour Arkalia-LUNA.

Ce package fournit un service de stockage et de recherche de souvenirs
vectoriels (VectorMemoryService) utilisé par les modules comme AssistantIA.
"""

from .service import VectorMemoryService, get_vector_memory_service

__all__ = ["VectorMemoryService", "get_vector_memory_service"]

