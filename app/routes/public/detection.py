from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.schemas.detection import (
    ListResponseModel
)
from app.services.detection import (
    CategoryService,
    DetectionObjectService,
    DetectionItemService,
    DetectionParamService
)
from app.services.utils.link_generator import LinkGeneratorService

# 创建路由实例
router = APIRouter(prefix="/detection", tags=["public/detection"])


@router.get("/categories", response_model=ListResponseModel[dict])
async def get_public_categories():
    """
    获取所有分类的（id和名称）列表，按排序号顺序返回（只返回状态为启用的数据）
    """
    try:
        # 获取所有分类
        categories, error = CategoryService.get_all()
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 确保categories不是None
        if not categories:
            categories = []
        
        # 过滤出状态为启用的数据，按排序号排序
        enabled_categories = sorted(
            [cat for cat in categories if cat['status'] == 1],
            key=lambda x: x['sort_order']
        )
        
        # 只返回id和名称
        result = [{
            "category_id": cat["category_id"],
            "category_name": cat["category_name"]
        } for cat in enabled_categories]
        
        return {
            "code": 200,
            "message": "获取分类列表成功",
            "data": result,
            "total": len(result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")


@router.get("/categories/{category_id}/objects", response_model=ListResponseModel[dict])
async def get_public_category_objects(category_id: int):
    """
    获取某一ID分类下所有检测对象的（id和名称）列表，按排序号顺序返回（只返回状态为启用的数据）
    """
    try:
        # 获取分类下的所有检测对象
        objects, error = DetectionObjectService.get_by_category_id(category_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 确保objects不是None
        if not objects:
            objects = []
        
        # 过滤出状态为启用的数据，按排序号排序
        enabled_objects = sorted(
            [obj for obj in objects if obj['status'] == 1],
            key=lambda x: x['sort_order']
        )
        
        # 只返回id和名称
        result = [{
            "object_id": obj['object_id'],
            "object_name": obj['object_name']
        } for obj in enabled_objects]
        
        return {
            "code": 200,
            "message": "获取检测对象列表成功",
            "data": result,
            "total": len(result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测对象列表失败: {str(e)}")


@router.get("/objects/{object_id}/items", response_model=ListResponseModel[dict])
async def get_public_object_items(object_id: int):
    """
    获取某一ID检测对象下所有检测项目的（id和名称）列表，按排序号顺序返回（只返回状态为启用的数据）
    """
    try:
        # 获取检测对象下的所有检测项目
        items, error = DetectionItemService.get_by_object_id(object_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 确保items不是None
        if not items:
            items = []
        
        # 过滤出状态为启用的数据，按排序号排序
        enabled_items = sorted(
            [item for item in items if item['status'] == 1],
            key=lambda x: x['sort_order']
        )
        
        # 只返回id和名称
        result = [{
            "item_id": item['item_id'],
            "item_name": item['item_name']
        } for item in enabled_items]
        
        return {
            "code": 200,
            "message": "获取检测项目列表成功",
            "data": result,
            "total": len(result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测项目列表失败: {str(e)}")


@router.get("/items/{item_id}/templates", response_model=ListResponseModel["TemplateDownloadInfo"])
async def get_item_templates(item_id: int):
    """
    获取检测项目下所有检测参数关联的委托单模板列表
    :param item_id: 检测项目ID
    :return: 委托单模板列表，包含id、name、code、下载链接
    """
    try:
        # 获取检测项目下的所有检测参数
        params, total, error = DetectionParamService.get_by_item_id(item_id, page=1, limit=1000)
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 确保params不是None
        if not params:
            params = []
        
        # 过滤出状态为启用的数据
        enabled_params = [param for param in params if param.status == 1]
        
        # 收集所有唯一的委托单模板
        template_dict = {}
        for param in enabled_params:
            # 检查是否关联了委托单模板
            if hasattr(param, 'template') and param.template:
                template = param.template
                if template.template_id not in template_dict and template.file_path:
                    # 生成带签名的下载链接
                    download_url = LinkGeneratorService.generate_signed_url(template.file_path)
                    
                    # 将模板信息添加到字典中，去重
                    template_dict[template.template_id] = {
                        "id": template.template_id,
                        "name": template.template_name,
                        "code": template.template_code,
                        "download_url": download_url
                    }
        
        # 将字典转换为列表
        result = list(template_dict.values())
        
        return {
            "code": 200,
            "message": "获取委托单模板列表成功",
            "data": result,
            "total": len(result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取委托单模板列表失败: {str(e)}")


@router.get("/categories/objects", response_model=ListResponseModel[dict])
async def get_categories_with_objects():
    """
    获取所有分类及其下的检测对象列表
    :return: 分类列表，每个分类包含id、name和objects字段，objects是检测对象列表
    """
    try:
        # 获取所有分类
        categories, error = CategoryService.get_all()
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 确保categories不是None
        if not categories:
            categories = []
        
        # 过滤出状态为启用的数据，按排序号排序
        enabled_categories = sorted(
            [cat for cat in categories if cat['status'] == 1],
            key=lambda x: x['sort_order']
        )
        
        # 结果列表
        result = []
        
        # 遍历每个分类，获取其下的检测对象
        for cat in enabled_categories:
            # 获取分类下的检测对象
            objects, error = DetectionObjectService.get_by_category_id(cat['category_id'])
            if error:
                raise HTTPException(status_code=500, detail=error)
            
            # 确保objects不是None
            if not objects:
                objects = []
            
            # 过滤出状态为启用的数据，按排序号排序
            enabled_objects = sorted(
                [obj for obj in objects if obj['status'] == 1],
                key=lambda x: x['sort_order']
            )
            
            # 构造分类及其检测对象信息
            category_info = {
                "id": cat['category_id'],
                "name": cat['category_name'],
                "objects": [{
                    "id": obj['object_id'],
                    "name": obj['object_name'],
                    "code": obj['object_code']
                } for obj in enabled_objects]
            }
            
            # 添加到结果列表
            result.append(category_info)
        
        return {
            "code": 200,
            "message": "获取分类及其检测对象列表成功",
            "data": result,
            "total": len(result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类及其检测对象列表失败: {str(e)}")


@router.get("/items/search", response_model=ListResponseModel[dict])
async def search_items(
    keyword: Optional[str] = Query(None, description="搜索关键词，支持检测对象、规范名称、规范代码、检测参数")
):
    """
    根据关键词搜索检测项目列表，支持按检测对象、规范名称、规范代码、检测参数搜索
    :param keyword: 搜索关键词
    :return: 检测项目列表，格式与get_public_object_items一致
    """
    try:
        # 获取所有检测项目
        items, error = DetectionItemService.get_all()
        if error:
            raise HTTPException(status_code=500, detail=error)
        
        # 确保items不是None
        if not items:
            items = []
        
        # 过滤出状态为启用的数据
        enabled_items = [item for item in items if item['status'] == 1]
        
        # 如果没有关键词，直接返回所有启用的检测项目
        if not keyword:
            # 只返回id和名称，与get_public_object_items接口一致
            result = [{
                "item_id": item['item_id'],
                "item_name": item['item_name']
            } for item in enabled_items]
            
            return {
                "code": 200,
                "message": "获取检测项目列表成功",
                "data": result,
                "total": len(result)
            }
        
        # 处理关键词搜索
        keyword_lower = keyword.lower()
        
        # 搜索结果列表
        search_result = []
        
        # 遍历所有启用的检测项目
        for item in enabled_items:
            # 搜索条件：检测对象名称、规范名称、规范代码、检测参数
            # 这里简化处理，实际可能需要关联查询多个表
            # 目前先基于item中的object_name进行搜索
            if keyword_lower in item['object_name'].lower() or keyword_lower in item['item_name'].lower():
                search_result.append({
                    "item_id": item['item_id'],
                    "item_name": item['item_name']
                })
        
        return {
            "code": 200,
            "message": "搜索检测项目列表成功",
            "data": search_result,
            "total": len(search_result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索检测项目列表失败: {str(e)}")
