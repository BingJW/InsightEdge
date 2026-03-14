# 商业情报分析系统

多维度评价指标的商业情报分析系统，用于上市公司市值管理与IP打造效果评价。

## 系统功能

1. **数据准备与导入**: 加载5个Excel数据表格
2. **数据清洗与标准化**: 去除重复值、填补缺失值、处理异常值
3. **数据分析与计算**: 基于指标体系计算各项KPI指标
4. **可视化展示与仪表盘**: 生成动态可视化图表和仪表盘
5. **数据报告生成**: 支持日报、周报、季报、年报等
6. **数据存储与处理**: 支持MySQL和MongoDB存储

## 环境配置

### 使用Conda环境

1. 创建conda环境：
```bash
conda env create -f environment.yml
```

2. 激活环境：
```bash
conda activate insightedge_bi
```

### 使用pip安装

```bash
pip install -r requirements.txt
```

## 数据文件

确保以下Excel文件位于 `data/` 目录下：

- 第2章 市值与财务表现指标数据.xlsx
- 第3章 媒体曝光度指标数据.xlsx
- 第4章 社交媒体互动指标数据 .xlsx
- 第5章 投资者关系指标数据.xlsx
- 第6章 风险与声誉管控指标数据.xlsx

## 使用方法

### Web界面使用（推荐）

1. **启动Web服务**：
   ```bash
   # Windows
   .\run_web.bat
   
   # 或直接运行
   python app.py
   ```

2. **访问系统**：
   - 打开浏览器访问：http://localhost:5000
   - 默认账户：`admin` / `admin123` 或 `user1` / `user123`

3. **功能模块**：
   - **仪表盘**：查看KPI指标、趋势图表、数据概览
   - **数据管理**：管理数据源、配置数据爬取（预留接口）
   - **报告中心**：生成和下载各类报告（日报、周报、季报、年报）
   - **设置**：查看用户信息和系统配置

### 命令行使用

运行主程序：
```bash
python main.py
```

### 模块化使用

```python
from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer
from src.visualizer import Visualizer
from src.report_generator import ReportGenerator

# 1. 加载数据
loader = DataLoader()
raw_data = loader.load_all_excel_files()

# 2. 清洗数据
cleaner = DataCleaner()
cleaned_data = cleaner.clean_all_data(raw_data)

# 3. 分析数据
analyzer = DataAnalyzer(cleaned_data)
kpis = analyzer.calculate_all_kpis()

# 4. 生成可视化
visualizer = Visualizer(cleaned_data, kpis)
visualizer.create_all_visualizations()

# 5. 生成报告
generator = ReportGenerator(cleaned_data, kpis, analyzer.trend_analysis)
generator.generate_quarterly_report()
```

## 配置说明

### 数据库配置

编辑 `config.py` 中的数据库配置：

```python
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
```

### 输出目录

系统会自动创建以下输出目录：

- `output/cleaned_data/`: 清洗后的数据
- `output/reports/`: 生成的报告
- `output/visualizations/`: 可视化图表

## 指标体系

系统基于以下六大维度进行分析：

1. **媒体曝光度指标** (Media Exposure Metrics)
2. **社交媒体互动数据指标** (Social Media Engagement Metrics)
3. **投资者关系指标** (Investor Relations Metrics)
4. **市值与财务表现指标** (Market Capitalization & Financial Performance Metrics)
5. **业务与资源整合实质指标** (Business & Resource Integration Metrics)
6. **风险与声誉管控指标** (Risk & Reputation Management Metrics)

详细指标定义请参考 `data/上市公司市值管理与IP打造效果评价指标体系.txt`

## 报告类型

- **日报**: 核心指标和预警信息
- **周报**: 各维度详细分析
- **季报**: 全面绩效报告（包含目标对比、趋势分析等）
- **年报**: 年度总结和趋势分析
- **Excel报告**: 数据表格格式的报告

## 可视化图表

系统生成以下类型的可视化图表：

- KPI综合仪表盘
- 市值趋势图
- 媒体曝光度分析
- 社交媒体互动分析
- 投资者关系图表
- 风险与声誉分析
- 各维度KPI对比

所有图表以HTML格式保存，可在浏览器中打开查看。

## 注意事项

1. 首次运行前，请确保所有Excel数据文件已放置在 `data/` 目录下
2. 数据库存储功能需要先配置数据库连接信息
3. 系统会自动处理数据格式、缺失值、异常值等问题
4. 生成的报告和可视化图表保存在 `output/` 目录下

## 系统架构

```
InsightEdge/
├── config.py                 # 系统配置
├── main.py                   # 主程序
├── requirements.txt          # Python依赖
├── environment.yml          # Conda环境配置
├── data/                     # 数据目录
│   ├── *.xlsx               # Excel数据文件
│   └── 指标体系.txt         # 指标体系文档
├── src/                      # 源代码目录
│   ├── data_loader.py       # 数据加载模块
│   ├── data_cleaner.py      # 数据清洗模块
│   ├── data_analyzer.py     # 数据分析模块
│   ├── visualizer.py        # 可视化模块
│   ├── report_generator.py  # 报告生成模块
│   └── database_manager.py  # 数据库管理模块
└── output/                   # 输出目录
    ├── cleaned_data/        # 清洗后的数据
    ├── reports/             # 生成的报告
    └── visualizations/      # 可视化图表
```

## Web API接口

系统提供RESTful API接口，详细文档请参考 `使用说明文档.md`。

主要接口：
- `GET /api/kpi_summary` - 获取KPI摘要
- `GET /api/data_overview` - 获取数据概览
- `GET /api/market_cap_trend` - 获取市值趋势
- `GET /api/reports` - 获取报告列表
- `POST /api/generate_report` - 生成报告
- `POST /api/refresh_data` - 刷新数据

## 详细文档

完整的使用说明请查看：**`使用说明文档.md`**

该文档包含：
- 详细的安装配置步骤
- Web界面使用指南
- API接口文档
- 常见问题解答
- 故障排除指南
- 系统维护说明

## 许可证

本项目仅供内部使用。


