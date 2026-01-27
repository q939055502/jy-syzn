# 检测规范表模型类
# 基于SQLAlchemy的ORM模型，用于表示检测规范数据和与数据库的交互
# 主要用于管理检测项目所依据的标准规范信息

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base


class DetectionStandard(Base):
    """检测规范表模型类，对应数据库中的detection_standard表
    
    该表用于管理检测项目所依据的标准规范信息，如国家标准、行业标准等
    """
    # 表名
    __tablename__ = 'detection_standard'
    
    # 主键
    standard_id = Column(Integer, primary_key=True, comment='规范ID，主键')
    
    # 基本信息
    standard_code = Column(String(100), nullable=False, unique=True, comment='规范编号，如GB/T 10001.1')
    standard_name = Column(String(255), nullable=False, comment='规范名称')
    standard_type = Column(String(50), nullable=True, comment='规范类型，如国家标准、行业标准等')
    effective_time = Column(Date, nullable=True, comment='生效日期')
    invalid_time = Column(Date, nullable=True, comment='失效日期')
    status = Column(Integer, default=1, comment='状态：1=有效，0=作废，2=待生效')
    replace_id = Column(Integer, ForeignKey('detection_standard.standard_id'), nullable=True, comment='替代的规范ID')
    remark = Column(Text, nullable=True, comment='备注信息')
    
    # 时间戳
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    # 自引用关系，用于表示规范的替代关系
    replace_standard = relationship('DetectionStandard', remote_side=[standard_id],backref='replaced_by', lazy=True, info={'comment': '被替代的规范'})
    
    # 多对多关系：一个检测规范可以被多个检测参数使用
    params = relationship('DetectionParam', secondary='detection_param_standard',
                        back_populates='standards', lazy=True,
                        info={'comment': '使用该规范的所有检测参数'})
    
    def __repr__(self):
        """返回检测规范对象的字符串表示
        
        :return: 包含规范编号和ID的字符串
        """
        return f"<DetectionStandard {self.standard_code} ({self.standard_id})>"
    
    def to_dict(self):
        """
        将检测规范对象转换为字典，用于API响应
        
        :return: 包含检测规范信息的字典
        """
        return {
            'standard_id': self.standard_id,
            'standard_code': self.standard_code,
            'standard_name': self.standard_name,
            'standard_type': self.standard_type,
            'effective_time': self.effective_time.isoformat() if self.effective_time else None,
            'invalid_time': self.invalid_time.isoformat() if self.invalid_time else None,
            'status': self.status,
            'replace_id': self.replace_id,
            'remark': self.remark,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }
