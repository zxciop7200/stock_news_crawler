"""
日志工具模块
提供统一的日志配置，支持控制台和文件双输出
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from config.settings import SETTINGS


def setup_logger(name: str = "stock_crawler") -> logging.Logger:
    """
    配置并返回logger实例

    Args:
        name: logger名称，建议使用模块名__name__

    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # 文件handler
    try:
        file_handler = logging.FileHandler(SETTINGS.LOG_FILE, encoding="utf-8", mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except PermissionError:
        logger.warning("⚠️ 日志文件被占用，仅输出到控制台")
    except Exception as e:
        logger.error(f"❌ 日志文件初始化失败: {e}")

    return logger


class ProgressLogger:
    """进度日志记录器"""

    def __init__(self, logger: logging.Logger, total: int, desc: str = "Processing"):
        self.logger = logger
        self.total = total
        self.desc = desc
        self.current = 0
        self.success = 0
        self.failed = 0

    def update(self, success: bool = True, message: str = "") -> None:
        """更新进度"""
        self.current += 1
        if success:
            self.success += 1
        else:
            self.failed += 1

        if self.current % max(1, self.total // 10) == 0 or self.current == self.total:
            percent = (self.current / self.total) * 100
            self.logger.info(
                f"📊 {self.desc}: {self.current}/{self.total} ({percent:.1f}%) "
                f"✅{self.success} ❌{self.failed}"
            )