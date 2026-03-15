"""
系统配置文件
"""
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 输出目录
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
VISUALIZATIONS_DIR = os.path.join(OUTPUT_DIR, 'visualizations')
CLEANED_DATA_DIR = os.path.join(OUTPUT_DIR, 'cleaned_data')

# 数据目录
DATA_DIR = os.path.join(OUTPUT_DIR, 'data_scraped')

# Target Urls
TARGET_URLS = {
    '第2章 市值与财务表现指标数据.xlsx': {
        '日总市值': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/日总市值',
        '周市值增长率': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/周市值增长率',
        '周相对估值水平': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/周相对估值水平',
        '日股价涨幅': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/日股价涨幅',
        '月超额收益': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/月超额收益',
        '月股价波动率': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/月股价波动率',
        '年经济增加值': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/年经济增加值',
        '季度投入资本回报率': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/季度投入资本回报率',
        '季度净资产收益率': 'http://127.0.0.1:5000/dataset/第2章 市值与财务表现指标数据.xlsx/季度净资产收益率',
    },
    '第3章 媒体曝光度指标数据.xlsx': {
        '情感倾向': 'http://127.0.0.1:5000/dataset/第3章 媒体曝光度指标数据.xlsx/情感倾向',
        '转载量': 'http://127.0.0.1:5000/dataset/第3章 媒体曝光度指标数据.xlsx/转载量',
        '核心信息量': 'http://127.0.0.1:5000/dataset/第3章 媒体曝光度指标数据.xlsx/核心信息量',
        '内容质量及媒体覆盖指标': 'http://127.0.0.1:5000/dataset/第3章 媒体曝光度指标数据.xlsx/内容质量及媒体覆盖指标',
    },
    '第4章 社交媒体互动指标数据 .xlsx': {
        '公司话题总讨论量': 'http://127.0.0.1:5000/dataset/第4章 社交媒体互动指标数据 .xlsx/公司话题总讨论量',
        '讨论热度指数': 'http://127.0.0.1:5000/dataset/第4章 社交媒体互动指标数据 .xlsx/讨论热度指数',
        '高互动内容占比': 'http://127.0.0.1:5000/dataset/第4章 社交媒体互动指标数据 .xlsx/高互动内容占比',
        '情感波动指数': 'http://127.0.0.1:5000/dataset/第4章 社交媒体互动指标数据 .xlsx/情感波动指数',
        '股吧人气排名': 'http://127.0.0.1:5000/dataset/第4章 社交媒体互动指标数据 .xlsx/股吧人气排名',
        '粉丝结构活跃指数': 'http://127.0.0.1:5000/dataset/第4章 社交媒体互动指标数据 .xlsx/粉丝结构活跃指数',
        '关键意见用户占比': 'http://127.0.0.1:5000/dataset/第4章 社交媒体互动指标数据 .xlsx/关键意见用户占比',
    },
    '第5章 投资者关系指标数据.xlsx': {
        '原始数据集合': 'http://127.0.0.1:5000/dataset/第5章 投资者关系指标数据.xlsx/原始数据集合',
    },
    '第6章 风险与声誉管控指标数据.xlsx': {
        'Sheet1': 'http://127.0.0.1:5000/dataset/第6章 风险与声誉管控指标数据.xlsx/Sheet1',
    },
}

# Excel文件路径
EXCEL_FILES = {
    'market_cap': os.path.join(DATA_DIR, '第2章 市值与财务表现指标数据.xlsx'),
    'media_exposure': os.path.join(DATA_DIR, '第3章 媒体曝光度指标数据.xlsx'),
    'social_media': os.path.join(DATA_DIR, '第4章 社交媒体互动指标数据 .xlsx'),
    'investor_relations': os.path.join(DATA_DIR, '第5章 投资者关系指标数据.xlsx'),
    'risk_reputation': os.path.join(DATA_DIR, '第6章 风险与声誉管控指标数据.xlsx')
}

# Excel文件工作表映射配置
# 每个数据文件的主工作表名称（用于KPI计算）
EXCEL_SHEET_MAPPING = {
    'market_cap': '总市值',  # 主工作表：总市值（19968行）
    'media_exposure': '情感分析',  # 主工作表：情感分析（600行）
    'social_media': '关键意见用户占比',  # 主工作表：关键意见用户占比（2600行）
    'investor_relations': '原始数据集',  # 主工作表：原始数据集（100行）
    'risk_reputation': 'Sheet1'  # 主工作表：Sheet1（100行）
}

# 辅助工作表映射（用于特定KPI计算）
EXCEL_AUXILIARY_SHEETS = {
    'media_exposure': {
        '转发量': '转发量',  # 用于计算总发稿量
        '月度信息量': '月度信息量',
        '成分股媒体覆盖指标': '成分股媒体覆盖指标'
    },
    'social_media': {
        '活跃度指标': '活跃度指标',
        '高活跃用户占比': '高活跃用户占比',
        '影响力指标': '影响力指标',
        '可传播信息量': '可传播信息量',
        '粉丝结构活跃指标': '粉丝结构活跃指标'
    },
    'market_cap': {
        '市值增长率': '市值增长率',
        '相对估值水平': '相对估值水平',
        '股价涨跌幅': '股价涨跌幅',
        '月度收益率': '月度收益率',
        '股价波动率': '股价波动率',
        '年度经济增加值': '年度经济增加值',
        '季度投资资本回报率': '季度投资资本回报率',
        '季度净资产收益率': '季度净资产收益率'
    }
}



# 数据库配置
DATABASE_CONFIG = {
    'mysql': {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'your_password',
        'database': 'insightedge_bi',
        'charset': 'utf8mb4'
    },
    'mongodb': {
        'host': 'localhost',
        'port': 27017,
        'database': 'insightedge_bi'
    }
}

# 报告配置
REPORT_CONFIG = {
    'daily': {'format': 'pdf', 'template': 'daily_report'},
    'weekly': {'format': 'pdf', 'template': 'weekly_report'},
    'monthly': {'format': 'pdf', 'template': 'monthly_report'},
    'quarterly': {'format': 'pdf', 'template': 'quarterly_report'},
    'yearly': {'format': 'pdf', 'template': 'yearly_report'}
}

# 创建必要的目录
for dir_path in [OUTPUT_DIR, REPORTS_DIR, VISUALIZATIONS_DIR, CLEANED_DATA_DIR]:
    os.makedirs(dir_path, exist_ok=True)


