# 项目数据关联规则挖掘功能

本文档介绍如何使用项目数据关联规则挖掘功能，对ClickHouse表中的项目测试数据进行深度分析，发现潜在的关联规则和模式。

## 功能概述

项目数据挖掘功能专门用于分析包含以下字段的项目测试数据：
- 项目名称、项目编号、项目类型、项目级别
- 产品线、产品类型
- 测试负责人、测试负责人所属组织架构
- 执行用例数、自动化执行用例数、关联缺陷、投入工时

## 支持的分析类型

### 1. 分类关联分析
- **卡方检验**: 检测分类字段间的关联性
- **Cramer's V**: 衡量关联强度
- **关联规则挖掘**: 使用Apriori算法发现频繁模式

### 2. 数值相关性分析
- **Pearson相关系数**: 线性相关性
- **Spearman相关系数**: 等级相关性
- **Kendall相关系数**: 等级一致性

### 3. 交叉类型关联
- **方差分析(ANOVA)**: 分类字段对数值字段的影响
- **组间差异分析**: 识别显著性差异

### 4. 模式识别
- **质量效率模式**: 自动化率、缺陷密度、测试效率的关系
- **组织绩效模式**: 不同组织的表现差异
- **产品洞察**: 产品线和产品类型的特征分析

## 快速开始

### 1. 运行简化测试

```bash
# 运行基础功能测试
python test_project_mining.py
```

这将创建示例数据并执行基础的关联规则挖掘分析。

### 2. 分析Excel数据

```python
from analysis.project_data_miner import ProjectDataMiner
import pandas as pd

# 读取项目数据
data = pd.read_excel('your_project_data.xlsx')

# 初始化挖掘器
config = {
    'min_support': 0.1,
    'min_confidence': 0.5,
    'correlation_threshold': 0.6
}
miner = ProjectDataMiner(config)

# 执行关联规则挖掘
results = miner.discover_project_associations(data)

# 查看结果
print("强分类关联:")
for assoc in results['categorical_associations']['strong_associations']:
    print(f"  {assoc['field1']} <-> {assoc['field2']}: {assoc['cramers_v']:.3f}")

print("强数值相关性:")
for corr in results['numerical_correlations']['strong_correlations']:
    print(f"  {corr['field1']} <-> {corr['field2']}: {corr['correlation']:.3f}")
```

### 3. 分析ClickHouse数据

```python
from analysis.project_clickhouse_analyzer import ProjectClickHouseAnalyzer

# 初始化分析器
analyzer = ProjectClickHouseAnalyzer(config_path='config/clickhouse_config.yaml')

# 分析项目数据表
results = analyzer.analyze_project_table(
    table_name='project_test_data',
    custom_field_mapping={
        'project_name': 'prj_name',
        'executed_cases': 'test_cases_count'
    },
    where_condition="test_date >= '2024-01-01'",
    limit=1000
)

# 查看分析摘要
summary = results['summary']
print(f"总项目数: {summary['total_projects']}")
print(f"关键关联: {len(summary['key_associations'])}")
print(f"主要相关性: {len(summary['main_correlations'])}")
```

## 专门分析功能

### 1. 组织绩效分析

```python
# 按组织分析项目性能
org_analysis = analyzer.analyze_project_performance_by_organization(
    table_name='project_test_data'
)

# 查看组织排名
rankings = org_analysis['organization_insights']['organization_rankings']
print("组织绩效排名:")
for rank, (org, score) in enumerate(rankings.items(), 1):
    print(f"  {rank}. {org}: {score:.3f}")
```

### 2. 产品线效率分析

```python
# 分析产品线效率
efficiency_analysis = analyzer.analyze_product_line_efficiency(
    table_name='project_test_data'
)

# 查看效率模式
patterns = efficiency_analysis['efficiency_analysis']['efficiency_patterns']
print("效率模式:")
for pattern in patterns:
    print(f"  {pattern['description']}: {pattern['impact']}")
```

### 3. 质量模式发现

