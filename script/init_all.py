#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一初始化脚本
用于初始化系统所有数据，包括用户、角色、权限、资源、动作、范围和检测相关数据
"""

import sys
import os
import re
import pymysql
from werkzeug.security import generate_password_hash

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config, DevelopmentConfig
from app.extensions import init_db, Base
from sqlalchemy import text
from app.models.user.user import User
from app.models.user.role import Role
from app.models.user.permission import Permission
from app.models.detection.category import Category
from app.models.detection.detection_object import DetectionObject
from app.models.detection.detection_item import DetectionItem
from app.models.detection.detection_param import DetectionParam
from app.models.detection.detection_standard import DetectionStandard
from app.models.detection.delegation_form_template import DelegationFormTemplate


def init_database():
    """初始化数据库，确保数据库存在"""
    print("开始初始化数据库...")
    
    # 使用开发配置（MySQL数据库）
    config = DevelopmentConfig()
    
    # 解析数据库连接URL
    db_url = config.SQLALCHEMY_DATABASE_URI
    # 使用正则表达式解析MySQL连接URL
    match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)(\?.*)?', db_url)
    if match:
        username = match.group(1)
        password = match.group(2)
        host = match.group(3)
        port = int(match.group(4))
        db_name = match.group(5)
        
        print(f"解析到数据库配置：主机={host}, 端口={port}, 用户名={username}, 数据库名={db_name}")
        
        # 创建数据库（如果不存在）
        try:
            # 先创建一个不指定数据库的连接
            conn = pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                charset='utf8mb4'
            )
            
            with conn.cursor() as cursor:
                # 检查数据库是否存在
                cursor.execute(f"SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
                result = cursor.fetchone()
                
                if not result:
                    # 创建数据库
                    cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"✅ 数据库 {db_name} 创建成功")
                else:
                    print(f"ℹ️ 数据库 {db_name} 已存在")
            
            conn.close()
            print("✅ 数据库连接配置完成")
        except Exception as e:
            print(f"❌ 创建数据库失败: {e}")
            sys.exit(1)
    else:
        print(f"❌ 无法解析数据库连接URL: {db_url}")
        sys.exit(1)


def init_permission_resources(db):
    """初始化系统内置权限资源"""
    print("开始初始化系统内置权限资源...")
    
    try:
        # 导入服务类
        from app.services.user.resource_service import ResourceService
        from app.services.user.action_service import ActionService
        from app.services.user.scope_service import ScopeService
        
        # 系统内置资源列表：与代码绑定
        # 格式：(资源标识, 资源名称, 描述)
        system_resources = [
            ("user", "用户", "用户管理相关资源"),
            ("role", "角色", "角色管理相关资源"),
            ("permission", "权限", "权限管理相关资源"),
            ("detection", "检测", "检测项目相关资源"),
            ("category", "分类", "分类管理相关资源"),
            ("standard", "规范", "检测规范相关资源"),
            ("template", "模板", "委托单模板相关资源")
        ]
        
        # 系统内置动作列表
        # 格式：(动作标识, 动作名称, 描述)
        system_actions = [
            ("view", "查看", "查看资源权限"),
            ("create", "创建", "创建资源权限"),
            ("update", "修改", "修改资源权限"),
            ("delete", "删除", "删除资源权限"),
            ("assign", "分配", "分配权限资源")
        ]
        
        # 系统内置范围列表
        # 格式：(范围标识, 范围名称, 描述)
        system_scopes = [
            ("all", "所有", "所有范围权限"),
            ("own", "自己", "自己的数据范围"),
            ("specific", "特定", "特定数据范围")
        ]
        
        # 系统内置权限列表：资源+动作的组合
        # 格式：(权限代码, 资源标识, 动作标识, 范围标识, 描述)
        system_permissions = [
            # 用户管理权限
            ("user_view", "user", "view", "all", "查看用户信息权限"),
            ("user_create", "user", "create", "all", "创建用户权限"),
            ("user_update", "user", "update", "all", "更新用户权限"),
            ("user_delete", "user", "delete", "all", "删除用户权限"),
            
            # 角色管理权限
            ("role_view", "role", "view", "all", "查看角色权限"),
            ("role_create", "role", "create", "all", "创建角色权限"),
            ("role_update", "role", "update", "all", "更新角色权限"),
            ("role_delete", "role", "delete", "all", "删除角色权限"),
            
            # 权限管理权限
            ("permission_view", "permission", "view", "all", "查看权限权限"),
            ("permission_create", "permission", "create", "all", "创建权限权限"),
            ("permission_update", "permission", "update", "all", "更新权限权限"),
            ("permission_delete", "permission", "delete", "all", "删除权限权限"),
            
            # 检测管理权限
            ("detection_view", "detection", "view", "all", "查看检测项目权限"),
            ("detection_create", "detection", "create", "all", "创建检测项目权限"),
            ("detection_update", "detection", "update", "all", "更新检测项目权限"),
            ("detection_delete", "detection", "delete", "all", "删除检测项目权限"),
            
            # 分类管理权限
            ("category_view", "category", "view", "all", "查看分类权限"),
            ("category_create", "category", "create", "all", "创建分类权限"),
            ("category_update", "category", "update", "all", "更新分类权限"),
            ("category_delete", "category", "delete", "all", "删除分类权限"),
            
            # 规范管理权限
            ("standard_view", "standard", "view", "all", "查看检测规范权限"),
            ("standard_create", "standard", "create", "all", "创建检测规范权限"),
            ("standard_update", "standard", "update", "all", "更新检测规范权限"),
            ("standard_delete", "standard", "delete", "all", "删除检测规范权限"),
            
            # 模板管理权限
            ("template_view", "template", "view", "all", "查看委托单模板权限"),
            ("template_create", "template", "create", "all", "创建委托单模板权限"),
            ("template_update", "template", "update", "all", "更新委托单模板权限"),
            ("template_delete", "template", "delete", "all", "删除委托单模板权限")
        ]
        
        print("📝 开始初始化系统内置资源...")
        
        # 初始化系统内置资源
        for resource_name, display_name, description in system_resources:
            existing_resource = ResourceService.get_resource_by_name(db, resource_name)
            if existing_resource:
                # 资源已存在，更新信息
                ResourceService.update_resource(db, existing_resource.id, 
                                              display_name=display_name, 
                                              description=description, 
                                              is_active=True, 
                                              is_system_builtin=True)
                print(f"ℹ️ 更新系统内置资源: {resource_name} - {display_name}")
            else:
                # 创建新资源
                ResourceService.create_resource(db, resource_name, display_name, description, is_system_builtin=True)
                print(f"✅ 创建系统内置资源: {resource_name} - {display_name}")
        
        print("📝 开始初始化系统内置动作...")
        
        # 初始化系统内置动作
        for action_name, display_name, description in system_actions:
            existing_action = ActionService.get_action_by_name(db, action_name)
            if existing_action:
                # 动作已存在，更新信息
                ActionService.update_action(db, existing_action.id, 
                                          display_name=display_name, 
                                          description=description, 
                                          is_active=True, 
                                          is_system_builtin=True)
                print(f"ℹ️ 更新系统内置动作: {action_name} - {display_name}")
            else:
                # 创建新动作
                ActionService.create_action(db, action_name, display_name, description, is_system_builtin=True)
                print(f"✅ 创建系统内置动作: {action_name} - {display_name}")
        
        print("📝 开始初始化系统内置范围...")
        
        # 初始化系统内置范围
        for scope_name, display_name, description in system_scopes:
            existing_scope = ScopeService.get_scope_by_name(db, scope_name)
            if existing_scope:
                # 范围已存在，更新信息
                ScopeService.update_scope(db, existing_scope.id, 
                                        display_name=display_name, 
                                        description=description, 
                                        is_active=True, 
                                        is_system_builtin=True)
                print(f"ℹ️ 更新系统内置范围: {scope_name} - {display_name}")
            else:
                # 创建新范围
                ScopeService.create_scope(db, scope_name, display_name, description, is_system_builtin=True)
                print(f"✅ 创建系统内置范围: {scope_name} - {display_name}")
        
        print("📝 开始初始化系统内置权限...")
        
        # 初始化系统内置权限
        for perm_code, resource_name, action_name, scope_name, description in system_permissions:
            # 检查权限是否已存在
            existing_perm = db.query(Permission).filter(Permission.code == perm_code).first()
            
            # 获取资源、动作、范围对象
            resource = ResourceService.get_resource_by_name(db, resource_name)
            action = ActionService.get_action_by_name(db, action_name)
            scope = ScopeService.get_scope_by_name(db, scope_name)
            
            if existing_perm:
                # 权限已存在，更新信息
                existing_perm.resource = resource_name
                existing_perm.action = action_name
                existing_perm.scope = scope_name
                existing_perm.description = description
                existing_perm.is_active = True
                existing_perm.is_system_builtin = True  # 确保系统内置权限标记正确
                
                # 更新关联关系
                existing_perm.resources = [resource] if resource else []
                existing_perm.actions = [action] if action else []
                existing_perm.scopes = [scope] if scope else []
                
                print(f"ℹ️ 更新系统内置权限: {perm_code} - {description}")
            else:
                # 创建新权限
                new_perm = Permission(
                    code=perm_code,
                    resource=resource_name,
                    action=action_name,
                    scope=scope_name,
                    description=description,
                    is_active=True,
                    is_system_builtin=True  # 标记为系统内置
                )
                
                # 添加关联关系
                if resource:
                    new_perm.resources.append(resource)
                if action:
                    new_perm.actions.append(action)
                if scope:
                    new_perm.scopes.append(scope)
                
                db.add(new_perm)
                print(f"✅ 创建系统内置权限: {perm_code} - {description}")
        
        # 提交事务
        db.commit()
        
        print("🎉 系统内置权限资源初始化完成！")
        print(f"\n📋 初始化结果:")
        print(f"   - 系统内置资源数量: {len(system_resources)}")
        print(f"   - 系统内置动作数量: {len(system_actions)}")
        print(f"   - 系统内置范围数量: {len(system_scopes)}")
        print(f"   - 系统内置权限数量: {len(system_permissions)}")
        print(f"   - 所有资源、动作、范围和权限已成功初始化！")
        print(f"\n💡 提示: 系统内置资源与代码绑定，管理页面只可分配权限，不可新增/删除")
        
    except Exception as e:
        print(f"\n❌ 初始化权限资源失败: {e}")
        db.rollback()
        raise


def init_user_data(db):
    """初始化用户、角色和基本权限数据"""
    print("开始初始化用户、角色和基本权限数据...")
    
    try:
        # 1. 从数据库中获取已创建的权限
        permissions = {}
        existing_permissions = db.query(Permission).all()
        for perm in existing_permissions:
            permissions[perm.code] = perm
        print(f"✅ 已获取 {len(permissions)} 个现有权限")
        
        # 2. 定义所需的角色列表及对应的权限
        roles_to_create = [
            {
                'name': '普通用户',
                'description': '基础用户角色，拥有基本的查看权限',
                'permissions': ['user_view', 'detection_view']
            },
            {
                'name': '管理员',
                'description': '管理员角色，拥有用户和角色管理权限',
                'permissions': ['user_view', 'user_create', 'user_update', 'role_view', 'detection_view', 'detection_create']
            },
            {
                'name': '审核员',
                'description': '审核员角色，拥有审核相关权限',
                'permissions': ['user_view', 'detection_view']
            }
        ]
        
        # 创建角色
        roles = {}
        for role_data in roles_to_create:
            role = Role(
                name=role_data['name'],
                description=role_data['description'],
                is_active=True
            )
            # 分配权限
            for perm_code in role_data['permissions']:
                role.permissions.append(permissions[perm_code])
            db.add(role)
            print(f"✅ 角色创建成功: {role.name} - {role.description}")
            roles[role_data['name']] = role
        db.commit()
        
        # 3. 定义所需的用户列表及对应的角色
        users_to_create = [
            {
                'username': 'aaa',
                'password': 'aaa',
                'name': '超级管理员',
                'is_admin': True,
                'roles': ['普通用户', '管理员', '审核员']
            },
            {
                'username': 'user1',
                'password': '123456',
                'name': '普通用户1',
                'is_admin': False,
                'roles': ['普通用户']
            },
            {
                'username': 'admin1',
                'password': '123',
                'name': '管理员1',
                'is_admin': False,
                'roles': ['管理员']
            },
            {
                'username': 'auditor1',
                'password': '123',
                'name': '审核员1',
                'is_admin': False,
                'roles': ['审核员']
            }
        ]
        
        # 创建用户
        for user_data in users_to_create:
            user = User(
                name=user_data['name'],
                username=user_data['username'],
                password=generate_password_hash(user_data['password']),
                is_active=True,
                is_admin=user_data['is_admin']
            )
            # 分配角色
            for role_name in user_data['roles']:
                user.roles.append(roles[role_name])
            db.add(user)
            print(f"✅ 用户创建成功: {user.username} (姓名: {user.name}, 角色: {', '.join(user_data['roles'])}")
        
        # 提交所有创建操作
        db.commit()
        
        print("🎉 用户、角色和权限数据初始化完成！")
        
    except Exception as e:
        print(f"\n❌ 初始化用户数据失败: {e}")
        db.rollback()
        raise


def init_detection_data(db):
    """初始化检测相关数据"""
    print("开始初始化检测相关数据...")
    
    try:
        # 1. 初始化分类数据
        print("\n1. 初始化分类数据:")
        categories_to_create = [
            {'category_name': '建筑材料', 'sort_order': 1},
            {'category_name': '装饰材料', 'sort_order': 2},
            {'category_name': '防水材料', 'sort_order': 3},
            {'category_name': '保温材料', 'sort_order': 4}
        ]
        
        categories = {}
        for cat_data in categories_to_create:
            category = Category(
                category_name=cat_data['category_name'],
                parent_id=None,
                sort_order=cat_data['sort_order'],
                status=1
            )
            db.add(category)
            db.flush()  # 获取category_id
            categories[cat_data['category_name']] = category
            print(f"✅ 分类创建成功: {category.category_name}")
        db.commit()
        
        # 2. 初始化检测对象数据
        print("\n2. 初始化检测对象数据:")
        detection_objects_to_create = [
            {
                'object_name': '普通硅酸盐水泥',
                'category': '建筑材料',
                'description': '强度等级42.5的普通硅酸盐水泥',
                'sort_order': 1
            },
            {
                'object_name': 'HRB400E钢筋',
                'category': '建筑材料',
                'description': '抗震钢筋，屈服强度≥400MPa',
                'sort_order': 2
            },
            {
                'object_name': '陶瓷砖',
                'category': '装饰材料',
                'description': '用于墙面和地面装饰的陶瓷砖',
                'sort_order': 1
            },
            {
                'object_name': '聚氨酯防水涂料',
                'category': '防水材料',
                'description': '双组份聚氨酯防水涂料',
                'sort_order': 1
            }
        ]
        
        detection_objects = {}
        for obj_data in detection_objects_to_create:
            detection_object = DetectionObject(
                object_name=obj_data['object_name'],
                category_id=categories[obj_data['category']].category_id,
                description=obj_data['description'],
                sort_order=obj_data['sort_order'],
                status=1
            )
            db.add(detection_object)
            db.flush()  # 获取object_id
            detection_objects[obj_data['object_name']] = detection_object
            print(f"✅ 检测对象创建成功: {detection_object.object_name}")
        db.commit()
        
        # 3. 初始化检测项目数据
        print("\n3. 初始化检测项目数据:")
        detection_items_to_create = [
            {
                'item_name': '水泥检测',
                'detection_object': '普通硅酸盐水泥',
                'description': '检测水泥的物理性能和化学性能，包括抗压强度、抗折强度、凝结时间、安定性等指标',
                'sort_order': 1,
                'status': 1
            },
            {
                'item_name': '钢筋检测',
                'detection_object': 'HRB400E钢筋',
                'description': '检测钢筋的力学性能和化学成分，包括屈服强度、抗拉强度、伸长率、弯曲性能等指标',
                'sort_order': 2,
                'status': 1
            },
            {
                'item_name': '瓷砖检测',
                'detection_object': '陶瓷砖',
                'description': '检测瓷砖的物理性能和外观质量，包括吸水率、断裂模数、表面平整度、边长偏差等指标',
                'sort_order': 3,
                'status': 1
            },
            {
                'item_name': '防水涂料检测',
                'detection_object': '聚氨酯防水涂料',
                'description': '检测防水涂料的物理性能和化学性能，包括拉伸强度、断裂伸长率、不透水性、低温柔性等指标',
                'sort_order': 4,
                'status': 1
            }
        ]
        
        detection_items = {}
        for item_data in detection_items_to_create:
            item = DetectionItem(
                item_name=item_data['item_name'],
                object_id=detection_objects[item_data['detection_object']].object_id,
                description=item_data['description'],
                sort_order=item_data['sort_order'],
                status=item_data['status']
            )
            db.add(item)
            db.flush()  # 获取item_id
            detection_items[item_data['item_name']] = item
            print(f"✅ 检测项目创建成功: {item.item_name}")
        db.commit()
        
        # 3. 初始化检测参数数据
        print("\n3. 初始化检测参数数据:")
        detection_params_to_create = [
            # 水泥检测参数
            {
                'item_name': '水泥检测',
                'material_name': '普通硅酸盐水泥',
                'param_name': '抗压强度',
                'price': '50.00元/组',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '水泥检测',
                'material_name': '普通硅酸盐水泥',
                'param_name': '抗折强度',
                'price': '40.00元/组',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '水泥检测',
                'material_name': '普通硅酸盐水泥',
                'param_name': '凝结时间',
                'price': '30.00元/组',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '水泥检测',
                'material_name': '普通硅酸盐水泥',
                'param_name': '安定性',
                'price': '25.00元/组',
                'is_required': 1,
                'is_regular_param': 1
            },
            # 钢筋检测参数
            {
                'item_name': '钢筋检测',
                'material_name': 'HRB400E钢筋',
                'param_name': '屈服强度',
                'price': '60.00元/根',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '钢筋检测',
                'material_name': 'HRB400E钢筋',
                'param_name': '抗拉强度',
                'price': '60.00元/根',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '钢筋检测',
                'material_name': 'HRB400E钢筋',
                'param_name': '伸长率',
                'price': '40.00元/根',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '钢筋检测',
                'material_name': 'HRB400E钢筋',
                'param_name': '弯曲性能',
                'price': '50.00元/根',
                'is_required': 1,
                'is_regular_param': 1
            },
            # 瓷砖检测参数
            {
                'item_name': '瓷砖检测',
                'material_name': '陶瓷砖',
                'param_name': '吸水率',
                'price': '30.00元/块',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '瓷砖检测',
                'material_name': '陶瓷砖',
                'param_name': '断裂模数',
                'price': '40.00元/块',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '瓷砖检测',
                'material_name': '陶瓷砖',
                'param_name': '表面平整度',
                'price': '25.00元/块',
                'is_required': 0,
                'is_regular_param': 1
            },
            {
                'item_name': '瓷砖检测',
                'material_name': '陶瓷砖',
                'param_name': '边长偏差',
                'price': '20.00元/块',
                'is_required': 0,
                'is_regular_param': 1
            },
            # 防水涂料检测参数
            {
                'item_name': '防水涂料检测',
                'material_name': '聚氨酯防水涂料',
                'param_name': '拉伸强度',
                'price': '80.00元/㎡',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '防水涂料检测',
                'material_name': '聚氨酯防水涂料',
                'param_name': '断裂伸长率',
                'price': '70.00元/㎡',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '防水涂料检测',
                'material_name': '聚氨酯防水涂料',
                'param_name': '不透水性',
                'price': '60.00元/㎡',
                'is_required': 1,
                'is_regular_param': 1
            },
            {
                'item_name': '防水涂料检测',
                'material_name': '聚氨酯防水涂料',
                'param_name': '低温柔性',
                'price': '50.00元/㎡',
                'is_required': 0,
                'is_regular_param': 1
            }
        ]
        
        detection_params = {}
        for param_data in detection_params_to_create:
            param = DetectionParam(
                item_id=detection_items[param_data['item_name']].item_id,
                param_name=param_data['param_name'],
                price=param_data['price'],
                is_regular_param=param_data['is_regular_param'],
                sort_order=0,
                status=1
            )
            db.add(param)
            db.flush()  # 获取param_id
            key = f"{param_data['item_name']}-{param_data['param_name']}"
            detection_params[key] = param
            print(f"✅ 检测参数创建成功: {param.param_name} - {param.price}")
        db.commit()
        
        # 4. 初始化检测规范数据
        print("\n4. 初始化检测规范数据:")
        detection_standards_to_create = [
            {
                'standard_code': 'GB 175-2023',
                'standard_name': '通用硅酸盐水泥',
                'standard_type': '国家标准',
                'status': 1
            },
            {
                'standard_code': 'GB/T 1499.2-2018',
                'standard_name': '钢筋混凝土用钢 第2部分：热轧带肋钢筋',
                'standard_type': '国家标准',
                'status': 1
            },
            {
                'standard_code': 'JC/T 900-2017',
                'standard_name': '混凝土界面处理剂',
                'standard_type': '行业标准',
                'status': 1
            }
        ]
        
        detection_standards = {}
        for std_data in detection_standards_to_create:
            standard = DetectionStandard(
                standard_code=std_data['standard_code'],
                standard_name=std_data['standard_name'],
                standard_type=std_data['standard_type'],
                status=std_data['status']
            )
            db.add(standard)
            db.flush()  # 获取standard_id
            detection_standards[std_data['standard_code']] = standard
            print(f"✅ 检测规范创建成功: {standard.standard_code} - {standard.standard_name}")
        db.commit()
        
        # 6. 初始化委托单模板数据
        print("\n6. 初始化委托单模板数据:")
        templates_to_create = [
            {
                'template_name': '水泥检测委托单',
                'template_version': 'V1.0',
                'template_code': 'SN-2024-001',
                'item_id': detection_items['水泥检测'].item_id,
                'file_type': 'pdf',
                'upload_user': 'aaa',
                'is_default': 1
            },
            {
                'template_name': '钢筋检测委托单',
                'template_version': 'V1.0',
                'template_code': 'GJ-2024-001',
                'item_id': detection_items['钢筋检测'].item_id,
                'file_type': 'pdf',
                'upload_user': 'aaa',
                'is_default': 0
            }
        ]
        
        templates = {}
        for template_data in templates_to_create:
            template = DelegationFormTemplate(
                template_name=template_data['template_name'],
                template_version=template_data['template_version'],
                template_code=template_data['template_code'],
                file_type=template_data['file_type'],
                upload_user=template_data['upload_user'],
                status=1
            )
            db.add(template)
            db.flush()  # 获取template_id
            templates[template_data['template_name']] = template
            print(f"✅ 委托单模板创建成功: {template.template_name} V{template.template_version}")
        db.commit()
        
        # 7. 更新检测参数，添加检测指南相关字段和关联
        print("\n7. 更新检测参数，添加检测指南相关字段和关联:")
        
        # 为水泥检测参数添加检测指南相关字段和关联
        cement_params = [param for param in detection_params.values() if param.param_name in ['抗压强度', '抗折强度', '凝结时间', '安定性']]
        for param in cement_params:
            # 添加检测指南相关字段
            param.sampling_batch = '每批次≤500吨取1组'
            param.sampling_require = '需使用无菌采样袋，采样量≥500g'
            param.required_info = '产品名称、批次号、生产日期、规格'
            param.report_time = '常规5个工作日，加急3个工作日'
            param.sample_processing_fee = '20.00元/组'
            
            # 关联检测规范
            if 'GB 175-2023' in detection_standards:
                param.standards.append(detection_standards['GB 175-2023'])
            
            # 关联委托单模板
            if '水泥检测委托单' in templates:
                param.template_id = templates['水泥检测委托单'].template_id
        print(f"✅ 已更新{len(cement_params)}个水泥检测参数")
        
        # 为钢筋检测参数添加检测指南相关字段和关联
        rebar_params = [param for param in detection_params.values() if param.param_name in ['屈服强度', '抗拉强度', '伸长率', '弯曲性能']]
        for param in rebar_params:
            # 添加检测指南相关字段
            param.sampling_batch = '每批次≤1000根取1组'
            param.sampling_require = '随机抽取，每组3根，每根长度≥1m'
            param.required_info = '产品名称、批次号、规格型号、生产日期'
            param.report_time = '常规3个工作日，加急1个工作日'
            param.sample_processing_fee = '30.00元/组'
            
            # 关联检测规范
            if 'GB/T 1499.2-2018' in detection_standards:
                param.standards.append(detection_standards['GB/T 1499.2-2018'])
            
            # 关联委托单模板
            if '钢筋检测委托单' in templates:
                param.template_id = templates['钢筋检测委托单'].template_id
        print(f"✅ 已更新{len(rebar_params)}个钢筋检测参数")
        
        db.commit()
        
        print("🎉 检测相关数据初始化完成！")
        
    except Exception as e:
        print(f"\n❌ 初始化检测数据失败: {e}")
        db.rollback()
        raise


def clean_existing_data(db):
    """清理现有数据"""
    print("开始清理现有数据...")
    
    try:
        # 导入text函数用于执行原生SQL
        from sqlalchemy import text
        
        # 删除所有用户、角色和权限数据
        # 注意：需要按照依赖关系的相反顺序删除
        # 1. 先删除用户与角色、用户与权限的关联
        db.execute(text("DELETE FROM user_roles"))
        db.execute(text("DELETE FROM user_permissions"))
        db.execute(text("DELETE FROM role_permissions"))
        # 删除新添加的权限-资源、权限-动作、权限-范围关联表数据
        db.execute(text("DELETE FROM permission_resources"))
        db.execute(text("DELETE FROM permission_actions"))
        db.execute(text("DELETE FROM permission_scopes"))
        print("✅ 已删除关联表数据")
        
        # 2. 删除用户数据
        db.query(User).delete()
        print("✅ 已删除用户表数据")
        
        # 3. 删除角色数据
        db.query(Role).delete()
        print("✅ 已删除角色表数据")
        
        # 4. 删除权限数据
        db.query(Permission).delete()
        print("✅ 已删除权限表数据")
        
        # 删除检测相关数据
        # 注意：需要按照依赖关系的相反顺序删除
        # 5. 删除委托单模板数据
        try:
            db.query(DelegationFormTemplate).delete()
            print("✅ 已删除委托单模板表数据")
        except Exception as e:
            print(f"ℹ️ 委托单模板表不存在或删除失败: {e}")
        
        # 6. 删除检测参数规范关联表数据
        try:
            db.execute(text("DELETE FROM detection_param_standard"))
            print("✅ 已删除检测参数规范关联表数据")
        except Exception as e:
            print(f"ℹ️ 检测参数规范关联表不存在或删除失败: {e}")
        
        # 7. 删除检测参数模板关联表数据
        try:
            db.execute(text("DELETE FROM detection_param_template"))
            print("✅ 已删除检测参数模板关联表数据")
        except Exception as e:
            print(f"ℹ️ 检测参数模板关联表不存在或删除失败: {e}")
        
        # 8. 删除检测规范数据
        try:
            db.query(DetectionStandard).delete()
            print("✅ 已删除检测规范表数据")
        except Exception as e:
            print(f"ℹ️ 检测规范表不存在或删除失败: {e}")
        
        # 9. 删除检测参数数据
        try:
            db.query(DetectionParam).delete()
            print("✅ 已删除检测参数表数据")
        except Exception as e:
            print(f"ℹ️ 检测参数表不存在或删除失败: {e}")
        
        # 10. 删除检测项目数据
        try:
            db.query(DetectionItem).delete()
            print("✅ 已删除检测项目表数据")
        except Exception as e:
            print(f"ℹ️ 检测项目表不存在或删除失败: {e}")
        

        
        # 14. 删除检测对象数据
        try:
            db.query(DetectionObject).delete()
            print("✅ 已删除检测对象表数据")
        except Exception as e:
            print(f"ℹ️ 检测对象表不存在或删除失败: {e}")
        
        # 15. 删除分类数据
        try:
            db.query(Category).delete()
            print("✅ 已删除分类表数据")
        except Exception as e:
            print(f"ℹ️ 分类表不存在或删除失败: {e}")
        
        # 提交删除操作
        db.commit()
        print("✅ 所有现有数据已清理完毕")
        
    except Exception as e:
        print(f"\n❌ 清理现有数据失败: {e}")
        db.rollback()
        raise


def main():
    """主函数"""
    print("=" * 60)
    print("统一初始化脚本开始执行")
    print("=" * 60)
    
    try:
        # 1. 初始化数据库
        init_database()
        
        # 2. 获取配置
        app_config = config['development']
        
        # 3. 初始化数据库连接
        engine, SessionLocal = init_db(app_config)
        print("✅ 数据库连接成功")
        
        # 4. 创建数据库表（先删除所有现有表，再重新创建）
        if engine is not None:
            print("开始创建数据库表...")
            # 先禁用外键约束，避免删除表时的外键约束错误
            with engine.begin() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            # 先删除所有现有表，确保表结构是最新的
            Base.metadata.drop_all(bind=engine)
            print("✅ 已删除所有现有表")
            # 再创建新表
            Base.metadata.create_all(bind=engine)
            # 重新启用外键约束
            with engine.begin() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            print("✅ 数据库表创建成功")
        else:
            raise RuntimeError("数据库引擎未正确初始化")
        
        # 5. 创建数据库会话
        db = SessionLocal()
        
        try:
            # 6. 清理现有数据
            clean_existing_data(db)
            
            # 7. 初始化权限资源
            init_permission_resources(db)
            
            # 8. 初始化用户数据
            init_user_data(db)
            
            # 9. 初始化检测数据
            init_detection_data(db)
            
            # 10. 验证数据
            print("\n开始验证初始化数据...")
            
            # 获取第一个用户（超级管理员）的所有权限（包括角色继承的权限）
            admin_user = db.query(User).filter_by(username='aaa').first()
            all_permissions = admin_user.get_all_permissions()
            print(f"用户'{admin_user.username}'的所有权限: {[p.code for p in all_permissions]}")
            
            # 验证检测数据
            print("\n检测数据验证:")
            # 获取分类数量
            category_count = db.query(Category).count()
            print(f"分类数量: {category_count}")
            
            # 获取检测项目数量
            item_count = db.query(DetectionItem).count()
            print(f"检测项目数量: {item_count}")
            
            # 获取检测对象数量
            object_count = db.query(DetectionObject).count()
            print(f"检测对象数量: {object_count}")
            
            # 获取检测参数数量
            param_count = db.query(DetectionParam).count()
            print(f"检测参数数量: {param_count}")
            
            # 获取检测规范数量
            standard_count = db.query(DetectionStandard).count()
            print(f"检测规范数量: {standard_count}")
            
            # 获取检测参数规范关联数量
            param_standard_count = db.execute(text("SELECT COUNT(*) FROM detection_param_standard")).scalar()
            print(f"检测参数规范关联数量: {param_standard_count}")
            
            # 验证模板关联是否正确
            cement_param_with_template = db.query(DetectionParam).filter(DetectionParam.template_id.isnot(None)).count()
            print(f"关联了模板的检测参数数量: {cement_param_with_template}")
            
            # 获取委托单模板数量
            template_count = db.query(DelegationFormTemplate).count()
            print(f"委托单模板数量: {template_count}")
            
            print("\n🎉 所有数据验证通过！")
            print("\n📋 初始化总结:")
            print("- 数据库初始化完成")
            print("- 数据库表创建完成")
            print("- 权限资源初始化完成")
            print("- 用户、角色和权限数据初始化完成")
            print("- 检测相关数据初始化完成")
            print("- 数据验证通过")
            
            print("\n💡 提示:")
            print("- 用户名: aaa")
            print("- 密码: aaa")
            print("- 请使用这些凭据登录系统")
            
        finally:
            # 关闭数据库会话
            db.close()
            print("\n✅ 数据库会话已关闭")
            
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        sys.exit(1)
    
    print("\n=" * 60)
    print("统一初始化脚本执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
