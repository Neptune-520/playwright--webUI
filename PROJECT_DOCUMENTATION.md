# 自动化测试平台 (Automation Test Platform) - 完整项目文档

## 一、项目概述

本项目是一个基于 Django + Playwright 的 Web 自动化测试平台，支持测试脚本的创建、编辑、录制、执行、结果管理和报告生成。平台采用前后端分离架构，后端提供 RESTful API，前端通过 Django 模板渲染页面。

### 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Django 4.2 + Django REST Framework |
| 浏览器自动化 | Playwright |
| 异步任务 | Celery (内存 Broker) |
| 数据库 | SQLite3 |
| 前端 | Vue 3 + Vite (automated_management_platform), Django 模板 |
| 依赖管理 | pip + npm |
| 其他 | openpyxl, jsonschema, django-cors-headers |

### 目录结构

```
new-python/
├── automation_test_platform/    # Django 项目配置
├── core/                        # 核心功能模块（分组、引擎、任务调度）
├── products/                    # 产品管理模块
├── test_manager/                # 测试管理模块（任务、结果、报告）
├── script_editor/               # 脚本编辑器模块（脚本、元素、动作集合、录制）
├── automated_management_platform/  # 自动化管理子平台（前后端）
├── templates/                   # HTML 模板文件
├── static/                      # 静态文件
├── media/                       # 媒体文件（截图等）
├── test_results/                # 测试结果 JSON 文件
├── venv/                        # Python 虚拟环境
├── db.sqlite3                   # SQLite 数据库
├── error_config.json            # 错误配置文件
├── manage.py                    # Django 管理入口
└── requirements.txt             # Python 依赖
```

---

## 二、项目配置 (`automation_test_platform/`)

### 2.1 `settings.py` - 项目设置

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `BASE_DIR` | Path | 项目根目录 | 项目基础路径 |
| `SECRET_KEY` | str | `'django-insecure-dev-key-change-in-production'` | Django 密钥 |
| `DEBUG` | bool | `True` | 调试模式 |
| `ALLOWED_HOSTS` | list | `['*']` | 允许的主机名 |
| `INSTALLED_APPS` | list | - | 已安装应用列表，包含: `core`, `products`, `test_manager`, `script_editor`, `rest_framework`, `corsheaders`, `django_celery_results` |
| `MIDDLEWARE` | list | - | 中间件列表，含 `CorsMiddleware` |
| `ROOT_URLCONF` | str | `'automation_test_platform.urls'` | 根 URL 配置 |
| `TEMPLATES` | list | - | 模板配置，DIRS 含 `BASE_DIR / 'templates'` |
| `WSGI_APPLICATION` | str | `'automation_test_platform.wsgi.application'` | WSGI 应用 |
| `DATABASES` | dict | SQLite3 | 数据库配置，使用 `db.sqlite3` |
| `LANGUAGE_CODE` | str | `'zh-hans'` | 语言代码 |
| `TIME_ZONE` | str | `'Asia/Shanghai'` | 时区 |
| `STATIC_URL` | str | `'/static/'` | 静态文件 URL |
| `STATICFILES_DIRS` | list | `[BASE_DIR / 'static']` | 静态文件目录 |
| `STATIC_ROOT` | Path | `BASE_DIR / 'staticfiles'` | 静态文件收集目录 |
| `MEDIA_URL` | str | `'/media/'` | 媒体文件 URL |
| `MEDIA_ROOT` | Path | `BASE_DIR / 'media'` | 媒体文件根目录 |
| `REST_FRAMEWORK` | dict | - | DRF 配置: `AllowAny` 权限, 分页 20 条/页 |
| `CORS_ALLOW_ALL_ORIGINS` | bool | `True` | 允许所有跨域来源 |
| `CELERY_BROKER_URL` | str | `'memory://'` | Celery Broker URL |
| `CELERY_RESULT_BACKEND` | str | `'cache+memory://'` | Celery 结果后端 |
| `CELERY_ACCEPT_CONTENT` | list | `['json']` | Celery 接受的内容类型 |
| `CELERY_TASK_SERIALIZER` | str | `'json'` | Celery 任务序列化器 |
| `CELERY_RESULT_SERIALIZER` | str | `'json'` | Celery 结果序列化器 |
| `CELERY_TASK_ALWAYS_EAGER` | bool | `True` | Celery 同步执行模式 |
| `PLAYWRIGHT_HEADLESS` | bool | `False` | Playwright 无头模式 |
| `PLAYWRIGHT_TIMEOUT` | int | `30000` | Playwright 默认超时(ms) |
| `PLAYWRIGHT_SLOW_MO` | int | `1000` | Playwright 操作延迟(ms) |
| `MARKETPLACE_API_BASE` | str | `'http://127.0.0.1:8000'` | 集合文件 API 地址（可环境变量覆盖） |
| `MANAGEMENT_PLATFORM_URL` | str | `'http://localhost:8001/api/script-results/upload'` | 管理平台上传地址（可环境变量覆盖） |
| `TEST_SCRIPTS_DIR` | Path | `BASE_DIR / 'test_scripts'` | 测试脚本文件目录 |
| `ELEMENT_LOCATORS_DIR` | Path | `BASE_DIR / 'element_locators'` | 元素定位器文件目录 |
| `TEST_RESULTS_DIR` | Path | `BASE_DIR / 'test_results'` | 测试结果文件目录 |
| `SCREENSHOTS_DIR` | Path | `MEDIA_ROOT / 'screenshots'` | 截图文件目录 |

### 2.2 `urls.py` - 主路由

| URL 前缀 | 包含模块 | 说明 |
|----------|---------|------|
| `admin/` | `django.contrib.admin` | Django 管理后台 |
| `api/core/` | `core.urls` | 核心 API |
| `api/products/` | `products.urls` | 产品管理 API |
| `api/tests/` | `test_manager.urls` | 测试管理 API |
| `api/scripts/` | `script_editor.urls` | 脚本编辑器 API |
| `/` | `automation_test_platform.frontend_urls` | 前端页面 |

### 2.3 `frontend_urls.py` - 前端页面路由

| URL 路径 | 视图模板 | 名称 |
|----------|---------|------|
| `/` | `dashboard.html` | `dashboard` |
| `/groups/` | `groups.html` | `groups-list` |
| `/global-config/` | `global_config.html` | `global-config` |
| `/action-sets/` | `action_sets.html` | `action-sets-list` |
| `/scripts/` | `scripts.html` | `scripts-list` |
| `/editor/` | `visual_editor.html` | `visual-editor` |
| `/tasks/` | `tasks.html` | `tasks-list` |
| `/results/` | `results.html` | `results-list` |
| `/results/<int:task_id>/` | `result_detail.html` | `result-detail` |
| `/test-input/` | `test_input.html` | `test-input` |
| `/error-config/` | `error_config.html` | `error-config` |

### 2.4 `celery.py` - Celery 配置

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `app` | Celery | Celery 实例，名称 `'automation_test_platform'`，从 Django settings 读取配置，自动发现任务 |

### 2.5 `__init__.py`

导出 `celery_app`，确保 Celery 在 Django 启动时加载。

