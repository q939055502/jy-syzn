# 角色服务类
# 包含角色相关的业务逻辑，如获取角色信息、创建角色、更新角色、删除角色等

from typing import List, Optional
from app.models.user.role import Role
from app.models.user.permission import Permission
from app.extensions import get_db


class RoleService:
    """角色服务类，处理角色相关的业务逻辑"""
    
    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[Role]:
        """
        根据角色ID获取角色信息
        :param role_id: 角色ID
        :return: 角色对象或None
        """
        # 获取数据库会话
        db = next(get_db())
        return db.query(Role).filter_by(id=role_id).first()
    
    @staticmethod
    def get_role_by_name(name: str) -> Optional[Role]:
        """
        根据角色名称获取角色信息
        :param name: 角色名称
        :return: 角色对象或None
        """
        # 获取数据库会话
        db = next(get_db())
        return db.query(Role).filter_by(name=name).first()
    
    @staticmethod
    def create_role(role_name: str, permissions: list, description: Optional[str] = None, parent_id: Optional[int] = None) -> Optional[Role]:
        """
        创建新角色
        :param role_name: 角色名称
        :param permissions: 权限列表
        :param description: 角色描述
        :param parent_id: 父角色ID
        :return: 创建的角色对象或None
        """
        # 获取数据库会话
        db = next(get_db())
        
        # 检查角色名称是否已存在
        existing_role = RoleService.get_role_by_name(role_name)
        if existing_role:
            print(f"角色名称 '{role_name}' 已存在")
            return None
        
        # 创建新角色对象
        new_role = Role(name=role_name, description=description, parent_id=parent_id)
        
        try:
            # 将角色添加到数据库会话
            db.add(new_role)
            db.flush()  # 刷新会话以获取角色ID
            
            # 添加权限
            if permissions:
                for perm_code in permissions:
                    permission = db.query(Permission).filter_by(code=perm_code).first()
                    if permission:
                        new_role.permissions.append(permission)
            
            # 提交事务
            db.commit()
            # 刷新会话以获取最新的角色数据
            db.refresh(new_role)
            return new_role
        except Exception as e:
            # 发生异常时回滚会话
            db.rollback()
            print(f"创建角色失败: {str(e)}")
            return None
    
    @staticmethod
    def update_role(role_id: int, **kwargs) -> Optional[Role]:
        """
        更新角色信息
        :param role_id: 角色ID
        :param kwargs: 要更新的角色信息，可能包含role_name和permissions
        :return: 更新后的角色对象或None
        """
        # 获取数据库会话
        db = next(get_db())
        
        # 在当前会话中获取角色
        role = db.query(Role).filter_by(id=role_id).first()
        
        if not role:
            return None
        
        try:
            # 处理角色名称更新
            if 'role_name' in kwargs and kwargs['role_name']:
                # 检查新名称是否已存在
                existing_role = RoleService.get_role_by_name(kwargs['role_name'])
                if existing_role and existing_role.id != role_id:
                    print(f"角色名称 '{kwargs['role_name']}' 已存在")
                    return None
                role.name = kwargs['role_name']
            
            # 处理角色描述更新
            if 'description' in kwargs:
                role.description = kwargs['description']
            
            # 处理父角色ID更新
            if 'parent_id' in kwargs:
                role.parent_id = kwargs['parent_id']
            
            # 处理权限更新
            if 'permissions' in kwargs and kwargs['permissions']:
                # 清空现有权限
                role.permissions.clear()
                
                # 添加新权限
                for perm_code in kwargs['permissions']:
                    permission = db.query(Permission).filter_by(code=perm_code).first()
                    if permission:
                        role.permissions.append(permission)
            
            # 提交事务
            db.commit()
            # 刷新会话以获取最新的角色数据
            db.refresh(role)
            return role
        except Exception as e:
            # 发生异常时回滚会话
            db.rollback()
            print(f"更新角色失败: {str(e)}")
            return None
    
    @staticmethod
    def delete_role(role_id: int) -> bool:
        """
        删除角色
        :param role_id: 角色ID
        :return: 是否删除成功
        """
        # 获取数据库会话
        db = next(get_db())
        
        # 在当前会话中获取角色
        role = db.query(Role).filter_by(id=role_id).first()
        
        if not role:
            return False
        
        try:
            # 删除角色
            db.delete(role)
            # 提交事务
            db.commit()
            return True
        except Exception as e:
            # 发生异常时回滚会话
            db.rollback()
            print(f"删除角色失败: {str(e)}")
            return False
    
    @staticmethod
    def toggle_role_active(role_id: int, is_active: bool) -> Optional[Role]:
        """
        激活或停用角色
        :param role_id: 角色ID
        :param is_active: 要设置的状态
        :return: 更新后的角色对象或None
        """
        return RoleService.update_role(role_id, is_active=is_active)
    
    @staticmethod
    def get_roles(skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[Role]:
        """
        获取角色列表
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :param is_active: 可选的角色状态过滤
        :return: 角色对象列表
        """
        # 获取数据库会话
        db = next(get_db())
        
        query = db.query(Role)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def add_permission_to_role(role_id: int, permission_id: int) -> bool:
        """
        为角色添加权限
        :param role_id: 角色ID
        :param permission_id: 权限ID
        :return: 是否添加成功
        """
        # 获取数据库会话
        db = next(get_db())
        
        # 在当前会话中获取角色和权限
        role = db.query(Role).filter_by(id=role_id).first()
        if not role:
            print(f"角色ID {role_id} 不存在")
            return False
        
        permission = db.query(Permission).filter_by(id=permission_id).first()
        if not permission:
            print(f"权限ID {permission_id} 不存在")
            return False
        
        # 检查权限是否已存在于角色中
        if permission in role.permissions:
            print(f"角色已拥有该权限")
            return True
        
        try:
            # 为角色添加权限
            role.permissions.append(permission)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"为角色添加权限失败: {str(e)}")
            return False
    
    @staticmethod
    def remove_permission_from_role(role_id: int, permission_id: int) -> bool:
        """
        从角色移除权限
        :param role_id: 角色ID
        :param permission_id: 权限ID
        :return: 是否移除成功
        """
        # 获取数据库会话
        db = next(get_db())
        
        # 在当前会话中获取角色和权限
        role = db.query(Role).filter_by(id=role_id).first()
        if not role:
            print(f"角色ID {role_id} 不存在")
            return False
        
        permission = db.query(Permission).filter_by(id=permission_id).first()
        if not permission:
            print(f"权限ID {permission_id} 不存在")
            return False
        
        # 检查权限是否存在于角色中
        if permission not in role.permissions:
            print(f"角色不拥有该权限")
            return True
        
        try:
            # 从角色移除权限
            role.permissions.remove(permission)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"从角色移除权限失败: {str(e)}")
            return False
    
    @staticmethod
    def get_role_permissions(role_id: int) -> Optional[List[Permission]]:
        """
        获取角色的所有权限
        :param role_id: 角色ID
        :return: 权限对象列表或None
        """
        role = RoleService.get_role_by_id(role_id)
        if role:
            return list(role.get_all_permissions())
        return None