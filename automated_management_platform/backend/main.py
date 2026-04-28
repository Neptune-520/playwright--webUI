import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, quote
from contextlib import contextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Any
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from database import init_db, get_db, Folder, ScriptResult, StepResultModel, Config

app = FastAPI(title="JSON File Management Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path("./uploads")
BASE_DIR.mkdir(exist_ok=True)

SCRIPT_RESULTS_DIR = BASE_DIR / "script_results"
SCRIPT_RESULTS_DIR.mkdir(exist_ok=True)


class StepResult(BaseModel):
    step_name: str
    step_order: int
    action_type: str
    status: str
    duration: float
    error: Optional[str] = None
    error_stack: Optional[str] = None
    screenshot: Optional[str] = None
    action_values: Optional[dict] = {}


class ScriptResultUpload(BaseModel):
    task_id: int
    task_name: str
    script_name: str
    started_at: str
    finished_at: str
    status: str
    step_results: List[StepResult]
    parameters: Optional[dict] = {}
    total_steps: int
    passed_steps: int
    failed_steps: int
    skipped_steps: int
    total_duration: float
    pass_rate: float
    username: Optional[str] = ""
    script_count: Optional[int] = None


def get_path_dir(relative_path: str) -> Path:
    if not relative_path or relative_path == "/":
        return BASE_DIR
    parts = [p for p in relative_path.split("/") if p]
    return BASE_DIR.joinpath(*parts)


def safe_resolve(target: Path) -> Path:
    resolved = target.resolve()
    if not str(resolved).startswith(str(BASE_DIR.resolve())):
        raise HTTPException(status_code=403, detail="不允许访问目录外部")
    return resolved


def get_item_info(path_obj: Path) -> dict:
    stat = path_obj.stat()
    return {
        "name": path_obj.name,
        "size": stat.st_size if path_obj.is_file() else 0,
        "is_folder": path_obj.is_dir(),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/items")
async def list_items(path: str = Query(default=""), db: Session = Depends(get_db)):
    dir_path = get_path_dir(path)
    dir_path = safe_resolve(dir_path)
    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=404, detail="目录不存在")

    items = []
    for item in dir_path.iterdir():
        if path == "" and item.name == "script_results":
            continue
        items.append(get_item_info(item))

    items.sort(key=lambda x: (not x["is_folder"], x["name"].lower()))
    return items


@app.post("/api/folder")
async def create_folder(name: str = Query(...), path: str = Query(default=""), db: Session = Depends(get_db)):
    dir_path = get_path_dir(path)
    dir_path = safe_resolve(dir_path)
    target = dir_path / name
    target = safe_resolve(target)
    if target.exists():
        raise HTTPException(status_code=400, detail="已存在同名项目")
    target.mkdir()

    folder = Folder(
        id=str(uuid.uuid4()),
        name=name,
        created_at=datetime.utcnow()
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)

    return get_item_info(target)


@app.delete("/api/items/{name}")
async def delete_item(name: str, path: str = Query(default=""), db: Session = Depends(get_db)):
    name = unquote(name)
    dir_path = get_path_dir(path)
    dir_path = safe_resolve(dir_path)
    target = dir_path / name
    target = safe_resolve(target)
    if not target.exists():
        raise HTTPException(status_code=404, detail="项目不存在")
    if target.is_dir():
        db.query(Folder).filter(Folder.name == name).delete()
        db.commit()
        shutil.rmtree(target)
    else:
        target.unlink()
    return {"message": f"'{name}' 已删除"}


@app.put("/api/items/{name}/rename")
async def rename_item(name: str, new_name: str = Query(...), path: str = Query(default=""), db: Session = Depends(get_db)):
    name = unquote(name)
    dir_path = get_path_dir(path)
    dir_path = safe_resolve(dir_path)
    target = dir_path / name
    target = safe_resolve(target)
    if not target.exists():
        raise HTTPException(status_code=404, detail="项目不存在")
    new_target = dir_path / new_name
    new_target = safe_resolve(new_target)
    if new_target.exists():
        raise HTTPException(status_code=400, detail="已存在同名项目")
    target.rename(new_target)

    folder = db.query(Folder).filter(Folder.name == name).first()
    if folder:
        folder.name = new_name
        db.commit()
        db.refresh(folder)

    return get_item_info(new_target)


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), path: str = Query(default="")):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="只允许上传 JSON 文件")
    content = await file.read()
    try:
        json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的 JSON 文件")

    dir_path = get_path_dir(path)
    dir_path = safe_resolve(dir_path)
    file_path = dir_path / file.filename
    file_path = safe_resolve(file_path)

    if file_path.exists():
        base, ext = os.path.splitext(file.filename)
        counter = 1
        while file_path.exists():
            file_path = dir_path / f"{base}_{counter}{ext}"
            file_path = safe_resolve(file_path)
            counter += 1

    with open(file_path, "wb") as f:
        f.write(content)
    return get_item_info(file_path)


