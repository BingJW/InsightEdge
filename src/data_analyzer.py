"""
数据分析与计算模块
基于指标体系计算各项KPI指标
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self, cleaned_data, data_loader=None, data_cleaner=None):
        self.cleaned_data = cleaned_data
        self.data_loader = data_loader  # 保存数据加载器引用，用于访问多工作表数据
        self.data_cleaner = data_cleaner  # 保存数据清洗器引用，用于访问清理后的多工作表数据
        self.kpi_results = {}
        self.trend_analysis = {}
    
    def calculate_all_kpis(self):
        """计算所有KPI指标"""
        logger.info("开始计算KPI指标...")
        
        # 1. 市值与财务表现指标
        if 'market_cap' in self.cleaned_data and self.cleaned_data['market_cap'] is not None:
            self.kpi_results['market_cap'] = self._calculate_market_cap_kpis()
        
        # 2. 媒体曝光度指标
        if 'media_exposure' in self.cleaned_data and self.cleaned_data['media_exposure'] is not None:
            self.kpi_results['media_exposure'] = self._calculate_media_exposure_kpis()
        
        # 3. 社交媒体互动指标
        if 'social_media' in self.cleaned_data and self.cleaned_data['social_media'] is not None:
            self.kpi_results['social_media'] = self._calculate_social_media_kpis()
        
        # 4. 投资者关系指标
        if 'investor_relations' in self.cleaned_data and self.cleaned_data['investor_relations'] is not None:
            self.kpi_results['investor_relations'] = self._calculate_investor_relations_kpis()
        
        # 5. 风险与声誉管控指标
        if 'risk_reputation' in self.cleaned_data and self.cleaned_data['risk_reputation'] is not None:
            self.kpi_results['risk_reputation'] = self._calculate_risk_reputation_kpis()
        
        # 6. 趋势分析
        self._calculate_trends()
        
        logger.info("KPI计算完成")
        return self.kpi_results
    
    def _calculate_market_cap_kpis(self):
        """
        计算市值与财务表现指标
        
        主要指标：
        - market_cap_growth_rate: 市值增长率 = (期末市值 - 期初市值) / 期初市值 × 100%
        """
        df = self.cleaned_data['market_cap']
        kpis = {}
        
        # 查找市值相关列
        market_cap_cols = [col for col in df.columns if '市值' in col or 'market_cap' in col.lower()]
        price_cols = [col for col in df.columns if '股价' in col or 'price' in col.lower()]
        revenue_cols = [col for col in df.columns if '收入' in col or 'revenue' in col.lower()]
        profit_cols = [col for col in df.columns if '利润' in col or 'profit' in col.lower()]
        
        if market_cap_cols:
            market_cap_col = market_cap_cols[0]
            # 总市值
            kpis['total_market_cap'] = df[market_cap_col].sum() if df[market_cap_col].dtype in ['int64', 'float64'] else 0
            
            # 市值增长率 - 按时间排序计算期初和期末值
            if len(df) > 1 and market_cap_col in df.columns:
                # 查找日期列 - 扩展匹配模式
                date_cols = [col for col in df.columns if any(keyword in str(col).lower() for keyword in [
                    'date', '时间', '日期', '交易日期', '交易时间', 'time'
                ])]
                
                if date_cols:
                    # 按时间排序
                    try:
                        date_col = date_cols[0]
                        # 处理不同格式的日期
                        if df[date_col].dtype == 'int64':
                            # YYYYMMDD格式：20251031
                            df['_date'] = pd.to_datetime(df[date_col].astype(str), format='%Y%m%d', errors='coerce')
                        elif df[date_col].dtype == 'object':
                            # 尝试解析字符串日期
                            df['_date'] = pd.to_datetime(df[date_col], errors='coerce')
                        else:
                            # datetime格式
                            df['_date'] = pd.to_datetime(df[date_col], errors='coerce')
                        
                        df_valid = df[df['_date'].notna()].copy()
                        if len(df_valid) > 1:
                            df_sorted = df_valid.sort_values('_date')
                            initial_cap = df_sorted[market_cap_col].iloc[0]
                            final_cap = df_sorted[market_cap_col].iloc[-1]
                            if pd.notna(initial_cap) and pd.notna(final_cap) and initial_cap > 0:
                                # 市值增长率 = (期末市值 - 期初市值) / 期初市值 × 100%
                                kpis['market_cap_growth_rate'] = (final_cap - initial_cap) / initial_cap * 100
                                logger.info(f"市值增长率计算: 期初={initial_cap:.2f}, 期末={final_cap:.2f}, 增长率={kpis['market_cap_growth_rate']:.2f}%")
                    except Exception as e:
                        logger.warning(f"日期解析失败: {str(e)}")
                        # 如果日期解析失败，使用索引顺序
                        if df[market_cap_col].dtype in ['int64', 'float64']:
                            initial_cap = df[market_cap_col].iloc[0]
                            final_cap = df[market_cap_col].iloc[-1]
                            if pd.notna(initial_cap) and pd.notna(final_cap) and initial_cap > 0:
                                kpis['market_cap_growth_rate'] = (final_cap - initial_cap) / initial_cap * 100
                                logger.info(f"使用索引顺序计算市值增长率: {kpis['market_cap_growth_rate']:.2f}%")
                else:
                    # 没有日期列，使用索引顺序
                    if df[market_cap_col].dtype in ['int64', 'float64']:
                        initial_cap = df[market_cap_col].iloc[0]
                        final_cap = df[market_cap_col].iloc[-1]
                        if pd.notna(initial_cap) and pd.notna(final_cap) and initial_cap > 0:
                            kpis['market_cap_growth_rate'] = (final_cap - initial_cap) / initial_cap * 100
        
        if price_cols:
            price_col = price_cols[0]
            # 股价涨幅 - 按时间排序计算期初和期末值
            if len(df) > 1 and price_col in df.columns:
                # 查找日期列
                date_cols = [col for col in df.columns if 'date' in col.lower() or '时间' in col or '日期' in col]
                
                if date_cols:
                    try:
                        date_col = date_cols[0]
                        df['_date'] = pd.to_datetime(df[date_col], errors='coerce')
                        df_valid = df[df['_date'].notna()].copy()
                        if len(df_valid) > 1:
                            df_sorted = df_valid.sort_values('_date')
                            initial_price = df_sorted[price_col].iloc[0]
                            final_price = df_sorted[price_col].iloc[-1]
                            if pd.notna(initial_price) and pd.notna(final_price) and initial_price > 0:
                                kpis['price_increase_rate'] = (final_price - initial_price) / initial_price * 100
                    except:
                        # 如果日期解析失败，使用索引顺序
                        if df[price_col].dtype in ['int64', 'float64']:
                            initial_price = df[price_col].iloc[0]
                            final_price = df[price_col].iloc[-1]
                            if pd.notna(initial_price) and pd.notna(final_price) and initial_price > 0:
                                kpis['price_increase_rate'] = (final_price - initial_price) / initial_price * 100
                else:
                    # 没有日期列，使用索引顺序
                    if df[price_col].dtype in ['int64', 'float64']:
                        initial_price = df[price_col].iloc[0]
                        final_price = df[price_col].iloc[-1]
                        if pd.notna(initial_price) and pd.notna(final_price) and initial_price > 0:
                            kpis['price_increase_rate'] = (final_price - initial_price) / initial_price * 100
            
            # 股价波动率
            if price_col in df.columns and df[price_col].dtype in ['int64', 'float64']:
                kpis['price_volatility'] = df[price_col].std() / df[price_col].mean() * 100 if df[price_col].mean() > 0 else 0
        
        if revenue_cols:
            revenue_col = revenue_cols[0]
            if revenue_col in df.columns and df[revenue_col].dtype in ['int64', 'float64']:
                kpis['total_revenue'] = df[revenue_col].sum()
                kpis['avg_revenue'] = df[revenue_col].mean()
        
        if profit_cols:
            profit_col = profit_cols[0]
            if profit_col in df.columns and df[profit_col].dtype in ['int64', 'float64']:
                kpis['total_profit'] = df[profit_col].sum()
                kpis['avg_profit'] = df[profit_col].mean()
                # ROE (简化计算)
                if revenue_cols and revenue_cols[0] in df.columns:
                    revenue_col = revenue_cols[0]
                    if df[revenue_col].sum() > 0:
                        kpis['roe'] = df[profit_col].sum() / df[revenue_col].sum() * 100
        
        return kpis
    
    def _calculate_media_exposure_kpis(self):
        """
        计算媒体曝光度指标
        
        主要指标：
        - total_articles: 总发稿量 = 数据表中的文章/发稿记录总数
        """
        df = self.cleaned_data['media_exposure']
        kpis = {}
        
        # 查找相关列
        article_cols = [col for col in df.columns if '发稿' in col or '文章' in col or 'article' in col.lower()]
        read_cols = [col for col in df.columns if '阅读' in col or 'read' in col.lower() or 'pv' in col.lower()]
        view_cols = [col for col in df.columns if '浏览' in col or 'view' in col.lower() or 'uv' in col.lower()]
        media_cols = [col for col in df.columns if '媒体' in col or 'media' in col.lower()]
        
        # 总发稿量 - 优先使用"转发量"工作表的数据
        # 如果没有找到"发稿"列，则使用数据行数作为总发稿量
        forwarding_df = None
        # 优先使用清理后的工作表数据
        if self.data_cleaner:
            forwarding_df = self.data_cleaner.get_cleaned_sheet('media_exposure', '转发量')
        # 如果没有清理后的数据，使用原始数据
        if forwarding_df is None and self.data_loader:
            forwarding_df = self.data_loader.get_sheet('media_exposure', '转发量')
            if forwarding_df is not None and len(forwarding_df) > 0:
                # 使用转发量工作表的总行数或转发量总和作为总发稿量
                forwarding_cols = [col for col in forwarding_df.columns if '转发' in str(col) or 'forward' in str(col).lower()]
                if forwarding_cols:
                    forwarding_col = forwarding_cols[0]
                    if forwarding_df[forwarding_col].dtype in ['int64', 'float64']:
                        kpis['total_articles'] = int(forwarding_df[forwarding_col].sum())
                        logger.info(f"使用转发量工作表计算总发稿量: {kpis['total_articles']}")
                    else:
                        kpis['total_articles'] = len(forwarding_df)
                        logger.info(f"使用转发量工作表行数计算总发稿量: {kpis['total_articles']}")
                else:
                    kpis['total_articles'] = len(forwarding_df)
                    logger.info(f"使用转发量工作表行数计算总发稿量: {kpis['total_articles']}")
            else:
                # 如果没有转发量工作表，使用当前工作表
                if article_cols:
                    article_col = article_cols[0]
                    if article_col in df.columns:
                        kpis['total_articles'] = len(df) if df[article_col].dtype == 'object' else int(df[article_col].sum())
                else:
                    kpis['total_articles'] = len(df)
                    logger.info(f"使用当前工作表行数计算总发稿量: {kpis['total_articles']}")
        else:
            # 如果没有多工作表支持，使用当前工作表
            if article_cols:
                article_col = article_cols[0]
                if article_col in df.columns:
                    kpis['total_articles'] = len(df) if df[article_col].dtype == 'object' else int(df[article_col].sum())
            else:
                kpis['total_articles'] = len(df)
                logger.info(f"使用当前工作表行数计算总发稿量: {kpis['total_articles']}")
        
        # 媒体覆盖范围
        if media_cols:
            media_col = media_cols[0]
            if media_col in df.columns:
                unique_media = df[media_col].nunique() if df[media_col].dtype == 'object' else 0
                kpis['media_coverage'] = unique_media
        
        # 总阅读量/浏览量
        if read_cols:
            read_col = read_cols[0]
            if read_col in df.columns and df[read_col].dtype in ['int64', 'float64']:
                kpis['total_reads'] = df[read_col].sum()
                kpis['avg_reads'] = df[read_col].mean()
        
        if view_cols:
            view_col = view_cols[0]
            if view_col in df.columns and df[view_col].dtype in ['int64', 'float64']:
                kpis['total_views'] = df[view_col].sum()
                kpis['avg_views'] = df[view_col].mean()
        
        # 加权媒体价值 (AVE) - 简化计算
        if article_cols and read_cols:
            article_col = article_cols[0]
            read_col = read_cols[0]
            if read_col in df.columns and df[read_col].dtype in ['int64', 'float64']:
                # 假设每1000次阅读 = 1元广告价值
                kpis['ave'] = df[read_col].sum() / 1000
        
        return kpis
    
    def _calculate_social_media_kpis(self):
        """
        计算社交媒体互动指标
        
        主要指标：
        - engagement_rate: 社交互动率 = (总互动数 / 总粉丝数) × 100%
          如果没有粉丝数，则使用发帖数计算：社交互动率 = (总互动数 / 总发帖数) × 100%
          总互动数 = 点赞数 + 评论数 + 转发数 + 其他互动
        """
        df = self.cleaned_data['social_media']
        kpis = {}
        
        # 查找相关列 - 扩展匹配模式
        # 粉丝数相关列
        follower_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['粉丝', 'follower', '关注', 'follow', '关注者', '关注数'])]
        # 点赞相关列
        like_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['点赞', 'like', '赞', '点赞数', 'likes'])]
        # 评论相关列
        comment_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['评论', 'comment', '留言', '评论数', 'comments'])]
        # 转发相关列
        share_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['转发', 'share', '分享', '转发数', 'shares'])]
        # 发帖相关列
        post_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['发帖', 'post', '发布', '内容', '帖子', 'posts', '发文'])]
        # 互动相关列（总互动数）
        engagement_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['互动', 'engagement', '互动数', '总互动'])]
        # 关键意见用户相关列
        kol_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['关键意见', 'kol', 'koc', '意见领袖', '关键用户', '关键意见用户'])]
        
        logger.info(f"社交媒体数据列名: {list(df.columns)}")
        logger.info(f"找到的列 - 粉丝: {follower_cols}, 点赞: {like_cols}, 评论: {comment_cols}, 转发: {share_cols}, 发帖: {post_cols}, 互动: {engagement_cols}, KOL: {kol_cols}")
        
        # 总粉丝数
        if follower_cols:
            follower_col = follower_cols[0]
            if follower_col in df.columns and df[follower_col].dtype in ['int64', 'float64']:
                kpis['total_followers'] = df[follower_col].sum()
                kpis['avg_followers'] = df[follower_col].mean()
        
        # 互动总量
        total_engagement = 0
        
        # 优先使用总互动数列（如果存在）
        if engagement_cols:
            engagement_col = engagement_cols[0]
            if engagement_col in df.columns and df[engagement_col].dtype in ['int64', 'float64']:
                total_engagement = df[engagement_col].sum()
                kpis['total_engagement'] = total_engagement
                logger.info(f"使用总互动数列: {engagement_col}, 总互动数: {total_engagement}")
        else:
            # 如果没有总互动数列，则分别计算
            if like_cols:
                like_col = like_cols[0]
                if like_col in df.columns and df[like_col].dtype in ['int64', 'float64']:
                    likes = df[like_col].sum()
                    kpis['total_likes'] = likes
                    total_engagement += likes
            
            if comment_cols:
                comment_col = comment_cols[0]
                if comment_col in df.columns and df[comment_col].dtype in ['int64', 'float64']:
                    comments = df[comment_col].sum()
                    kpis['total_comments'] = comments
                    total_engagement += comments
            
            if share_cols:
                share_col = share_cols[0]
                if share_col in df.columns and df[share_col].dtype in ['int64', 'float64']:
                    shares = df[share_col].sum()
                    kpis['total_shares'] = shares
                    total_engagement += shares
            
            kpis['total_engagement'] = total_engagement
        
        # 关键意见用户占比
        if kol_cols:
            kol_col = kol_cols[0]
            if kol_col in df.columns:
                if df[kol_col].dtype in ['int64', 'float64']:
                    # 如果是数值类型，计算平均值或总和
                    kpis['kol_ratio'] = df[kol_col].mean() if '占比' in kol_col or 'ratio' in kol_col.lower() else df[kol_col].sum()
                else:
                    # 如果是文本类型，尝试提取数值
                    try:
                        numeric_values = pd.to_numeric(df[kol_col], errors='coerce')
                        kpis['kol_ratio'] = numeric_values.mean() if '占比' in kol_col or 'ratio' in kol_col.lower() else numeric_values.sum()
                    except:
                        pass
        
        # 互动率 - 修正计算公式
        if total_engagement > 0:
            if follower_cols:
                follower_col = follower_cols[0]
                if follower_col in df.columns and df[follower_col].dtype in ['int64', 'float64']:
                    total_followers = df[follower_col].sum()
                    if total_followers > 0:
                        # 社交互动率 = (总互动数 / 总粉丝数) × 100%
                        kpis['engagement_rate'] = (total_engagement / total_followers) * 100
                        logger.info(f"计算互动率: {total_engagement} / {total_followers} * 100 = {kpis['engagement_rate']:.2f}%")
                    else:
                        kpis['engagement_rate'] = 0.0
                        logger.warning(f"粉丝数为0，无法计算互动率")
                else:
                    kpis['engagement_rate'] = 0.0
                    logger.warning(f"粉丝列 {follower_col} 不是数值类型")
            else:
                # 如果没有粉丝数，使用发帖数计算：社交互动率 = (总互动数 / 总发帖数) × 100%
                if post_cols:
                    post_col = post_cols[0]
                    if post_col in df.columns and df[post_col].dtype in ['int64', 'float64']:
                        total_posts = df[post_col].sum()
                        if total_posts > 0:
                            kpis['engagement_rate'] = (total_engagement / total_posts) * 100
                            logger.info(f"使用发帖数计算互动率: {total_engagement} / {total_posts} * 100 = {kpis['engagement_rate']:.2f}%")
                        else:
                            kpis['engagement_rate'] = 0.0
                            logger.warning(f"发帖数为0，无法计算互动率")
                    else:
                        kpis['engagement_rate'] = 0.0
                        logger.warning(f"发帖列 {post_col} 不是数值类型")
                else:
                    # 如果既没有粉丝数也没有发帖数，检查是否有KOL占比数据
                    if kol_cols:
                        kol_col = kol_cols[0]
                        if kol_col in df.columns and df[kol_col].dtype in ['int64', 'float64']:
                            # 使用KOL占比作为替代指标（但这不是传统意义上的互动率）
                            avg_kol_ratio = df[kol_col].mean()
                            kpis['kol_ratio'] = avg_kol_ratio
                            kpis['engagement_rate'] = 0.0  # 保持为0，因为确实无法计算
                            logger.warning(f"缺少粉丝数和互动数据，无法计算传统互动率。已计算KOL占比: {avg_kol_ratio:.2f}%")
                        else:
                            kpis['engagement_rate'] = 0.0
                            logger.warning(f"未找到粉丝数、发帖数或KOL数据，无法计算互动率。数据列: {list(df.columns)}")
                    else:
                        kpis['engagement_rate'] = 0.0
                        logger.warning(f"未找到粉丝列或发帖列，无法计算互动率。数据列: {list(df.columns)}")
        else:
            kpis['engagement_rate'] = 0.0
            if not kol_cols:
                logger.warning(f"总互动数为0，且无KOL数据，无法计算互动率。数据列: {list(df.columns)}")
            else:
                # 即使没有互动数据，也计算KOL占比
                kol_col = kol_cols[0]
                if kol_col in df.columns and df[kol_col].dtype in ['int64', 'float64']:
                    kpis['kol_ratio'] = df[kol_col].mean()
                    logger.info(f"无互动数据，已计算KOL占比: {kpis['kol_ratio']:.2f}%")
        
        return kpis
    
    def _calculate_investor_relations_kpis(self):
        """
        计算投资者关系指标
        
        主要指标：
        - research_report_coverage: 研报覆盖度 = 唯一券商/分析师数量
          如果研报列为文本类型：研报覆盖度 = 研报列的唯一值数量（nunique）
          如果研报列为数值类型：研报覆盖度 = 非零值的数量或总和
        """
        df = self.cleaned_data['investor_relations']
        kpis = {}
        
        # 查找相关列 - 扩展匹配模式
        # 优先查找"券商数量"列（实际数据中的列名）
        report_cols = [col for col in df.columns if any(keyword in str(col).lower() for keyword in [
            '研报', 'report', '研究报告', '券商研报', 
            '券商数量', '券商', 'broker', 'broker_count', '券商数'
        ])]
        rating_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['评级', 'rating', '评价'])]
        holding_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['持股', 'holding', '持仓'])]
        trading_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['交易', 'trading', '成交', '交易额'])]
        
        logger.info(f"投资者关系数据列名: {list(df.columns)}")
        logger.info(f"找到的列 - 研报/券商: {report_cols}, 评级: {rating_cols}, 持股: {holding_cols}, 交易: {trading_cols}")
        
        # 券商研报覆盖度
        # 如果研报列为文本类型：研报覆盖度 = 研报列的唯一值数量（nunique）
        # 如果研报列为数值类型：研报覆盖度 = 非零值的数量或总和
        if report_cols:
            report_col = report_cols[0]
            if report_col in df.columns:
                if df[report_col].dtype == 'object':
                    # 计算唯一券商数量
                    unique_reports = df[report_col].nunique()
                    kpis['research_report_coverage'] = unique_reports
                    logger.info(f"研报覆盖度（唯一券商数）: {unique_reports}")
                elif df[report_col].dtype in ['int64', 'float64']:
                    # 如果是数值类型（如"券商数量"列），计算总和
                    # 注意：这是100家公司的数据，每家公司有对应的券商数量
                    # 研报覆盖度应该是所有公司的券商数量总和，或者有研报覆盖的公司数量
                    if '数量' in str(report_col) or 'count' in str(report_col).lower():
                        # 如果是数量列，计算总和（所有公司的券商数量总和）
                        kpis['research_report_coverage'] = int(df[report_col].sum())
                        logger.info(f"研报覆盖度（券商数量总和）: {kpis['research_report_coverage']}")
                    else:
                        # 其他情况，计算非零值数量（有研报覆盖的公司数量）
                        non_zero_count = (df[report_col] > 0).sum()
                        kpis['research_report_coverage'] = int(non_zero_count) if non_zero_count > 0 else 0
                        logger.info(f"研报覆盖度（有覆盖的公司数）: {kpis['research_report_coverage']}")
                else:
                    kpis['research_report_coverage'] = 0
        else:
            # 如果没有找到研报/券商列，查找其他可能的列
            analyst_cols = [col for col in df.columns if any(keyword in str(col).lower() for keyword in [
                '分析师', 'analyst', '分析师数量', 'analyst_count'
            ])]
            if analyst_cols:
                analyst_col = analyst_cols[0]
                if analyst_col in df.columns:
                    if df[analyst_col].dtype in ['int64', 'float64']:
                        # 使用分析师数量作为研报覆盖度的替代
                        kpis['research_report_coverage'] = int(df[analyst_col].sum())
                        logger.info(f"使用分析师数量计算覆盖度: {kpis['research_report_coverage']}")
                    else:
                        coverage = df[analyst_col].nunique()
                        kpis['research_report_coverage'] = int(coverage)
                        logger.info(f"使用分析师列（唯一值）计算覆盖度: {coverage}")
            else:
                # 如果都没有，返回0而不是行数
                kpis['research_report_coverage'] = 0
                logger.warning(f"未找到研报/券商相关列，研报覆盖度设为0。数据列: {list(df.columns)}")
        
        # 日均交易额
        if trading_cols:
            trading_col = trading_cols[0]
            if trading_col in df.columns and df[trading_col].dtype in ['int64', 'float64']:
                kpis['avg_daily_trading_value'] = df[trading_col].mean()
                kpis['total_trading_value'] = df[trading_col].sum()
        
        # 机构持股比例
        if holding_cols:
            holding_col = holding_cols[0]
            if holding_col in df.columns and df[holding_col].dtype in ['int64', 'float64']:
                kpis['avg_institutional_holding'] = df[holding_col].mean()
                kpis['total_institutional_holding'] = df[holding_col].sum()
        
        return kpis
    
    def _calculate_risk_reputation_kpis(self):
        """计算风险与声誉管控指标"""
        df = self.cleaned_data['risk_reputation']
        kpis = {}
        
        # 查找相关列
        sentiment_cols = [col for col in df.columns if '情感' in col or 'sentiment' in col.lower() or '舆情' in col]
        negative_cols = [col for col in df.columns if '负面' in col or 'negative' in col.lower()]
        risk_cols = [col for col in df.columns if '风险' in col or 'risk' in col.lower()]
        compliance_cols = [col for col in df.columns if '合规' in col or 'compliance' in col.lower() or '监管' in col]
        
        # 负面舆情占比
        if negative_cols and sentiment_cols:
            negative_col = negative_cols[0]
            sentiment_col = sentiment_cols[0]
            if negative_col in df.columns and sentiment_col in df.columns:
                if df[negative_col].dtype in ['int64', 'float64']:
                    total_negative = df[negative_col].sum()
                    total_sentiment = df[sentiment_col].sum() if df[sentiment_col].dtype in ['int64', 'float64'] else len(df)
                    if total_sentiment > 0:
                        kpis['negative_sentiment_ratio'] = total_negative / total_sentiment * 100
        
        # 风险事件数量
        if risk_cols:
            risk_col = risk_cols[0]
            if risk_col in df.columns:
                if df[risk_col].dtype == 'object':
                    kpis['risk_events_count'] = len(df[df[risk_col].notna()])
                elif df[risk_col].dtype in ['int64', 'float64']:
                    kpis['risk_events_count'] = df[risk_col].sum()
        
        # 合规事件数量
        if compliance_cols:
            compliance_col = compliance_cols[0]
            if compliance_col in df.columns:
                if df[compliance_col].dtype == 'object':
                    kpis['compliance_events_count'] = len(df[df[compliance_col].notna()])
                elif df[compliance_col].dtype in ['int64', 'float64']:
                    kpis['compliance_events_count'] = df[compliance_col].sum()
        
        return kpis
    
    def _calculate_trends(self):
        """计算趋势分析"""
        for key, kpis in self.kpi_results.items():
            trends = {}
            
            # 如果有时间序列数据，计算趋势
            if key in self.cleaned_data:
                df = self.cleaned_data[key]
                
                # 查找日期列
                date_cols = [col for col in df.columns if 'date' in col.lower() or '时间' in col or '日期' in col]
                
                if date_cols:
                    date_col = date_cols[0]
                    try:
                        df['_date'] = pd.to_datetime(df[date_col])
                        df_sorted = df.sort_values('_date')
                        
                        # 计算数值列的趋势
                        numeric_cols = df_sorted.select_dtypes(include=[np.number]).columns
                        for col in numeric_cols[:5]:  # 限制列数
                            if len(df_sorted) > 1:
                                # 线性回归计算趋势
                                x = np.arange(len(df_sorted))
                                y = df_sorted[col].values
                                if len(y) > 1 and not np.isnan(y).all():
                                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                                    trends[f'{col}_trend'] = {
                                        'slope': slope,
                                        'r_squared': r_value ** 2,
                                        'direction': 'increasing' if slope > 0 else 'decreasing'
                                    }
                    except:
                        pass
            
            self.trend_analysis[key] = trends
    
    def get_kpi_summary(self):
        """获取KPI摘要"""
        summary = []
        for category, kpis in self.kpi_results.items():
            for kpi_name, kpi_value in kpis.items():
                summary.append({
                    '类别': category,
                    '指标名称': kpi_name,
                    '指标值': kpi_value
                })
        return pd.DataFrame(summary)


if __name__ == "__main__":
    from data_loader import DataLoader
    from data_cleaner import DataCleaner
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    analyzer = DataAnalyzer(cleaned_data)
    kpis = analyzer.calculate_all_kpis()
    
    summary = analyzer.get_kpi_summary()
    print("\nKPI指标摘要:")
    print(summary.to_string())