### 2.6 `wsgi.py` / `asgi.py`

标准 Django WSGI/ASGI 配置入口，设置 `DJANGO_SETTINGS_MODULE`。

---

## 三、核心模块 (`core/`)

### 3.1 数据模型 (`models.py`)

#### `Group` - 分组模型

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | CharField(max_length=100) | 分组名称 |
| `code` | CharField(max_length=50) | 分组代码 |
| `type` | CharField(max_length=20, choices) | 分组类型，选项: `script`(脚本分组), `action_set`(动作集合分组), `task`(任务分组) |
| `description` | TextField | 描述，默认空 |
| `parent` | ForeignKey('self') | 父分组，支持层级结构 |
| `order` | IntegerField | 排序，默认 0 |
| `created_by` | ForeignKey(User) | 创建人 |
| `created_at` | DateTimeField | 创建时间，自动 |
| `updated_at` | DateTimeField | 更新时间，自动 |

**属性:**
- `full_path` (property): 返回完整层级路径，如 `父分组 / 子分组`
- `unique_together`: `['code', 'type']`

### 3.2 序列化器 (`serializers.py`)

#### `GroupSerializer`

| 字段 | 来源 | 说明 |
|------|------|------|
| `id` | 模型 | 主键 |
| `name` | 模型 | 分组名称 |
| `code` | 模型 | 分组代码 |
| `type` | 模型 | 分组类型 |
| `type_display` | `get_type_display` | 类型显示名（只读） |
| `description` | 模型 | 描述 |
| `parent` | 模型 | 父分组 ID |
| `order` | 模型 | 排序 |
| `full_path` | ReadOnlyField | 完整路径（只读） |
| `children_count` | SerializerMethodField | 子分组数量 |
| `created_by` | 模型 | 创建人 ID |
| `created_at` | 模型 | 创建时间 |
| `updated_at` | 模型 | 更新时间 |

`get_children_count(obj)`: 返回 `obj.children.count()`

#### `GroupCreateSerializer`

字段: `id`, `name`, `code`, `type`, `description`, `parent`, `order`

`create()`: 从请求上下文获取用户并创建分组

### 3.3 API 接口 (`views.py` + `urls.py`)

| 方法 | URL | 函数名 | 说明 |
|------|-----|--------|------|
| GET | `/api/core/health/` | `health_check` | 健康检查，返回 `{'status': 'ok'}` |
| GET | `/api/core/dashboard/` | `dashboard` | 仪表盘统计，返回任务/脚本/元素统计和最近任务 |
| GET/POST | `/api/core/groups/` | `group_list` | 分组列表/创建 |
| GET/PUT/DELETE | `/api/core/groups/<int:pk>/` | `group_detail` | 分组详情/更新/删除 |
| DELETE | `/api/core/scripts/clear-screenshots/` | `clear_screenshots` | 清理截图文件 |
| DELETE | `/api/core/scripts/clear-task-results/` | `clear_task_results` | 清理任务结果文件 |
| GET/POST | `/api/core/error-config/` | `error_config_list` | 错误配置列表/新增 |
| PUT | `/api/core/error-config/<int:config_id>/` | `update_error_config` | 更新错误配置 |
| DELETE | `/api/core/error-config/<int:config_id>/delete/` | `delete_error_config` | 删除错误配置 |

**`dashboard` 返回数据结构:**

```json
{
  "statistics": {
    "total_tasks": 0,
    "running_tasks": 0,
    "completed_tasks": 0,
    "failed_tasks": 0,
    "total_scripts": 0,
    "published_scripts": 0,
    "total_elements": 0,
    "pass_rate": 0.0
  },
  "recent_tasks": [{"id": 1, "name": "", "status": "", "created_at": ""}]
}
```

### 3.4 信号 (`signals.py`)

| 信号名 | 类型 | 说明 |
|--------|------|------|
| `script_execution_completed` | Django Signal | 脚本执行完成信号（已废弃） |

### 3.5 信号处理器 (`signal_handlers.py`)

| 函数名 | 说明 |
|--------|------|
| `on_script_execution_completed(sender, **kwargs)` | 已废弃，仅记录日志 |
| `_check_and_update_task_group_status(task_group_id)` | 已废弃，无操作 |

### 3.6 任务调度 (`tasks.py`)

#### Celery 任务

| 任务名 | 类型 | 说明 |
|--------|------|------|
| `execute_test_task` | `@shared_task(bind=True)` | 执行单脚本测试任务 |
| `execute_multi_script_task` | `@shared_task(bind=True)` | 执行多脚本测试任务 |
| `cleanup_old_results` | `@shared_task` | 清理旧测试结果（默认30天） |

#### 同步包装函数

| 函数名 | 说明 |
|--------|------|
| `run_test_task_sync(task_id)` | 单脚本同步执行包装器 |
| `run_multi_script_task_sync(task_id)` | 多脚本同步执行包装器 |
| `execute_test_task_sync_for_aggregate(task_id, celery_task_id)` | 聚合任务同步执行包装器 |

#### 内部执行函数

| 函数名 | 参数 | 返回 | 说明 |
|--------|------|------|------|
| `_execute_test_task_internal(task_id, celery_task_id)` | 任务ID, Celery任务ID | result_data dict | 单脚本内部执行逻辑 |
| `_execute_multi_script_internal(task_id, celery_task_id)` | 任务ID, Celery任务ID | result_data dict | 多脚本内部执行逻辑 |
| `_execute_single_script_in_task(task_id, script, parameters, step_offset, global_config)` | 任务ID, 脚本, 参数, 步骤偏移, 全局配置 | results list | 在多脚本任务中执行单个脚本 |
| `execute_step(loop, engine, step, parameters, step_screenshot, global_config)` | 事件循环, 引擎, 步骤, 参数, 截图标志, 全局配置 | result dict | 执行单个测试步骤 |
| `execute_action_set_step(loop, engine, as_step, parameters, step_screenshot)` | 事件循环, 引擎, 动作集合步骤, 参数, 截图标志 | result dict | 执行动作集合中的步骤 |

**`execute_step` 返回结构:**

```json
{
  "step_name": "",
  "step_order": 0,
  "action_type": "",
  "status": "passed|failed|skipped",
  "duration": 0.0,
  "error": null,
  "error_stack": null,
  "screenshot": null,
  "element_screenshot": null,
  "action_values": {},
  "logs": []
}
```

### 3.7 Playwright 引擎 (`playwright_engine.py` + `engines/`)

#### `PlaywrightEngine` (核心引擎, `playwright_engine.py`)

继承: `ScreenshotMixin`, `ElementLocatorMixin`, `ActionExecutorMixin`

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `headless` | bool | 无头模式 |
| `timeout` | int | 默认超时(ms) |
| `slow_mo` | int | 操作延迟(ms) |
| `screenshots_dir` | Path | 截图目录 |
| `global_config` | dict | 全局配置 |
| `browser` | Browser | Playwright 浏览器实例 |
| `context` | BrowserContext | 浏览器上下文 |
| `page` | Page | 当前页面 |
| `playwright` | - | Playwright 实例 |
| `start(browser_type, **context_options)` | async | 启动浏览器，返回 page |
| `close()` | async | 关闭浏览器 |

#### `ScreenshotMixin` (`engines/screenshot_manager.py`)

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `take_screenshot(name, full_page)` | 名称, 是否全页 | str(文件路径) | 截取页面截图 |
| `take_element_screenshot(element, name)` | 元素, 名称 | str(文件路径) | 截取元素截图 |

#### `ElementLocatorMixin` (`engines/element_locator.py`)

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `get_element(locator_config)` | 定位器配置 dict | Playwright Locator | 获取元素，支持备选定位器 |
| `_locate_element(locator_type, locator_value)` | 定位类型, 定位值 | Playwright Locator | 根据类型定位元素 |
| `_escape_css_id(id_value)` | ID值 | str | 转义 CSS ID 特殊字符 |
| `_debug_blocking_elements(locator)` | Locator | None | 调试遮挡元素（日志输出） |

**支持的定位类型:** `css`, `xpath`, `id`, `name`, `class_name`, `tag_name`, `text`, `role`, `test_id`, `placeholder`, `label`

**`locator_config` 结构:**

```json
{
  "type": "css",
  "value": "#myElement",
  "timeout": 10000,
  "backup_locators": [{"type": "css", "value": ".fallback"}]
}
```

#### `ActionExecutorMixin` (`engines/action_executor.py`)

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `execute_action(action_type, element_config, value, config, step_screenshot)` | 操作类型, 元素配置, 值, 配置, 截图标志 | result dict | 执行单个操作 |
| `execute_script(steps, take_screenshots, step_screenshot)` | 步骤列表, 截图标志, 步骤截图标志 | results list | 执行步骤列表 |

**支持的操作类型 (action_type):**

| 操作类型 | 说明 | 参数 |
|----------|------|------|
| `navigate` | 导航到URL | value=URL |
| `click` | 点击元素 | element_config, config.force |
| `fill` | 填充输入框 | element_config, value |
| `select` | 选择下拉选项 | element_config, value |
| `random_select` | 随机选择 | element_config, config.random_options, config.select_mode |
| `random_number` | 随机数值 | element_config, config.random_min, config.random_max |
| `check` | 勾选复选框 | element_config |
| `uncheck` | 取消勾选 | element_config |
| `wait` | 等待 | value=毫秒数 |
| `wait_for_selector` | 等待元素 | element_config, config.state |
| `screenshot` | 截图 | value=名称, config.full_page |
| `scroll` | 滚动 | element_config(可选), config.scroll_type, config.amount |
| `hover` | 悬停 | element_config |
| `focus` | 聚焦 | element_config |
| `press` | 按键 | element_config, value=键名 |
| `upload` | 上传文件 | element_config, value=文件路径 |
| `assert_text` | 断言文本 | element_config, value=期望文本 |
| `assert_visible` | 断言可见 | element_config |
| `assert_value` | 断言值 | element_config, value=期望值 |
| `custom` | 自定义操作 | value=Python代码 |
| `action_set` | 动作集合 | (在 tasks.py 中处理) |

#### `PlaywrightSync` (同步辅助类)

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `run_async(coro)` | 协程 | 结果 | 同步运行异步协程 |

### 3.8 错误信息管理器 (`engines/error_message_manager.py`)

#### `ErrorRule` 数据类

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | str | 规则名称 |
| `pattern` | str | 正则匹配模式 |
| `message_template` | str | 消息模板，支持 `{url}`, `{timeout}`, `{option}`, `{step_name}` 占位符 |
| `action_type` | Optional[str] | 关联操作类型 |

#### `ErrorMessageManager` 类

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `add_rule(name, pattern, message_template, action_type)` | 规则参数 | None | 添加错误规则 |
| `format_error_message(original_error, action_type, context)` | 原始错误, 操作类型, 上下文 | str | 格式化错误信息 |
| `get_supported_actions()` | - | List[str] | 获取支持的操作类型 |
| `get_rules_for_action(action_type)` | 操作类型 | List[ErrorRule] | 获取指定类型的规则 |
| `get_all_rules()` | - | List[Dict] | 获取所有规则字典 |

**全局实例:** `error_message_manager`

**内置规则覆盖:** 导航(页面关闭、超时、网络错误、被拦截)、点击(不可见、被遮挡、超时)、填写(非输入框、禁用、超时)、选择(非下拉框、选项不存在)、等待(元素未出现)、断言(文本/可见性/值不匹配)、上传(文件不存在)、通用(超时、浏览器关闭、元素未找到)

### 3.9 管理器类

#### `ScriptManager` (`managers/script_manager.py`)

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `__init__(scripts_dir)` | 脚本目录 | - | 初始化 |
| `save_script_to_json(script_data, filename)` | 脚本数据, 文件名 | Path | 保存脚本到 JSON |
| `load_script_from_json(filename)` | 文件名 | dict | 从 JSON 加载脚本 |
| `validate_script(script_data)` | 脚本数据 | `{'valid': bool, 'errors': list}` | 验证脚本数据（JSON Schema） |
| `list_script_files()` | - | List[str] | 列出脚本文件 |
| `delete_script_file(filename)` | 文件名 | bool | 删除脚本文件 |

**`SCRIPT_SCHEMA`**: JSON Schema 定义，要求 `name`, `target_url`, `steps` 为必填，`action_type` 枚举值限定。

#### `ElementLocatorManager` (`managers/element_locator_manager.py`)

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `save_locators_to_json(locators, filename)` | 定位器列表, 文件名 | Path | 保存定位器到 JSON |
| `load_locators_from_json(filename)` | 文件名 | List[dict] | 从 JSON 加载定位器 |
| `export_page_locators(page_url, locators)` | 页面URL, 定位器列表 | Path | 按域名+路径导出定位器 |

#### `TestResultExporter` (`managers/test_result_manager.py`)

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `__init__(results_dir)` | 结果目录 | - | 初始化 |
| `save_result(task_id, result_data)` | 任务ID, 结果数据 | Path | 保存结果到 `task_{id}_result.json` |
| `load_result(task_id)` | 任务ID | Optional[dict] | 加载结果 |
| `export_report(task_id, format)` | 任务ID, 格式(json/html) | Path | 导出测试报告 |

---

## 四、产品管理模块 (`products/`)

### 4.1 数据模型 (`models.py`)

#### `ProductType` - 产品类型

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | CharField(max_length=100, unique=True) | 产品类型名称 |
| `code` | CharField(max_length=50, unique=True) | 产品类型代码 |
| `description` | TextField | 描述，默认空 |
| `icon` | ImageField | 图标，上传到 `product_icons/` |
| `is_active` | BooleanField | 是否启用，默认 True |
| `created_at` | DateTimeField | 创建时间，自动 |
| `updated_at` | DateTimeField | 更新时间，自动 |