@app.get("/api/items/{name}/download")
async def download_item(name: str, path: str = Query(default="")):
    name = unquote(name)
    dir_path = get_path_dir(path)
    dir_path = safe_resolve(dir_path)
    target = dir_path / name
    target = safe_resolve(target)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(path=target, filename=target.name, media_type="application/json")


@app.get("/api/items/{name}/preview")
async def preview_item(name: str, path: str = Query(default="")):
    name = unquote(name)
    dir_path = get_path_dir(path)
    dir_path = safe_resolve(dir_path)
    target = dir_path / name
    target = safe_resolve(target)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    try:
        with open(target, "r", encoding="utf-8") as f:
            content = json.load(f)
        return content
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSON 解析失败")


@app.get("/api/search")
async def search_items(keyword: str = Query(default="")):
    if not keyword:
        return []

    results = []
    keyword_lower = keyword.lower()

    def scan_directory(dir_path: Path, relative_prefix: str = ""):
        if not dir_path.exists() or not dir_path.is_dir():
            return
        try:
            for item in dir_path.iterdir():
                if item.is_file():
                    if keyword_lower in item.name.lower():
                        rel_path = f"./{relative_prefix}/{item.name}" if relative_prefix else f"./{item.name}"
                        stat = item.stat()
                        results.append({
                            "name": item.name,
                            "path": rel_path,
                            "size": stat.st_size,
                            "is_folder": False,
                            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        })
                elif item.is_dir():
                    new_prefix = f"{relative_prefix}/{item.name}" if relative_prefix else item.name
                    scan_directory(item, new_prefix)
        except PermissionError:
            pass

    scan_directory(BASE_DIR)
    results.sort(key=lambda x: x["name"].lower())
    return results


@app.post("/api/script-results/upload")
async def upload_script_result(result: ScriptResultUpload, db: Session = Depends(get_db)):
    result_id = str(uuid.uuid4())

    step_results_db = []
    for step in result.step_results:
        step_db = StepResultModel(
            id=str(uuid.uuid4()),
            step_name=step.step_name,
            step_order=step.step_order,
            action_type=step.action_type,
            status=step.status,
            duration=step.duration,
            error=step.error,
            error_stack=step.error_stack,
            screenshot=step.screenshot,
            action_values=step.action_values or {}
        )
        step_results_db.append(step_db)

    script_result = ScriptResult(
        id=result_id,
        task_id=result.task_id,
        task_name=result.task_name,
        script_name=result.script_name,
        started_at=result.started_at,
        finished_at=result.finished_at,
        status=result.status,
        parameters=result.parameters or {},
        total_steps=result.total_steps,
        passed_steps=result.passed_steps,
        failed_steps=result.failed_steps,
        skipped_steps=result.skipped_steps,
        total_duration=result.total_duration,
        pass_rate=result.pass_rate,
        username=result.username or "",
        script_count=result.script_count,
        step_results=step_results_db,
        created_at=datetime.utcnow()
    )
    db.add(script_result)
    db.commit()
    db.refresh(script_result)

    return {"message": "脚本执行结果已保存", "id": result_id}


