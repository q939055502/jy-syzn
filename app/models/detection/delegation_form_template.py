# 委托单模板表模型类
# 基于SQLAlchemy的ORM模型，用于表示检测行业委托单模板数据和与数据库的交互
# 主要用于管理供客户下载填写的委托单模板，关联检测项目组

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.extensions import Base


class DelegationFormTemplate(Base):
    """委托单模板表模型类，对应数据库中的delegation_form_template表
    
    该表用于管理检测行业委托单模板，供客户下载填写
    """
    # 表名
    __tablename__ = 'delegation_form_template'
    
    # 主键
    template_id = Column(Integer, primary_key=True, comment='模板ID，自增主键')
    
    # 模板核心信息字段（检测行业必备）
    template_name = Column(String(100), nullable=False, comment='模板名称（如：水泥物理性能检测委托单）')
    template_version = Column(String(20), nullable=False, default='V1.0', comment='模板版本（如V1.0、2025修订版）')
    template_code = Column(String(50), unique=True, nullable=True, comment='模板编号（唯一标识，如：SNT-2024-001）')
    
    # 文件下载核心字段
    file_type = Column(String(20), nullable=False, comment='文件类型（doc/docx/xls/xlsx）')
    
    # 管理字段（检测行业标准化）
    upload_time = Column(DateTime, default=datetime.utcnow, comment='模板上传时间')
    upload_user = Column(String(50), comment='上传人（管理员账号/名称）')
    status = Column(Integer, default=1, comment='状态：1=启用（可下载），0=禁用（下线）')
    remark = Column(String(500), comment='模板备注（如：适配GB 175-2024最新规范）')
    
    # 关系定义
    # 一个委托单模板可以被多个检测参数使用（多对一关系）
    params = relationship('DetectionParam', back_populates='template', lazy=True,
                        info={'comment': '使用该模板的所有检测参数'})
    
    def __repr__(self):
        """返回委托单模板对象的字符串表示
        
        :return: 包含模板名称和ID的字符串
        """
        return f"<DelegationFormTemplate {self.template_name} ({self.template_id})>"
    
    @property
    def file_path(self):
        """
        动态生成文件路径
        
        根据检测项目名称、模板名称、模板编号和文件类型生成统一的文件路径
        文件路径格式：/static/templates/delegation_form_templates/{模板名称}{模板编号}.{文件类型}
        """
        # 移除file_type中的点，因为这里会添加
        file_extension = self.file_type[1:] if self.file_type.startswith('.') else self.file_type
        return f"/static/templates/delegation_form_templates/{self.template_name}{self.template_code}.{file_extension}"
    
    def to_dict(self):
        """
        将委托单模板对象转换为字典，用于API响应
        
        :return: 包含委托单模板信息的字典
        """
        return {
            'template_id': self.template_id,
            'template_name': self.template_name,
            'template_version': self.template_version,
            'template_code': self.template_code,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'upload_user': self.upload_user,
            'status': self.status,
            'remark': self.remark
        }