#### `ProductParameter` - 产品参数

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `product_type` | ForeignKey(ProductType) | 关联产品类型 |
| `name` | CharField(max_length=100) | 参数名称 |
| `code` | CharField(max_length=50) | 参数代码 |
| `input_type` | CharField(max_length=20, choices) | 输入类型: `text`, `select`, `radio`, `checkbox`, `number`, `color`, `file` |
| `is_required` | BooleanField | 是否必填，默认 True |
| `default_value` | CharField(max_length=255) | 默认值 |
| `placeholder` | CharField(max_length=100) | 占位提示 |
| `validation_regex` | CharField(max_length=255) | 验证正则 |
| `order` | IntegerField | 排序，默认 0 |
| `is_active` | BooleanField | 是否启用 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

`unique_together`: `['product_type', 'code']`

#### `ProductOption` - 参数选项

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `parameter` | ForeignKey(ProductParameter) | 关联参数 |
| `display_value` | CharField(max_length=100) | 显示值 |
| `actual_value` | CharField(max_length=255) | 实际值 |
| `price_modifier` | DecimalField(10,2) | 价格调整，默认 0 |
| `order` | IntegerField | 排序，默认 0 |
| `is_active` | BooleanField | 是否启用 |

### 4.2 API 接口 (`views.py` + `urls.py`)

| 方法 | URL | 函数名 | 说明 |
|------|-----|--------|------|
| GET/POST | `/api/products/` | `product_type_list` | 产品类型列表/创建 |
| GET/PUT/DELETE | `/api/products/<int:pk>/` | `product_type_detail` | 产品类型详情/更新/删除 |
| GET/POST | `/api/products/<int:product_type_id>/parameters/` | `product_parameter_list` | 产品参数列表/创建 |
| GET/PUT/DELETE | `/api/products/parameters/<int:pk>/` | `product_parameter_detail` | 产品参数详情/更新/删除 |

**ViewSet (同时存在):**
- `ProductTypeViewSet`: 列表用 `ProductTypeListSerializer`，详情用 `ProductTypeSerializer`
- `ProductParameterViewSet`
- `ProductOptionViewSet`

### 4.3 序列化器 (`serializers.py`)

| 序列化器 | 字段 | 说明 |
|----------|------|------|
| `ProductOptionSerializer` | id, display_value, actual_value, price_modifier, order, is_active | 参数选项 |
| `ProductParameterSerializer` | id, name, code, input_type, is_required, default_value, placeholder, validation_regex, order, is_active, **options**(嵌套) | 参数详情 |
| `ProductTypeSerializer` | id, name, code, description, icon, is_active, created_at, updated_at, **parameters**(嵌套), **parameters_count** | 产品类型详情 |
| `ProductTypeListSerializer` | id, name, code, description, is_active, **parameters_count** | 产品类型列表 |
| `ProductParameterCreateSerializer` | id, product_type, name, code, input_type, is_required, default_value, placeholder, validation_regex, order, is_active, **options**(嵌套，可写) | 参数创建/更新 |

---

## 五、测试管理模块 (`test_manager/`)

### 5.1 数据模型 (`models.py`)

#### `TestTask` - 测试任务

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | CharField(max_length=200) | 任务名称 |
| `script` | ForeignKey(TestScript) | 主测试脚本 |
| `status` | CharField(max_length=20, choices) | 状态: `pending`(待执行), `running`(执行中), `completed`(已完成), `failed`(失败), `cancelled`(已取消) |
| `parameters` | JSONField | 测试参数，默认 dict |
| `group` | ForeignKey(Group) | 分组（限 task 类型） |
| `scheduled_time` | DateTimeField | 计划执行时间 |
| `started_at` | DateTimeField | 开始时间 |
| `finished_at` | DateTimeField | 结束时间 |
| `celery_task_id` | CharField(max_length=100) | Celery 任务 ID |
| `task_group` | ForeignKey(TaskGroup) | 任务组（已废弃） |
| `is_aggregate_subtask` | BooleanField | 是否为聚合任务子任务 |
| `upload_to_management` | BooleanField | 是否上传至管理平台 |
| `management_platform_url` | CharField(max_length=500) | 管理平台 API 地址 |
| `upload_status` | CharField(max_length=20, choices) | 上传状态: `none`, `uploading`, `uploaded`, `failed`, `pending` |
| `send_email` | BooleanField | 是否发送邮件通知 |
| `created_by` | ForeignKey(User) | 创建人 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

**属性:**
- `script_count` (property): 返回 `task_scripts.count()`
- `get_all_scripts()`: 获取所有关联脚本

#### `TaskScript` - 任务脚本关联

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `task` | ForeignKey(TestTask) | 测试任务 |
| `script` | ForeignKey(TestScript) | 测试脚本 |
| `order` | IntegerField | 执行顺序 |
| `parameters` | JSONField | 测试参数 |

`unique_together`: `['task', 'script']`

#### `TaskGroup` - 任务组（已废弃）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | CharField(max_length=200) | 任务组名称 |
| `description` | TextField | 描述 |
| `status` | CharField(max_length=20, choices) | 状态: `pending`, `running`, `completed`, `partial`, `failed`, `cancelled` |
| `group` | ForeignKey(Group) | 分组 |
| `scheduled_time` | DateTimeField | 计划执行时间 |
| `started_at` | DateTimeField | 开始时间 |
| `finished_at` | DateTimeField | 结束时间 |
| `celery_task_id` | CharField(max_length=100) | Celery 任务 ID |
| `created_by` | ForeignKey(User) | 创建人 |

**属性:** `total_scripts`, `completed_scripts`, `failed_scripts`

#### `TaskGroupItem` - 任务组项（已废弃）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `task_group` | ForeignKey(TaskGroup) | 任务组 |
| `script` | ForeignKey(TestScript) | 测试脚本 |
| `order` | IntegerField | 执行顺序 |
| `parameters` | JSONField | 测试参数 |
| `status` | CharField(max_length=20, choices) | 状态: `pending`, `running`, `completed`, `failed`, `skipped` |
| `task` | ForeignKey(TestTask) | 关联任务 |
| `started_at` | DateTimeField | 开始时间 |
| `finished_at` | DateTimeField | 结束时间 |
| `error_message` | TextField | 错误信息 |

#### `TestResult` - 测试结果

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `task` | ForeignKey(TestTask) | 测试任务 |
| `step_name` | CharField(max_length=200) | 步骤名称 |
| `step_order` | IntegerField | 步骤顺序 |
| `status` | CharField(max_length=20, choices) | 状态: `passed`, `failed`, `skipped`, `error` |
| `duration` | FloatField | 执行时长(秒) |
| `error_message` | TextField | 错误信息 |
| `error_stack` | TextField | 错误堆栈 |
| `screenshot` | ImageField | 截图 |
| `action_values` | JSONField | 操作值（如输入值、随机选择的值） |
| `logs` | JSONField | 执行日志 |
| `created_at` | DateTimeField | 创建时间 |

#### `TestReport` - 测试报告

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `task` | OneToOneField(TestTask) | 测试任务 |
| `total_steps` | IntegerField | 总步骤数 |
| `passed_steps` | IntegerField | 通过步骤数 |
| `failed_steps` | IntegerField | 失败步骤数 |
| `skipped_steps` | IntegerField | 跳过步骤数 |
| `total_duration` | FloatField | 总执行时长(秒) |
| `summary` | JSONField | 汇总数据 |
| `created_at` | DateTimeField | 创建时间 |

