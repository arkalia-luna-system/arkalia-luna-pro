#!/usr/bin/env python3
"""
🌕 TaskIA HTML Formatter
📝 Formateur HTML selon le principe OCP
🔧 Version: 2.0.0
👤 Author: Athalia
📅 Created: 2025-01-27
"""

from typing import Any

from modules.taskia.interfaces.formatter_interface import IFormatter


class HtmlFormatter(IFormatter):
    """
    Formateur HTML pour interface web.

    Principe OCP : Extension du comportement sans modification
    Principe LSP : Implémente l'interface IFormatter
    """

    def __init__(self, title: str = "TaskIA Data", css_class: str = "taskia-data"):
        """
        Initialise le formateur HTML.

        Args:
            title: Titre de la page HTML
            css_class: Classe CSS pour le conteneur
        """
        self._title = title
        self._css_class = css_class

    def format(self, data: dict[str, Any]) -> str:
        """
        Formate les données en HTML.

        Args:
            data: Données à formater

        Returns:
            Données formatées en HTML
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='fr'>",
            "<head>",
            f"    <title>{self._title}</title>",
            "    <meta charset='utf-8'>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 20px; }",
            "        .taskia-data { background: #f5f5f5; padding: 20px; border-radius: 8px; }",
            "        .section { margin-bottom: 20px; }",
            "        .section h2 { color: #333; border-bottom: 2px solid #007acc; }",
            "        .item { margin: 5px 0; padding: 5px; background: white; border-radius: 4px; }",
            "        .key { font-weight: bold; color: #007acc; }",
            "    </style>",
            "</head>",
            "<body>",
            f"    <div class='{self._css_class}'>",
            f"        <h1>🌕 {self._title}</h1>",
        ]

        if not data:
            html_parts.append("        <p><em>Aucune donnée disponible</em></p>")
        else:
            for key, value in data.items():
                html_parts.append("        <div class='section'>")
                html_parts.append(f"            <h2>{key.title()}</h2>")

                if isinstance(value, dict):
                    html_parts.append(self._format_dict_html(value))
                elif isinstance(value, list):
                    html_parts.append(self._format_list_html(value))
                else:
                    html_parts.append(
                        f"            <div class='item'>"
                        f"<span class='key'>{key}:</span> {value}</div>"
                    )

                html_parts.append("        </div>")

        html_parts.extend(["    </div>", "</body>", "</html>"])

        return "\n".join(html_parts)

    def _format_dict_html(self, data: dict[str, Any]) -> str:
        """Formate un dictionnaire en HTML."""
        lines = []
        for k, v in data.items():
            lines.append(f"            <div class='item'><span class='key'>{k}:</span> {v}</div>")
        return "\n".join(lines)

    def _format_list_html(self, data: list) -> str:
        """Formate une liste en HTML."""
        lines = ["            <ul>"]
        for item in data:
            lines.append(f"                <li>{item}</li>")
        lines.append("            </ul>")
        return "\n".join(lines)

    def get_format_type(self) -> str:
        """
        Retourne le type de formatage supporté.

        Returns:
            Type de formatage
        """
        return "html"
