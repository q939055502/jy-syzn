# 检测项目表模型类
# 基于SQLAlchemy的ORM模型，用于表示检测项目数据和与数据库的交互
# 主要用于管理相关检测参数的分组，是连接分类、规范和具体检测参数的核心表

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.extensions import Base


class DetectionItem(Base):
    """检测项目表模型类，对应数据库中的detection_item表
    
    该表是核心关联表，连接分类、规范和具体检测参数，用于管理相关检测参数的分组
    """
    # 表名
    __tablename__ = 'detection_item'
    
    # 主键
    item_id = Column(Integer, primary_key=True, comment='项目ID，主键')
    
    # 外键
    object_id = Column(Integer, ForeignKey('detection_object.object_id'), nullable=False,
                        comment='检测对象ID，关联到detection_object表')
    
    # 基本信息
    item_name = Column(String(255), nullable=False, comment='项目名称')
    description = Column(String(255), nullable=True, comment='项目描述，用于说明项目的用途和范围')
    sort_order = Column(Integer, default=0, comment='排序序号，用于控制显示顺序')
    status = Column(Integer, default=1, comment='状态：1=启用，0=禁用')
    
    # 唯一约束：同一检测对象下项目名称唯一
    __table_args__ = (
        UniqueConstraint('item_name', 'object_id', name='_item_name_object_uc'),
    )
    
    # 时间戳
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    # 一个检测项目属于一个检测对象
    detection_object = relationship('DetectionObject', back_populates='detection_items',
                          info={'comment': '所属检测对象'})
    
    # 一个检测项目包含多个检测参数
    detection_params = relationship('DetectionParam', back_populates='item', lazy=True,
                                  info={'comment': '项目包含的所有检测参数'})
    

    
    def __repr__(self):
        """返回检测项目对象的字符串表示
        
        :return: 包含项目名称和ID的字符串
        """
        return f"<DetectionItem {self.item_name} ({self.item_id})>"
    
    def to_dict(self):
        """
        将检测项目对象转换为字典，用于API响应
        
        :return: 包含检测项目信息的字典
        """
        return {
            'item_id': self.item_id,
            'object_id': self.object_id,
            'item_name': self.item_name,
            'description': self.description,
            'sort_order': self.sort_order,
            'status': self.status,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }