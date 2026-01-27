# 数据图片数据访问层
# 封装数据图片相关的数据库和Redis操作，确保数据一致性

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from redis import Redis
from app.models.image.data_image import DataImage
from app.dal.base_dal import BaseDAL


class DataImageDAL(BaseDAL):
    """数据图片数据访问层，处理数据图片相关的数据访问操作"""
    
    def __init__(self, db: Session, redis: Redis):
        super().__init__(db, redis, DataImage)
    
    def get_by_data_and_device(self, data_unique_id: str, device_type: str) -> Optional[DataImage]:
        """
        根据数据唯一标识和设备类型获取数据图片
        :param data_unique_id: 数据唯一标识
        :param device_type: 设备类型
        :return: 数据图片实例，不存在则返回None
        """
        instance = self.db.query(self.model).filter_by(
            data_unique_id=data_unique_id,
            device_type=device_type
        ).first()
        
        if instance:
            # 将数据存入缓存
            cache_key = f"data_img:{data_unique_id}:{device_type}"
            self.set_cache(cache_key, self._serialize_instance(instance))
        
        return instance
    
    def get_by_data_id(self, data_unique_id: str) -> List[DataImage]:
        """
        根据数据唯一标识获取所有设备类型的数据图片
        :param data_unique_id: 数据唯一标识
        :return: 数据图片实例列表
        """
        return self.db.query(self.model).filter_by(
            data_unique_id=data_unique_id
        ).all()
    
    def batch_update_by_data_id(self, data_unique_id: str, data_dict: Dict[str, any]) -> int:
        """
        根据数据唯一标识批量更新数据图片
        :param data_unique_id: 数据唯一标识
        :param data_dict: 要更新的数据字典
        :return: 更新的记录数
        """
        # 更新数据库
        result = self.db.query(self.model).filter_by(
            data_unique_id=data_unique_id
        ).update(data_dict)
        self.db.commit()
        
        # 清除相关缓存
        # 先获取所有设备类型，然后清除对应缓存
        device_types = self.db.query(self.model.device_type).filter_by(
            data_unique_id=data_unique_id
        ).distinct().all()
        
        for device_type in device_types:
            cache_key = f"data_img:{data_unique_id}:{device_type[0]}"
            self.delete_cache(cache_key)
        
        return result
    
    def delete_by_data_id(self, data_unique_id: str) -> int:
        """
        根据数据唯一标识删除所有设备类型的数据图片
        :param data_unique_id: 数据唯一标识
        :return: 删除的记录数
        """
        # 先获取所有设备类型，然后清除对应缓存
        device_types = self.db.query(self.model.device_type).filter_by(
            data_unique_id=data_unique_id
        ).distinct().all()
        
        for device_type in device_types:
            cache_key = f"data_img:{data_unique_id}:{device_type[0]}"
            self.delete_cache(cache_key)
        
        # 删除数据库中的记录
        result = self.db.query(self.model).filter_by(
            data_unique_id=data_unique_id
        ).delete()
        self.db.commit()
        
        return result
    
    def create(self, data: Dict[str, any]) -> DataImage:
        """
        创建新数据图片记录，重写父类方法，避免使用错误的主键字段名
        :param data: 数据字典
        :return: 创建的数据图片实例
        """
        # 直接创建实例
        instance = self.model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update(self, id: int, data: Dict[str, any]) -> DataImage:
        """
        更新数据图片记录，重写父类方法，避免使用错误的主键字段名
        :param id: 图片ID
        :param data: 数据字典
        :return: 更新的数据图片实例
        """
        # 直接查询实例
        instance = self.db.query(self.model).filter_by(image_id=id).first()
        if not instance:
            return None
        
        # 更新实例
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
