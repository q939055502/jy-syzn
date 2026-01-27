# API权限服务类
# 包含API权限相关的业务逻辑，如获取API权限信息、创建API权限绑定、更新API权限、删除API权限等

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user.api_permission import ApiPermission
from app.models.user.permission import Permission
from app.extensions import get_db


class ApiPermissionService:
    """API权限服务类，处理API权限相关的业务逻辑"""
    
    @staticmethod
    def get_api_permission_by_id(db: Session, api_permission_id: int) -> Optional[ApiPermission]:
        """
        根据API权限ID获取API权限信息
        :param db: 数据库会话对象
        :param api_permission_id: API权限ID
        :return: API权限对象或None
        """
        return db.query(ApiPermission).filter(ApiPermission.id == api_permission_id).first()
    
    @staticmethod
    def get_api_permissions(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[ApiPermission]:
        """
        获取API权限列表
        :param db: 数据库会话对象
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :param is_active: 可选的API权限状态过滤
        :return: API权限对象列表
        """
        query = db.query(ApiPermission)
        if is_active is not None:
            query = query.filter(ApiPermission.is_active == is_active)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_api_permissions_by_path(db: Session, path: str, is_active: Optional[bool] = None) -> List[ApiPermission]:
        """
        根据API路径获取API权限列表
        :param db: 数据库会话对象
        :param path: API路径
        :param is_active: 可选的API权限状态过滤
        :return: API权限对象列表
        """
        query = db.query(ApiPermission).filter(ApiPermission.path == path)
        if is_active is not None:
            query = query.filter(ApiPermission.is_active == is_active)
        return query.all()
    
    @staticmethod
    def get_api_permissions_by_method(db: Session, method: str, is_active: Optional[bool] = None) -> List[ApiPermission]:
        """
        根据API方法获取API权限列表
        :param db: 数据库会话对象
        :param method: API方法（如GET、POST等）
        :param is_active: 可选的API权限状态过滤
        :return: API权限对象列表
        """
        query = db.query(ApiPermission).filter(ApiPermission.method == method)
        if is_active is not None:
            query = query.filter(ApiPermission.is_active == is_active)
        return query.all()
    
    @staticmethod
    def get_api_permissions_by_permission(db: Session, permission_id: int, is_active: Optional[bool] = None) -> List[ApiPermission]:
        """
        根据权限ID获取API权限列表
        :param db: 数据库会话对象
        :param permission_id: 权限ID
        :param is_active: 可选的API权限状态过滤
        :return: API权限对象列表
        """
        query = db.query(ApiPermission).filter(ApiPermission.permission_id == permission_id)
        if is_active is not None:
            query = query.filter(ApiPermission.is_active == is_active)
        return query.all()
    
    @staticmethod
    def get_permission_by_api(db: Session, path: str, method: str) -> Optional[Permission]:
        """
        根据API路径和方法获取关联的权限
        :param db: 数据库会话对象
        :param path: API路径
        :param method: API方法
        :return: 关联的权限对象或None
        """
        api_permission = db.query(ApiPermission).filter_by(
            path=path, method=method, is_active=True
        ).first()
        return api_permission.permission if api_permission else None
    
    @staticmethod
    def create_api_permission(db: Session, path: str, method: str, permission_id: int, description: Optional[str] = None, is_active: bool = True) -> Optional[ApiPermission]:
        """
        创建新的API权限绑定
        :param db: 数据库会话对象
        :param path: API路径
        :param method: API方法
        :param permission_id: 权限ID
        :param description: API描述
        :param is_active: 是否启用
        :return: 创建的API权限对象或None
        """
        try:
            return ApiPermission.create_api_permission(
                path=path, 
                method=method, 
                permission_id=permission_id, 
                description=description, 
                is_active=is_active, 
                db=db, 
                commit=True
            )
        except Exception as e:
            print(f"创建API权限绑定失败: {str(e)}")
            return None
    
    @staticmethod
    def update_api_permission(db: Session, api_permission_id: int, **kwargs) -> Optional[ApiPermission]:
        """
        更新API权限信息
        :param db: 数据库会话对象
        :param api_permission_id: API权限ID
        :param kwargs: 要更新的API权限信息
        :return: 更新后的API权限对象或None
        """
        api_permission = ApiPermissionService.get_api_permission_by_id(db, api_permission_id)
        if not api_permission:
            return None
        
        try:
            # 更新API权限属性
            for key, value in kwargs.items():
                if hasattr(api_permission, key):
                    setattr(api_permission, key, value)
            
            db.commit()
            db.refresh(api_permission)
            return api_permission
        except Exception as e:
            db.rollback()
            print(f"更新API权限失败: {str(e)}")
            return None
    
    @staticmethod
    def delete_api_permission(db: Session, api_permission_id: int) -> bool:
        """
        删除API权限
        :param db: 数据库会话对象
        :param api_permission_id: API权限ID
        :return: 是否删除成功
        """
        api_permission = ApiPermissionService.get_api_permission_by_id(db, api_permission_id)
        if not api_permission:
            return False
        
        try:
            db.delete(api_permission)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"删除API权限失败: {str(e)}")
            return False
    
    @staticmethod
    def toggle_api_permission_active(db: Session, api_permission_id: int, is_active: bool) -> Optional[ApiPermission]:
        """
        激活或停用API权限
        :param db: 数据库会话对象
        :param api_permission_id: API权限ID
        :param is_active: 要设置的状态
        :return: 更新后的API权限对象或None
        """
        return ApiPermissionService.update_api_permission(db, api_permission_id, is_active=is_active)
    
    @staticmethod
    def bind_permission_to_api(db: Session, path: str, method: str, permission_id: int, description: Optional[str] = None) -> Optional[ApiPermission]:
        """
        为API绑定权限（如果已存在则更新）
        :param db: 数据库会话对象
        :param path: API路径
        :param method: API方法
        :param permission_id: 权限ID
        :param description: API描述
        :return: 创建或更新后的API权限对象或None
        """
        # 检查是否已存在该API的权限绑定
        existing_api_permission = db.query(ApiPermission).filter_by(
            path=path, method=method
        ).first()
        
        if existing_api_permission:
            # 更新现有绑定
            return ApiPermissionService.update_api_permission(
                db, 
                existing_api_permission.id, 
                permission_id=permission_id, 
                description=description, 
                is_active=True
            )
        else:
            # 创建新绑定
            return ApiPermissionService.create_api_permission(
                db, 
                path=path, 
                method=method, 
                permission_id=permission_id, 
                description=description, 
                is_active=True
            )
    
    @staticmethod
    def unbind_permission_from_api(db: Session, path: str, method: str) -> bool:
        """
        解除API的权限绑定（停用绑定）
        :param db: 数据库会话对象
        :param path: API路径
        :param method: API方法
        :return: 是否解除成功
        """
        api_permission = db.query(ApiPermission).filter_by(
            path=path, method=method
        ).first()
        
        if api_permission:
            return ApiPermissionService.toggle_api_permission_active(db, api_permission.id, False) is not None
        return False
    
    @staticmethod
    def check_api_permission(db: Session, path: str, method: str, required_permission_code: str) -> bool:
        """
        检查API是否需要特定权限
        :param db: 数据库会话对象
        :param path: API路径
        :param method: API方法
        :param required_permission_code: 所需权限代码
        :return: 是否需要该权限
        """
        permission = ApiPermissionService.get_permission_by_api(db, path, method)
        return permission is not None and permission.code == required_permission_code
    
    @staticmethod
    def is_api_public(db: Session, path: str, method: str) -> bool:
        """
        检查API是否为公开（不需要权限验证）
        :param db: 数据库会话对象
        :param path: API路径
        :param method: API方法
        :return: 是否为公开API
        """
        # 如果API没有绑定任何权限，或者绑定的权限已停用，则视为公开API
        api_permission = db.query(ApiPermission).filter_by(
            path=path, method=method
        ).first()
        return api_permission is None or not api_permission.is_active
