# 检测相关数据访问层
# 包含所有检测相关模型的DAL类

from typing import List, Optional, Dict, Any
from app.models.detection import DetectionItem, DetectionParam, DetectionStandard, Category, DelegationFormTemplate, DetectionObject
from app.dal.base_dal import BaseDAL






class DetectionParamDAL(BaseDAL):
    """检测参数数据访问层"""
    
    def __init__(self, db, redis):
        super().__init__(db, redis, DetectionParam)
    
    def get_by_item_id(self, item_id: int) -> List[DetectionParam]:
        """
        根据项目ID获取检测参数列表
        :param item_id: 项目ID
        :return: 检测参数列表
        """
        return self.get_by_condition({"item_id": item_id})
    
    def get_by_status(self, status: int) -> List[DetectionParam]:
        """
        根据状态获取检测参数列表
        :param status: 状态：1=启用，0=禁用
        :return: 检测参数列表
        """
        return self.get_by_condition({"status": status})
    
    def get_by_template_id(self, template_id: int) -> List[DetectionParam]:
        """
        根据委托单模板ID获取检测参数列表，包含关联的项目和对象信息
        :param template_id: 委托单模板ID
        :return: 检测参数列表
        """
        from sqlalchemy.orm import joinedload
        return self.db.query(self.model).filter_by(template_id=template_id).options(
            joinedload(self.model.item).joinedload(DetectionItem.detection_object)
        ).all()
    
    def get_by_id(self, param_id: int, with_relations: bool = False) -> Optional[DetectionParam]:
        """
        根据ID获取检测参数信息
        :param param_id: 检测参数ID
        :param with_relations: 是否加载关联数据（standards和template）
        :return: 检测参数实例，不存在则返回None
        """
        if with_relations:
            from sqlalchemy.orm import joinedload
            return self.db.query(self.model).filter(self.model.param_id == param_id).options(
                joinedload(self.model.standards),
                joinedload(self.model.template),
                joinedload(self.model.item).joinedload(DetectionItem.detection_object)
            ).first()
        return super().get_by_id(param_id)
    
    def get_paginated(self, page: int = 1, limit: int = 10, condition: Optional[Dict[str, Any]] = None) -> tuple:
        """
        分页获取检测参数列表
        :param page: 当前页码，默认1
        :param limit: 每页数量，默认10
        :param condition: 查询条件字典
        :return: (检测参数列表, 总记录数)
        """
        from sqlalchemy.orm import joinedload
        
        query = self.db.query(self.model)
        
        # 应用条件过滤
        if condition:
            query = query.filter_by(**condition)
        
        # 获取总记录数
        total = query.count()
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 获取分页数据，同时加载关联的规范、模板、项目和检测对象信息
        items = query.options(
            joinedload(self.model.standards),
            joinedload(self.model.template),
            joinedload(self.model.item).joinedload(DetectionItem.detection_object)
        ).offset(offset).limit(limit).all()
        
        return items, total
    
    def search(self, search_params: Dict[str, Any], fuzzy_fields: Optional[List[str]] = None, 
              related_fields: Optional[Dict[str, Any]] = None, page: int = 1, limit: int = 10) -> tuple:
        """
        搜索检测参数并分页
        :param search_params: 搜索参数字典
        :param fuzzy_fields: 模糊搜索字段列表
        :param related_fields: 关联表搜索配置
        :param page: 当前页码，默认1
        :param limit: 每页数量，默认10
        :return: (检测参数列表, 总记录数)
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
        
        # 获取总记录数
        total = query.count()
        
        # 计算偏移量并获取分页数据，同时加载关联的规范、模板、项目和检测对象信息
        from sqlalchemy.orm import joinedload
        offset = (page - 1) * limit
        items = query.options(
            joinedload(self.model.standards),
            joinedload(self.model.template),
            joinedload(self.model.item).joinedload(DetectionItem.detection_object)
        ).offset(offset).limit(limit).all()
        
        return items, total
    
    def update_standards(self, param_id: int, standard_ids: List[int]) -> bool:
        """
        更新检测参数关联的检测规范
        :param param_id: 检测参数ID
        :param standard_ids: 检测规范ID列表
        :return: 更新成功返回True，失败返回False
        """
        try:
            from app.models.associations import DetectionParamStandard
            
            # 清除现有关联
            self.db.query(DetectionParamStandard).filter(DetectionParamStandard.param_id == param_id).delete()
            
            # 添加新关联
            if standard_ids:
                for standard_id in standard_ids:
                    param_standard = DetectionParamStandard(
                        param_id=param_id,
                        standard_id=standard_id
                    )
                    self.db.add(param_standard)
            
            # 提交事务
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e


class DetectionItemDAL(BaseDAL):
    """检测项目数据访问层"""
    
    def __init__(self, db, redis):
        super().__init__(db, redis, DetectionItem)
    
    def get_by_name(self, name: str) -> Optional[DetectionItem]:
        """
        根据名称获取检测项目
        :param name: 项目名称
        :return: 检测项目实例，不存在则返回None
        """
        items = self.get_by_condition({"item_name": name})
        return items[0] if items else None


class DetectionStandardDAL(BaseDAL):
    """检测标准数据访问层"""
    
    def __init__(self, db, redis):
        super().__init__(db, redis, DetectionStandard)
    
    def get_by_status(self, status: int) -> List[DetectionStandard]:
        """
        根据状态获取检测标准列表
        :param status: 状态：1=有效，0=作废，2=待生效
        :return: 检测标准列表
        """
        return self.get_by_condition({"status": status})
    
    def get_by_ids(self, standard_ids: List[int]) -> List[DetectionStandard]:
        """
        根据ID列表获取检测标准列表
        :param standard_ids: 检测标准ID列表
        :return: 检测标准列表
        """
        return self.db.query(self.model).filter(self.model.standard_id.in_(standard_ids)).all()
    
    def get_by_code(self, standard_code: str) -> Optional[DetectionStandard]:
        """
        根据规范编号获取检测标准
        :param standard_code: 规范编号
        :return: 检测标准实例，不存在则返回None
        """
        standards = self.get_by_condition({"standard_code": standard_code})
        return standards[0] if standards else None


class CategoryDAL(BaseDAL):
    """分类数据访问层"""
    
    def __init__(self, db, redis):
        super().__init__(db, redis, Category)
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """
        根据名称获取分类
        :param name: 分类名称
        :return: 分类实例，不存在则返回None
        """
        categories = self.get_by_condition({"category_name": name})
        return categories[0] if categories else None
    
    def get_by_parent_id(self, parent_id: int) -> List[Category]:
        """
        根据父分类ID获取子分类列表
        :param parent_id: 父分类ID
        :return: 子分类列表
        """
        return self.get_by_condition({"parent_id": parent_id})
    
    def get_by_status(self, status: int) -> List[Category]:
        """
        根据状态获取分类列表
        :param status: 状态：1=启用，0=禁用
        :return: 分类列表
        """
        return self.get_by_condition({"status": status})
    
    def get_all_with_tree(self) -> List[Category]:
        """
        获取所有分类，并构建为树形结构
        :return: 分类列表
        """
        # 获取所有分类
        categories = self.get_all()
        return categories


class DetectionObjectDAL(BaseDAL):
    """检测对象数据访问层"""
    
    def __init__(self, db, redis):
        super().__init__(db, redis, DetectionObject)
    
    def get_by_name(self, name: str) -> Optional[DetectionObject]:
        """
        根据名称获取检测对象
        :param name: 检测对象名称
        :return: 检测对象实例，不存在则返回None
        """
        objects = self.get_by_condition({"object_name": name})
        return objects[0] if objects else None
    
    def get_by_category_id(self, category_id: int) -> List[DetectionObject]:
        """
        根据分类ID获取检测对象列表
        :param category_id: 分类ID
        :return: 检测对象列表
        """
        return self.get_by_condition({"category_id": category_id})
    
    def get_by_status(self, status: int) -> List[DetectionObject]:
        """
        根据状态获取检测对象列表
        :param status: 状态：1=启用，0=禁用
        :return: 检测对象列表
        """
        return self.get_by_condition({"status": status})
    
    def get_by_ids(self, object_ids: List[int]) -> List[DetectionObject]:
        """
        根据ID列表获取检测对象列表
        :param object_ids: 检测对象ID列表
        :return: 检测对象列表
        """
        return self.db.query(self.model).filter(self.model.object_id.in_(object_ids)).all()
    
    def search(self, keyword: str, status: Optional[int] = None) -> List[DetectionObject]:
        """
        根据关键词搜索检测对象，支持名称和编码搜索，并可按状态过滤
        :param keyword: 搜索关键词
        :param status: 状态过滤：1=启用，0=禁用，None=不过滤
        :return: 检测对象列表
        """
        from sqlalchemy import or_
        
        # 构建缓存键，包含关键词和状态
        cache_key = f"{self.cache_prefix}:search:v1:{keyword}:{status}"
        
        # 尝试从缓存获取
        cached_result = self.get_cache(cache_key)
        if cached_result:
            # 缓存中的数据是序列化的，需要重新查询数据库获取关联的对象
            # 我们可以从缓存中获取ID列表，然后批量查询数据库
            object_ids = [item["object_id"] for item in cached_result]
            if object_ids:
                return self.get_by_ids(object_ids)
        
        # 缓存未命中，执行数据库查询
        query = self.db.query(self.model)
        
        # 构建搜索条件
        conditions = []
        if keyword:
            conditions.append(
                or_(
                    self.model.object_name.ilike(f"%{keyword}%"),
                    self.model.object_code.ilike(f"%{keyword}%")
                )
            )
        
        # 添加状态过滤
        if status is not None:
            conditions.append(self.model.status == status)
        
        if conditions:
            query = query.filter(*conditions)
        
        results = query.all()
        
        # 将结果序列化后存入缓存
        if results:
            serialized_results = [self._serialize_instance(item) for item in results]
            self.set_cache(cache_key, serialized_results)
        
        return results


class DelegationFormTemplateDAL(BaseDAL):
    """委托单模板数据访问层"""
    
    def __init__(self, db, redis):
        super().__init__(db, redis, DelegationFormTemplate)
    
    def get_by_status(self, status: int) -> List[DelegationFormTemplate]:
        """
        根据状态获取委托单模板列表
        :param status: 状态：1=启用，0=禁用
        :return: 委托单模板列表
        """
        return self.get_by_condition({"status": status})
    
    def search(self, search_keyword: str, status: Optional[int] = None) -> List[DelegationFormTemplate]:
        """
        根据关键词搜索委托单模板，支持按模板名称和编号搜索和状态过滤
        :param search_keyword: 搜索关键词
        :param status: 状态过滤：1=启用，0=禁用，None=不过滤
        :return: 委托单模板列表
        """
        # 配置搜索参数
        search_params = {
            "template_name": search_keyword,
            "template_code": search_keyword
        }
        
        # 如果status不为None，添加到搜索参数中
        if status is not None:
            search_params["status"] = status
        
        # 配置模糊搜索字段
        fuzzy_fields = ["template_name", "template_code"]
        
        # 配置关联表搜索
        related_fields = {}
        
        return self.base_search(search_params, fuzzy_fields, related_fields)
    
    def base_search(self, search_params: Dict[str, Any], fuzzy_fields: Optional[List[str]] = None, related_fields: Optional[Dict[str, Any]] = None) -> List[DelegationFormTemplate]:
        """
        调用父类的search方法进行搜索
        :param search_params: 搜索参数字典
        :param fuzzy_fields: 需要进行模糊搜索的字段列表
        :param related_fields: 关联表搜索配置
        :return: 搜索结果列表
        """
        return super().search(search_params, fuzzy_fields, related_fields)
