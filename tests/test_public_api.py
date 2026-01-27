import pytest
from fastapi.testclient import TestClient
import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 直接导入app.py文件
import importlib.util

# 创建一个模块规范
app_py_path = os.path.join(project_root, "app.py")
spec = importlib.util.spec_from_file_location("app_module", app_py_path)
app_module = importlib.util.module_from_spec(spec)
sys.modules["app_module"] = app_module
spec.loader.exec_module(app_module)

# 从导入的模块中获取app对象
app = app_module.app

client = TestClient(app)


def test_get_public_categories():
    """测试获取所有分类列表接口"""
    response = client.get("/api/public/detection/categories")
    assert response.status_code == 200
    assert "code" in response.json()
    assert response.json()["code"] == 200
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)


def test_get_public_category_objects():
    """测试获取分类下的检测对象接口"""
    # 先获取一个有效的分类ID
    categories_response = client.get("/api/public/detection/categories")
    categories = categories_response.json()["data"]
    
    if categories:
        category_id = categories[0]["category_id"]
        response = client.get(f"/api/public/detection/categories/{category_id}/objects")
        assert response.status_code == 200
        assert "code" in response.json()
        assert response.json()["code"] == 200
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)


def test_get_public_object_items():
    """测试获取检测对象下的检测项目接口"""
    # 先获取一个有效的分类ID
    categories_response = client.get("/api/public/detection/categories")
    categories = categories_response.json()["data"]
    
    if categories:
        category_id = categories[0]["category_id"]
        # 获取该分类下的检测对象
        objects_response = client.get(f"/api/public/detection/categories/{category_id}/objects")
        objects = objects_response.json()["data"]
        
        if objects:
            object_id = objects[0]["object_id"]
            response = client.get(f"/api/public/detection/objects/{object_id}/items")
            assert response.status_code == 200
            assert "code" in response.json()
            assert response.json()["code"] == 200
            assert "data" in response.json()
            assert isinstance(response.json()["data"], list)


def test_get_public_item_params():
    """测试获取检测项目下的检测参数接口"""
    # 先获取一个有效的分类ID
    categories_response = client.get("/api/public/detection/categories")
    categories = categories_response.json()["data"]
    
    if categories:
        category_id = categories[0]["category_id"]
        # 获取该分类下的检测对象
        objects_response = client.get(f"/api/public/detection/categories/{category_id}/objects")
        objects = objects_response.json()["data"]
        
        if objects:
            object_id = objects[0]["object_id"]
            # 获取该检测对象下的检测项目
            items_response = client.get(f"/api/public/detection/objects/{object_id}/items")
            items = items_response.json()["data"]
            
            if items:
                item_id = items[0]["item_id"]
                # 测试获取委托单模板列表接口
                response = client.get(f"/api/public/detection/items/{item_id}/templates")
                assert response.status_code == 200
                assert "code" in response.json()
                assert response.json()["code"] == 200
                assert "data" in response.json()
                assert isinstance(response.json()["data"], list)


def test_get_categories_with_objects():
    """测试获取分类及其检测对象列表接口"""
    response = client.get("/api/public/detection/categories/objects")
    assert response.status_code == 200
    assert "code" in response.json()
    assert response.json()["code"] == 200
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)
    
    # 验证返回的数据结构
    categories = response.json()["data"]
    for category in categories:
        assert "id" in category
        assert "name" in category
        assert "objects" in category
        assert isinstance(category["objects"], list)
        
        # 验证检测对象的数据结构
        for obj in category["objects"]:
            assert "id" in obj
            assert "name" in obj
            assert "code" in obj
