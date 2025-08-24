# 依赖模块安装说明

## 概述
本文档说明如何安装data-analysis项目的所有依赖模块，特别是今天新增的可配置Apriori分析功能所需的模块。

## 快速安装

### 1. 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 2. 安装所有依赖
```bash
# 安装requirements.txt中的所有模块
pip install -r requirements.txt
```

### 3. 验证安装
```bash
# 运行依赖检查脚本
python check_dependencies.py
```

## 今天新增的核心模块

### 必需模块
- **pyyaml==6.0.1** - YAML配置文件解析
- **loguru==0.7.2** - 高级日志记录
- **reportlab>=4.0.0** - PDF报告生成
- **tqdm==4.66.1** - 进度条显示

### 可选模块
- **fonttools>=4.0.0** - PDF中文字体支持
- **orjson>=3.8.0** - 高性能JSON处理
- **streamlit==1.28.1** - Web界面（可选）

## 分步安装（如果全量安装失败）

```bash
# 核心数据处理模块
pip install pandas numpy scipy matplotlib seaborn plotly

# 机器学习和数据挖掘
pip install scikit-learn mlxtend networkx statsmodels

# 文件处理
pip install openpyxl xlrd

# 配置和日志
pip install pyyaml loguru tqdm

# 报告生成
pip install reportlab fonttools

# 数据库连接（如需要）
pip install sqlalchemy clickhouse-connect

# 其他工具
pip install python-dotenv
```

## 常见问题

### 1. 网络问题
如果安装速度慢，可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 权限问题
如果遇到权限问题，建议使用虚拟环境而不是全局安装。

### 3. 版本冲突
如果出现版本冲突，可以尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 今天新增功能验证

安装完成后，可以测试新增功能：

```bash
# 测试可配置分析器
python run_configurable_analysis.py --help

# 运行完整分析示例
python run_configurable_analysis.py

# 检查HTML报告饼图修复
# 查看生成的HTML文件：reports/目录下的最新HTML文件
```

## 模块功能说明

| 模块 | 用途 | 今天新增 |
|------|------|----------|
| pyyaml | YAML配置文件解析 | ✅ |
| loguru | 结构化日志记录 | ✅ |
| reportlab | PDF报告生成 | ✅ |
| fonttools | 字体处理 | ✅ |
| tqdm | 进度条显示 | ✅ |
| plotly | 交互式图表（HTML报告） | 更新 |
| pandas | 数据处理 | 原有 |
| numpy | 数值计算 | 原有 |
| mlxtend | Apriori算法 | 原有 |

## 支持的功能

安装完成后，项目支持以下功能：

1. **可配置项目数据分析**
   - YAML配置文件支持
   - 中英文字段映射
   - 灵活的维度和指标字段配置

2. **Apriori关联规则挖掘**
   - 自动发现数据关联模式
   - 可配置算法参数
   - 数据标签分类

3. **多格式报告生成**
   - PDF报告（中文支持）
   - HTML交互式报告
   - 修复了饼图显示问题

4. **一键式执行**
   - 命令行参数支持
   - 自动数据生成
   - 友好的用户界面

## 技术支持

如果安装过程中遇到问题，请：
1. 检查Python版本（需要3.8+）
2. 确保网络连接正常
3. 尝试使用虚拟环境
4. 查看错误日志详细信息