**属性:** `pass_rate` (property): 通过率百分比

### 5.2 API 接口 (`views.py` + `urls.py`)

| 方法 | URL | 函数名 | 说明 |
|------|-----|--------|------|
| GET/POST | `/api/tests/tasks/` | `task_list` | 任务列表(排除任务组子任务)/创建 |
| GET/PUT/DELETE | `/api/tests/tasks/<int:pk>/` | `task_detail` | 任务详情/更新/删除 |
| POST | `/api/tests/tasks/<int:task_id>/execute/` | `execute_task_view` | 执行任务 |
| POST | `/api/tests/tasks/<int:task_id>/stop/` | `stop_task` | 停止任务 |
| POST | `/api/tests/tasks/<int:task_id>/upload/` | `trigger_upload` | 触发上传结果到管理平台 |
| GET | `/api/tests/results/` | `result_list` | 结果列表(可按task_id过滤) |
| GET | `/api/tests/results/<int:pk>/` | `result_detail` | 结果详情 |
| GET | `/api/tests/results/<int:result_id>/screenshots/` | `get_test_screenshots` | 获取结果截图 |
| GET | `/api/tests/results/<int:task_id>/export/` | `export_test_report` | 导出测试报告(支持json格式) |

**辅助函数:**

| 函数名 | 参数 | 返回 | 说明 |
|--------|------|------|------|
| `get_management_platform_url()` | - | str | 获取管理平台URL（优先全局配置） |
| `get_username()` | - | str | 获取用户名（优先全局配置） |
| `upload_result_to_management(task_id)` | 任务ID | tuple[bool, Optional[str]] | 上传结果到管理平台 |

### 5.3 邮件通知 (`email_notification.py`)

| 函数名 | 参数 | 返回 | 说明 |
|--------|------|------|------|
| `send_task_notification(task_id, task_name, status, result_data, report_id)` | 任务ID, 名称, 状态, 结果数据, 报告ID | bool | 发送任务完成邮件通知 |

**功能特点:**
- 支持 SSL(465) 和 STARTTLS 端口
- 生成美观的 HTML 邮件（含通过率统计、报告链接）
- 支持单脚本和多脚本任务的不同邮件模板
- 支持中文通过率/失败率显示

### 5.4 序列化器 (`serializers.py`)

| 序列化器 | 说明 |
|----------|------|
| `TaskScriptSerializer` | 任务脚本关联，含 script_name, script_code |
| `TestResultSerializer` | 测试结果，含 status_display, original_error_message |
| `TestReportSerializer` | 测试报告，含 pass_rate |
| `TestTaskListSerializer` | 任务列表，含 script_name, status_display, results_count, report |
| `TestTaskWithReportListSerializer` | 带报告的任务列表（与 List 相同） |
| `TestTaskDetailSerializer` | 任务详情，含 results, report, scripts_passed, scripts_failed |
| `TestTaskCreateSerializer` | 任务创建，含 scripts(脚本ID列表), upload_to_management |
| `TestTaskExecuteSerializer` | 任务执行，含 parameters |
| `TaskGroupItemSerializer` | 任务组项（已废弃） |
| `TaskGroupListSerializer` | 任务组列表（已废弃） |
| `TaskGroupDetailSerializer` | 任务组详情（已废弃） |
| `TaskGroupCreateSerializer` | 任务组创建（已废弃） |

---

## 六、脚本编辑器模块 (`script_editor/`)

### 6.1 数据模型 (`models.py`)

#### `ElementLocator` - 元素定位器

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | CharField(max_length=100) | 元素名称 |
| `code` | CharField(max_length=50, unique=True) | 元素代码 |
| `locator_type` | CharField(max_length=20, choices) | 定位类型: `css`, `xpath`, `id`, `name`, `class_name`, `tag_name`, `text`, `role`, `test_id`, `placeholder`, `label` |
| `locator_value` | CharField(max_length=500) | 定位值 |
| `page_url` | URLField(max_length=500) | 所在页面URL |
| `description` | TextField | 描述 |
| `wait_timeout` | IntegerField | 等待超时(ms)，默认 10000 |
| `wait_state` | CharField(max_length=20, choices) | 等待状态: `visible`, `hidden`, `attached`, `detached` |
| `is_active` | BooleanField | 是否启用 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

**方法:** `to_playwright_locator()` -> 返回 `{'type', 'value', 'timeout', 'state'}`

#### `TestScript` - 测试脚本

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | CharField(max_length=200) | 脚本名称 |
| `code` | CharField(max_length=50, unique=True) | 脚本代码 |
| `description` | TextField | 描述 |
| `status` | CharField(max_length=20, choices) | 状态: `draft`, `published`, `archived` |
| `version` | IntegerField | 版本号，默认 1 |
| `target_url` | URLField(max_length=500) | 目标网站URL |
| `script_data` | JSONField | 脚本数据 |
| `group` | ForeignKey(Group) | 分组（限 script 类型） |
| `created_by` | ForeignKey(User) | 创建人 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

#### `ScriptVersion` - 脚本版本

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `script` | ForeignKey(TestScript) | 关联脚本 |
| `version_number` | IntegerField | 版本号 |
| `script_data` | JSONField | 脚本数据 |
| `change_note` | TextField | 变更说明 |
| `created_by` | ForeignKey(User) | 创建人 |
| `created_at` | DateTimeField | 创建时间 |

`unique_together`: `['script', 'version_number']`

#### `TestStep` - 测试步骤

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `script` | ForeignKey(TestScript) | 测试脚本 |
| `name` | CharField(max_length=200) | 步骤名称 |
| `order` | IntegerField | 执行顺序 |
| `action_type` | CharField(max_length=30, choices) | 操作类型（见下方列表） |
| `element` | ForeignKey(ElementLocator) | 目标元素 |
| `action_set_ref` | ForeignKey(ActionSet) | 动作集合引用 |
| `action_set_params` | JSONField | 动作集合参数 |
| `action_value` | TextField | 操作值 |
| `action_config` | JSONField | 操作配置 |
| `description` | TextField | 描述 |
| `is_enabled` | BooleanField | 是否启用 |
| `continue_on_failure` | BooleanField | 失败时继续 |
| `retry_count` | IntegerField | 重试次数 |
| `retry_interval` | IntegerField | 重试间隔(ms) |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

**`ACTION_TYPE_CHOICES`:** `navigate`, `click`, `fill`, `select`, `random_select`, `random_number`, `check`, `uncheck`, `wait`, `wait_for_selector`, `screenshot`, `scroll`, `hover`, `focus`, `press`, `upload`, `assert_text`, `assert_visible`, `assert_value`, `action_set`, `custom`

#### `ActionSet` - 动作集合

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | CharField(max_length=200) | 动作集合名称 |
| `code` | CharField(max_length=50, unique=True) | 动作集合代码 |
| `description` | TextField | 描述 |
| `category` | CharField(max_length=100, choices) | 分类: `input`, `navigation`, `form`, `validation`, `general` |
| `group` | ForeignKey(Group) | 分组（限 action_set 类型） |
| `is_builtin` | BooleanField | 是否内置 |
| `is_active` | BooleanField | 是否启用 |
| `created_by` | ForeignKey(User) | 创建人 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

