# 📈 股票新闻爬虫 (Stock News Crawler)

基于 Python + akshare 的股票新闻采集系统，支持多线程并发爬取、智能去重、断点续爬和多种存储格式。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 特性

- **🔄 智能重试机制**：使用 tenacity 实现指数退避重试，自动处理网络超时和连接错误
- **⚡ 高性能存储**：支持 CSV 追加模式，比 Excel 快 10-100 倍，适合大数据量
- **🗄️ 多格式支持**：Excel（查看方便）、CSV（性能最佳）、SQLite（支持 SQL 查询）
- **⏯️ 断点续爬**：自动记录爬取进度，避免重复工作
- **🧵 多线程并发**：可配置线程数，高效爬取新闻正文
- **🔧 环境变量配置**：所有参数支持通过环境变量动态配置，无需改代码
- **🛡️ 类型安全**：完整类型注解，降低运行时错误

---

## 📁 项目结构

```
stock_news_crawler/
├── config/                    # 配置文件目录
│   ├── __init__.py
│   └── settings.py             # 核心配置（支持环境变量）
├── data/                       # 数据存储目录
│   ├── raw/                    # 原始数据（股票列表、爬取记录）
│   └── processed/              # 处理后数据（新闻文件）
├── logs/                       # 日志目录
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── crawler/                # 爬虫模块
│   │   ├── __init__.py
│   │   ├── news_fetcher.py     # 新闻列表获取（akshare接口）
│   │   └── content_parser.py   # 正文解析（多线程+重试）
│   ├── storage/                # 存储模块
│   │   ├── __init__.py
│   │   ├── data_handler.py     # 数据处理（多格式支持）
│   │   └── record_manager.py   # 记录管理（Bug修复版）
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── logger.py           # 日志工具
│       └── helpers.py          # 辅助函数（股票代码清洗）
├── tests/                      # 测试目录
│   ├── __init__.py
│   └── test_crawler.py         # 单元测试
├── main.py                     # 程序入口
├── requirements.txt            # 依赖列表
└── README.md                   # 本文件
```

---

## 🛠️ 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/stock_news_crawler.git
cd stock_news_crawler
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表：**
- `akshare>=1.12.0` - 股票数据接口
- `pandas>=2.0.0` - 数据处理
- `openpyxl>=3.1.0` - Excel读写
- `requests>=2.31.0` - HTTP请求
- `beautifulsoup4>=4.12.0` - HTML解析
- `tqdm>=4.66.0` - 进度条
- `tenacity>=8.2.0` - 重试机制（新增）

---

## 🚀 快速开始

### 方式一：使用默认股票列表（立即运行）

```bash
python main.py
```

程序将使用内置的默认股票列表（深市主板50只股票）开始爬取。

### 方式二：自定义股票列表（推荐）

#### 方法 A：TXT 文件（推荐，便于版本控制）

创建 `data/raw/stock_list.txt`，每行一个股票代码：

```
# 这是注释行
000001-平安银行
000002-万科A
600000-浦发银行
000858-五粮液
```

支持格式：
- `000001`（仅代码）
- `000001-平安银行`（代码-名称）
- `000001 平安银行`（空格分隔）

#### 方法 B：Excel 文件

创建 `data/raw/stock_list.xlsx`，包含列名为 **"股票代码"** 的列：

| 股票代码 | 股票名称 |
|---------|---------|
| 000001  | 平安银行 |
| 000002  | 万科A   |

### 方式三：环境变量配置（高级）

```bash
# 使用CSV格式（性能最佳）
set OUTPUT_FORMAT=csv

# 设置并发线程数
set MAX_WORKERS=20

# 设置请求间隔（防封IP）
set REQUEST_DELAY=0.5

# 运行
python main.py
```
## 爬取过程


![img.png](img.png)

使用时，可删除项目中的图片，对项目无任何影响

---

## ⚙️ 配置说明

### 环境变量列表

| 环境变量 | 默认值 | 说明 | 示例 |
|---------|-------|------|------|
| `OUTPUT_FORMAT` | `xlsx` | 输出格式：`xlsx`/`csv`/`db` | `csv` |
| `MAX_WORKERS` | `15` | 并发线程数 | `20` |
| `REQUEST_TIMEOUT` | `8` | 请求超时（秒） | `10` |
| `REQUEST_DELAY` | `0.3` | 请求间隔（秒） | `0.5` |
| `RE_CRAWL_DAYS` | `1` | 重新爬取间隔（天） | `7` |
| `MAX_RETRY_ATTEMPTS` | `3` | 最大重试次数 | `5` |
| `RETRY_BACKOFF_FACTOR` | `1.0` | 重试退避系数 | `2.0` |

