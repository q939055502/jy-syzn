# 修复Redis缓存数据问题

## 问题描述
Redis获取用户缓存失败，错误信息为：'str' object has no attribute '_sa_instance_state'

## 根本原因
- 旧代码直接使用`instance.__dict__`序列化对象，包含了SQLAlchemy的内部属性`_sa_instance_state`
- 新代码无法正确处理这些旧数据

## 修复方案

### 1. 清理Redis中的旧缓存数据
使用PowerShell命令清理所有用户相关的缓存数据：
```powershell
$keys = redis-cli keys "user:*"
foreach ($key in $keys) {
    if ($key) {
        redis-cli del $key
    }
}
```

### 2. 修改代码，添加对旧数据的兼容处理
在BaseDAL类的get_by_id方法中添加对`_sa_instance_state`属性的过滤：
```python
if cached_data:
    # 过滤掉_sa_instance_state属性，处理旧缓存数据
    if isinstance(cached_data, dict):
        cached_data = {k: v for k, v in cached_data.items() if k != '_sa_instance_state'}
    # 从缓存数据创建模型实例
    instance = self.model(**cached_data)
    # 将实例附加到会话，确保实例是数据库会话的一部分
    self.db.add(instance)
    self.db.refresh(instance)
    return instance
```

### 3. 添加缓存版本控制
在BaseDAL类中添加缓存版本号，确保新代码只使用新版本的缓存：
```python
def _get_cache_key(self, id: Any) -> str:
    """
    生成带版本号的缓存键
    :param id: 数据ID
    :return: 带版本号的缓存键字符串
    """
    return f"{self.cache_prefix}:v1:{id}"
```

## 预期效果
- 清理旧缓存数据，消除现有错误
- 添加兼容处理，防止类似问题再次发生
- 添加版本控制，提高系统的健壮性和可维护性

## 执行顺序
1. 退出Plan mode
2. 清理Redis缓存
3. 修改BaseDAL类，添加兼容处理
4. 修改BaseDAL类，添加缓存版本控制
5. 测试修复效果