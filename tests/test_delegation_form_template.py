import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接从app.py文件导入app实例
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

# 创建测试客户端
client = TestClient(app)

# 测试文件路径
TEST_FILES_DIR = Path("D:\\Projects\\jy_syzn\\测试数据")
TEST_FILES = [
    "委托单文件测试.doc",
    "委托单文件测试.docx",
    "委托单文件测试.xls",
    "委托单文件测试.xlsx"
]

# 不允许的文件格式
INVALID_FILE = "invalid_file.pdf"

# 测试用的模板数据
TEST_TEMPLATE_DATA = {
    "template_name": "测试模板",
    "template_version": "V1.0",
    "item_id": 1,
    "file_type": "xlsx",
    "upload_user": "admin",
    "is_default": False,
    "status": 1,
    "remark": "测试模板"
}

# 获取token
@pytest.fixture(scope="module")
def token():
    response = client.post(
        "/api/auth/token",
        data={"username": "aaa", "password": "aaa"}
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]

# 测试创建委托单模板，使用四种测试文件
def test_create_template_with_valid_files(token):
    for test_file in TEST_FILES:
        file_path = TEST_FILES_DIR / test_file
        assert file_path.exists(), f"测试文件 {test_file} 不存在"
        
        # 获取文件扩展名
        file_extension = file_path.suffix[1:]
        
        # 更新文件类型
        test_data = TEST_TEMPLATE_DATA.copy()
        test_data["file_type"] = file_extension
        
        # 发送请求
        with open(file_path, "rb") as f:
            response = client.post(
                "/api/detection/templates",
                headers={"Authorization": f"Bearer {token}"},
                data=test_data,
                files={"file": (test_file, f, f"application/vnd.ms-{file_extension}")}
            )
        
        # 验证响应
        assert response.status_code == 201, f"创建模板失败，文件：{test_file}，响应：{response.text}"
        assert "data" in response.json()
        assert "template_id" in response.json()["data"]

# 测试更新委托单模板，使用四种测试文件
def test_update_template_with_valid_files(token):
    # 先创建一个模板
    test_file = TEST_FILES[0]
    file_path = TEST_FILES_DIR / test_file
    file_extension = file_path.suffix[1:]
    
    test_data = TEST_TEMPLATE_DATA.copy()
    test_data["file_type"] = file_extension
    
    with open(file_path, "rb") as f:
        create_response = client.post(
            "/api/detection/templates",
            headers={"Authorization": f"Bearer {token}"},
            data=test_data,
            files={"file": (test_file, f, f"application/vnd.ms-{file_extension}")}
        )
    
    assert create_response.status_code == 201
    template_id = create_response.json()["data"]["template_id"]
    
    # 使用不同的文件更新模板
    for test_file in TEST_FILES[1:]:
        file_path = TEST_FILES_DIR / test_file
        assert file_path.exists(), f"测试文件 {test_file} 不存在"
        
        # 获取文件扩展名
        file_extension = file_path.suffix[1:]
        
        # 更新文件类型
        update_data = {
            "template_name": "更新后的测试模板",
            "file_type": file_extension
        }
        
        # 发送请求
        with open(file_path, "rb") as f:
            response = client.put(
                f"/api/detection/templates/{template_id}",
                headers={"Authorization": f"Bearer {token}"},
                data=update_data,
                files={"file": (test_file, f, f"application/vnd.ms-{file_extension}")}
            )
        
        # 验证响应
        assert response.status_code == 200, f"更新模板失败，文件：{test_file}，响应：{response.text}"
        assert "data" in response.json()
        assert response.json()["data"]["template_id"] == template_id
        assert response.json()["data"]["template_name"] == "更新后的测试模板"

# 测试创建委托单模板，使用不允许的文件格式
def test_create_template_with_invalid_file(token):
    # 创建一个无效的PDF文件
    invalid_file_path = TEST_FILES_DIR / INVALID_FILE
    invalid_file_path.touch(exist_ok=True)
    
    # 发送请求
    with open(invalid_file_path, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    
    with open(invalid_file_path, "rb") as f:
        response = client.post(
            "/api/detection/templates",
            headers={"Authorization": f"Bearer {token}"},
            data=TEST_TEMPLATE_DATA,
            files={"file": (INVALID_FILE, f, "application/pdf")}
        )
    
    # 验证响应
    assert response.status_code == 400
    assert "不支持的文件格式" in response.json()["detail"]
    
    # 删除无效文件
    invalid_file_path.unlink()

# 测试更新委托单模板，使用不允许的文件格式
def test_update_template_with_invalid_file(token):
    # 先创建一个模板
    test_file = TEST_FILES[0]
    file_path = TEST_FILES_DIR / test_file
    file_extension = file_path.suffix[1:]
    
    test_data = TEST_TEMPLATE_DATA.copy()
    test_data["file_type"] = file_extension
    
    with open(file_path, "rb") as f:
        create_response = client.post(
            "/api/detection/templates",
            headers={"Authorization": f"Bearer {token}"},
            data=test_data,
            files={"file": (test_file, f, f"application/vnd.ms-{file_extension}")}
        )
    
    assert create_response.status_code == 201
    template_id = create_response.json()["data"]["template_id"]
    
    # 创建一个无效的PDF文件
    invalid_file_path = TEST_FILES_DIR / INVALID_FILE
    invalid_file_path.touch(exist_ok=True)
    
    # 发送请求
    with open(invalid_file_path, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    
    with open(invalid_file_path, "rb") as f:
        response = client.put(
            f"/api/detection/templates/{template_id}",
            headers={"Authorization": f"Bearer {token}"},
            data={"template_name": "更新后的测试模板"},
            files={"file": (INVALID_FILE, f, "application/pdf")}
        )
    
    # 验证响应
    assert response.status_code == 400
    assert "不支持的文件格式" in response.json()["detail"]
    
    # 删除无效文件
    invalid_file_path.unlink()