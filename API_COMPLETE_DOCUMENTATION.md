# API 接口完整文档

本文档涵盖两个项目的所有 REST API 接口：
- **自动化测试平台** (automation_test_platform) - Django + DRF，端口 8000
- **自动化管理平台** (automated_management_platform) - FastAPI，端口 8001

---

## 一、自动化测试平台 - Core API (`/api/core/`)

### 1.1 健康检查

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/core/health/` |
| 函数名 | `health_check` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L36) |
| 权限 | AllowAny |
| 说明 | 检查平台是否正常运行 |

**请求参数:** 无

**响应示例:**
```json
{
  "status": "ok",
  "message": "Automation Test Platform is running"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态: `ok` 表示平台运行正常 |
| `message` | string | 平台提示信息 |

---

### 1.2 仪表盘统计

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/core/dashboard/` |
| 函数名 | `dashboard` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L44) |
| 权限 | 需要登录 |
| 说明 | 获取任务/脚本/元素统计数据和最近任务 |

**请求参数:** 无

**响应示例:**
```json
{
  "statistics": {
    "total_tasks": 10,
    "running_tasks": 1,
    "completed_tasks": 7,
    "failed_tasks": 2,
    "total_scripts": 15,
    "published_scripts": 10,
    "total_elements": 25,
    "pass_rate": 85.5
  },
  "recent_tasks": [
    {"id": 1, "name": "任务1", "status": "completed", "created_at": "2024-01-01T10:00:00"}
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `statistics` | object | 统计数据对象 |
| `statistics.total_tasks` | int | 总任务数 |
| `statistics.running_tasks` | int | 执行中的任务数 |
| `statistics.completed_tasks` | int | 已完成的任务数 |
| `statistics.failed_tasks` | int | 失败的任务数 |
| `statistics.total_scripts` | int | 总脚本数 |
| `statistics.published_scripts` | int | 已发布的脚本数 |
| `statistics.total_elements` | int | 启用的元素定位器数 |
| `statistics.pass_rate` | float | 通过率百分比 |
| `recent_tasks` | array | 最近5条任务记录 |
| `recent_tasks[].id` | int | 任务ID |
| `recent_tasks[].name` | string | 任务名称 |
| `recent_tasks[].status` | string | 任务状态: `pending`/`running`/`completed`/`failed`/`cancelled` |
| `recent_tasks[].created_at` | string | 创建时间(ISO格式) |

---

### 1.3 分组列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/core/groups/` |
| 函数名 | `group_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L89) |
| 权限 | AllowAny |
| 说明 | 获取分组列表，可按类型筛选 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `type` | string | 否 | 分组类型: `script`, `action_set`, `task` |

**响应示例:**
```json
[
  {
    "id": 1,
    "name": "脚本分组",
    "code": "script_group_1",
    "type": "script",
    "type_display": "脚本分组",
    "description": "",
    "parent": null,
    "order": 0,
    "full_path": "脚本分组",
    "children_count": 2,
    "created_by": 1,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 分组主键 |
| `name` | string | 分组名称 |
| `code` | string | 分组代码(唯一标识) |
| `type` | string | 分组类型: `script`/`action_set`/`task` |
| `type_display` | string | 类型显示名 |
| `description` | string | 描述 |
| `parent` | int/null | 父分组ID，无则为null |
| `order` | int | 排序号 |
| `full_path` | string | 完整层级路径，如"父分组 / 子分组" |
| `children_count` | int | 子分组数量 |
| `created_by` | int | 创建人用户ID |
| `created_at` | string | 创建时间(ISO格式) |
| `updated_at` | string | 更新时间(ISO格式) |

---

### 1.4 创建分组

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/core/groups/` |
| 函数名 | `group_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L89) |
| 权限 | AllowAny |
| 说明 | 创建新分组 |

**请求体:**
```json
{
  "name": "新分组",
  "code": "new_group",
  "type": "script",
  "description": "描述",
  "parent": null,
  "order": 0
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 分组名称 |
| `code` | string | 是 | 分组代码(同一类型下唯一) |
| `type` | string | 是 | 分组类型: `script`/`action_set`/`task` |
| `description` | string | 否 | 描述，默认空 |
| `parent` | int/null | 否 | 父分组ID，支持层级结构 |
| `order` | int | 否 | 排序，默认0 |

**响应状态码:** 201 Created

---

### 1.5 分组详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/core/groups/<id>/` |
| 函数名 | `group_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L107) |
| 权限 | AllowAny |
| 说明 | 获取分组详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 分组主键 |

**响应示例:** 同分组列表单项结构

---

### 1.6 更新分组

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/core/groups/<id>/` |
| 函数名 | `group_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L107) |
| 权限 | AllowAny |
| 说明 | 更新分组信息 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 分组主键 |

**请求体:** 同创建分组

---

### 1.7 删除分组

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/core/groups/<id>/` |
| 函数名 | `group_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L107) |
| 权限 | AllowAny |
| 说明 | 删除分组，有子分组时不可删除 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 分组主键 |

**错误响应:** `{"error": "Cannot delete group with children"}`

---

### 1.8 清理截图

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/core/scripts/clear-screenshots/` |
| 函数名 | `clear_screenshots` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L128) |
| 权限 | AllowAny |
| 说明 | 删除所有截图文件 |

**响应示例:**
```json
{
  "message": "成功清理 5 个截图文件",
  "deleted_count": 5
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 清理结果描述 |
| `deleted_count` | int | 已删除的截图文件数量 |

---

### 1.9 清理任务结果

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/core/scripts/clear-task-results/` |
| 函数名 | `clear_task_results` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L148) |
| 权限 | AllowAny |
| 说明 | 删除所有任务结果 JSON 文件 |

**响应示例:**
```json
{
  "message": "成功清理 3 个任务结果文件",
  "deleted_count": 3
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 清理结果描述 |
| `deleted_count` | int | 已删除的任务结果文件数量 |

---

### 1.10 错误配置列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/core/error-config/` |
| 函数名 | `error_config_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L167) |
| 权限 | AllowAny |
| 说明 | 获取内置规则和自定义错误配置规则 |

**响应示例:**
```json
{
  "builtin_rules": [
    {"name": "规则名", "pattern": "正则", "message_template": "消息模板", "action_type": "click"}
  ],
  "custom_rules": [
    {"id": 1, "name": "自定义规则", "pattern": "正则", "message_template": "模板", "action_type": ""}
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `builtin_rules` | array | 内置错误规则列表 |
| `builtin_rules[].name` | string | 规则名称 |
| `builtin_rules[].pattern` | string | 正则表达式，用于匹配错误 |
| `builtin_rules[].message_template` | string | 消息模板 |
| `builtin_rules[].action_type` | string | 动作类型，如 `click` |
| `custom_rules` | array | 自定义错误规则列表 |
| `custom_rules[].id` | int | 规则主键 |
| `custom_rules[].name` | string | 规则名称 |
| `custom_rules[].pattern` | string | 正则表达式 |
| `custom_rules[].message_template` | string | 消息模板 |
| `custom_rules[].action_type` | string | 动作类型 |

---

### 1.11 新增错误配置

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/core/error-config/` |
| 函数名 | `error_config_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L167) |
| 权限 | AllowAny |
| 说明 | 添加自定义错误规则 |

**请求体:**
```json
{
  "name": "规则名称",
  "pattern": "正则表达式",
  "message_template": "消息模板",
  "action_type": ""
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 规则名称 |
| `pattern` | string | 是 | 正则表达式，用于匹配错误信息 |
| `message_template` | string | 是 | 消息模板，匹配时显示的消息 |
| `action_type` | string | 否 | 关联的动作类型，如 `click`、`fill` 等 |

**响应状态码:** 201 Created

---

### 1.12 更新错误配置

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/core/error-config/<id>/` |
| 函数名 | `update_error_config` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L195) |
| 权限 | AllowAny |
| 说明 | 更新自定义错误规则 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 规则ID |

**请求体:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 否 | 规则名称，未提供则保持原值 |
| `pattern` | string | 否 | 正则表达式，未提供则保持原值 |
| `message_template` | string | 否 | 消息模板，未提供则保持原值 |
| `action_type` | string | 否 | 动作类型，未提供则保持原值 |

---

### 1.13 删除错误配置

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/core/error-config/<id>/delete/` |
| 函数名 | `delete_error_config` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/core/views.py#L213) |
| 权限 | AllowAny |
| 说明 | 删除自定义错误规则 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 规则ID |

---

## 二、自动化测试平台 - Products API (`/api/products/`)

### 2.1 产品类型列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/products/` |
| 函数名 | `product_type_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L37) |
| 权限 | AllowAny |
| 说明 | 获取所有产品类型列表 |

**响应示例:**
```json
[
  {
    "id": 1,
    "name": "产品类型",
    "code": "product_type_1",
    "description": "描述",
    "is_active": true,
    "parameters_count": 3
  }
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 产品类型主键 |
| `name` | string | 产品类型名称 |
| `code` | string | 产品类型代码(唯一标识) |
| `description` | string | 描述信息 |
| `is_active` | bool | 是否启用 |
| `parameters_count` | int | 该产品类型下的参数数量 |

---

### 2.2 创建产品类型

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/products/` |
| 函数名 | `product_type_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L37) |
| 权限 | AllowAny |
| 说明 | 创建新产品类型 |

**请求体:**
```json
{
  "name": "新产品",
  "code": "new_product",
  "description": "描述",
  "icon": null,
  "is_active": true
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 产品类型名称 |
| `code` | string | 是 | 产品类型代码(唯一) |
| `description` | string | 否 | 描述信息，默认空 |
| `icon` | string/null | 否 | 图标URL或null |
| `is_active` | bool | 否 | 是否启用，默认true |

**响应状态码:** 201 Created

---

### 2.3 产品类型详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/products/<id>/` |
| 函数名 | `product_type_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L51) |
| 权限 | AllowAny |
| 说明 | 获取产品类型详情，含嵌套参数和选项 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 产品类型主键 |

**响应示例:**
```json
{
  "id": 1,
  "name": "产品类型",
  "code": "product_type_1",
  "description": "描述",
  "icon": "/media/product_icons/xxx.png",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "parameters_count": 3,
  "parameters": [
    {
      "id": 1,
      "name": "参数名",
      "code": "param_1",
      "input_type": "select",
      "is_required": true,
      "default_value": "",
      "placeholder": "请选择",
      "validation_regex": "",
      "order": 0,
      "is_active": true,
      "options": [
        {"id": 1, "display_value": "选项1", "actual_value": "value1", "price_modifier": "0.00", "order": 0, "is_active": true}
      ]
    }
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 产品类型主键 |
| `name` | string | 产品类型名称 |
| `code` | string | 产品类型代码 |
| `description` | string | 描述信息 |
| `icon` | string/null | 图标URL |
| `is_active` | bool | 是否启用 |
| `created_at` | string | 创建时间(ISO格式) |
| `updated_at` | string | 更新时间(ISO格式) |
| `parameters_count` | int | 参数数量 |
| `parameters` | array | 参数列表 |
| `parameters[].id` | int | 参数主键 |
| `parameters[].name` | string | 参数名称 |
| `parameters[].code` | string | 参数代码 |
| `parameters[].input_type` | string | 输入类型: `text`/`select`/`radio`/`checkbox`/`number`/`color`/`file` |
| `parameters[].is_required` | bool | 是否必填 |
| `parameters[].default_value` | string | 默认值 |
| `parameters[].placeholder` | string | 提示文字 |
| `parameters[].validation_regex` | string | 验证正则 |
| `parameters[].order` | int | 排序号 |
| `parameters[].is_active` | bool | 是否启用 |
| `parameters[].options` | array | 选项列表(仅select/radio/checkbox类型) |
| `parameters[].options[].id` | int | 选项主键 |
| `parameters[].options[].display_value` | string | 选项显示文本 |
| `parameters[].options[].actual_value` | string | 选项实际值 |
| `parameters[].options[].price_modifier` | string | 价格调整值(字符串格式小数) |
| `parameters[].options[].order` | int | 选项排序 |
| `parameters[].options[].is_active` | bool | 选项是否启用 |

---

### 2.4 更新产品类型

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/products/<id>/` |
| 函数名 | `product_type_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L51) |
| 权限 | AllowAny |
| 说明 | 更新产品类型信息 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 产品类型主键 |

**请求体:** 同创建产品类型，所有字段可选

---

### 2.5 删除产品类型

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/products/<id>/` |
| 函数名 | `product_type_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L51) |
| 权限 | AllowAny |
| 说明 | 删除产品类型 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 产品类型主键 |

---

### 2.6 产品参数列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/products/<product_type_id>/parameters/` |
| 函数名 | `product_parameter_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L69) |
| 权限 | AllowAny |
| 说明 | 获取指定产品类型的参数列表 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `product_type_id` | int | 是 | 产品类型主键 |

**响应示例:** 同产品类型详情中的 `parameters` 数组结构

---

### 2.7 创建产品参数

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/products/<product_type_id>/parameters/` |
| 函数名 | `product_parameter_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L69) |
| 权限 | AllowAny |
| 说明 | 为产品类型创建新参数 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `product_type_id` | int | 是 | 产品类型主键 |

**请求体:**
```json
{
  "name": "参数名",
  "code": "param_code",
  "input_type": "select",
  "is_required": true,
  "default_value": "",
  "placeholder": "提示",
  "validation_regex": "",
  "order": 0,
  "is_active": true,
  "options": [
    {"display_value": "选项1", "actual_value": "v1", "price_modifier": "0.00", "order": 0, "is_active": true}
  ]
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 参数名称 |
| `code` | string | 是 | 参数代码(同一产品类型下唯一) |
| `input_type` | string | 是 | 输入类型: `text`/`select`/`radio`/`checkbox`/`number`/`color`/`file` |
| `is_required` | bool | 否 | 是否必填，默认false |
| `default_value` | string | 否 | 默认值，默认空 |
| `placeholder` | string | 否 | 提示文字，默认空 |
| `validation_regex` | string | 否 | 验证正则，默认空 |
| `order` | int | 否 | 排序号，默认0 |
| `is_active` | bool | 否 | 是否启用，默认true |
| `options` | array | 否 | 选项列表，用于select/radio/checkbox类型 |
| `options[].display_value` | string | 是 | 选项显示文本 |
| `options[].actual_value` | string | 是 | 选项实际值 |
| `options[].price_modifier` | string | 否 | 价格调整，默认"0.00" |
| `options[].order` | int | 否 | 选项排序，默认0 |
| `options[].is_active` | bool | 否 | 是否启用，默认true |

**支持输入类型:** `text`, `select`, `radio`, `checkbox`, `number`, `color`, `file`

---

### 2.8 产品参数详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/products/parameters/<id>/` |
| 函数名 | `product_parameter_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L85) |
| 权限 | AllowAny |
| 说明 | 获取产品参数详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 参数主键 |

---

### 2.9 更新产品参数

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/products/parameters/<id>/` |
| 函数名 | `product_parameter_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L85) |
| 权限 | AllowAny |
| 说明 | 更新产品参数 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 参数主键 |

---

### 2.10 删除产品参数

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/products/parameters/<id>/` |
| 函数名 | `product_parameter_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/products/views.py#L85) |
| 权限 | AllowAny |
| 说明 | 删除产品参数 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 参数主键 |

---

## 三、自动化测试平台 - Test Manager API (`/api/tests/`)

### 3.1 任务列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/tests/tasks/` |
| 函数名 | `task_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L192) |
| 权限 | 需要登录 |
| 说明 | 获取任务列表（排除子任务） |

**响应示例:**
```json
[
  {
    "id": 1,
    "name": "测试任务",
    "script": 1,
    "script_name": "测试脚本",
    "status": "completed",
    "status_display": "已完成",
    "parameters": {},
    "group": null,
    "scheduled_time": null,
    "created_by": 1,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00",
    "results_count": 5,
    "report": {"id": 1, "pass_rate": 100.0}
  }
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 任务主键 |
| `name` | string | 任务名称 |
| `script` | int/null | 关联脚本ID |
| `script_name` | string/null | 关联脚本名称 |
| `status` | string | 任务状态: `pending`/`running`/`completed`/`failed`/`cancelled` |
| `status_display` | string | 状态显示名，如"已完成" |
| `parameters` | object | 任务执行参数 |
| `group` | int/null | 分组ID |
| `scheduled_time` | string/null | 计划执行时间 |
| `created_by` | int | 创建人用户ID |
| `created_at` | string | 创建时间(ISO格式) |
| `updated_at` | string | 更新时间(ISO格式) |
| `results_count` | int | 关联的测试结果数量 |
| `report` | object/null | 关联的测试报告，含 `id` 和 `pass_rate` 等 |

---

### 3.2 创建任务

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/tests/tasks/` |
| 函数名 | `task_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L192) |
| 权限 | 需要登录 |
| 说明 | 创建新测试任务 |

**请求体:**
```json
{
  "name": "新任务",
  "script": 1,
  "scripts": [1, 2, 3],
  "status": "pending",
  "parameters": {},
  "group": null,
  "scheduled_time": "2024-01-01T10:00:00",
  "upload_to_management": false,
  "send_email": false
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 任务名称 |
| `script` | int | 否 | 单脚本模式: 关联的脚本ID |
| `scripts` | array | 否 | 多脚本模式: 脚本ID数组 |
| `status` | string | 否 | 初始状态，默认 `pending` |
| `parameters` | object | 否 | 执行参数，默认 `{}` |
| `group` | int/null | 否 | 分组ID |
| `scheduled_time` | string/null | 否 | 计划执行时间(ISO格式) |
| `upload_to_management` | bool | 否 | 是否上传到管理平台，默认false |
| `send_email` | bool | 否 | 是否发送邮件通知，默认false |

**响应状态码:** 201 Created

---

### 3.3 任务详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/tests/tasks/<id>/` |
| 函数名 | `task_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L206) |
| 权限 | 需要登录 |
| 说明 | 获取任务详情，含测试结果和报告 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 任务主键 |

**响应示例:**
```json
{
  "id": 1,
  "name": "测试任务",
  "status": "completed",
  "parameters": {},
  "results": [],
  "report": {
    "id": 1,
    "total_steps": 10,
    "passed_steps": 9,
    "failed_steps": 1,
    "skipped_steps": 0,
    "total_duration": 45.5,
    "pass_rate": 90.0,
    "created_at": "2024-01-01T10:00:00"
  },
  "scripts_passed": 0,
  "scripts_failed": 0
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 任务主键 |
| `name` | string | 任务名称 |
| `status` | string | 任务状态 |
| `parameters` | object | 执行参数 |
| `results` | array | 测试结果列表(每个步骤的执行结果) |
| `report` | object/null | 测试报告对象 |
| `report.id` | int | 报告主键 |
| `report.total_steps` | int | 总步骤数 |
| `report.passed_steps` | int | 通过步骤数 |
| `report.failed_steps` | int | 失败步骤数 |
| `report.skipped_steps` | int | 跳过步骤数 |
| `report.total_duration` | float | 总执行时长(秒) |
| `report.pass_rate` | float | 通过率百分比 |
| `report.created_at` | string | 报告创建时间 |
| `scripts_passed` | int | 多脚本模式: 通过的脚本数 |
| `scripts_failed` | int | 多脚本模式: 失败的脚本数 |

---

### 3.4 更新任务

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/tests/tasks/<id>/` |
| 函数名 | `task_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L206) |
| 权限 | 需要登录 |
| 说明 | 更新任务信息 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 任务主键 |

**请求体:** 同创建任务，所有字段可选，未提供则保持原值

---

### 3.5 删除任务

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/tests/tasks/<id>/` |
| 函数名 | `task_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L206) |
| 权限 | 需要登录 |
| 说明 | 删除任务及其关联的测试结果和报告 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 任务主键 |

---

### 3.6 执行任务

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/tests/tasks/<id>/execute/` |
| 函数名 | `execute_task_view` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L258) |
| 权限 | AllowAny |
| 说明 | 执行测试任务（支持单脚本/多脚本，异步/同步模式） |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 任务主键 |

**请求体:**
```json
{
  "parameters": {},
  "upload_to_management": false,
  "send_email": false
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `parameters` | object | 否 | 运行时参数，覆盖任务预设参数 |
| `upload_to_management` | bool | 否 | 是否上传到管理平台，默认false |
| `send_email` | bool | 否 | 是否发送邮件通知，默认false |

**响应示例:**
```json
{
  "task_id": 1,
  "celery_task_id": "abc-123",
  "status": "started",
  "message": "Test task execution started",
  "script_count": 1
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | int | 任务ID |
| `celery_task_id` | string | Celery异步任务ID |
| `status` | string | 执行状态: `started` |
| `message` | string | 执行消息 |
| `script_count` | int | 要执行的脚本数量 |

**任务状态流转:** `pending` -> `running` -> `completed`/`failed`/`cancelled`

---

### 3.7 停止任务

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/tests/tasks/<id>/stop/` |
| 函数名 | `stop_task` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L321) |
| 权限 | AllowAny |
| 说明 | 停止正在运行的任务 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 任务主键 |

**响应示例:**
```json
{
  "task_id": 1,
  "status": "cancelled",
  "message": "Test task stopped"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | int | 任务ID |
| `status` | string | 停止后的状态: `cancelled` |
| `message` | string | 停止消息 |

---

### 3.8 上传结果到管理平台

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/tests/tasks/<id>/upload/` |
| 函数名 | `trigger_upload` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L170) |
| 权限 | AllowAny |
| 说明 | 将任务执行结果上传到管理平台 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 任务主键 |

**前置条件:** 任务状态必须为 `completed` 或 `failed`

**响应示例:**
```json
{
  "message": "Upload successful",
  "task_id": 1,
  "report_id": "uuid-string"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 上传结果消息 |
| `task_id` | int | 任务ID |
| `report_id` | string | 管理平台生成的报告UUID |

---

### 3.9 结果列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/tests/results/` |
| 函数名 | `result_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L347) |
| 权限 | 需要登录 |
| 说明 | 获取测试结果列表 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `task_id` | int | 否 | 按任务ID筛选 |

---

### 3.10 结果详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/tests/results/<id>/` |
| 函数名 | `result_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L358) |
| 权限 | 需要登录 |
| 说明 | 获取单个测试结果详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 结果主键 |

---

### 3.11 获取结果截图

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/tests/results/<id>/screenshots/` |
| 函数名 | `get_test_screenshots` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L366) |
| 权限 | AllowAny |
| 说明 | 获取测试步骤的截图 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 结果主键 |

