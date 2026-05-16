from importlib import import_module

from app.investigators.base import Investigator


class PluginManager:
    def load(self, dotted_paths: list[str]) -> list[Investigator]:
        plugins: list[Investigator] = []
        for dotted_path in dotted_paths:
            module_name, class_name = dotted_path.rsplit(".", 1)
            cls = getattr(import_module(module_name), class_name)
            plugin = cls()
            if not isinstance(plugin, Investigator):
                raise TypeError(f"{dotted_path} is not an Investigator")
            plugins.append(plugin)
        return plugins
