"""
上市公司商业情报系统 - Streamlit应用
提供全局筛选、动态对比和全量指标展示功能
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import warnings
import os
import sys
import ast
import time
from io import StringIO, BytesIO, BytesIO
import zipfile

# 忽略警告
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="上市公司商业情报系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏Streamlit默认的菜单和页脚
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 模拟数据生成函数
def generate_mock_data():
    """生成模拟数据"""
    companies = ['招商银行', '平安银行', '中国平安', '万科A', '比亚迪']
    
    # 生成日期序列
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    
    data = {}
    for company in companies:
        # 市值与财务数据
        market_cap_data = {
            '日期': dates,
            '日总市值(万元)': np.random.uniform(1000000, 5000000, len(dates)) + np.cumsum(np.random.randn(len(dates)) * 10000),
            '周市值上涨率(%)': np.random.uniform(-5, 10, len(dates)),
            '周相对估值水平': np.random.uniform(0.8, 1.5, len(dates)),
            '日股价涨幅(%)': np.random.uniform(-3, 5, len(dates)),
            '月超额收益(%)': np.random.uniform(-2, 8, len(dates)),
            '月股价波动率(%)': np.random.uniform(1, 5, len(dates)),
            '季度净资产回报率(ROE)(%)': np.random.uniform(8, 20, len(dates)),
            '季度投入资本回报率(ROIC)(%)': np.random.uniform(6, 18, len(dates)),
            '年度经济增加值(EVA)(万元)': np.random.uniform(50000, 200000, len(dates))
        }
        
        # 媒体曝光度数据
        media_data = {
            '日期': dates,
            '内容质量及媒体覆盖指标': np.random.uniform(60, 95, len(dates)),
            '核心信息量': np.random.uniform(50, 200, len(dates)),
            '转发量': np.random.uniform(100, 1000, len(dates)),
            '情感倾向得分': np.random.uniform(0.5, 0.9, len(dates))
        }
        
        # 社交媒体互动数据
        social_data = {
            '日期': dates,
            '公司话题总讨论量': np.random.uniform(500, 5000, len(dates)),
            '讨论热度指数': np.random.uniform(60, 95, len(dates)),
            '股吧人气排名': np.random.randint(1, 100, len(dates)),
            '粉丝结构活跃指数': np.random.uniform(50, 90, len(dates)),
            '用户活动关键议题数': np.random.uniform(10, 50, len(dates)),
            '高互动内容活动数': np.random.uniform(5, 30, len(dates)),
            '情感关注指数': np.random.uniform(0.6, 0.95, len(dates))
        }
        
        # 投资者关系数据
        investor_data = {
            '日期': dates,
            '投资者关注度': np.random.uniform(60, 95, len(dates)),
            '机构持股比例(%)': np.random.uniform(30, 70, len(dates)),
            '研报覆盖数量': np.random.randint(5, 50, len(dates))
        }
        
        # 风险与声誉数据
        risk_data = {
            '日期': dates,
            '风险评分': np.random.uniform(20, 80, len(dates)),
            '声誉指数': np.random.uniform(60, 95, len(dates)),
            '负面舆情数量': np.random.randint(0, 10, len(dates))
        }
        
        data[company] = {
            'market_cap': pd.DataFrame(market_cap_data),
            'media': pd.DataFrame(media_data),
            'social': pd.DataFrame(social_data),
            'investor': pd.DataFrame(investor_data),
            'risk': pd.DataFrame(risk_data)
        }
    
    return companies, data

# 初始化数据
@st.cache_data
def load_data():
    companies, data = generate_mock_data()
    return companies, data

# ==================== 页面展示函数 ====================

def show_comprehensive_evaluation(companies, data, single_mode=True):
    """综合评价页面"""
    st.header("综合评价")
    
    # 计算五个维度的分值
    dimensions = ['市值与财务', '媒体曝光度', '社交媒体互动', '投资者关系', '风险与声誉']
    
    if single_mode:
        company = companies[0]
        # 单选模式：显示具体数值
        df_market = data[company]['market_cap']
        df_media = data[company]['media']
        df_social = data[company]['social']
        df_investor = data[company]['investor']
        df_risk = data[company]['risk']
        
        # 计算各维度得分（0-100分）
        market_score = min(100, (df_market['日总市值(万元)'].iloc[-1] / 5000000) * 100)
        media_score = df_media['内容质量及媒体覆盖指标'].iloc[-1]
        social_score = df_social['讨论热度指数'].iloc[-1]
        investor_score = df_investor['投资者关注度'].iloc[-1]
        risk_score = df_risk['声誉指数'].iloc[-1]
        
        scores = [market_score, media_score, social_score, investor_score, risk_score]
        
        # 雷达图
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=dimensions,
            fill='toself',
            name=company,
            line_color='rgb(75, 192, 192)'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title=f"{company} - 五维度综合评价雷达图",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # KPI指标卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "总市值",
                f"{df_market['日总市值(万元)'].iloc[-1]:,.0f}万元",
                delta=f"{df_market['日总市值(万元)'].iloc[-1] - df_market['日总市值(万元)'].iloc[-2]:,.0f}万元"
            )
        with col2:
            st.metric(
                "日股价涨幅",
                f"{df_market['日股价涨幅(%)'].iloc[-1]:.2f}%",
                delta=f"{df_market['日股价涨幅(%)'].iloc[-1] - df_market['日股价涨幅(%)'].iloc[-2]:.2f}%"
            )
        with col3:
            total_score = np.mean(scores)
            st.metric(
                "综合评价总分",
                f"{total_score:.1f}分",
                delta=f"{scores[0] - scores[-1]:.1f}分" if len(scores) > 1 else None
            )
        with col4:
            sentiment_score = df_media['情感倾向得分'].iloc[-1]
            sentiment_status = "正面" if sentiment_score > 0.7 else "中性" if sentiment_score > 0.5 else "负面"
            st.metric(
                "情感波动预警",
                sentiment_status,
                delta=f"{sentiment_score:.2f}"
            )
        
    else:
        # 多选模式：重叠对比
        fig = go.Figure()
        colors = px.colors.qualitative.Set3[:len(companies)]
        
        for idx, company in enumerate(companies):
            df_market = data[company]['market_cap']
            df_media = data[company]['media']
            df_social = data[company]['social']
            df_investor = data[company]['investor']
            df_risk = data[company]['risk']
            
            market_score = min(100, (df_market['日总市值(万元)'].iloc[-1] / 5000000) * 100)
            media_score = df_media['内容质量及媒体覆盖指标'].iloc[-1]
            social_score = df_social['讨论热度指数'].iloc[-1]
            investor_score = df_investor['投资者关注度'].iloc[-1]
            risk_score = df_risk['声誉指数'].iloc[-1]
            
            scores = [market_score, media_score, social_score, investor_score, risk_score]
            
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=dimensions,
                fill='toself',
                name=company,
                line_color=colors[idx]
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="多公司对比 - 五维度综合评价雷达图",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 对比表格
        comparison_data = []
        for company in companies:
            df_market = data[company]['market_cap']
            df_media = data[company]['media']
            
            market_score = min(100, (df_market['日总市值(万元)'].iloc[-1] / 5000000) * 100)
            media_score = df_media['内容质量及媒体覆盖指标'].iloc[-1]
            social_score = data[company]['social']['讨论热度指数'].iloc[-1]
            investor_score = data[company]['investor']['投资者关注度'].iloc[-1]
            risk_score = data[company]['risk']['声誉指数'].iloc[-1]
            total_score = np.mean([market_score, media_score, social_score, investor_score, risk_score])
            
            comparison_data.append({
                '公司': company,
                '总市值(万元)': f"{df_market['日总市值(万元)'].iloc[-1]:,.0f}",
                '日股价涨幅(%)': f"{df_market['日股价涨幅(%)'].iloc[-1]:.2f}",
                '综合评价总分': f"{total_score:.1f}",
                '排名': 0  # 稍后计算
            })
        
        # 计算排名
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df['排名'] = comparison_df['综合评价总分'].str.replace('分', '').astype(float).rank(ascending=False, method='min').astype(int)
        comparison_df = comparison_df.sort_values('排名')
        
        st.subheader("对比分析表")
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

def show_market_cap_dashboard(companies, data, single_mode=True):
    """市值与财务表现指标看板"""
    st.header("市值与财务表现指标看板")
    
    indicators = [
        '日总市值', '周市值上涨', '周相对估值水平', '日股价涨幅', 
        '月超额收益', '月股价波动率', '季度净资产回报率(ROE)', 
        '季度投入资本回报率(ROIC)', '年度经济增加值(EVA)'
    ]
    
    if single_mode:
        company = companies[0]
        df = data[company]['market_cap']
        
        # 显示所有指标
        for indicator in indicators:
            st.subheader(indicator)
            
            if indicator == '日总市值':
                col_name = '日总市值(万元)'
            elif indicator == '周市值上涨':
                col_name = '周市值上涨率(%)'
            elif indicator == '周相对估值水平':
                col_name = '周相对估值水平'
            elif indicator == '日股价涨幅':
                col_name = '日股价涨幅(%)'
            elif indicator == '月超额收益':
                col_name = '月超额收益(%)'
            elif indicator == '月股价波动率':
                col_name = '月股价波动率(%)'
                st.warning("⚠️ 注意：月股价波动率为负向指标，数值越低越好")
            elif indicator == '季度净资产回报率(ROE)':
                col_name = '季度净资产回报率(ROE)(%)'
            elif indicator == '季度投入资本回报率(ROIC)':
                col_name = '季度投入资本回报率(ROIC)(%)'
            elif indicator == '年度经济增加值(EVA)':
                col_name = '年度经济增加值(EVA)(万元)'
            else:
                continue
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col_name],
                mode='lines',
                name=company,
                line=dict(color='rgb(75, 192, 192)', width=2)
            ))
            fig.update_layout(
                title=f"{company} - {indicator}历史走势",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示最新值和环比
            latest_value = df[col_name].iloc[-1]
            prev_value = df[col_name].iloc[-2] if len(df) > 1 else latest_value
            change = latest_value - prev_value
            change_pct = (change / prev_value * 100) if prev_value != 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("最新值", f"{latest_value:,.2f}")
            with col2:
                st.metric("环比变化", f"{change:,.2f}", delta=f"{change_pct:.2f}%")
            with col3:
                st.metric("平均值", f"{df[col_name].mean():,.2f}")
            
            st.markdown("---")
    
    else:
        # 多选模式：多线对比
        fig = go.Figure()
        colors = px.colors.qualitative.Set3[:len(companies)]
        
        for idx, company in enumerate(companies):
            df = data[company]['market_cap']
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df['日总市值(万元)'],
                mode='lines',
                name=company,
                line=dict(color=colors[idx], width=2)
            ))
        
        fig.update_layout(
            title="多公司对比 - 日总市值走势",
            xaxis_title="日期",
            yaxis_title="总市值(万元)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示所有指标的对比图表
        for indicator in indicators[1:]:  # 跳过日总市值（已显示）
            st.subheader(indicator)
            
            if indicator == '月股价波动率':
                st.warning("⚠️ 注意：月股价波动率为负向指标，数值越低越好")
            
            fig = go.Figure()
            for idx, company in enumerate(companies):
                df = data[company]['market_cap']
                
                if indicator == '周市值上涨':
                    col_name = '周市值上涨率(%)'
                elif indicator == '周相对估值水平':
                    col_name = '周相对估值水平'
                elif indicator == '日股价涨幅':
                    col_name = '日股价涨幅(%)'
                elif indicator == '月超额收益':
                    col_name = '月超额收益(%)'
                elif indicator == '月股价波动率':
                    col_name = '月股价波动率(%)'
                elif indicator == '季度净资产回报率(ROE)':
                    col_name = '季度净资产回报率(ROE)(%)'
                elif indicator == '季度投入资本回报率(ROIC)':
                    col_name = '季度投入资本回报率(ROIC)(%)'
                elif indicator == '年度经济增加值(EVA)':
                    col_name = '年度经济增加值(EVA)(万元)'
                else:
                    continue
                
                fig.add_trace(go.Scatter(
                    x=df['日期'],
                    y=df[col_name],
                    mode='lines',
                    name=company,
                    line=dict(color=colors[idx], width=2)
                ))
            
            fig.update_layout(
                title=f"多公司对比 - {indicator}",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")

def show_media_dashboard(companies, data, single_mode=True):
    """媒体曝光度指标看板"""
    st.header("媒体曝光度指标看板")
    
    indicators = [
        '内容质量及媒体覆盖指标', '核心信息量', '转发量', '情感相关'
    ]
    
    if single_mode:
        company = companies[0]
        df = data[company]['media']
        
        for indicator in indicators:
            st.subheader(indicator)
            
            if indicator == '内容质量及媒体覆盖指标':
                col_name = '内容质量及媒体覆盖指标'
            elif indicator == '核心信息量':
                col_name = '核心信息量'
            elif indicator == '转发量':
                col_name = '转发量'
            elif indicator == '情感相关':
                col_name = '情感倾向得分'
            else:
                continue
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col_name],
                mode='lines',
                name=company,
                line=dict(color='rgb(75, 192, 192)', width=2)
            ))
            fig.update_layout(
                title=f"{company} - {indicator}历史走势",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            latest_value = df[col_name].iloc[-1]
            prev_value = df[col_name].iloc[-2] if len(df) > 1 else latest_value
            change = latest_value - prev_value
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("最新值", f"{latest_value:,.2f}")
            with col2:
                st.metric("环比变化", f"{change:,.2f}")
            with col3:
                st.metric("平均值", f"{df[col_name].mean():,.2f}")
            
            st.markdown("---")
    
    else:
        # 多选模式
        for indicator in indicators:
            st.subheader(indicator)
            
            if indicator == '内容质量及媒体覆盖指标':
                col_name = '内容质量及媒体覆盖指标'
            elif indicator == '核心信息量':
                col_name = '核心信息量'
            elif indicator == '转发量':
                col_name = '转发量'
            elif indicator == '情感相关':
                col_name = '情感倾向得分'
            else:
                continue
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set3[:len(companies)]
            
            for idx, company in enumerate(companies):
                df = data[company]['media']
                fig.add_trace(go.Scatter(
                    x=df['日期'],
                    y=df[col_name],
                    mode='lines',
                    name=company,
                    line=dict(color=colors[idx], width=2)
                ))
            
            fig.update_layout(
                title=f"多公司对比 - {indicator}",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")

def show_social_dashboard(companies, data, single_mode=True):
    """社交媒体互动指标看板"""
    st.header("社交媒体互动指标看板")
    
    indicators = [
        '公司话题总讨论量', '讨论热度指数', '股吧人气排名', 
        '粉丝结构活跃指数', '用户活动关键议题', '高互动内容活动', '情感关注指数'
    ]
    
    if single_mode:
        company = companies[0]
        df = data[company]['social']
        
        for indicator in indicators:
            st.subheader(indicator)
            
            col_name_map = {
                '公司话题总讨论量': '公司话题总讨论量',
                '讨论热度指数': '讨论热度指数',
                '股吧人气排名': '股吧人气排名',
                '粉丝结构活跃指数': '粉丝结构活跃指数',
                '用户活动关键议题': '用户活动关键议题数',
                '高互动内容活动': '高互动内容活动数',
                '情感关注指数': '情感关注指数'
            }
            
            col_name = col_name_map.get(indicator)
            if not col_name:
                continue
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col_name],
                mode='lines',
                name=company,
                line=dict(color='rgb(75, 192, 192)', width=2)
            ))
            fig.update_layout(
                title=f"{company} - {indicator}历史走势",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            latest_value = df[col_name].iloc[-1]
            prev_value = df[col_name].iloc[-2] if len(df) > 1 else latest_value
            change = latest_value - prev_value
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("最新值", f"{latest_value:,.2f}")
            with col2:
                st.metric("环比变化", f"{change:,.2f}")
            with col3:
                st.metric("平均值", f"{df[col_name].mean():,.2f}")
            
            st.markdown("---")
    
    else:
        # 多选模式
        for indicator in indicators:
            st.subheader(indicator)
            
            col_name_map = {
                '公司话题总讨论量': '公司话题总讨论量',
                '讨论热度指数': '讨论热度指数',
                '股吧人气排名': '股吧人气排名',
                '粉丝结构活跃指数': '粉丝结构活跃指数',
                '用户活动关键议题': '用户活动关键议题数',
                '高互动内容活动': '高互动内容活动数',
                '情感关注指数': '情感关注指数'
            }
            
            col_name = col_name_map.get(indicator)
            if not col_name:
                continue
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set3[:len(companies)]
            
            for idx, company in enumerate(companies):
                df = data[company]['social']
                fig.add_trace(go.Scatter(
                    x=df['日期'],
                    y=df[col_name],
                    mode='lines',
                    name=company,
                    line=dict(color=colors[idx], width=2)
                ))
            
            fig.update_layout(
                title=f"多公司对比 - {indicator}",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")

def show_investor_dashboard(companies, data, single_mode=True):
    """投资者关系指标看板"""
    st.header("投资者关系指标看板")
    
    if single_mode:
        company = companies[0]
        df = data[company]['investor']
        
        indicators = ['投资者关注度', '机构持股比例', '研报覆盖数量']
        col_names = ['投资者关注度', '机构持股比例(%)', '研报覆盖数量']
        
        for indicator, col_name in zip(indicators, col_names):
            st.subheader(indicator)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col_name],
                mode='lines',
                name=company,
                line=dict(color='rgb(75, 192, 192)', width=2)
            ))
            fig.update_layout(
                title=f"{company} - {indicator}历史走势",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            latest_value = df[col_name].iloc[-1]
            prev_value = df[col_name].iloc[-2] if len(df) > 1 else latest_value
            change = latest_value - prev_value
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("最新值", f"{latest_value:,.2f}")
            with col2:
                st.metric("环比变化", f"{change:,.2f}")
            with col3:
                st.metric("平均值", f"{df[col_name].mean():,.2f}")
            
            st.markdown("---")
    
    else:
        # 多选模式
        indicators = ['投资者关注度', '机构持股比例', '研报覆盖数量']
        col_names = ['投资者关注度', '机构持股比例(%)', '研报覆盖数量']
        
        for indicator, col_name in zip(indicators, col_names):
            st.subheader(indicator)
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set3[:len(companies)]
            
            for idx, company in enumerate(companies):
                df = data[company]['investor']
                fig.add_trace(go.Scatter(
                    x=df['日期'],
                    y=df[col_name],
                    mode='lines',
                    name=company,
                    line=dict(color=colors[idx], width=2)
                ))
            
            fig.update_layout(
                title=f"多公司对比 - {indicator}",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")

def show_risk_dashboard(companies, data, single_mode=True):
    """风险与声誉管控指标看板"""
    st.header("风险与声誉管控指标看板")
    
    if single_mode:
        company = companies[0]
        df = data[company]['risk']
        
        indicators = ['风险评分', '声誉指数', '负面舆情数量']
        col_names = ['风险评分', '声誉指数', '负面舆情数量']
        
        for indicator, col_name in zip(indicators, col_names):
            st.subheader(indicator)
            
            if indicator == '风险评分':
                st.warning("⚠️ 注意：风险评分为负向指标，数值越低越好")
            elif indicator == '负面舆情数量':
                st.warning("⚠️ 注意：负面舆情数量为负向指标，数值越低越好")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col_name],
                mode='lines',
                name=company,
                line=dict(color='rgb(75, 192, 192)', width=2)
            ))
            fig.update_layout(
                title=f"{company} - {indicator}历史走势",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            latest_value = df[col_name].iloc[-1]
            prev_value = df[col_name].iloc[-2] if len(df) > 1 else latest_value
            change = latest_value - prev_value
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("最新值", f"{latest_value:,.2f}")
            with col2:
                st.metric("环比变化", f"{change:,.2f}")
            with col3:
                st.metric("平均值", f"{df[col_name].mean():,.2f}")
            
            st.markdown("---")
    
    else:
        # 多选模式
        indicators = ['风险评分', '声誉指数', '负面舆情数量']
        col_names = ['风险评分', '声誉指数', '负面舆情数量']
        
        for indicator, col_name in zip(indicators, col_names):
            st.subheader(indicator)
            
            if indicator == '风险评分':
                st.warning("⚠️ 注意：风险评分为负向指标，数值越低越好")
            elif indicator == '负面舆情数量':
                st.warning("⚠️ 注意：负面舆情数量为负向指标，数值越低越好")
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set3[:len(companies)]
            
            for idx, company in enumerate(companies):
                df = data[company]['risk']
                fig.add_trace(go.Scatter(
                    x=df['日期'],
                    y=df[col_name],
                    mode='lines',
                    name=company,
                    line=dict(color=colors[idx], width=2)
                ))
            
            fig.update_layout(
                title=f"多公司对比 - {indicator}",
                xaxis_title="日期",
                yaxis_title=indicator,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")

def show_export_report_dialog(companies, data):
    """导出报告对话框"""
    st.markdown("---")
    
    # 对话框标题
    col1, col2 = st.columns([10, 1])
    with col1:
        st.subheader("📥 导出报告")
    with col2:
        if st.button("✕", type="secondary", use_container_width=True):
            st.session_state.show_export_dialog = False
            st.rerun()
    
    st.info(f"💡 将为以下公司生成报告：{', '.join(companies)}")
    
    # 报告类型选择
    report_type = st.selectbox(
        "选择报告类型",
        ["日报", "周报", "季报", "年报", "Excel数据报告"],
        help="选择要生成的报告类型"
    )
    
    # 报告内容选项
    st.subheader("报告内容选项")
    include_charts = st.checkbox("包含图表", value=True)
    include_data_tables = st.checkbox("包含数据表格", value=True)
    include_comparison = st.checkbox("包含对比分析", value=len(companies) > 1)
    
    # 生成报告按钮
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("🚀 生成报告", type="primary", use_container_width=True):
            generate_and_download_report(
                companies, 
                data, 
                report_type,
                include_charts,
                include_data_tables,
                include_comparison
            )
    with col2:
        if st.button("取消", use_container_width=True):
            st.session_state.show_export_dialog = False
            st.rerun()

def generate_and_download_report(companies, data, report_type, include_charts, include_data_tables, include_comparison):
    """生成并下载报告"""
    try:
        # 显示生成进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📊 正在准备报告数据...")
        progress_bar.progress(10)
        time.sleep(0.3)
        
        # 准备报告数据
        report_data = prepare_report_data(companies, data, include_comparison)
        
        status_text.text("📝 正在生成报告...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        # 根据报告类型生成报告
        if report_type == "Excel数据报告":
            # 生成Excel报告
            report_file = generate_excel_report_streamlit(
                companies, 
                report_data, 
                include_data_tables
            )
            file_extension = "xlsx"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            # 生成PDF报告
            report_file = generate_pdf_report_streamlit(
                companies,
                report_data,
                report_type,
                include_charts,
                include_data_tables,
                include_comparison
            )
            file_extension = "pdf"
            mime_type = "application/pdf"
        
        status_text.text("✅ 报告生成完成！")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # 生成文件名
        report_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_names = "_".join(companies[:2])  # 最多显示2个公司名
        if len(companies) > 2:
            company_names += f"_等{len(companies)}家"
        filename = f"{report_type}_{company_names}_{report_date}.{file_extension}"
        
        # 提供下载
        st.download_button(
            label=f"📥 下载{report_type}",
            data=report_file,
            file_name=filename,
            mime_type=mime_type,
            use_container_width=True,
            type="primary"
        )
        
        st.success(f"✅ {report_type}生成成功！")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ 报告生成失败: {str(e)}")
        st.exception(e)

def prepare_report_data(companies, data, include_comparison):
    """准备报告数据"""
    report_data = {
        'companies': companies,
        'summary': {},
        'kpis': {},
        'comparison': None
    }
    
    # 计算各公司的KPI
    for company in companies:
        company_data = data[company]
        
        # 市值与财务
        market_cap = company_data['market_cap']
        latest_market_cap = market_cap['日总市值(万元)'].iloc[-1]
        market_cap_growth = ((market_cap['日总市值(万元)'].iloc[-1] - market_cap['日总市值(万元)'].iloc[0]) / market_cap['日总市值(万元)'].iloc[0] * 100) if len(market_cap) > 1 else 0
        
        # 媒体曝光度
        media = company_data['media']
        media_score = media['内容质量及媒体覆盖指标'].iloc[-1]
        total_shares = media['转发量'].sum()
        
        # 社交媒体
        social = company_data['social']
        social_score = social['讨论热度指数'].iloc[-1]
        total_discussions = social['公司话题总讨论量'].sum()
        
        # 投资者关系
        investor = company_data['investor']
        investor_score = investor['投资者关注度'].iloc[-1]
        
        # 风险与声誉
        risk = company_data['risk']
        risk_score = risk['声誉指数'].iloc[-1]
        
        report_data['kpis'][company] = {
            'market_cap': latest_market_cap,
            'market_cap_growth': market_cap_growth,
            'media_score': media_score,
            'total_shares': total_shares,
            'social_score': social_score,
            'total_discussions': total_discussions,
            'investor_score': investor_score,
            'risk_score': risk_score,
            'comprehensive_score': np.mean([media_score, social_score, investor_score, risk_score])
        }
    
    # 对比分析
    if include_comparison and len(companies) > 1:
        comparison_data = []
        for company in companies:
            kpis = report_data['kpis'][company]
            comparison_data.append({
                '公司': company,
                '总市值(万元)': f"{kpis['market_cap']:,.0f}",
                '市值增长率(%)': f"{kpis['market_cap_growth']:.2f}",
                '媒体得分': f"{kpis['media_score']:.1f}",
                '社交得分': f"{kpis['social_score']:.1f}",
                '投资者得分': f"{kpis['investor_score']:.1f}",
                '声誉得分': f"{kpis['risk_score']:.1f}",
                '综合得分': f"{kpis['comprehensive_score']:.1f}"
            })
        report_data['comparison'] = pd.DataFrame(comparison_data)
    
    return report_data

def generate_excel_report_streamlit(companies, report_data, include_data_tables):
    """生成Excel报告（Streamlit版本）"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # KPI汇总表
        kpi_summary = []
        for company in companies:
            kpis = report_data['kpis'][company]
            kpi_summary.append({
                '公司': company,
                '总市值(万元)': kpis['market_cap'],
                '市值增长率(%)': kpis['market_cap_growth'],
                '媒体曝光度得分': kpis['media_score'],
                '社交媒体得分': kpis['social_score'],
                '投资者关系得分': kpis['investor_score'],
                '风险声誉得分': kpis['risk_score'],
                '综合得分': kpis['comprehensive_score']
            })
        
        kpi_df = pd.DataFrame(kpi_summary)
        kpi_df.to_excel(writer, sheet_name='KPI汇总', index=False)
        
        # 对比分析表
        if report_data['comparison'] is not None:
            report_data['comparison'].to_excel(writer, sheet_name='对比分析', index=False)
        
        # 详细数据表（如果包含）
        if include_data_tables and len(companies) == 1:
            company = companies[0]
            # 这里可以添加详细数据表
            # 由于是模拟数据，暂时跳过
    
    output.seek(0)
    return output.getvalue()

