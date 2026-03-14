"""
数据清洗与标准化模块
负责数据清洗、缺失值处理、异常值处理、格式标准化
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import os
from config import CLEANED_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.cleaned_data = {}
        self.cleaned_sheets = {}  # 存储所有清理后的工作表数据
        self.cleaning_log = {}
    
    def clean_all_data(self, raw_data, data_loader=None):
        """清洗所有数据，包括所有工作表"""
        logger.info("开始数据清洗...")
        
        # 清洗主工作表数据
        for key, df in raw_data.items():
            if df is not None:
                try:
                    cleaned_df = self.clean_dataframe(df, key)
                    self.cleaned_data[key] = cleaned_df
                    logger.info(f"数据表 {key} 主工作表清洗完成")
                except Exception as e:
                    logger.error(f"清洗数据表 {key} 主工作表失败: {str(e)}")
                    self.cleaned_data[key] = None
        
        # 清洗所有辅助工作表数据
        if data_loader is not None and hasattr(data_loader, 'all_sheets'):
            from config import EXCEL_SHEET_MAPPING
            
            logger.info(f"开始处理所有工作表，共 {len(data_loader.all_sheets)} 个文件")
            
            for file_key in data_loader.all_sheets.keys():
                all_sheets = data_loader.get_all_sheets(file_key)
                
                if not all_sheets:
                    logger.warning(f"文件 {file_key} 没有工作表数据")
                    continue
                
                logger.info(f"处理文件 {file_key}，共 {len(all_sheets)} 个工作表: {list(all_sheets.keys())}")
                
                self.cleaned_sheets[file_key] = {}
                
                # 获取主工作表名称
                main_sheet_name = EXCEL_SHEET_MAPPING.get(file_key)
                
                # 清理所有工作表
                for sheet_name, sheet_df in all_sheets.items():
                    if sheet_df is None or sheet_df.empty:
                        logger.warning(f"文件 {file_key} 工作表 {sheet_name} 为空，跳过")
                        continue
                    
                    # 如果主工作表已经在cleaned_data中清理过，使用已清理的数据
                    if sheet_name == main_sheet_name and file_key in self.cleaned_data and self.cleaned_data[file_key] is not None:
                        self.cleaned_sheets[file_key][sheet_name] = self.cleaned_data[file_key]
                        logger.info(f"数据表 {file_key} 主工作表 {sheet_name} 使用已清理的数据 ({len(self.cleaned_data[file_key])}行)")
                    else:
                        # 清理其他工作表
                        try:
                            cleaned_sheet_df = self.clean_dataframe(sheet_df, f"{file_key}_{sheet_name}")
                            self.cleaned_sheets[file_key][sheet_name] = cleaned_sheet_df
                            logger.info(f"数据表 {file_key} 工作表 {sheet_name} 清洗完成 ({len(cleaned_sheet_df)}行)")
                        except Exception as e:
                            logger.error(f"清洗数据表 {file_key} 工作表 {sheet_name} 失败: {str(e)}")
                            import traceback
                            logger.error(traceback.format_exc())
                            self.cleaned_sheets[file_key][sheet_name] = None
                
                logger.info(f"文件 {file_key} 处理完成，共 {len(self.cleaned_sheets[file_key])} 个有效工作表")
        else:
            logger.warning("data_loader 为空或没有 all_sheets 属性，只处理主工作表")
        
        return self.cleaned_data
    
    def get_cleaned_sheet(self, file_key, sheet_name):
        """获取清理后的指定工作表数据"""
        if file_key in self.cleaned_sheets:
            return self.cleaned_sheets[file_key].get(sheet_name)
        return None
    
    def get_all_cleaned_sheets(self, file_key):
        """获取指定文件的所有清理后的工作表"""
        return self.cleaned_sheets.get(file_key, {})
    
    def clean_dataframe(self, df, table_name):
        """清洗单个数据框"""
        original_shape = df.shape
        df = df.copy()
        
        # 1. 去除重复值
        df = self._remove_duplicates(df, table_name)
        
        # 2. 标准化列名
        df = self._standardize_columns(df, table_name)
        
        # 3. 处理缺失值
        df = self._handle_missing_values(df, table_name)
        
        # 4. 处理异常值
        df = self._handle_outliers(df, table_name)
        
        # 5. 标准化日期格式
        df = self._standardize_dates(df, table_name)
        
        # 6. 标准化数值格式
        df = self._standardize_numeric(df, table_name)
        
        # 7. 数据类型转换
        df = self._convert_dtypes(df, table_name)
        
        final_shape = df.shape
        self.cleaning_log[table_name] = {
            'original_shape': original_shape,
            'final_shape': final_shape,
            'rows_removed': original_shape[0] - final_shape[0],
            'columns_changed': original_shape[1] - final_shape[1]
        }
        
        return df
    
    def _remove_duplicates(self, df, table_name):
        """去除重复值"""
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        removed = before - after
        if removed > 0:
            logger.info(f"{table_name}: 移除了 {removed} 行重复数据")
        return df
    
    def _standardize_columns(self, df, table_name):
        """标准化列名"""
        # 去除前后空格
        df.columns = df.columns.str.strip()
        # 统一命名风格（下划线分隔）
        df.columns = df.columns.str.replace(' ', '_').str.replace('-', '_')
        df.columns = df.columns.str.lower()
        return df
    
    def _handle_missing_values(self, df, table_name):
        """处理缺失值"""
        missing_info = {}
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_pct = missing_count / len(df) * 100
                missing_info[col] = {'count': missing_count, 'percentage': missing_pct}
                
                # 根据列类型选择填充策略
                if df[col].dtype in ['int64', 'float64']:
                    # 数值列：使用中位数填充
                    median = df[col].median()
                    if pd.notna(median):
                        df[col].fillna(median, inplace=True)
                    else:
                        df[col].fillna(0, inplace=True)
                elif df[col].dtype == 'object':
                    # 文本列：使用众数或"未知"填充
                    mode = df[col].mode()
                    if len(mode) > 0:
                        df[col].fillna(mode[0], inplace=True)
                    else:
                        df[col].fillna('未知', inplace=True)
                elif 'date' in col.lower() or '时间' in col or '日期' in col:
                    # 日期列：使用前一个有效值填充
                    df[col] = df[col].ffill()
                    df[col] = df[col].bfill()
        
        if missing_info:
            logger.info(f"{table_name}: 处理了缺失值: {missing_info}")
        
        return df
    
    def _handle_outliers(self, df, table_name):
        """处理异常值"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            if IQR > 0:
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # 将异常值替换为边界值
                outliers_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                if outliers_count > 0:
                    df.loc[df[col] < lower_bound, col] = lower_bound
                    df.loc[df[col] > upper_bound, col] = upper_bound
                    logger.info(f"{table_name}.{col}: 处理了 {outliers_count} 个异常值")
        
        return df
    
    def _standardize_dates(self, df, table_name):
        """标准化日期格式"""
        date_patterns = ['date', 'time', '日期', '时间', 'datetime']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in date_patterns):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logger.info(f"{table_name}.{col}: 已转换为日期格式")
                except:
                    pass
        
        return df
    
    def _standardize_numeric(self, df, table_name):
        """标准化数值格式"""
        # 统一金额单位（假设原始数据可能是万元或元）
        amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                       for keyword in ['金额', '收入', '成本', '利润', '市值', 'amount', 'revenue', 'cost', 'profit'])]
        
        for col in amount_cols:
            if df[col].dtype in ['int64', 'float64']:
                # 检查数值范围，如果最大值小于10000，可能是万元单位，转换为元
                max_val = df[col].max()
                if max_val < 10000 and max_val > 0:
                    df[col] = df[col] * 10000
                    logger.info(f"{table_name}.{col}: 已从万元转换为元")
        
        return df
    
    def _convert_dtypes(self, df, table_name):
        """优化数据类型"""
        # 将整数列转换为int32以节省内存
        for col in df.select_dtypes(include=['int64']).columns:
            if df[col].min() >= np.iinfo(np.int32).min and df[col].max() <= np.iinfo(np.int32).max:
                df[col] = df[col].astype('int32')
        
        # 将浮点数列转换为float32以节省内存
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    
    def save_cleaned_data(self):
        """保存清洗后的数据，包括所有工作表"""
        os.makedirs(CLEANED_DATA_DIR, exist_ok=True)
        
        # 保存所有数据文件
        saved_files = set()
        
        # 首先保存有多个工作表的数据文件
        for file_key, sheets_dict in self.cleaned_sheets.items():
            if len(sheets_dict) > 0:
                file_path = os.path.join(CLEANED_DATA_DIR, f"{file_key}_cleaned.xlsx")
                
                try:
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        sheet_count = 0
                        used_sheet_names = set()
                        
                        for sheet_name, sheet_df in sheets_dict.items():
                            if sheet_df is not None and not sheet_df.empty:
                                # 确保sheet名称不超过31个字符（Excel限制）
                                safe_sheet_name = sheet_name[:31] if len(sheet_name) > 31 else sheet_name
                                
                                # 避免重复的sheet名称
                                final_sheet_name = safe_sheet_name
                                counter = 1
                                while final_sheet_name in used_sheet_names:
                                    final_sheet_name = f"{safe_sheet_name[:28]}_{counter}"
                                    counter += 1
                                
                                used_sheet_names.add(final_sheet_name)
                                sheet_df.to_excel(writer, sheet_name=final_sheet_name, index=False)
                                sheet_count += 1
                                logger.info(f"已保存工作表: {file_key}/{sheet_name} -> {final_sheet_name} ({len(sheet_df)}行)")
                        
                        if sheet_count > 0:
                            logger.info(f"已保存清洗后的数据文件（包含{sheet_count}个工作表）: {file_path}")
                            saved_files.add(file_key)
                except Exception as e:
                    logger.error(f"保存数据文件 {file_key} 失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
        
        # 保存只有主工作表的数据文件（如果还没有保存）
        for key, df in self.cleaned_data.items():
            if key not in saved_files and df is not None and not df.empty:
                file_path = os.path.join(CLEANED_DATA_DIR, f"{key}_cleaned.xlsx")
                try:
                    df.to_excel(file_path, index=False)
                    logger.info(f"已保存清洗后的数据（主工作表）: {file_path}")
                except Exception as e:
                    logger.error(f"保存数据文件 {key} 失败: {str(e)}")
    
    def get_cleaning_summary(self):
        """获取清洗摘要"""
        summary = []
        for key, log in self.cleaning_log.items():
            summary.append({
                '数据表': key,
                '原始行数': log['original_shape'][0],
                '清洗后行数': log['final_shape'][0],
                '移除行数': log['rows_removed'],
                '原始列数': log['original_shape'][1],
                '清洗后列数': log['final_shape'][1]
            })
        return pd.DataFrame(summary)


if __name__ == "__main__":
    from data_loader import DataLoader
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    cleaner.save_cleaned_data()
    
    summary = cleaner.get_cleaning_summary()
    print("\n数据清洗摘要:")
    print(summary.to_string())

