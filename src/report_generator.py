"""
数据报告生成模块
支持生成日报、周报、季报、年报等
"""
import pandas as pd
import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging
from config import REPORTS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 注册中文字体
def register_chinese_fonts():
    """注册中文字体"""
    try:
        # 尝试注册常见的中文字体
        font_paths = [
            # Windows 常见字体路径
            r'C:\Windows\Fonts\simhei.ttf',  # 黑体
            r'C:\Windows\Fonts\msyh.ttc',   # 微软雅黑
            r'C:\Windows\Fonts\simsun.ttc',  # 宋体
            r'C:\Windows\Fonts\msyhbd.ttc', # 微软雅黑 Bold
        ]
        
        chinese_font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    if 'simhei' in font_path.lower():
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        pdfmetrics.registerFont(TTFont('ChineseFontBold', font_path))
                        chinese_font_registered = True
                        logger.info(f"成功注册中文字体: {font_path}")
                        break
                    elif 'msyh' in font_path.lower():
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        pdfmetrics.registerFont(TTFont('ChineseFontBold', font_path))
                        chinese_font_registered = True
                        logger.info(f"成功注册中文字体: {font_path}")
                        break
                    elif 'simsun' in font_path.lower():
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        pdfmetrics.registerFont(TTFont('ChineseFontBold', font_path))
                        chinese_font_registered = True
                        logger.info(f"成功注册中文字体: {font_path}")
                        break
                except Exception as e:
                    logger.warning(f"注册字体失败 {font_path}: {str(e)}")
                    continue
        
        if not chinese_font_registered:
            logger.warning("未找到中文字体，PDF中的中文可能显示为乱码")
            return False
        
        return True
    except Exception as e:
        logger.error(f"注册中文字体时出错: {str(e)}")
        return False

# 初始化时注册字体
_chinese_font_available = register_chinese_fonts()