**响应示例:**
```json
{
  "result_id": 1,
  "screenshots": [
    {
      "id": 1,
      "step_name": "步骤1",
      "url": "/media/screenshots/xxx.png"
    }
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `result_id` | int | 测试结果ID |
| `screenshots` | array | 截图列表 |
| `screenshots[].id` | int | 截图主键 |
| `screenshots[].step_name` | string | 步骤名称 |
| `screenshots[].url` | string | 截图访问URL |

---

### 3.12 导出测试报告

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/tests/results/<id>/export/` |
| 函数名 | `export_test_report` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/test_manager/views.py#L385) |
| 权限 | AllowAny |
| 说明 | 导出测试报告（JSON格式） |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 任务主键 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `format` | string | 否 | 格式: `json`（默认） |

**响应:** 返回JSON文件或文件下载

---

## 四、自动化测试平台 - Script Editor API (`/api/scripts/`)

### 4.1 脚本列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/` |
| 函数名 | `script_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L25) |
| 权限 | 需要登录 |
| 说明 | 获取所有脚本列表 |

**响应示例:**
```json
[
  {
    "id": 1,
    "name": "测试脚本",
    "code": "test_script_1",
    "description": "描述",
    "status": "published",
    "version": 1,
    "target_url": "https://example.com",
    "group": null,
    "created_by": 1,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00",
    "steps_count": 5
  }
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 脚本主键 |
| `name` | string | 脚本名称 |
| `code` | string | 脚本代码(唯一标识) |
| `description` | string | 脚本描述 |
| `status` | string | 状态: `draft`(草稿)/`published`(已发布)/`archived`(已归档) |
| `version` | int | 当前版本号 |
| `target_url` | string | 目标网址 |
| `group` | int/null | 分组ID |
| `created_by` | int | 创建人用户ID |
| `created_at` | string | 创建时间(ISO格式) |
| `updated_at` | string | 更新时间(ISO格式) |
| `steps_count` | int | 步骤数量 |

---

### 4.2 创建脚本

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/` |
| 函数名 | `script_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L25) |
| 权限 | 需要登录 |
| 说明 | 创建新测试脚本 |

