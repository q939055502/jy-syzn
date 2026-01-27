# 排序工具函数模块
# 提供通用的排序功能，如按sort_order属性排序

from typing import List, Any


def sort_by_order(items: List[Any], order_by: str = 'sort_order', reverse: bool = False) -> List[Any]:
    """
    按指定属性对对象列表进行排序
    
    :param items: 要排序的对象列表
    :param order_by: 排序的属性名，默认为'sort_order'
    :param reverse: 是否逆序排序，默认为False（升序）
    :return: 排序后的对象列表
    """
    if not items:
        return []
    
    return sorted(items, key=lambda x: getattr(x, order_by, 0), reverse=reverse)