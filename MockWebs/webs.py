import os
import pandas as pd
from flask import Flask, render_template_string, abort

app = Flask(__name__)

# 获取当前代码文件所在的绝对目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接得到 data 文件夹的绝对路径
DATA_DIR = os.path.join(BASE_DIR, 'data')

def get_excel_files():
    """获取 data 目录下所有的 Excel 文件"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        return []
    return [f for f in os.listdir(DATA_DIR) if f.endswith(('.xlsx', '.xls'))]

@app.route('/')
def index():
    """第一层：网站主页（展示所有 Excel 文件）"""
    files = get_excel_files()
    
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>数据中心 - 首页</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .file-list { font-size: 18px; line-height: 1.6; }
        </style>
    </head>
    <body>
        <h1>欢迎来到数据中心</h1>
        <p>请选择你要查看的数据集文件：</p>
        <ul class="file-list">
            {% for file in files %}
                <li><a href="/dataset/{{ file }}">{{ file }}</a></li>
            {% endfor %}
            {% if not files %}
                <p style="color: red;">当前 data/ 目录下没有发现 Excel 文件，请添加后刷新！</p>
            {% endif %}
        </ul>
    </body>
    </html>
    """
    return render_template_string(html_template, files=files)

@app.route('/dataset/<filename>')
def file_index(filename):
    """第二层：文件详情页（展示该 Excel 文件下的所有 Sheet）"""
    files = get_excel_files()
    if filename not in files:
        abort(404)
        
    file_path = os.path.join(DATA_DIR, filename)
    
    try:
        # 使用 pd.ExcelFile 高效获取所有 sheet 的名称，而不必加载所有数据
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        
        html_template = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>{{ filename }} - Sheet 列表</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h2 { color: #444; }
                .sheet-list { font-size: 16px; line-height: 1.6; }
                .nav-link { display: inline-block; margin-bottom: 20px; color: #0066cc; text-decoration: none; }
                .nav-link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <a href="/" class="nav-link">← 返回首页</a>
            <h2>文件: {{ filename }}</h2>
            <p>该文件包含以下数据表 (Sheets)：</p>
            <ul class="sheet-list">
                {% for sheet in sheet_names %}
                    <li><a href="/dataset/{{ filename }}/{{ sheet }}">{{ sheet }}</a></li>
                {% endfor %}
            </ul>
        </body>
        </html>
        """
        return render_template_string(html_template, filename=filename, sheet_names=sheet_names)
        
    except Exception as e:
        return f"读取 Excel 结构出错: {str(e)}", 500

@app.route('/dataset/<filename>/<sheet_name>')
def sheet_data(filename, sheet_name):
    """第三层：数据落地页（展示具体某个 Sheet 的表格数据）"""
    files = get_excel_files()
    if filename not in files:
        abort(404)
        
    file_path = os.path.join(DATA_DIR, filename)
    
    try:
        # 只读取特定的 sheet 数据
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # 转换为 HTML 表格
        table_html = df.to_html(index=False, border=1, classes='dataframe')
        
        html_template = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>{{ sheet_name }} - 数据详情</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .nav-link { display: inline-block; margin-bottom: 20px; color: #0066cc; text-decoration: none; margin-right: 15px; }
                .nav-link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div>
                <a href="/" class="nav-link">← 返回首页</a>
                <a href="/dataset/{{ filename }}" class="nav-link">↑ 返回上级 ({{ filename }})</a>
            </div>
            <h2>数据表: {{ sheet_name }}</h2>
            <div class="table-container">
                {{ table_html | safe }}
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template, filename=filename, sheet_name=sheet_name, table_html=table_html)
        
    except Exception as e:
        return f"读取表单数据出错: {str(e)}", 500

if __name__ == '__main__':
    print(f"[*] 正在启动服务...")
    print(f"[*] 数据目录绝对路径: {DATA_DIR}")
    print(f"[*] 爬虫目标主页地址: http://127.0.0.1:5000/")
    app.run(host='127.0.0.1', port=5000, debug=True)