import json
from pathlib import Path
from database import init_db, SessionLocal, Config

CONFIG_FILE = Path(__file__).parent / 'config.json'

DEFAULT_CONFIG = {
    'management_platform_url': 'http://localhost:8001/api/script-results/upload',
    'username': ''
}


def get_config():
    try:
        db = SessionLocal()
        configs = db.query(Config).all()
        if configs:
            return {config.key: config.value for config in configs}
    except Exception:
        pass
    finally:
        if db:
            db.close()
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def update_config(data: dict):
    try:
        db = SessionLocal()
        for key, value in data.items():
            config = db.query(Config).filter(Config.key == key).first()
            if config:
                config.value = value
            else:
                db.add(Config(key=key, value=value))
        db.commit()
        
        configs = db.query(Config).all()
        return {config.key: config.value for config in configs}
    except Exception:
        if db:
            db.rollback()
        current = get_config()
        current.update(data)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        return current
    finally:
        if db:
            db.close()


def get_upload_url():
    config = get_config()
    return config.get('management_platform_url', DEFAULT_CONFIG['management_platform_url'])
