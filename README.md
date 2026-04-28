# 自动化测试平台

这是一个混合架构的自动化测试项目，核心由 `Django + Django REST Framework + Playwright` 驱动，并内置一个独立的自动化管理子平台 `automated_management_platform`，其技术栈为 `FastAPI + Vue 3 + Vite`。

项目当前既包含主测试平台，也包含结果管理与文件管理子系统，因此在本地开发时通常需要按需启动多个服务。

## 项目概览

### 主平台（自动化测试平台）

- 基于 `Django 4.2`
- 使用 `Playwright` 执行 Web 自动化测试
- 提供脚本编辑、录制、执行、结果管理、报告查看等能力
- 同时提供 Django 模板页面和 REST API

### 自动化管理子平台

- 后端基于 `FastAPI`
- 前端基于 `Vue 3 + Vite`
- 提供 JSON 文件管理、脚本结果接收、结果分析、全局配置管理等能力

## 技术栈

### 后端

- `Django`
- `Django REST Framework`
- `Playwright`
- `Celery`
- `FastAPI`
- `SQLAlchemy`

### 前端

- `Django Templates`
- `Vue 3`
- `Vite`
- `Axios`

### 数据存储

- `SQLite3` 主库：`db.sqlite3`
- `SQLite` 子平台库：`automated_management_platform/backend/automated_management.db`
- 文件结果目录：`test_results`
- 截图目录：`media/screenshots`
- 子平台上传目录：`automated_management_platform/backend/uploads`

## 仓库结构

```text
playwright集成/
├── automation_test_platform/         # Django 项目配置
├── core/                             # 核心能力：分组、仪表盘、执行引擎、任务调度等
├── products/                         # 产品类型、参数与选项管理
├── test_manager/                     # 测试任务、执行结果、报告、邮件通知
├── script_editor/                    # 脚本、步骤、定位器、动作集合、录制与导入导出
├── automated_management_platform/    # 自动化管理子平台
│   ├── backend/                      # FastAPI 后端
│   └── frontend/                     # Vue 3 + Vite 前端
├── templates/                        # Django 模板页面
├── static/                           # 静态资源
├── media/                            # 媒体文件
├── test_results/                     # 测试结果 JSON
├── manage.py                         # Django 管理入口
├── requirements.txt                  # 主平台 Python 依赖
├── setup.bat                         # Windows 一键初始化脚本
├── run.bat                           # Django 启动脚本
├── run_celery.bat                    # Celery Worker 启动脚本
├── db.sqlite3                        # Django 主数据库
└── .env.example                      # 示例环境变量模板
```

## 核心模块说明

### `core`

主平台公共核心模块，负责仪表盘、分组管理、错误配置、Playwright 执行引擎、任务执行调度等。

### `products`

产品类型、参数、选项管理模块，用于支持测试任务的参数化配置。

### `test_manager`

负责测试任务、任务脚本关联、执行结果、测试报告、结果上传与通知能力。

### `script_editor`

项目中最核心的业务模块之一，负责测试脚本、测试步骤、元素定位器、动作集合、脚本录制、版本管理、导入导出等能力。

### `automated_management_platform`

独立管理子平台：

- `backend` 提供文件管理、结果接收、结果分析和配置 API
- `frontend` 提供管理界面

## 运行架构

本仓库不是单一服务，而是混合架构：

1. `Django` 主平台提供主业务页面和 API，默认端口 `8000`
2. `FastAPI` 子平台后端提供管理 API，默认端口 `8001`
3. `Vue + Vite` 子平台前端提供管理界面，默认端口 `5173`

其中主平台本身已经带有 Django 模板页面，因此只使用主平台时，不一定需要启动 Vue 前端。

## 环境要求

- Python `3.9+`
- Node.js `18+`，建议同时安装 `npm`
- Windows 环境下可直接使用仓库内的 `.bat` 脚本
- 首次运行 Playwright 前需要安装浏览器

## 快速开始

### 1. 初始化 Django 主平台

项目已经提供 Windows 初始化脚本：

```bat
setup.bat
```

该脚本会自动执行以下操作：

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python manage.py migrate
python manage.py init_sample_data
```

如果你希望手动执行，也可以按上面的顺序逐步安装。

### 2. 启动 Django 主平台

```bat
run.bat
```

或手动执行：

```bat
venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
```

启动后可访问：

- 主平台页面：`http://127.0.0.1:8000`
- Django API 根路径：`http://127.0.0.1:8000/api/`

### 3. 启动自动化管理子平台后端

```bat
cd automated_management_platform\backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

默认接口地址：

- `http://127.0.0.1:8001`

### 4. 启动自动化管理子平台前端

```bat
cd automated_management_platform\frontend
npm install
npm run dev
```

默认访问地址：

- `http://127.0.0.1:5173`

## 常用启动顺序

