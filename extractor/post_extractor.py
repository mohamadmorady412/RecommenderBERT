from typing import Dict, Any
import re
from abstract_extractor import AbstractExtractor
from config_loader import PluginConfig, FieldConfig

class PostExtractor(AbstractExtractor):
    """Concrete implementation of a post extractor."""
    
    def __init__(self, plugin_path: str):
        """Initialize with a plugin configuration file."""
        self._plugin = PluginConfig.from_file(plugin_path)

    def _get_nested_value(self, post: Dict[str, Any], key_path: str) -> Any:
        """Get a value from a nested dictionary using a dot-separated key path."""
        keys = key_path.split('.')
        value = post
        for key in keys:
            value = value.get(key, None)
            if value is None:
                break
        return value

    def _extract_hashtags(self, text: str) -> list:
        """Extract hashtags from a text string."""
        return re.findall(r'#\w+', text)

    def _evaluate_extractor(self, post: Dict[str, Any], field: 'FieldConfig') -> Any:
        """Evaluate the extractor expression to get the field value."""
        options = [opt.strip() for opt in field.extractor.split('||')]
        for option in options:
            if option.startswith('post.'):
                value = self._get_nested_value(post, option[5:])
                if value is not None:
                    return value
            elif option == 'extractHashtags(post.body)':
                body = self._get_nested_value(post, 'body') or ''
                return self._extract_hashtags(body)
        return field.default

    def extract(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields from a post based on the plugin configuration."""
        result = {}
        for field in self._plugin:
            value = self._evaluate_extractor(post, field)
            if value is None and field.required:
                raise ValueError(f"Required field '{field.name}' not found in post.")
            result[field.name] = value
        return result

    def format_output(self, extracted_data: Dict[str, Any], format_type: str = 'text') -> str:
        """Format the extracted data into the desired output format."""
        if format_type == 'text':
            return '\n'.join(f"{key}: {value}" for key, value in extracted_data.items())
        elif format_type == 'json':
            import json
            return json.dumps(extracted_data, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def __repr__(self):
        return f"PostExtractor(plugin={self._plugin})"

    def __iter__(self):
        """Allow iteration over plugin fields."""
        return iter(self._plugin)
