"""
可视化展示与仪表盘模块
生成动态可视化图表和仪表盘
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import logging
from config import VISUALIZATIONS_DIR

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Visualizer:
    """可视化生成器"""
    
    def __init__(self, cleaned_data, kpi_results):
        self.cleaned_data = cleaned_data
        self.kpi_results = kpi_results
        self.figures = {}
    
    def create_all_visualizations(self):
        """创建所有可视化图表"""
        logger.info("开始生成可视化图表...")
        
        # 1. KPI仪表盘
        self.create_kpi_dashboard()
        
        # 2. 市值趋势图
        if 'market_cap' in self.cleaned_data:
            self.create_market_cap_charts()
        
        # 3. 媒体曝光度图表
        if 'media_exposure' in self.cleaned_data:
            self.create_media_exposure_charts()
        
        # 4. 社交媒体互动图表
        if 'social_media' in self.cleaned_data:
            self.create_social_media_charts()
        
        # 5. 投资者关系图表
        if 'investor_relations' in self.cleaned_data:
            self.create_investor_relations_charts()
        
        # 6. 风险与声誉图表
        if 'risk_reputation' in self.cleaned_data:
            self.create_risk_reputation_charts()
        
        # 7. 综合对比图
        self.create_comparison_charts()
        
        logger.info("可视化图表生成完成")
        return self.figures
    
    def create_kpi_dashboard(self):
        """创建KPI仪表盘"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('市值指标', '媒体曝光', '社交互动', '投资者关系', '风险管控', '综合评分'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # 市值指标
        if 'market_cap' in self.kpi_results:
            market_kpis = self.kpi_results['market_cap']
            if 'market_cap_growth_rate' in market_kpis:
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number+delta",
                        value=market_kpis.get('market_cap_growth_rate', 0),
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "市值增长率(%)"},
                        delta={'reference': 0},
                        gauge={'axis': {'range': [-100, 100]},
                               'bar': {'color': "darkblue"},
                               'steps': [{'range': [-100, 0], 'color': "lightgray"},
                                        {'range': [0, 50], 'color': "gray"}],
                               'threshold': {'line': {'color': "red", 'width': 4},
                                           'thickness': 0.75, 'value': 90}}
                    ),
                    row=1, col=1
                )
        
        # 媒体曝光
        if 'media_exposure' in self.kpi_results:
            media_kpis = self.kpi_results['media_exposure']
            if 'total_articles' in media_kpis:
                fig.add_trace(
                    go.Indicator(
                        mode="number",
                        value=media_kpis.get('total_articles', 0),
                        title={'text': "总发稿量"},
                        number={'font': {'size': 40}}
                    ),
                    row=1, col=2
                )
        
        # 社交互动
        if 'social_media' in self.kpi_results:
            social_kpis = self.kpi_results['social_media']
            if 'engagement_rate' in social_kpis:
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=social_kpis.get('engagement_rate', 0),
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "互动率(%)"},
                        gauge={'axis': {'range': [0, 10]},
                               'bar': {'color': "darkgreen"},
                               'steps': [{'range': [0, 3], 'color': "lightgray"},
                                        {'range': [3, 6], 'color': "gray"}],
                               'threshold': {'line': {'color': "red", 'width': 4},
                                           'thickness': 0.75, 'value': 8}}
                    ),
                    row=1, col=3
                )
        
        fig.update_layout(height=600, title_text="KPI综合仪表盘")
        self.figures['kpi_dashboard'] = fig
        self._save_figure(fig, 'kpi_dashboard.html')
    
    def create_market_cap_charts(self):
        """创建市值相关图表"""
        df = self.cleaned_data['market_cap']
        
        # 查找市值和股价列
        market_cap_cols = [col for col in df.columns if '市值' in col or 'market_cap' in col.lower()]
        price_cols = [col for col in df.columns if '股价' in col or 'price' in col.lower()]
        date_cols = [col for col in df.columns if 'date' in col.lower() or '时间' in col or '日期' in col]
        
        if market_cap_cols:
            market_cap_col = market_cap_cols[0]
            fig = go.Figure()
            
            # 如果有日期列，按日期排序
            if date_cols:
                date_col = date_cols[0]
                try:
                    df['_date'] = pd.to_datetime(df[date_col])
                    df_sorted = df.sort_values('_date')
                    fig.add_trace(go.Scatter(
                        x=df_sorted['_date'],
                        y=df_sorted[market_cap_col],
                        mode='lines+markers',
                        name='市值',
                        line=dict(color='blue', width=2)
                    ))
                except:
                    fig.add_trace(go.Scatter(
                        y=df[market_cap_col],
                        mode='lines+markers',
                        name='市值',
                        line=dict(color='blue', width=2)
                    ))
            else:
                fig.add_trace(go.Scatter(
                    y=df[market_cap_col],
                    mode='lines+markers',
                    name='市值',
                    line=dict(color='blue', width=2)
                ))
            
            fig.update_layout(
                title='市值趋势图',
                xaxis_title='时间',
                yaxis_title='市值',
                height=400
            )
            self.figures['market_cap_trend'] = fig
            self._save_figure(fig, 'market_cap_trend.html')
    
    def create_media_exposure_charts(self):
        """创建媒体曝光度图表"""
        df = self.cleaned_data['media_exposure']
        
        # 查找相关列
        article_cols = [col for col in df.columns if '发稿' in col or '文章' in col or 'article' in col.lower()]
        read_cols = [col for col in df.columns if '阅读' in col or 'read' in col.lower()]
        media_cols = [col for col in df.columns if '媒体' in col or 'media' in col.lower()]
        
        if article_cols and read_cols:
            article_col = article_cols[0]
            read_col = read_cols[0]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df[article_col] if df[article_col].dtype == 'object' else range(len(df)),
                y=df[read_col] if read_col in df.columns and df[read_col].dtype in ['int64', 'float64'] else [0] * len(df),
                name='阅读量',
                marker_color='skyblue'
            ))
            
            fig.update_layout(
                title='媒体曝光度分析',
                xaxis_title='文章',
                yaxis_title='阅读量',
                height=400
            )
            self.figures['media_exposure'] = fig
            self._save_figure(fig, 'media_exposure.html')
        
        # 媒体分布饼图
        if media_cols:
            media_col = media_cols[0]
            if media_col in df.columns and df[media_col].dtype == 'object':
                media_counts = df[media_col].value_counts().head(10)
                fig = go.Figure(data=[go.Pie(
                    labels=media_counts.index,
                    values=media_counts.values,
                    hole=0.3
                )])
                fig.update_layout(title='媒体分布', height=400)
                self.figures['media_distribution'] = fig
                self._save_figure(fig, 'media_distribution.html')
    
    def create_social_media_charts(self):
        """创建社交媒体互动图表"""
        df = self.cleaned_data['social_media']
        
        # 查找相关列
        like_cols = [col for col in df.columns if '点赞' in col or 'like' in col.lower()]
        comment_cols = [col for col in df.columns if '评论' in col or 'comment' in col.lower()]
        share_cols = [col for col in df.columns if '转发' in col or 'share' in col.lower()]
        
        engagement_data = {}
        if like_cols:
            like_col = like_cols[0]
            if like_col in df.columns and df[like_col].dtype in ['int64', 'float64']:
                engagement_data['点赞'] = df[like_col].sum()
        
        if comment_cols:
            comment_col = comment_cols[0]
            if comment_col in df.columns and df[comment_col].dtype in ['int64', 'float64']:
                engagement_data['评论'] = df[comment_col].sum()
        
        if share_cols:
            share_col = share_cols[0]
            if share_col in df.columns and df[share_col].dtype in ['int64', 'float64']:
                engagement_data['转发'] = df[share_col].sum()
        
        if engagement_data:
            fig = go.Figure(data=[go.Bar(
                x=list(engagement_data.keys()),
                y=list(engagement_data.values()),
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )])
            fig.update_layout(
                title='社交媒体互动分析',
                xaxis_title='互动类型',
                yaxis_title='数量',
                height=400
            )
            self.figures['social_engagement'] = fig
            self._save_figure(fig, 'social_engagement.html')
    
    def create_investor_relations_charts(self):
        """创建投资者关系图表"""
        df = self.cleaned_data['investor_relations']
        
        # 查找相关列
        trading_cols = [col for col in df.columns if '交易' in col or 'trading' in col.lower() or '成交' in col]
        
        if trading_cols:
            trading_col = trading_cols[0]
            if trading_col in df.columns and df[trading_col].dtype in ['int64', 'float64']:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=df[trading_col],
                    mode='lines+markers',
                    name='交易额',
                    line=dict(color='green', width=2)
                ))
                fig.update_layout(
                    title='投资者关系 - 交易额趋势',
                    xaxis_title='时间',
                    yaxis_title='交易额',
                    height=400
                )
                self.figures['investor_trading'] = fig
                self._save_figure(fig, 'investor_trading.html')
    
    def create_risk_reputation_charts(self):
        """创建风险与声誉图表"""
        df = self.cleaned_data['risk_reputation']
        
        # 查找相关列
        sentiment_cols = [col for col in df.columns if '情感' in col or 'sentiment' in col.lower()]
        risk_cols = [col for col in df.columns if '风险' in col or 'risk' in col.lower()]
        
        if sentiment_cols:
            sentiment_col = sentiment_cols[0]
            if sentiment_col in df.columns:
                # 情感分布
                if sentiment_col in df.columns and df[sentiment_col].dtype == 'object':
                    sentiment_counts = df[sentiment_col].value_counts()
                    fig = go.Figure(data=[go.Bar(
                        x=sentiment_counts.index,
                        y=sentiment_counts.values,
                        marker_color=['red' if '负面' in str(x) else 'green' if '正面' in str(x) else 'gray' 
                                     for x in sentiment_counts.index]
                    )])
                    fig.update_layout(
                        title='舆情情感分析',
                        xaxis_title='情感类型',
                        yaxis_title='数量',
                        height=400
                    )
                    self.figures['sentiment_analysis'] = fig
                    self._save_figure(fig, 'sentiment_analysis.html')
    
    def create_comparison_charts(self):
        """创建综合对比图"""
        # 创建各维度KPI对比
        categories = []
        values = []
        
        for category, kpis in self.kpi_results.items():
            # 计算每个类别的综合得分（简化）
            if kpis:
                avg_value = sum([v for v in kpis.values() if isinstance(v, (int, float))]) / len([v for v in kpis.values() if isinstance(v, (int, float))])
                categories.append(category)
                values.append(avg_value)
        
        if categories:
            fig = go.Figure(data=[go.Bar(
                x=categories,
                y=values,
                marker_color='steelblue'
            )])
            fig.update_layout(
                title='各维度KPI综合对比',
                xaxis_title='维度',
                yaxis_title='综合得分',
                height=400
            )
            self.figures['kpi_comparison'] = fig
            self._save_figure(fig, 'kpi_comparison.html')
    
    def _save_figure(self, fig, filename):
        """保存图表"""
        os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
        file_path = os.path.join(VISUALIZATIONS_DIR, filename)
        fig.write_html(file_path)
        logger.info(f"已保存图表: {file_path}")
    
    def create_dashboard_html(self):
        """创建综合仪表盘HTML"""
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>商业情报分析系统 - 仪表盘</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .dashboard { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
                .chart-container { border: 1px solid #ddd; padding: 10px; }
                h1 { text-align: center; }
            </style>
        </head>
        <body>
            <h1>商业情报分析系统 - 综合仪表盘</h1>
            <div class="dashboard">
        """
        
        for name, fig in self.figures.items():
            html_file = f"{name}.html"
            dashboard_html += f'<div class="chart-container"><iframe src="{html_file}" width="100%" height="500px"></iframe></div>\n'
        
        dashboard_html += """
            </div>
        </body>
        </html>
        """
        
        dashboard_path = os.path.join(VISUALIZATIONS_DIR, 'dashboard.html')
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        logger.info(f"已创建仪表盘: {dashboard_path}")


if __name__ == "__main__":
    from data_loader import DataLoader
    from data_cleaner import DataCleaner
    from data_analyzer import DataAnalyzer
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    analyzer = DataAnalyzer(cleaned_data, data_loader=None)
    kpis = analyzer.calculate_all_kpis()
    
    visualizer = Visualizer(cleaned_data, kpis)
    visualizer.create_all_visualizations()
    visualizer.create_dashboard_html()


