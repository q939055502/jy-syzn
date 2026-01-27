## 任务概述
移除`DetectionObject`模型中的`object_type`属性，并更新所有相关代码和文档。

## 执行步骤

### 1. 修改检测对象模型
- **文件**：`app/models/detection/detection_object.py`
- **操作**：
  - 移除第25行的`object_type`字段定义
  - 从第65行的`to_dict()`方法中移除`object_type`返回项

### 2. 更新数据模式
- **文件**：`app/schemas/detection.py`
- **操作**：
  - 从第81行的`DetectionObjectBase`类中移除`object_type`字段

### 3. 更新服务层代码
- **文件**：`app/services/detection/detection_object_service.py`
  - 移除所有对`object_type`属性的引用
- **文件**：`app/services/detection/detection_item_service.py`
  - 移除所有对`object_type`属性的引用

### 4. 更新初始化脚本
- **文件**：`script/init_all.py`
- **操作**：
  - 从第431、437、443、449行的检测对象数据中移除`object_type`键值对
  - 从第459行的`DetectionObject`构造函数中移除`object_type`参数

### 5. 更新模型说明文档
- **文件**：`app/models/模型说明.md`
- **操作**：
  - 从第236行的示例代码中移除`object_type`属性

### 6. 执行初始化脚本
- **命令**：`python script/init_all.py`
- **目的**：
  - 删除现有数据库并重新创建
  - 执行所有模型迁移
  - 写入初始化数据

## 预期结果
- 成功移除`DetectionObject`模型的`object_type`属性
- 所有相关代码和文档已更新
- 初始化脚本执行成功，数据库表结构和数据正确
- 系统功能正常运行，无相关错误

## 注意事项
- 需仔细检查所有服务层代码，确保移除所有`object_type`引用
- 初始化脚本会删除现有数据库，执行前需确认数据备份
- 执行过程中如遇错误，需根据错误信息调整代码并重新执行