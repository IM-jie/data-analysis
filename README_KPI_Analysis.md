# KPI Excel数据分析系统

## 概述

这是一个专门用于分析部门KPI数据的Python系统，支持从Excel文件中读取数据，进行异常检测、趋势分析和生成可视化报告。系统能够自动识别季度数据、部门信息和各种KPI指标，并提供多种异常检测算法来发现偏离异常趋势的指标数据。

## 功能特性

### 🔍 数据读取与处理
- **自动列检测**: 自动识别季度列（如2025Q1、2025Q2等）、部门列和指标列
- **数据质量验证**: 检查缺失值、重复数据、无效值等数据质量问题
- **数据重塑**: 支持宽格式到长格式的数据转换，便于时间序列分析
- **多格式支持**: 支持.xlsx和.xls格式的Excel文件

### 🚨 异常检测
- **多种算法**: 支持Isolation Forest、LOF、One-Class SVM、IQR、Z-score等多种异常检测方法
- **自动阈值**: 根据数据分布自动调整异常检测阈值
- **多维度分析**: 支持单指标和多指标联合异常检测
- **可视化展示**: 提供异常值的散点图和热力图展示

### 📈 趋势分析
- **趋势斜率计算**: 使用线性回归计算指标变化趋势
- **变化点检测**: 自动识别趋势变化的关键时间点
- **季节性分析**: 检测数据中的周期性模式
- **波动性评估**: 计算指标的稳定性指标
- **移动平均**: 提供平滑的趋势线

### 📊 可视化报告
- **HTML报告**: 生成美观的交互式HTML分析报告
- **多种图表**: 包含分布图、趋势图、异常检测图、部门对比图等
- **数据摘要**: 提供详细的数据统计和摘要信息
- **建议生成**: 基于分析结果自动生成改进建议

### 🎯 灵活分析
- **特定指标分析**: 可以针对单个指标进行深入分析
- **特定部门分析**: 可以针对单个部门进行专项分析
- **批量处理**: 支持处理包含100+指标的大型数据集
- **结果导出**: 支持将分析结果导出为Excel格式

### 🔍 数据挖掘功能
- **关联关系发现**: 自动发现指标间的相关性、互信息和因果关系
- **关联规则挖掘**: 使用Apriori算法挖掘指标间的关联规则
- **因果关系分析**: 基于滞后相关性分析指标间的因果关系
- **基于关联关系的异常检测**: 当关联关系发生变化时自动识别异常
- **业务洞察生成**: 基于挖掘结果生成业务建议和洞察

## 系统架构

```
data-analysis/
├── src/
│   ├── utils/
│   │   └── excel_reader.py          # Excel数据读取器
│   ├── analysis/
│   │   └── kpi_anomaly_detector.py  # 异常检测和趋势分析
│   ├── visualization/
│   │   └── kpi_report_generator.py  # 报告生成器
│   └── kpi_excel_analyzer.py        # 主分析器
├── config/
│   └── kpi_config.yaml              # 配置文件
├── reports/                         # 报告输出目录
├── example_kpi_analysis.py          # 使用示例
└── requirements.txt                 # 依赖包列表
```

## 安装与配置

### 1. 环境要求
- Python 3.8+
- 推荐使用虚拟环境

### 2. 安装依赖
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 3. 依赖包说明
- `pandas`: 数据处理和分析
- `numpy`: 数值计算
- `scikit-learn`: 机器学习算法（异常检测）
- `plotly`: 交互式图表
- `matplotlib/seaborn`: 静态图表
- `openpyxl/xlrd`: Excel文件读写
- `jinja2`: HTML模板引擎
- `loguru`: 日志记录

## 使用方法

### 1. 快速开始

#### 创建示例数据并运行分析
```bash
# 运行完整示例
python example_kpi_analysis.py
```

