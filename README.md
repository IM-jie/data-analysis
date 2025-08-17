# 数据分析项目 - KPI指标分析

## 项目概述

本项目是一个基于ClickHouse数据仓库的KPI指标数据分析系统，主要功能包括：

- **数据连接**: 连接ClickHouse数据仓库
- **KPI计算**: 通过SQL计算各种KPI指标
- **数据挖掘**: 数据分布分析、趋势分析、异常检测
- **可视化**: 生成分析图表和报告

## 项目结构

```
data-analysis/
├── config/                 # 配置文件
│   ├── database.yaml      # 数据库连接配置
│   └── kpi_config.yaml    # KPI指标配置
├── src/                   # 源代码
│   ├── database/          # 数据库连接模块
│   ├── kpi/              # KPI计算模块
│   ├── analysis/         # 数据分析模块
│   ├── visualization/    # 可视化模块
│   └── utils/            # 工具函数
├── sql/                  # SQL查询文件
├── reports/              # 分析报告输出
├── notebooks/            # Jupyter笔记本
└── tests/                # 测试文件
```

## 安装和配置

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置数据库连接：
   - 复制 `config/database.yaml.example` 为 `config/database.yaml`
   - 修改数据库连接参数

3. 配置KPI指标：
   - 编辑 `config/kpi_config.yaml` 文件
   - 定义需要分析的KPI指标

## 使用方法

### 基本使用

```python
from src.database.connection import ClickHouseConnector
from src.kpi.calculator import KPICalculator
from src.analysis.analyzer import DataAnalyzer

# 连接数据库
connector = ClickHouseConnector()
calculator = KPICalculator(connector)

# 计算KPI指标
kpi_data = calculator.calculate_kpi('user_retention_rate')

# 数据分析
analyzer = DataAnalyzer()
analysis_result = analyzer.analyze_distribution(kpi_data)
```

### 运行分析报告

```bash
python -m src.main --kpi user_retention_rate --analysis distribution,trend,anomaly
```

## 主要功能

### 1. KPI指标计算
- 用户留存率
- 转化率
- 活跃用户数
- 收入指标
- 自定义指标

### 2. 数据分析
- **分布分析**: 数据分布情况统计
- **趋势分析**: 时间序列趋势分析
- **异常检测**: 自动标识异常数据点

### 3. 可视化
- 分布直方图
- 趋势线图
- 异常点标记
- 交互式图表

## 配置说明

### 数据库配置 (config/database.yaml)
```yaml
clickhouse:
  host: localhost
  port: 9000
  database: analytics
  user: default
  password: ""
```

### KPI配置 (config/kpi_config.yaml)
```yaml
kpi_metrics:
  user_retention_rate:
    sql_file: "user_retention.sql"
    description: "用户留存率"
    unit: "%"
    threshold:
      warning: 0.3
      critical: 0.2
```

## 开发指南

1. 添加新的KPI指标：
   - 在 `sql/` 目录下创建SQL文件
   - 在 `config/kpi_config.yaml` 中配置指标参数

2. 添加新的分析方法：
   - 在 `src/analysis/` 目录下创建分析模块
   - 实现相应的分析函数

3. 添加新的可视化：
   - 在 `src/visualization/` 目录下创建可视化模块

## 测试

```bash
python -m pytest tests/
```

## 许可证

MIT License