如果你只想使用主自动化测试平台：

1. 初始化 Python 依赖
2. 安装 Playwright 浏览器
3. 执行 `python manage.py migrate`
4. 启动 Django 服务

如果你要联动结果管理子平台：

1. 启动 Django 主平台
2. 启动 FastAPI 子平台后端
3. 启动 Vue 子平台前端

## 数据库与初始化

### Django 主平台

- 数据库：`db.sqlite3`
- 配置位置：`automation_test_platform/settings.py`
- 初始化方式：

```bat
python manage.py migrate
python manage.py init_sample_data
```

### FastAPI 子平台

- 默认数据库连接：`sqlite:///./automated_management.db`
- 常见数据库文件位置：`automated_management_platform/backend/automated_management.db`
- 建表方式：服务启动时自动执行 `init_db()`

如果仓库里已有旧版 JSON 数据，可执行迁移脚本：

```bat
cd automated_management_platform\backend
python migrate_json_to_db.py
```

## 配置说明

### Django 主平台配置

主配置文件位于 `automation_test_platform/settings.py`。

当前代码里真正通过环境变量读取的主要配置有：

- `MARKETPLACE_API_BASE`
- `MANAGEMENT_PLATFORM_URL`

其余如 `SECRET_KEY`、`DEBUG`、`ALLOWED_HOSTS`、`CELERY_BROKER_URL`、`PLAYWRIGHT_HEADLESS` 等配置，当前主要仍写在代码中。

### `.env.example`

仓库提供了 `.env.example`，但需要注意：

- 该文件更像配置模板
- 其中部分变量当前代码并没有完整接线读取
- 不应假设复制为 `.env` 后所有变量都会自动生效

### FastAPI 子平台配置

子平台配置来源主要有三类：

1. 环境变量 `DATABASE_URL`
2. 数据库中的 `config` 表
3. 回退配置文件

## Celery 说明

仓库内包含 `run_celery.bat`，但当前 `automation_test_platform/settings.py` 中配置为：

- `CELERY_BROKER_URL = 'memory://'`
- `CELERY_RESULT_BACKEND = 'cache+memory://'`
- `CELERY_TASK_ALWAYS_EAGER = True`

这意味着当前更偏向本地开发态的同步执行模式，而不是标准的 Redis 异步任务部署。因此：

- 本地开发通常不强制要求启动 Celery Worker
- 如果未来切换到 Redis 等真实消息中间件，再补充异步部署方案更合适

## 前端代理注意事项

`automated_management_platform/frontend/vite.config.js` 中当前代理目标写死为：

```js
const proxyTarget = 'http://192.168.20.193:8001'
```

这通常只适用于特定内网环境。若你在本地开发，请先改成自己的实际后端地址，例如：

```js
const proxyTarget = 'http://127.0.0.1:8001'
```

否则 Vue 前端可能无法正确代理到 FastAPI 服务。

## 主要访问入口

### Django 主平台

- 首页：`/`
- 分组管理：`/groups/`
- 全局配置：`/global-config/`
- 动作集合：`/action-sets/`
- 脚本列表：`/scripts/`
- 可视化编辑器：`/editor/`
- 测试任务：`/tasks/`
- 结果列表：`/results/`
- 错误配置：`/error-config/`

### API 路由前缀

- `api/core/`
- `api/products/`
- `api/tests/`
- `api/scripts/`

## 已有文档

仓库中已经有较完整的补充文档，可作为 README 之外的深入参考：

- `PROJECT_DOCUMENTATION.md`
- `API_COMPLETE_DOCUMENTATION.md`
- `automated_management_platform/API_DOCUMENTATION.md`
- `定位器类型和值完整指南.md`

## 测试现状

当前仓库内未看到完整统一的自动化测试工程结构，例如：

- 未发现标准化的 `pytest` 配置
- 未发现统一的顶层 `tests/` 目录
- 未发现独立的 Playwright 测试配置文件

目前更接近“业务平台 + 少量辅助验证脚本”的状态，因此建议优先以手工验证和核心流程验证为主。

## 已知注意事项

1. 主平台是 Django 模板页面与 API 并存，并非纯前后端分离项目。
2. 子平台 `automated_management_platform` 才是标准的前后端分离结构。
3. 当前仓库默认使用 SQLite，适合本地开发与演示。
4. 项目会同时写入数据库和文件目录，排查问题时需要同时关注两类存储。
5. 如果你此前清空过数据库，需要重新执行初始化命令以恢复示例数据。

## 推荐的本地开发方式

### 仅体验主平台

```bat
setup.bat
run.bat
```

### 联调完整项目

```bat
run.bat
cd automated_management_platform\backend && uvicorn main:app --host 0.0.0.0 --port 8001 --reload
cd automated_management_platform\frontend && npm install && npm run dev
```