def generate_pdf_report_streamlit(companies, report_data, report_type, include_charts, include_data_tables, include_comparison):
    """生成PDF报告（Streamlit版本）"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
    except ImportError:
        # 如果reportlab未安装，生成一个简单的文本报告
        return generate_text_report(companies, report_data, report_type)
    
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    
    # 标题
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, f"商业情报分析系统 - {report_type}")
    
    # 报告日期
    c.setFont("Helvetica", 12)
    report_date = datetime.now().strftime('%Y年%m月%d日')
    c.drawString(50, height - 80, f"报告日期: {report_date}")
    
    # 公司信息
    y_pos = height - 120
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "分析公司:")
    c.setFont("Helvetica", 12)
    y_pos -= 25
    for company in companies:
        c.drawString(70, y_pos, f"• {company}")
        y_pos -= 20
    
    # KPI汇总
    y_pos -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "关键指标汇总:")
    y_pos -= 25
    
    for company in companies:
        if y_pos < 100:
            c.showPage()
            y_pos = height - 50
        
        kpis = report_data['kpis'][company]
        c.setFont("Helvetica-Bold", 12)
        c.drawString(70, y_pos, company)
        y_pos -= 20
        
        c.setFont("Helvetica", 10)
        c.drawString(90, y_pos, f"总市值: {kpis['market_cap']:,.0f}万元")
        y_pos -= 15
        c.drawString(90, y_pos, f"市值增长率: {kpis['market_cap_growth']:.2f}%")
        y_pos -= 15
        c.drawString(90, y_pos, f"媒体曝光度得分: {kpis['media_score']:.1f}")
        y_pos -= 15
        c.drawString(90, y_pos, f"社交媒体得分: {kpis['social_score']:.1f}")
        y_pos -= 15
        c.drawString(90, y_pos, f"投资者关系得分: {kpis['investor_score']:.1f}")
        y_pos -= 15
        c.drawString(90, y_pos, f"风险声誉得分: {kpis['risk_score']:.1f}")
        y_pos -= 15
        c.drawString(90, y_pos, f"综合得分: {kpis['comprehensive_score']:.1f}")
        y_pos -= 25
    
    # 对比分析（如果有多家公司）
    if include_comparison and report_data['comparison'] is not None:
        if y_pos < 150:
            c.showPage()
            y_pos = height - 50
        
        y_pos -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, "对比分析:")
        y_pos -= 25
        
        comparison_df = report_data['comparison']
        c.setFont("Helvetica", 10)
        for idx, row in comparison_df.iterrows():
            if y_pos < 100:
                c.showPage()
                y_pos = height - 50
            c.drawString(70, y_pos, f"{row['公司']}: 综合得分 {row['综合得分']}")
            y_pos -= 15
    
    # 报告说明
    if y_pos < 100:
        c.showPage()
        y_pos = height - 50
    
    y_pos -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "报告说明:")
    y_pos -= 20
    c.setFont("Helvetica", 9)
    c.drawString(50, y_pos, "本报告基于当前选择的数据生成，包含关键指标汇总和分析。")
    y_pos -= 15
    c.drawString(50, y_pos, "详细数据请参考Excel数据报告。")
    
    c.save()
    output.seek(0)
    return output.getvalue()

def generate_text_report(companies, report_data, report_type):
    """生成文本格式报告（当PDF库不可用时）"""
    report_text = f"""