```python
# 发现质量模式
quality_patterns = analyzer.discover_quality_patterns(
    table_name='project_test_data',
    quality_threshold=0.1  # 10%缺陷率阈值
)

# 查看质量洞察
high_quality = quality_patterns['quality_patterns']['high_quality_patterns']
print("高质量模式:")
for pattern in high_quality:
    print(f"  {pattern['pattern']}: {pattern['characteristics']}")
```

## 配置说明

### ClickHouse配置 (config/clickhouse_config.yaml)

```yaml
# ClickHouse数据库配置
clickhouse:
  host: localhost
  port: 18123
  username: default
  password: your_password
  database: project_db
  secure: false

# 数据挖掘配置
data_mining:
  min_support: 0.1        # Apriori最小支持度
  min_confidence: 0.5     # 关联规则最小置信度
  min_lift: 1.2          # 最小提升度
  correlation_threshold: 0.6  # 强相关性阈值
```

### 字段映射配置

如果您的数据表字段名与标准字段名不同，可以使用自定义映射：

```python
custom_field_mapping = {
    'project_name': 'prj_name',
    'project_id': 'prj_id', 
    'project_type': 'prj_type',
    'project_level': 'prj_level',
    'product_line': 'prod_line',
    'product_type': 'prod_type',
    'test_owner': 'tester_name',
    'test_owner_org': 'tester_org',
    'executed_cases': 'test_cases_executed',
    'automated_cases': 'auto_test_cases',
    'related_bugs': 'bug_count',
    'effort_hours': 'work_hours'
}
```

## 分析结果解读

### 1. 关联强度解释

- **Cramer's V值**:
  - < 0.1: 弱关联
  - 0.1-0.3: 中等关联
  - 0.3-0.5: 强关联
  - > 0.5: 非常强关联

- **相关系数**:
  - |r| < 0.3: 弱相关
  - 0.3 ≤ |r| < 0.7: 中等相关
  - |r| ≥ 0.7: 强相关

### 2. 质量指标基准

- **自动化率**: 建议 > 60%
- **缺陷密度**: 建议 < 5%
- **测试效率**: 建议 > 2 用例/小时

### 3. 显著性判断

- **p值 < 0.05**: 统计显著
- **p值 ≥ 0.05**: 无统计显著性

## 实际应用场景

### 1. 测试策略优化
通过分析项目类型与自动化率的关系，制定针对性的自动化策略。

### 2. 资源配置优化
基于组织绩效分析结果，优化测试资源在不同组织间的配置。

### 3. 质量风险预警
识别高缺陷密度的项目特征模式，建立质量风险预警机制。

### 4. 效率提升建议
分析测试效率与各因素的关系，提出流程优化建议。

## 生成的报告

系统会自动生成HTML格式的分析报告，包含：

1. **数据概览**: 项目数量、字段分布等基础信息
2. **关联规则发现**: 分类字段间的关联关系
3. **数值相关性分析**: 连续变量间的相关性
4. **组织绩效分析**: 各组织的表现对比
5. **产品洞察**: 产品维度的分析结果
6. **关键发现与建议**: 总结性洞察和改进建议

报告保存路径: `reports/project_mining/project_mining_{table_name}_{timestamp}.html`

## 故障排除

### 1. 连接问题
- 确保ClickHouse服务正在运行
- 检查连接配置是否正确
- 验证网络连通性

### 2. 字段映射问题
- 检查字段名是否正确
- 确认字段类型匹配
- 使用custom_field_mapping参数进行映射

### 3. 数据质量问题
- 检查数据是否包含足够的记录
- 确认关键字段不全为空值
- 验证数值字段的数据类型

## 扩展开发

如需扩展功能，可以：

1. 在`ProjectDataMiner`类中添加新的分析方法
2. 在`ProjectClickHouseAnalyzer`类中添加新的业务分析
3. 扩展报告生成模板
4. 添加新的可视化图表

## 技术支持

如遇到问题，请检查：
1. 依赖包是否完整安装
2. 配置文件是否正确
3. 数据格式是否符合要求
4. 查看日志文件获取详细错误信息

更多技术细节请参考源代码注释和API文档。