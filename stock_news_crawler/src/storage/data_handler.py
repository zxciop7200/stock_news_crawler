import pandas as pd
import sqlite3
from typing import List, Set, Optional
from pathlib import Path
from config.settings import SETTINGS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_existing_news() -> pd.DataFrame:
    output_file = SETTINGS.OUTPUT_FILE

    if not output_file.exists():
        logger.debug(f"输出文件不存在，创建新数据集: {output_file}")
        return pd.DataFrame(columns=[
            "股票代码", "发布时间", "新闻标题", "文章来源", "新闻链接", "新闻正文"
        ])

    try:
        suffix = output_file.suffix.lower()

        if suffix == '.xlsx' or suffix == '.xls':
            df = pd.read_excel(output_file, engine='openpyxl' if suffix == '.xlsx' else 'xlrd')
            logger.info(f"📖 已加载Excel数据: {len(df)} 条")

        elif suffix == '.csv':
            df = pd.read_csv(output_file, encoding='utf-8-sig')
            logger.info(f"📖 已加载CSV数据: {len(df)} 条")

        elif suffix == '.db':
            conn = sqlite3.connect(output_file)
            try:
                df = pd.read_sql_query("SELECT * FROM news", conn)
                logger.info(f"📖 已加载SQLite数据: {len(df)} 条")
            finally:
                conn.close()
        else:
            logger.warning(f"⚠️ 不支持的文件格式: {suffix}，创建新数据集")
            return pd.DataFrame(columns=[
                "股票代码", "发布时间", "新闻标题", "文章来源", "新闻链接", "新闻正文"
            ])

        required_cols = ["股票代码", "新闻链接"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"❌ 数据文件缺少必要列: {missing_cols}")
            raise ValueError(f"数据文件格式错误，缺少列: {missing_cols}")

        return df

    except Exception as e:
        logger.error(f"❌ 读取数据文件失败: {str(e)}")
        logger.warning("⚠️ 将创建新数据集继续运行")
        return pd.DataFrame(columns=[
            "股票代码", "发布时间", "新闻标题", "文章来源", "新闻链接", "新闻正文"
        ])


def get_existing_urls(existing_news: pd.DataFrame) -> Set[str]:
    if existing_news.empty or "新闻链接" not in existing_news.columns:
        return set()

    urls = set(existing_news["新闻链接"].dropna().astype(str).tolist())
    logger.debug(f"📊 已有URL去重集合: {len(urls)} 条")
    return urls


def save_news_data(existing_news: pd.DataFrame, new_news_list: List[pd.DataFrame]) -> None:
    if not new_news_list:
        logger.info("\n✅ 本次无新增新闻")
        return

    new_df = pd.concat(new_news_list, ignore_index=True)
    new_count = len(new_df)

    if new_count == 0:
        logger.info("\n✅ 本次无新增新闻")
        return

    output_file = SETTINGS.OUTPUT_FILE
    suffix = output_file.suffix.lower()

    try:
        if suffix == '.csv':
            file_exists = output_file.exists()
            new_df.to_csv(
                output_file, 
                mode='a', 
                header=not file_exists,
                index=False, 
                encoding='utf-8-sig'
            )

            if file_exists:
                with open(output_file, 'r', encoding='utf-8-sig') as f:
                    total_lines = sum(1 for _ in f) - 1
            else:
                total_lines = new_count

            logger.info(f"\n🎉 本次新增: {new_count} 条 | 总计: {total_lines} 条 (CSV追加)")

        elif suffix == '.db':
            conn = sqlite3.connect(output_file)
            try:
                new_df.to_sql('news', conn, if_exists='append', index=False)

                cursor = conn.execute("SELECT COUNT(*) FROM news")
                total_count = cursor.fetchone()[0]

                logger.info(f"\n🎉 本次新增: {new_count} 条 | 总计: {total_count} 条 (SQLite)")

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_news_code ON news(股票代码)
                ''')
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_news_url ON news(新闻链接)
                ''')
                conn.commit()
            finally:
                conn.close()

        else:
            final_df = pd.concat([existing_news, new_df], ignore_index=True)
            final_df.to_excel(output_file, index=False, engine='openpyxl')

            logger.info(f"\n🎉 本次新增: {new_count} 条 | 总计: {len(final_df)} 条 (Excel)")

    except PermissionError:
        logger.error(f"❌ 无法写入文件（可能被占用）: {output_file}")
        logger.info("💡 提示：请关闭正在查看该文件的Excel/编辑器")
    except Exception as e:
        logger.error(f"❌ 保存数据失败: {str(e)}")
        raise


def export_by_date(df: pd.DataFrame, output_dir: Path, date_col: str = "发布时间") -> None:
    if df.empty or date_col not in df.columns:
        logger.warning("⚠️ 无数据或缺少日期列，跳过分区导出")
        return

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df['date_key'] = df[date_col].dt.strftime('%Y_%m_%d')

    for date_key, group in df.groupby('date_key'):
        filename = output_dir / f"news_{date_key}.xlsx"
        group.drop('date_key', axis=1).to_excel(filename, index=False)
        logger.info(f"📁 已导出 {date_key}: {len(group)} 条 -> {filename.name}")


def get_storage_stats() -> dict:
    output_file = SETTINGS.OUTPUT_FILE
    stats = {
        "file_path": str(output_file),
        "file_exists": output_file.exists(),
        "file_size_mb": 0,
        "record_count": 0,
        "format": output_file.suffix.lower()
    }

    if not output_file.exists():
        return stats

    stats["file_size_mb"] = round(output_file.stat().st_size / (1024 * 1024), 2)

    try:
        suffix = output_file.suffix.lower()
        if suffix == '.csv':
            with open(output_file, 'r', encoding='utf-8-sig') as f:
                stats["record_count"] = sum(1 for _ in f) - 1
        elif suffix == '.db':
            conn = sqlite3.connect(output_file)
            cursor = conn.execute("SELECT COUNT(*) FROM news")
            stats["record_count"] = cursor.fetchone()[0]
            conn.close()
        else:
            stats["record_count"] = -1
    except Exception as e:
        logger.debug(f"统计记录数失败: {e}")
        stats["record_count"] = -1

    return stats