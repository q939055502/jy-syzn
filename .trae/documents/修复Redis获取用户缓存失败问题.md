# 修复Redis获取用户缓存失败问题

## 问题分析

Redis获取用户缓存失败，错误信息为：`'_sa_instance_state' is an invalid keyword argument for User`

**根本原因**：在将对象保存到Redis缓存时，直接使用了`instance.__dict__`，这包含了SQLAlchemy的内部状态属性`_sa_instance_state`。当从缓存读取数据并尝试创建对象时，这个内部属性被传递给构造函数，导致错误。

## 修复方案

在BaseDAL类中添加一个`_serialize_instance`辅助方法，用于将对象转换为可序列化的字典，排除SQLAlchemy内部属性。然后修改所有保存缓存的地方，使用这个新方法。

## 修复步骤

### 1. 添加序列化辅助方法

在BaseDAL类中添加`_serialize_instance`方法，用于将对象转换为可序列化的字典，排除`_sa_instance_state`属性。

### 2. 修改BaseDAL中的缓存保存代码

修改以下方法中保存缓存的代码：
- `get_by_id`：第148行
- `create`：第195行
- `update`：第226行
- `save`：第269行

### 3. 修改UserDAL中的缓存保存代码

修改`UserDAL.get_by_username`方法中保存缓存的代码（第48-50行）。

## 具体修改点

### 文件：`app/dal/base_dal.py`

1. **添加`_serialize_instance`方法**：
```python
def _serialize_instance(self, instance: ModelType) -> dict:
    """
    将模型实例转换为可序列化的字典，排除SQLAlchemy内部属性
    :param instance: 模型实例
    :return: 可序列化的字典
    """
    # 排除SQLAlchemy内部状态属性
    return {k: v for k, v in instance.__dict__.items() if k != '_sa_instance_state'}
```

2. **修改`get_by_id`方法**：
```python
# 原代码
RedisUtils.set_cache(self.redis, cache_key, instance.__dict__, expire=cache_expire)

# 修改后
RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
```

3. **修改`create`方法**：
```python
# 原代码
RedisUtils.set_cache(self.redis, cache_key, instance.__dict__, expire=cache_expire)

# 修改后
RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
```

4. **修改`update`方法**：
```python
# 原代码
RedisUtils.set_cache(self.redis, cache_key, instance.__dict__, expire=cache_expire)

# 修改后
RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
```

5. **修改`save`方法**：
```python
# 原代码
RedisUtils.set_cache(self.redis, cache_key, instance.__dict__, expire=cache_expire)

# 修改后
RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
```

### 文件：`app/dal/user_dal.py`

**修改`get_by_username`方法**：
```python
# 原代码
self.set_cache(self._get_cache_key(instance.id), instance.__dict__)
self.set_cache(username_cache_key, instance.__dict__)

# 修改后
self.set_cache(self._get_cache_key(instance.id), self._serialize_instance(instance))
self.set_cache(username_cache_key, self._serialize_instance(instance))
```

## 预期效果

- 修复Redis获取用户缓存失败的问题
- 确保所有模型类都能正确地序列化到Redis缓存
- 提高缓存命中率，减少数据库查询压力
- 提升系统性能

## 测试验证

1. 启动应用
2. 登录系统
3. 查看Redis缓存中是否有用户信息
4. 多次访问需要认证的接口，查看日志中是否还有Redis获取缓存失败的错误

## 风险评估

- 低风险：修改仅影响缓存序列化，不影响核心业务逻辑
- 回退简单：如果出现问题，只需恢复原代码即可
- 兼容性好：不改变现有API和数据结构