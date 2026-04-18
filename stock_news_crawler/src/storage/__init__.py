"""
存储模块初始化文件
"""
from src.storage.data_handler import (
    load_existing_news,
    get_existing_urls,
    save_news_data,
    get_storage_stats
)
from src.storage.record_manager import (
    load_crawled_record,
    update_crawled_record
)

__all__ = [
    'load_existing_news',
    'get_existing_urls',
    'save_news_data',
    'get_storage_stats',
    'load_crawled_record',
    'update_crawled_record'
]