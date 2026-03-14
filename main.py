"""
商业情报分析系统 - 主程序
整合所有模块，实现完整的数据分析流程
"""
import os
import sys
import logging
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer
from src.visualizer import Visualizer
from src.report_generator import ReportGenerator
from src.database_manager import DatabaseManager
from config import OUTPUT_DIR, REPORTS_DIR, VISUALIZATIONS_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, 'system.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BusinessIntelligenceSystem:
    """商业情报分析系统主类"""
    
    def __init__(self):
        self.loader = None
        self.cleaner = None
        self.analyzer = None
        self.visualizer = None
        self.report_generator = None
        self.db_manager = None
        
        self.raw_data = {}
        self.cleaned_data = {}
        self.kpi_results = {}
        self.trend_analysis = {}
    
    def initialize(self):
        """初始化系统"""
        logger.info("=" * 60)
        logger.info("商业情报分析系统启动")
        logger.info("=" * 60)
        
        self.loader = DataLoader()
        self.cleaner = DataCleaner()
    
    def load_data(self):
        """步骤1: 数据加载"""
        logger.info("\n步骤1: 数据加载与导入")
        logger.info("-" * 60)
        
        self.raw_data = self.loader.load_all_excel_files()
        
        # 显示数据摘要
        summary = self.loader.get_data_summary()
        logger.info("\n数据加载摘要:")
        logger.info(f"\n{summary.to_string()}")
        
        # 显示数据信息
        data_info = self.loader.get_data_info()
        for key, info in data_info.items():
            logger.info(f"\n{key} 数据表信息:")
            logger.info(f"  形状: {info['shape']}")
            logger.info(f"  缺失值总数: {sum(info['missing_values'].values())}")
            logger.info(f"  重复行数: {info['duplicate_rows']}")
        
        return self.raw_data
    
    def clean_data(self):
        """步骤2: 数据清洗与标准化"""
        logger.info("\n步骤2: 数据清洗与标准化")
        logger.info("-" * 60)
        
        self.cleaned_data = self.cleaner.clean_all_data(self.raw_data)
        
        # 保存清洗后的数据
        self.cleaner.save_cleaned_data()
        
        # 显示清洗摘要
        cleaning_summary = self.cleaner.get_cleaning_summary()
        logger.info("\n数据清洗摘要:")
        logger.info(f"\n{cleaning_summary.to_string()}")
        
        return self.cleaned_data
    
    def analyze_data(self):
        """步骤3: 数据分析与计算"""
        logger.info("\n步骤3: 数据分析与计算")
        logger.info("-" * 60)
        
        self.analyzer = DataAnalyzer(self.cleaned_data, data_loader=self.loader)
        self.kpi_results = self.analyzer.calculate_all_kpis()
        self.trend_analysis = self.analyzer.trend_analysis
        
        # 显示KPI摘要
        kpi_summary = self.analyzer.get_kpi_summary()
        logger.info("\nKPI指标摘要:")
        logger.info(f"\n{kpi_summary.to_string()}")
        
        return self.kpi_results
    
    def create_visualizations(self):
        """步骤4: 可视化展示与仪表盘"""
        logger.info("\n步骤4: 可视化展示与仪表盘")
        logger.info("-" * 60)
        
        self.visualizer = Visualizer(self.cleaned_data, self.kpi_results)
        figures = self.visualizer.create_all_visualizations()
        
        # 创建综合仪表盘
        self.visualizer.create_dashboard_html()
        
        logger.info(f"\n可视化图表已保存到: {VISUALIZATIONS_DIR}")
        logger.info(f"仪表盘文件: {os.path.join(VISUALIZATIONS_DIR, 'dashboard.html')}")
        
        return figures
    
    def generate_reports(self, report_types=['quarterly']):
        """步骤5: 数据报告生成"""
        logger.info("\n步骤5: 数据报告生成")
        logger.info("-" * 60)
        
        self.report_generator = ReportGenerator(
            self.cleaned_data,
            self.kpi_results,
            self.trend_analysis
        )
        
        generated_reports = {}
        
        for report_type in report_types:
            if report_type == 'daily':
                report_path = self.report_generator.generate_daily_report()
                generated_reports['daily'] = report_path
            elif report_type == 'weekly':
                report_path = self.report_generator.generate_weekly_report()
                generated_reports['weekly'] = report_path
            elif report_type == 'quarterly':
                report_path = self.report_generator.generate_quarterly_report()
                generated_reports['quarterly'] = report_path
            elif report_type == 'yearly':
                report_path = self.report_generator.generate_yearly_report()
                generated_reports['yearly'] = report_path
        
        # 生成Excel报告
        excel_report = self.report_generator.generate_excel_report('quarterly')
        generated_reports['excel'] = excel_report
        
        logger.info(f"\n报告已生成到: {REPORTS_DIR}")
        for report_type, report_path in generated_reports.items():
            logger.info(f"  {report_type}: {report_path}")
        
        return generated_reports
    
    def save_to_database(self, db_type='mysql'):
        """步骤6: 数据存储与处理"""
        logger.info("\n步骤6: 数据存储与处理")
        logger.info("-" * 60)
        
        try:
            self.db_manager = DatabaseManager(db_type)
            self.db_manager.save_data(self.cleaned_data)
            self.db_manager.save_kpis(self.kpi_results)
            logger.info(f"数据已保存到{db_type.upper()}数据库")
            self.db_manager.close_connection()
        except Exception as e:
            logger.warning(f"数据库存储失败（可能需要先配置数据库）: {str(e)}")
    
    def run_full_pipeline(self, report_types=['quarterly'], save_to_db=False, db_type='mysql'):
        """运行完整的数据分析流程"""
        try:
            # 初始化
            self.initialize()
            
            # 步骤1: 数据加载
            self.load_data()
            
            # 步骤2: 数据清洗
            self.clean_data()
            
            # 步骤3: 数据分析
            self.analyze_data()
            
            # 步骤4: 可视化
            self.create_visualizations()
            
            # 步骤5: 报告生成
            self.generate_reports(report_types)
            
            # 步骤6: 数据库存储（可选）
            if save_to_db:
                self.save_to_database(db_type)
            
            logger.info("\n" + "=" * 60)
            logger.info("系统运行完成！")
            logger.info("=" * 60)
            
            return {
                'status': 'success',
                'cleaned_data': self.cleaned_data,
                'kpi_results': self.kpi_results,
                'reports': REPORTS_DIR,
                'visualizations': VISUALIZATIONS_DIR
            }
            
        except Exception as e:
            logger.error(f"系统运行出错: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }


def main():
    """主函数"""
    system = BusinessIntelligenceSystem()
    
    # 运行完整流程
    result = system.run_full_pipeline(
        report_types=['daily', 'weekly', 'quarterly'],
        save_to_db=False  # 设置为True并配置数据库后启用
    )
    
    if result['status'] == 'success':
        print("\n系统运行成功！")
        print(f"报告目录: {result['reports']}")
        print(f"可视化目录: {result['visualizations']}")
    else:
        print(f"\n系统运行失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()


