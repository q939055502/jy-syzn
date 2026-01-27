# 修复API文档与实际代码不符的问题

## 问题分析

通过对比 `API接口说明.md` 与实际代码，发现以下问题：

1. **委托单模板模型（DelegationFormTemplate）**：
   - 文档中包含 `applicable_scenario` 字段，但实际模型中不存在该字段
   - 文档缺少 `upload_time`、`remark` 等实际存在的字段
   - 文档显示 `file_path` 需在请求中提供，实际是动态生成的

2. **请求参数与响应字段不匹配**：
   - 文档中的请求/响应结构与实际代码不一致

## 修复计划

1. **更新 API接口说明.md**：
   - 删除模板相关接口中的 `applicable_scenario` 字段
   - 添加 `upload_time`、`remark` 等实际存在的字段
   - 修正请求/响应结构以匹配实际代码
   - 确保所有模板相关接口的描述准确反映实际实现

2. **更新模板相关的请求/响应示例**：
   - 修正模板列表获取接口的响应示例
   - 修正单个模板获取接口的响应示例
   - 修正模板创建接口的请求体和响应示例
   - 修正模板更新接口的请求体和响应示例

## 具体修改点

1. **模板列表获取接口（GET /api/detection/templates）**：
   - 删除响应中的 `applicable_scenario` 字段
   - 添加 `upload_time`、`remark` 字段

2. **单个模板获取接口（GET /api/detection/templates/{template_id}）**：
   - 删除响应中的 `applicable_scenario` 字段
   - 添加 `upload_time`、`remark` 字段

3. **创建模板接口（POST /api/detection/templates）**：
   - 删除请求体和响应中的 `applicable_scenario` 字段
   - 修正请求参数说明，移除 `applicable_scenario`
   - 添加 `upload_time` 到响应示例

4. **更新模板接口（PUT /api/detection/templates/{template_id}）**：
   - 删除请求体和响应中的 `applicable_scenario` 字段
   - 修正请求参数说明，移除 `applicable_scenario`

## 验证方法

- 检查修改后的 API文档 与实际代码模型匹配
- 确保所有模板相关接口描述准确反映实际实现
- 验证请求/响应示例与实际 API 行为一致