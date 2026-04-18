"""
爬取记录管理模块
修复原版的DataFrame更新bug，现在正确返回更新后的记录
"""
import pandas as pd
from typing import List, Dict
from config.settings import SETTINGS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_crawled_record() -> pd.DataFrame:
    """读取爬取记录"""
    if SETTINGS.RECORD_FILE.exists():
        df = pd.read_csv(SETTINGS.RECORD_FILE)
        df["最后爬取时间"] = pd.to_datetime(df["最后爬取时间"])
        return df
    return pd.DataFrame(columns=["股票代码", "最后爬取时间"])


def save_crawled_record(record_df: pd.DataFrame) -> None:
    """保存爬取记录"""
    record_df.to_csv(SETTINGS.RECORD_FILE, index=False, encoding="utf-8-sig")


def update_crawled_record(
        crawled_record: pd.DataFrame,
        update_record_list: List[Dict]
) -> pd.DataFrame:
    """
    更新爬取记录（修复版）

    关键修复：原版中crawled_record是局部变量，修改不会反映到原数据。
    现在返回更新后的DataFrame，调用者需要接收返回值。

    Args:
        crawled_record: 当前爬取记录（不会被修改，基于它创建新记录）
        update_record_list: 需要更新的记录列表

    Returns:
        更新后的爬取记录DataFrame
    """
    if not update_record_list:
        return crawled_record

    update_df = pd.DataFrame(update_record_list)

    # 创建新记录：过滤掉旧记录中需要更新的股票，然后追加新记录
    # 使用copy()避免修改原始数据
    filtered = crawled_record[~crawled_record["股票代码"].isin(update_df["股票代码"])].copy()
    result = pd.concat([filtered, update_df], ignore_index=True)

    # 保存到文件
    save_crawled_record(result)
    logger.info(f"📝 已更新 {len(update_record_list)} 条爬取记录")

    return result