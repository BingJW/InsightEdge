"""
数据加载模块
负责从Excel文件加载数据并进行初步检查
支持多工作表Excel文件
"""
import pandas as pd
import os
import logging
from config import EXCEL_FILES, DATA_DIR, EXCEL_SHEET_MAPPING, EXCEL_AUXILIARY_SHEETS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """数据加载器"""
    
    def __init__(self):
        self.data = {}
        self.data_info = {}
        self.all_sheets = {}  # 存储所有工作表数据
    
    def load_all_excel_files(self):
        """加载所有Excel文件的主工作表"""
        logger.info("开始加载Excel数据文件...")
        
        for key, file_path in EXCEL_FILES.items():
            if os.path.exists(file_path):
                try:
                    # 获取主工作表名称
                    sheet_name = EXCEL_SHEET_MAPPING.get(key)
                    
                    if sheet_name:
                        # 尝试读取指定的工作表
                        try:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                            self.data[key] = df
                            self._analyze_data_structure(key, df)
                            logger.info(f"成功加载文件: {file_path}, 工作表: {sheet_name}, 数据形状: {df.shape}")
                        except Exception as e:
                            logger.warning(f"无法读取指定工作表 '{sheet_name}'，尝试读取第一个工作表: {str(e)}")
                            # 如果指定工作表不存在，读取第一个工作表
                            df = pd.read_excel(file_path, sheet_name=0)
                            self.data[key] = df
                            self._analyze_data_structure(key, df)
                            logger.info(f"成功加载文件: {file_path}, 使用第一个工作表, 数据形状: {df.shape}")
                    else:
                        # 如果没有配置工作表名称，读取第一个工作表
                        df = pd.read_excel(file_path, sheet_name=0)
                        self.data[key] = df
                        self._analyze_data_structure(key, df)
                        logger.info(f"成功加载文件: {file_path}, 使用第一个工作表, 数据形状: {df.shape}")
                    
                    # 同时加载所有工作表到all_sheets中
                    self._load_all_sheets(key, file_path)
                    
                except Exception as e:
                    logger.error(f"加载文件失败 {file_path}: {str(e)}")
                    self.data[key] = None
            else:
                logger.warning(f"文件不存在: {file_path}")
                self.data[key] = None
        
        return self.data
    
    def _load_all_sheets(self, key, file_path):
        """加载Excel文件的所有工作表"""
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            self.all_sheets[key] = {}
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    self.all_sheets[key][sheet_name] = df
                    logger.debug(f"加载工作表: {key}/{sheet_name}, 形状: {df.shape}")
                except Exception as e:
                    logger.warning(f"无法加载工作表 {key}/{sheet_name}: {str(e)}")
            
            logger.info(f"文件 {key} 共加载 {len(self.all_sheets[key])} 个工作表")
        except Exception as e:
            logger.warning(f"无法读取文件 {file_path} 的所有工作表: {str(e)}")
    
    def get_sheet(self, file_key, sheet_name):
        """获取指定文件的工作表数据"""
        if file_key in self.all_sheets:
            return self.all_sheets[file_key].get(sheet_name)
        return None
    
    def get_all_sheets(self, file_key):
        """获取指定文件的所有工作表"""
        return self.all_sheets.get(file_key, {})
    
    def _analyze_data_structure(self, key, df):
        """分析数据结构"""
        info = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        }
        
        # 检查数值列的异常值
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            info['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # 检查日期列
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].dropna().iloc[0])
                    date_cols.append(col)
                except:
                    pass
        info['date_columns'] = date_cols
        
        self.data_info[key] = info
        logger.info(f"数据表 {key} 分析完成: {df.shape[0]}行, {df.shape[1]}列")
    
    def get_data_info(self):
        """获取所有数据的信息摘要"""
        return self.data_info
    
    def get_data_summary(self):
        """生成数据摘要报告"""
        summary = []
        for key, info in self.data_info.items():
            summary.append({
                '数据表': key,
                '行数': info['shape'][0],
                '列数': info['shape'][1],
                '缺失值总数': sum(info['missing_values'].values()),
                '重复行数': info['duplicate_rows'],
                '内存使用(MB)': round(info['memory_usage'], 2)
            })
        return pd.DataFrame(summary)
    
    def load_single_file(self, file_key):
        """加载单个文件"""
        if file_key in EXCEL_FILES:
            file_path = EXCEL_FILES[file_key]
            if os.path.exists(file_path):
                try:
                    df = pd.read_excel(file_path)
                    self.data[file_key] = df
                    self._analyze_data_structure(file_key, df)
                    return df
                except Exception as e:
                    logger.error(f"加载文件失败 {file_path}: {str(e)}")
                    return None
            else:
                logger.warning(f"文件不存在: {file_path}")
                return None
        else:
            logger.error(f"未知的文件键: {file_key}")
            return None


if __name__ == "__main__":
    loader = DataLoader()
    data = loader.load_all_excel_files()
    summary = loader.get_data_summary()
    print("\n数据加载摘要:")
    print(summary.to_string())


