from abc import ABC, abstractmethod
from typing import Dict, Any, List
from constants import FORMAT_TEXT

class AbstractExtractor(ABC):
    """Abstract base class for extractors."""
    
    @abstractmethod
    def extract(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields from a post."""
        pass

    @abstractmethod
    def format_output(self, extracted_data: Dict[str, Any], format_type: str) -> str:
        """Format extracted data into the desired output."""
        pass

    def process_posts(self, posts: List[Dict[str, Any]], format_type: str = FORMAT_TEXT) -> List[str]:
        """Process multiple posts and return formatted outputs."""
        return [self.format_output(self.extract(post), format_type) for post in posts]