#### 使用命令行工具
```bash
# 创建示例Excel文件
python src/kpi_excel_analyzer.py --create-sample

# 分析Excel文件
python src/kpi_excel_analyzer.py your_kpi_data.xlsx

# 分析特定指标
python src/kpi_excel_analyzer.py your_kpi_data.xlsx --metric "在编人数"

# 分析特定部门
python src/kpi_excel_analyzer.py your_kpi_data.xlsx --department "技术部"

# 进行关联关系分析
python src/kpi_excel_analyzer.py your_kpi_data.xlsx --associations

# 导出结果到Excel
python src/kpi_excel_analyzer.py your_kpi_data.xlsx --export-excel results.xlsx
```

### 2. 编程接口使用

#### 基础分析
```python
from src.kpi_excel_analyzer import KPIExcelAnalyzer

# 初始化分析器
analyzer = KPIExcelAnalyzer()

# 进行完整分析
results = analyzer.analyze_excel_file("your_kpi_data.xlsx")

# 查看结果
print(f"报告路径: {results['report_path']}")
print(f"异常指标数量: {len(results['analysis_results']['anomalies'])}")
```

#### 特定指标分析
```python
# 分析特定指标
results = analyzer.analyze_specific_metric("your_kpi_data.xlsx", "在编人数")

# 获取异常检测结果
anomalies = results['analysis_results']['anomalies']
for method, result in anomalies['value'].items():
    if result.get('anomalies'):
        count = sum(result['anomalies'])
        print(f"{method}: {count}个异常")
```

#### 手动分析流程
```python
from src.utils.excel_reader import ExcelKPIReader
from src.analysis.kpi_anomaly_detector import KPIComprehensiveAnalyzer

# 1. 读取数据
reader = ExcelKPIReader("your_kpi_data.xlsx")
data = reader.read_excel()

# 2. 检测列类型
column_info = reader.detect_columns()

# 3. 进行异常检测
analyzer = KPIComprehensiveAnalyzer()
results = analyzer.analyze_kpi_data(
    data=data,
    department_column=column_info['department_column'],
    metric_columns=column_info['metric_columns'],
    time_columns=column_info['quarter_columns']
)
```

#### 关联关系挖掘
```python
from src.analysis.kpi_association_miner import KPIAssociationMiner, KPIAssociationAnomalyDetector

# 1. 初始化关联关系挖掘器
miner = KPIAssociationMiner()
detector = KPIAssociationAnomalyDetector(miner)

# 2. 发现关联关系
association_results = miner.discover_associations(
    data=data,
    metric_columns=column_info['metric_columns']
)

# 3. 构建基线并检测异常
baseline = detector.build_baseline(data, column_info['metric_columns'])
anomalies = detector.detect_association_anomalies(new_data, column_info['metric_columns'])

# 4. 生成洞察
insights = detector.generate_anomaly_insights(anomalies)
```

### 3. Excel数据格式要求

#### 基本格式
- **部门列**: 包含部门名称的列（如"部门名称"、"部门"等）
- **季度列**: 格式为YYYYQ[1-4]的列（如"2025Q1"、"2025Q2"等）
- **指标列**: 其他数值列作为KPI指标

#### 示例数据结构
| 部门名称 | 在编人数 | 执行用例数 | 2025Q1_在编人数 | 2025Q1_执行用例数 | 2025Q2_在编人数 | 2025Q2_执行用例数 |
|---------|---------|-----------|----------------|------------------|----------------|------------------|
| 技术部   | 50      | 1000      | 45             | 950              | 52             | 1050             |
| 产品部   | 30      | 500       | 28             | 480              | 32             | 520              |

## 配置说明

### 配置文件 (config/kpi_config.yaml)
```yaml
# 分析配置
analysis_config:
  # 分布分析配置
  distribution:
    bins: 20
    outlier_method: "iqr"
    
  # 趋势分析配置
  trend:
    window_size: 3
    seasonality: 4
    
  # 异常检测配置
  anomaly:
    method: "isolation_forest"
    contamination: 0.1
    threshold: 0.95

# 报告配置
report_config:
  output_format: ["html"]
  charts:
    - distribution_histogram
    - trend_line
    - anomaly_scatter
  auto_generate: true
```

