"""
新闻正文解析模块
使用多线程并发爬取新闻正文内容，支持重试机制和错误处理
"""
import re
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from config.settings import SETTINGS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@retry(
    stop=stop_after_attempt(SETTINGS.MAX_RETRY_ATTEMPTS),
    wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
    retry=retry_if_exception_type((ConnectionError, Timeout, HTTPError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def get_news_content(url: str) -> str:
    """
    爬取单条新闻正文（带重试机制）

    Args:
        url: 新闻详情页URL

    Returns:
        新闻正文文本，失败时返回错误信息
    """
    try:
        response = requests.get(
            url,
            headers=SETTINGS.HEADERS,
            timeout=SETTINGS.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")

        # 正文定位策略
        content_div = (
                soup.find("div", class_="Body") or
                soup.find("div", id="ContentBody") or
                soup.find("div", class_="content") or
                soup.find("article") or
                soup.find("div", class_=re.compile("content|article|main", re.I))
        )

        if content_div:
            paragraphs = content_div.find_all("p")
            content = "\n".join([
                p.get_text(strip=True)
                for p in paragraphs
                if p.get_text(strip=True)
            ]).strip()

            content = re.sub(r'\n{3,}', '\n\n', content)
            return content if content else "正文内容为空"

        title = soup.find("title")
        if title:
            return f"未能提取正文，页面标题: {title.get_text(strip=True)}"
        return "未能提取正文内容"

    except Timeout:
        return "爬取失败：请求超时"
    except ConnectionError:
        return "爬取失败：网络连接错误"
    except HTTPError as e:
        return f"爬取失败：HTTP错误 {e.response.status_code}"
    except Exception as e:
        logger.error(f"解析URL时发生意外错误: {url}, 错误: {str(e)}")
        return f"爬取失败：未知错误 - {str(e)}"


def batch_get_contents(urls: List[str]) -> List[str]:
    """多线程批量爬取新闻正文"""
    if not urls:
        return []

    results: List[str] = [""] * len(urls)

    with ThreadPoolExecutor(max_workers=SETTINGS.MAX_WORKERS) as executor:
        future_to_index = {
            executor.submit(get_news_content, url): i
            for i, url in enumerate(urls)
        }

        for future in tqdm(
                as_completed(future_to_index),
                total=len(urls),
                desc="爬取正文",
                leave=False,
                unit="条"
        ):
            idx = future_to_index[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error(f"Future执行异常 [索引{idx}]: {str(e)}")
                results[idx] = f"系统错误: {str(e)}"

    return results