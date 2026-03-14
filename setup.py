"""
系统安装脚本
"""
from setuptools import setup, find_packages

setup(
    name="insightedge-bi",
    version="1.0.0",
    description="商业情报分析系统",
    author="InsightEdge Team",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "openpyxl>=3.1.0",
        "xlrd>=2.0.0",
        "pymysql>=1.1.0",
        "pymongo>=4.5.0",
        "sqlalchemy>=2.0.0",
        "plotly>=5.17.0",
        "dash>=2.14.0",
        "scikit-learn>=1.3.0",
        "scipy>=1.11.0",
        "reportlab>=4.0.0",
        "fpdf2>=2.7.0",
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
        "mysql-connector-python>=8.1.0",
        "dash-bootstrap-components>=1.5.0",
        "xlsxwriter>=3.1.0"
    ],
    python_requires=">=3.8",
)




