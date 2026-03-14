"""
检查数据结构和KPI计算
"""
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer

# 加载数据
loader = DataLoader()
raw_data = loader.load_all_excel_files()

print("=" * 60)
print("原始数据检查")
print("=" * 60)
for key, df in raw_data.items():
    if df is not None:
        print(f"\n{key}:")
        print(f"  形状: {df.shape}")
        print(f"  列名: {list(df.columns)[:10]}")
        if len(df) > 0:
            print(f"  第一行数据:")
            for col in df.columns[:5]:
                val = df[col].iloc[0]
                print(f"    {col}: {val} (类型: {type(val).__name__})")

# 清洗数据
cleaner = DataCleaner()
cleaned_data = cleaner.clean_all_data(raw_data)

print("\n" + "=" * 60)
print("清洗后数据检查")
print("=" * 60)
for key, df in cleaned_data.items():
    if df is not None:
        print(f"\n{key}:")
        print(f"  形状: {df.shape}")
        print(f"  列名: {list(df.columns)[:10]}")
        # 检查日期列
        date_cols = [col for col in df.columns if any(kw in str(col).lower() for kw in ['date', 'time', '日期', '时间'])]
        if date_cols:
            print(f"  找到日期列: {date_cols}")
            date_col = date_cols[0]
            sample_dates = df[date_col].dropna().head(5)
            print(f"  日期样本: {sample_dates.tolist()}")

# 计算KPI
analyzer = DataAnalyzer(cleaned_data)
kpis = analyzer.calculate_all_kpis()

print("\n" + "=" * 60)
print("KPI计算结果")
print("=" * 60)
for category, kpi_dict in kpis.items():
    print(f"\n{category}:")
    for kpi_name, kpi_value in kpi_dict.items():
        print(f"  {kpi_name}: {kpi_value}")

# 获取KPI摘要
summary = analyzer.get_kpi_summary()
print("\n" + "=" * 60)
print("KPI摘要DataFrame")
print("=" * 60)
print(summary.to_string())