**方法:** `expand_to_steps(parameters=None)` -> 展开为 Playwright 步骤列表

#### `ActionSetStep` - 动作集合步骤

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `action_set` | ForeignKey(ActionSet) | 动作集合 |
| `name` | CharField(max_length=200) | 步骤名称 |
| `order` | IntegerField | 执行顺序 |
| `action_type` | CharField(max_length=30, choices) | 操作类型 |
| `locator_type` | CharField(max_length=20, choices) | 定位类型 |
| `locator_value` | CharField(max_length=500) | 定位值 |
| `locator_description` | CharField(max_length=200) | 定位描述 |
| `action_value` | TextField | 操作值 |
| `action_value_type` | CharField(max_length=20, choices) | 值类型: `static`, `parameter`, `expression` |
| `parameter_name` | CharField(max_length=100) | 参数名称 |
| `action_config` | JSONField | 操作配置 |
| `wait_timeout` | IntegerField | 等待超时(ms)，默认 10000 |
| `continue_on_failure` | BooleanField | 失败时继续 |
| `retry_count` | IntegerField | 重试次数 |
| `retry_interval` | IntegerField | 重试间隔(ms) |
| `random_options` | JSONField | 随机选项列表 |
| `select_mode` | CharField(max_length=20, choices) | 选择模式: `dropdown`, `click` |
| `random_min` | IntegerField | 随机数最小值 |
| `random_max` | IntegerField | 随机数最大值 |
| `force_click` | BooleanField | 强制点击 |
| `description` | TextField | 描述 |
| `is_enabled` | BooleanField | 是否启用 |

**方法:** `to_playwright_step(parameters=None)` -> 转换为 Playwright 步骤 dict

#### `ActionSetParameter` - 动作集合参数

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `action_set` | ForeignKey(ActionSet) | 动作集合 |
| `name` | CharField(max_length=100) | 参数名称 |
| `code` | CharField(max_length=50) | 参数代码 |
| `description` | TextField | 描述 |
| `default_value` | CharField(max_length=255) | 默认值 |
| `is_required` | BooleanField | 是否必填 |
| `order` | IntegerField | 排序 |

#### `GlobalConfig` - 全局配置（单例）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `headless_mode` | BooleanField | 无头模式，默认 False |
| `default_timeout` | IntegerField | 默认超时(ms)，默认 30000 |
| `step_screenshot` | BooleanField | 每步截图，默认 False |
| `slow_mo` | IntegerField | 操作延迟(ms)，默认 0 |
| `viewport_width` | IntegerField | 视口宽度，默认 1920 |
| `viewport_height` | IntegerField | 视口高度，默认 1080 |
| `scroll_distance` | IntegerField | 默认滚动距离(像素)，默认 500 |
| `scroll_direction` | CharField(max_length=10, choices) | 滚动方向: `down`, `up`, `left`, `right` |
| `marketplace_api_url` | CharField(max_length=500) | 集合文件 API 地址 |
| `management_platform_url` | CharField(max_length=500) | 管理平台 API 地址 |
| `username` | CharField(max_length=100) | 用户名 |
| `email_smtp_host` | CharField(max_length=200) | SMTP 服务器地址 |
| `email_smtp_port` | IntegerField | SMTP 端口，默认 465 |
| `email_username` | CharField(max_length=200) | 发件人邮箱 |
| `email_password` | CharField(max_length=200) | 邮箱密码/授权码 |
| `email_use_ssl` | BooleanField | 使用 SSL 连接，默认 True |
| `email_recipients` | CharField(max_length=1000) | 收件人列表（逗号分隔） |
| `email_enable` | BooleanField | 启用邮件通知，默认 False |
| `report_base_url` | CharField(max_length=500) | 报告访问地址前缀 |
| `updated_at` | DateTimeField | 更新时间 |
| `updated_by` | ForeignKey(User) | 更新人 |

**类方法:** `get_config()` -> 获取或创建全局配置单例(pk=1)

### 6.2 API 接口

#### 脚本管理 (`views.py`)

| 方法 | URL | 函数名 | 说明 |
|------|-----|--------|------|
| GET/POST | `/api/scripts/` | `script_list` | 脚本列表/创建 |
| GET/PUT/DELETE | `/api/scripts/<int:pk>/` | `script_detail` | 脚本详情/更新/删除 |
| POST | `/api/scripts/<int:script_id>/duplicate/` | `duplicate_script` | 复制脚本 |
| GET | `/api/scripts/<int:script_id>/versions/` | `script_versions` | 脚本版本列表 |
| GET | `/api/scripts/<int:script_id>/versions/<int:version_id>/` | `script_version_detail` | 版本详情 |
| GET/POST | `/api/scripts/elements/` | `element_list` | 元素定位器列表/创建 |
| GET/PUT/DELETE | `/api/scripts/elements/<int:pk>/` | `element_detail` | 元素详情/更新/删除 |
| GET/POST | `/api/scripts/steps/` | `step_list` | 测试步骤列表/创建 |
| GET/PUT/DELETE | `/api/scripts/steps/<int:pk>/` | `step_detail` | 步骤详情/更新/删除 |
| GET/POST | `/api/scripts/visual-editor/` | `visual_editor` | 可视化编辑器（获取操作类型/创建脚本） |
| POST | `/api/scripts/validate-script/` | `validate_script` | 验证脚本数据 |
| GET/PUT | `/api/scripts/global-config/` | `global_config` | 全局配置读取/更新 |
| POST | `/api/scripts/export/` | `export_scripts` | 批量导出脚本(json/excel) |
| GET | `/api/scripts/<int:pk>/export/` | `export_script_detail` | 单脚本导出 |
| POST | `/api/scripts/import/` | `import_scripts` | 导入脚本(json/excel) |

#### 录制功能 (`views.py`)

| 方法 | URL | 函数名 | 说明 |
|------|-----|--------|------|
| POST | `/api/scripts/recording/start/` | `recording_start` | 启动录制会话 |
| GET | `/api/scripts/recording/<str:session_id>/actions/` | `recording_actions` | 获取录制操作 |
| POST | `/api/scripts/recording/<str:session_id>/stop/` | `recording_stop` | 停止录制 |
| POST | `/api/scripts/recording/<str:session_id>/convert/` | `recording_convert` | 转换录制为脚本/动作集合 |

**内部函数:**
- `_convert_to_action_set(actions, name, code, user, data)`: 将录制操作转换为动作集合
- `_convert_to_script(actions, name, code, user, data)`: 将录制操作转换为脚本

#### 动作集合管理 (`views_actionset.py`)

