# 状态管理工具类
# 集中处理检测系统中各类实体的递归状态管理逻辑


class StatusManager:
    """状态管理工具类，处理各类实体的递归状态管理"""
    
    @staticmethod
    def recursively_disable_category(category_id, db, redis):
        """
        递归禁用分类及其所有子分类、检测对象、检测项目和检测参数
        :param category_id: 分类ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import CategoryDAL, DetectionObjectDAL, DetectionItemDAL, DetectionParamDAL
        
        # 获取DAL实例
        category_dal = CategoryDAL(db, redis)
        object_dal = DetectionObjectDAL(db, redis)
        item_dal = DetectionItemDAL(db, redis)
        param_dal = DetectionParamDAL(db, redis)
        
        # 1. 递归禁用所有子分类
        children = category_dal.get_by_parent_id(category_id)
        for child in children:
            StatusManager.recursively_disable_category(child.category_id, db, redis)
        
        # 2. 禁用所有关联的检测对象
        objects = object_dal.get_by_category_id(category_id)
        for obj in objects:
            # 禁用检测对象
            object_dal.update(obj.object_id, {"status": 0})
            
            # 3. 禁用关联的检测项目
            items = item_dal.get_by_condition({"object_id": obj.object_id})
            for item in items:
                # 禁用检测项目
                item_dal.update(item.item_id, {"status": 0})
                
                # 4. 禁用关联的检测参数
                params = param_dal.get_by_condition({"item_id": item.item_id})
                for param in params:
                    # 禁用检测参数
                    param_dal.update(param.param_id, {"status": 0})
        
        # 5. 最后禁用当前分类
        category_dal.update(category_id, {"status": 0})
    
    @staticmethod
    def recursively_enable_category(category_id, db, redis):
        """
        递归启用分类及其所有上级分类
        :param category_id: 分类ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import CategoryDAL
        
        # 获取DAL实例
        category_dal = CategoryDAL(db, redis)
        
        # 获取当前分类
        current_category = category_dal.get_by_id(category_id)
        if not current_category:
            return
        
        # 如果当前分类已经启用，不需要继续处理
        if current_category.status == 1:
            return
        
        # 1. 启用当前分类
        category_dal.update(category_id, {"status": 1})
        
        # 2. 递归启用上级分类
        if current_category.parent_id:
            StatusManager.recursively_enable_category(current_category.parent_id, db, redis)
    
    @staticmethod
    def recursively_disable_detection_object(object_id, db, redis):
        """
        递归禁用检测对象及其所有检测项目和检测参数
        :param object_id: 检测对象ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import DetectionObjectDAL, DetectionItemDAL, DetectionParamDAL
        
        # 获取DAL实例
        object_dal = DetectionObjectDAL(db, redis)
        item_dal = DetectionItemDAL(db, redis)
        param_dal = DetectionParamDAL(db, redis)
        
        # 2. 禁用所有关联的检测项目
        items = item_dal.get_by_condition({"object_id": object_id})
        for item in items:
            # 禁用检测项目
            item_dal.update(item.item_id, {"status": 0})
            
            # 3. 禁用所有关联的检测参数
            params = param_dal.get_by_condition({"item_id": item.item_id})
            for param in params:
                # 禁用检测参数
                param_dal.update(param.param_id, {"status": 0})
    
    @staticmethod
    def recursively_enable_detection_object(object_id, db, redis):
        """
        递归启用检测对象及其所属分类
        :param object_id: 检测对象ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import DetectionObjectDAL, CategoryDAL
        
        # 获取DAL实例
        object_dal = DetectionObjectDAL(db, redis)
        category_dal = CategoryDAL(db, redis)
        
        # 获取检测对象
        detection_object = object_dal.get_by_id(object_id)
        if not detection_object:
            return
        
        # 1. 启用当前检测对象
        object_dal.update(object_id, {"status": 1})
        
        # 2. 递归启用所属分类
        if detection_object.category_id:
            StatusManager.recursively_enable_category(detection_object.category_id, db, redis)
    
    @staticmethod
    def recursively_disable_detection_item(item_id, db, redis):
        """
        递归禁用检测项目及其所有检测参数
        :param item_id: 检测项目ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import DetectionItemDAL, DetectionParamDAL
        
        # 获取DAL实例
        item_dal = DetectionItemDAL(db, redis)
        param_dal = DetectionParamDAL(db, redis)
        
        # 2. 禁用所有关联的检测参数
        params = param_dal.get_by_condition({"item_id": item_id})
        for param in params:
            # 禁用检测参数
            param_dal.update(param.param_id, {"status": 0})
    
    @staticmethod
    def recursively_enable_detection_item(item_id, db, redis):
        """
        递归启用检测项目及其所属检测对象和分类
        :param item_id: 检测项目ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import DetectionItemDAL, DetectionObjectDAL
        
        # 获取DAL实例
        item_dal = DetectionItemDAL(db, redis)
        object_dal = DetectionObjectDAL(db, redis)
        
        # 获取检测项目
        detection_item = item_dal.get_by_id(item_id)
        if not detection_item:
            return
        
        # 1. 启用当前检测项目
        item_dal.update(item_id, {"status": 1})
        
        # 2. 递归启用所属检测对象
        if detection_item.object_id:
            StatusManager.recursively_enable_detection_object(detection_item.object_id, db, redis)
    
    @staticmethod
    def recursively_disable_detection_param(param_id, db, redis):
        """
        禁用检测参数
        :param param_id: 检测参数ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import DetectionParamDAL
        
        # 获取DAL实例
        param_dal = DetectionParamDAL(db, redis)
        
        # 禁用当前检测参数
        param_dal.update(param_id, {"status": 0})
    
    @staticmethod
    def recursively_enable_detection_param(param_id, db, redis):
        """
        递归启用检测参数及其所属检测项目、检测对象和分类
        :param param_id: 检测参数ID
        :param db: 数据库会话
        :param redis: Redis客户端
        """
        from app.dal.detection_dal import DetectionParamDAL
        
        # 获取DAL实例
        param_dal = DetectionParamDAL(db, redis)
        
        # 获取检测参数
        detection_param = param_dal.get_by_id(param_id)
        if not detection_param:
            return
        
        # 1. 启用当前检测参数
        param_dal.update(param_id, {"status": 1})
        
        # 2. 递归启用所属检测项目
        if detection_param.item_id:
            StatusManager.recursively_enable_detection_item(detection_param.item_id, db, redis)