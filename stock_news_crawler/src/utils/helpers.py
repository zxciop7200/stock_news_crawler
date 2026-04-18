# ===================== src/utils/helpers.py =====================
"""
辅助函数模块
提供股票列表读取、数据验证等通用功能
"""
import re
import pandas as pd
from pathlib import Path
from typing import List, Optional, Set
from config.settings import SETTINGS
from src.utils.logger import setup_logger

# 初始化模块级日志器
logger = setup_logger(__name__)


def validate_stock_code(code: str) -> bool:
    """
    验证股票代码格式是否合法
    
    规则：
    - 必须是6位数字
    - 深市：000/001/002/003/300开头
    - 沪市：600/601/603/605/688开头
    
    Args:
        code: 待验证的股票代码字符串
        
    Returns:
        bool: 是否合法
        
    Example:
        >>> validate_stock_code("000001")
        True
        >>> validate_stock_code("abc123")
        False
    """
    if not code or len(code) != 6:
        return False
    
    # 必须为纯数字
    if not code.isdigit():
        return False
    
    # 检查有效前缀（可根据需要扩展）
    valid_prefixes = ('000', '001', '002', '003', '300', '600', '601', '603', '605', '688')
    return code.startswith(valid_prefixes)


def clean_stock_code(code: str) -> Optional[str]:
    """
    清洗股票代码，移除多余字符并标准化格式
    
    Args:
        code: 原始股票代码（可能包含空格、后缀等）
        
    Returns:
        清洗后的6位代码，若不合法则返回None
        
    Example:
        >>> clean_stock_code(" 000001.sz ")
        "000001"
        >>> clean_stock_code("1")
        "000001"
    """
    if pd.isna(code) or not isinstance(code, (str, int, float)):
        return None
    
    # 转换为字符串并清理
    code_str = str(code).strip().upper()
    
    # 移除常见后缀（如.SZ, .SH）
    code_str = re.sub(r'\.(SZ|SH|BJ)$', '', code_str, flags=re.IGNORECASE)
    
    # 移除所有非数字字符
    code_str = re.sub(r'[^0-9]', '', code_str)
    
    # 补齐6位（如输入"1"转为"000001"）
    code_str = code_str.zfill(6)
    
    # 验证格式
    if validate_stock_code(code_str):
        return code_str
    return None


def read_stock_codes_from_txt(file_path: Path) -> Optional[List[str]]:
    """
    从txt文件读取股票代码列表
    
    支持的文件格式：
    - 每行一个代码：000001
    - 代码-名称格式：000001-平安银行
    - 带空格或制表符分隔：000001 平安银行
    
    Args:
        file_path: txt文件路径
        
    Returns:
        股票代码列表，读取失败返回None
        
    Note:
        会自动跳过空行、注释行（以#开头）和格式错误的行
    """
    if not file_path.exists():
        logger.debug(f"txt文件不存在: {file_path}")
        return None
    
    stock_codes = []
    invalid_lines = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 解析格式：优先尝试"代码-名称"格式，其次尝试空白符分隔
                code = None
                if "-" in line:
                    code = line.split("-")[0].strip()
                elif "\t" in line:
                    code = line.split("\t")[0].strip()
                elif " " in line:
                    code = line.split()[0].strip()
                else:
                    code = line
                
                # 清洗并验证
                cleaned = clean_stock_code(code)
                if cleaned:
                    stock_codes.append(cleaned)
                else:
                    invalid_lines.append((line_num, line))
        
        # 报告结果
        if stock_codes:
            logger.info(f"✅ 从txt文件读取到 {len(stock_codes)} 只有效股票")
            if invalid_lines:
                logger.warning(f"⚠️ 跳过 {len(invalid_lines)} 行无效数据（前5行: {invalid_lines[:5]}）")
            return stock_codes
        else:
            logger.warning(f"⚠️ 文件 {file_path.name} 中未找到有效股票代码")
            return None
            
    except UnicodeDecodeError:
        logger.error(f"❌ 文件编码错误，请确保 {file_path.name} 使用UTF-8编码")
        return None
    except Exception as e:
        logger.error(f"❌ 读取txt文件失败：{str(e)}")
        return None


