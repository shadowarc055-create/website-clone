# Modular Plugin System

Plugins are Python classes that inherit from `Investigator`.

```python
class MyInvestigator(Investigator):
    name = "my_source"
    supported_types = {EntityType.DOMAIN}
    async def investigate(self, entity: Entity) -> list[Finding]:
        ...
```

Load external plugins with `PluginManager.load(["package.module.MyInvestigator"])`. Plugins should be side-effect free and return structured findings. Storage and recursive queue decisions belong to the engine.