@app.get("/api/script-results")
async def list_script_results(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    username: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(ScriptResult)

    if status:
        query = query.filter(ScriptResult.status == status)
    if keyword:
        keyword_lower = f"%{keyword}%"
        query = query.filter(
            or_(
                ScriptResult.task_name.ilike(keyword_lower),
                ScriptResult.script_name.ilike(keyword_lower)
            )
        )
    if username:
        usernames = [u.strip() for u in username.split(',') if u.strip()]
        if len(usernames) == 1:
            query = query.filter(ScriptResult.username == usernames[0])
        else:
            query = query.filter(ScriptResult.username.in_(usernames))
    if start_date:
        query = query.filter(ScriptResult.started_at >= start_date + "T00:00:00")
    if end_date:
        query = query.filter(ScriptResult.started_at <= end_date + "T23:59:59")

    total = query.count()
    results = query.order_by(ScriptResult.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    paginated = [r.to_dict() for r in results]

    return {
        "data": paginated,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
    }


@app.get("/api/script-results/stats")
async def get_script_results_stats(db: Session = Depends(get_db)):
    total = db.query(ScriptResult).count()

    if total == 0:
        return {
            "total": 0,
            "success_rate": 0.0,
            "fail_rate": 0.0,
            "avg_duration": 0.0,
        }

    success_count = db.query(ScriptResult).filter(ScriptResult.status == "completed").count()
    failure_count = db.query(ScriptResult).filter(ScriptResult.status == "failed").count()

    total_duration_result = db.query(func.sum(ScriptResult.total_duration)).scalar() or 0.0
    avg_duration = total_duration_result / total if total > 0 else 0.0

    return {
        "total": total,
        "success_rate": round((success_count / total) * 100, 2) if total > 0 else 0.0,
        "fail_rate": round((failure_count / total) * 100, 2) if total > 0 else 0.0,
        "avg_duration": round(avg_duration, 2),
    }


@app.get("/api/script-results/trend")
async def get_script_results_trend(db: Session = Depends(get_db)):
    all_results = db.query(ScriptResult).all()

    trend_map = {}
    for r in all_results:
        started_at = r.started_at or ""
        if started_at:
            date_str = started_at[:10]
            if date_str not in trend_map:
                trend_map[date_str] = {
                    "date": date_str,
                    "total": 0,
                    "success": 0,
                    "fail": 0,
                    "avg_duration": 0.0,
                    "total_duration": 0.0,
                }
            trend_map[date_str]["total"] += 1
            if r.status == "completed":
                trend_map[date_str]["success"] += 1
            elif r.status == "failed":
                trend_map[date_str]["fail"] += 1
            trend_map[date_str]["total_duration"] += r.total_duration or 0.0

    trend_list = list(trend_map.values())
    for item in trend_list:
        if item["total"] > 0:
            item["avg_duration"] = round(item["total_duration"] / item["total"], 2)
        del item["total_duration"]

    trend_list.sort(key=lambda x: x["date"])

    return trend_list


@app.get("/api/script-results/anomalies")
async def get_script_results_anomalies(db: Session = Depends(get_db)):
    failed_results = db.query(ScriptResult).filter(ScriptResult.status == "failed").all()

    error_type_dist = {}
    failing_steps = {}

    for r in failed_results:
        for step in r.step_results:
            if step.status == "failed":
                error = step.error or "Unknown Error"
                error_type_dist[error] = error_type_dist.get(error, 0) + 1

                step_name = step.step_name or "Unknown Step"
                if step_name not in failing_steps:
                    failing_steps[step_name] = {
                        "step_name": step_name,
                        "fail_count": 0,
                        "error_types": {},
                    }
                failing_steps[step_name]["fail_count"] += 1
                if error:
                    failing_steps[step_name]["error_types"][error] = (
                        failing_steps[step_name]["error_types"].get(error, 0) + 1
                    )

    error_distribution = [
        {"error_type": k, "count": v, "type": k}
        for k, v in sorted(error_type_dist.items(), key=lambda x: x[1], reverse=True)
    ]

    top_failing_steps = sorted(
        failing_steps.values(), key=lambda x: x["fail_count"], reverse=True
    )[:10]

    return {
        "error_type_distribution": error_distribution,
        "error_types": error_distribution,
        "top_failing_steps": top_failing_steps,
    }


@app.get("/api/script-results/{result_id}")
async def get_script_result(result_id: str, db: Session = Depends(get_db)):
    result = db.query(ScriptResult).filter(ScriptResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="结果记录不存在")

    return result.to_dict()


@app.delete("/api/script-results/{result_id}")
async def delete_script_result(result_id: str, db: Session = Depends(get_db)):
    result = db.query(ScriptResult).filter(ScriptResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="结果记录不存在")

    try:
        db.delete(result)
        db.commit()
        return {"message": "结果记录已删除"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除失败")


@app.get("/api/config")
async def get_configuration(db: Session = Depends(get_db)):
    configs = db.query(Config).all()
    config_dict = {}
    for config in configs:
        config_dict[config.key] = config.value

    if not config_dict:
        config_dict = {
            'management_platform_url': 'http://localhost:8001/api/script-results/upload',
            'username': ''
        }

    return config_dict


@app.post("/api/config")
async def update_configuration(data: dict, db: Session = Depends(get_db)):
    for key, value in data.items():
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
        else:
            config = Config(key=key, value=value)
            db.add(config)

    db.commit()

    configs = db.query(Config).all()
    config_dict = {config.key: config.value for config in configs}

    return {"message": "配置更新成功", "config": config_dict}
