"""
新闻列表获取模块
从akshare获取股票新闻列表，处理去重和正文爬取
"""
import akshare as ak
import pandas as pd
from typing import Optional, Set, Dict
from datetime import datetime, timedelta
from config.settings import SETTINGS
from src.utils.logger import setup_logger
from src.crawler.content_parser import batch_get_contents
import time

logger = setup_logger(__name__)


def fetch_news_list(symbol: str) -> Optional[pd.DataFrame]:
    """
    从akshare获取股票新闻列表

    Args:
        symbol: 股票代码（如"000001"）

    Returns:
        新闻列表DataFrame，失败返回None
    """
    try:
        df = ak.stock_news_em(symbol=symbol)
        if df.empty:
            return None
        df["股票代码"] = symbol
        return df
    except Exception as e:
        logger.error(f"获取 {symbol} 新闻列表失败: {str(e)}")
        return None


def should_crawl(symbol: str, crawled_record: pd.DataFrame, now: datetime) -> bool:
    """
    判断是否需要爬取（基于RE_CRAWL_DAYS配置）

    Returns:
        True表示需要爬取，False表示跳过
    """
    record = crawled_record[crawled_record["股票代码"] == symbol]
    if not record.empty:
        last_time = record["最后爬取时间"].iloc[0]
        if pd.notna(last_time) and (now - last_time) < timedelta(days=SETTINGS.RE_CRAWL_DAYS):
            logger.info(f"⏭️ {symbol} 已爬取，跳过")
            return False
    return True


def process_stock_news(
        symbol: str,
        existing_urls: Set[str],
        crawled_record: pd.DataFrame,
        now: datetime
) -> Optional[Dict]:
    """
    处理单只股票的完整流程

    Args:
        symbol: 股票代码
        existing_urls: 已有URL集合（去重用）
        crawled_record: 爬取记录DataFrame
        now: 当前时间

    Returns:
        包含new_df和update_record的字典，无需爬取返回None
    """
    if not should_crawl(symbol, crawled_record, now):
        return None

    logger.info(f"🆕 {symbol} 爬取新闻列表...")
    news_df = fetch_news_list(symbol)

    if news_df is None:
        logger.info(f"ℹ️ {symbol} 无新闻")
        return {"new_df": None, "update_record": {"股票代码": symbol, "最后爬取时间": now}}

    # 去重：过滤已存在的URL
    new_df = news_df[~news_df["新闻链接"].isin(existing_urls)].copy()

    if new_df.empty:
        logger.info(f"ℹ️ {symbol} 无新新闻")
        return {"new_df": None, "update_record": {"股票代码": symbol, "最后爬取时间": now}}

    # 爬取正文
    logger.info(f"⚡ {symbol} 正在爬取 {len(new_df)} 条正文...")
    urls = new_df["新闻链接"].tolist()
    contents = batch_get_contents(urls)
    new_df["新闻正文"] = contents

    # 保留需要的列
    keep_cols = ["股票代码", "发布时间", "新闻标题", "文章来源", "新闻链接", "新闻正文"]
    new_df = new_df[keep_cols].copy()

    logger.info(f"✅ {symbol} 新增 {len(new_df)} 条")
    time.sleep(SETTINGS.REQUEST_DELAY)

    return {"new_df": new_df, "update_record": {"股票代码": symbol, "最后爬取时间": now}}