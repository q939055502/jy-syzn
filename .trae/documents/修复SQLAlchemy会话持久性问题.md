## 问题分析

### 用户问题

1. 组批计算和送检要求计算是否是同一接口？
2. 每次请求是否使用新的数据库链接查询？

### 回答

1. **组批计算和送检要求计算是两个独立的接口**：

   * 组批计算：`POST /api/detection/calculate-batches`

   * 送检要求计算：`POST /api/detection/sampling-requirements`

2. **每次请求使用新的数据库会话**：

   * 所有路由函数依赖于 `get_db_and_redis` 生成器函数

   * 每次调用都会创建新的数据库会话

   * 路由执行完毕后，会话通过 `finally` 块关闭

### 根本问题

**序列化时机问题**：

* FastAPI 在路由函数返回后进行响应模型序列化

* 当序列化尝试访问关联属性（如 `item.guides`）时，数据库会话已关闭

* 导致 `Instance is not persistent within this Session` 错误

### 解决方案

保留response\_model，提前完成 ORM 实例序列化（最优解）

**修改所有检测相关路由，直接返回字典数据**：

1. **修改** **`sample-rules`** **路由**

   * 移除 `response_model` 参数，直接返回字典

   * 在会话关闭前完成所有数据处理

   * 将结果转换为普通 Python 数据结构

2. **修改** **`calculate-batches`** **路由**

   * 移除 `response_model` 参数，直接返回字典

   * 在会话关闭前完成所有数据处理

   * 将结果转换为普通 Python 数据结构

3. **修改** **`sampling-requirements`** **路由**

   * 移除 `response_model` 参数，直接返回字典

   * 在会话关闭前完成所有数据处理

   * 将结果转换为普通 Python 数据结构

### 实施步骤

1. **修改** **`app/routes/detection.py`** **中的** **`sample-rules`** **路由**

   * 移除 `response_model` 参数

   * 直接返回字典数据结构

2. **修改** **`app/routes/detection.py`** **中的** **`calculate-batches`** **路由**

   * 移除 `response_model` 参数

   * 直接返回字典数据结构

3. **修改** **`app/routes/detection.py`** **中的** **`sampling-requirements`** **路由**

   * 移除 `response_model` 参数

   * 直接返回字典数据结构

4. **创建新的测试脚本，验证修复效果**

### 预期效果

* 所有路由不再返回数据库模型实例

* 避免在会话关闭后访问关联属性

* 消除 `Instance is not persistent within this Session` 错误

* 所有测试用例通过

  <br />