**请求体:**
```json
{
  "name": "新脚本",
  "code": "new_script",
  "description": "描述",
  "status": "draft",
  "target_url": "https://example.com",
  "script_data": {},
  "group": null
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 脚本名称 |
| `code` | string | 是 | 脚本代码(唯一) |
| `description` | string | 否 | 描述，默认空 |
| `status` | string | 否 | 状态，默认 `draft` |
| `target_url` | string | 否 | 目标网址，默认空 |
| `script_data` | object | 否 | 脚本数据JSON，默认 `{}` |
| `group` | int/null | 否 | 分组ID |

**脚本状态:** `draft`（草稿）、`published`（已发布）、`archived`（已归档）

---

### 4.3 脚本详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/<id>/` |
| 函数名 | `script_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L39) |
| 权限 | 需要登录 |
| 说明 | 获取脚本详情，含步骤、元素、动作集合 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 脚本主键 |

---

### 4.4 更新脚本

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/scripts/<id>/` |
| 函数名 | `script_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L39) |
| 权限 | 需要登录 |
| 说明 | 更新脚本信息 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 脚本主键 |

---

### 4.5 删除脚本

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/scripts/<id>/` |
| 函数名 | `script_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L39) |
| 权限 | 需要登录 |
| 说明 | 删除脚本 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 脚本主键 |

---

### 4.6 复制脚本

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/<id>/duplicate/` |
| 函数名 | `duplicate_script` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L58) |
| 权限 | AllowAny |
| 说明 | 复制脚本及其所有步骤 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 脚本主键 |

**响应示例:**
```json
{
  "id": 2,
  "name": "测试脚本 (Copy)",
  "code": "test_script_1_copy_1704110400"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 新复制的脚本主键 |
| `name` | string | 新脚本名称(自动添加Copy后缀) |
| `code` | string | 新脚本代码(自动添加时间戳后缀) |

---

### 4.7 脚本版本列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/<id>/versions/` |
| 函数名 | `script_versions` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L98) |
| 权限 | 需要登录 |
| 说明 | 获取脚本的所有历史版本 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 脚本主键 |

**响应示例:**
```json
[
  {"id": 1, "version": 1, "created_at": "2024-01-01T10:00:00", "script_data": {...}}
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 版本主键 |
| `version` | int | 版本号 |
| `created_at` | string | 版本创建时间 |
| `script_data` | object | 该版本的脚本数据JSON |

---

### 4.8 版本详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/<id>/versions/<version_id>/` |
| 函数名 | `script_version_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L105) |
| 权限 | 需要登录 |
| 说明 | 获取特定版本的脚本数据 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 脚本主键 |
| `version_id` | int | 是 | 版本主键 |

**响应示例:**
```json
{
  "id": 1,
  "version": 1,
  "created_at": "2024-01-01T10:00:00",
  "script_data": {}
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 版本主键 |
| `version` | int | 版本号 |
| `created_at` | string | 版本创建时间 |
| `script_data` | object | 该版本的完整脚本数据JSON |

---

### 4.9 单脚本导出

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/<id>/export/` |
| 函数名 | `export_script_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L567) |
| 权限 | AllowAny |
| 说明 | 导出单个脚本为 JSON 或 Excel |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 脚本主键 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `export_format` | string | 否 | 格式: `json`（默认）或 `excel` |

**响应:** 返回JSON或Excel文件下载

---

