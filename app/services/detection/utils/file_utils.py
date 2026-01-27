# 文件工具类
# 包含文件和目录相关的工具方法，如目录检查和创建、文件操作等

from pathlib import Path
import os
import shutil


def ensure_dir(dir_path):
    """
    检查目录是否存在，不存在则创建
    
    :param dir_path: 目录路径，可以是字符串或Path对象
    :return: 无返回值
    """
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)


def get_file_extension(filename):
    """
    获取文件的扩展名
    
    :param filename: 文件名
    :return: 扩展名（不含点），如果没有扩展名则返回空字符串
    """
    return Path(filename).suffix[1:] if Path(filename).suffix else ""


def is_allowed_file(filename):
    """
    检查文件是否为允许的格式
    
    :param filename: 文件名
    :return: True如果是允许的格式，否则返回False
    """
    allowed_extensions = {'doc', 'docx', 'xls', 'xlsx'}
    file_extension = get_file_extension(filename).lower()
    return file_extension in allowed_extensions


def move_file(src_path, dest_path):
    """
    移动文件
    
    :param src_path: 源文件路径
    :param dest_path: 目标文件路径
    :return: 无返回值
    """
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    
    # 确保目标目录存在
    ensure_dir(dest_path.parent)
    
    # 如果目标文件已存在，先删除
    if dest_path.exists():
        dest_path.unlink()
    
    # 移动文件
    shutil.move(str(src_path), str(dest_path))


def copy_file(src_path, dest_path):
    """
    复制文件
    
    :param src_path: 源文件路径
    :param dest_path: 目标文件路径
    :return: 无返回值
    """
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    
    # 确保目标目录存在
    ensure_dir(dest_path.parent)
    
    # 复制文件
    shutil.copy2(str(src_path), str(dest_path))


def delete_file(file_path):
    """
    删除文件，如果文件不存在则忽略
    
    :param file_path: 文件路径
    :return: 无返回值
    """
    file_path = Path(file_path)
    if file_path.exists():
        file_path.unlink()


def generate_file_path(item_name, template_name, template_code, file_extension):
    """
    生成委托单模板的文件路径
    
    :param item_name: 检测项目名称
    :param template_name: 模板名称
    :param template_code: 模板编号
    :param file_extension: 文件扩展名
    :return: 生成的文件路径
    """
    # 构建文件名：模板名称 + 模板编号 + 扩展名
    filename = f"{template_name}{template_code}.{file_extension}"
    
    # 构建完整路径
    return Path("static") / "templates" / item_name / filename


def get_absolute_file_path(relative_path):
    """
    获取文件的绝对路径
    
    :param relative_path: 相对路径
    :return: 绝对路径
    """
    # 向上走5级目录：file_utils.py -> utils -> detection -> services -> app -> 项目根目录
    return Path(__file__).parent.parent.parent.parent.parent / relative_path


def get_web_file_path(absolute_path):
    """
    获取用于Web访问的文件路径
    
    :param absolute_path: 绝对路径
    :return: Web访问路径
    """
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent.parent
    
    # 将绝对路径转换为相对路径
    relative_path = absolute_path.relative_to(root_dir)
    
    # 转换为Web路径格式（使用正斜杠）
    return f"/{relative_path.as_posix()}"