import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class ElementLocatorManager:
    def __init__(self, locators_dir: Path = None):
        self.locators_dir = locators_dir or settings.ELEMENT_LOCATORS_DIR
        self.locators_dir.mkdir(parents=True, exist_ok=True)
    
    def save_locators_to_json(self, locators: List[Dict[str, Any]], filename: str = 'locators.json') -> Path:
        filepath = self.locators_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(locators, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Locators saved to {filepath}")
        return filepath
    
    def load_locators_from_json(self, filename: str = 'locators.json') -> List[Dict[str, Any]]:
        filepath = self.locators_dir / filename
        
        if not filepath.exists():
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            locators = json.load(f)
        
        return locators
    
    def export_page_locators(self, page_url: str, locators: List[Dict[str, Any]]) -> Path:
        from urllib.parse import urlparse
        parsed_url = urlparse(page_url)
        domain = parsed_url.netloc.replace('.', '_')
        path = parsed_url.path.replace('/', '_').strip('_') or 'home'
        
        filename = f"{domain}_{path}_locators.json"
        return self.save_locators_to_json(locators, filename)
