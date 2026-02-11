# 检测标准管理系统 API 接口文档

## 1. 接口概述

### 1.1 统一响应格式

所有API接口采用统一的JSON响应格式，便于前端统一处理：

#### 1.1.1 成功响应（单条数据）
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据对象
  }
}
```

#### 1.1.2 成功响应（列表数据）
```json
{
  "code": 200,
  "message": "获取列表成功",
  "data": [
    // 数据列表
  ],
  "total": 100 // 总记录数（仅列表接口返回）
}
```

#### 1.1.3 失败响应
```json
{
  "code": 400,
  "message": "操作失败: 具体错误原因",
  "data": null
}
```

### 1.2 认证方式

- 采用 **JWT Token** 认证机制
- 获取Token：通过 `/api/auth/token` 接口获取
- 认证方式：在请求头中添加 `Authorization: Bearer {token}`
- Token有效期：访问令牌默认15分钟，刷新令牌默认7天，可通过刷新Token接口更新
- 单端登录限制：同一用户在新设备登录后，旧设备的令牌会自动失效，新设备登录时会收到相应提示

## 2. 认证相关接口

### 2.1 获取Token

**请求信息**
- `POST /api/auth/token`
- Content-Type: `application/x-www-form-urlencoded`

**请求参数**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应示例**

#### 2.1.1 首次登录
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "name": "管理员",
      "username": "admin",
      "is_active": true,
      "is_admin": true,
      "created_at": "2025-12-20T10:00:00",
      "updated_at": "2025-12-21T15:30:00",
      "last_login_at": "2025-12-21T15:30:00",
      "roles": ["admin", "editor"],
      "permissions": ["read", "write", "delete", "manage_users"]
    }
  }
}
```

#### 2.1.2 其他设备登录
```json
{
  "code": 200,
  "message": "登录成功，您的账号已在其他设备登录",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "name": "管理员",
      "username": "admin",
      "is_active": true,
      "is_admin": true,
      "created_at": "2025-12-20T10:00:00",
      "updated_at": "2025-12-21T15:30:00",
      "last_login_at": "2025-12-21T15:30:00",
      "roles": ["admin", "editor"],
      "permissions": ["read", "write", "delete", "manage_users"]
    }
  }
}
```

### 2.2 刷新Token

**请求信息**
- `POST /api/auth/refresh`
- Content-Type: `application/json`

**请求参数**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| refresh_token | string | 是 | 刷新令牌 |

**请求体示例**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "令牌刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**说明**：
- 每次使用刷新令牌获取新访问令牌时，系统会同时生成新的刷新令牌
- 旧的刷新令牌会被添加到黑名单，无法再次使用
- 新刷新令牌的有效期与原刷新令牌相同（默认7天）

### 2.3 获取当前用户信息

