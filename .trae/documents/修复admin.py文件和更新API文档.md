## 1. 修复admin.py文件中的问题

### 1.1 修复导入错误
- 将`ResponseModel`的导入从`app.schemas.detection`改为正确的导入路径

### 1.2 修复权限检查逻辑
- 检查`get_current_admin`函数中的权限检查逻辑，确保正确判断管理员权限

### 1.3 修复UserAdminService方法调用
- 检查`create_user`、`update_user`等方法的参数，确保调用正确

### 1.4 修复返回格式问题
- 修复`get_user`函数中`user.dict()`的调用，因为`user`是字典而不是Pydantic模型

### 1.5 修复角色管理接口
- 检查并修复角色管理相关接口的参数和返回格式

## 2. 更新API_DOCUMENTATION.md文件

### 2.1 更新用户管理接口
- 移除UserResponse模型中多余的`email`和`role`字段
- 添加`is_online`字段，用于显示用户在线状态

### 2.2 更新检测项目相关接口
- 添加`is_regular_param`字段到检测项目响应格式
- 添加`sample_image_path`和`sample_video_path`字段到检测指南响应格式

### 2.3 添加新接口描述
- 添加`sample-rules`接口的描述
- 添加`calculate-batches`接口的描述
- 添加`sampling-requirements`接口的描述

### 2.4 修复文档中的其他错误
- 修复请求示例中的错误
- 修复响应格式中的错误

## 3. 验证修复
- 运行测试脚本，确保所有接口正常工作
- 检查API文档，确保所有接口描述正确

## 4. 注意事项
- 保持代码风格一致
- 确保接口描述与实际代码一致
- 确保文档更新后准确反映当前系统状态