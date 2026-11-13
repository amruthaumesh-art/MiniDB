
"""Plugin management for MiniDB."""

from typing import Any, Dict


class PluginManager:
    """Register, retrieve, and manage MiniDB plugins."""

    def __init__(self):
        self._plugins: Dict[str, Any] = {}

    def register(self, name: str, plugin: Any) -> None:
        """Register a plugin with a unique name."""
        if not name:
            raise ValueError("Plugin name cannot be empty.")

        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' is already registered.")

        if not callable(getattr(plugin, "activate", None)):
            raise TypeError("A plugin must implement activate(database).")

        self._plugins[name] = plugin

    def activate(self, name: str, database: Any) -> None:
        """Activate a registered plugin."""
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' is not registered.")

        self._plugins[name].activate(database)

    def get(self, name: str) -> Any:
        """Return a registered plugin."""
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' is not registered.")

        return self._plugins[name]

    def list_plugins(self) -> list[str]:
        """Return the names of all registered plugins."""
        return list(self._plugins.keys())