### 4.10 批量导出脚本

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/export/` |
| 函数名 | `export_scripts` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L538) |
| 权限 | AllowAny |
| 说明 | 批量导出脚本为 JSON 或 Excel |

**请求体:**
```json
{
  "script_ids": [1, 2, 3],
  "format": "json"
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `script_ids` | array | 是 | 要导出的脚本ID数组 |
| `format` | string | 否 | 导出格式: `json`（默认）或 `excel` |

**响应:** 返回JSON或Excel文件下载

---

### 4.11 导入脚本

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/import/` |
| 函数名 | `import_scripts` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L597) |
| 权限 | AllowAny |
| 说明 | 从 JSON 或 Excel 文件导入脚本 |

**请求参数（Form Data）:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file` | File | 是 | 上传的文件（.json/.xlsx/.xls） |
| `conflict_strategy` | string | 否 | 冲突策略: `skip`/`overwrite`/`rename` |
| `format` | string | 否 | 文件格式: `json`/`excel`/`auto`（默认） |

---

### 4.12 元素定位器列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/elements/` |
| 函数名 | `element_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L112) |
| 权限 | 需要登录 |
| 说明 | 获取所有元素定位器 |

---

### 4.13 创建元素定位器

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/elements/` |
| 函数名 | `element_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L112) |
| 权限 | 需要登录 |
| 说明 | 创建新元素定位器 |

**请求体:**
```json
{
  "name": "登录按钮",
  "code": "login_btn",
  "locator_type": "css",
  "locator_value": "#login-btn",
  "page_url": "https://example.com/login",
  "description": "登录页面按钮",
  "wait_timeout": 10000,
  "wait_state": "visible",
  "is_active": true
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 元素名称 |
| `code` | string | 是 | 元素代码(唯一标识) |
| `locator_type` | string | 是 | 定位类型: `css`/`xpath`/`id`/`name`/`class_name`/`tag_name`/`text`/`role`/`test_id`/`placeholder`/`label` |
| `locator_value` | string | 是 | 定位器值 |
| `page_url` | string | 否 | 所在页面URL |
| `description` | string | 否 | 描述信息 |
| `wait_timeout` | int | 否 | 等待超时时间(毫秒)，默认10000 |
| `wait_state` | string | 否 | 等待状态: `visible`/`hidden`/`attached`/`detached` |
| `is_active` | bool | 否 | 是否启用，默认true |

**支持定位类型:** `css`, `xpath`, `id`, `name`, `class_name`, `tag_name`, `text`, `role`, `test_id`, `placeholder`, `label`

**等待状态:** `visible`, `hidden`, `attached`, `detached`

---

### 4.14 元素定位器详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/elements/<id>/` |
| 函数名 | `element_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L126) |
| 权限 | 需要登录 |
| 说明 | 获取元素定位器详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 元素主键 |

**响应示例:** 同创建元素定位器的请求体结构，额外包含 `id`, `created_at`, `updated_at` 字段

---

### 4.15 更新元素定位器

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/scripts/elements/<id>/` |
| 函数名 | `element_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L126) |
| 权限 | 需要登录 |
| 说明 | 更新元素定位器 |

**请求体:** 同创建元素定位器，所有字段可选

---

### 4.16 删除元素定位器

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/scripts/elements/<id>/` |
| 函数名 | `element_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L126) |
| 权限 | 需要登录 |
| 说明 | 删除元素定位器 |

---

### 4.17 测试步骤列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/steps/` |
| 函数名 | `step_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L144) |
| 权限 | 需要登录 |
| 说明 | 获取所有测试步骤 |

---

### 4.18 创建测试步骤

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/steps/` |
| 函数名 | `step_list` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L144) |
| 权限 | 需要登录 |
| 说明 | 创建新测试步骤 |

**请求体:**
```json
{
  "script": 1,
  "name": "点击登录",
  "order": 0,
  "action_type": "click",
  "element": 1,
  "action_set_ref": null,
  "action_set_params": {},
  "action_value": "",
  "action_config": {},
  "description": "点击登录按钮",
  "is_enabled": true,
  "continue_on_failure": false,
  "retry_count": 0,
  "retry_interval": 1000
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `script` | int | 是 | 所属脚本ID |
| `name` | string | 是 | 步骤名称 |
| `order` | int | 否 | 排序号，默认0 |
| `action_type` | string | 是 | 操作类型: `navigate`/`click`/`fill`/`select`/`random_select`/`random_number`/`check`/`uncheck`/`wait`/`wait_for_selector`/`screenshot`/`scroll`/`hover`/`focus`/`press`/`upload`/`assert_text`/`assert_visible`/`assert_value`/`action_set`/`custom` |
| `element` | int/null | 否 | 关联的元素定位器ID |
| `action_set_ref` | int/null | 否 | 关联的动作集合ID |
| `action_set_params` | object | 否 | 动作集合参数 |
| `action_value` | string | 否 | 操作值(如fill的文本内容) |
| `action_config` | object | 否 | 操作配置JSON |
| `description` | string | 否 | 步骤描述 |
| `is_enabled` | bool | 否 | 是否启用，默认true |
| `continue_on_failure` | bool | 否 | 失败后是否继续执行，默认false |
| `retry_count` | int | 否 | 重试次数，默认0 |
| `retry_interval` | int | 否 | 重试间隔(毫秒)，默认1000 |

**支持操作类型:** `navigate`, `click`, `fill`, `select`, `random_select`, `random_number`, `check`, `uncheck`, `wait`, `wait_for_selector`, `screenshot`, `scroll`, `hover`, `focus`, `press`, `upload`, `assert_text`, `assert_visible`, `assert_value`, `action_set`, `custom`

---

### 4.19 测试步骤详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/steps/<id>/` |
| 函数名 | `step_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L158) |
| 权限 | 需要登录 |
| 说明 | 获取步骤详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 步骤主键 |

---

### 4.20 更新测试步骤

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/scripts/steps/<id>/` |
| 函数名 | `step_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L158) |
| 权限 | 需要登录 |
| 说明 | 更新测试步骤 |

**请求体:** 同创建测试步骤，所有字段可选

---

### 4.21 删除测试步骤

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/scripts/steps/<id>/` |
| 函数名 | `step_detail` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L158) |
| 权限 | 需要登录 |
| 说明 | 删除测试步骤 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 步骤主键 |

---

