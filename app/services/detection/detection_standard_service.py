# 检测规范服务类
# 包含检测规范相关的业务逻辑，如获取规范信息、创建规范、更新规范等

from app.models.detection import DetectionStandard
from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.detection_dal import DetectionStandardDAL


class DetectionStandardService:
    """检测规范服务类，处理检测规范相关的业务逻辑"""
    
    @staticmethod
    def get_by_id(standard_id):
        """
        根据ID获取检测规范信息
        :param standard_id: 规范ID
        :return: 成功返回 (规范对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            standard = standard_dal.get_by_id(standard_id)
            if standard:
                return (standard, None)
            else:
                return (None, f"规范ID {standard_id} 不存在")
        except Exception as e:
            return (None, f"获取检测规范失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_code(standard_code):
        """
        根据规范编号获取检测规范信息
        :param standard_code: 规范编号
        :return: 成功返回 (规范对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            standards = standard_dal.get_by_condition({"standard_code": standard_code})
            if standards:
                return (standards[0], None)
            else:
                return (None, f"规范编号 {standard_code} 不存在")
        except Exception as e:
            return (None, f"获取检测规范失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_all():
        """
        获取所有检测规范列表
        :return: 成功返回 (规范列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            standards = standard_dal.get_all()
            return (standards, None)
        except Exception as e:
            return (None, f"获取检测规范列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_status(status):
        """
        根据状态获取检测规范列表
        :param status: 状态：1=有效，0=作废，2=待生效
        :return: 成功返回 (规范列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            standards = standard_dal.get_by_status(status)
            return (standards, None)
        except Exception as e:
            return (None, f"获取检测规范列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_ids(standard_ids):
        """
        根据ID列表获取检测规范列表
        :param standard_ids: 规范ID列表
        :return: 成功返回 (规范列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            standards = standard_dal.get_by_ids(standard_ids)
            return (standards, None)
        except Exception as e:
            return (None, f"获取检测规范列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def create(standard_data):
        """
        创建新检测规范
        :param standard_data: 规范数据字典
        :return: 成功返回 (规范对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 验证必填字段
            if 'standard_code' not in standard_data or not standard_data['standard_code']:
                return (None, "规范编号不能为空")
            if 'standard_name' not in standard_data or not standard_data['standard_name']:
                return (None, "规范名称不能为空")
            
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            
            # 检查规范编号是否已存在
            existing_standard, _ = DetectionStandardService.get_by_code(standard_data['standard_code'])
            if existing_standard:
                return (None, f"规范编号 {standard_data['standard_code']} 已存在")
            
            # 处理替代规范ID
            replace_id = standard_data.get('replace_id')
            if replace_id:
                # 检查替代规范是否存在
                replace_standard = standard_dal.get_by_id(replace_id)
                if not replace_standard:
                    return (None, f"替代规范ID {replace_id} 不存在")
            
            # 创建规范数据
            create_data = {
                'standard_code': standard_data['standard_code'],
                'standard_name': standard_data['standard_name'],
                'standard_type': standard_data.get('standard_type'),
                'effective_time': standard_data.get('effective_time'),
                'invalid_time': standard_data.get('invalid_time'),
                'status': standard_data.get('status', 1),
                'replace_id': replace_id,
                'remark': standard_data.get('remark')
            }
            
            # 创建规范
            standard = standard_dal.create(create_data)
            return (standard, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突（双重保障）
            if 'Duplicate entry' in str(e) and 'standard_code' in str(e):
                return (None, f"规范编号 {standard_data['standard_code']} 已存在")
            return (None, f"创建检测规范失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def update(standard_id, standard_data):
        """
        更新检测规范信息
        :param standard_id: 规范ID
        :param standard_data: 要更新的规范数据
        :return: 成功返回 (规范对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 验证必填字段
            if 'standard_code' in standard_data and not standard_data['standard_code']:
                return (None, "规范编号不能为空")
            if 'standard_name' in standard_data and not standard_data['standard_name']:
                return (None, "规范名称不能为空")
            
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            
            # 检查规范是否存在
            current_standard = standard_dal.get_by_id(standard_id)
            if not current_standard:
                return (None, f"规范ID {standard_id} 不存在")
            
            # 当更新规范编号时，检查唯一性
            if 'standard_code' in standard_data and standard_data['standard_code'] != current_standard.standard_code:
                # 检查是否有其他规范使用了相同的编号
                existing_standard, _ = DetectionStandardService.get_by_code(standard_data['standard_code'])
                if existing_standard:
                    return (None, f"规范编号 {standard_data['standard_code']} 已存在")
            
            # 处理替代规范ID
            if 'replace_id' in standard_data:
                replace_id = standard_data['replace_id']
                if replace_id:
                    # 检查新的替代规范是否存在
                    replace_standard = standard_dal.get_by_id(replace_id)
                    if not replace_standard:
                        return (None, f"替代规范ID {replace_id} 不存在")
            
            # 更新规范
            standard = standard_dal.update(standard_id, standard_data)
            
            return (standard, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突（双重保障）
            if 'Duplicate entry' in str(e) and 'standard_code' in str(e):
                return (None, f"规范编号 {standard_data['standard_code']} 已存在")
            return (None, f"更新检测规范失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def enable_standard(standard_id):
        """
        启用检测规范
        :param standard_id: 规范ID
        :return: 成功返回 (规范对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            
            # 更新规范状态为有效(1)
            standard = standard_dal.update(standard_id, {'status': 1})
            
            if not standard:
                return (None, f"规范ID {standard_id} 不存在")
            
            return (standard, None)
        except Exception as e:
            return (None, f"启用检测规范失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def disable_standard(standard_id):
        """
        禁用检测规范
        :param standard_id: 规范ID
        :return: 成功返回 (规范对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            
            # 更新规范状态为作废(0)
            standard = standard_dal.update(standard_id, {'status': 0})
            
            if not standard:
                return (None, f"规范ID {standard_id} 不存在")
            
            return (standard, None)
        except Exception as e:
            return (None, f"禁用检测规范失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def delete(standard_id):
        """
        删除检测规范
        :param standard_id: 规范ID
        :return: 成功返回 (True, None)，失败返回 (False, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            standard_dal = DetectionStandardDAL(db, redis)
            
            # 获取规范对象
            standard = standard_dal.get_by_id(standard_id)
            if not standard:
                return (False, f"规范ID {standard_id} 不存在")
            
            # 检查规范是否被使用
            try:
                # 1. 检查是否有其他规范引用此规范作为替代规范
                referenced_standards = standard_dal.get_by_condition({"replace_id": standard_id})
                referenced_count = len(referenced_standards)
                if referenced_count > 0:
                    return (False, f"规范ID {standard_id} 被 {referenced_count} 个规范引用为替代规范，无法删除")
                
                # 未来添加新的关联检查时，只需在此处添加新的检查逻辑
                # 例如：
                # 4. 检查是否有XX使用此规范
                # xx_count = standard_dal.get_used_count(standard_id)
                # if xx_count > 0:
                #     return (False, f"规范ID {standard_id} 被 {xx_count} 个XX使用，无法删除")
                    
            except Exception as e:
                return (False, f"检查规范使用情况失败: {str(e)}")
            
            # 删除规范
            success = standard_dal.delete(standard_id)
            return (success, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return (False, f"删除检测规范失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
