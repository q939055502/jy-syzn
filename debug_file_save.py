#!/usr/bin/env python3
"""
调试文件保存逻辑
"""

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

# 模拟服务层代码
from app.services.detection.utils.file_utils import generate_file_path, get_absolute_file_path, ensure_dir

# 测试数据
item_name = "水泥检测"
template_name = "测试模板"
template_version = "v1.0"
file_type = ".doc"

# 1. 移除file_type中的点
file_extension = file_type[1:] if file_type.startswith('.') else file_type
print(f"文件扩展名：{file_extension}")

# 2. 生成文件路径
file_path = generate_file_path(item_name, template_name, template_version, file_extension)
print(f"生成的相对路径：{file_path}")

# 3. 获取绝对路径
absolute_file_path = get_absolute_file_path(file_path)
print(f"生成的绝对路径：{absolute_file_path}")

# 4. 确保目录存在
print(f"\n目录检查：")
print(f"目录路径：{absolute_file_path.parent}")
print(f"目录是否存在：{absolute_file_path.parent.exists()}")

# 5. 确保目录存在
ensure_dir(absolute_file_path.parent)
print(f"确保目录存在后，目录是否存在：{absolute_file_path.parent.exists()}")

# 6. 模拟文件上传
print(f"\n模拟文件上传：")

# 测试文件路径
test_file_path = Path("d:/Projects/jy_syzn/测试数据/委托单文件测试.doc")
print(f"测试文件路径：{test_file_path}")
print(f"测试文件是否存在：{test_file_path.exists()}")

# 7. 保存文件到临时位置
print(f"\n保存文件到临时位置：")
with NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
    shutil.copyfileobj(open(test_file_path, "rb"), temp_file)
    temp_file_path = temp_file.name
    print(f"临时文件路径：{temp_file_path}")
    print(f"临时文件是否存在：{Path(temp_file_path).exists()}")

# 8. 保存文件到最终位置
print(f"\n保存文件到最终位置：")
print(f"从：{temp_file_path}")
print(f"到：{absolute_file_path}")

try:
    shutil.copy2(temp_file_path, absolute_file_path)
    print(f"文件复制成功")
    print(f"最终文件是否存在：{absolute_file_path.exists()}")
    print(f"最终文件大小：{absolute_file_path.stat().st_size} 字节")
except Exception as e:
    print(f"文件复制失败：{str(e)}")

# 9. 清理临时文件
print(f"\n清理临时文件：")
if Path(temp_file_path).exists():
    Path(temp_file_path).unlink()
    print(f"临时文件已删除")
else:
    print(f"临时文件不存在")