### 4.22 可视化编辑器

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/visual-editor/` |
| 函数名 | `visual_editor` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L177) |
| 权限 | AllowAny |
| 说明 | 获取可用的操作类型和定位类型列表 |

**响应示例:**
```json
{
  "action_types": [{"value": "click", "label": "点击"}, ...],
  "locator_types": [{"value": "css", "label": "CSS选择器"}, ...]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `action_types` | array | 操作类型列表 |
| `action_types[].value` | string | 操作类型值 |
| `action_types[].label` | string | 操作类型显示名称 |
| `locator_types` | array | 定位类型列表 |
| `locator_types[].value` | string | 定位类型值 |
| `locator_types[].label` | string | 定位类型显示名称 |

---

### 4.23 通过可视化编辑器创建脚本

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/visual-editor/` |
| 函数名 | `visual_editor` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L177) |
| 权限 | AllowAny |
| 说明 | 通过可视化数据创建脚本 |

**请求体:**
```json
{
  "name": "新脚本",
  "code": "visual_script_1",
  "description": "描述",
  "target_url": "https://example.com",
  "steps": [
    {"name": "步骤1", "action_type": "navigate", "value": "https://example.com", "config": {}, "description": "", "is_enabled": true, "continue_on_failure": false, "retry_count": 0, "retry_interval": 1000}
  ],
  "parameters": []
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 脚本名称 |
| `code` | string | 是 | 脚本代码 |
| `description` | string | 否 | 描述 |
| `target_url` | string | 否 | 目标网址 |
| `steps` | array | 是 | 步骤数组 |
| `steps[].name` | string | 是 | 步骤名称 |
| `steps[].action_type` | string | 是 | 操作类型 |
| `steps[].value` | string | 否 | 操作值 |
| `steps[].config` | object | 否 | 配置JSON |
| `steps[].description` | string | 否 | 步骤描述 |
| `steps[].is_enabled` | bool | 否 | 是否启用 |
| `steps[].continue_on_failure` | bool | 否 | 失败后继续 |
| `steps[].retry_count` | int | 否 | 重试次数 |
| `steps[].retry_interval` | int | 否 | 重试间隔(毫秒) |
| `parameters` | array | 否 | 参数定义数组 |

**响应状态码:** 201 Created，返回创建的脚本数据

---

### 4.24 验证脚本数据

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/validate-script/` |
| 函数名 | `validate_script` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L239) |
| 权限 | AllowAny |
| 说明 | 验证脚本数据是否符合 JSON Schema |

**请求体:** 脚本数据 JSON

**响应示例:**
```json
{
  "valid": false,
  "errors": ["'name' is a required property"]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `valid` | bool | 验证是否通过 |
| `errors` | array | 错误信息列表(验证失败时) |

---

### 4.25 全局配置获取

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/global-config/` |
| 函数名 | `global_config` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L522) |
| 权限 | 需要登录 |
| 说明 | 获取全局配置（浏览器、超时、邮件等） |

**响应示例:**
```json
{
  "browser": {"type": "chromium", "headless": false},
  "timeout": {"navigation": 30000, "action": 10000},
  "email": {"smtp_server": "", "smtp_port": 25, "username": "", "password": ""}
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `browser` | object | 浏览器配置 |
| `browser.type` | string | 浏览器类型: `chromium`/`firefox`/`webkit` |
| `browser.headless` | bool | 是否无头模式 |
| `timeout` | object | 超时配置 |
| `timeout.navigation` | int | 导航超时(毫秒) |
| `timeout.action` | int | 操作超时(毫秒) |
| `email` | object | 邮件配置 |
| `email.smtp_server` | string | SMTP服务器地址 |
| `email.smtp_port` | int | SMTP端口 |
| `email.username` | string | SMTP用户名 |
| `email.password` | string | SMTP密码 |

---

### 4.26 更新全局配置

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/scripts/global-config/` |
| 函数名 | `global_config` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L522) |
| 权限 | 需要登录 |
| 说明 | 更新全局配置 |

**请求体:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `browser` | object | 否 | 浏览器配置 |
| `timeout` | object | 否 | 超时配置 |
| `email` | object | 否 | 邮件配置 |

---

### 4.27 启动录制

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/recording/start/` |
| 函数名 | `recording_start` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L250) |
| 权限 | AllowAny |
| 说明 | 启动浏览器录制会话 |

**请求体:**
```json
{
  "target_url": "https://example.com",
  "viewport_width": 1920,
  "viewport_height": 1080
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `target_url` | string | 是 | 目标网址 |
| `viewport_width` | int | 否 | 视口宽度，默认1920 |
| `viewport_height` | int | 否 | 视口高度，默认1080 |

**响应示例:**
```json
{
  "session_id": "uuid-string",
  "status": "starting",
  "target_url": "https://example.com"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 录制会话ID(UUID) |
| `status` | string | 状态: `starting` |
| `target_url` | string | 目标网址 |

---

### 4.28 获取录制操作

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/recording/<session_id>/actions/` |
| 函数名 | `recording_actions` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L291) |
| 权限 | AllowAny |
| 说明 | 获取已录制的操作列表 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `session_id` | string | 是 | 录制会话ID |

**响应示例:**
```json
{
  "session_id": "uuid",
  "status": "recording",
  "actions": [
    {"action_type": "navigate", "value": "https://example.com", "locators": [], "description": "导航", "timestamp": "..."}
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 录制会话ID |
| `status` | string | 状态: `recording` |
| `actions` | array | 已录制操作列表 |
| `actions[].action_type` | string | 操作类型 |
| `actions[].value` | string | 操作值 |
| `actions[].locators` | array | 定位器列表 |
| `actions[].description` | string | 操作描述 |
| `actions[].timestamp` | string | 操作时间戳 |

---

### 4.29 停止录制

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/recording/<session_id>/stop/` |
| 函数名 | `recording_stop` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L303) |
| 权限 | AllowAny |
| 说明 | 停止录制并返回所有操作 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `session_id` | string | 是 | 录制会话ID |

**响应示例:**
```json
{
  "session_id": "uuid",
  "status": "stopped",
  "action_count": 5,
  "actions": [
    {"action_type": "navigate", "value": "https://example.com", "locators": [], "description": "导航", "timestamp": "..."}
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 录制会话ID |
| `status` | string | 状态: `stopped` |
| `action_count` | int | 录制操作数量 |
| `actions` | array | 录制操作列表(同获取录制操作) |

---

### 4.30 转换录制为脚本/动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/recording/<session_id>/convert/` |
| 函数名 | `recording_convert` |
| 文件路径 | [views.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views.py#L320) |
| 权限 | AllowAny |
| 说明 | 将录制操作转换为脚本或动作集合 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `session_id` | string | 是 | 录制会话ID |

**请求体:**
```json
{
  "mode": "script",
  "name": "录制脚本",
  "code": "rec_script_1",
  "target_url": "https://example.com",
  "group_code": "",
  "category": "general"
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 是 | 转换模式: `script`(脚本) 或 `action_set`(动作集合) |
| `name` | string | 是 | 名称 |
| `code` | string | 是 | 代码 |
| `target_url` | string | 否 | 目标网址 |
| `group_code` | string | 否 | 分组代码 |
| `category` | string | 否 | 分类(仅action_set模式): `input`/`navigation`/`form`/`validation`/`general` |

**转换模式:** `script`（脚本）或 `action_set`（动作集合）

---

### 4.31 动作集合列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/` |
| 函数名 | `action_set_list` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L15) |
| 权限 | AllowAny |
| 说明 | 获取动作集合列表，可按分类筛选 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `category` | string | 否 | 分类: `input`, `navigation`, `form`, `validation`, `general` |

**响应示例:**
```json
[
  {
    "id": 1,
    "name": "登录操作",
    "code": "login_action_set",
    "description": "描述",
    "category": "form",
    "is_builtin": false,
    "is_active": true,
    "steps_count": 3,
    "parameters_count": 2
  }
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 动作集合主键 |
| `name` | string | 动作集合名称 |
| `code` | string | 动作集合代码 |
| `description` | string | 描述 |
| `category` | string | 分类 |
| `is_builtin` | bool | 是否内置 |
| `is_active` | bool | 是否启用 |
| `steps_count` | int | 步骤数量 |
| `parameters_count` | int | 参数数量 |

---

### 4.32 创建动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/action-sets/` |
| 函数名 | `action_set_list` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L15) |
| 权限 | AllowAny |
| 说明 | 创建新动作集合 |

**请求体:**
```json
{
  "name": "登录操作",
  "code": "login_action_set",
  "description": "描述",
  "category": "form",
  "group": null,
  "is_builtin": false,
  "is_active": true,
  "steps": [],
  "parameters": []
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 动作集合名称 |
| `code` | string | 是 | 动作集合代码(唯一) |
| `description` | string | 否 | 描述 |
| `category` | string | 是 | 分类: `input`/`navigation`/`form`/`validation`/`general` |
| `group` | int/null | 否 | 分组ID |
| `is_builtin` | bool | 否 | 是否内置，默认false |
| `is_active` | bool | 否 | 是否启用，默认true |
| `steps` | array | 否 | 步骤数组 |
| `parameters` | array | 否 | 参数定义数组 |

---

### 4.33 动作集合详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/<id>/` |
| 函数名 | `action_set_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L151) |
| 权限 | AllowAny |
| 说明 | 获取动作集合详情，含步骤和参数 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 动作集合主键 |

**响应示例:** 同创建动作集合的请求体结构，额外包含 `id`, `created_at`, `updated_at`, `steps`(展开的步骤列表), `parameters`(参数定义列表) 字段

---

### 4.34 更新动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/scripts/action-sets/<id>/` |
| 函数名 | `action_set_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L151) |
| 权限 | AllowAny |
| 说明 | 更新动作集合（内置的不可修改） |

**请求体:** 同创建动作集合，所有字段可选。注意: 内置动作集合不可修改

---

### 4.35 删除动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/scripts/action-sets/<id>/` |
| 函数名 | `action_set_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L151) |
| 权限 | AllowAny |
| 说明 | 删除动作集合（内置的不可删除） |

**注意:** 内置动作集合不可删除

---

### 4.36 导出动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/<id>/export/` |
| 函数名 | `action_set_export` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L33) |
| 权限 | AllowAny |
| 说明 | 导出单个动作集合的完整数据 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 动作集合主键 |

**响应:** 返回动作集合的完整JSON数据(含步骤和参数)

---

### 4.37 展开动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/action-sets/<id>/expand/` |
| 函数名 | `action_set_expand` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L174) |
| 权限 | AllowAny |
| 说明 | 将动作集合展开为 Playwright 步骤列表 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 动作集合主键 |

**请求体:**
```json
{
  "parameters": {"param1": "value1"}
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `parameters` | object | 否 | 参数值映射，用于替换动作集合中的参数引用 |

**响应示例:**
```json
{
  "action_set": {"id": 1, "name": "登录操作", "code": "login_action_set"},
  "steps": [{"step_name": "步骤1", "action_type": "click", ...}],
  "parameters_used": {"param1": "value1"}
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `action_set` | object | 动作集合基本信息 |
| `action_set.id` | int | 动作集合主键 |
| `action_set.name` | string | 动作集合名称 |
| `action_set.code` | string | 动作集合代码 |
| `steps` | array | 展开后的Playwright步骤列表 |
| `parameters_used` | object | 实际使用的参数值 |

---

### 4.38 批量导出动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/action-sets/export/` |
| 函数名 | `action_set_batch_export` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L41) |
| 权限 | AllowAny |
| 说明 | 批量导出动作集合 |

**请求体:**
```json
{
  "ids": [1, 2, 3]
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ids` | array | 是 | 要导出的动作集合ID数组 |

**响应:** 返回动作集合数组的JSON数据

---

### 4.39 导入动作集合

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/action-sets/import/` |
| 函数名 | `action_set_import` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L54) |
| 权限 | AllowAny |
| 说明 | 从 JSON 导入动作集合 |

**请求体:** 动作集合数据数组（自动跳过已存在的 code）

**响应示例:**
```json
{
  "imported": 3,
  "skipped": 1,
  "message": "成功导入 3 个动作集合，跳过 1 个已存在的"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `imported` | int | 成功导入的数量 |
| `skipped` | int | 跳过的数量(code已存在) |
| `message` | string | 导入结果描述 |

---

### 4.40 获取分类列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/categories/` |
| 函数名 | `action_set_categories` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L188) |
| 权限 | AllowAny |
| 说明 | 获取所有已使用的动作集合分类 |

**响应示例:** `["form", "navigation", "general"]`

**响应类型:** string数组，包含所有已使用的分类值

---

### 4.41 动作集合步骤列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/<action_set_id>/steps/` |
| 函数名 | `action_set_step_list` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L195) |
| 权限 | AllowAny |
| 说明 | 获取动作集合的所有步骤 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `action_set_id` | int | 是 | 动作集合主键 |

---

### 4.42 创建动作集合步骤

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/action-sets/<action_set_id>/steps/` |
| 函数名 | `action_set_step_list` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L195) |
| 权限 | AllowAny |
| 说明 | 为动作集合添加步骤 |

**请求体:**
```json
{
  "name": "步骤名",
  "order": 0,
  "action_type": "click",
  "locator_type": "css",
  "locator_value": "#btn",
  "locator_description": "按钮",
  "action_value": "",
  "action_value_type": "static",
  "parameter_name": "",
  "action_config": {},
  "wait_timeout": 10000,
  "continue_on_failure": false,
  "retry_count": 0,
  "retry_interval": 1000,
  "random_options": [],
  "select_mode": "dropdown",
  "random_min": null,
  "random_max": null,
  "force_click": false,
  "description": "",
  "is_enabled": true
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 步骤名称 |
| `order` | int | 否 | 排序号，默认0 |
| `action_type` | string | 是 | 操作类型 |
| `locator_type` | string | 否 | 定位类型 |
| `locator_value` | string | 否 | 定位器值 |
| `locator_description` | string | 否 | 定位器描述 |
| `action_value` | string | 否 | 操作值 |
| `action_value_type` | string | 否 | 值类型: `static`(静态值)/`parameter`(参数引用)/`expression`(表达式) |
| `parameter_name` | string | 否 | 参数名称(当action_value_type为parameter时) |
| `action_config` | object | 否 | 操作配置JSON |
| `wait_timeout` | int | 否 | 等待超时(毫秒)，默认10000 |
| `continue_on_failure` | bool | 否 | 失败后继续，默认false |
| `retry_count` | int | 否 | 重试次数，默认0 |
| `retry_interval` | int | 否 | 重试间隔(毫秒)，默认1000 |
| `random_options` | array | 否 | 随机选项列表(用于random_select) |
| `select_mode` | string | 否 | 选择模式: `dropdown`(下拉框)/`click`(点击选择) |
| `random_min` | int/null | 否 | 随机数最小值 |
| `random_max` | int/null | 否 | 随机数最大值 |
| `force_click` | bool | 否 | 强制点击，默认false |
| `description` | string | 否 | 步骤描述 |
| `is_enabled` | bool | 否 | 是否启用，默认true |

**值类型:** `static`（静态值）、`parameter`（参数引用）、`expression`（表达式）

**选择模式:** `dropdown`（下拉框）、`click`（点击选择）

---

### 4.43 动作集合步骤详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/steps/<id>/` |
| 函数名 | `action_set_step_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L214) |
| 权限 | AllowAny |
| 说明 | 获取步骤详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 步骤主键 |

**响应示例:** 同创建动作集合步骤的请求体结构

---

### 4.44 更新动作集合步骤

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/scripts/action-sets/steps/<id>/` |
| 函数名 | `action_set_step_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L214) |
| 权限 | AllowAny |
| 说明 | 更新步骤 |

**请求体:** 同创建动作集合步骤，所有字段可选

---

### 4.45 删除动作集合步骤

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/scripts/action-sets/steps/<id>/` |
| 函数名 | `action_set_step_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L214) |
| 权限 | AllowAny |
| 说明 | 删除步骤 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 步骤主键 |

---

### 4.46 步骤重排序

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/action-sets/<action_set_id>/steps/reorder/` |
| 函数名 | `action_set_step_reorder` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L237) |
| 权限 | AllowAny |
| 说明 | 批量更新步骤顺序 |

**请求体:**
```json
{
  "steps": [
    {"id": 1, "order": 0},
    {"id": 2, "order": 1},
    {"id": 3, "order": 2}
  ]
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `steps` | array | 是 | 步骤排序数组 |
| `steps[].id` | int | 是 | 步骤ID |
| `steps[].order` | int | 是 | 新排序号 |

**响应示例:**
```json
{"message": "步骤排序已更新"}
```

---

### 4.47 动作集合参数列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/<action_set_id>/parameters/` |
| 函数名 | `action_set_parameter_list` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L253) |
| 权限 | AllowAny |
| 说明 | 获取动作集合的所有参数定义 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `action_set_id` | int | 是 | 动作集合主键 |

**响应示例:**
```json
[
  {"id": 1, "name": "用户名", "code": "username", "description": "登录用户名", "default_value": "", "is_required": true, "order": 0}
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 参数主键 |
| `name` | string | 参数名称 |
| `code` | string | 参数代码 |
| `description` | string | 参数描述 |
| `default_value` | string | 默认值 |
| `is_required` | bool | 是否必填 |
| `order` | int | 排序号 |

---

### 4.48 创建动作集合参数

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/action-sets/<action_set_id>/parameters/` |
| 函数名 | `action_set_parameter_list` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L253) |
| 权限 | AllowAny |
| 说明 | 为动作集合添加参数定义 |

**请求体:**
```json
{
  "name": "用户名",
  "code": "username",
  "description": "登录用户名",
  "default_value": "",
  "is_required": true,
  "order": 0
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 参数名称 |
| `code` | string | 是 | 参数代码(同一动作集合下唯一) |
| `description` | string | 否 | 参数描述 |
| `default_value` | string | 否 | 默认值 |
| `is_required` | bool | 否 | 是否必填，默认false |
| `order` | int | 否 | 排序号，默认0 |

---

### 4.49 动作集合参数详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/action-sets/parameters/<id>/` |
| 函数名 | `action_set_parameter_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L272) |
| 权限 | AllowAny |
| 说明 | 获取参数详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | int | 是 | 参数主键 |

**响应示例:** 同创建动作集合参数的请求体结构

---

### 4.50 更新动作集合参数

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/scripts/action-sets/parameters/<id>/` |
| 函数名 | `action_set_parameter_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L272) |
| 权限 | AllowAny |
| 说明 | 更新参数定义 |

**请求体:** 同创建动作集合参数，所有字段可选

---

### 4.51 删除动作集合参数

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/scripts/action-sets/parameters/<id>/` |
| 函数名 | `action_set_parameter_detail` |
| 文件路径 | [views_actionset.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_actionset.py#L272) |
| 权限 | AllowAny |
| 说明 | 删除参数定义 |

---

### 4.52 市场文件列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/marketplace/items/` |
| 函数名 | `marketplace_list_items` |
| 文件路径 | [views_marketplace.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_marketplace.py#L76) |
| 权限 | AllowAny |
| 说明 | 列出集合市场文件（含文件夹），自动附加预览元数据 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | string | 否 | 目录路径 |

**响应示例:**
```json
[
  {"name": "文件夹1", "is_folder": true, "path": "folder1"},
  {"name": "登录脚本", "is_folder": false, "path": "folder1/login.json", "metadata": {"category": "form", "description": "登录操作"}}
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 文件/文件夹名称 |
| `is_folder` | bool | 是否为文件夹 |
| `path` | string | 相对路径 |
| `metadata` | object/null | 文件元数据预览(仅文件) |
| `metadata.category` | string | 分类 |
| `metadata.description` | string | 描述 |

---

### 4.53 市场搜索

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/marketplace/search/` |
| 函数名 | `marketplace_search_items` |
| 文件路径 | [views_marketplace.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_marketplace.py#L89) |
| 权限 | AllowAny |
| 说明 | 按关键字搜索市场中的文件 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `keyword` | string | 是 | 搜索关键字 |

**响应示例:** 同市场文件列表结构

---

### 4.54 创建文件夹

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/marketplace/folder/` |
| 函数名 | `marketplace_create_folder` |
| 文件路径 | [views_marketplace.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_marketplace.py#L111) |
| 权限 | AllowAny |
| 说明 | 在市场中新建文件夹 |

**请求体:**
```json
{
  "name": "新文件夹",
  "path": ""
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 文件夹名称 |
| `path` | string | 否 | 父目录路径，默认根目录 |

---

### 4.55 下载文件

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/marketplace/download/` |
| 函数名 | `marketplace_download_file` |
| 文件路径 | [views_marketplace.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_marketplace.py#L127) |
| 权限 | AllowAny |
| 说明 | 获取市场文件内容预览数据 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 是 | 文件名 |
| `path` | string | 否 | 文件路径 |

**响应:** 返回文件JSON内容

---

### 4.56 预览文件

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/scripts/marketplace/preview/` |
| 函数名 | `marketplace_preview_file` |
| 文件路径 | [views_marketplace.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_marketplace.py#L141) |
| 权限 | AllowAny |
| 说明 | 预览市场文件 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 是 | 文件名 |
| `path` | string | 否 | 文件路径 |

**响应:** 返回文件JSON内容(同下载文件)

---

### 4.57 上传文件

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/scripts/marketplace/upload/` |
| 函数名 | `marketplace_upload_file` |
| 文件路径 | [views_marketplace.py](file:///c:/Users/ittest/Desktop/new-python/script_editor/views_marketplace.py#L155) |
| 权限 | AllowAny |
| 说明 | 上传 JSON 文件到市场 |

**请求体:**
```json
{
  "filename": "test.json",
  "path": "",
  "content": {"name": "测试", "description": "描述"}
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `filename` | string | 是 | 文件名(含.json扩展名) |
| `path` | string | 否 | 目标目录路径，默认根目录 |
| `content` | object | 是 | 文件JSON内容 |

**响应示例:**
```json
{"message": "文件已上传", "path": "test.json"}
```

---

## 五、自动化管理平台 API (`http://localhost:8001`)

### 5.1 文件/文件夹列表

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/items` |
| 函数名 | `list_items` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L97) |
| 权限 | AllowAny |
| 说明 | 列出指定目录下的文件和文件夹 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | string | 否 | 相对路径，默认为空表示根目录 |

**响应示例:**
```json
[
  {"name": "folder1", "size": 0, "is_folder": true, "modified_time": "2024-01-01T10:00:00"},
  {"name": "test.json", "size": 1024, "is_folder": false, "modified_time": "2024-01-01T10:00:00"}
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 文件/文件夹名称 |
| `size` | int | 文件大小(字节)，文件夹为0 |
| `is_folder` | bool | 是否为文件夹 |
| `modified_time` | string | 修改时间(ISO格式) |

---

### 5.2 创建文件夹

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/folder` |
| 函数名 | `create_folder` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L114) |
| 权限 | AllowAny |
| 说明 | 在指定目录创建新文件夹 |

**请求体:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 文件夹名称 |
| `path` | string | 否 | 父目录路径，默认根目录 |

**响应示例:**
```json
{"message": "文件夹已创建", "path": "folder1"}
```

---

### 5.3 删除文件/文件夹

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/items/<name>` |
| 函数名 | `delete_item` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L136) |
| 权限 | AllowAny |
| 说明 | 删除指定文件或文件夹 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 是 | 文件/文件夹名称（URL编码） |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | string | 否 | 所在目录路径 |

**响应示例:**
```json
{"message": "已删除"}
```

---

### 5.4 重命名文件/文件夹

| 属性 | 值 |
|------|------|
| 接口路径 | `PUT /api/items/<name>/rename` |
| 函数名 | `rename_item` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L154) |
| 权限 | AllowAny |
| 说明 | 重命名文件或文件夹 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 是 | 原名称（URL编码） |

**请求体:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `new_name` | string | 是 | 新名称 |
| `path` | string | 否 | 所在目录路径 |

**响应示例:**
```json
{"message": "已重命名", "old_name": "old.json", "new_name": "new.json"}
```

---

### 5.5 上传文件

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/upload` |
| 函数名 | `upload_file` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L178) |
| 权限 | AllowAny |
| 说明 | 上传 JSON 文件（同名文件自动加后缀） |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file` | File | 是 | JSON 文件 |
| `path` | string | 否 | 目标目录路径 |

**响应示例:**
```json
{"message": "文件已上传", "filename": "test.json"}
```

---

### 5.6 下载文件

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/items/<name>/download` |
| 函数名 | `download_item` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L206) |
| 权限 | AllowAny |
| 说明 | 下载 JSON 文件 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 是 | 文件名（URL编码） |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | string | 否 | 所在目录路径 |

**响应:** 返回文件下载流

---

### 5.7 预览文件

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/items/<name>/preview` |
| 函数名 | `preview_item` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L218) |
| 权限 | AllowAny |
| 说明 | 获取 JSON 文件内容 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 是 | 文件名（URL编码） |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | string | 否 | 所在目录路径 |

**响应:** 返回文件JSON内容

---

### 5.8 搜索文件

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/search` |
| 函数名 | `search_items` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L235) |
| 权限 | AllowAny |
| 说明 | 递归搜索所有目录下的文件 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `keyword` | string | 是 | 搜索关键字（匹配文件名） |

**响应示例:**
```json
[
  {"name": "test.json", "path": "folder1/test.json", "size": 1024}
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 文件名 |
| `path` | string | 完整路径 |
| `size` | int | 文件大小(字节) |

---

### 5.9 上传脚本结果

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/script-results/upload` |
| 函数名 | `upload_script_result` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L270) |
| 权限 | AllowAny |
| 说明 | 接收测试平台上传的执行结果，保存到数据库 |

**请求体:**
```json
{
  "task_id": 1,
  "task_name": "测试任务",
  "script_name": "测试脚本",
  "started_at": "2024-01-01T10:00:00",
  "finished_at": "2024-01-01T10:01:00",
  "status": "completed",
  "step_results": [
    {
      "step_name": "步骤1",
      "step_order": 0,
      "action_type": "click",
      "status": "passed",
      "duration": 1.5,
      "error": null,
      "error_stack": null,
      "screenshot": null,
      "action_values": {}
    }
  ],
  "parameters": {},
  "total_steps": 5,
  "passed_steps": 5,
  "failed_steps": 0,
  "skipped_steps": 0,
  "total_duration": 10.5,
  "pass_rate": 100.0,
  "username": "admin",
  "script_count": null
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | int | 是 | 测试平台任务ID |
| `task_name` | string | 是 | 任务名称 |
| `script_name` | string | 是 | 脚本名称 |
| `started_at` | string | 是 | 开始执行时间(ISO格式) |
| `finished_at` | string | 是 | 完成时间(ISO格式) |
| `status` | string | 是 | 执行状态: `completed`/`failed` |
| `step_results` | array | 是 | 步骤执行结果列表 |
| `step_results[].step_name` | string | 是 | 步骤名称 |
| `step_results[].step_order` | int | 是 | 步骤序号 |
| `step_results[].action_type` | string | 是 | 操作类型 |
| `step_results[].status` | string | 是 | 步骤状态: `passed`/`failed`/`skipped` |
| `step_results[].duration` | float | 是 | 执行时长(秒) |
| `step_results[].error` | string/null | 否 | 错误信息 |
| `step_results[].error_stack` | string/null | 否 | 错误堆栈 |
| `step_results[].screenshot` | string/null | 否 | 截图Base64或URL |
| `step_results[].action_values` | object | 否 | 操作相关值 |
| `parameters` | object | 否 | 执行参数 |
| `total_steps` | int | 是 | 总步骤数 |
| `passed_steps` | int | 是 | 通过步骤数 |
| `failed_steps` | int | 是 | 失败步骤数 |
| `skipped_steps` | int | 是 | 跳过步骤数 |
| `total_duration` | float | 是 | 总执行时长(秒) |
| `pass_rate` | float | 是 | 通过率百分比 |
| `username` | string | 否 | 执行用户名 |
| `script_count` | int/null | 否 | 多脚本模式的脚本数量 |

**响应示例:**
```json
{
  "message": "脚本执行结果已保存",
  "id": "uuid-string"
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 保存结果消息 |
| `id` | string | 新创建的记录UUID |

---

### 5.10 脚本结果列表（分页）

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/script-results` |
| 函数名 | `list_script_results` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L317) |
| 权限 | AllowAny |
| 说明 | 分页查询脚本执行结果，支持多条件筛选 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `page` | int | 否 | 页码，默认 1 |
| `page_size` | int | 否 | 每页条数，默认 20，最大 100 |
| `status` | string | 否 | 状态筛选: `completed`, `failed` |
| `keyword` | string | 否 | 关键字搜索（任务名/脚本名） |
| `username` | string | 否 | 用户名筛选（多个用逗号分隔） |
| `start_date` | string | 否 | 起始日期（YYYY-MM-DD） |
| `end_date` | string | 否 | 结束日期（YYYY-MM-DD） |

**响应示例:**
```json
{
  "data": [],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | array | 结果记录列表 |
| `total` | int | 总记录数 |
| `page` | int | 当前页码 |
| `page_size` | int | 每页条数 |
| `total_pages` | int | 总页数 |

---

### 5.11 脚本结果详情

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/script-results/<result_id>` |
| 函数名 | `get_script_result` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L469) |
| 权限 | AllowAny |
| 说明 | 获取单条脚本执行结果详情 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `result_id` | string | 是 | 结果记录 UUID |

**响应示例:** 同上传脚本结果的请求体结构，额外包含 `id`, `created_at` 字段

---

### 5.12 删除脚本结果

| 属性 | 值 |
|------|------|
| 接口路径 | `DELETE /api/script-results/<result_id>` |
| 函数名 | `delete_script_result` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L478) |
| 权限 | AllowAny |
| 说明 | 删除结果记录 |

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `result_id` | string | 是 | 结果记录 UUID |

**响应示例:**
```json
{"message": "结果已删除"}
```

---

### 5.13 统计数据

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/script-results/stats` |
| 函数名 | `get_script_results_stats` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L365) |
| 权限 | AllowAny |
| 说明 | 获取执行结果统计（成功率、失败率、平均耗时） |

**响应示例:**
```json
{
  "total": 100,
  "success_rate": 85.0,
  "fail_rate": 15.0,
  "avg_duration": 12.5
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | int | 总记录数 |
| `success_rate` | float | 成功率百分比 |
| `fail_rate` | float | 失败率百分比 |
| `avg_duration` | float | 平均执行时长(秒) |

---

### 5.14 趋势数据

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/script-results/trend` |
| 函数名 | `get_script_results_trend` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L391) |
| 权限 | AllowAny |
| 说明 | 获取按日期汇总的执行趋势数据 |

**响应示例:**
```json
[
  {
    "date": "2024-01-01",
    "total": 10,
    "success": 8,
    "fail": 2,
    "avg_duration": 12.5
  }
]
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期(YYYY-MM-DD) |
| `total` | int | 当日执行总数 |
| `success` | int | 当日成功数 |
| `fail` | int | 当日失败数 |
| `avg_duration` | float | 当日平均执行时长(秒) |

---

### 5.15 异常分析

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/script-results/anomalies` |
| 函数名 | `get_script_results_anomalies` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L427) |
| 权限 | AllowAny |
| 说明 | 获取失败结果的错误类型分布和高频失败步骤 |

**响应示例:**
```json
{
  "error_type_distribution": [
    {"error_type": "TimeoutError", "count": 5, "type": "TimeoutError"}
  ],
  "error_types": [
    {"error_type": "TimeoutError", "count": 5, "type": "TimeoutError"}
  ],
  "top_failing_steps": [
    {
      "step_name": "点击登录",
      "fail_count": 3,
      "error_types": {"TimeoutError: 30000ms": 3}
    }
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `error_type_distribution` | array | 错误类型分布列表 |
| `error_type_distribution[].error_type` | string | 错误类型 |
| `error_type_distribution[].count` | int | 出现次数 |
| `error_type_distribution[].type` | string | 错误类型(重复字段) |
| `error_types` | array | 错误类型列表(同上) |
| `top_failing_steps` | array | 高频失败步骤列表 |
| `top_failing_steps[].step_name` | string | 步骤名称 |
| `top_failing_steps[].fail_count` | int | 失败次数 |
| `top_failing_steps[].error_types` | object | 错误类型分布映射 |

---

### 5.16 获取配置

| 属性 | 值 |
|------|------|
| 接口路径 | `GET /api/config` |
| 函数名 | `get_configuration` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L493) |
| 权限 | AllowAny |
| 说明 | 获取平台配置（管理平台URL、用户名等） |

**响应示例:**
```json
{
  "management_platform_url": "http://localhost:8001/api/script-results/upload",
  "username": ""
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `management_platform_url` | string | 管理平台上传接口URL |
| `username` | string | 用户名 |

---

### 5.17 更新配置

| 属性 | 值 |
|------|------|
| 接口路径 | `POST /api/config` |
| 函数名 | `update_configuration` |
| 文件路径 | [main.py](file:///c:/Users/ittest/Desktop/new-python/automated_management_platform/backend/main.py#L509) |
| 权限 | AllowAny |
| 说明 | 更新平台配置 |

**请求体:**
```json
{
  "management_platform_url": "http://localhost:8001/api/script-results/upload",
  "username": "admin"
}
```

**请求体字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `management_platform_url` | string | 否 | 管理平台上传接口URL |
| `username` | string | 否 | 用户名 |

**响应示例:**
```json
{"message": "配置已更新"}
```

---

## 六、接口索引汇总

### 自动化测试平台 (Django, 端口 8000)

| 序号 | 方法 | 接口路径 | 说明 |
|------|------|---------|------|
| 1 | GET | `/api/core/health/` | 健康检查 |
| 2 | GET | `/api/core/dashboard/` | 仪表盘统计 |
| 3 | GET | `/api/core/groups/` | 分组列表 |
| 4 | POST | `/api/core/groups/` | 创建分组 |
| 5 | GET | `/api/core/groups/<id>/` | 分组详情 |
| 6 | PUT | `/api/core/groups/<id>/` | 更新分组 |
| 7 | DELETE | `/api/core/groups/<id>/` | 删除分组 |
| 8 | DELETE | `/api/core/scripts/clear-screenshots/` | 清理截图 |
| 9 | DELETE | `/api/core/scripts/clear-task-results/` | 清理结果 |
| 10 | GET | `/api/core/error-config/` | 错误配置列表 |
| 11 | POST | `/api/core/error-config/` | 新增错误配置 |
| 12 | PUT | `/api/core/error-config/<id>/` | 更新错误配置 |
| 13 | DELETE | `/api/core/error-config/<id>/delete/` | 删除错误配置 |
| 14 | GET | `/api/products/` | 产品类型列表 |
| 15 | POST | `/api/products/` | 创建产品类型 |
| 16 | GET | `/api/products/<id>/` | 产品类型详情 |
| 17 | PUT | `/api/products/<id>/` | 更新产品类型 |
| 18 | DELETE | `/api/products/<id>/` | 删除产品类型 |
| 19 | GET | `/api/products/<id>/parameters/` | 产品参数列表 |
| 20 | POST | `/api/products/<id>/parameters/` | 创建产品参数 |
| 21 | GET | `/api/products/parameters/<id>/` | 参数详情 |
| 22 | PUT | `/api/products/parameters/<id>/` | 更新参数 |
| 23 | DELETE | `/api/products/parameters/<id>/` | 删除参数 |
| 24 | GET | `/api/tests/tasks/` | 任务列表 |
| 25 | POST | `/api/tests/tasks/` | 创建任务 |
| 26 | GET | `/api/tests/tasks/<id>/` | 任务详情 |
| 27 | PUT | `/api/tests/tasks/<id>/` | 更新任务 |
| 28 | DELETE | `/api/tests/tasks/<id>/` | 删除任务 |
| 29 | POST | `/api/tests/tasks/<id>/execute/` | 执行任务 |
| 30 | POST | `/api/tests/tasks/<id>/stop/` | 停止任务 |
| 31 | POST | `/api/tests/tasks/<id>/upload/` | 上传结果 |
| 32 | GET | `/api/tests/results/` | 结果列表 |
| 33 | GET | `/api/tests/results/<id>/` | 结果详情 |
| 34 | GET | `/api/tests/results/<id>/screenshots/` | 结果截图 |
| 35 | GET | `/api/tests/results/<id>/export/` | 导出报告 |
| 36 | GET | `/api/scripts/` | 脚本列表 |
| 37 | POST | `/api/scripts/` | 创建脚本 |
| 38 | GET | `/api/scripts/<id>/` | 脚本详情 |
| 39 | PUT | `/api/scripts/<id>/` | 更新脚本 |
| 40 | DELETE | `/api/scripts/<id>/` | 删除脚本 |
| 41 | POST | `/api/scripts/<id>/duplicate/` | 复制脚本 |
| 42 | GET | `/api/scripts/<id>/versions/` | 版本列表 |
| 43 | GET | `/api/scripts/<id>/versions/<vid>/` | 版本详情 |
| 44 | GET | `/api/scripts/<id>/export/` | 单脚本导出 |
| 45 | POST | `/api/scripts/export/` | 批量导出 |
| 46 | POST | `/api/scripts/import/` | 导入 |
| 47 | GET | `/api/scripts/elements/` | 元素列表 |
| 48 | POST | `/api/scripts/elements/` | 创建元素 |
| 49 | GET | `/api/scripts/elements/<id>/` | 元素详情 |
| 50 | PUT | `/api/scripts/elements/<id>/` | 更新元素 |
| 51 | DELETE | `/api/scripts/elements/<id>/` | 删除元素 |
| 52 | GET | `/api/scripts/steps/` | 步骤列表 |
| 53 | POST | `/api/scripts/steps/` | 创建步骤 |
| 54 | GET | `/api/scripts/steps/<id>/` | 步骤详情 |
| 55 | PUT | `/api/scripts/steps/<id>/` | 更新步骤 |
| 56 | DELETE | `/api/scripts/steps/<id>/` | 删除步骤 |
| 57 | GET | `/api/scripts/visual-editor/` | 可视化编辑器(获取类型) |
| 58 | POST | `/api/scripts/visual-editor/` | 可视化创建脚本 |
| 59 | POST | `/api/scripts/validate-script/` | 验证脚本 |
| 60 | GET | `/api/scripts/global-config/` | 全局配置 |
| 61 | PUT | `/api/scripts/global-config/` | 更新全局配置 |
| 62 | POST | `/api/scripts/recording/start/` | 启动录制 |
| 63 | GET | `/api/scripts/recording/<sid>/actions/` | 获取录制操作 |
| 64 | POST | `/api/scripts/recording/<sid>/stop/` | 停止录制 |
| 65 | POST | `/api/scripts/recording/<sid>/convert/` | 转换录制 |
| 66 | GET | `/api/scripts/action-sets/` | 动作集合列表 |
| 67 | POST | `/api/scripts/action-sets/` | 创建动作集合 |
| 68 | GET | `/api/scripts/action-sets/<id>/` | 动作集合详情 |
| 69 | PUT | `/api/scripts/action-sets/<id>/` | 更新动作集合 |
| 70 | DELETE | `/api/scripts/action-sets/<id>/` | 删除动作集合 |
| 71 | GET | `/api/scripts/action-sets/<id>/export/` | 导出动作集合 |
| 72 | POST | `/api/scripts/action-sets/<id>/expand/` | 展开动作集合 |
| 73 | POST | `/api/scripts/action-sets/export/` | 批量导出 |
| 74 | POST | `/api/scripts/action-sets/import/` | 导入动作集合 |
| 75 | GET | `/api/scripts/action-sets/categories/` | 分类列表 |
| 76 | GET | `/api/scripts/action-sets/<aid>/steps/` | 步骤列表 |
| 77 | POST | `/api/scripts/action-sets/<aid>/steps/` | 创建步骤 |
| 78 | POST | `/api/scripts/action-sets/<aid>/steps/reorder/` | 步骤重排序 |
| 79 | GET | `/api/scripts/action-sets/steps/<id>/` | 步骤详情 |
| 80 | PUT | `/api/scripts/action-sets/steps/<id>/` | 更新步骤 |
| 81 | DELETE | `/api/scripts/action-sets/steps/<id>/` | 删除步骤 |
| 82 | GET | `/api/scripts/action-sets/<aid>/parameters/` | 参数列表 |
| 83 | POST | `/api/scripts/action-sets/<aid>/parameters/` | 创建参数 |
| 84 | GET | `/api/scripts/action-sets/parameters/<id>/` | 参数详情 |
| 85 | PUT | `/api/scripts/action-sets/parameters/<id>/` | 更新参数 |
| 86 | DELETE | `/api/scripts/action-sets/parameters/<id>/` | 删除参数 |
| 87 | GET | `/api/scripts/marketplace/items/` | 市场文件列表 |
| 88 | GET | `/api/scripts/marketplace/search/` | 市场搜索 |
| 89 | POST | `/api/scripts/marketplace/folder/` | 创建文件夹 |
| 90 | GET | `/api/scripts/marketplace/download/` | 下载文件 |
| 91 | GET | `/api/scripts/marketplace/preview/` | 预览文件 |
| 92 | POST | `/api/scripts/marketplace/upload/` | 上传文件 |

**小计: 92 个接口**

### 自动化管理平台 (FastAPI, 端口 8001)

| 序号 | 方法 | 接口路径 | 说明 |
|------|------|---------|------|
| 1 | GET | `/api/items` | 文件/文件夹列表 |
| 2 | POST | `/api/folder` | 创建文件夹 |
| 3 | DELETE | `/api/items/<name>` | 删除文件/文件夹 |
| 4 | PUT | `/api/items/<name>/rename` | 重命名 |
| 5 | POST | `/api/upload` | 上传文件 |
| 6 | GET | `/api/items/<name>/download` | 下载文件 |
| 7 | GET | `/api/items/<name>/preview` | 预览文件 |
| 8 | GET | `/api/search` | 搜索文件 |
| 9 | POST | `/api/script-results/upload` | 上传脚本结果 |
| 10 | GET | `/api/script-results` | 结果列表(分页) |
| 11 | GET | `/api/script-results/<id>` | 结果详情 |
| 12 | DELETE | `/api/script-results/<id>` | 删除结果 |
| 13 | GET | `/api/script-results/stats` | 统计数据 |
| 14 | GET | `/api/script-results/trend` | 趋势数据 |
| 15 | GET | `/api/script-results/anomalies` | 异常分析 |
| 16 | GET | `/api/config` | 获取配置 |
| 17 | POST | `/api/config` | 更新配置 |

**小计: 17 个接口**

### 总计: 109 个接口
