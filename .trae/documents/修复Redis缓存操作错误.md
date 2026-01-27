## 问题分析

1. **核心错误**：`Redis删除用户缓存失败: 'UserDAL' object has no attribute 'delete_cache'`

2. **根本原因**：
   - `UserDAL.invalidate_cache` 方法调用了 `self.delete_cache()`，但 `BaseDAL` 类中未定义此实例方法
   - `UserDAL.get_by_username` 方法调用了 `self.get_cache()` 和 `self.set_cache()`，同样未在 `BaseDAL` 中定义
   - `DetectionStandardDAL.get_by_status` 静态方法调用了 `self.get_by_condition()`，静态方法不能访问实例方法

3. **设计不一致**：
   - `BaseDAL` 类的其他方法（如 `create`、`update`、`delete`）直接使用 `RedisUtils` 静态方法
   - 但部分子类尝试使用实例方法访问缓存，导致属性错误

## 修复方案

### 1. 在 `BaseDAL` 中添加缓存实例方法

在 `app/dal/base_dal.py` 中添加以下实例方法：
- `get_cache(key: str) -> Optional[Any]`
- `set_cache(key: str, value: Any, expire: Optional[int] = None) -> bool`
- `delete_cache(key: str) -> bool`

这些方法内部调用 `RedisUtils` 静态方法，保持接口一致性。

### 2. 修复 `DetectionStandardDAL.get_by_status` 方法

将 `app/dal/detection_dal.py` 中的 `get_by_status` 方法从静态方法改为实例方法，或使用 `RedisUtils` 静态方法。

## 修复步骤

1. 修改 `app/dal/base_dal.py`，添加缓存实例方法
2. 修改 `app/dal/detection_dal.py`，修复静态方法错误
3. 重新启动服务器，验证修复效果

## 预期效果

- 修复 Redis 缓存操作错误
- 保持代码设计一致性
- 确保所有缓存操作正常工作
- 解决 500 Internal Server Error 问题