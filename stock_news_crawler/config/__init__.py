# ===================== config/__init__.py =====================
"""
配置模块初始化文件
导出配置类和实例供其他模块使用
"""
from config.settings import CrawlerConfig, SETTINGS

__all__ = ['CrawlerConfig', 'SETTINGS']