商业情报分析系统 - {report_type}
报告日期: {datetime.now().strftime('%Y年%m月%d日')}

分析公司: {', '.join(companies)}

关键指标汇总:
"""
    for company in companies:
        kpis = report_data['kpis'][company]
        report_text += f"""
{company}:
  总市值: {kpis['market_cap']:,.0f}万元
  市值增长率: {kpis['market_cap_growth']:.2f}%
  媒体曝光度得分: {kpis['media_score']:.1f}
  社交媒体得分: {kpis['social_score']:.1f}
  投资者关系得分: {kpis['investor_score']:.1f}
  风险声誉得分: {kpis['risk_score']:.1f}
  综合得分: {kpis['comprehensive_score']:.1f}
"""
    
    if report_data['comparison'] is not None:
        report_text += "\n对比分析:\n"
        report_text += report_data['comparison'].to_string(index=False)
    
    return report_text.encode('utf-8')

def show_data_sync_page():
    """数据更新/同步页面"""
    # 添加返回按钮
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("← 返回", type="secondary", use_container_width=True):
            st.session_state.show_data_sync = False
            st.rerun()
    
    st.header("🔄 数据更新/同步")
    
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 导入config模块
    import config
    
    # 读取当前配置
    target_urls = config.TARGET_URLS.copy()
    
    st.info('💡 提示：您可以修改下方URL配置，然后点击"更新配置并开始爬取"按钮来更新数据源。')
    st.markdown("---")
    
    # 显示格式化的TARGET_URLS
    st.subheader("📋 当前爬虫目标URL配置")
    
    # 使用expander来组织显示
    edited_urls = {}
    
    for file_name, sheets in target_urls.items():
        with st.expander(f"📄 {file_name}", expanded=False):
            edited_sheets = {}
            
            for sheet_name, url in sheets.items():
                new_url = st.text_input(
                    f"{sheet_name}",
                    value=url,
                    key=f"{file_name}_{sheet_name}",
                    help=f"修改 {sheet_name} 的数据源URL"
                )
                edited_sheets[sheet_name] = new_url
            
            edited_urls[file_name] = edited_sheets
    
    st.markdown("---")
    
    # 更新配置和开始爬取按钮
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 仅更新配置", use_container_width=True, type="secondary"):
            update_config_file(edited_urls)
            st.success("✅ 配置已更新！")
    
    with col2:
        if st.button("🚀 更新配置并开始爬取", use_container_width=True, type="primary"):
            # 更新配置
            update_config_file(edited_urls)
            
            # 显示爬取进度
            progress_container = st.container()
            status_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # 执行爬取
            try:
                run_scraper_with_progress(progress_bar, status_text, edited_urls)
                
                # 显示成功消息
                st.success("✅ 数据更新完成！")
                
                # 添加庆祝动画
                st.balloons()
                time.sleep(0.3)
                st.snow()
                
            except Exception as e:
                st.error(f"❌ 数据更新失败: {str(e)}")
                st.exception(e)

def update_config_file(new_urls):
    """更新config.py文件中的TARGET_URLS"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    
    # 读取config.py文件
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 构建新的TARGET_URLS字典字符串
    new_config_str = "TARGET_URLS = {\n"
    for file_name, sheets in new_urls.items():
        new_config_str += f"    '{file_name}': {{\n"
        for sheet_name, url in sheets.items():
            new_config_str += f"        '{sheet_name}': '{url}',\n"
        new_config_str += "    },\n"
    new_config_str += "}\n"
    
    # 找到TARGET_URLS的开始和结束位置
    start_marker = "# Target Urls"
    end_marker = "# Excel文件路径"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        # 替换TARGET_URLS部分
        new_content = (
            content[:start_idx + len(start_marker)] + 
            "\n" + new_config_str + 
            "\n" + content[end_idx:]
        )
        
        # 写回文件
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        raise ValueError("无法找到TARGET_URLS配置位置")

