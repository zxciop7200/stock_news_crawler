"""
爬虫模块初始化文件
"""
from src.crawler.news_fetcher import process_stock_news, fetch_news_list
from src.crawler.content_parser import batch_get_contents, get_news_content

__all__ = [
    'process_stock_news',
    'fetch_news_list',
    'batch_get_contents',
    'get_news_content'
]