### 配置文件修改

如需永久修改默认配置，编辑 `config/settings.py`：

```python
# 修改默认股票列表
DEFAULT_STOCK_LIST = [
    "000001", "000002", "000858", "600519"  # 你的股票列表
]

# 修改并发数
MAX_WORKERS: int = 20
```

---

## 📊 输出格式对比

| 格式 | 文件扩展名 | 优点 | 缺点 | 适用场景 |
|-----|-----------|------|------|---------|
| **Excel** | `.xlsx` | 兼容性好，可直接查看 | 大数据量慢，全量重写 | 小数据量、人工查看 |
| **CSV** | `.csv` | 性能最佳，追加写入 | 无格式，中文需UTF-8 BOM | 大数据量、程序处理 |
| **SQLite** | `.db` | 支持SQL查询，索引加速 | 需要工具查看 | 数据分析、复杂查询 |

### 切换格式

```bash
# Windows CMD
set OUTPUT_FORMAT=csv
python main.py

# Windows PowerShell
$env:OUTPUT_FORMAT="csv"
python main.py

# Linux/macOS
export OUTPUT_FORMAT=csv
python main.py
```

---

## 🔄 断点续爬机制

系统自动维护两个记录文件：

1. **`data/raw/股票爬取记录.csv`** - 记录每只股票的最后爬取时间
2. **`data/processed/深市企业新闻.xlsx`**（或其他格式）- 已爬取的新闻数据

### 工作原理

- 每次运行前检查 `RE_CRAWL_DAYS`（默认1天）
- 若股票在N天内已爬取，则自动跳过
- 新闻链接自动去重，避免重复存储

### 强制重新爬取

```bash
# 方法1：删除记录文件
del data\raw\股票爬取记录.csv

# 方法2：设置间隔为0天
set RE_CRAWL_DAYS=0
python main.py
```

---

## 🧪 测试

运行单元测试：

```bash
python -m unittest tests.test_crawler
```

测试覆盖：
- 股票代码清洗和验证
- 记录管理 Bug 修复验证
- 数据存储格式兼容性

---

## 📈 性能优化建议

### 大数据量场景（>1000只股票）

```bash
# 1. 使用CSV格式（推荐）
set OUTPUT_FORMAT=csv

# 2. 增加线程数（根据网络状况）
set MAX_WORKERS=30

# 3. 适当降低请求间隔（如果IP未被封锁）
set REQUEST_DELAY=0.1

# 4. 运行
python main.py
```

### 避免被封IP

```bash
# 1. 增加请求间隔
set REQUEST_DELAY=1.0

# 2. 减少并发数
set MAX_WORKERS=5

# 3. 增加重试次数
set MAX_RETRY_ATTEMPTS=5
```

---

## 🐛 常见问题

### Q1: 遇到 "akshare 版本不匹配" 错误？

```bash
pip install --upgrade akshare
```

### Q2: Excel 文件被占用无法写入？

关闭正在查看该文件的 Excel 软件，或切换到 CSV 格式：

```bash
set OUTPUT_FORMAT=csv
python main.py
```

### Q3: 如何只爬取特定几只股票？

创建 `data/raw/stock_list.txt`：

```
000001
000002
```

### Q4: 如何查看 SQLite 数据库？

使用 [DB Browser for SQLite](https://sqlitebrowser.org/) 或命令行：

```bash
sqlite3 data\processed\深市企业新闻.db
SELECT * FROM news LIMIT 10;
```

### Q5: 日志文件在哪里？

日志位于 `logs/crawler.log`，包含详细调试信息。

---

## 📝 更新日志

### v1.0.0 (2026-4-18)
- 🎉 初始版本发布
- 支持 akshare 新闻爬取
- 基础多线程支持
- Excel 存储格式

---

## 📧 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/zxciop7200/stock_news_crawler/issues)。

**免责声明**：本工具仅供学习研究使用，不构成任何投资建议。股市有风险，投资需谨慎。
