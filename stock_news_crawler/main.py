"""
主程序入口
协调各模块完成股票新闻爬取任务
"""
from datetime import datetime
from src.utils.logger import setup_logger
from src.utils.helpers import get_stock_list
from src.crawler.news_fetcher import process_stock_news
from src.storage.data_handler import load_existing_news, get_existing_urls, save_news_data
from src.storage.record_manager import load_crawled_record, update_crawled_record


def main():
    # 初始化
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("股票新闻爬虫启动")
    logger.info("=" * 50)

    # 加载股票列表
    STOCK_LIST = get_stock_list()
    if not STOCK_LIST:
        logger.error("❌ 未获取到有效股票列表，程序退出")
        return

    # 加载数据
    crawled_record = load_crawled_record()
    existing_news = load_existing_news()
    existing_urls = get_existing_urls(existing_news)
    now = datetime.now()

    logger.info(f"📊 已有新闻：{len(existing_news)} 条 | 目标股票：{len(STOCK_LIST)} 只\n")

    new_news_list = []
    update_record_list = []

    # 处理每只股票
    for symbol in STOCK_LIST:
        result = process_stock_news(symbol, existing_urls, crawled_record, now)
        if result:
            if result["new_df"] is not None:
                new_news_list.append(result["new_df"])
                # 更新URL集合防止同批次重复
                existing_urls.update(result["new_df"]["新闻链接"].tolist())
            update_record_list.append(result["update_record"])

    # 保存结果
    save_news_data(existing_news, new_news_list)

    # 关键修复：接收返回值更新crawled_record
    crawled_record = update_crawled_record(crawled_record, update_record_list)

    logger.info("\n✅ 全部完成！")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()