| 方法 | URL | 函数名 | 说明 |
|------|-----|--------|------|
| GET/POST | `/api/scripts/action-sets/` | `action_set_list` | 动作集合列表(可按category过滤)/创建 |
| GET | `/api/scripts/action-sets/<int:pk>/` | `action_set_detail` | 动作集合详情/更新/删除 |
| GET | `/api/scripts/action-sets/<int:pk>/export/` | `action_set_export` | 导出动作集合 |
| POST | `/api/scripts/action-sets/export/` | `action_set_batch_export` | 批量导出 |
| POST | `/api/scripts/action-sets/import/` | `action_set_import` | 导入动作集合 |
| POST | `/api/scripts/action-sets/<int:pk>/expand/` | `action_set_expand` | 展开动作集合为步骤 |
| GET | `/api/scripts/action-sets/categories/` | `action_set_categories` | 获取分类列表 |
| GET/POST | `/api/scripts/action-sets/<int:action_set_id>/steps/` | `action_set_step_list` | 步骤列表/创建 |
| GET/PUT/DELETE | `/api/scripts/action-sets/steps/<int:pk>/` | `action_set_step_detail` | 步骤详情/更新/删除 |
| POST | `/api/scripts/action-sets/<int:action_set_id>/steps/reorder/` | `action_set_step_reorder` | 步骤重排序 |
| GET/POST | `/api/scripts/action-sets/<int:action_set_id>/parameters/` | `action_set_parameter_list` | 参数列表/创建 |
| GET/PUT/DELETE | `/api/scripts/action-sets/parameters/<int:pk>/` | `action_set_parameter_detail` | 参数详情/更新/删除 |

#### 集合文件市场 (`views_marketplace.py`)

| 方法 | URL | 函数名 | 说明 |
|------|-----|--------|------|
| GET | `/api/scripts/marketplace/items/` | `marketplace_list_items` | 列出市场文件（含文件夹） |
| GET | `/api/scripts/marketplace/search/` | `marketplace_search_items` | 搜索市场文件 |
| POST | `/api/scripts/marketplace/folder/` | `marketplace_create_folder` | 创建文件夹 |
| GET | `/api/scripts/marketplace/download/` | `marketplace_download_file` | 下载文件 |
| GET | `/api/scripts/marketplace/preview/` | `marketplace_preview_file` | 预览文件 |
| POST | `/api/scripts/marketplace/upload/` | `marketplace_upload_file` | 上传文件 |

**内部函数:**
- `get_marketplace_api_base()` -> 从全局配置获取 API 基地址
- `_marketplace_get(path, params)` -> 向市场 API 发 GET 请求
- `_marketplace_post(path, files, params)` -> 向市场 API 发 POST 请求
- `_get_file_metadata(data)` -> 提取文件元数据
- `_enrich_items_with_metadata(items, path)` -> 为文件项添加预览元数据

### 6.3 导入导出服务 (`services.py`)

#### `ScriptExportImportService`

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `export_scripts_to_json(script_ids)` | 脚本ID列表 | dict | 导出为 JSON 格式 |
| `export_scripts_to_excel(script_ids)` | 脚本ID列表 | Workbook | 导出为 Excel 格式（含6个Sheet） |
| `import_scripts_from_json(file_data, conflict_strategy, user)` | 文件数据, 冲突策略, 用户 | result dict | 从 JSON 导入 |
| `import_scripts_from_excel(file_data, conflict_strategy, user)` | 文件数据, 冲突策略, 用户 | result dict | 从 Excel 导入 |

**冲突策略:** `skip`(跳过), `overwrite`(覆盖), `rename`(重命名)

**Excel Sheet 结构:**
1. 脚本概览: 脚本代码, 名称, 描述, 状态, 版本, 目标URL, 分组代码, 分组名称
2. 脚本步骤: 14 列
3. 元素定位器: 10 列
4. 动作集合: 8 列
5. 动作集合步骤: 21 列
6. 动作集合参数: 7 列

### 6.4 录制引擎 (`recording_engine.py`)

#### `RecordingEngine`

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `playwright` | - | Playwright 实例 |
| `browser` | Browser | 浏览器实例 |
| `context` | BrowserContext | 浏览器上下文 |
| `page` | Page | 当前页面 |
| `actions` | List[Dict] | 已录制的操作列表 |
| `is_recording` | bool | 是否正在录制 |
| `session_id` | str | 会话 ID |
| `_action_index` | int | 操作计数器 |
| `start_recording(target_url, session_id, viewport_width, viewport_height)` | async | 启动录制 |
| `stop_recording()` | async | 停止录制，返回 actions 列表 |
| `get_actions()` | - | 获取已录制的操作列表 |
| `close()` | async | 关闭浏览器 |
| `_on_action(action_json)` | async | 处理录制到的操作 |
| `_generate_locator(element_info)` | static | 根据元素信息生成定位器列表 |
| `_generate_element_description(element_info)` | static | 生成元素描述 |
| `_generate_description(action_type, element_info, value, locators)` | static | 生成操作描述 |
| `_escape_css_id(id_value)` | static | 转义 CSS ID |

**定位器生成优先级:** `data-fixid` > `id` > `data-testid` > `name` > `placeholder` > `text` > `className` > `tagName`

### 6.5 录制会话管理 (`session_manager.py`)

#### `RecordingSession` 数据类

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | str | 会话 ID |
| `target_url` | str | 目标 URL |
| `status` | str | 状态: `starting`, `recording`, `stopped`, `error` |
| `actions` | List[Dict] | 录制操作列表 |
| `engine` | Optional[RecordingEngine] | 录制引擎实例 |
| `started_at` | Optional[datetime] | 开始时间 |
| `stopped_at` | Optional[datetime] | 停止时间 |
| `error` | Optional[str] | 错误信息 |
| `loop` | Optional[AbstractEventLoop] | 事件循环 |
| `thread` | Optional[Thread] | 运行线程 |
| `viewport_width` | int | 视口宽度 |
| `viewport_height` | int | 视口高度 |

#### `RecordingSessionManager` 类

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `create_session(target_url, user, viewport_width, viewport_height)` | cls | str(session_id) | 创建录制会话（在后台线程运行） |
| `get_session(session_id)` | cls | Optional[RecordingSession] | 获取会话 |
| `stop_session(session_id)` | cls | Optional[List[Dict]] | 停止会话，返回操作列表 |
| `get_session_actions(session_id)` | cls | Optional[Dict] | 获取会话操作数据 |
| `cleanup_session(session_id)` | cls | None | 清理会话资源 |
| `cleanup_old_sessions(max_age_seconds)` | cls | None | 清理旧会话（默认1小时） |

---

## 七、错误配置 (`error_config.json`)

自定义错误规则列表，每条规则包含:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 规则 ID |
| `name` | str | 规则名称 |
| `pattern` | str | 正则匹配模式 |
| `message_template` | str | 消息模板 |
| `action_type` | str | 关联操作类型 |

当前默认规则:
```json
[{
  "id": 1,
  "name": "通用_执行终止跳过其余步骤",
  "pattern": "(Skipped due to previous failure|由于之前的失败而跳过)",
  "message_template": "由于之前的失败而跳过",
  "action_type": ""
}]
```

---

## 八、完整 API 接口汇总