def read_stock_codes_from_excel(file_path: Path) -> Optional[List[str]]:
    """
    从excel文件读取股票代码列表
    
    要求：
    - 文件必须包含配置中指定的列名（默认"股票代码"）
    - 支持.xlsx和.xls格式
    
    Args:
        file_path: excel文件路径
        
    Returns:
        股票代码列表，读取失败返回None
        
    Note:
        会自动清洗数据（去空格、补零、去重）
    """
    if not file_path.exists():
        logger.debug(f"excel文件不存在: {file_path}")
        return None
    
    try:
        # 读取excel，指定引擎以支持不同格式
        if file_path.suffix == '.xls':
            df = pd.read_excel(file_path, engine='xlrd')
        else:
            df = pd.read_excel(file_path, engine='openpyxl')
        
        # 检查必要列
        if SETTINGS.STOCK_CODE_COLUMN not in df.columns:
            available_cols = ", ".join(df.columns.tolist())
            logger.error(f"❌ Excel文件缺少列 '{SETTINGS.STOCK_CODE_COLUMN}'，可用列: {available_cols}")
            return None
        
        # 提取并清洗股票代码
        raw_codes = df[SETTINGS.STOCK_CODE_COLUMN].tolist()
        valid_codes = []
        invalid_count = 0
        
        for code in raw_codes:
            cleaned = clean_stock_code(code)
            if cleaned:
                valid_codes.append(cleaned)
            else:
                invalid_count += 1
        
        # 去重保持顺序（使用dict.fromkeys技巧）
        unique_codes = list(dict.fromkeys(valid_codes))
        
        duplicates = len(valid_codes) - len(unique_codes)
        logger.info(
            f"✅ 从Excel读取: 原始{len(raw_codes)}条, "
            f"有效{len(unique_codes)}只, 去重{duplicates}只, 无效{invalid_count}条"
        )
        
        return unique_codes if unique_codes else None
        
    except ImportError as e:
        missing_lib = 'xlrd' if 'xlrd' in str(e) else 'openpyxl'
        logger.error(f"❌ 缺少依赖库: pip install {missing_lib}")
        return None
    except Exception as e:
        logger.error(f"❌ 读取Excel文件失败：{str(e)}")
        return None


def get_stock_list() -> List[str]:
    """
    获取股票列表（优先级：txt > excel > 默认列表）
    
    搜索顺序：
    1. 优先读取txt文件（raw/stock_list.txt）
    2. 其次读取excel文件（raw/stock_list.xlsx）
    3. 最后使用默认列表（config中定义的DEFAULT_STOCK_LIST）
    
    Returns:
        股票代码列表（确保去重且格式统一）
        
    Raises:
        ValueError: 当所有来源都失败且默认列表为空时
    """
    # 优先级1：txt文件（便于手动编辑和版本控制）
    stock_codes = read_stock_codes_from_txt(SETTINGS.STOCK_FILE_TXT)
    if stock_codes:
        return stock_codes
    
    # 优先级2：excel文件（便于从其他系统导出）
    stock_codes = read_stock_codes_from_excel(SETTINGS.STOCK_FILE_EXCEL)
    if stock_codes:
        return stock_codes
    
    # 优先级3：默认列表（兜底方案）
    if SETTINGS.DEFAULT_STOCK_LIST:
        logger.warning(
            f"⚠️ 未找到股票列表文件，使用默认列表（{len(SETTINGS.DEFAULT_STOCK_LIST)}只股票）\n"
            f"💡 提示：请在以下路径配置股票列表:\n"
            f"   - {SETTINGS.STOCK_FILE_TXT}\n"
            f"   - {SETTINGS.STOCK_FILE_EXCEL}"
        )
        return SETTINGS.DEFAULT_STOCK_LIST.copy()  # 返回副本防止修改原列表
    
    # 极端情况：没有任何可用数据
    logger.critical("❌ 严重错误：无法获取任何股票列表，请检查配置")
    raise ValueError("无法获取股票列表：所有数据源均失败且默认列表为空")


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """
    将列表分块，用于批量处理
    
    Args:
        items: 原始列表
        chunk_size: 每块大小
        
    Returns:
        分块后的列表的列表
        
    Example:
        >>> chunk_list([1,2,3,4,5], 2)
        [[1,2], [3,4], [5]]
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def format_stock_info(code: str, name: Optional[str] = None) -> str:
    """
    格式化股票信息用于日志显示
    
    Args:
        code: 股票代码
        name: 股票名称（可选）
        
    Returns:
        格式化字符串，如"000001(平安银行)"
    """
    if name:
        return f"{code}({name})"
    return code