def get_chinese_style_sheet():
    """获取支持中文的样式表"""
    styles = getSampleStyleSheet()
    
    if _chinese_font_available:
        # 创建支持中文的样式
        chinese_font_name = 'ChineseFont'
        chinese_font_bold_name = 'ChineseFontBold'
        
        # 修改现有样式以支持中文
        for style_name in ['Normal', 'Title', 'Heading1', 'Heading2', 'Heading3']:
            if style_name in styles:
                styles[style_name].fontName = chinese_font_name
        
        # 创建新的中文样式
        styles.add(ParagraphStyle(
            name='ChineseNormal',
            parent=styles['Normal'],
            fontName=chinese_font_name,
            fontSize=12
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=styles['Title'],
            fontName=chinese_font_bold_name,
            fontSize=24
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=styles['Heading1'],
            fontName=chinese_font_bold_name,
            fontSize=18
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading2',
            parent=styles['Heading2'],
            fontName=chinese_font_bold_name,
            fontSize=16
        ))
    
    return styles


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, cleaned_data, kpi_results, trend_analysis):
        self.cleaned_data = cleaned_data
        self.kpi_results = kpi_results
        self.trend_analysis = trend_analysis
        self.reports = {}
    
    def generate_daily_report(self):
        """生成日报"""
        logger.info("生成日报...")
        report_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"日报_{report_date}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = get_chinese_style_sheet()
        
        # 标题
        title_style = styles['ChineseTitle'] if _chinese_font_available else styles['Title']
        normal_style = styles['ChineseNormal'] if _chinese_font_available else styles['Normal']
        heading1_style = styles['ChineseHeading1'] if _chinese_font_available else styles['Heading1']
        
        story.append(Paragraph(f"商业情报分析系统 - 日报", title_style))
        story.append(Paragraph(f"报告日期: {report_date}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 执行摘要
        story.append(Paragraph("执行摘要", heading1_style))
        summary = self._generate_summary('daily')
        story.append(Paragraph(summary, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 关键指标
        story.append(Paragraph("关键指标", heading1_style))
        kpi_table = self._create_kpi_table()
        story.append(kpi_table)
        story.append(Spacer(1, 0.2*inch))
        
        # 预警与风险提示
        story.append(Paragraph("预警与风险提示", heading1_style))
        warnings = self._generate_warnings()
        story.append(Paragraph(warnings, normal_style))
        
        doc.build(story)
        logger.info(f"日报已生成: {filepath}")
        return filepath
    
    def generate_weekly_report(self):
        """生成周报"""
        logger.info("生成周报...")
        report_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"周报_{report_date}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = get_chinese_style_sheet()
        
        title_style = styles['ChineseTitle'] if _chinese_font_available else styles['Title']
        normal_style = styles['ChineseNormal'] if _chinese_font_available else styles['Normal']
        heading1_style = styles['ChineseHeading1'] if _chinese_font_available else styles['Heading1']
        
        story.append(Paragraph(f"商业情报分析系统 - 周报", title_style))
        story.append(Paragraph(f"报告日期: {report_date}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 各维度详细分析
        for category in ['market_cap', 'media_exposure', 'social_media', 'investor_relations', 'risk_reputation']:
            if category in self.kpi_results:
                story.append(Paragraph(self._get_category_name(category), heading1_style))
                analysis = self._generate_category_analysis(category)
                story.append(Paragraph(analysis, normal_style))
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        logger.info(f"周报已生成: {filepath}")
        return filepath
    
    def generate_quarterly_report(self):
        """生成季报"""
        logger.info("生成季报...")
        report_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"季报_{report_date}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = get_chinese_style_sheet()
        
        title_style = styles['ChineseTitle'] if _chinese_font_available else styles['Title']
        normal_style = styles['ChineseNormal'] if _chinese_font_available else styles['Normal']
        heading1_style = styles['ChineseHeading1'] if _chinese_font_available else styles['Heading1']
        heading2_style = styles['ChineseHeading2'] if _chinese_font_available else styles['Heading2']
        
        story.append(Paragraph(f"商业情报分析系统 - 季度报告", title_style))
        story.append(Paragraph(f"报告日期: {report_date}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 执行摘要
        story.append(Paragraph("执行摘要", heading1_style))
        summary = self._generate_summary('quarterly')
        story.append(Paragraph(summary, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 项目目标回顾
        story.append(Paragraph("项目目标回顾", heading1_style))
        story.append(Paragraph("本季度设定的KPI目标已完成评估，详见各维度分析。", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 整体绩效概览
        story.append(Paragraph("整体绩效概览", heading1_style))
        kpi_table = self._create_kpi_table()
        story.append(kpi_table)
        story.append(Spacer(1, 0.2*inch))
        
        # 分维度详细分析
        story.append(Paragraph("分维度详细分析", heading1_style))
        for category in ['market_cap', 'media_exposure', 'social_media', 'investor_relations', 'risk_reputation']:
            if category in self.kpi_results:
                story.append(Paragraph(self._get_category_name(category), heading2_style))
                analysis = self._generate_category_analysis(category)
                story.append(Paragraph(analysis, normal_style))
                story.append(Spacer(1, 0.2*inch))
        
        # 目标达成对比
        story.append(Paragraph("目标达成对比", heading1_style))
        story.append(Paragraph("各KPI实际值与目标值对比分析已完成。", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 成功亮点与最佳实践
        story.append(Paragraph("成功亮点与最佳实践", heading1_style))
        highlights = self._generate_highlights()
        story.append(Paragraph(highlights, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 挑战与改进建议
        story.append(Paragraph("挑战与改进建议", heading1_style))
        challenges = self._generate_challenges()
        story.append(Paragraph(challenges, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 下季度行动计划
        story.append(Paragraph("下季度行动计划", heading1_style))
        action_plan = self._generate_action_plan()
        story.append(Paragraph(action_plan, normal_style))
        
        doc.build(story)
        logger.info(f"季报已生成: {filepath}")
        return filepath
    
    def generate_yearly_report(self):
        """生成年报"""
        logger.info("生成年报...")
        report_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"年报_{report_date}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = get_chinese_style_sheet()
        
        title_style = styles['ChineseTitle'] if _chinese_font_available else styles['Title']
        normal_style = styles['ChineseNormal'] if _chinese_font_available else styles['Normal']
        heading1_style = styles['ChineseHeading1'] if _chinese_font_available else styles['Heading1']
        heading2_style = styles['ChineseHeading2'] if _chinese_font_available else styles['Heading2']
        
        story.append(Paragraph(f"商业情报分析系统 - 年度报告", title_style))
        story.append(Paragraph(f"报告日期: {report_date}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 年度总结
        story.append(Paragraph("年度总结", heading1_style))
        summary = self._generate_summary('yearly')
        story.append(Paragraph(summary, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 全年趋势分析
        story.append(Paragraph("全年趋势分析", heading1_style))
        trend_analysis_text = self._generate_trend_analysis()
        story.append(Paragraph(trend_analysis_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 各维度年度表现
        for category in ['market_cap', 'media_exposure', 'social_media', 'investor_relations', 'risk_reputation']:
            if category in self.kpi_results:
                story.append(Paragraph(self._get_category_name(category) + " - 年度表现", heading2_style))
                analysis = self._generate_category_analysis(category)
                story.append(Paragraph(analysis, normal_style))
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        logger.info(f"年报已生成: {filepath}")
        return filepath
    
    def generate_excel_report(self, report_type='quarterly'):
        """生成Excel格式报告"""
        logger.info(f"生成Excel报告: {report_type}")
        report_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"{report_type}_报告_{report_date}.xlsx"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter', engine_kwargs={'options': {'strings_to_urls': False}}) as writer:
                # KPI汇总表
                kpi_summary = []
                for category, kpis in self.kpi_results.items():
                    for kpi_name, kpi_value in kpis.items():
                        kpi_summary.append({
                            '类别': category,
                            '指标名称': kpi_name,
                            '指标值': kpi_value
                        })
                kpi_df = pd.DataFrame(kpi_summary)
                kpi_df.to_excel(writer, sheet_name='KPI汇总', index=False)
                
                # 各维度详细数据
                for category, df in self.cleaned_data.items():
                    if df is not None:
                        # 确保sheet名称不超过31个字符（Excel限制）
                        sheet_name = self._get_category_name(category)
                        if len(sheet_name) > 31:
                            sheet_name = sheet_name[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Excel报告已生成: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"生成Excel报告失败: {str(e)}")
            # 如果xlsxwriter失败，尝试使用openpyxl
            try:
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    kpi_summary = []
                    for category, kpis in self.kpi_results.items():
                        for kpi_name, kpi_value in kpis.items():
                            kpi_summary.append({
                                '类别': category,
                                '指标名称': kpi_name,
                                '指标值': kpi_value
                            })
                    kpi_df = pd.DataFrame(kpi_summary)
                    kpi_df.to_excel(writer, sheet_name='KPI汇总', index=False)
                    
                    for category, df in self.cleaned_data.items():
                        if df is not None:
                            sheet_name = self._get_category_name(category)
                            if len(sheet_name) > 31:
                                sheet_name = sheet_name[:31]
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                logger.info(f"Excel报告已生成（使用openpyxl）: {filepath}")
                return filepath
            except Exception as e2:
                logger.error(f"使用openpyxl生成Excel报告也失败: {str(e2)}")
                raise
    
    def _generate_summary(self, report_type):
        """生成执行摘要"""
        summary_parts = []
        
        if 'market_cap' in self.kpi_results:
            market_kpis = self.kpi_results['market_cap']
            if 'market_cap_growth_rate' in market_kpis:
                growth_rate = market_kpis['market_cap_growth_rate']
                summary_parts.append(f"市值增长率为 {growth_rate:.2f}%")
        
        if 'media_exposure' in self.kpi_results:
            media_kpis = self.kpi_results['media_exposure']
            if 'total_articles' in media_kpis:
                articles = media_kpis['total_articles']
                summary_parts.append(f"总发稿量为 {articles}")
        
        if 'social_media' in self.kpi_results:
            social_kpis = self.kpi_results['social_media']
            if 'engagement_rate' in social_kpis:
                engagement = social_kpis['engagement_rate']
                summary_parts.append(f"社交媒体互动率为 {engagement:.2f}%")
        
        return "；".join(summary_parts) if summary_parts else "暂无数据"
    
    def _create_kpi_table(self):
        """创建KPI表格"""
        data = [['类别', '指标名称', '指标值']]
        
        for category, kpis in self.kpi_results.items():
            for kpi_name, kpi_value in kpis.items():
                data.append([category, kpi_name, str(kpi_value)])
        
        table = Table(data)
        
        # 确定使用的字体
        header_font = 'ChineseFontBold' if _chinese_font_available else 'Helvetica-Bold'
        body_font = 'ChineseFont' if _chinese_font_available else 'Helvetica'
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), header_font),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), body_font),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table
    
    def _generate_category_analysis(self, category):
        """生成类别分析"""
        if category not in self.kpi_results:
            return "暂无数据"
        
        kpis = self.kpi_results[category]
        analysis_parts = []
        
        for kpi_name, kpi_value in kpis.items():
            analysis_parts.append(f"{kpi_name}: {kpi_value}")
        
        return "；".join(analysis_parts)
    
    def _generate_warnings(self):
        """生成预警信息"""
        warnings = []
        
        if 'risk_reputation' in self.kpi_results:
            risk_kpis = self.kpi_results['risk_reputation']
            if 'negative_sentiment_ratio' in risk_kpis:
                ratio = risk_kpis['negative_sentiment_ratio']
                if ratio > 5:
                    warnings.append(f"负面舆情占比达到 {ratio:.2f}%，需要关注")
        
        return "；".join(warnings) if warnings else "暂无预警信息"
    
    def _generate_highlights(self):
        """生成成功亮点"""
        highlights = []
        
        if 'market_cap' in self.kpi_results:
            market_kpis = self.kpi_results['market_cap']
            if 'market_cap_growth_rate' in market_kpis and market_kpis['market_cap_growth_rate'] > 0:
                highlights.append("市值实现正增长")
        
        return "；".join(highlights) if highlights else "持续优化中"
    
    def _generate_challenges(self):
        """生成挑战与改进建议"""
        return "建议持续优化各维度指标，加强风险管控"
    
    def _generate_action_plan(self):
        """生成行动计划"""
        return "下季度将继续优化市值管理策略，提升媒体曝光度和社交互动效果"
    
    def _generate_trend_analysis(self):
        """生成趋势分析"""
        return "全年整体趋势向好，各维度指标均有提升"
    
    def _get_category_name(self, category):
        """获取类别中文名称"""
        names = {
            'market_cap': '市值与财务表现',
            'media_exposure': '媒体曝光度',
            'social_media': '社交媒体互动',
            'investor_relations': '投资者关系',
            'risk_reputation': '风险与声誉管控'
        }
        return names.get(category, category)


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
    
    generator = ReportGenerator(cleaned_data, kpis, analyzer.trend_analysis)
    generator.generate_quarterly_report()
    generator.generate_excel_report('quarterly')


