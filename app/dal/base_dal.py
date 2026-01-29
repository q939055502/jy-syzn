# 基础数据访问层
# 封装数据库和Redis操作，确保数据一致性

from typing import Any, Optional, Type, TypeVar, List, Dict
from sqlalchemy.orm import Session
from redis import Redis
from app.utils.redis_utils import RedisUtils


ModelType = TypeVar('ModelType')


class BaseDAL:
    """基础数据访问层，封装了MySQL和Redis操作"""
    
    def __init__(self, db: Session, redis: Redis, model: Type[ModelType]):
        """
        初始化DAL
        :param db: 数据库会话
        :param redis: Redis客户端
        :param model: 数据模型类
        """
        self.db = db
        self.redis = redis
        self.model = model
        # 缓存键前缀，使用模型名称
        self.cache_prefix = model.__name__.lower()
        # 默认缓存过期时间（秒）
        self.default_expire = 3600
    
    def _get_cache_key(self, id: Any) -> str:
        """
        生成带版本号的缓存键
        :param id: 数据ID
        :return: 带版本号的缓存键字符串
        """
        # 添加版本号v1，便于后续缓存结构变更时升级
        return f"{self.cache_prefix}:v1:{id}"
    
    def get_cache(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        :param key: 缓存键
        :return: 缓存值，不存在或解析失败返回None
        """
        try:
            return RedisUtils.get_cache(self.redis, key)
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
    
    def set_cache(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置缓存数据
        :param key: 缓存键
        :param value: 缓存值
        :param expire: 缓存过期时间（秒），默认使用类的默认值
        :return: 设置成功返回True，失败返回False
        """
        if expire is None:
            expire = self.default_expire
        
        try:
            return RedisUtils.set_cache(self.redis, key, value, expire)
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    def delete_cache(self, key: str) -> bool:
        """
        删除缓存数据
        :param key: 缓存键
        :return: 删除成功返回True，失败返回False
        """
        try:
            return RedisUtils.delete_cache(self.redis, key)
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False
    
    def _serialize_instance(self, instance: ModelType) -> dict:
        """
        将模型实例转换为可序列化的字典，排除SQLAlchemy内部属性
        :param instance: 模型实例
        :return: 可序列化的字典
        """
        # 排除SQLAlchemy内部状态属性
        return {k: v for k, v in instance.__dict__.items() if k != '_sa_instance_state'}
    
    def get_by_id(self, id: Any, cache_expire: Optional[int] = None) -> Optional[ModelType]:
        """
        根据ID获取数据，优先从缓存获取
        :param id: 数据ID
        :param cache_expire: 缓存过期时间（秒），默认使用类的默认值
        :return: 数据模型实例，不存在则返回None
        """
        if cache_expire is None:
            cache_expire = self.default_expire
        
        # 使用统一的方法获取ID字段名
        id_field = self._get_id_field_name()
        
        # 直接从数据库获取实例，确保实例与会话关联
        instance = self.db.query(self.model).filter_by(**{id_field: id}).first()
        
        if instance:
            # 将数据存入缓存，使用序列化方法排除内部属性
            cache_key = self._get_cache_key(id)
            RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
        
        return instance
    
    def get_all(self) -> List[ModelType]:
        """
        获取所有数据
        注意：此方法不使用缓存，因为数据量可能很大，且频繁变化
        :return: 数据模型实例列表
        """
        return self.db.query(self.model).all()
    
    def get_by_condition(self, condition: Dict[str, Any]) -> List[ModelType]:
        """
        根据条件获取数据
        注意：此方法不使用缓存，因为条件查询的结果可能多样
        :param condition: 查询条件字典
        :return: 数据模型实例列表
        """
        return self.db.query(self.model).filter_by(**condition).all()
    
    def _get_id_field_name(self) -> str:
        """
        获取模型的ID字段名
        :return: ID字段名字符串
        """
        # 根据模型类型确定ID字段名
        if self.model.__name__ == "DetectionItem":
            return "item_id"
        elif self.model.__name__ == "DetectionStandard":
            return "standard_id"
        elif self.model.__name__ == "DetectionParam":
            # DetectionParam模型使用"param_id"作为主键字段名
            return "param_id"
        elif self.model.__name__ == "DelegationFormTemplate":
            # DelegationFormTemplate模型使用"template_id"作为主键字段名
            return "template_id"
        elif self.model.__name__ == "DetectionObject":
            # DetectionObject模型使用"object_id"作为主键字段名
            return "object_id"
        elif self.model.__name__ == "Category":
            # Category模型使用"category_id"作为主键字段名
            return "category_id"
        elif self.model.__name__ == "User":
            # User模型使用"id"作为主键字段名
            return "id"
        elif self.model.__name__ == "DataImage":
            # DataImage模型使用"image_id"作为主键字段名
            return "image_id"
        else:
            # 默认使用类名小写+_id
            return f"{self.model.__name__.lower()}_id"
    
    def _get_instance_id(self, instance: ModelType) -> Any:
        """
        获取实例的ID值
        :param instance: 数据模型实例
        :return: ID值
        """
        id_field = self._get_id_field_name()
        return getattr(instance, id_field)
    
    def create(self, data: Dict[str, Any], cache_expire: Optional[int] = None) -> ModelType:
        """
        创建新数据，同时更新缓存
        :param data: 数据字典
        :param cache_expire: 缓存过期时间（秒），默认使用类的默认值
        :return: 数据模型实例
        """
        if cache_expire is None:
            cache_expire = self.default_expire
        
        # 创建模型实例
        instance = self.model(**data)
        
        # 保存到数据库
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        
        # 将数据存入缓存，使用序列化方法排除内部属性
        instance_id = self._get_instance_id(instance)
        cache_key = self._get_cache_key(instance_id)
        RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
        
        return instance
    
    def update(self, id: Any, data: Dict[str, Any], cache_expire: Optional[int] = None) -> Optional[ModelType]:
        """
        更新数据，同时更新缓存
        :param id: 数据ID
        :param data: 要更新的数据字典
        :param cache_expire: 缓存过期时间（秒），默认使用类的默认值
        :return: 更新后的数据模型实例，不存在则返回None
        """
        if cache_expire is None:
            cache_expire = self.default_expire
        
        # 获取数据实例
        instance = self.get_by_id(id)
        if not instance:
            return None
        
        # 更新实例属性
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        # 保存到数据库
        self.db.commit()
        self.db.refresh(instance)
        
        # 更新缓存，使用序列化方法排除内部属性
        cache_key = self._get_cache_key(id)
        RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
        
        return instance
    
    def delete(self, id: Any) -> bool:
        """
        删除数据，同时删除缓存
        :param id: 数据ID
        :return: 删除成功返回True，失败返回False
        """
        # 获取数据实例
        instance = self.get_by_id(id)
        if not instance:
            return False
        
        # 删除缓存
        cache_key = self._get_cache_key(id)
        RedisUtils.delete_cache(self.redis, cache_key)
        
        # 删除数据库中的数据
        self.db.delete(instance)
        self.db.commit()
        
        return True
    
    def save(self, instance: ModelType, cache_expire: Optional[int] = None) -> ModelType:
        """
        保存数据实例，同时更新缓存
        :param instance: 数据模型实例
        :param cache_expire: 缓存过期时间（秒），默认使用类的默认值
        :return: 保存后的数据模型实例
        """
        if cache_expire is None:
            cache_expire = self.default_expire
        
        # 保存到数据库
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        
        # 更新缓存，使用序列化方法排除内部属性
        instance_id = self._get_instance_id(instance)
        cache_key = self._get_cache_key(instance_id)
        RedisUtils.set_cache(self.redis, cache_key, self._serialize_instance(instance), expire=cache_expire)
        
        return instance
    
    def batch_create(self, data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量创建数据
        注意：此方法不使用缓存，因为批量操作的数据量可能很大
        :param data_list: 数据字典列表
        :return: 创建的数据模型实例列表
        """
        instances = [self.model(**data) for data in data_list]
        self.db.add_all(instances)
        self.db.commit()
        return instances
    
    def count(self, condition: Optional[Dict[str, Any]] = None) -> int:
        """
        统计数据数量
        注意：此方法不使用缓存，因为数量可能频繁变化
        :param condition: 查询条件字典，默认统计所有数据
        :return: 数据数量
        """
        if condition:
            return self.db.query(self.model).filter_by(**condition).count()
        return self.db.query(self.model).count()
    
    def search(self, search_params: Dict[str, Any], fuzzy_fields: Optional[List[str]] = None, related_fields: Optional[Dict[str, Any]] = None) -> List[ModelType]:
        """
        根据搜索参数进行模糊搜索
        :param search_params: 搜索参数字典，键为字段名，值为搜索关键词
        :param fuzzy_fields: 需要进行模糊搜索的字段列表
        :param related_fields: 关联表搜索配置，键为关联属性名，值为关联表搜索字段配置
        :return: 搜索结果列表
        """
        from sqlalchemy import or_
        
        query = self.db.query(self.model)
        conditions = []
        
        # 处理模糊搜索字段
        if fuzzy_fields:
            for field in fuzzy_fields:
                if field in search_params and search_params[field]:
                    # 直接字段模糊搜索
                    conditions.append(getattr(self.model, field).ilike(f"%{search_params[field]}%"))
        
        # 处理关联表搜索
        if related_fields:
            for relation_name, related_config in related_fields.items():
                if hasattr(self.model, relation_name):
                    relation = getattr(self.model, relation_name)
                    related_field = related_config.get('field')
                    related_search_value = search_params.get(related_config.get('search_key'))
                    
                    if related_field and related_search_value:
                        # 关联表字段模糊搜索
                        conditions.append(getattr(relation, related_field).ilike(f"%{related_search_value}%"))
        
        # 处理精确匹配字段
        for field, value in search_params.items():
            # 如果字段不在模糊搜索列表中，也不在关联表搜索配置中，则进行精确匹配
            if value and field not in (fuzzy_fields or []) and field not in (related_fields or {}).keys():
                if hasattr(self.model, field):
                    conditions.append(getattr(self.model, field) == value)
        
        if conditions:
            query = query.filter(or_(*conditions))
        
        return query.all()
