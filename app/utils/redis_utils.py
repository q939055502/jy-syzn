# Redis工具函数
# 提供常用的Redis操作封装

import json
from typing import Any, Optional, Dict
import uuid
from redis import Redis


class RedisUtils:
    """Redis工具类，封装常用的Redis操作"""
    
    @staticmethod
    def set_cache(redis_client: Redis, key: str, value: Any, expire: int = 3600) -> bool:
        """
        设置缓存
        :param redis_client: Redis客户端
        :param key: 缓存键
        :param value: 缓存值，可以是任意类型，会被转换为JSON字符串
        :param expire: 过期时间（秒），默认3600秒
        :return: 设置成功返回True，失败返回False
        """
        try:
            if not redis_client:
                return False
            # 将值转换为JSON字符串
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            # 设置缓存
            redis_client.set(key, json_value, ex=expire)
            return True
        except Exception as e:
            print(f"Set cache error: {str(e)}")
            return False
    
    @staticmethod
    def get_cache(redis_client: Redis, key: str) -> Optional[Any]:
        """
        获取缓存
        :param redis_client: Redis客户端
        :param key: 缓存键
        :return: 缓存值，不存在或解析失败返回None
        """
        try:
            if not redis_client:
                return None
            # 获取缓存值
            value = redis_client.get(key)
            if value is None:
                return None
            # 解析JSON字符串
            return json.loads(value)
        except Exception as e:
            print(f"Get cache error: {str(e)}")
            return None
    
    @staticmethod
    def delete_cache(redis_client: Redis, key: str) -> bool:
        """
        删除缓存
        :param redis_client: Redis客户端
        :param key: 缓存键
        :return: 删除成功返回True，失败返回False
        """
        try:
            if not redis_client:
                return False
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Delete cache error: {str(e)}")
            return False
    
    @staticmethod
    def increment(redis_client: Redis, key: str, amount: int = 1) -> Optional[int]:
        """
        计数器自增
        :param redis_client: Redis客户端
        :param key: 计数器键
        :param amount: 自增数量，默认1
        :return: 自增后的值，失败返回None
        """
        try:
            if not redis_client:
                return None
            return redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Increment error: {str(e)}")
            return None
    
    @staticmethod
    def decrement(redis_client: Redis, key: str, amount: int = 1) -> Optional[int]:
        """
        计数器自减
        :param redis_client: Redis客户端
        :param key: 计数器键
        :param amount: 自减数量，默认1
        :return: 自减后的值，失败返回None
        """
        try:
            if not redis_client:
                return None
            return redis_client.decrby(key, amount)
        except Exception as e:
            print(f"Decrement error: {str(e)}")
            return None
    
    @staticmethod
    def get_lock(redis_client: Redis, key: str, expire: int = 30) -> Optional[str]:
        """
        获取分布式锁
        :param redis_client: Redis客户端
        :param key: 锁键
        :param expire: 锁过期时间（秒），默认30秒
        :return: 锁ID，获取失败返回None
        """
        try:
            if not redis_client:
                return None
            # 生成唯一锁ID
            lock_id = str(uuid.uuid4())
            # 使用setnx获取锁
            success = redis_client.setnx(key, lock_id)
            if success:
                # 设置锁过期时间
                redis_client.expire(key, expire)
                return lock_id
            return None
        except Exception as e:
            print(f"Get lock error: {str(e)}")
            return None
    
    @staticmethod
    def release_lock(redis_client: Redis, key: str, lock_id: str) -> bool:
        """
        释放分布式锁
        :param redis_client: Redis客户端
        :param key: 锁键
        :param lock_id: 锁ID
        :return: 释放成功返回True，失败返回False
        """
        try:
            if not redis_client:
                return False
            # 使用Lua脚本确保原子性
            lua_script = """
            if redis.call('get', KEYS[1]) == ARGV[1] then
                return redis.call('del', KEYS[1])
            else
                return 0
            end
            """
            result = redis_client.eval(lua_script, 1, key, lock_id)
            return result == 1
        except Exception as e:
            print(f"Release lock error: {str(e)}")
            return False
    
    @staticmethod
    def set_hash_field(redis_client: Redis, hash_key: str, field: str, value: Any) -> bool:
        """
        设置哈希字段
        :param redis_client: Redis客户端
        :param hash_key: 哈希键
        :param field: 字段名
        :param value: 字段值，会被转换为JSON字符串
        :return: 设置成功返回True，失败返回False
        """
        try:
            if not redis_client:
                return False
            # 将值转换为JSON字符串
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            # 设置哈希字段
            redis_client.hset(hash_key, field, json_value)
            return True
        except Exception as e:
            print(f"Set hash field error: {str(e)}")
            return False
    
    @staticmethod
    def get_hash_field(redis_client: Redis, hash_key: str, field: str) -> Optional[Any]:
        """
        获取哈希字段
        :param redis_client: Redis客户端
        :param hash_key: 哈希键
        :param field: 字段名
        :return: 字段值，不存在或解析失败返回None
        """
        try:
            if not redis_client:
                return None
            # 获取字段值
            value = redis_client.hget(hash_key, field)
            if value is None:
                return None
            # 解析JSON字符串
            return json.loads(value)
        except Exception as e:
            print(f"Get hash field error: {str(e)}")
            return None
    
    @staticmethod
    def get_hash_all(redis_client: Redis, hash_key: str) -> Optional[Dict[str, Any]]:
        """
        获取哈希所有字段
        :param redis_client: Redis客户端
        :param hash_key: 哈希键
        :return: 所有字段和值的字典，不存在或解析失败返回None
        """
        try:
            if not redis_client:
                return None
            # 获取所有字段和值
            hash_data = redis_client.hgetall(hash_key)
            if not hash_data:
                return None
            # 解析所有值
            result = {}
            for field, value in hash_data.items():
                try:
                    result[field] = json.loads(value)
                except Exception:
                    result[field] = value
            return result
        except Exception as e:
            print(f"Get hash all error: {str(e)}")
            return None
    
    @staticmethod
    def delete_hash_field(redis_client: Redis, hash_key: str, field: str) -> bool:
        """
        删除哈希字段
        :param redis_client: Redis客户端
        :param hash_key: 哈希键
        :param field: 字段名
        :return: 删除成功返回True，失败返回False
        """
        try:
            if not redis_client:
                return False
            redis_client.hdel(hash_key, field)
            return True
        except Exception as e:
            print(f"Delete hash field error: {str(e)}")
            return False
    
    @staticmethod
    def add_to_set(redis_client: Redis, key: str, *members: Any) -> int:
        """
        添加元素到集合
        :param redis_client: Redis客户端
        :param key: 集合键
        :param members: 要添加的元素
        :return: 成功添加的元素数量
        """
        try:
            if not redis_client:
                return 0
            # 将元素转换为字符串
            str_members = [str(member) for member in members]
            return redis_client.sadd(key, *str_members)
        except Exception as e:
            print(f"Add to set error: {str(e)}")
            return 0
    
    @staticmethod
    def remove_from_set(redis_client: Redis, key: str, *members: Any) -> int:
        """
        从集合中移除元素
        :param redis_client: Redis客户端
        :param key: 集合键
        :param members: 要移除的元素
        :return: 成功移除的元素数量
        """
        try:
            if not redis_client:
                return 0
            # 将元素转换为字符串
            str_members = [str(member) for member in members]
            return redis_client.srem(key, *str_members)
        except Exception as e:
            print(f"Remove from set error: {str(e)}")
            return 0
    
    @staticmethod
    def is_member_of_set(redis_client: Redis, key: str, member: Any) -> bool:
        """
        检查元素是否在集合中
        :param redis_client: Redis客户端
        :param key: 集合键
        :param member: 要检查的元素
        :return: 在集合中返回True，否则返回False
        """
        try:
            if not redis_client:
                return False
            return redis_client.sismember(key, str(member))
        except Exception as e:
            print(f"Is member of set error: {str(e)}")
            return False
    
    @staticmethod
    def get_set_members(redis_client: Redis, key: str) -> list:
        """
        获取集合所有元素
        :param redis_client: Redis客户端
        :param key: 集合键
        :return: 集合元素列表
        """
        try:
            if not redis_client:
                return []
            return list(redis_client.smembers(key))
        except Exception as e:
            print(f"Get set members error: {str(e)}")
            return []
    
    @staticmethod
    def set_key_expire(redis_client: Redis, key: str, expire: int) -> bool:
        """
        设置键的过期时间
        :param redis_client: Redis客户端
        :param key: 键
        :param expire: 过期时间（秒）
        :return: 设置成功返回True，失败返回False
        """
        try:
            if not redis_client:
                return False
            redis_client.expire(key, expire)
            return True
        except Exception as e:
            print(f"Set key expire error: {str(e)}")
            return False
    
    @staticmethod
    def get_key_ttl(redis_client: Redis, key: str) -> int:
        """
        获取键的剩余过期时间
        :param redis_client: Redis客户端
        :param key: 键
        :return: 剩余过期时间（秒），-1表示永久有效，-2表示键不存在
        """
        try:
            if not redis_client:
                return -2
            return redis_client.ttl(key)
        except Exception as e:
            print(f"Get key ttl error: {str(e)}")
            return -2