### Core API (`/api/core/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/core/health/` | 健康检查 |
| GET | `/api/core/dashboard/` | 仪表盘统计 |
| GET | `/api/core/groups/` | 分组列表 |
| POST | `/api/core/groups/` | 创建分组 |
| GET | `/api/core/groups/<id>/` | 分组详情 |
| PUT | `/api/core/groups/<id>/` | 更新分组 |
| DELETE | `/api/core/groups/<id>/` | 删除分组 |
| DELETE | `/api/core/scripts/clear-screenshots/` | 清理截图 |
| DELETE | `/api/core/scripts/clear-task-results/` | 清理结果 |
| GET | `/api/core/error-config/` | 错误配置列表 |
| POST | `/api/core/error-config/` | 新增错误配置 |
| PUT | `/api/core/error-config/<id>/` | 更新错误配置 |
| DELETE | `/api/core/error-config/<id>/delete/` | 删除错误配置 |

### Products API (`/api/products/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/products/` | 产品类型列表 |
| POST | `/api/products/` | 创建产品类型 |
| GET | `/api/products/<id>/` | 产品类型详情 |
| PUT | `/api/products/<id>/` | 更新产品类型 |
| DELETE | `/api/products/<id>/` | 删除产品类型 |
| GET | `/api/products/<id>/parameters/` | 产品参数列表 |
| POST | `/api/products/<id>/parameters/` | 创建产品参数 |
| GET | `/api/products/parameters/<id>/` | 参数详情 |
| PUT | `/api/products/parameters/<id>/` | 更新参数 |
| DELETE | `/api/products/parameters/<id>/` | 删除参数 |

### Test Manager API (`/api/tests/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tests/tasks/` | 任务列表 |
| POST | `/api/tests/tasks/` | 创建任务 |
| GET | `/api/tests/tasks/<id>/` | 任务详情 |
| PUT | `/api/tests/tasks/<id>/` | 更新任务 |
| DELETE | `/api/tests/tasks/<id>/` | 删除任务 |
| POST | `/api/tests/tasks/<id>/execute/` | 执行任务 |
| POST | `/api/tests/tasks/<id>/stop/` | 停止任务 |
| POST | `/api/tests/tasks/<id>/upload/` | 上传结果 |
| GET | `/api/tests/results/` | 结果列表 |
| GET | `/api/tests/results/<id>/` | 结果详情 |
| GET | `/api/tests/results/<id>/screenshots/` | 结果截图 |
| GET | `/api/tests/results/<id>/export/` | 导出报告 |

### Script Editor API (`/api/scripts/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/scripts/` | 脚本列表 |
| POST | `/api/scripts/` | 创建脚本 |
| GET | `/api/scripts/<id>/` | 脚本详情 |
| PUT | `/api/scripts/<id>/` | 更新脚本 |
| DELETE | `/api/scripts/<id>/` | 删除脚本 |
| POST | `/api/scripts/<id>/duplicate/` | 复制脚本 |
| GET | `/api/scripts/<id>/versions/` | 版本列表 |
| GET | `/api/scripts/<id>/versions/<vid>/` | 版本详情 |
| GET | `/api/scripts/<id>/export/` | 单脚本导出 |
| GET | `/api/scripts/elements/` | 元素列表 |
| POST | `/api/scripts/elements/` | 创建元素 |
| GET | `/api/scripts/elements/<id>/` | 元素详情 |
| PUT | `/api/scripts/elements/<id>/` | 更新元素 |
| DELETE | `/api/scripts/elements/<id>/` | 删除元素 |
| GET | `/api/scripts/steps/` | 步骤列表 |
| POST | `/api/scripts/steps/` | 创建步骤 |
| GET | `/api/scripts/steps/<id>/` | 步骤详情 |
| PUT | `/api/scripts/steps/<id>/` | 更新步骤 |
| DELETE | `/api/scripts/steps/<id>/` | 删除步骤 |
| GET | `/api/scripts/visual-editor/` | 可视化编辑器 |
| POST | `/api/scripts/visual-editor/` | 通过可视化编辑器创建 |
| POST | `/api/scripts/validate-script/` | 验证脚本 |
| GET | `/api/scripts/global-config/` | 全局配置 |
| PUT | `/api/scripts/global-config/` | 更新全局配置 |
| POST | `/api/scripts/export/` | 批量导出 |
| POST | `/api/scripts/import/` | 导入 |
| POST | `/api/scripts/recording/start/` | 启动录制 |
| GET | `/api/scripts/recording/<sid>/actions/` | 获取录制操作 |
| POST | `/api/scripts/recording/<sid>/stop/` | 停止录制 |
| POST | `/api/scripts/recording/<sid>/convert/` | 转换录制 |
| GET | `/api/scripts/action-sets/` | 动作集合列表 |
| POST | `/api/scripts/action-sets/` | 创建动作集合 |
| GET | `/api/scripts/action-sets/<id>/` | 动作集合详情 |
| PUT | `/api/scripts/action-sets/<id>/` | 更新动作集合 |
| DELETE | `/api/scripts/action-sets/<id>/` | 删除动作集合 |
| GET | `/api/scripts/action-sets/<id>/export/` | 导出动作集合 |
| POST | `/api/scripts/action-sets/<id>/expand/` | 展开动作集合 |
| POST | `/api/scripts/action-sets/export/` | 批量导出 |
| POST | `/api/scripts/action-sets/import/` | 导入动作集合 |
| GET | `/api/scripts/action-sets/categories/` | 分类列表 |
| GET | `/api/scripts/action-sets/<aid>/steps/` | 步骤列表 |
| POST | `/api/scripts/action-sets/<aid>/steps/` | 创建步骤 |
| POST | `/api/scripts/action-sets/<aid>/steps/reorder/` | 步骤重排序 |
| GET | `/api/scripts/action-sets/steps/<id>/` | 步骤详情 |
| PUT | `/api/scripts/action-sets/steps/<id>/` | 更新步骤 |
| DELETE | `/api/scripts/action-sets/steps/<id>/` | 删除步骤 |
| GET | `/api/scripts/action-sets/<aid>/parameters/` | 参数列表 |
| POST | `/api/scripts/action-sets/<aid>/parameters/` | 创建参数 |
| GET | `/api/scripts/action-sets/parameters/<id>/` | 参数详情 |
| PUT | `/api/scripts/action-sets/parameters/<id>/` | 更新参数 |
| DELETE | `/api/scripts/action-sets/parameters/<id>/` | 删除参数 |
| GET | `/api/scripts/marketplace/items/` | 市场文件列表 |
| GET | `/api/scripts/marketplace/search/` | 市场搜索 |
| POST | `/api/scripts/marketplace/folder/` | 创建文件夹 |
| GET | `/api/scripts/marketplace/download/` | 下载文件 |
| GET | `/api/scripts/marketplace/preview/` | 预览文件 |
| POST | `/api/scripts/marketplace/upload/` | 上传文件 |

---

## 九、依赖清单 (`requirements.txt`)

| 包名 | 版本要求 |
|------|---------|
| Django | >=4.2,<5.0 |
| playwright | >=1.40.0 |
| djangorestframework | >=3.14.0 |
| django-cors-headers | >=4.3.0 |
| python-dotenv | >=1.0.0 |
| Pillow | >=10.0.0 |
| celery | >=5.3.0 |
| redis | >=5.0.0 |
| django-celery-results | >=2.5.0 |
| jsonschema | >=4.20.0 |
| openpyxl | >=3.1.0 |
| requests | >=2.31.0 |
