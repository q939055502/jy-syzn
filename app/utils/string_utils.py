# 字符串处理工具函数
# 包含生成随机字符串、清理字符串等功能

import random
import string
import re


def generate_random_string(length=16, chars=None):
    """
    生成随机字符串
    :param length: 字符串长度，默认为16
    :param chars: 字符集，默认为大小写字母和数字
    :return: 随机字符串
    """
    if chars is None:
        chars = string.ascii_letters + string.digits
    
    return ''.join(random.choice(chars) for _ in range(length))


def sanitize_string(s, allowed_chars=None):
    """
    清理字符串，移除或替换不允许的字符
    :param s: 输入字符串
    :param allowed_chars: 允许的字符正则表达式，默认为字母、数字、空格和常见标点符号
    :return: 清理后的字符串
    """
    if s is None:
        return None
    
    if allowed_chars is None:
        # 默认为字母、数字、空格和常见标点符号
        allowed_chars = r'[^a-zA-Z0-9\s\.,!\?\-\_\(\)]'
    
    return re.sub(allowed_chars, '', s)


def truncate_string(s, max_length=100, suffix='...'):
    """
    截断字符串到指定长度
    :param s: 输入字符串
    :param max_length: 最大长度
    :param suffix: 截断后的后缀
    :return: 截断后的字符串
    """
    if s is None:
        return None
    
    if len(s) <= max_length:
        return s
    
    return s[:max_length - len(suffix)] + suffix


def capitalize_sentence(s):
    """
    将字符串中每个句子的首字母大写
    :param s: 输入字符串
    :return: 处理后的字符串
    """
    if s is None:
        return None
    
    # 使用正则表达式将每个句子的首字母大写
    return re.sub(r'([.!?]\s+|^)([a-z])', lambda match: match.group(1) + match.group(2).upper(), s)
