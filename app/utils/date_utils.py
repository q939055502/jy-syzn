# 日期处理工具函数
# 包含日期格式化、解析和获取当前时间等功能

from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_current_datetime(tz='UTC'):
    """
    获取当前时间
    :param tz: 时区，默认为UTC
    :return: 当前时间的datetime对象
    """
    return datetime.now(ZoneInfo(tz))


def format_date(dt, fmt='%Y-%m-%d %H:%M:%S'):
    """
    格式化日期
    :param dt: datetime或date对象
    :param fmt: 格式化字符串，默认为'%Y-%m-%d %H:%M:%S'
    :return: 格式化后的日期字符串
    """
    if dt is None:
        return None
    return dt.strftime(fmt)


def parse_date(date_str, fmt='%Y-%m-%d %H:%M:%S'):
    """
    解析日期字符串为datetime对象
    :param date_str: 日期字符串
    :param fmt: 日期格式，默认为'%Y-%m-%d %H:%M:%S'
    :return: datetime对象
    """
    if not date_str:
        return None
    return datetime.strptime(date_str, fmt)


def get_date_range(start_date, end_date):
    """
    获取两个日期之间的所有日期
    :param start_date: 开始日期（date对象）
    :param end_date: 结束日期（date对象）
    :return: 日期列表
    """
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date = current_date + timedelta(days=1)
    return dates


def get_iso8601_datetime(dt=None, tz='UTC'):
    """
    获取 ISO 8601 格式的带时区日期时间字符串
    常规业务中优先使用此方法，提供简单直观无歧义的日期时间表示
    
    :param dt: datetime 对象，默认为当前时间
    :param tz: 时区，默认为UTC
    :return: ISO 8601 格式的日期时间字符串
    """
    try:
        if dt is None:
            dt = get_current_datetime(tz)
        elif dt.tzinfo is None:
            # 如果传入的 datetime 对象没有时区信息，添加指定时区
            dt = dt.replace(tzinfo=ZoneInfo(tz))
        return dt.isoformat()
    except ZoneInfoNotFoundError:
        # 处理无效时区名称，回退到UTC时区
        print(f"警告: 无效的时区名称 '{tz}'，已回退到UTC时区")
        if dt is None:
            dt = get_current_datetime('UTC')
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.isoformat()
    except Exception as e:
        # 处理其他可能的异常
        print(f"警告: 日期时间格式化时发生错误: {str(e)}")
        # 回退到简单的ISO格式，不带时区信息
        if dt is None:
            dt = datetime.now()
        return dt.isoformat() + "Z"  # 使用Z表示UTC时间
