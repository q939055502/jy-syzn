from fastapi import APIRouter, HTTPException
from app.schemas.detection import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ResponseModel, ListResponseModel
)
from app.services.detection import CategoryService

# 创建路由实例
router = APIRouter()


@router.get("/categories", response_model=ListResponseModel[CategoryResponse])
def get_categories(page: int = 1, limit: int = 100):
    """获取所有分类（树形结构），支持分页"""
    categories, error = CategoryService.get_category_tree()
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # 处理分页
    start = (page - 1) * limit
    end = start + limit
    paginated_categories = categories[start:end]
    
    return {"data": paginated_categories, "total": len(categories), "message": "获取分类列表成功"}


@router.get("/categories/{category_id}", response_model=ResponseModel[CategoryResponse])
def get_category(category_id: int):
    """获取单个分类"""
    category, error = CategoryService.get_by_id(category_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": category, "message": "获取分类成功"}


@router.post("/categories", response_model=ResponseModel[CategoryResponse], status_code=201)
def create_category(category: CategoryCreate):
    """创建分类"""
    category_obj, error = CategoryService.create(category.model_dump())
    if error:
        if "不能为空" in error:
            raise HTTPException(status_code=400, detail=error)
        if "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": category_obj, "message": "创建分类成功", "code": 201}


@router.put("/categories/{category_id}", response_model=ResponseModel[CategoryResponse])
def update_category(category_id: int, category: CategoryUpdate):
    """更新分类"""
    category_obj, error = CategoryService.update(category_id, category.model_dump(exclude_unset=True))
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        if "不能为空" in error:
            raise HTTPException(status_code=400, detail=error)
        if "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": category_obj, "message": "更新分类成功"}


@router.delete("/categories/{category_id}", response_model=ResponseModel, status_code=200)
def delete_category(category_id: int):
    """删除分类"""
    success, error = CategoryService.delete(category_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        if "存在" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"message": "删除分类成功"}
