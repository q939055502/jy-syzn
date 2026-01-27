# 验证工具函数
# 包含电子邮件、密码和手机号码的验证功能

import re


def validate_email(email):
    """
    验证电子邮件格式
    :param email: 电子邮件地址
    :return: 是否有效
    """
    if not email:
        return False
    
    # 简单的电子邮件格式验证正则表达式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_password(password, min_length=8, require_digit=True, require_uppercase=True, require_lowercase=True):
    """
    验证密码强度
    :param password: 密码
    :param min_length: 最小长度
    :param require_digit: 是否需要包含数字
    :param require_uppercase: 是否需要包含大写字母
    :param require_lowercase: 是否需要包含小写字母
    :return: 验证结果（布尔值）和错误信息
    """
    errors = []
    
    if not password:
        errors.append('密码不能为空')
    elif len(password) < min_length:
        errors.append(f'密码长度不能少于{min_length}个字符')
    
    if require_digit and not any(char.isdigit() for char in password):
        errors.append('密码必须包含至少一个数字')
    
    if require_uppercase and not any(char.isupper() for char in password):
        errors.append('密码必须包含至少一个大写字母')
    
    if require_lowercase and not any(char.islower() for char in password):
        errors.append('密码必须包含至少一个小写字母')
    
    return len(errors) == 0, errors


def validate_phone(phone):
    """
    验证手机号码格式（支持国内手机号）
    :param phone: 手机号码
    :return: 是否有效
    """
    if not phone:
        return False
    
    # 国内手机号码格式验证正则表达式
    phone_pattern = r'^1[3-9]\d{9}$'
    return re.match(phone_pattern, phone) is not None


def validate_username(username, min_length=3, max_length=20):
    """
    验证用户名格式
    :param username: 用户名
    :param min_length: 最小长度
    :param max_length: 最大长度
    :return: 是否有效
    """
    if not username:
        return False
    
    # 用户名格式验证正则表达式（只允许字母、数字、下划线，且不能以数字开头）
    username_pattern = fr'^[a-zA-Z_][a-zA-Z0-9_]{{{min_length-1},{max_length-1}}}$'
    return re.match(username_pattern, username) is not None
