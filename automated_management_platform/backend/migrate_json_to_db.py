import json
import uuid
from pathlib import Path
from datetime import datetime
from database import init_db, SessionLocal, Folder, ScriptResult, StepResultModel, Config, DATABASE_URL

BASE_DIR = Path(__file__).parent / "uploads"
SCRIPT_RESULTS_DIR = BASE_DIR / "script_results"
FOLDERS_JSON = Path(__file__).parent / "folders.json"
CONFIG_JSON = Path(__file__).parent / "config.json"


def migrate_folders(db):
    if not FOLDERS_JSON.exists():
        print("folders.json not found, skipping folder migration")
        return 0
    
    with open(FOLDERS_JSON, 'r', encoding='utf-8') as f:
        folders_data = json.load(f)
    
    count = 0
    for folder in folders_data:
        existing = db.query(Folder).filter(Folder.id == folder['id']).first()
        if not existing:
            folder_obj = Folder(
                id=folder['id'],
                name=folder['name'],
                created_at=datetime.fromisoformat(folder['created_at']) if folder.get('created_at') else datetime.utcnow()
            )
            db.add(folder_obj)
            count += 1
    
    db.commit()
    print(f"Migrated {count} folders")
    return count


def migrate_script_results(db):
    if not SCRIPT_RESULTS_DIR.exists():
        print("script_results directory not found, skipping migration")
        return 0
    
    count = 0
    for file in SCRIPT_RESULTS_DIR.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            existing = db.query(ScriptResult).filter(ScriptResult.id == data.get('id')).first()
            if existing:
                continue
            
            result_id = data.get('id', str(uuid.uuid4()))
            script_result = ScriptResult(
                id=result_id,
                task_id=data.get('task_id', 0),
                task_name=data.get('task_name', ''),
                script_name=data.get('script_name', ''),
                started_at=data.get('started_at', ''),
                finished_at=data.get('finished_at', ''),
                status=data.get('status', 'unknown'),
                parameters=data.get('parameters', {}),
                total_steps=data.get('total_steps', 0),
                passed_steps=data.get('passed_steps', 0),
                failed_steps=data.get('failed_steps', 0),
                skipped_steps=data.get('skipped_steps', 0),
                total_duration=data.get('total_duration', 0.0),
                pass_rate=data.get('pass_rate', 0.0),
                username=data.get('username', ''),
                script_count=data.get('script_count'),
                created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
            )
            db.add(script_result)
            
            for step_data in data.get('step_results', []):
                step = StepResultModel(
                    id=str(uuid.uuid4()),
                    script_result_id=result_id,
                    step_name=step_data.get('step_name', ''),
                    step_order=step_data.get('step_order', 0),
                    action_type=step_data.get('action_type', ''),
                    status=step_data.get('status', 'unknown'),
                    duration=step_data.get('duration', 0.0),
                    error=step_data.get('error'),
                    error_stack=step_data.get('error_stack'),
                    screenshot=step_data.get('screenshot'),
                    action_values=step_data.get('action_values', {})
                )
                db.add(step)
            
            count += 1
        except (json.JSONDecodeError, IOError, Exception) as e:
            print(f"Error migrating {file}: {e}")
            continue
    
    db.commit()
    print(f"Migrated {count} script results")
    return count


def migrate_config(db):
    if not CONFIG_JSON.exists():
        print("config.json not found, skipping config migration")
        return 0
    
    with open(CONFIG_JSON, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    count = 0
    for key, value in config_data.items():
        existing = db.query(Config).filter(Config.key == key).first()
        if not existing:
            config_obj = Config(
                key=key,
                value=value
            )
            db.add(config_obj)
            count += 1
    
    db.commit()
    print(f"Migrated {count} config entries")
    return count


def main():
    print(f"Starting database migration...")
    print(f"Database URL: {DATABASE_URL}")
    
    init_db()
    
    db = SessionLocal()
    try:
        migrate_folders(db)
        migrate_script_results(db)
        migrate_config(db)
        print("Migration completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
