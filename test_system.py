"""
系统测试脚本
用于快速测试各个模块是否正常工作
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer
from config import EXCEL_FILES

def test_data_loading():
    """测试数据加载"""
    print("=" * 60)
    print("测试1: 数据加载模块")
    print("=" * 60)
    
    loader = DataLoader()
    
    # 检查文件是否存在
    missing_files = []
    for key, file_path in EXCEL_FILES.items():
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"警告: 文件不存在 - {file_path}")
    
    if missing_files:
        print(f"\n共有 {len(missing_files)} 个文件缺失")
        return False
    
    # 加载数据
    data = loader.load_all_excel_files()
    
    # 检查加载结果
    loaded_count = sum(1 for v in data.values() if v is not None)
    print(f"\n成功加载 {loaded_count}/{len(data)} 个数据文件")
    
    if loaded_count == len(data):
        print("✓ 数据加载测试通过")
        return True
    else:
        print("✗ 数据加载测试失败")
        return False

def test_data_cleaning():
    """测试数据清洗"""
    print("\n" + "=" * 60)
    print("测试2: 数据清洗模块")
    print("=" * 60)
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    cleaned_count = sum(1 for v in cleaned_data.values() if v is not None)
    print(f"\n成功清洗 {cleaned_count}/{len(cleaned_data)} 个数据文件")
    
    if cleaned_count > 0:
        print("✓ 数据清洗测试通过")
        return True
    else:
        print("✗ 数据清洗测试失败")
        return False

def test_data_analysis():
    """测试数据分析"""
    print("\n" + "=" * 60)
    print("测试3: 数据分析模块")
    print("=" * 60)
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    analyzer = DataAnalyzer(cleaned_data)
    kpis = analyzer.calculate_all_kpis()
    
    kpi_count = len(kpis)
    print(f"\n计算了 {kpi_count} 个类别的KPI指标")
    
    if kpi_count > 0:
        print("✓ 数据分析测试通过")
        return True
    else:
        print("✗ 数据分析测试失败")
        return False

def test_visualization():
    """测试可视化"""
    print("\n" + "=" * 60)
    print("测试4: 可视化模块")
    print("=" * 60)
    
    try:
        import plotly
        print("✓ Plotly库已安装")
    except ImportError:
        print("✗ Plotly库未安装")
        return False
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    analyzer = DataAnalyzer(cleaned_data)
    kpis = analyzer.calculate_all_kpis()
    
    from src.visualizer import Visualizer
    visualizer = Visualizer(cleaned_data, kpis)
    
    try:
        visualizer.create_all_visualizations()
        print("✓ 可视化测试通过")
        return True
    except Exception as e:
        print(f"✗ 可视化测试失败: {str(e)}")
        return False

def test_report_generation():
    """测试报告生成"""
    print("\n" + "=" * 60)
    print("测试5: 报告生成模块")
    print("=" * 60)
    
    try:
        from reportlab.lib.pagesizes import A4
        print("✓ ReportLab库已安装")
    except ImportError:
        print("✗ ReportLab库未安装")
        return False
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    analyzer = DataAnalyzer(cleaned_data)
    kpis = analyzer.calculate_all_kpis()
    
    from src.report_generator import ReportGenerator
    generator = ReportGenerator(cleaned_data, kpis, analyzer.trend_analysis)
    
    try:
        generator.generate_excel_report('quarterly')
        print("✓ 报告生成测试通过")
        return True
    except Exception as e:
        print(f"✗ 报告生成测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("\n")
    print("=" * 60)
    print("商业情报分析系统 - 系统测试")
    print("=" * 60)
    print("\n")
    
    results = []
    
    results.append(("数据加载", test_data_loading()))
    results.append(("数据清洗", test_data_cleaning()))
    results.append(("数据分析", test_data_analysis()))
    results.append(("可视化", test_visualization()))
    results.append(("报告生成", test_report_generation()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("\n✓ 所有测试通过！系统可以正常使用。")
    else:
        print("\n✗ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()




