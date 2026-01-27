# 为detection模块创建接口层计划

## 1. 目录结构设计

创建完整的API路由和模型验证结构：

```
app/
├── routes/             # 新增：API路由目录
│   ├── __init__.py     # 路由包初始化
│   └── detection.py    # detection模块路由
├── schemas/            # 新增：Pydantic模型目录
│   ├── __init__.py     # 模型包初始化
│   └── detection.py    # detection模块Pydantic模型
├── models/             # 已存在：数据模型
├── services/           # 已存在：业务逻辑
└── app.py              # 已存在：主应用文件
```

## 2. 实现内容

### 2.1 创建Pydantic模型

在`app/schemas/detection.py`中实现：
- 分类（Category）的请求和响应模型
- 检测规范（DetectionStandard）的请求和响应模型
- 检测项目组（DetectionGroup）的请求和响应模型
- 检测项目（DetectionItem）的请求和响应模型
- 检测指南（DetectionGuide）的请求和响应模型
- 委托单模板（DelegationFormTemplate）的请求和响应模型

### 2.2 创建API路由

在`app/routes/detection.py`中实现RESTful API：

| 资源 | 方法 | 路径 | 功能 | 服务调用 |
|------|------|------|------|----------|
| 分类 | GET | /api/detection/categories | 获取所有分类 | CategoryService.get_all() |
| 分类 | GET | /api/detection/categories/{id} | 获取单个分类 | CategoryService.get_by_id() |
| 分类 | POST | /api/detection/categories | 创建分类 | CategoryService.create() |
| 分类 | PUT | /api/detection/categories/{id} | 更新分类 | CategoryService.update() |
| 分类 | DELETE | /api/detection/categories/{id} | 删除分类 | CategoryService.delete() |
| 检测规范 | GET | /api/detection/standards | 获取所有规范 | DetectionStandardService.get_all() |
| 检测规范 | GET | /api/detection/standards/{id} | 获取单个规范 | DetectionStandardService.get_by_id() |
| 检测规范 | POST | /api/detection/standards | 创建规范 | DetectionStandardService.create() |
| 检测规范 | PUT | /api/detection/standards/{id} | 更新规范 | DetectionStandardService.update() |
| 检测规范 | DELETE | /api/detection/standards/{id} | 删除规范 | DetectionStandardService.delete() |
| 检测项目组 | GET | /api/detection/groups | 获取所有项目组 | DetectionGroupService.get_all() |
| 检测项目组 | GET | /api/detection/groups/{id} | 获取单个项目组 | DetectionGroupService.get_by_id() |
| 检测项目组 | POST | /api/detection/groups | 创建项目组 | DetectionGroupService.create() |
| 检测项目组 | PUT | /api/detection/groups/{id} | 更新项目组 | DetectionGroupService.update() |
| 检测项目组 | DELETE | /api/detection/groups/{id} | 删除项目组 | DetectionGroupService.delete() |
| 检测项目 | GET | /api/detection/items | 获取所有项目 | DetectionItemService.get_all() |
| 检测项目 | GET | /api/detection/items/{id} | 获取单个项目 | DetectionItemService.get_by_id() |
| 检测项目 | POST | /api/detection/items | 创建项目 | DetectionItemService.create() |
| 检测项目 | PUT | /api/detection/items/{id} | 更新项目 | DetectionItemService.update() |
| 检测项目 | DELETE | /api/detection/items/{id} | 删除项目 | DetectionItemService.delete() |
| 检测指南 | GET | /api/detection/guides | 获取所有指南 | DetectionGuideService.get_all() |
| 检测指南 | GET | /api/detection/guides/{id} | 获取单个指南 | DetectionGuideService.get_by_id() |
| 检测指南 | POST | /api/detection/guides | 创建指南 | DetectionGuideService.create() |
| 检测指南 | PUT | /api/detection/guides/{id} | 更新指南 | DetectionGuideService.update() |
| 检测指南 | DELETE | /api/detection/guides/{id} | 删除指南 | DetectionGuideService.delete() |
| 委托单模板 | GET | /api/detection/templates | 获取所有模板 | DelegationFormTemplateService.get_all() |
| 委托单模板 | GET | /api/detection/templates/{id} | 获取单个模板 | DelegationFormTemplateService.get_by_id() |
| 委托单模板 | POST | /api/detection/templates | 创建模板 | DelegationFormTemplateService.create() |
| 委托单模板 | PUT | /api/detection/templates/{id} | 更新模板 | DelegationFormTemplateService.update() |
| 委托单模板 | DELETE | /api/detection/templates/{id} | 删除模板 | DelegationFormTemplateService.delete() |

### 2.3 注册路由

在`app/routes/__init__.py`中创建路由注册函数，在`app.py`中注册所有路由。

### 2.4 错误处理

实现统一的错误处理，将服务层返回的错误信息转换为合适的HTTP状态码和响应格式。

## 3. 技术要点

1. **使用FastAPI的APIRouter**实现模块化路由管理
2. **使用Pydantic模型**进行请求和响应验证
3. **遵循RESTful API设计规范**
4. **统一的响应格式**：成功返回数据，失败返回错误信息和状态码
5. **调用已有的服务层**，不重复实现业务逻辑
6. **适当的HTTP状态码**：200成功，201创建成功，400请求错误，404资源不存在，500服务器错误

## 4. 依赖添加

在`requirements.txt`中添加Pydantic依赖：
```
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

## 5. 实现步骤

1. 创建目录结构
2. 安装Pydantic依赖
3. 实现Pydantic模型
4. 实现API路由
5. 注册路由到主应用
6. 测试API功能

## 6. 预期效果

- 完整的RESTful API接口，支持所有detection模块的CRUD操作
- 严格的请求验证，确保数据完整性
- 清晰的错误信息，便于前端开发
- 模块化的代码结构，便于维护和扩展