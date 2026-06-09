"""MongoDB 连接管理"""
from typing import Dict

from pymongo import MongoClient
from pymongo.database import Database as PyMongoDatabase
from pymongo.collection import Collection

from config.settings import settings


class Database:
    """平台数据库连接管理（同步 pymongo）"""

    _client: MongoClient = None
    _smartcare_clients: Dict[str, MongoClient] = {}

    @classmethod
    def init(cls) -> None:
        """连接平台数据库"""
        cls._client = MongoClient(settings.PLATFORM_MONGO_URI)

    @classmethod
    def get_db(cls) -> PyMongoDatabase:
        """返回平台数据库实例"""
        return cls._client[settings.PLATFORM_DB_NAME]

    @classmethod
    def get_collection(cls, name: str) -> Collection:
        """返回平台数据库中的指定集合"""
        return cls.get_db()[name]

    @classmethod
    def get_smartcare_client(cls, uri: str) -> MongoClient:
        """获取或创建 SmartCare 连接的 MongoClient（带缓存）"""
        if uri not in cls._smartcare_clients:
            cls._smartcare_clients[uri] = MongoClient(uri)
        return cls._smartcare_clients[uri]

    @classmethod
    def close(cls) -> None:
        """关闭所有数据库连接"""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
        for client in cls._smartcare_clients.values():
            client.close()
        cls._smartcare_clients.clear()
