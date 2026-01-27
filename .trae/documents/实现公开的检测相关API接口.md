## 实现计划

### 1. 创建路由文件
- 在 `app/routes/public/` 目录下创建 `detection.py` 文件
- 定义新的路由实例，用于处理公开的检测相关接口
- 在 `app/routes/public/__init__.py` 中注册该路由

### 2. 实现API接口

#### 接口1：获取所有分类列表
- **路径**：`GET /api/public/detection/categories`
- **功能**：获取所有状态为启用的分类（id和名称）列表，按排序号顺序返回
- **实现**：
  - 使用 `CategoryService` 获取所有分类
  - 过滤出 `status=1` 的数据
  - 按 `sort_order` 排序
  - 只返回 `category_id` 和 `category_name` 字段

#### 接口2：获取分类下的检测对象
- **路径**：`GET /api/public/detection/categories/{category_id}/objects`
- **功能**：获取指定ID分类下所有状态为启用的检测对象（id和名称）列表，按排序号顺序返回
- **实现**：
  - 使用 `DetectionObjectService` 获取指定分类下的检测对象
  - 过滤出 `status=1` 的数据
  - 按 `sort_order` 排序
  - 只返回 `object_id` 和 `object_name` 字段

#### 接口3：获取检测对象下的检测项目
- **路径**：`GET /api/public/detection/objects/{object_id}/items`
- **功能**：获取指定ID检测对象下所有状态为启用的检测项目（id和名称）列表，按排序号顺序返回
- **实现**：
  - 使用 `DetectionItemService` 获取指定检测对象下的检测项目
  - 过滤出 `status=1` 的数据
  - 按 `sort_order` 排序
  - 只返回 `item_id` 和 `item_name` 字段

#### 接口4：获取检测项目下的检测参数
- **路径**：`GET /api/public/detection/items/{item_id}/params`
- **功能**：获取指定ID检测项目下所有状态为启用的检测参数列表，包含详细信息
- **实现**：
  - 使用 `DetectionParamService` 获取指定检测项目下的检测参数
  - 过滤出 `status=1` 的数据
  - 按 `sort_order` 排序
  - 返回详细信息，包括：
    - ID、检测对象、项目名称、参数名称、价格、样品加工费
    - 组批规则、取样频率、取样要求、送检要求、所需信息、报告时间
    - 规范信息、常规参数、排序号、委托单模板下载链接

### 3. 服务层调整
- 检查现有服务层方法是否满足需求，如需调整则添加新方法
- 确保返回数据格式符合要求
- 处理数据关联关系，如检测参数与规范、模板的关联

### 4. 数据格式处理
- 确保返回数据符合用户要求的字段格式
- 处理日期时间格式，确保统一
- 构建正确的委托单模板下载链接

### 5. 测试
- 确保接口可以正常访问
- 验证返回数据格式和内容正确性
- 测试不同参数下的响应

## 代码风格
- 遵循项目现有代码风格和命名规范
- 添加详细的接口文档和注释
- 处理异常情况，返回友好的错误信息
- 使用现有的依赖注入和数据库连接方式

## 预计文件修改
1. `app/routes/public/__init__.py` - 注册新路由
2. `app/routes/public/detection.py` - 实现新的API接口
3. 可能需要调整相关服务层代码（如 `DetectionParamService`）以返回所需的详细信息