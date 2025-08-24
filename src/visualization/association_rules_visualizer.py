#!/usr/bin/env python3
"""
Apriori关联规则可视化模块
提供多种可视化方式展示关联规则之间的关系
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from typing import List, Dict, Any, Optional
from pathlib import Path

# 导入中文字体管理器
try:
    from ..utils.chinese_font_manager import ChineseFontManager
    font_manager = ChineseFontManager()
except ImportError:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from utils.chinese_font_manager import ChineseFontManager
        font_manager = ChineseFontManager()
    except ImportError:
        font_manager = None


class AssociationRulesVisualizer:
    """Apriori关联规则可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        self.setup_matplotlib()
        
    def setup_matplotlib(self):
        """设置matplotlib中文支持"""
        if font_manager:
            try:
                font_manager._setup_matplotlib_font()
            except AttributeError:
                # 如果方法不存在，尝试其他方法
                if hasattr(font_manager, 'setup_matplotlib'):
                    font_manager.setup_matplotlib()
        plt.style.use('default')
        
    def visualize_association_rules(self, 
                                  rules: List[Dict],
                                  output_dir: str = "reports",
                                  format: str = "both") -> Dict[str, str]:
        """
        生成关联规则的多种可视化图表
        
        Args:
            rules: 关联规则列表
            output_dir: 输出目录
            format: 输出格式 ('matplotlib', 'plotly', 'both')
            
        Returns:
            生成的图表文件路径字典
        """
        if not rules:
            print("⚠️ 没有关联规则可供可视化")
            return {}
        
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # 1. 网络图 - 展示规则之间的关系
        if format in ['matplotlib', 'both']:
            network_file = self.create_network_graph(rules, output_dir)
            if network_file:
                generated_files['network_matplotlib'] = network_file
        
        if format in ['plotly', 'both']:
            network_plotly_file = self.create_interactive_network(rules, output_dir)
            if network_plotly_file:
                generated_files['network_plotly'] = network_plotly_file
        
        # 2. 气泡图 - 支持度、置信度、提升度关系
        if format in ['plotly', 'both']:
            bubble_plotly_file = self.create_interactive_bubble_chart(rules, output_dir)
            if bubble_plotly_file:
                generated_files['bubble_plotly'] = bubble_plotly_file
        
        # 3. 热力图 - 规则强度矩阵
        if format in ['matplotlib', 'both']:
            heatmap_file = self.create_rules_heatmap(rules, output_dir)
            if heatmap_file:
                generated_files['heatmap_matplotlib'] = heatmap_file
        
        print(f"✅ 生成了 {len(generated_files)} 个关联规则可视化图表")
        return generated_files
    
    def create_network_graph(self, rules: List[Dict], output_dir: str) -> Optional[str]:
        """创建关联规则网络图（matplotlib版本）"""
        try:
            # 创建有向图
            G = nx.DiGraph()
            
            # 添加节点和边
            for rule in rules:
                antecedents = rule.get('antecedents', [])
                consequents = rule.get('consequents', [])
                confidence = rule.get('confidence', 0)
                lift = rule.get('lift', 1)
                
                # 添加节点
                for ant in antecedents:
                    G.add_node(ant, node_type='antecedent')
                for cons in consequents:
                    G.add_node(cons, node_type='consequent')
                
                # 添加边
                for ant in antecedents:
                    for cons in consequents:
                        G.add_edge(ant, cons, confidence=confidence, lift=lift, weight=confidence)
            
            if len(G.nodes()) == 0:
                return None
            
            # 创建图形
            plt.figure(figsize=(16, 12))
            
            # 计算布局
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # 绘制节点
            node_colors = []
            node_sizes = []
            for node in G.nodes():
                degree = G.degree(node)
                node_sizes.append(300 + degree * 100)
                
                # 根据节点类型设置颜色
                if any(node in rule.get('antecedents', []) for rule in rules):
                    node_colors.append('#FF6B6B')  # 前置条件 - 红色
                else:
                    node_colors.append('#4ECDC4')  # 后置条件 - 青色
            
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
            
            # 绘制边
            edge_weights = [G[u][v]['confidence'] * 5 for u, v in G.edges()]
            edge_colors = [G[u][v]['lift'] for u, v in G.edges()]
            
            edges = nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color=edge_colors,
                                        edge_cmap=plt.cm.viridis, alpha=0.6, arrows=True,
                                        arrowsize=20, arrowstyle='->')
            
            # 添加节点标签
            labels = {node: node[:12] + '...' if len(node) > 15 else node for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
            
            # 添加颜色条和标题
            plt.colorbar(edges, label='提升度 (Lift)')
            plt.title('关联规则网络图\\n节点大小：度中心性 | 边粗细：置信度 | 边颜色：提升度', 
                     fontsize=14, pad=20)
            plt.axis('off')
            
            # 添加图例
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', 
                          markersize=10, label='前置条件'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', 
                          markersize=10, label='后置条件')
            ]
            plt.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
            
            output_file = f"{output_dir}/association_rules_network.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 关联规则网络图已生成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ 创建网络图失败: {e}")
            return None
    
    def create_interactive_network(self, rules: List[Dict], output_dir: str) -> Optional[str]:
        """创建交互式关联规则网络图（Plotly版本）"""
        try:
            # 构建节点和边数据
            nodes = set()
            edges = []
            
            for rule in rules:
                antecedents = rule.get('antecedents', [])
                consequents = rule.get('consequents', [])
                confidence = rule.get('confidence', 0)
                support = rule.get('support', 0)
                lift = rule.get('lift', 1)
                
                nodes.update(antecedents)
                nodes.update(consequents)
                
                for ant in antecedents:
                    for cons in consequents:
                        edges.append({
                            'source': ant, 'target': cons,
                            'confidence': confidence, 'support': support, 'lift': lift
                        })
            
            if not nodes:
                return None
            
            # 创建网络图
            G = nx.DiGraph()
            for edge in edges:
                G.add_edge(edge['source'], edge['target'], **edge)
            
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # 准备节点数据
            node_x, node_y, node_text, node_size, node_color = [], [], [], [], []
            
            for node in nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
                
                degree = G.degree(node)
                node_size.append(10 + degree * 5)
                
                if any(node in rule.get('antecedents', []) for rule in rules):
                    node_color.append(1)  # 前置条件
                else:
                    node_color.append(0)  # 后置条件
            
            # 准备边数据
            edge_x, edge_y = [], []
            
            for edge in edges:
                x0, y0 = pos[edge['source']]
                x1, y1 = pos[edge['target']]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            # 创建图形
            fig = go.Figure()
            
            # 添加边
            fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'),
                                   hoverinfo='none', mode='lines', name='关联关系'))
            
            # 添加节点
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y, mode='markers+text', hoverinfo='text',
                text=node_text, textposition="middle center",
                hovertext=[f"节点: {text}<br>度: {G.degree(text)}" for text in node_text],
                marker=dict(size=node_size, color=node_color, colorscale=['lightblue', 'orange'],
                          showscale=True, colorbar=dict(title="节点类型", tickvals=[0, 1],
                          ticktext=["后置条件", "前置条件"]), line=dict(width=2)),
                name='字段节点'
            ))
            
            fig.update_layout(
                title=dict(text='交互式关联规则网络图<br><sub>鼠标悬停查看详情</sub>', x=0.5),
                showlegend=True, hovermode='closest', margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                font=dict(family="Microsoft YaHei, Arial")
            )
            
            output_file = f"{output_dir}/association_rules_network_interactive.html"
            fig.write_html(output_file)
            
            print(f"📊 交互式关联规则网络图已生成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ 创建交互式网络图失败: {e}")
            return None
    
    def create_interactive_bubble_chart(self, rules: List[Dict], output_dir: str) -> Optional[str]:
        """创建交互式关联规则气泡图"""
        try:
            if not rules:
                return None
            
            # 准备数据
            rule_data = []
            for i, rule in enumerate(rules):
                ant_str = ' & '.join(rule.get('antecedents', []))
                cons_str = ' & '.join(rule.get('consequents', []))
                
                rule_data.append({
                    'rule_id': f"规则{i+1}",
                    'antecedents': ant_str,
                    'consequents': cons_str,
                    'support': rule.get('support', 0),
                    'confidence': rule.get('confidence', 0),
                    'lift': rule.get('lift', 1),
                    'rule_text': f"{ant_str} → {cons_str}"
                })
            
            df = pd.DataFrame(rule_data)
            
            # 创建交互式气泡图
            fig = px.scatter(
                df, x='support', y='confidence', size='lift', color='lift',
                hover_name='rule_id',
                hover_data={'antecedents': True, 'consequents': True,
                          'support': ':.3f', 'confidence': ':.3f', 'lift': ':.3f'},
                labels={'support': '支持度 (Support)', 'confidence': '置信度 (Confidence)', 'lift': '提升度 (Lift)'},
                title='交互式关联规则气泡图<br><sub>气泡大小和颜色表示提升度</sub>',
                color_continuous_scale='viridis'
            )
            
            fig.update_traces(marker=dict(sizemin=5, sizemax=50, line=dict(width=1, color='white')))
            fig.update_layout(font=dict(family="Microsoft YaHei, Arial"), hovermode='closest')
            
            output_file = f"{output_dir}/association_rules_bubble_interactive.html"
            fig.write_html(output_file)
            
            print(f"📊 交互式关联规则气泡图已生成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ 创建交互式气泡图失败: {e}")
            return None
    
    def create_rules_heatmap(self, rules: List[Dict], output_dir: str) -> Optional[str]:
        """创建关联规则强度热力图"""
        try:
            if not rules:
                return None
            
            # 收集所有项目
            all_items = set()
            for rule in rules:
                all_items.update(rule.get('antecedents', []))
                all_items.update(rule.get('consequents', []))
            
            if len(all_items) < 2:
                return None
            
            all_items = sorted(list(all_items))
            
            # 创建关联矩阵
            matrix = np.zeros((len(all_items), len(all_items)))
            
            for rule in rules:
                antecedents = rule.get('antecedents', [])
                consequents = rule.get('consequents', [])
                confidence = rule.get('confidence', 0)
                
                for ant in antecedents:
                    for cons in consequents:
                        i = all_items.index(ant)
                        j = all_items.index(cons)
                        matrix[i, j] = max(matrix[i, j], confidence)
            
            # 创建热力图
            plt.figure(figsize=(12, 10))
            
            # 处理标签长度
            labels = [item[:20] + '...' if len(item) > 20 else item for item in all_items]
            
            sns.heatmap(matrix, xticklabels=labels, yticklabels=labels,
                       annot=True, fmt='.2f', cmap='YlOrRd',
                       cbar_kws={'label': '关联强度 (置信度)'})
            
            plt.title('关联规则强度矩阵热力图\\n行→列的关联强度')
            plt.xlabel('后置条件 (Consequents)')
            plt.ylabel('前置条件 (Antecedents)')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            
            plt.tight_layout()
            
            output_file = f"{output_dir}/association_rules_heatmap.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 关联规则热力图已生成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ 创建热力图失败: {e}")
            return None
    
    def generate_visualization_summary(self, rules: List[Dict], generated_files: Dict[str, str]) -> str:
        """生成可视化总结报告"""
        if not rules:
            return "没有关联规则可分析"
        
        # 计算统计信息
        avg_confidence = np.mean([rule.get('confidence', 0) for rule in rules])
        avg_support = np.mean([rule.get('support', 0) for rule in rules])
        avg_lift = np.mean([rule.get('lift', 1) for rule in rules])
        
        high_confidence_rules = len([r for r in rules if r.get('confidence', 0) > 0.8])
        high_lift_rules = len([r for r in rules if r.get('lift', 1) > 1.5])
        
        summary = f"""
# 关联规则可视化分析报告

## 📊 数据概览
- 总关联规则数: {len(rules)}
- 生成的可视化图表: {len(generated_files)}
- 平均置信度: {avg_confidence:.3f}
- 平均支持度: {avg_support:.3f}
- 平均提升度: {avg_lift:.3f}
- 高置信度规则(>0.8): {high_confidence_rules}
- 高提升度规则(>1.5): {high_lift_rules}

## 📈 可视化图表
"""
        
        for chart_type, file_path in generated_files.items():
            summary += f"- {chart_type}: {file_path}\n"
        
        summary += """

## 🎯 分析建议

1. **高价值规则识别**: 关注置信度>0.8且提升度>1.5的规则
2. **网络分析**: 查看网络图中的核心节点和关键路径
3. **热力图分析**: 识别强关联的字段组合
4. **气泡图筛选**: 寻找位于右上角的高质量规则
"""
        
        return summary