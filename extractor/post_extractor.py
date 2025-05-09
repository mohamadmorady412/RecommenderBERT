from typing import Dict, Any, Callable
import re
from abstract_extractor import AbstractExtractor
from config_loader import PluginConfig, FieldConfig
from constants import FORMAT_TEXT, FORMAT_JSON, SUPPORTED_FORMATS

class MissingKeyError(Exception):
    """Custom exception for missing keys in nested dictionary lookup."""
    pass

class PostExtractor(AbstractExtractor):
    """Concrete implementation of a post extractor.

    This class extracts fields from posts based on a plugin configuration.
    It uses `FieldConfig` (defined in config_loader.py) to specify how each field
    should be extracted from a post dictionary.
    """
    
    def __init__(self, plugin_path: str):
        """Initialize with a plugin configuration file.

        Args:
            plugin_path (str): Path to the JSON plugin configuration file.
        """
        self._plugin: PluginConfig = PluginConfig.from_file(plugin_path)
        self._extractor_registry: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._register_default_extractors()

    def _register_default_extractors(self) -> None:
        """Register default extractor functions."""
        self.register_extractor('extractHashtags', self._extract_hashtags)

    def register_extractor(self, name: str, func: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a custom extractor function.

        Args:
            name (str): Name of the extractor function (used in plugin configuration).
            func (Callable): The extractor function that takes a post and returns a value.
        """
        self._extractor_registry[name] = func

    def _get_nested_value(self, post: Dict[str, Any], key_path: str, raise_on_missing: bool = False) -> Any:
        """Look up a value from a nested dictionary using a dot-separated key path.

        Args:
            post (Dict[str, Any]): The post dictionary to extract from.
            key_path (str): Dot-separated path to the desired key (e.g., 'title' or 'meta.author').
            raise_on_missing (bool): If True, raise MissingKeyError if the key is not found.

        Returns:
            Any: The value if found, None otherwise (unless raise_on_missing is True).

        Raises:
            MissingKeyError: If raise_on_missing is True and the key is not found.
        """
        keys = key_path.split('.')
        value = post
        for key in keys:
            value = value.get(key, None)
            if value is None:
                if raise_on_missing:
                    raise MissingKeyError(f"Key '{key}' not found in path '{key_path}'")
                break
        return value

    def _extract_hashtags(self, post: Dict[str, Any]) -> list:
        """Extract hashtags from the post's body.

        Args:
            post (Dict[str, Any]): The post dictionary.

        Returns:
            list: List of hashtags found in the post body.
        """
        body = self._get_nested_value(post, 'body', raise_on_missing=False) or ''
        return re.findall(r'#\w+', body)

    def _evaluate_extractor(self, post: Dict[str, Any], field: FieldConfig) -> Any:
        """Evaluate the extractor expression to get the field value.

        Args:
            post (Dict[str, Any]): The post dictionary to extract from.
            field (FieldConfig): Configuration for the field, including the extractor expression.

        Returns:
            Any: The extracted value or the default value if none found.

        Raises:
            ValueError: If an invalid extractor function is specified.
        """
        options = [opt.strip() for opt in field.extractor.split('||')]
        for option in options:
            if option.startswith('post.'):
                value = self._get_nested_value(post, option[5:], raise_on_missing=field.required)
                if value is not None:
                    return value
            elif option.startswith('extract'):
                func_name = option.split('(')[0]
                if func_name in self._extractor_registry:
                    return self._extractor_registry[func_name](post)
                raise ValueError(f"Unknown extractor function: {func_name}")
        return field.default

    def extract(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields from a post based on the plugin configuration.

        Args:
            post (Dict[str, Any]): The post dictionary to extract fields from.

        Returns:
            Dict[str, Any]: Dictionary of extracted field names and values.

        Raises:
            ValueError: If a required field is not found in the post.
        """
        result = {}
        for field in self._plugin:
            value = self._evaluate_extractor(post, field)
            if value is None and field.required:
                raise ValueError(f"Required field '{field.name}' not found in post.")
            result[field.name] = value
        return result

    def format_output(self, extracted_data: Dict[str, Any], format_type: str = FORMAT_TEXT) -> str:
        """Format the extracted data into the desired output format.

        Args:
            extracted_data (Dict[str, Any]): The extracted fields and their values.
            format_type (str): The output format (see constants.py for supported formats).

        Returns:
            str: Formatted output string.

        Raises:
            ValueError: If the format_type is unsupported.
        """
        if format_type not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format type: {format_type}. Supported formats: {SUPPORTED_FORMATS}")
        if format_type == FORMAT_TEXT:
            return '\n'.join(f"{key}: {value}" for key, value in extracted_data.items())
        elif format_type == FORMAT_JSON:
            import json
            return json.dumps(extracted_data, ensure_ascii=False, indent=2)
        return ""  # This line is unreachable due to the SUPPORTED_FORMATS check

    def __repr__(self) -> str:
        """Return a string representation of the extractor."""
        return f"PostExtractor(plugin={self._plugin})"

    def __iter__(self):
        """Allow iteration over plugin fields."""
        return iter(self._plugin)