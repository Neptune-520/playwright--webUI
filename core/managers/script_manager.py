import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from django.conf import settings
import jsonschema
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


SCRIPT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "target_url", "steps"],
    "properties": {
        "name": {"type": "string"},
        "code": {"type": "string"},
        "description": {"type": "string"},
        "target_url": {"type": "string", "format": "uri"},
        "product_type_id": {"type": "integer"},
        "status": {"type": "string", "enum": ["draft", "published", "archived"]},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "action_type"],
                "properties": {
                    "name": {"type": "string"},
                    "order": {"type": "integer"},
                    "action_type": {
                        "type": "string",
                        "enum": [
                            "navigate", "click", "fill", "select", "random_select", "check", "uncheck",
                            "wait", "wait_for_selector", "screenshot", "scroll",
                            "hover", "focus", "press", "upload", "assert_text",
                            "assert_visible", "assert_value", "custom"
                        ]
                    },
                    "element": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "value": {"type": "string"},
                            "timeout": {"type": "integer"},
                            "state": {"type": "string"},
                        }
                    },
                    "value": {"type": "string"},
                    "config": {"type": "object"},
                    "description": {"type": "string"},
                    "is_enabled": {"type": "boolean"},
                    "continue_on_failure": {"type": "boolean"},
                    "retry_count": {"type": "integer"},
                    "retry_interval": {"type": "integer"},
                }
            }
        },
        "parameters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "code": {"type": "string"},
                    "value": {"type": "string"},
                    "is_required": {"type": "boolean"},
                }
            }
        }
    }
}


class ScriptManager:
    def __init__(self, scripts_dir: Path = None):
        self.scripts_dir = scripts_dir or settings.TEST_SCRIPTS_DIR
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def save_script_to_json(self, script_data: Dict[str, Any], filename: str = None) -> Path:
        if filename is None:
            filename = f"{script_data.get('code', 'script')}_{script_data.get('version', 1)}.json"
        
        filepath = self.scripts_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Script saved to {filepath}")
        return filepath
    
    def load_script_from_json(self, filename: str) -> Dict[str, Any]:
        filepath = self.scripts_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Script file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        
        return script_data
    
    def validate_script(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            'valid': False,
            'errors': [],
        }
        
        try:
            validate(instance=script_data, schema=SCRIPT_SCHEMA)
            result['valid'] = True
        except ValidationError as e:
            result['errors'].append({
                'path': list(e.path),
                'message': e.message,
            })
        except Exception as e:
            result['errors'].append({
                'path': [],
                'message': str(e),
            })
        
        return result
    
    def list_script_files(self) -> List[str]:
        return [f.name for f in self.scripts_dir.glob('*.json')]
    
    def delete_script_file(self, filename: str) -> bool:
        filepath = self.scripts_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False