**请求信息**
- `GET /api/auth/me`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取用户信息成功",
  "data": {
    "id": 1,
    "name": "管理员",
    "username": "admin",
    "is_active": true,
    "is_admin": true,
    "created_at": "2025-12-20T10:00:00",
    "updated_at": "2025-12-21T15:30:00",
    "last_login_at": "2025-12-21T15:30:00",
    "roles": ["admin", "editor"],
    "permissions": ["read", "write", "delete", "manage_users"]
  }
}
```

### 2.4 注销登录

**请求信息**
- `POST /api/auth/logout`
- Headers: `Authorization: Bearer {access_token}`

**说明**：
- 注销后，当前访问令牌将被添加到黑名单，无法再用于访问API
- 同时清除Redis中的用户令牌缓存，包括访问令牌和刷新令牌，使刷新令牌也失效

**响应示例**
```json
{
  "code": 200,
  "message": "注销成功",
  "data": null
}
```

## 3. 检测相关接口

**注意**：所有检测相关接口（`/api/detection/*`）需要登录才能访问，请求时需在Headers中添加 `Authorization: Bearer {access_token}`。

### 3.1 分类相关接口

#### 3.1.1 获取分类列表

**请求信息**
- `GET /api/detection/categories`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 100 | 每页数量，用于分页 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取分类列表成功",
  "data": [
    {
      "category_id": 1,
      "category_name": "建筑材料",
      "parent_id": null,
      "sort_order": 0,
      "status": 1,
      "create_time": "2025-12-20T10:00:00",
      "update_time": "2025-12-20T10:00:00",
      "children": []
    }
  ],
  "total": 4
}
```

#### 3.1.2 获取单个分类

**请求信息**
- `GET /api/detection/categories/{category_id}`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取分类成功",
  "data": {
    "category_id": 1,
    "category_name": "建筑材料",
    "parent_id": null,
    "sort_order": 0,
    "status": 1,
    "create_time": "2025-12-20T10:00:00",
    "update_time": "2025-12-20T10:00:00"
  }
}
```

#### 3.1.3 创建分类

**请求信息**
- `POST /api/detection/categories`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "category_name": "防水材料",
  "parent_id": null,
  "sort_order": 2,
  "status": 1
}
```

**响应示例**
```json
{
  "code": 201,
  "message": "创建分类成功",
  "data": {
    "category_id": 3,
    "category_name": "防水材料",
    "parent_id": null,
    "sort_order": 2,
    "status": 1,
    "create_time": "2025-12-21T12:00:00",
    "update_time": "2025-12-21T12:00:00"
  }
}
```

#### 3.1.4 更新分类

**请求信息**
- `PUT /api/detection/categories/{category_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "category_name": "新型防水材料",
  "parent_id": null,
  "sort_order": 0,
  "status": 1
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新分类成功",
  "data": {
    "category_id": 3,
    "category_name": "新型防水材料",
    "parent_id": null,
    "sort_order": 0,
    "status": 1,
    "create_time": "2025-12-21T12:00:00",
    "update_time": "2025-12-21T12:30:00"
  }
}
```

#### 3.1.5 删除分类

**请求信息**
- `DELETE /api/detection/categories/{category_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)

**响应示例**
```json
{
  "code": 200,
  "message": "删除分类成功",
  "data": null
}
```



### 3.2 检测对象相关接口

#### 3.2.1 获取检测对象列表

**请求信息**
- `GET /api/detection/objects`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 100 | 每页数量，用于分页 |
| status | integer | 否 | null | 状态：1=启用，0=禁用，精确匹配 |
| search | string | 否 | null | 搜索关键词，支持按名称或编码模糊搜索 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测对象列表成功",
  "data": [
    {
      "object_name": "普通硅酸盐水泥",
      "object_code": "11",
      "category_id": 3,
      "description": "强度等级42.5的普通硅酸盐水泥",
      "status": 1,
      "object_id": 1,
      "create_time": "2026-01-17T17:23:44",
      "update_time": "2026-01-18T12:39:18",
      "category_name": "防水材料"
    }
  ],
  "total": 2
}
```

#### 3.2.2 获取单个检测对象

**请求信息**
- `GET /api/detection/objects/{object_id}`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测对象成功",
  "data": {
    "object_name": "普通硅酸盐水泥",
    "object_code": "11",
    "category_id": 3,
    "description": "强度等级42.5的普通硅酸盐水泥",
    "status": 1,
    "object_id": 1,
    "create_time": "2026-01-17T17:23:44",
    "update_time": "2026-01-18T12:39:18",
    "category_name": "防水材料"
  }
}
```

#### 3.2.3 创建检测对象

**请求信息**
- `POST /api/detection/objects`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "object_name": "HRB400E钢筋",
  "object_code": "HRB400E",
  "category_id": 1,
  "description": "高强度抗震钢筋，强度等级400E",
  "sort_order": 0,
  "status": 1
}
```

**验证规则**
- 分类ID必须存在且状态为启用（status=1），禁用分类无法关联

**响应示例**
```json
{
  "code": 201,
  "message": "创建检测对象成功",
  "data": {
    "object_name": "HRB400E钢筋",
    "object_code": "HRB400E",
    "category_id": 1,
    "category_name": "建筑材料",
    "description": "高强度抗震钢筋，强度等级400E",
    "sort_order": 0,
    "status": 1,
    "object_id": 3,
    "create_time": "2026-01-18T17:00:00",
    "update_time": "2026-01-18T17:00:00"
  }
}
```

#### 3.2.4 更新检测对象

**请求信息**
- `PUT /api/detection/objects/{object_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "object_name": "HRB400E抗震钢筋",
  "object_code": "HRB400E",
  "category_id": 1,
  "description": "高强度抗震钢筋，强度等级400E，符合GB 1499.2-2018标准",
  "sort_order": 1,
  "status": 1
}
```

**验证规则**
- 如果修改了分类ID，新分类必须存在且状态为启用（status=1），禁用分类无法关联

**响应示例**
```json
{
  "code": 200,
  "message": "更新检测对象成功",
  "data": {
    "object_name": "HRB400E抗震钢筋",
    "object_code": "HRB400E",
    "category_id": 1,
    "description": "高强度抗震钢筋，强度等级400E，符合GB 1499.2-2018标准",
    "status": 1,
    "object_id": 2,
    "create_time": "2026-01-17T17:23:44",
    "update_time": "2026-01-18T17:30:00",
    "category_name": "建筑材料"
  }
}
```

#### 3.2.5 删除检测对象

**请求信息**
- `DELETE /api/detection/objects/{object_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)

**响应示例**
```json
{
  "code": 200,
  "message": "删除检测对象成功",
  "data": null
}
```

### 3.3 检测项目相关接口

#### 3.3.1 获取检测项目列表

**请求信息**
- `GET /api/detection/items`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 100 | 每页数量，用于分页 |
| status | integer | 否 | null | 状态：1=启用，0=禁用，精确匹配 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测项目列表成功",
  "data": [
    {
      "item_id": 1,
      "object_id": 1,
      "object_name": "普通硅酸盐水泥",
      "item_name": "水泥检测",
      "description": "检测水泥的物理性能和化学性能，包括抗压强度、抗折强度、凝结时间、安定性等指标",
      "sort_order": 0,
      "status": 1,
      "create_time": "2025-12-20T10:00:00",
      "update_time": "2025-12-20T10:00:00"
    }
  ],
  "total": 4
}
```

#### 3.3.2 获取单个检测项目

**请求信息**
- `GET /api/detection/items/{item_id}`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测项目成功",
  "data": {
    "item_id": 1,
    "object_id": 1,
    "object_name": "普通硅酸盐水泥",
    "item_name": "水泥检测",
    "description": "检测水泥的物理性能和化学性能，包括抗压强度、抗折强度、凝结时间、安定性等指标",
    "sort_order": 0,
    "status": 1,
    "create_time": "2025-12-20T10:00:00",
    "update_time": "2025-12-20T10:00:00"
  }
}
```

#### 3.3.3 创建检测项目

**请求信息**
- `POST /api/detection/items`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "object_id": 1,
  "item_name": "水泥检测",
  "description": "检测水泥的物理性能和化学性能，包括抗压强度、抗折强度、凝结时间、安定性等指标",
  "sort_order": 0,
  "status": 1
}
```

**响应示例**
```json
{
  "code": 201,
  "message": "创建检测项目成功",
  "data": {
    "item_id": 1,
    "object_id": 1,
    "object_name": "普通硅酸盐水泥",
    "item_name": "水泥检测",
    "description": "检测水泥的物理性能和化学性能，包括抗压强度、抗折强度、凝结时间、安定性等指标",
    "sort_order": 0,
    "status": 1,
    "create_time": "2025-12-21T11:00:00",
    "update_time": "2025-12-21T11:00:00"
  }
}
```

#### 3.3.4 更新检测项目

**请求信息**
- `PUT /api/detection/items/{item_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "object_id": 1,
  "item_name": "水泥物理性能检测",
  "description": "更新后的检测项目描述，仅检测水泥物理性能",
  "sort_order": 0,
  "status": 1
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新检测项目成功",
  "data": {
    "item_id": 1,
    "object_id": 1,
    "object_name": "普通硅酸盐水泥",
    "item_name": "水泥物理性能检测",
    "description": "更新后的检测项目描述，仅检测水泥物理性能",
    "sort_order": 0,
    "status": 1,
    "create_time": "2025-12-21T11:00:00",
    "update_time": "2025-12-21T11:30:00"
  }
}
```

#### 3.3.5 删除检测项目

**请求信息**
- `DELETE /api/detection/items/{item_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)

**响应示例**
```json
{
  "code": 200,
  "message": "删除检测项目成功",
  "data": null
}
```

### 3.4 检测参数相关接口

#### 3.4.1 获取检测参数列表

**请求信息**
- `GET /api/detection/params`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 100 | 每页数量，用于分页 |
| param_name | string | 否 | null | 检测参数名称，支持模糊搜索 |
| material_name | string | 否 | null | 材料名称，支持模糊搜索 |
| item_id | integer | 否 | null | 项目ID，精确匹配 |
| status | integer | 否 | null | 状态：1=启用，0=禁用，精确匹配 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测参数列表成功",
  "data": [
    {
      "param_id": 1,
      "item_id": 1,
      "param_name": "抗压强度",
      "material_name": "普通硅酸盐水泥",
      "price": "50.00元/组",
      "sample_processing_fee": "20.00元/组",
      "is_regular_param": 1,
      "sort_order": 0,
      "status": 1,
      "template_id": 1,
      "sampling_batch": "每批次≤500吨取1组",
      "sampling_frequency": "每月1次",
      "sampling_require": "需使用无菌采样袋，采样量≥500g",
      "inspection_require": "样品需在24小时内送检",
      "required_info": "产品名称、批次号、生产日期、规格",
      "report_time": "常规5个工作日，加急3个工作日",
      "sample_image_path": "/images/sampling/cement.jpg",
      "create_time": "2025-12-20T10:00:00",
      "update_time": "2025-12-20T10:00:00",
      "standard_ids": [1],
      "standards": [
        {
          "standard_id": 1,
          "standard_code": "GB 175-2023",
          "standard_name": "通用硅酸盐水泥"
        }
      ],
      "template": {
        "template_id": 1,
        "template_name": "水泥检测委托单",
        "template_version": "V1.0",
        "template_code": "SN-2024-001",
        "file_path": "/static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx",
        "file_type": ".docx",
        "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx&expire=1737820800&signature=abc123xyz"
      }
    }
  ],
  "total": 16
}
```

#### 3.4.2 获取单个检测参数

**请求信息**
- `GET /api/detection/params/{param_id}`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测参数成功",
  "data": {
      "param_id": 1,
      "item_id": 1,
      "param_name": "抗压强度",
      "material_name": "普通硅酸盐水泥",
      "price": "50.00元/组",
      "sample_processing_fee": "20.00元/组",
      "is_regular_param": 1,
      "sort_order": 0,
      "status": 1,
      "template_id": 1,
      "sampling_batch": "每批次≤500吨取1组",
      "sampling_frequency": "每月1次",
      "sampling_require": "需使用无菌采样袋，采样量≥500g",
      "inspection_require": "样品需在24小时内送检",
      "required_info": "产品名称、批次号、生产日期、规格",
      "report_time": "常规5个工作日，加急3个工作日",
      "sample_image_path": "/images/sampling/cement.jpg",
      "create_time": "2025-12-20T10:00:00",
      "update_time": "2025-12-20T10:00:00",
      "standard_ids": [1],
      "standards": [
        {
          "standard_id": 1,
          "standard_code": "GB 175-2023",
          "standard_name": "通用硅酸盐水泥"
        }
      ],
      "template": {
        "template_id": 1,
        "template_name": "水泥检测委托单",
        "template_version": "V1.0",
        "template_code": "SN-2024-001",
        "file_path": "/static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx",
        "file_type": ".docx",
        "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx&expire=1737820800&signature=abc123xyz"
      }
    }
}
```

#### 3.4.3 创建检测参数

**请求信息**
- `POST /api/detection/params`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "item_id": 1,
  "param_name": "抗折强度",
  "material_name": "普通硅酸盐水泥",
  "price": "40.00元/组",
  "sample_processing_fee": "20.00元/组",
  "is_regular_param": 1,
  "sort_order": 1,
  "status": 1,
  "template_id": 1,
  "sampling_batch": "每批次≤500吨取1组",
  "sampling_frequency": "每月1次",
  "sampling_require": "需使用无菌采样袋，采样量≥500g",
  "inspection_require": "样品需在24小时内送检",
  "required_info": "产品名称、批次号、生产日期、规格",
  "report_time": "常规5个工作日，加急3个工作日",
  "sample_image_path": "/images/sampling/cement.jpg"
}
```

**响应示例**
```json
{
  "code": 201,
  "message": "创建检测参数成功",
  "data": {
      "param_id": 2,
      "item_id": 1,
      "param_name": "抗折强度",
      "material_name": "普通硅酸盐水泥",
      "price": "40.00元/组",
      "sample_processing_fee": "20.00元/组",
      "is_regular_param": 1,
      "sort_order": 1,
      "status": 1,
      "template_id": 1,
      "sampling_batch": "每批次≤500吨取1组",
      "sampling_frequency": "每月1次",
      "sampling_require": "需使用无菌采样袋，采样量≥500g",
      "inspection_require": "样品需在24小时内送检",
      "required_info": "产品名称、批次号、生产日期、规格",
      "report_time": "常规5个工作日，加急3个工作日",
      "sample_image_path": "/images/sampling/cement.jpg",
      "create_time": "2025-12-21T12:00:00",
      "update_time": "2025-12-21T12:00:00",
      "standard_ids": [],
      "standards": [],
      "template": {
        "template_id": 1,
        "template_name": "水泥检测委托单",
        "template_version": "V1.0",
        "template_code": "SN-2024-001",
        "file_path": "/static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx",
        "file_type": ".docx",
        "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx&expire=1737820800&signature=abc123xyz"
      }
    }
}
```

#### 3.4.4 更新检测参数

**请求信息**
- `PUT /api/detection/params/{param_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "param_name": "抗折强度检测",
  "price": "45.00元/组",
  "sort_order": 0,
  "status": 1,
  "sampling_batch": "每批次≤600吨取1组"
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新检测参数成功",
  "data": {
      "param_id": 2,
      "item_id": 1,
      "param_name": "抗折强度检测",
      "material_name": "普通硅酸盐水泥",
      "price": "45.00元/组",
      "sample_processing_fee": "20.00元/组",
      "is_regular_param": 1,
      "sort_order": 0,
      "status": 1,
      "template_id": 1,
      "sampling_batch": "每批次≤600吨取1组",
      "sampling_frequency": "每月1次",
      "sampling_require": "需使用无菌采样袋，采样量≥500g",
      "inspection_require": "样品需在24小时内送检",
      "required_info": "产品名称、批次号、生产日期、规格",
      "report_time": "常规5个工作日，加急3个工作日",
      "sample_image_path": "/images/sampling/cement.jpg",
      "create_time": "2025-12-21T12:00:00",
      "update_time": "2025-12-21T12:30:00",
      "standard_ids": [],
      "standards": [],
      "template": {
        "template_id": 1,
        "template_name": "水泥检测委托单",
        "template_version": "V1.0",
        "template_code": "SN-2024-001",
        "file_path": "/static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx",
        "file_type": ".docx",
        "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx&expire=1737820800&signature=abc123xyz"
      }
    }
}
```

#### 3.4.5 删除检测参数

**请求信息**
- `DELETE /api/detection/params/{param_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)

**响应示例**
```json
{
  "code": 200,
  "message": "删除检测参数成功",
  "data": null
}
```

### 3.5 委托单模板相关接口

#### 3.5.1 获取委托单模板列表

**请求信息**
- `GET /api/detection/templates`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 100 | 每页数量，用于分页 |
| search_keyword | string | 否 | null | 搜索关键词，支持按模板名称和编号模糊搜索 |
| status | integer | 否 | null | 状态：1=启用，0=禁用，精确匹配 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取委托单模板列表成功",
  "data": [
    {
      "template_id": 1,
      "template_name": "水泥检测委托单",
      "template_version": "V1.0",
      "template_code": "SN-2024-001",
      "file_path": "/static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx",
      "file_type": ".docx",
      "upload_user": "admin",
      "status": 1,
      "remark": "水泥检测通用委托单模板",
      "upload_time": "2025-12-20T10:00:00",
      "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx&expire=1737820800&signature=abc123xyz"
    }
  ],
  "total": 2
}
```

#### 3.5.2 获取单个委托单模板

**请求信息**
- `GET /api/detection/templates/{template_id}`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取委托单模板成功",
  "data": {
      "template_id": 1,
      "template_name": "水泥检测委托单",
      "template_version": "V1.0",
      "template_code": "SN-2024-001",
      "file_path": "/static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx",
      "file_type": ".docx",
      "upload_user": "admin",
      "status": 1,
      "remark": "水泥检测通用委托单模板",
      "upload_time": "2025-12-20T10:00:00",
      "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx&expire=1737820800&signature=abc123xyz"
    }
}
```

#### 3.5.3 创建委托单模板

**请求信息**
- `POST /api/detection/templates`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `multipart/form-data`

**请求参数**
| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| template_name | Form | string | 是 | 模板名称 |
| template_version | Form | string | 是 | 模板版本 |
| template_code | Form | string | 否 | 模板编号，唯一标识 |
| file_type | Form | string | 是 | 文件类型，仅支持.doc、.docx、.xls、.xlsx |
| status | Form | integer | 否 | 状态：1=启用，0=禁用 |
| remark | Form | string | 否 | 备注 |
| file | File | file | 是 | 模板文件，仅支持.doc、.docx、.xls、.xlsx格式 |

**响应示例**
```json
{
  "code": 201,
  "message": "创建委托单模板成功",
  "data": {
      "template_id": 2,
      "template_name": "钢筋检测委托单",
      "template_version": "V1.0",
      "template_code": "GJ-2024-001",
      "file_path": "/static/templates/delegation_form_templates/钢筋检测委托单GJ-2024-001.docx",
      "file_type": ".docx",
      "upload_user": "admin",
      "status": 1,
      "remark": "钢筋检测通用委托单模板",
      "upload_time": "2025-12-21T14:00:00"
    }
}
```

#### 3.5.4 更新委托单模板

**请求信息**
- `PUT /api/detection/templates/{template_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `multipart/form-data`

**请求参数**
| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| template_id | URL路径 | integer | 是 | 模板ID |
| template_name | Form | string | 否 | 模板名称 |
| template_version | Form | string | 否 | 模板版本 |
| template_code | Form | string | 否 | 模板编号，唯一标识 |
| file_type | Form | string | 否 | 文件类型，仅支持.doc、.docx、.xls、.xlsx |
| status | Form | integer | 否 | 状态：1=启用，0=禁用 |
| remark | Form | string | 否 | 备注 |
| file | File | file | 否 | 模板文件（可选，不提供则不更新文件），仅支持.doc、.docx、.xls、.xlsx格式 |

**响应示例**
```json
{
  "code": 200,
  "message": "更新委托单模板成功",
  "data": {
      "template_id": 2,
      "template_name": "钢筋检测委托单（更新版）",
      "template_version": "V1.1",
      "template_code": "GJ-2024-002",
      "file_path": "/static/templates/delegation_form_templates/钢筋检测委托单（更新版）GJ-2024-002.docx",
      "file_type": ".docx",
      "upload_user": "admin",
      "status": 1,
      "remark": "更新后的钢筋检测委托单模板",
      "upload_time": "2025-12-21T14:00:00"
    }
}
```

#### 3.5.5 删除委托单模板

**请求信息**
- `DELETE /api/detection/templates/{template_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)

**说明**：
- 删除模板时，系统会同时删除对应的模板文件

**响应示例**
```json
{
  "code": 200,
  "message": "删除委托单模板成功",
  "data": null
}
```

#### 3.5.6 获取委托单模板使用情况

**请求信息**
- `GET /api/detection/templates/{template_id}/usage`
- Headers: `Authorization: Bearer {access_token}`

**说明**：
- 获取委托单模板被使用情况，通过查检测参数查对应的检测项目，再通过对应的检测项目查对应的检测对象
- 返回格式：检测对象名称（启/禁用）--检测项目名称（启/禁用）--检测参数名称（启/禁用）

**响应示例**
```json
{
  "code": 200,
  "message": "获取委托单模板使用情况成功",
  "data": [
    "水泥（启用）--水泥物理性能检测（启用）--密度（禁用）",
    "水泥（启用）--水泥物理性能检测（启用）--抗压强度（启用）"
  ]
}
```

## 4. 公开API接口

### 4.1 获取所有分类列表

**请求信息**
- `GET /api/public/detection/categories`

**描述**
获取所有分类的（id和名称）列表，按排序号顺序返回（只返回状态为启用的数据）

**响应示例**
```json
{
  "code": 200,
  "message": "获取分类列表成功",
  "data": [
    {
      "category_id": 1,
      "category_name": "建筑材料"
    },
    {
      "category_id": 2,
      "category_name": "防水材料"
    }
  ],
  "total": 2
}
```

### 4.2 获取分类下的检测对象

**请求信息**
- `GET /api/public/detection/categories/{category_id}/objects`

**参数说明**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| category_id | integer | 是 | 分类ID |

**描述**
获取某一ID分类下所有检测对象的（id和名称）列表，按排序号顺序返回（只返回状态为启用的数据）

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测对象列表成功",
  "data": [
    {
      "object_id": 1,
      "object_name": "普通硅酸盐水泥"
    },
    {
      "object_id": 2,
      "object_name": "HRB400E钢筋"
    }
  ],
  "total": 2
}
```

### 4.3 获取所有分类及其检测对象

**请求信息**
- `GET /api/public/detection/categories/objects`

**描述**
获取所有分类及其下的检测对象列表，按排序号顺序返回（只返回状态为启用的数据）

**响应示例**
```json
{
  "code": 200,
  "message": "获取分类及其检测对象列表成功",
  "data": [
    {
      "id": 1,
      "name": "建筑材料",
      "objects": [
        {
          "id": 1,
          "name": "普通硅酸盐水泥",
          "code": "11"
        },
        {
          "id": 2,
          "name": "HRB400E钢筋",
          "code": "HRB400E"
        }
      ]
    },
    {
      "id": 2,
      "name": "防水材料",
      "objects": [
        {
          "id": 3,
          "name": "沥青防水材料",
          "code": "LQ"
        }
      ]
    }
  ],
  "total": 2
}
```

### 4.4 获取检测对象下的检测项目

**请求信息**
- `GET /api/public/detection/objects/{object_id}/items`

**参数说明**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| object_id | integer | 是 | 检测对象ID |

**描述**
获取某一ID检测对象下所有检测项目的（id和名称）列表，按排序号顺序返回（只返回状态为启用的数据）

**响应示例**
```json
{
  "code": 200,
  "message": "获取检测项目列表成功",
  "data": [
    {
      "item_id": 1,
      "item_name": "水泥物理性能检测"
    },
    {
      "item_id": 2,
      "item_name": "水泥化学性能检测"
    }
  ],
  "total": 2
}
```

### 4.5 获取检测项目下的委托单模板列表

**请求信息**
- `GET /api/public/detection/items/{item_id}/templates`

**参数说明**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| item_id | integer | 是 | 检测项目ID |

**描述**
获取某一ID检测项目下所有检测参数关联的委托单模板列表，返回去重后的模板信息，包含模板ID、名称、编号和带签名的下载链接

**响应示例**
```json
{
  "code": 200,
  "message": "获取委托单模板列表成功",
  "data": [
    {
      "id": 1,
      "name": "水泥检测委托单",
      "code": "SN-2024-001",
      "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/水泥检测委托单SN-2024-001.docx&expire=1737820800&signature=abc123xyz"
    },
    {
      "id": 2,
      "name": "钢筋检测委托单",
      "code": "GJ-2024-001",
      "download_url": "http://localhost:1314/api/public/files/download/signed?file_path=static/templates/delegation_form_templates/钢筋检测委托单GJ-2024-001.docx&expire=1737820800&signature=def456uvw"
    }
  ],
  "total": 2
}
```

### 4.6 搜索检测项目

**请求信息**
- `GET /api/public/detection/items/search`

**参数说明**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| keyword | string | 是 | - | 搜索关键词，支持按检测对象、规范名称、规范代码、检测参数搜索 |

**描述**
根据关键词搜索检测项目列表，支持按检测对象、规范名称、规范代码、检测参数进行搜索。返回格式与"获取检测对象下的检测项目"接口一致，只返回检测项目的ID和名称。
- 返回包含关键词的检测项目（不区分大小写）

**响应示例**
```json
{
  "code": 200,
  "message": "搜索检测项目列表成功",
  "data": [
    {
      "item_id": 1,
      "item_name": "水泥物理性能检测"
    },
    {
      "item_id": 2,
      "item_name": "水泥化学性能检测"
    }
  ],
  "total": 2
}
```

**使用示例**
```
# 不带关键词，返回所有启用的检测项目
GET /api/public/detection/items/search

# 带关键词搜索，返回包含"水泥"的检测项目
GET /api/public/detection/items/search?keyword=水泥

# 带关键词搜索，返回包含"钢筋"的检测项目
GET /api/public/detection/items/search?keyword=钢筋
```
## 5. 管理接口

### 5.1 用户管理接口

#### 5.1.1 获取用户列表

**请求信息**
- `GET /api/admin/users`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 10 | 每页数量，用于分页 |
| username | string | 否 | null | 用户名，支持模糊搜索 |
| status | integer | 否 | null | 状态：1=启用，0=禁用，精确匹配 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取用户列表成功",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "name": "管理员",
      "email": "admin@example.com",
      "is_active": true,
      "is_admin": true,
      "created_at": "2025-12-20T10:00:00",
      "updated_at": "2025-12-20T10:00:00",
      "last_login_at": "2025-12-21T15:30:00",
      "roles": ["admin"]
    }
  ],
  "total": 1
}
```

#### 5.1.2 获取单个用户

**请求信息**
- `GET /api/admin/users/{user_id}`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取用户成功",
  "data": {
    "id": 1,
    "username": "admin",
    "name": "管理员",
    "email": "admin@example.com",
    "is_active": true,
    "is_admin": true,
    "created_at": "2025-12-20T10:00:00",
    "updated_at": "2025-12-20T10:00:00",
    "last_login_at": "2025-12-21T15:30:00",
    "roles": ["admin"]
  }
}
```

#### 5.1.3 创建用户

**请求信息**
- `POST /api/admin/users`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "username": "user1",
  "password": "password123",
  "name": "用户1",
  "email": "user1@example.com",
  "is_active": true,
  "roles": ["editor"]
}
```

**响应示例**
```json
{
  "code": 201,
  "message": "创建用户成功",
  "data": {
    "id": 2,
    "username": "user1",
    "name": "用户1",
    "email": "user1@example.com",
    "is_active": true,
    "is_admin": false,
    "created_at": "2025-12-21T16:00:00",
    "updated_at": "2025-12-21T16:00:00",
    "last_login_at": null,
    "roles": ["editor"]
  }
}
```

#### 5.1.4 更新用户

**请求信息**
- `PUT /api/admin/users/{user_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "name": "用户1（更新）",
  "email": "user1_update@example.com",
  "is_active": true,
  "roles": ["editor", "viewer"]
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新用户成功",
  "data": {
    "id": 2,
    "username": "user1",
    "name": "用户1（更新）",
    "email": "user1_update@example.com",
    "is_active": true,
    "is_admin": false,
    "created_at": "2025-12-21T16:00:00",
    "updated_at": "2025-12-21T16:30:00",
    "last_login_at": null,
    "roles": ["editor", "viewer"]
  }
}
```

#### 5.1.5 删除用户

**请求信息**
- `DELETE /api/admin/users/{user_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)

**响应示例**
```json
{
  "code": 200,
  "message": "删除用户成功",
  "data": null
}
```

### 5.2 角色管理接口

#### 5.2.1 获取角色列表

**请求信息**
- `GET /api/admin/roles`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 10 | 每页数量，用于分页 |
| name | string | 否 | null | 角色名称，支持模糊搜索 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取角色列表成功",
  "data": [
    {
      "id": 1,
      "name": "admin",
      "description": "管理员角色",
      "created_at": "2025-12-20T10:00:00",
      "updated_at": "2025-12-20T10:00:00"
    }
  ],
  "total": 1
}
```

#### 5.2.2 获取单个角色

**请求信息**
- `GET /api/admin/roles/{role_id}`
- Headers: `Authorization: Bearer {access_token}`

**响应示例**
```json
{
  "code": 200,
  "message": "获取角色成功",
  "data": {
    "id": 1,
    "name": "admin",
    "description": "管理员角色",
    "created_at": "2025-12-20T10:00:00",
    "updated_at": "2025-12-20T10:00:00",
    "permissions": ["read", "write", "delete", "manage_users"]
  }
}
```

#### 5.2.3 创建角色

**请求信息**
- `POST /api/admin/roles`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "name": "editor",
  "description": "编辑角色",
  "permissions": ["read", "write"]
}
```

**响应示例**
```json
{
  "code": 201,
  "message": "创建角色成功",
  "data": {
    "id": 2,
    "name": "editor",
    "description": "编辑角色",
    "created_at": "2025-12-21T17:00:00",
    "updated_at": "2025-12-21T17:00:00",
    "permissions": ["read", "write"]
  }
}
```

#### 5.2.4 更新角色

**请求信息**
- `PUT /api/admin/roles/{role_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)
- Content-Type: `application/json`

**请求体**
```json
{
  "description": "编辑角色（更新）",
  "permissions": ["read", "write", "delete"]
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新角色成功",
  "data": {
    "id": 2,
    "name": "editor",
    "description": "编辑角色（更新）",
    "created_at": "2025-12-21T17:00:00",
    "updated_at": "2025-12-21T17:30:00",
    "permissions": ["read", "write", "delete"]
  }
}
```

#### 5.2.5 删除角色

**请求信息**
- `DELETE /api/admin/roles/{role_id}`
- Headers: `Authorization: Bearer {token}` (管理员权限)

**响应示例**
```json
{
  "code": 200,
  "message": "删除角色成功",
  "data": null
}
```

### 5.3 权限管理接口

#### 5.3.1 获取权限列表

**请求信息**
- `GET /api/admin/permissions`
- Headers: `Authorization: Bearer {access_token}`

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，用于分页 |
| limit | integer | 否 | 10 | 每页数量，用于分页 |
| name | string | 否 | null | 权限名称，支持模糊搜索 |

**响应示例**
```json
{
  "code": 200,
  "message": "获取权限列表成功",
  "data": [
    {
      "id": 1,
      "name": "read",
      "description": "读取权限",
      "created_at": "2025-12-20T10:00:00",
      "updated_at": "2025-12-20T10:00:00"
    }
  ],
  "total": 1
}
```

## 6. 图片接口

### 6.1 获取图片

**请求信息**
- `GET /api/image/{data_unique_id}`

**参数说明**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| data_unique_id | string | 是 | - | 数据唯一标识 |
| device_type | string | 是 | - | 设备类型，必须是pc、phone或tablet中的一个 |
| image_type | string | 否 | png | 图片类型，可选值：png或svg |

**描述**
根据数据唯一标识和设备类型获取图片，支持PNG和SVG两种格式

**响应说明**
- 成功：返回图片流，Content-Type根据图片类型自动设置
  - PNG格式：Content-Type为image/png
  - SVG格式：Content-Type为image/svg+xml
- 失败：返回错误信息

**错误响应示例**
```json
{
  "code": 404,
  "message": "图片不存在",
  "data": null
}
```

**使用示例**
```
# 获取PNG格式图片
GET /api/image/detection:1?device_type=pc&image_type=png

# 获取SVG格式图片  
GET /api/image/detection:1?device_type=pc&image_type=svg
```

## 7. 常见状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | 成功 | 操作成功 |
| 201 | 创建成功 | 资源创建成功 |
| 400 | 请求错误 | 参数错误或请求格式错误 |
| 401 | 未授权 | Token无效或过期 |
| 403 | 禁止访问 | 没有权限 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 500 | 服务器错误 | 服务器内部错误 |

## 8. 错误码说明

| 错误码 | 描述 |
|--------|------|
| 10001 | 参数错误 |
| 10002 | 资源不存在 |
| 10003 | 权限不足 |
| 10004 | 操作失败 |
| 10005 | 数据库错误 |
| 10006 | 网络错误 |
| 10007 | 业务规则冲突 |
| 10008 | 文件操作错误 |

## 9. 最佳实践

1. **请求格式**
   - 所有API请求必须使用HTTPS协议
   - GET请求的参数必须使用URL查询字符串
   - POST/PUT/PATCH请求的参数必须使用JSON格式放在请求体中
   - 所有请求头必须包含Content-Type和Authorization（如果需要认证）

2. **响应处理**
   - 所有API响应必须使用JSON格式
   - 客户端必须检查响应的code字段，根据code字段处理不同的情况
   - 客户端必须处理网络错误和超时情况

3. **认证与授权**
   - 所有需要认证的API必须在请求头中包含Authorization字段
   - Token过期后，客户端必须使用刷新令牌获取新的访问令牌
   - 客户端必须处理Token无效或过期的情况

4. **错误处理**
   - 客户端必须处理所有可能的错误情况
   - 客户端必须显示友好的错误信息给用户
   - 客户端必须记录详细的错误日志，便于调试和分析

5. **性能优化**
   - 客户端必须合理使用缓存，减少API请求次数
   - 客户端必须使用分页查询，避免一次性获取大量数据
   - 客户端必须异步加载数据，提高用户体验

6. **安全性**
   - 客户端必须保护用户的Token，避免泄露
   - 客户端必须使用安全的存储方式存储Token
   - 客户端必须验证服务器的SSL证书，避免中间人攻击
