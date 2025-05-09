import json
from dataclasses import dataclass
from typing import List, Optional, Any

@dataclass
class FieldConfig:
    """Configuration for a single field in the plugin."""
    name: str
    type: str
    required: bool
    extractor: str
    default: Optional[Any] = None

@dataclass
class PluginConfig:
    """Configuration for the entire plugin."""
    plugin_name: str
    version: str
    fields: List[FieldConfig]

    @classmethod
    def from_file(cls, plugin_path: str) -> 'PluginConfig':
        """Load plugin configuration from a JSON file."""
        with open(plugin_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        fields = [FieldConfig(**field) for field in data.get('fields', [])]
        return cls(
            plugin_name=data.get('plugin_name', 'unknown'),
            version=data.get('version', '0.0'),
            fields=fields
        )

    def __iter__(self):
        """Allow iteration over fields."""
        return iter(self.fields)

    def __repr__(self):
        return f"PluginConfig(name={self.plugin_name}, version={self.version}, fields={len(self.fields)})"
