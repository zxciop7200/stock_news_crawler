"""
测试模块
包含爬虫各组件的单元测试
"""
import unittest
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.helpers import validate_stock_code, clean_stock_code
from src.storage.record_manager import load_crawled_record, update_crawled_record


class TestHelpers(unittest.TestCase):
    """测试辅助函数"""

    def test_validate_stock_code(self):
        self.assertTrue(validate_stock_code("000001"))
        self.assertTrue(validate_stock_code("600000"))
        self.assertFalse(validate_stock_code("123"))  # 太短
        self.assertFalse(validate_stock_code("abc123"))  # 非数字

    def test_clean_stock_code(self):
        self.assertEqual(clean_stock_code(" 000001.sz "), "000001")
        self.assertEqual(clean_stock_code("1"), "000001")
        self.assertIsNone(clean_stock_code("invalid"))


class TestRecordManager(unittest.TestCase):
    """测试记录管理（关键Bug修复验证）"""

    def test_update_returns_new_dataframe(self):
        """验证update_crawled_record返回新的DataFrame"""
        # 创建初始记录
        initial = pd.DataFrame({
            "股票代码": ["000001"],
            "最后爬取时间": [datetime(2024, 1, 1)]
        })

        # 更新记录
        updates = [{"股票代码": "000002", "最后爬取时间": datetime.now()}]
        result = update_crawled_record(initial, updates)

        # 验证返回的是新DataFrame且包含更新
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("000002", result["股票代码"].tolist())


if __name__ == "__main__":
    unittest.main()