## 异常检测算法

### 1. Isolation Forest
- **原理**: 基于异常点更容易被隔离的特性
- **适用**: 高维数据，计算效率高
- **参数**: contamination（异常比例）

### 2. Local Outlier Factor (LOF)
- **原理**: 基于局部密度比较
- **适用**: 能够检测局部异常
- **参数**: n_neighbors（邻居数量）

### 3. IQR方法
- **原理**: 基于四分位距的统计方法
- **适用**: 单变量异常检测
- **参数**: factor（倍数因子，默认1.5）

### 4. Z-score方法
- **原理**: 基于标准差的统计方法
- **适用**: 正态分布数据
- **参数**: threshold（阈值，默认3.0）

## 输出结果

### 1. HTML报告
- **数据摘要**: 部门数量、指标数量、数据质量等
- **异常检测结果**: 各指标的异常检测结果和可视化
- **趋势分析**: 趋势斜率、波动性、季节性分析
- **部门对比**: 部门间的指标对比热力图
- **分析建议**: 基于结果的改进建议

### 2. Excel导出
- **数据摘要表**: 基本统计信息
- **异常检测结果表**: 详细的异常检测结果
- **趋势分析结果表**: 趋势分析数据
- **建议表**: 分析建议汇总

### 3. 控制台输出
- **分析进度**: 实时显示分析进度
- **摘要信息**: 关键指标摘要
- **错误信息**: 详细的错误和警告信息

## 最佳实践

### 1. 数据准备
- 确保Excel文件格式规范
- 检查数据完整性，处理缺失值
- 验证数值数据的有效性
- 统一列名命名规范

### 2. 参数调优
- 根据数据特点选择合适的异常检测算法
- 调整contamination参数控制异常检测敏感度
- 根据业务需求设置趋势分析窗口大小

### 3. 结果解读
- 结合业务背景理解异常检测结果
- 关注趋势变化的关键时间点
- 对比不同部门的指标表现
- 定期更新分析模型

### 4. 系统维护
- 定期更新依赖包版本
- 监控系统性能和资源使用
- 备份重要的分析结果
- 记录分析参数和配置变更

## 故障排除

### 常见问题

#### 1. 依赖包安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2. Excel文件读取失败
- 检查文件格式是否为.xlsx或.xls
- 确认文件没有被其他程序占用
- 验证文件路径是否正确

#### 3. 内存不足
- 减少同时处理的指标数量
- 使用数据采样进行分析
- 增加系统内存或使用云服务器

#### 4. 图表显示异常
- 检查中文字体是否正确安装
- 确认plotly版本兼容性
- 尝试使用不同的浏览器打开HTML报告

### 日志查看
系统使用loguru进行日志记录，可以通过以下方式查看详细日志：
```python
from loguru import logger

# 设置日志级别
logger.add("kpi_analysis.log", level="DEBUG")
```

## 扩展开发

### 1. 添加新的异常检测算法
```python
class CustomAnomalyDetector:
    def detect_anomalies(self, data, **kwargs):
        # 实现自定义异常检测逻辑
        pass
```

### 2. 自定义报告模板
- 修改`src/visualization/kpi_report_generator.py`中的HTML模板
- 添加新的图表类型
- 自定义CSS样式

### 3. 集成其他数据源
- 扩展`ExcelKPIReader`类支持其他数据格式
- 添加数据库连接功能
- 支持API数据接口

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。在提交代码前，请确保：
1. 代码符合PEP 8规范
2. 添加适当的测试用例
3. 更新相关文档
4. 通过所有测试

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本系统仅用于数据分析，不保证分析结果的准确性。在实际业务决策中，请结合专业知识和业务背景进行综合判断。
