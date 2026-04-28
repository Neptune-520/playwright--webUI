# 自动化测试平台 API 接口文档

> 本文档完整记录自动化测试平台与自动化管理平台的所有 API 接口、参数、变量及其定义。

---

## 目录

### 一、自动化测试平台（Django + DRF）
1. [全局配置](#全局配置)
2. [核心接口 (core)](#核心接口)
3. [脚本编辑器 (script_editor)](#脚本编辑器)
4. [动作集合 (action_sets)](#动作集合)
5. [集合市场 (marketplace)](#集合市场)
6. [测试管理 (test_manager)](#测试管理)
7. [数据库模型字段定义](#数据库模型)

### 二、自动化管理平台（FastAPI）
1. [全局配置](#管理平台全局配置)
2. [文件管理接口](#文件管理接口)
3. [脚本结果管理接口](#脚本结果管理接口)
4. [数据库模型字段定义](#管理平台数据库模型)

---

## 一、自动化测试平台

### 全局配置

#### 基础信息
| 配置项 | 值 |
|--------|-----|
| 技术栈 | Django + Django REST Framework |
| 默认地址 | `http://localhost:8000` |
| URL 前缀 | `/api/` |
| 认证方式 | Session / Token (部分接口 AllowAny) |

#### 环境变量（.env）
| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | String | `sqlite:///db.sqlite3` | 数据库连接字符串 |
| `CELERY_BROKER_URL` | String | `redis://localhost:6379/0` | Celery 消息代理地址 |
| `CELERY_RESULT_BACKEND` | String | `redis://localhost:6379/1` | Celery 结果存储地址 |
| `SECRET_KEY` | String | 必填 | Django 密钥 |
| `DEBUG` | Boolean | `True` | 调试模式开关 |

---

### 核心接口

#### 1. 健康检查
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/core/health/` |
| **权限** | AllowAny |
| **说明** | 检查平台是否正常运行 |

**响应示例：**
```json
{
  "status": "ok",
  "message": "Automation Test Platform is running"
}
```

#### 2. 仪表盘统计
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/core/dashboard/` |
| **权限** | 需认证 |
| **说明** | 获取平台概览统计数据 |

**响应字段定义：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `statistics.total_tasks` | Integer | 总任务数 |
| `statistics.running_tasks` | Integer | 执行中任务数 |
| `statistics.completed_tasks` | Integer | 已完成任务数 |
| `statistics.failed_tasks` | Integer | 失败任务数 |
| `statistics.total_scripts` | Integer | 总脚本数 |
| `statistics.published_scripts` | Integer | 已发布脚本数 |
| `statistics.total_elements` | Integer | 活跃元素定位器数 |
| `statistics.pass_rate` | Float | 总体通过率（百分比） |
| `recent_tasks` | Array | 最近5条任务记录，包含 id、name、status、created_at |

#### 3. 分组管理
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/core/groups/` |
| **URL** | `GET/PUT/DELETE /api/core/groups/<pk>/` |
| **权限** | AllowAny |
| **说明** | 管理脚本/动作集合/任务的分组 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `type` | String | 否 | 分组类型：`script`、`action_set`、`task` |

**POST/PUT 请求体字段：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 分组名称 |
| `code` | String | 是 | 分组代码（同类型下唯一） |
| `type` | String | 是 | 分组类型：`script`、`action_set`、`task` |
| `description` | String | 否 | 分组描述 |
| `parent` | Integer | 否 | 父分组ID（支持嵌套） |
| `order` | Integer | 否 | 排序序号，默认0 |

**响应字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 分组ID |
| `name` | String | 分组名称 |
| `code` | String | 分组代码 |
| `type` | String | 分组类型 |
| `type_display` | String | 分组类型显示名称 |
| `description` | String | 描述 |
| `parent` | Integer/null | 父分组ID |
| `order` | Integer | 排序 |
| `full_path` | String | 完整路径（如 "父分组 / 子分组"） |
| `children_count` | Integer | 子分组数量 |
| `created_by` | Integer | 创建人ID |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

#### 4. 清理截图
| 属性 | 值 |
|------|-----|
| **URL** | `DELETE /api/core/scripts/clear-screenshots/` |
| **权限** | AllowAny |
| **说明** | 清理所有测试截图文件 |

**响应字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `message` | String | 清理结果消息 |
| `deleted_count` | Integer | 已删除文件数量 |

#### 5. 清理任务结果
| 属性 | 值 |
|------|-----|
| **URL** | `DELETE /api/core/scripts/clear-task-results/` |
| **权限** | AllowAny |
| **说明** | 清理所有任务结果JSON文件 |

**响应字段：** 同上

#### 6. 错误配置管理
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/core/error-config/` |
| **URL** | `PUT /api/core/error-config/<config_id>/` |
| **URL** | `DELETE /api/core/error-config/<config_id>/delete/` |
| **权限** | AllowAny |
| **说明** | 管理自定义错误消息匹配规则 |

**POST 请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 否 | 规则名称 |
| `pattern` | String | 否 | 正则匹配模式 |
| `message_template` | String | 否 | 错误消息模板 |
| `action_type` | String | 否 | 关联的操作类型 |

**GET 响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `builtin_rules` | Array | 内置错误匹配规则列表 |
| `custom_rules` | Array | 用户自定义错误匹配规则列表 |

---

### 脚本编辑器

#### 1. 脚本列表
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/` |
| **URL** | `POST /api/scripts/` |
| **权限** | 需认证 |
| **说明** | 获取/创建测试脚本 |

**GET 响应字段（列表）：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 脚本ID |
| `name` | String | 脚本名称 |
| `code` | String | 脚本代码（唯一标识） |
| `description` | String | 脚本描述 |
| `status` | String | 状态：`draft`、`published`、`archived` |
| `status_display` | String | 状态显示名称 |
| `version` | Integer | 版本号 |
| `target_url` | String | 目标网站URL |
| `steps_count` | Integer | 步骤数量 |
| `group` | Integer/null | 分组ID |
| `group_name` | String | 分组名称 |
| `created_by` | Integer | 创建人ID |
| `created_by_name` | String | 创建人用户名 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

**POST 请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 脚本名称 |
| `code` | String | 是 | 脚本代码（唯一） |
| `description` | String | 否 | 描述 |
| `status` | String | 否 | 状态，默认 `draft` |
| `target_url` | String | 否 | 目标URL |
| `group` | Integer | 否 | 分组ID |
| `steps` | Array | 否 | 步骤列表（嵌套对象） |

**步骤嵌套对象字段：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 步骤名称 |
| `order` | Integer | 是 | 执行顺序（从0开始） |
| `action_type` | String | 是 | 操作类型（见操作类型定义表） |
| `element` | Integer/null | 否 | 元素定位器ID |
| `action_value` | String | 否 | 操作值 |
| `action_config` | Object | 否 | 操作配置JSON |
| `description` | String | 否 | 步骤描述 |
| `is_enabled` | Boolean | 否 | 是否启用，默认true |
| `continue_on_failure` | Boolean | 否 | 失败时是否继续，默认false |
| `retry_count` | Integer | 否 | 重试次数，默认0 |
| `retry_interval` | Integer | 否 | 重试间隔（毫秒），默认1000 |
| `action_set_ref` | Integer/null | 否 | 引用的动作集合ID |
| `action_set_params` | Object | 否 | 动作集合参数JSON |

#### 2. 脚本详情
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/<pk>/` |
| **URL** | `PUT /api/scripts/<pk>/` |
| **URL** | `DELETE /api/scripts/<pk>/` |
| **权限** | 需认证 |
| **说明** | 获取/更新/删除单个脚本 |

**GET 响应字段：** 包含脚本详情及 `steps` 数组（完整步骤列表）

#### 3. 复制脚本
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/<script_id>/duplicate/` |
| **权限** | AllowAny |
| **说明** | 复制一个脚本及其所有步骤 |

**响应：** 返回新脚本的 id、name、code

#### 4. 脚本版本
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/<script_id>/versions/` |
| **URL** | `GET /api/scripts/<script_id>/versions/<version_id>/` |
| **权限** | 需认证 |
| **说明** | 获取脚本历史版本 |

**版本字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 版本记录ID |
| `script` | Integer | 脚本ID |
| `version_number` | Integer | 版本号 |
| `script_data` | Object | 脚本数据快照 |
| `change_note` | String | 变更说明 |
| `created_by` | Integer | 创建人ID |
| `created_by_name` | String | 创建人用户名 |
| `created_at` | DateTime | 创建时间 |

#### 5. 元素定位器
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/scripts/elements/` |
| **URL** | `GET/PUT/DELETE /api/scripts/elements/<pk>/` |
| **权限** | 需认证 |
| **说明** | 管理页面元素定位器 |

**元素定位器字段：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | Integer | - | 元素ID |
| `name` | String | 是 | 元素名称（如 "Login Button"） |
| `code` | String | 是 | 元素代码（唯一） |
| `locator_type` | String | 是 | 定位类型：`css`、`xpath`、`id`、`name`、`class_name`、`tag_name`、`text`、`role`、`test_id`、`placeholder`、`label` |
| `locator_value` | String | 是 | 定位值 |
| `page_url` | String | 否 | 所在页面URL |
| `description` | String | 否 | 描述 |
| `wait_timeout` | Integer | 否 | 等待超时（毫秒），默认10000 |
| `wait_state` | String | 否 | 等待状态：`visible`、`hidden`、`attached`、`detached` |
| `is_active` | Boolean | 否 | 是否启用 |

#### 6. 测试步骤
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/scripts/steps/` |
| **URL** | `GET/PUT/DELETE /api/scripts/steps/<pk>/` |
| **权限** | 需认证 |
| **说明** | 管理脚本步骤 |

**步骤字段：** 同脚本创建中的 steps 字段

**额外只读字段（GET响应）：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `element_name` | String | 元素名称 |
| `element_locator_type` | String | 元素定位类型 |
| `element_locator_value` | String | 元素定位值 |
| `action_set_name` | String | 动作集合名称 |

#### 7. 可视化编辑器
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/scripts/visual-editor/` |
| **权限** | AllowAny |
| **说明** | 可视化创建脚本 |

**GET 响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `action_types` | Array | 所有可用操作类型列表 [{value, label}] |
| `locator_types` | Array | 所有可用定位类型列表 [{value, label}] |

**POST 请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 脚本名称 |
| `code` | String | 是 | 脚本代码 |
| `description` | String | 否 | 描述 |
| `target_url` | String | 是 | 目标URL |
| `steps` | Array | 是 | 步骤列表 |
| `parameters` | Array | 否 | 参数列表 |

#### 8. 脚本验证
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/validate-script/` |
| **权限** | AllowAny |
| **说明** | 验证脚本数据是否合法 |

**请求体：** 脚本JSON数据
**响应：** 验证结果对象

#### 9. 录制功能
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/recording/start/` |
| **URL** | `GET /api/scripts/recording/<session_id>/actions/` |
| **URL** | `POST /api/scripts/recording/<session_id>/stop/` |
| **URL** | `POST /api/scripts/recording/<session_id>/convert/` |
| **权限** | AllowAny |
| **说明** | 浏览器录制操作并转换为脚本/动作集合 |

**POST /recording/start/ 请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `target_url` | String | 是 | 目标网站URL |
| `viewport_width` | Integer | 否 | 视口宽度，默认1920 |
| `viewport_height` | Integer | 否 | 视口高度，默认1080 |

**响应（start）：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `session_id` | String | 录制会话ID |
| `status` | String | 状态：`starting` |
| `target_url` | String | 目标URL |

**POST /recording/convert/ 请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `mode` | String | 否 | 转换模式：`script` 或 `action_set` |
| `name` | String | 否 | 生成的名称 |
| `code` | String | 否 | 生成的代码 |
| `category` | String | 否 | 动作集合分类 |
| `group_code` | String | 否 | 分组代码 |
| `target_url` | String | 否 | 目标URL（脚本模式） |

#### 10. 全局配置
| 属性 | 值 |
|------|-----|
| **URL** | `GET/PUT /api/scripts/global-config/` |
| **权限** | 需认证 |
| **说明** | 获取/更新全局配置 |

**全局配置字段（完整定义）：**
| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `id` | Integer | 1 | 配置记录ID（全局唯一） |
| `headless_mode` | Boolean | false | 无头模式（不显示浏览器窗口） |
| `default_timeout` | Integer | 30000 | 默认超时时间（毫秒） |
| `step_screenshot` | Boolean | false | 每步截图开关 |
| `slow_mo` | Integer | 0 | 操作间延迟（毫秒） |
| `viewport_width` | Integer | 1920 | 浏览器视口宽度 |
| `viewport_height` | Integer | 1080 | 浏览器视口高度 |
| `scroll_distance` | Integer | 500 | 默认滚动距离（像素） |
| `scroll_direction` | String | `down` | 默认滚动方向：`down`、`up`、`left`、`right` |
| `marketplace_api_url` | String | `http://127.0.0.1:8000` | 集合市场API地址 |
| `management_platform_url` | String | `http://localhost:8001/api/script-results/upload` | 管理平台上传地址 |
| `username` | String | `''` | 上传结果的用户标识 |
| `email_smtp_host` | String | `''` | SMTP服务器地址 |
| `email_smtp_port` | Integer | 465 | SMTP端口 |
| `email_username` | String | `''` | 发件人邮箱 |
| `email_password` | String | `''` | 邮箱密码/授权码 |
| `email_use_ssl` | Boolean | true | 使用SSL连接 |
| `email_recipients` | String | `''` | 收件人列表（逗号分隔） |
| `email_enable` | Boolean | false | 启用邮件通知 |
| `report_base_url` | String | `''` | 报告访问地址前缀 |
| `updated_at` | DateTime | - | 更新时间 |
| `updated_by` | Integer/null | - | 更新人ID |
| `updated_by_name` | String | - | 更新人用户名 |

#### 11. 脚本导出
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/export/` |
| **URL** | `GET /api/scripts/<pk>/export/` |
| **权限** | AllowAny |
| **说明** | 导出脚本为JSON或Excel |

**POST 请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `script_ids` | Array<Integer> | 是 | 要导出的脚本ID列表 |
| `format` | String | 否 | 导出格式：`json` 或 `excel` |

**GET 查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `export_format` | String | 否 | 导出格式：`json` 或 `excel` |

#### 12. 脚本导入
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/import/` |
| **权限** | AllowAny |
| **说明** | 从JSON或Excel导入脚本 |

**请求参数（multipart/form-data）：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file` | File | 是 | 上传的文件 |
| `format` | String | 否 | 文件格式：`json`、`excel`、`auto` |
| `conflict_strategy` | String | 否 | 冲突处理：`skip`（跳过）、`overwrite`（覆盖）、`rename`（重命名） |

**响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `success` | Integer | 成功导入数量 |
| `failed` | Integer | 失败数量 |
| `skipped` | Integer | 跳过数量 |
| `errors` | Array | 错误详情列表 |
| `action_sets_created` | Integer | 新建动作集合数 |
| `scripts_created` | Integer | 新建脚本数 |
| `elements_created` | Integer | 新建元素数 |
| `elements_reused` | Integer | 复用元素数 |

---

### 动作集合

#### 1. 动作集合列表
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/scripts/action-sets/` |
| **权限** | AllowAny |
| **说明** | 获取/创建动作集合 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `category` | String | 否 | 按分类过滤 |

**动作集合字段：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | Integer | - | 动作集合ID |
| `name` | String | 是 | 名称 |
| `code` | String | 是 | 代码（唯一） |
| `description` | String | 否 | 描述 |
| `category` | String | 否 | 分类：`input`、`navigation`、`form`、`validation`、`general` |
| `group` | Integer/null | 否 | 分组ID |
| `is_builtin` | Boolean | - | 是否内置 |
| `is_active` | Boolean | 否 | 是否启用 |
| `created_by` | Integer/null | - | 创建人ID |
| `created_at` | DateTime | - | 创建时间 |
| `updated_at` | DateTime | - | 更新时间 |
| `steps_count` | Integer | - | 步骤数量（只读） |
| `parameters_count` | Integer | - | 参数数量（只读） |
| `category_display` | String | - | 分类显示名（只读） |
| `group_name` | String | - | 分组名称（只读） |

#### 2. 动作集合详情
| 属性 | 值 |
|------|-----|
| **URL** | `GET/PUT/DELETE /api/scripts/action-sets/<pk>/` |
| **权限** | AllowAny（GET）/ 需认证（PUT/DELETE） |
| **说明** | 获取/更新/删除单个动作集合 |

**GET 响应包含完整步骤列表 `steps`：**

**动作集合步骤字段：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | Integer | - | 步骤ID |
| `name` | String | 是 | 步骤名称 |
| `order` | Integer | 是 | 执行顺序 |
| `action_type` | String | 是 | 操作类型：`click`、`fill`、`select`、`random_select`、`random_number`、`check`、`uncheck`、`wait`、`wait_for_selector`、`scroll`、`hover`、`focus`、`press`、`assert_text`、`assert_visible` |
| `locator_type` | String | 否 | 定位类型：`css`、`xpath`、`id`、`name`、`class_name`、`text`、`placeholder`、`label` |
| `locator_value` | String | 否 | 定位值 |
| `locator_description` | String | 否 | 定位描述 |
| `action_value` | String | 否 | 操作值 |
| `action_value_type` | String | 否 | 值类型：`static`、`parameter`、`expression` |
| `parameter_name` | String | 否 | 参数名称（当使用参数化值时） |
| `action_config` | Object | 否 | 配置JSON（包含locators等） |
| `wait_timeout` | Integer | 否 | 等待超时（毫秒） |
| `continue_on_failure` | Boolean | 否 | 失败时继续 |
| `retry_count` | Integer | 否 | 重试次数 |
| `retry_interval` | Integer | 否 | 重试间隔（毫秒） |
| `random_options` | Array | 否 | 随机选项列表（用于random_select） |
| `select_mode` | String | 否 | 选择模式：`dropdown`（下拉框）、`click`（点击卡片） |
| `random_min` | Integer | 否 | 随机数最小值 |
| `random_max` | Integer | 否 | 随机数最大值 |
| `force_click` | Boolean | 否 | 强制点击（忽略元素拦截） |
| `description` | String | 否 | 描述 |
| `is_enabled` | Boolean | 否 | 是否启用 |

**只读显示字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `action_type_display` | String | 操作类型显示名 |
| `locator_type_display` | String | 定位类型显示名 |
| `action_value_type_display` | String | 值类型显示名 |
| `select_mode_display` | String | 选择模式显示名 |

#### 3. 动作集合展开
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/action-sets/<pk>/expand/` |
| **权限** | AllowAny |
| **说明** | 将动作集合展开为可执行步骤（替换参数） |

**请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `parameters` | Object | 否 | 参数映射 {"param_name": "value"} |

**响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `action_set` | Object | 动作集合信息 {id, name, code} |
| `steps` | Array | 展开后的步骤列表 |
| `parameters_used` | Object | 使用的参数 |

#### 4. 动作集合导入/导出
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/action-sets/import/` |
| **URL** | `POST /api/scripts/action-sets/export/` |
| **URL** | `GET /api/scripts/action-sets/<pk>/export/` |
| **权限** | AllowAny |
| **说明** | 批量导入/导出动作集合（JSON格式） |

**导出请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `ids` | Array<Integer> | 是 | 要导出的动作集合ID列表 |

**导入响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `message` | String | 结果消息 |
| `success_count` | Integer | 成功导入数 |
| `skipped_count` | Integer | 跳过数（code已存在） |
| `errors` | Array | 错误详情 |

#### 5. 分类列表
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/action-sets/categories/` |
| **权限** | AllowAny |
| **说明** | 获取所有已使用的分类列表 |

#### 6. 步骤管理
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/scripts/action-sets/<action_set_id>/steps/` |
| **URL** | `GET/PUT/DELETE /api/scripts/action-sets/steps/<pk>/` |
| **URL** | `POST /api/scripts/action-sets/<action_set_id>/steps/reorder/` |
| **权限** | AllowAny |
| **说明** | 管理动作集合的步骤 |

**reorder 请求体：**
```json
{
  "steps": [
    {"id": 1, "order": 0},
    {"id": 2, "order": 1}
  ]
}
```

#### 7. 参数管理
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/scripts/action-sets/<action_set_id>/parameters/` |
| **URL** | `GET/PUT/DELETE /api/scripts/action-sets/parameters/<pk>/` |
| **权限** | AllowAny |
| **说明** | 管理动作集合的参数定义 |

**参数字段：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 参数名称 |
| `code` | String | 是 | 参数代码（同动作集合下唯一） |
| `description` | String | 否 | 描述 |
| `default_value` | String | 否 | 默认值 |
| `is_required` | Boolean | 否 | 是否必填 |
| `order` | Integer | 否 | 排序 |

---

### 集合市场

#### 1. 市场列表
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/marketplace/items/` |
| **权限** | AllowAny |
| **说明** | 获取集合市场中的文件/文件夹列表 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | String | 否 | 当前目录路径 |

#### 2. 市场搜索
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/marketplace/search/` |
| **权限** | AllowAny |
| **说明** | 搜索集合市场文件 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `keyword` | String | 是 | 搜索关键词 |

#### 3. 创建文件夹
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/marketplace/folder/` |
| **权限** | AllowAny |
| **说明** | 在市场目录中创建文件夹 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 文件夹名称 |
| `path` | String | 否 | 父目录路径 |

#### 4. 下载文件
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/marketplace/download/` |
| **权限** | AllowAny |
| **说明** | 下载市场中的JSON文件 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 文件名 |
| `path` | String | 否 | 文件路径 |

#### 5. 预览文件
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/scripts/marketplace/preview/` |
| **权限** | AllowAny |
| **说明** | 预览JSON文件内容 |

#### 6. 上传文件
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/scripts/marketplace/upload/` |
| **权限** | AllowAny |
| **说明** | 上传JSON文件到市场 |

---

### 测试管理

#### 1. 任务列表
| 属性 | 值 |
|------|-----|
| **URL** | `GET/POST /api/tests/tasks/` |
| **权限** | GET需认证 / POST需认证 |
| **说明** | 获取/创建测试任务 |

**GET 响应字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 任务ID |
| `name` | String | 任务名称 |
| `script` | Integer | 主脚本ID |
| `script_name` | String | 主脚本名称 |
| `status` | String | 状态：`pending`、`running`、`completed`、`failed`、`cancelled` |
| `status_display` | String | 状态显示名 |
| `group` | Integer/null | 分组ID |
| `group_name` | String | 分组名称 |
| `script_count` | Integer | 关联脚本数量 |
| `task_scripts` | Array | 任务脚本列表 [{id, script, script_name, script_code, order, parameters}] |
| `scheduled_time` | DateTime/null | 计划执行时间 |
| `started_at` | DateTime/null | 实际开始时间 |
| `finished_at` | DateTime/null | 实际结束时间 |
| `created_by` | Integer | 创建人ID |
| `created_by_name` | String | 创建人用户名 |
| `results_count` | Integer | 测试结果数量 |
| `report` | Object/null | 测试报告对象 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

**POST 请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 任务名称 |
| `scripts` | Array<Integer> | 是 | 脚本ID列表（支持多选） |
| `parameters` | Object | 否 | 测试参数映射 |
| `group` | Integer | 否 | 分组ID |
| `scheduled_time` | DateTime | 否 | 计划执行时间 |
| `upload_to_management` | Boolean | 否 | 是否上传到管理平台 |

**测试报告字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 报告ID |
| `task` | Integer | 关联任务ID |
| `total_steps` | Integer | 总步骤数 |
| `passed_steps` | Integer | 通过步骤数 |
| `failed_steps` | Integer | 失败步骤数 |
| `skipped_steps` | Integer | 跳过步骤数 |
| `total_duration` | Float | 总执行时长（秒） |
| `summary` | Object | 汇总数据JSON |
| `pass_rate` | Float | 通过率（百分比） |
| `created_at` | DateTime | 创建时间 |

#### 2. 任务详情
| 属性 | 值 |
|------|-----|
| **URL** | `GET/PUT/DELETE /api/tests/tasks/<pk>/` |
| **权限** | 需认证 |
| **说明** | 获取/更新/删除单个任务 |

**GET 额外字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `parameters` | Object | 测试参数 |
| `celery_task_id` | String | Celery任务ID |
| `upload_to_management` | Boolean | 是否上传到管理平台 |
| `upload_status` | String | 上传状态：`none`、`uploading`、`uploaded`、`failed`、`pending` |
| `upload_status_display` | String | 上传状态显示名 |
| `scripts_passed` | Integer | 已通过的脚本数 |
| `scripts_failed` | Integer | 已失败的脚本数 |
| `results` | Array | 完整测试结果列表 |
| `report` | Object/null | 测试报告 |

#### 3. 执行任务
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/tests/tasks/<task_id>/execute/` |
| **权限** | AllowAny |
| **说明** | 执行测试任务 |

**请求体：**
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `parameters` | Object | 否 | 覆盖任务的测试参数 |
| `upload_to_management` | Boolean | 否 | 是否上传到管理平台 |
| `send_email` | Boolean | 否 | 是否发送邮件通知 |

**响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `task_id` | Integer | 任务ID |
| `celery_task_id` | String | Celery异步任务ID |
| `status` | String | 状态：`started` |
| `message` | String | 消息 |
| `script_count` | Integer | 脚本数量（仅多脚本任务） |

#### 4. 停止任务
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/tests/tasks/<task_id>/stop/` |
| **权限** | 需认证 |
| **说明** | 停止正在执行的任务 |

#### 5. 手动上传结果
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/tests/tasks/<task_id>/upload/` |
| **权限** | AllowAny |
| **说明** | 手动将已完成任务的结果上传到管理平台 |

#### 6. 测试结果列表
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/tests/results/` |
| **权限** | 需认证 |
| **说明** | 获取测试结果列表 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `task_id` | Integer | 否 | 按任务ID过滤 |

**测试结果字段：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 结果ID |
| `task` | Integer | 关联任务ID |
| `step_name` | String | 步骤名称 |
| `step_order` | Integer | 步骤顺序 |
| `status` | String | 状态：`passed`、`failed`、`skipped`、`error` |
| `status_display` | String | 状态显示名 |
| `duration` | Float | 执行时长（秒） |
| `error_message` | String | 错误信息 |
| `error_stack` | String | 错误堆栈 |
| `original_error_message` | String | 原始错误堆栈（同error_stack） |
| `screenshot` | String/null | 截图URL |
| `action_values` | Object | 操作值JSON（如输入值、随机选择的值等） |
| `logs` | Array | 执行日志列表 |
| `created_at` | DateTime | 创建时间 |

#### 7. 测试结果详情
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/tests/results/<pk>/` |
| **权限** | 需认证 |
| **说明** | 获取单个测试结果详情 |

#### 8. 获取截图
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/tests/results/<result_id>/screenshots/` |
| **权限** | AllowAny |
| **说明** | 获取测试结果关联的截图 |

**响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `result_id` | Integer | 结果ID |
| `screenshots` | Array | 截图列表 [{id, step_name, url}] |

#### 9. 导出报告
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/tests/results/<task_id>/export/` |
| **权限** | AllowAny |
| **说明** | 导出任务测试报告 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `format` | String | 否 | 导出格式：`json`（默认） |

**响应：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `task_id` | Integer | 任务ID |
| `report_file` | String | 报告文件路径 |
| `format` | String | 导出格式 |

---

## 数据库模型

### Group（分组）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | CharField(100) | NOT NULL | - | 分组名称 |
| `code` | CharField(50) | NOT NULL | - | 分组代码 |
| `type` | CharField(20) | NOT NULL | - | 类型：script、action_set、task |
| `description` | TextField | - | `''` | 描述 |
| `parent` | ForeignKey(self) | NULL | NULL | 父分组 |
| `order` | IntegerField | NOT NULL | 0 | 排序 |
| `created_by` | ForeignKey(User) | NULL | NULL | 创建人 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |

### ElementLocator（元素定位器）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | CharField(100) | NOT NULL | - | 元素名称 |
| `code` | CharField(50) | UNIQUE | - | 元素代码 |
| `locator_type` | CharField(20) | NOT NULL | `css` | 定位类型 |
| `locator_value` | CharField(500) | NOT NULL | - | 定位值 |
| `page_url` | URLField(500) | - | `''` | 所在页面URL |
| `description` | TextField | - | `''` | 描述 |
| `wait_timeout` | IntegerField | NOT NULL | 10000 | 等待超时（毫秒） |
| `wait_state` | CharField(20) | NOT NULL | `visible` | 等待状态 |
| `is_active` | BooleanField | NOT NULL | true | 是否启用 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |

### TestScript（测试脚本）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | CharField(200) | NOT NULL | - | 脚本名称 |
| `code` | CharField(50) | UNIQUE | - | 脚本代码 |
| `description` | TextField | - | `''` | 描述 |
| `status` | CharField(20) | NOT NULL | `draft` | 状态：draft、published、archived |
| `version` | IntegerField | NOT NULL | 1 | 版本号 |
| `target_url` | URLField(500) | NOT NULL | - | 目标URL |
| `script_data` | JSONField | NOT NULL | `{}` | 脚本数据JSON |
| `group` | ForeignKey(Group) | NULL | NULL | 分组 |
| `created_by` | ForeignKey(User) | NULL | NULL | 创建人 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |

### TestStep（测试步骤）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `script` | ForeignKey(TestScript) | NOT NULL | - | 所属脚本 |
| `name` | CharField(200) | NOT NULL | - | 步骤名称 |
| `order` | IntegerField | NOT NULL | 0 | 执行顺序 |
| `action_type` | CharField(30) | NOT NULL | - | 操作类型 |
| `element` | ForeignKey(ElementLocator) | NULL | NULL | 目标元素 |
| `action_set_ref` | ForeignKey(ActionSet) | NULL | NULL | 动作集合引用 |
| `action_set_params` | JSONField | - | `{}` | 动作集合参数 |
| `action_value` | TextField | - | `''` | 操作值 |
| `action_config` | JSONField | NOT NULL | `{}` | 操作配置 |
| `description` | TextField | - | `''` | 描述 |
| `is_enabled` | BooleanField | NOT NULL | true | 是否启用 |
| `continue_on_failure` | BooleanField | NOT NULL | false | 失败时继续 |
| `retry_count` | IntegerField | NOT NULL | 0 | 重试次数 |
| `retry_interval` | IntegerField | NOT NULL | 1000 | 重试间隔（毫秒） |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |

### ActionSet（动作集合）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | CharField(200) | NOT NULL | - | 名称 |
| `code` | CharField(50) | UNIQUE | - | 代码 |
| `description` | TextField | - | `''` | 描述 |
| `category` | CharField(100) | NOT NULL | `general` | 分类 |
| `group` | ForeignKey(Group) | NULL | NULL | 分组 |
| `is_builtin` | BooleanField | NOT NULL | false | 是否内置 |
| `is_active` | BooleanField | NOT NULL | true | 是否启用 |
| `created_by` | ForeignKey(User) | NULL | NULL | 创建人 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |

### ActionSetStep（动作集合步骤）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `action_set` | ForeignKey(ActionSet) | NOT NULL | - | 所属动作集合 |
| `name` | CharField(200) | NOT NULL | - | 步骤名称 |
| `order` | IntegerField | NOT NULL | 0 | 执行顺序 |
| `action_type` | CharField(30) | NOT NULL | - | 操作类型 |
| `locator_type` | CharField(20) | - | `css` | 定位类型 |
| `locator_value` | CharField(500) | - | `''` | 定位值 |
| `locator_description` | CharField(200) | - | `''` | 定位描述 |
| `action_value` | TextField | - | `''` | 操作值 |
| `action_value_type` | CharField(20) | NOT NULL | `static` | 值类型 |
| `parameter_name` | CharField(100) | - | `''` | 参数名称 |
| `action_config` | JSONField | - | `{}` | 操作配置 |
| `wait_timeout` | IntegerField | NOT NULL | 10000 | 等待超时（毫秒） |
| `continue_on_failure` | BooleanField | NOT NULL | false | 失败时继续 |
| `retry_count` | IntegerField | NOT NULL | 0 | 重试次数 |
| `retry_interval` | IntegerField | NOT NULL | 1000 | 重试间隔（毫秒） |
| `random_options` | JSONField | NULL | `[]` | 随机选项列表 |
| `select_mode` | CharField(20) | NOT NULL | `dropdown` | 选择模式 |
| `random_min` | IntegerField | NULL | 0 | 随机数最小值 |
| `random_max` | IntegerField | NULL | 100 | 随机数最大值 |
| `force_click` | BooleanField | NOT NULL | false | 强制点击 |
| `description` | TextField | - | `''` | 描述 |
| `is_enabled` | BooleanField | NOT NULL | true | 是否启用 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |

### ActionSetParameter（动作集合参数）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `action_set` | ForeignKey(ActionSet) | NOT NULL | - | 所属动作集合 |
| `name` | CharField(100) | NOT NULL | - | 参数名称 |
| `code` | CharField(50) | NOT NULL | - | 参数代码 |
| `description` | TextField | - | `''` | 描述 |
| `default_value` | CharField(255) | - | `''` | 默认值 |
| `is_required` | BooleanField | NOT NULL | true | 是否必填 |
| `order` | IntegerField | NOT NULL | 0 | 排序 |

### TestTask（测试任务）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | CharField(200) | NOT NULL | - | 任务名称 |
| `script` | ForeignKey(TestScript) | NOT NULL | - | 主测试脚本 |
| `status` | CharField(20) | NOT NULL | `pending` | 状态 |
| `parameters` | JSONField | NOT NULL | `{}` | 测试参数 |
| `group` | ForeignKey(Group) | NULL | NULL | 分组 |
| `scheduled_time` | DateTimeField | NULL | NULL | 计划执行时间 |
| `started_at` | DateTimeField | NULL | NULL | 开始时间 |
| `finished_at` | DateTimeField | NULL | NULL | 结束时间 |
| `celery_task_id` | CharField(100) | NOT NULL | `''` | Celery任务ID |
| `task_group` | ForeignKey(TaskGroup) | NULL | NULL | 任务组（已废弃） |
| `is_aggregate_subtask` | BooleanField | NOT NULL | false | 是否为聚合子任务 |
| `upload_to_management` | BooleanField | NOT NULL | false | 是否上传管理平台 |
| `management_platform_url` | CharField(500) | - | `''` | 管理平台地址（留空用全局配置） |
| `upload_status` | CharField(20) | NOT NULL | `none` | 上传状态 |
| `send_email` | BooleanField | NOT NULL | false | 是否发送邮件通知 |
| `created_by` | ForeignKey(User) | NULL | NULL | 创建人 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |

### TaskScript（任务脚本关联）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `task` | ForeignKey(TestTask) | NOT NULL | - | 所属任务 |
| `script` | ForeignKey(TestScript) | NOT NULL | - | 关联脚本 |
| `order` | IntegerField | NOT NULL | 0 | 执行顺序 |
| `parameters` | JSONField | NOT NULL | `{}` | 参数 |

### TestResult（测试结果）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `task` | ForeignKey(TestTask) | NOT NULL | - | 所属任务 |
| `step_name` | CharField(200) | NOT NULL | - | 步骤名称 |
| `step_order` | IntegerField | NOT NULL | - | 步骤顺序 |
| `status` | CharField(20) | NOT NULL | - | 状态：passed、failed、skipped、error |
| `duration` | FloatField | NOT NULL | 0 | 执行时长（秒） |
| `error_message` | TextField | - | `''` | 错误信息 |
| `error_stack` | TextField | - | `''` | 错误堆栈 |
| `screenshot` | ImageField | NULL | NULL | 截图文件 |
| `action_values` | JSONField | - | `{}` | 操作值 |
| `logs` | JSONField | NOT NULL | `[]` | 执行日志 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |

### TestReport（测试报告）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `task` | OneToOneField(TestTask) | NOT NULL | - | 关联任务 |
| `total_steps` | IntegerField | NOT NULL | 0 | 总步骤数 |
| `passed_steps` | IntegerField | NOT NULL | 0 | 通过步骤数 |
| `failed_steps` | IntegerField | NOT NULL | 0 | 失败步骤数 |
| `skipped_steps` | IntegerField | NOT NULL | 0 | 跳过步骤数 |
| `total_duration` | FloatField | NOT NULL | 0 | 总时长（秒） |
| `summary` | JSONField | NOT NULL | `{}` | 汇总数据 |
| `created_at` | DateTimeField | auto_now_add | - | 创建时间 |

### GlobalConfig（全局配置）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `headless_mode` | BooleanField | NOT NULL | false | 无头模式 |
| `default_timeout` | IntegerField | NOT NULL | 30000 | 默认超时（毫秒） |
| `step_screenshot` | BooleanField | NOT NULL | false | 每步截图 |
| `slow_mo` | IntegerField | NOT NULL | 0 | 操作延迟（毫秒） |
| `viewport_width` | IntegerField | NOT NULL | 1920 | 视口宽度 |
| `viewport_height` | IntegerField | NOT NULL | 1080 | 视口高度 |
| `scroll_distance` | IntegerField | NOT NULL | 500 | 滚动距离（像素） |
| `scroll_direction` | CharField(10) | NOT NULL | `down` | 滚动方向 |
| `marketplace_api_url` | CharField(500) | NOT NULL | 见上 | 市场API地址 |
| `management_platform_url` | CharField(500) | NOT NULL | 见上 | 管理平台地址 |
| `username` | CharField(100) | - | `''` | 用户名标识 |
| `email_smtp_host` | CharField(200) | - | `''` | SMTP服务器 |
| `email_smtp_port` | IntegerField | NOT NULL | 465 | SMTP端口 |
| `email_username` | CharField(200) | - | `''` | 发件人邮箱 |
| `email_password` | CharField(200) | - | `''` | 邮箱密码 |
| `email_use_ssl` | BooleanField | NOT NULL | true | SSL连接 |
| `email_recipients` | CharField(1000) | - | `''` | 收件人列表 |
| `email_enable` | BooleanField | NOT NULL | false | 启用邮件 |
| `report_base_url` | CharField(500) | - | `''` | 报告访问地址 |
| `updated_at` | DateTimeField | auto_now | - | 更新时间 |
| `updated_by` | ForeignKey(User) | NULL | NULL | 更新人 |

---

## 二、自动化管理平台

### 管理平台全局配置

| 配置项 | 值 |
|--------|-----|
| 技术栈 | FastAPI + SQLAlchemy + SQLite |
| 默认地址 | `http://localhost:8001` |
| 数据库 | `sqlite:///./automated_management.db` |

#### 环境变量
| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | String | `sqlite:///./automated_management.db` | 数据库连接字符串 |

#### Pydantic 模型定义

**StepResult（步骤结果 - 请求验证模型）**
| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `step_name` | String | 是 | - | 步骤名称 |
| `step_order` | Integer | 是 | - | 步骤顺序 |
| `action_type` | String | 是 | - | 操作类型 |
| `status` | String | 是 | - | 状态 |
| `duration` | Float | 是 | - | 执行时长（秒） |
| `error` | String/null | 否 | null | 错误信息 |
| `error_stack` | String/null | 否 | null | 错误堆栈 |
| `screenshot` | String/null | 否 | null | 截图URL |
| `action_values` | Object | 否 | `{}` | 操作值（可包含 sub_steps 嵌套数组） |

**ScriptResultUpload（脚本结果上传模型）**
| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `task_id` | Integer | 是 | - | 任务ID |
| `task_name` | String | 是 | - | 任务名称 |
| `script_name` | String | 是 | - | 脚本名称 |
| `started_at` | String | 是 | - | 开始时间（ISO格式） |
| `finished_at` | String | 是 | - | 结束时间（ISO格式） |
| `status` | String | 是 | - | 整体状态：completed、failed |
| `step_results` | Array<StepResult> | 是 | - | 步骤结果列表 |
| `parameters` | Object | 否 | `{}` | 执行参数 |
| `total_steps` | Integer | 是 | - | 总步骤数 |
| `passed_steps` | Integer | 是 | - | 通过步骤数 |
| `failed_steps` | Integer | 是 | - | 失败步骤数 |
| `skipped_steps` | Integer | 是 | - | 跳过步骤数 |
| `total_duration` | Float | 是 | - | 总时长（秒） |
| `pass_rate` | Float | 是 | - | 通过率（百分比） |
| `username` | String | 否 | `""` | 用户名标识 |
| `script_count` | Integer/null | 否 | null | 脚本数量（多脚本任务） |

---

### 文件管理接口

#### 1. 列出目录项目
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/items` |
| **权限** | 无需认证 |
| **说明** | 列出指定目录下的文件和文件夹 |

**查询参数：**
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `path` | String | 否 | `""` | 目录相对路径（空表示根目录） |

**响应（项目信息）：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | String | 项目（文件/文件夹）名称 |
| `size` | Integer | 文件大小（字节），文件夹为0 |
| `is_folder` | Boolean | 是否为文件夹 |
| `modified_time` | String | 修改时间（ISO格式） |

**辅助函数定义：**
| 函数名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `get_path_dir(relative_path)` | relative_path: String | Path | 将相对路径转换为绝对路径 |
| `safe_resolve(target)` | target: Path | Path | 安全检查路径是否在BASE_DIR内，防止路径穿越 |
| `get_item_info(path_obj)` | path_obj: Path | dict | 获取文件/文件夹的元信息 |

**全局变量：**
| 变量名 | 类型 | 值 | 说明 |
|--------|------|-----|------|
| `BASE_DIR` | Path | `./uploads` | 上传文件根目录 |
| `SCRIPT_RESULTS_DIR` | Path | `./uploads/script_results` | 脚本结果目录（从列表中隐藏） |

#### 2. 创建文件夹
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/folder` |
| **权限** | 无需认证 |
| **说明** | 在指定目录创建新文件夹 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | String | 是 | 文件夹名称 |
| `path` | String | 否 | 父目录路径 |

#### 3. 删除项目
| 属性 | 值 |
|------|-----|
| **URL** | `DELETE /api/items/{name}` |
| **权限** | 无需认证 |
| **说明** | 删除文件或文件夹 |

**路径参数：**
| 参数名 | 类型 | 说明 |
|--------|------|------|
| `name` | String | 项目名称（URL编码） |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | String | 否 | 父目录路径 |

#### 4. 重命名项目
| 属性 | 值 |
|------|-----|
| **URL** | `PUT /api/items/{name}/rename` |
| **权限** | 无需认证 |
| **说明** | 重命名文件或文件夹 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `new_name` | String | 是 | 新名称 |
| `path` | String | 否 | 父目录路径 |

#### 5. 上传文件
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/upload` |
| **权限** | 无需认证 |
| **说明** | 上传JSON文件（自动处理重名） |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | String | 否 | 目标目录路径 |

**请求体（multipart）：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | 是 | JSON文件（必须为.json扩展名） |

**逻辑说明：** 如果文件已存在，自动添加 `_1`、`_2` 等后缀避免覆盖。

#### 6. 下载文件
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/items/{name}/download` |
| **权限** | 无需认证 |
| **说明** | 下载JSON文件 |

#### 7. 预览文件
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/items/{name}/preview` |
| **权限** | 无需认证 |
| **说明** | 预览JSON文件内容 |

**响应：** JSON解析后的对象数据

#### 8. 搜索项目
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/search` |
| **权限** | 无需认证 |
| **说明** | 递归搜索文件名 |

**查询参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `keyword` | String | 否 | 搜索关键词（模糊匹配，不区分大小写） |

**响应（搜索结果）：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | String | 文件名 |
| `path` | String | 相对路径 |
| `size` | Integer | 文件大小 |
| `is_folder` | Boolean | 是否为文件夹（始终false） |
| `modified_time` | String | 修改时间 |

---

### 脚本结果管理接口

#### 1. 上传脚本结果
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/script-results/upload` |
| **权限** | 无需认证 |
| **说明** | 上传脚本执行结果（由测试平台自动调用） |

**请求体：** ScriptResultUpload JSON对象
**响应：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | String | "脚本执行结果已保存" |
| `id` | String | 结果记录UUID |

**处理逻辑：**
1. 生成UUID作为结果ID
2. 遍历 step_results，为每个步骤创建 StepResultModel 记录
3. 创建 ScriptResult 记录并关联所有步骤
4. 返回成功消息和结果ID

#### 2. 列出脚本结果（分页+过滤）
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/script-results` |
| **权限** | 无需认证 |
| **说明** | 分页获取脚本执行结果列表 |

**查询参数：**
| 参数名 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|--------|------|------|--------|------|------|
| `page` | Integer | 否 | 1 | >= 1 | 当前页码 |
| `page_size` | Integer | 否 | 20 | 1-100 | 每页条数 |
| `status` | String | 否 | null | - | 按状态过滤（completed/failed） |
| `keyword` | String | 否 | null | - | 按任务名/脚本名模糊搜索 |
| `username` | String | 否 | null | - | 按用户名过滤（逗号分隔多个） |
| `start_date` | String | 否 | null | - | 按开始日期过滤（格式：YYYY-MM-DD） |
| `end_date` | String | 否 | null | - | 按结束日期过滤（格式：YYYY-MM-DD） |

**响应：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | Array | 结果列表（每条包含完整 step_results） |
| `total` | Integer | 总记录数 |
| `page` | Integer | 当前页码 |
| `page_size` | Integer | 每页条数 |
| `total_pages` | Integer | 总页数 |

#### 3. 统计信息
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/script-results/stats` |
| **权限** | 无需认证 |
| **说明** | 获取整体统计数据 |

**响应：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | Integer | 总记录数 |
| `success_rate` | Float | 成功率（百分比） |
| `fail_rate` | Float | 失败率（百分比） |
| `avg_duration` | Float | 平均执行时长（秒） |

#### 4. 趋势数据
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/script-results/trend` |
| **权限** | 无需认证 |
| **说明** | 按日期分组的执行趋势 |

**响应（按日期数组）：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | String | 日期（YYYY-MM-DD） |
| `total` | Integer | 当日总执行数 |
| `success` | Integer | 当日成功数 |
| `fail` | Integer | 当日失败数 |
| `avg_duration` | Float | 当日平均时长 |

#### 5. 异常分析
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/script-results/anomalies` |
| **权限** | 无需认证 |
| **说明** | 分析失败任务中的错误类型和高频失败步骤 |

**响应：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `error_type_distribution` | Array | 错误类型分布 [{error_type, count, type}] |
| `error_types` | Array | 同上（别名） |
| `top_failing_steps` | Array | 最易失败的10个步骤 [{step_name, fail_count, error_types}] |

#### 6. 获取单个结果详情
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/script-results/{result_id}` |
| **权限** | 无需认证 |
| **说明** | 获取单个脚本结果的完整详情 |

**路径参数：**
| 参数名 | 类型 | 说明 |
|--------|------|------|
| `result_id` | String | 结果记录UUID |

#### 7. 删除结果
| 属性 | 值 |
|------|-----|
| **URL** | `DELETE /api/script-results/{result_id}` |
| **权限** | 无需认证 |
| **说明** | 删除脚本结果及其所有步骤（级联删除） |

---

### 配置管理接口

#### 1. 获取配置
| 属性 | 值 |
|------|-----|
| **URL** | `GET /api/config` |
| **权限** | 无需认证 |
| **说明** | 获取管理平台配置 |

**响应：**
```json
{
  "management_platform_url": "http://localhost:8001/api/script-results/upload",
  "username": ""
}
```

#### 2. 更新配置
| 属性 | 值 |
|------|-----|
| **URL** | `POST /api/config` |
| **权限** | 无需认证 |
| **说明** | 更新管理平台配置 |

**请求体：** JSON对象，键为配置key，值为配置value
**响应：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | String | "配置更新成功" |
| `config` | Object | 更新后的完整配置 |

---

### 管理平台数据库模型

#### Folder（文件夹）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | String(36) | PK, Index | UUID | 文件夹唯一ID |
| `name` | String(255) | NOT NULL, Index | - | 文件夹名称 |
| `created_at` | DateTime | - | utcnow | 创建时间 |

#### ScriptResult（脚本结果）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | String(36) | PK, Index | UUID | 结果唯一ID |
| `task_id` | Integer | NOT NULL, Index | - | 任务ID |
| `task_name` | String(255) | NOT NULL, Index | - | 任务名称 |
| `script_name` | String(255) | NOT NULL, Index | - | 脚本名称 |
| `started_at` | String(50) | NOT NULL, Index | - | 开始时间（ISO格式） |
| `finished_at` | String(50) | NOT NULL | - | 结束时间（ISO格式） |
| `status` | String(50) | NOT NULL, Index | - | 状态：completed、failed |
| `parameters` | JSON | - | `{}` | 执行参数 |
| `total_steps` | Integer | NOT NULL | - | 总步骤数 |
| `passed_steps` | Integer | NOT NULL | - | 通过步骤数 |
| `failed_steps` | Integer | NOT NULL | - | 失败步骤数 |
| `skipped_steps` | Integer | NOT NULL | - | 跳过步骤数 |
| `total_duration` | Float | NOT NULL | - | 总时长（秒） |
| `pass_rate` | Float | NOT NULL | - | 通过率 |
| `username` | String(100) | NULL, Index | `""` | 用户名标识 |
| `script_count` | Integer | NULL | NULL | 脚本数量 |
| `created_at` | DateTime | Index | utcnow | 创建时间 |

**数据库索引：**
- `idx_script_results_status` - 按状态查询
- `idx_script_results_started_at` - 按开始时间查询
- `idx_script_results_username` - 按用户名查询
- `idx_script_results_task_name` - 按任务名查询
- `idx_script_results_created_at` - 按创建时间查询

#### StepResultModel（步骤结果）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | String(36) | PK, Index | UUID | 步骤唯一ID |
| `script_result_id` | String(36) | FK, Index, NOT NULL | - | 所属结果ID（级联删除） |
| `step_name` | String(255) | NOT NULL, Index | - | 步骤名称 |
| `step_order` | Integer | NOT NULL | - | 步骤顺序 |
| `action_type` | String(100) | NOT NULL | - | 操作类型 |
| `status` | String(50) | NOT NULL, Index | - | 步骤状态 |
| `duration` | Float | NOT NULL | - | 执行时长（秒） |
| `error` | Text | NULL | NULL | 错误信息 |
| `error_stack` | Text | NULL | NULL | 错误堆栈 |
| `screenshot` | String(500) | NULL | NULL | 截图URL |
| `action_values` | JSON | - | `{}` | 操作值（可含 sub_steps） |

**数据库索引：**
- `idx_step_results_status` - 按状态查询
- `idx_step_results_step_name` - 按步骤名查询

#### Config（配置）
| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | Integer | PK, Index | 自增 | 配置ID |
| `key` | String(100) | NOT NULL, UNIQUE, Index | - | 配置键 |
| `value` | JSON | NULL | NULL | 配置值 |
| `updated_at` | DateTime | - | utcnow | 更新时间 |

---

## 三、操作类型完整定义

### 测试步骤操作类型 (TestStep.ACTION_TYPE_CHOICES)

| 操作代码 | 中文名称 | 说明 |
|----------|---------|------|
| `navigate` | 导航到URL | 打开指定网址 |
| `click` | 点击元素 | 点击页面元素 |
| `fill` | 填充输入框 | 在输入框中填入文本 |
| `select` | 选择下拉选项 | 从下拉菜单中选择 |
| `random_select` | 随机选择 | 从多个选项中随机选择 |
| `random_number` | 随机数值 | 在范围内生成随机数 |
| `check` | 勾选复选框 | 选中checkbox |
| `uncheck` | 取消勾选 | 取消选中checkbox |
| `wait` | 等待 | 固定时长等待 |
| `wait_for_selector` | 等待元素 | 等待元素出现 |
| `screenshot` | 截图 | 对页面或元素截图 |
| `scroll` | 滚动 | 滚动页面 |
| `hover` | 悬停 | 鼠标悬停到元素上 |
| `focus` | 聚焦 | 将焦点设置到元素 |
| `press` | 按键 | 按下键盘按键 |
| `upload` | 上传文件 | 上传文件到页面 |
| `assert_text` | 断言文本 | 验证文本内容 |
| `assert_visible` | 断言可见 | 验证元素可见 |
| `assert_value` | 断言值 | 验证元素值 |
| `action_set` | 动作集合 | 引用并执行动作集合 |
| `custom` | 自定义操作 | 自定义逻辑 |

### 动作集合操作类型 (ActionSetStep.ACTION_TYPE_CHOICES)

| 操作代码 | 中文名称 | 说明 |
|----------|---------|------|
| `click` | 点击元素 | 点击页面元素 |
| `fill` | 填充输入框 | 在输入框中填入文本 |
| `select` | 选择下拉选项 | 从下拉菜单中选择 |
| `random_select` | 随机选择 | 从多个选项中随机选择 |
| `random_number` | 随机数值 | 在范围内生成随机数 |
| `check` | 勾选复选框 | 选中checkbox |
| `uncheck` | 取消勾选 | 取消选中checkbox |
| `wait` | 等待 | 固定时长等待 |
| `wait_for_selector` | 等待元素 | 等待元素出现 |
| `scroll` | 滚动 | 滚动页面 |
| `hover` | 悬停 | 鼠标悬停到元素上 |
| `focus` | 聚焦 | 将焦点设置到元素 |
| `press` | 按键 | 按下键盘按键 |
| `assert_text` | 断言文本 | 验证文本内容 |
| `assert_visible` | 断言可见 | 验证元素可见 |

### 状态枚举

**任务状态 (TestTask.STATUS_CHOICES)：**
| 状态码 | 中文 | 说明 |
|--------|------|------|
| `pending` | 待执行 | 任务已创建，等待执行 |
| `running` | 执行中 | 任务正在执行 |
| `completed` | 已完成 | 任务成功完成 |
| `failed` | 失败 | 任务执行失败 |
| `cancelled` | 已取消 | 任务被手动取消 |

**测试结果状态 (TestResult.STATUS_CHOICES)：**
| 状态码 | 中文 | 说明 |
|--------|------|------|
| `passed` | 通过 | 步骤执行成功 |
| `failed` | 失败 | 步骤执行失败 |
| `skipped` | 跳过 | 步骤被跳过 |
| `error` | 错误 | 步骤发生异常 |

**上传状态 (TestTask.upload_status)：**
| 状态码 | 中文 | 说明 |
|--------|------|------|
| `none` | 未上传 | 未执行上传 |
| `uploading` | 上传中 | 正在上传 |
| `uploaded` | 已上传 | 上传成功 |
| `failed` | 上传失败 | 上传失败 |
| `pending` | 待上传 | 等待上传（任务完成但尚未上传） |

---

## 四、两平台接口交互关系

### 数据流

```
自动化测试平台                          自动化管理平台
     │                                       │
     │  执行任务 (POST /api/tests/tasks/:id/execute/)
     │  ────────────────────────────────────→│
     │                                       │
     │  任务执行完成，生成 TestResult 记录     │
     │                                       │
     │  上传结果 (POST /api/script-results/upload)
     │  ────────────────────────────────────→│
     │         ScriptResultUpload JSON        │
     │                                       │
     │                          创建 ScriptResult 记录
     │                          创建 StepResultModel 记录
     │                                       │
     │                                       │
```

### 上传数据映射

| 测试平台字段 | 管理平台字段 | 转换逻辑 |
|-------------|-------------|---------|
| `TestTask.id` | `task_id` | 直接映射 |
| `TestTask.name` | `task_name` | 直接映射 |
| `TestTask.script.name` | `script_name` | 通过关联获取 |
| `TestTask.started_at` | `started_at` | ISO格式转换 |
| `TestTask.finished_at` | `finished_at` | ISO格式转换 |
| `TestTask.status` | `status` | completed/failed |
| `TestResult.step_name` | `step_results[].step_name` | 每条记录映射 |
| `TestResult.step_order + 1` | `step_results[].step_order` | 从0开始改为从1开始 |
| `TestResult.status` | `step_results[].status` | 直接映射 |
| `TestResult.duration` | `step_results[].duration` | 直接映射 |
| `TestResult.error_message` | `step_results[].error` | 映射错误信息 |
| `TestResult.error_stack` | `step_results[].error_stack` | 映射错误堆栈 |
| `TestResult.action_values` | `step_results[].action_values` | 包含 sub_steps 嵌套 |
| `TestReport.*` | `total_steps, passed_steps...` | 从报告对象获取 |
| `GlobalConfig.username` | `username` | 从全局配置获取 |

---

## 五、Celery 异步任务与执行引擎

### 1. Celery 任务函数

#### execute_test_task（单脚本任务）
| 属性 | 值 |
|------|-----|
| **定义** | `@shared_task(bind=True)` |
| **参数** | `self: Task`, `task_id: Integer` |
| **说明** | 通过 Celery 异步执行单脚本测试任务 |

**执行流程：**
1. 获取 `TestTask` 对象
2. 删除旧的结果记录 (`task.results.all().delete()`)
3. 设置任务状态为 `running`，记录开始时间
4. 初始化 `PlaywrightEngine`（使用全局配置）
5. 创建异步事件循环，启动浏览器
6. 遍历脚本的启用步骤（按 order 排序）
7. 对每个步骤调用 `execute_step()` 执行
8. 将结果写入 `TestResult` 表
9. 如果步骤失败且 `continue_on_failure=false`，跳过后续步骤
10. 处理断点（breakpoint）重试逻辑
11. 计算统计信息，创建 `TestReport` 记录
12. 关闭浏览器和事件循环
13. 通过 `TestResultExporter` 保存 JSON 结果文件
14. 如果 `upload_to_management=true`，调用管理平台上传接口
15. 如果 `send_email=true`，发送通知邮件

**返回结果：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | Integer | 任务ID |
| `task_name` | String | 任务名称 |
| `script_name` | String | 脚本名称 |
| `started_at` | String | 开始时间（ISO格式） |
| `finished_at` | String | 结束时间（ISO格式） |
| `status` | String | 最终状态 |
| `step_results` | Array | 步骤执行结果列表 |
| `total_steps` | Integer | 总步骤数 |
| `passed_steps` | Integer | 通过数 |
| `failed_steps` | Integer | 失败数 |
| `skipped_steps` | Integer | 跳过数 |
| `total_duration` | Float | 总时长（秒） |
| `pass_rate` | Float | 通过率 |
| `parameters` | Object | 使用的参数 |

#### execute_multi_script_task（多脚本任务）
| 属性 | 值 |
|------|-----|
| **定义** | `@shared_task(bind=True)` |
| **参数** | `self: Task`, `task_id: Integer` |
| **说明** | 执行包含多个脚本的聚合测试任务 |

**执行流程：** 与单脚本类似，但会依次执行 `TaskScript` 关联的所有脚本。每个脚本使用独立的浏览器实例，步骤名称前加上 `[脚本名]` 前缀。

**返回额外字段：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `script_count` | Integer | 脚本总数 |
| `script_results` | Array | 各脚本汇总 [{status, name, passed_steps, failed_steps}] |
| `successful_scripts` | Integer | 成功脚本数 |
| `failed_scripts` | Integer | 失败脚本数 |

#### execute_step（步骤执行）
| 属性 | 值 |
|------|-----|
| **定义** | `def execute_step(loop, engine, step, parameters, step_screenshot, global_config)` |
| **参数** | |
| `loop` | asyncio.EventLoop | 异步事件循环 |
| `engine` | PlaywrightEngine | 浏览器引擎实例 |
| `step` | TestStep | 步骤对象 |
| `parameters` | dict | 测试参数映射 |
| `step_screenshot` | bool | 是否截图 |
| `global_config` | GlobalConfig | 全局配置对象 |

**处理逻辑：**
1. 如果是 `action_set` 类型，展开执行所有子步骤，结果存入 `sub_steps` 数组
2. 替换参数化值（`{{param_name}}` 格式）
3. 构建 `element_config`（从 `action_config.locators` 或 `TestStep.element`）
4. 处理特殊操作类型配置（`random_select`、`random_number`、`click` 的 `force`）
5. 执行重试逻辑（`retry_count` 次重试，间隔 `retry_interval` 毫秒）
6. 调用 `engine.execute_action()` 执行操作
7. 根据结果构建 `action_values`（如 `{'输入值': 'xxx'}`、`{'操作': '点击'}`）

**返回结果：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `step_name` | String | 步骤名称 |
| `step_order` | Integer | 步骤顺序 |
| `action_type` | String | 操作类型 |
| `status` | String | 执行状态 |
| `duration` | Float | 执行时长（秒） |
| `error` | String/null | 简化错误信息 |
| `error_stack` | String/null | 原始错误堆栈 |
| `screenshot` | String/null | 页面截图路径 |
| `element_screenshot` | String/null | 元素截图路径 |
| `action_values` | Object | 操作值 |
| `logs` | Array | 执行日志 |
| `sub_results` | Array | 子步骤结果（仅 action_set） |

#### execute_action_set_step（动作集合子步骤执行）
| 属性 | 值 |
|------|-----|
| **定义** | `def execute_action_set_step(loop, engine, as_step, parameters, step_screenshot)` |
| **参数** | |
| `as_step` | ActionSetStep | 动作集合步骤对象 |
| 其余 | 同 `execute_step` | - |

**与 execute_step 的区别：**
- 处理 `action_value_type` 为 `parameter` 时，从 `parameters` 中取值
- 使用 `ActionSetStep` 特有的字段（`locator_type`、`locator_value`、`wait_timeout`、`force_click` 等）
- 不记录 `screenshot`，只记录 `element_screenshot`

#### cleanup_old_results（清理旧结果）
| 属性 | 值 |
|------|-----|
| **定义** | `@shared_task` |
| **参数** | `days: Integer` (默认30) |
| **说明** | 清理超过指定天数的已完成/失败/取消任务 |

#### run_test_task_sync / run_multi_script_task_sync
| 属性 | 值 |
|------|-----|
| **定义** | 同步执行包装函数 |
| **说明** | 不使用 Celery 时，创建 FakeRequest/FakeSelf 模拟 Celery 任务上下文，直接调用内部执行逻辑 |

---

### 2. Playwright 引擎

#### PlaywrightEngine 核心方法
| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `__init__` | `headless`, `timeout`, `slow_mo`, `global_config` | - | 初始化引擎配置 |
| `start` | `viewport: dict` | `page: Page` | 启动浏览器并打开页面 |
| `close` | - | - | 关闭浏览器 |
| `execute_action` | `action_type`, `element_config`, `value`, `config`, `step_screenshot` | `dict` | 执行指定操作，返回 `{success, error, original_error, screenshot, element_screenshot, selected_value, available_options, generated_value, random_min, random_max}` |
| `take_screenshot` | `name: str` | `str` | 截图并返回文件路径 |
| `_resolve_locator` | `page`, `config` | `Locator` | 解析定位器（支持主定位器和备用定位器回退） |

**element_config 结构：**
```python
{
    'type': 'css',           # 定位类型
    'value': '#login-btn',   # 定位值
    'timeout': 30000,        # 等待超时（毫秒）
    'backup_locators': [     # 备用定位器列表
        {'type': 'xpath', 'value': '//button[@id="login"]'}
    ]
}
```

---

### 3. ScriptManager（脚本管理器）

#### SCRIPT_SCHEMA（脚本验证模式）
基于 JSON Schema Draft-07，验证脚本数据结构。

**必填字段：** `name`、`target_url`、`steps`

**步骤枚举操作类型：**
```
navigate, click, fill, select, random_select, check, uncheck,
wait, wait_for_selector, screenshot, scroll, hover, focus,
press, upload, assert_text, assert_visible, assert_value, custom
```

#### ScriptManager 类方法
| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `__init__` | `scripts_dir: Path` | - | 初始化脚本目录 |
| `save_script_to_json` | `script_data: dict`, `filename: str` | `Path` | 保存脚本为 JSON 文件 |
| `load_script_from_json` | `filename: str` | `dict` | 从 JSON 文件加载脚本 |
| `validate_script` | `script_data: dict` | `dict` | 验证脚本数据，返回 `{valid, errors}` |
| `list_script_files` | - | `List[str]` | 列出所有脚本文件 |
| `delete_script_file` | `filename: str` | `bool` | 删除脚本文件 |

---

### 4. TestResultExporter（测试结果导出器）

#### 核心属性
| 属性名 | 类型 | 说明 |
|--------|------|------|
| `RESULTS_DIR` | `str` | `"test_results"` |
| `SCREENSHOTS_DIR` | `str` | `"test_results/screenshots"` |

#### 核心方法
| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `save_result` | `task_id: int`, `result_data: dict` | `str` | 保存结果为 JSON 文件，返回文件路径 |
| `load_result` | `task_id: int` | `dict` | 从 JSON 文件加载结果 |
| `list_results` | `status: str` (可选) | `list` | 列出结果文件 |
| `delete_result` | `task_id: int` | `bool` | 删除结果文件 |
| `export_to_excel` | `result_data: dict`, `output_path: str` | `str` | 导出为 Excel（openpyxl） |
| `export_to_json` | `result_data: dict`, `output_path: str` | `str` | 导出为格式化 JSON |
| `clear_all_results` | `clear_screenshots: bool` | `int` | 清理所有结果文件，返回删除数量 |
| `clear_screenshots` | - | `int` | 仅清理截图文件 |
| `get_result_file_path` | `task_id: int` | `str` | 获取结果文件路径 |

---

### 5. ErrorMessageManager（错误消息管理器）

#### 内置错误匹配规则 (BUILTIN_RULES)
| 规则名称 | 正则模式 | 适用操作类型 | 友好消息 |
|---------|---------|-------------|---------|
| `element_not_found` | `(locator timed out|Element not found|Could not find element)` | `click` | 元素未找到 |
| `element_not_interactable` | `(element is not visible|element not interactable|element is not clickable)` | `click` | 元素不可交互 |
| `element_obscured` | `(element is obscured|click intercepted|element click intercepted)` | `click` | 元素被遮挡 |
| `element_detached` | `(element is not attached to the DOM|detached|target closed)` | `click` | 元素已从DOM移除 |
| `selector_invalid` | `(malformed selector|invalid selector)` | `click` | 选择器无效 |
| `fill_element_not_found` | `(locator timed out|Element not found)` | `fill` | 输入框元素未找到 |
| `fill_not_interactable` | `(element is not visible|element is not editable)` | `fill` | 输入框不可编辑 |
| `fill_element_obscured` | `(element is obscured)` | `fill` | 输入框被遮挡 |
| `fill_detached` | `(element is not attached to the DOM)` | `fill` | 输入框已从DOM移除 |
| `page_closed` | `(page.*closed|browser.*closed|context.*closed)` | `fill` | 页面已关闭 |
| `navigation_failed` | `(net::ERR_|navigation failed|timeout.*navigation)` | `click` | 页面导航失败 |
| `timeout` | `(Timeout.*exceeded|timed out after|TimeoutError)` | `click` | 操作超时 |
| `network_error` | `(net::ERR_|network error|connection refused)` | `click` | 网络异常 |

#### 核心方法
| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `get_friendly_message` | `error_message: str`, `action_type: str` | `str` | 匹配并返回友好错误消息 |
| `add_custom_rule` | `name`, `pattern`, `message_template`, `action_type` | - | 添加自定义匹配规则 |
| `get_custom_rules` | - | `list` | 获取所有自定义规则 |
| `delete_rule` | `rule_name: str` | - | 删除自定义规则 |

---

## 六、错误响应格式

### 自动化测试平台（DRF 标准格式）
```json
{
    "detail": "错误描述信息",
    "non_field_errors": ["非字段级错误"],
    "field_name": ["字段错误信息"]
}
```

**常见 HTTP 状态码：**
| 状态码 | 说明 |
|--------|------|
| `400` | 请求参数错误/业务逻辑错误 |
| `401` | 未认证 |
| `403` | 无权限 |
| `404` | 资源不存在 |
| `405` | 方法不允许 |
| `409` | 冲突（如 code 已存在） |
| `500` | 服务器内部错误 |

### 自动化管理平台（FastAPI 标准格式）
```json
{
    "detail": "错误描述信息"
}
```

---

## 七、前端 API 调用示例

### 自动化管理平台前端 (`src/api/index.js`)

```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:8001/api',
  timeout: 10000,
})

// 请求拦截器 - 统一处理错误提示
api.interceptors.response.use(
  response => response,
  error => {
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

// 示例调用
const getScriptResults = async (params) => {
  const response = await api.get('/script-results', { params })
  return response.data
}

const uploadScriptResult = async (data) => {
  const response = await api.post('/script-results/upload', data)
  return response.data
}
```

---

## 八、部署说明

### 1. 自动化测试平台

```bash
# 1. 进入项目目录
cd c:\Users\ittest\Desktop\new-python

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
copy .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY 等

# 4. 初始化数据库
python manage.py migrate

# 5. 创建超级用户（可选）
python manage.py createsuperuser

# 6. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

**可选：启动 Celery Worker**
```bash
celery -A automation_test_platform worker -l info
```

### 2. 自动化管理平台

```bash
# 1. 进入后端目录
cd c:\Users\ittest\Desktop\new-python\automated_management_platform\backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行数据库迁移（如果首次运行或从旧数据迁移）
python migrate_json_to_db.py

# 4. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. 前端构建

```bash
# 1. 进入前端目录
cd c:\Users\ittest\Desktop\new-python\automated_management_platform\frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 生产构建
npm run build
```

### 4. 环境变量完整列表

| 变量 | 平台 | 默认值 | 说明 |
|------|------|--------|------|
| `SECRET_KEY` | 测试平台 | 必填 | Django 加密密钥 |
| `DEBUG` | 测试平台 | `True` | 调试模式 |
| `DATABASE_URL` | 测试平台 | `sqlite:///db.sqlite3` | 测试平台数据库 |
| `DATABASE_URL` | 管理平台 | `sqlite:///./automated_management.db` | 管理平台数据库 |
| `CELERY_BROKER_URL` | 测试平台 | `redis://localhost:6379/0` | Celery 消息代理 |
| `CELERY_RESULT_BACKEND` | 测试平台 | `redis://localhost:6379/1` | Celery 结果存储 |

---

## 九、集合市场内部实现

### 代理请求函数

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `_marketplace_get(request, endpoint, params)` | request, endpoint, params | `requests.Response` | 向集合市场后端发送 GET 请求 |
| `_marketplace_post(request, endpoint, data, params)` | request, endpoint, data, params | `requests.Response` | 向集合市场后端发送 POST 请求 |

**逻辑说明：**
- 目标地址由 `GlobalConfig.marketplace_api_url` 决定
- 自动添加请求头：`Content-Type: application/json`、`Accept: application/json`
- 捕获并记录请求异常

### 元数据补充

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `_enrich_items_with_metadata(items, request)` | items 列表, request | `list` | 为市场条目添加 `used_count` 和 `imported` 标记 |

**逻辑说明：**
1. 如果 item 是 JSON 文件（`is_file=True` 且 `name.endswith('.json')`），则：
   - 读取 JSON 内容
   - 检查本地 `ActionSet.objects.filter(code=content['code'])` 是否存在 → 标记 `imported=True`
   - 统计引用次数 → 标记 `used_count=N`
2. 如果是文件夹或无法读取的 JSON，标记 `imported=False`、`used_count=0`

---

## 十、序列化器完整映射

### TestTask 相关

| 序列化器 | 字段列表 | 嵌套关系 | 说明 |
|----------|---------|---------|------|
| `TestTaskListSerializer` | id, name, script, script_name, script_code, status, status_display, group, group_name, created_by, created_by_name, created_at, updated_at, started_at, finished_at, task_scripts, results_count | task_scripts (嵌套), report (嵌套) | 列表页展示 |
| `TestTaskWithReportListSerializer` | id, name, script, script_name, status, status_display, group, group_name, created_by, created_by_name, created_at, task_scripts, results_count, report | task_scripts, report | 带报告的列表 |
| `TestTaskDetailSerializer` | id, name, script, script_name, status, status_display, group, group_name, created_by, created_by_name, created_at, task_scripts, parameters, scheduled_time, upload_to_management, celery_task_id, started_at, finished_at, results_count, scripts_passed, scripts_failed, results, report | task_scripts, results, report | 详情页完整数据 |
| `TestTaskCreateSerializer` | id, name, script, script_name, status, status_display, group, group_name, created_by, created_by_name, created_at, task_scripts, scheduled_time, parameters, upload_to_management, send_email | task_scripts (写入嵌套) | 创建/更新任务 |

### TestResult 相关

| 序列化器 | 字段列表 | 说明 |
|----------|---------|------|
| `TestResultSerializer` | id, task, step_name, step_order, status, status_display, duration, error_message, error_stack, original_error_message, screenshot, action_values, logs, created_at | 测试结果 |

### TestReport 相关

| 序列化器 | 字段列表 | 说明 |
|----------|---------|------|
| `TestReportSerializer` | id, task, total_steps, passed_steps, failed_steps, skipped_steps, total_duration, summary, pass_rate, created_at | 测试报告 |

### ActionSet 相关

| 序列化器 | 字段列表 | 说明 |
|----------|---------|------|
| `ActionSetListSerializer` | id, name, code, description, category, category_display, is_builtin, is_active, steps_count, parameters_count, used_scripts_count, group, group_name, created_by, created_by_name, created_at, updated_at | 列表页展示 |
| `ActionSetDetailSerializer` | id, name, code, description, category, category_display, is_builtin, is_active, steps, parameters, group, group_name, created_by, created_by_name, created_at, updated_at | 详情页（含嵌套 steps 和 parameters） |
| `ActionSetCreateSerializer` | id, name, code, description, category, is_active, group, steps, parameters | 创建/更新（支持嵌套写入） |
| `ActionSetStepSerializer` | id, action_set, name, order, action_type, action_type_display, locator_type, locator_type_display, locator_value, locator_description, action_value, action_value_type, action_value_type_display, parameter_name, action_config, wait_timeout, continue_on_failure, retry_count, retry_interval, random_options, select_mode, select_mode_display, random_min, random_max, force_click, description, is_enabled, created_at, updated_at | 步骤详情 |
| `ActionSetStepNestedSerializer` | name, order, action_type, locator_type, locator_value, locator_description, action_value, action_value_type, parameter_name, action_config, wait_timeout, continue_on_failure, retry_count, retry_interval, random_options, select_mode, random_min, random_max, force_click, description, is_enabled | 步骤写入（无只读字段） |
| `ActionSetParameterSerializer` | id, name, code, description, default_value, is_required, order | 参数详情 |

### GlobalConfig 相关

| 序列化器 | 字段列表 | 说明 |
|----------|---------|------|
| `GlobalConfigSerializer` | id, headless_mode, default_timeout, step_screenshot, slow_mo, viewport_width, viewport_height, scroll_distance, scroll_direction, marketplace_api_url, management_platform_url, username, email_smtp_host, email_smtp_port, email_username, email_password, email_use_ssl, email_recipients, email_enable, report_base_url, updated_at, updated_by, updated_by_name | 全局配置（含用户信息） |

---

## 十一、邮件通知模块

### send_task_notification

| 属性 | 值 |
|------|-----|
| **定义** | `send_task_notification(task_id, task_name, status, result_data=None, report_id=None)` |
| **文件** | `test_manager/email_notification.py` |
| **说明** | 发送任务执行结果通知邮件 |

**参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| `task_id` | Integer | 任务ID |
| `task_name` | String | 任务名称 |
| `status` | String | 任务状态（`completed`/`failed`） |
| `result_data` | dict | 测试结果数据（可选） |
| `report_id` | String | 管理平台报告ID（可选） |

**邮件内容：**
- 主题：`[自动化测试] {任务名} - 成功/失败`
- 格式：HTML 富文本邮件（响应式设计）
- 颜色：成功用 `#10b981`（绿色），失败用 `#ef4444`（红色）
- 统计展示：通过率、通过/成功数、失败数、跳过数（多脚本/单脚本模式不同布局）
- 底部：查看完整报告按钮（链接到管理平台报告页面）

**发送逻辑：**
1. 从 `GlobalConfig` 获取邮件配置
2. 检查 `email_enable` 开关和配置完整性
3. 根据多脚本/单脚本模式生成不同的统计表格
4. 支持 SMTP SSL（端口 465）和 STARTTLS 两种模式
5. 成功返回 `True`，失败返回 `False` 并记录日志

---

## 十二、聚合任务创建逻辑

### TaskViewSet.perform_create

当创建包含多个脚本的任务时，自动标记为聚合任务并创建 `TaskScript` 关联：

```python
# 1. 保存任务
task = serializer.save(
    created_by=self.request.user,
    status='idle'
)

# 2. 如果是多脚本任务
if len(scripts) > 1:
    task.is_aggregate_task = True
    task.save()
    
    for i, script in enumerate(scripts):
        TaskScript.objects.create(
            aggregate_task=task,
            script=script,
            order=i
        )
```

**字段映射：**
| 前端参数 | 模型字段 | 说明 |
|---------|---------|------|
| `scripts[]` | `TaskScript.script` | 选中的脚本ID列表 |
| `parameters` | `TestTask.parameters` | 全局参数 |
| `group` | `TestTask.group` | 分组 |
| `scheduled_time` | `TestTask.scheduled_time` | 计划执行时间 |
| `upload_to_management` | `TestTask.upload_to_management` | 是否上传管理平台 |

---

## 十三、数据库模型关系图

```
Group (分组)
  ├── TestScript.group (FK)
  ├── ActionSet.group (FK)
  └── TestTask.group (FK)

TestScript (测试脚本)
  ├── TestStep.script (FK) → TestStep
  ├── TaskScript.script (FK) → TaskScript → TestTask
  └── TestScriptVersion.script (FK)

ElementLocator (元素定位器)
  └── TestStep.element (FK)

ActionSet (动作集合)
  ├── ActionSetStep.action_set (FK)
  ├── ActionSetParameter.action_set (FK)
  └── TestStep.action_set_ref (FK)

TestTask (测试任务)
  ├── TestResult.task (FK)
  ├── TestReport.task (OneToOne)
  ├── TaskScript.task (FK)
  ├── TaskGroupItem.task (FK) (已废弃)
  └── TestScriptVersion.task (FK) (已废弃)

TestResult (测试结果)
  └── screenshot → ImageField (文件存储)

GlobalConfig (全局配置)
  └── 单例模式（仅一条记录，id=1）
```

---

## 十四、常见问题排查

### 1. Celery 未启动时的同步执行模式
当 Celery 不可用时（Redis 未启动、Worker 未运行），系统会自动降级为同步执行模式：
- `execute_test_task.apply_async()` 失败时捕获异常
- 调用 `run_test_task_sync(task_id)` 替代
- 同步模式下创建 `FakeRequest`（包含当前用户）和 `FakeSelf`（模拟 Celery Task 对象）
- **注意**：同步执行会阻塞 HTTP 请求，直到任务完成

### 2. 数据库迁移冲突处理
当出现多个 `0005_xxx.py` 等冲突迁移文件时：
```bash
# 查看迁移状态
python manage.py showmigrations

# 合并冲突（选择保留正确的迁移链）
python manage.py makemigrations --merge

# 或手动删除冲突文件，重新生成
python manage.py makemigrations
python manage.py migrate
```

### 3. 截图路径配置
- 截图存储在 `test_results/screenshots/` 目录
- `TestResult.screenshot` 使用 Django `ImageField`，通过 `MEDIA_URL` 访问
- 确保 `settings.py` 中配置了 `MEDIA_ROOT` 和 `MEDIA_URL`
- 管理平台通过 `report_base_url` 拼接报告访问链接

### 4. 管理平台数据库迁移
```bash
cd automated_management_platform/backend
python migrate_json_to_db.py
```
- 迁移脚本自动创建数据库表
- 从 `uploads/script_results/*.json` 导入历史记录
- 从 `folders.json` 导入文件夹元数据
- 从 `config.json` 导入配置项
- 重复运行不会重复导入（通过 UUID 检查）

### 5. 跨域问题
- 管理平台已配置 CORS：`allow_origins=["*"]`
- 如需限制来源，修改 `main.py` 中的 `allow_origins` 列表

### 6. Python 3.14 兼容性
- 使用 SQLAlchemy >= 2.0.36（低版本不兼容 Python 3.14）
- 使用 Alembic >= 1.14.0
- Django 4.x+ 支持 Python 3.14

---

## 十五、前端组件结构（自动化管理平台）

| 组件 | 文件 | 说明 |
|------|------|------|
| `App.vue` | `frontend/src/App.vue` | 根组件，包含路由和布局 |
| `GlobalConfig` | `components/GlobalConfig.vue` | 全局配置页 |
| `FileList` | `components/FileList.vue` | 文件列表/文件夹浏览 |
| `FileUpload` | `components/FileUpload.vue` | 文件上传模态框 |
| `FilePreview` | `components/FilePreview.vue` | JSON 文件预览 |
| `ScriptAnalysis` | `components/ScriptAnalysis.vue` | 脚本分析（统计+趋势+异常） |
| `ReportList` | `components/ReportList.vue` | 报告列表（分页+过滤） |
| `ReportDetail` | `components/ReportDetail.vue` | 报告详情（可折叠子步骤） |
| `ContextMenu` | `components/ContextMenu.vue` | 右键菜单 |
| `ConfirmModal` | `components/ConfirmModal.vue` | 确认对话框 |
| `FolderModal` | `components/FolderModal.vue` | 新建文件夹模态框 |
| `RenameModal` | `components/RenameModal.vue` | 重命名模态框 |
| `DeleteConfirmModal` | `components/DeleteConfirmModal.vue` | 删除确认模态框 |

**状态管理：** 使用 Vue 3 `ref`/`reactive` 组件级状态，无全局状态管理库

**API 调用：** `src/api/index.js` 封装 axios，统一错误处理（Element Plus `ElMessage`）

**UI 框架：** Element Plus + Bootstrap Icons
