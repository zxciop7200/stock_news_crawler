"""
配置文件模块
包含所有项目配置，支持环境变量覆盖默认值
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass
class CrawlerConfig:
    """
    爬虫配置类
    使用dataclass确保类型安全，支持环境变量覆盖
    """
    # ===================== 路径配置 =====================
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    # 数据目录结构
    DATA_DIR: Path = field(init=False)
    RAW_DATA_DIR: Path = field(init=False)
    PROCESSED_DATA_DIR: Path = field(init=False)
    LOG_DIR: Path = field(init=False)

    def __post_init__(self):
        """初始化派生路径并创建必要目录"""
        self.DATA_DIR = self.BASE_DIR / "data"
        self.RAW_DATA_DIR = self.DATA_DIR / "raw"
        self.PROCESSED_DATA_DIR = self.DATA_DIR / "processed"
        self.LOG_DIR = self.BASE_DIR / "logs"

        for directory in [self.RAW_DATA_DIR, self.PROCESSED_DATA_DIR, self.LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

        # 初始化股票文件路径
        self.STOCK_FILE_TXT = self.RAW_DATA_DIR / "stock_list.txt"
        self.STOCK_FILE_EXCEL = self.RAW_DATA_DIR / "stock_list.xlsx"

        # 初始化输出文件路径
        output_format = os.getenv('OUTPUT_FORMAT', 'xlsx').lower()
        if output_format == 'csv':
            self.OUTPUT_FILE = self.PROCESSED_DATA_DIR / "深市企业新闻.csv"
        elif output_format == 'db':
            self.OUTPUT_FILE = self.PROCESSED_DATA_DIR / "深市企业新闻.db"
        else:
            self.OUTPUT_FILE = self.PROCESSED_DATA_DIR / "深市企业新闻.xlsx"

        self.RECORD_FILE = self.RAW_DATA_DIR / "股票爬取记录.csv"
        self.LOG_FILE = self.LOG_DIR / "crawler.log"

    # Excel文件配置
    STOCK_CODE_COLUMN: str = "股票代码"
    STOCK_NAME_COLUMN: str = "股票名称"

    # 默认股票列表
    DEFAULT_STOCK_LIST: List[str] = field(default_factory=lambda: [
        "000001", "000002", "000006", "000007", "000008", "000009", "000010",
        "000011", "000012", "000014", "000016", "000017", "000019", "000020",
        "000021", "000025", "000026", "000027", "000028", "000029", "000030",
        "000031", "000032", "000034", "000035", "000036", "000037", "000039",
        "000042", "000045", "000048", "000049", "000050", "000055", "000056",
        "000058", "000059", "000060", "000061", "000062", "000063", "000065",
        "000066", "000068", "000069", "000070", "000078", "001872", "001914"
    ])

    # ===================== 爬虫核心配置（支持环境变量覆盖） =====================
    RE_CRAWL_DAYS: int = field(default_factory=lambda: int(os.getenv('RE_CRAWL_DAYS', '1')))
    MAX_WORKERS: int = field(default_factory=lambda: int(os.getenv('MAX_WORKERS', '15')))
    REQUEST_TIMEOUT: int = field(default_factory=lambda: int(os.getenv('REQUEST_TIMEOUT', '8')))
    REQUEST_DELAY: float = field(default_factory=lambda: float(os.getenv('REQUEST_DELAY', '0.3')))
    MAX_RETRY_ATTEMPTS: int = field(default_factory=lambda: int(os.getenv('MAX_RETRY_ATTEMPTS', '3')))
    RETRY_BACKOFF_FACTOR: float = field(default_factory=lambda: float(os.getenv('RETRY_BACKOFF_FACTOR', '1.0')))

    # 请求头配置
    HEADERS: dict = field(default_factory=lambda: {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })

    def validate(self) -> None:
        """配置验证方法"""
        assert self.MAX_WORKERS > 0, "MAX_WORKERS必须为正整数"
        assert self.REQUEST_TIMEOUT > 0, "REQUEST_TIMEOUT必须为正整数"
        assert self.REQUEST_DELAY >= 0, "REQUEST_DELAY不能为负数"
        assert self.RE_CRAWL_DAYS >= 0, "RE_CRAWL_DAYS不能为负数"
        assert self.MAX_RETRY_ATTEMPTS > 0, "MAX_RETRY_ATTEMPTS必须为正整数"


# 全局配置实例
SETTINGS = CrawlerConfig()
SETTINGS.validate()