def run_scraper_with_progress(progress_bar, status_text, target_urls):
    """执行爬虫并显示进度"""
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 导入爬虫模块
    from src.data_scraper import DataScraper
    import config
    
    # 创建爬虫实例
    scraper = DataScraper(target_urls=target_urls, base_save_dir=config.DATA_DIR)
    
    # 计算总任务数
    total_tasks = sum(len(sheets) for sheets in target_urls.values())
    completed_tasks = 0
    
    # 遍历所有文件
    for file_idx, (file_name, sheets) in enumerate(target_urls.items()):
        status_text.text(f"📄 正在处理: {file_name} ({file_idx + 1}/{len(target_urls)})")
        
        # 为每个文件创建Excel写入器
        save_path = os.path.join(config.DATA_DIR, file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                # 遍历每个sheet
                for sheet_idx, (sheet_name, url) in enumerate(sheets.items()):
                    status_text.text(f"  ├── 正在爬取: {sheet_name} ({sheet_idx + 1}/{len(sheets)})")
                    
                    # 爬取数据
                    data = scraper.scrape_table_data(url)
                    
                    if data:
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        status_text.text(f"  └── ✅ {sheet_name}: 成功抓取 {len(data)} 条数据")
                    else:
                        df = pd.DataFrame()
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        status_text.text(f"  └── ⚠️ {sheet_name}: 未抓取到数据，已创建空表")
                    
                    # 更新进度
                    completed_tasks += 1
                    progress = completed_tasks / total_tasks
                    progress_bar.progress(progress)
                    time.sleep(0.1)  # 短暂延迟以显示动画效果
            
            status_text.text(f"✅ {file_name} 处理完成")
            time.sleep(0.2)
            
        except Exception as e:
            status_text.text(f"❌ {file_name} 处理失败: {str(e)}")
            raise
    
        status_text.text("🎉 所有数据爬取任务已完成！")
        time.sleep(0.5)  # 短暂延迟以显示完成状态

companies, company_data = load_data()

# 初始化session_state
if 'show_data_sync' not in st.session_state:
    st.session_state.show_data_sync = False
if 'show_export_dialog' not in st.session_state:
    st.session_state.show_export_dialog = False

# 侧边栏
with st.sidebar:
    st.title("📊 商业情报系统")
    st.markdown("---")
    
    # 全局筛选
    st.subheader("全局筛选")
    selected_companies = st.multiselect(
        "请选择上市公司",
        options=companies,
        default=[],
        help="可选择1-5家公司进行对比分析"
    )
    
    st.markdown("---")
    
    # 导航菜单
    st.subheader("章节导航")
    page = st.radio(
        "选择章节",
        [
            "综合评价",
            "市值与财务表现指标看板",
            "媒体曝光度指标看板",
            "社交媒体互动指标看板",
            "投资者关系指标看板",
            "风险与声誉管控指标看板"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 数据更新/同步模块（与全局筛选和章节导航同级）
    st.subheader("数据更新/同步")
    if st.button("🔄 数据更新/同步", use_container_width=True, type="primary"):
        st.session_state.show_data_sync = True
        st.rerun()

# 数据更新/同步页面（独立显示，不受公司选择影响）
if st.session_state.get('show_data_sync', False):
    show_data_sync_page()
else:
    # 正常显示主界面
    # 导出报告按钮（右上角）- 仅在选择了公司时显示
    if len(selected_companies) > 0:
        col1, col2 = st.columns([10, 1])
        with col2:
            if st.button("📥 导出报告", use_container_width=True, type="primary"):
                st.session_state.show_export_dialog = True
        
        # 导出报告对话框
        if st.session_state.get('show_export_dialog', False):
            show_export_report_dialog(selected_companies, company_data)
    
    # 主界面逻辑
    if len(selected_companies) == 0:
        # 未选择公司
        st.title("欢迎使用上市公司商业情报系统")
        st.info("👈 请在左侧选择公司以开始分析")
        st.markdown("""
        ### 系统功能说明
        
        - **单选模式**：选择1家公司时，系统进入"深度诊断模式"，显示该公司的详细趋势分析
        - **多选模式**：选择2-5家公司时，系统进入"横向对比模式"，所有图表显示多条曲线或分区对比
        
        ### 支持的指标维度
        
        1. **市值与财务表现**：总市值、市值增长率、估值水平、股价表现等
        2. **媒体曝光度**：内容质量、核心信息量、转发量、情感分析等
        3. **社交媒体互动**：讨论量、热度指数、人气排名、活跃度等
        4. **投资者关系**：关注度、持股比例、研报覆盖等
        5. **风险与声誉**：风险评分、声誉指数、负面舆情等
        """)
    
    elif len(selected_companies) == 1:
        # 深度诊断模式
        company = selected_companies[0]
        st.title(f"📈 {company} - 深度诊断模式")
        
        if page == "综合评价":
            show_comprehensive_evaluation([company], company_data, single_mode=True)
        elif page == "市值与财务表现指标看板":
            show_market_cap_dashboard([company], company_data, single_mode=True)
        elif page == "媒体曝光度指标看板":
            show_media_dashboard([company], company_data, single_mode=True)
        elif page == "社交媒体互动指标看板":
            show_social_dashboard([company], company_data, single_mode=True)
        elif page == "投资者关系指标看板":
            show_investor_dashboard([company], company_data, single_mode=True)
        elif page == "风险与声誉管控指标看板":
            show_risk_dashboard([company], company_data, single_mode=True)
    
    else:
        # 横向对比模式
        st.title(f"🔍 横向对比模式 - {len(selected_companies)}家公司")
        
        if page == "综合评价":
            show_comprehensive_evaluation(selected_companies, company_data, single_mode=False)
        elif page == "市值与财务表现指标看板":
            show_market_cap_dashboard(selected_companies, company_data, single_mode=False)
        elif page == "媒体曝光度指标看板":
            show_media_dashboard(selected_companies, company_data, single_mode=False)
        elif page == "社交媒体互动指标看板":
            show_social_dashboard(selected_companies, company_data, single_mode=False)
        elif page == "投资者关系指标看板":
            show_investor_dashboard(selected_companies, company_data, single_mode=False)
        elif page == "风险与声誉管控指标看板":
            show_risk_dashboard(selected_companies, company_data, single_mode=False)
