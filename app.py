"""
Flask Web应用主程序
"""
from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import json
import pandas as pd
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.data_analyzer import DataAnalyzer
from src.report_generator import ReportGenerator
from config import OUTPUT_DIR, REPORTS_DIR, VISUALIZATIONS_DIR
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'insightedge-bi-secret-key-2024'
app.config['UPLOAD_FOLDER'] = OUTPUT_DIR

# Flask-Login配置
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 自定义未授权处理
@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': '需要登录'}), 401
    return redirect(url_for('login'))

# 简单的用户模型（实际项目中应该使用数据库）
class User(UserMixin):
    def __init__(self, id, username, password_hash, role='user'):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
    
    def is_super_admin(self):
        """检查是否为超级管理员"""
        return self.role == 'super_admin'
    
    def is_admin(self):
        """检查是否为管理员（包括超级管理员）"""
        return self.role in ['admin', 'super_admin']

# 用户数据文件路径
USERS_DB_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    """从文件加载用户数据"""
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                users_db = {}
                for username, user_data in users_data.items():
                    users_db[username] = User(
                        user_data['id'],
                        user_data['username'],
                        user_data['password_hash'],
                        user_data.get('role', 'user')
                    )
                return users_db
        except Exception as e:
            logger.error(f"加载用户数据失败: {str(e)}")
    
    # 如果文件不存在，创建默认用户
    default_users = {
        'admin': User('1', 'admin', generate_password_hash('admin123'), 'super_admin'),
        'user1': User('2', 'user1', generate_password_hash('user123'), 'user'),
    }
    save_users(default_users)
    return default_users

def save_users(users_db):
    """保存用户数据到文件"""
    try:
        users_data = {}
        for username, user in users_db.items():
            users_data[username] = {
                'id': user.id,
                'username': user.username,
                'password_hash': user.password_hash,
                'role': user.role
            }
        with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存用户数据失败: {str(e)}")

# 加载用户数据
users_db = load_users()

@login_manager.user_loader
def load_user(user_id):
    for user in users_db.values():
        if user.id == user_id:
            return user
    return None

def super_admin_required(f):
    """超级管理员权限检查装饰器"""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_super_admin():
            return jsonify({'success': False, 'error': '需要超级管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 全局数据缓存
data_cache = {
    'raw_data': None,
    'cleaned_data': None,
    'kpi_results': None,
    'analyzer': None,
    'loader': None,
    'last_update': None
}

def get_analyzer():
    """获取或创建数据分析器"""
    if data_cache['analyzer'] is None or data_cache['cleaned_data'] is None:
        loader = DataLoader()
        raw_data = loader.load_all_excel_files()
        
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_all_data(raw_data, data_loader=loader)
        
        # 保存清理后的数据（包括所有工作表）
        cleaner.save_cleaned_data()
        
        analyzer = DataAnalyzer(cleaned_data, data_loader=loader, data_cleaner=cleaner)
        kpi_results = analyzer.calculate_all_kpis()
        
        data_cache['raw_data'] = raw_data
        data_cache['cleaned_data'] = cleaned_data
        data_cache['kpi_results'] = kpi_results
        data_cache['analyzer'] = analyzer
        data_cache['loader'] = loader
        data_cache['last_update'] = datetime.now().isoformat()
    
    return data_cache['analyzer']

@app.route('/')
def index():
    """首页"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users_db.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """仪表盘页面"""
    return render_template('dashboard.html')

@app.route('/api/kpi_summary')
@login_required
def api_kpi_summary():
    """
    获取KPI摘要
    
    返回的主要指标：
    - market_cap_growth_rate: 市值增长率
    - total_articles: 总发稿量
    - engagement_rate: 社交互动率
    - research_report_coverage: 研报覆盖度
    """
    try:
        analyzer = get_analyzer()
        kpi_summary = analyzer.get_kpi_summary()
        
        # 转换为字典格式
        result = []
        for _, row in kpi_summary.iterrows():
            result.append({
                'category': row['类别'],
                'kpi_name': row['指标名称'],
                'kpi_value': float(row['指标值']) if isinstance(row['指标值'], (int, float)) else str(row['指标值'])
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'last_update': data_cache['last_update']
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/data_analysis')
@login_required
def api_data_analysis():
    """获取数据分析结果"""
    try:
        analyzer = get_analyzer()
        cleaned_data = data_cache['cleaned_data']
        
        analysis = {
            'categories': {},
            'summary': {}
        }
        
        # 分析每个数据类别
        category_names = {
            'market_cap': '市值与财务表现',
            'media_exposure': '媒体曝光度',
            'social_media': '社交媒体互动',
            'investor_relations': '投资者关系',
            'risk_reputation': '风险与声誉管控'
        }
        
        for category, df in cleaned_data.items():
            if df is not None and not df.empty:
                category_info = {
                    'name': category_names.get(category, category),
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns)[:10],  # 只返回前10个列名
                    'has_date': False,
                    'date_column': None,
                    'numeric_columns': [],
                    'sample_data': {}
                }
                
                # 检查日期列
                date_cols = [col for col in df.columns if any(kw in str(col).lower() for kw in ['date', 'time', '日期', '时间'])]
                if date_cols:
                    category_info['has_date'] = True
                    category_info['date_column'] = date_cols[0]
                
                # 获取数值列
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                category_info['numeric_columns'] = numeric_cols[:5]  # 前5个数值列
                
                # 获取样本数据（前3行）
                if len(df) > 0:
                    sample = df.head(3).to_dict('records')
                    category_info['sample_data'] = sample
                
                analysis['categories'][category] = category_info
        
        # 计算总体统计
        total_rows = sum(info['rows'] for info in analysis['categories'].values())
        total_columns = sum(info['columns'] for info in analysis['categories'].values())
        analysis['summary'] = {
            'total_categories': len(analysis['categories']),
            'total_rows': total_rows,
            'total_columns': total_columns,
            'categories_with_data': list(analysis['categories'].keys())
        }
        
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/data_overview')
@login_required
def api_data_overview():
    """获取数据概览"""
    try:
        if data_cache['loader'] is None:
            loader = DataLoader()
            loader.load_all_excel_files()
            data_cache['loader'] = loader
        else:
            loader = data_cache['loader']
        
        summary = loader.get_data_summary()
        
        result = []
        for _, row in summary.iterrows():
            result.append({
                'table_name': row['数据表'],
                'rows': int(row['行数']),
                'columns': int(row['列数']),
                'missing_values': int(row['缺失值总数']),
                'duplicate_rows': int(row['重复行数']),
                'memory_mb': float(row['内存使用(MB)'])
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/data_table/<table_name>/sheets')
@login_required
def api_data_table_sheets(table_name):
    """获取指定数据表的所有工作表列表"""
    try:
        analyzer = get_analyzer()
        data_cleaner = analyzer.data_cleaner if hasattr(analyzer, 'data_cleaner') else None
        
        if data_cleaner is None:
            return jsonify({'success': False, 'error': '数据清洗器未初始化'}), 404
        
        # 获取所有工作表
        sheets = []
        if table_name in data_cleaner.cleaned_sheets:
            for sheet_name, sheet_df in data_cleaner.cleaned_sheets[table_name].items():
                if sheet_df is not None and not sheet_df.empty:
                    sheets.append({
                        'name': sheet_name,
                        'rows': len(sheet_df),
                        'columns': len(sheet_df.columns)
                    })
        
        # 如果没有找到工作表，检查主工作表
        if not sheets and table_name in data_cache['cleaned_data']:
            df = data_cache['cleaned_data'][table_name]
            if df is not None and not df.empty:
                from config import EXCEL_SHEET_MAPPING
                main_sheet_name = EXCEL_SHEET_MAPPING.get(table_name, '主工作表')
                sheets.append({
                    'name': main_sheet_name,
                    'rows': len(df),
                    'columns': len(df.columns)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'table_name': table_name,
                'sheets': sheets
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/data_table/<table_name>')
@login_required
def api_data_table(table_name):
    """获取指定数据表的内容"""
    try:
        analyzer = get_analyzer()
        data_cleaner = analyzer.data_cleaner if hasattr(analyzer, 'data_cleaner') else None
        
        # 获取sheet参数
        sheet_name = request.args.get('sheet', None, type=str)
        
        # 确定要使用的数据框
        df = None
        
        if data_cleaner and table_name in data_cleaner.cleaned_sheets:
            if sheet_name:
                # 使用指定的sheet
                df = data_cleaner.get_cleaned_sheet(table_name, sheet_name)
            else:
                # 如果没有指定sheet，使用第一个可用的sheet
                sheets = data_cleaner.cleaned_sheets[table_name]
                if sheets:
                    df = list(sheets.values())[0]
        
        # 如果还没有找到数据，尝试使用主工作表
        if df is None or df.empty:
            cleaned_data = data_cache['cleaned_data']
            if cleaned_data is None:
                return jsonify({'success': False, 'error': '数据未加载'}), 404
            
            if table_name not in cleaned_data:
                return jsonify({'success': False, 'error': f'数据表 {table_name} 不存在'}), 404
            
            df = cleaned_data[table_name]
        
        if df is None or df.empty:
            return jsonify({'success': False, 'error': '数据表为空'}), 404
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)
        
        # 搜索过滤
        df_filtered = df.copy()
        if search:
            # 在所有列中搜索
            mask = False
            for col in df.columns:
                mask = mask | df[col].astype(str).str.contains(search, case=False, na=False)
            df_filtered = df[mask]
        
        # 计算总行数
        total_rows = len(df_filtered)
        
        # 分页
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df_filtered.iloc[start_idx:end_idx]
        
        # 转换为字典格式
        data = {
            'columns': list(df.columns),
            'rows': [],
            'total_rows': total_rows,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_rows + per_page - 1) // per_page,
            'sheet_name': sheet_name or '主工作表',
            'table_name': table_name
        }
        
        # 转换数据行
        for _, row in df_page.iterrows():
            row_dict = {}
            for col in df.columns:
                value = row[col]
                # 处理NaN值
                if pd.isna(value):
                    row_dict[col] = None
                # 处理日期类型
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    row_dict[col] = value.strftime('%Y-%m-%d') if pd.notna(value) else None
                else:
                    row_dict[col] = str(value) if value is not None else None
            data['rows'].append(row_dict)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/market_cap_trend')
@login_required
def api_market_cap_trend():
    """获取市值趋势数据"""
    try:
        cleaned_data = data_cache['cleaned_data']
        if cleaned_data is None or 'market_cap' not in cleaned_data:
            return jsonify({'success': False, 'error': '数据未加载'}), 404
        
        df = cleaned_data['market_cap']
        if df is None or df.empty:
            return jsonify({'success': False, 'error': '市值数据为空'}), 404
        
        # 查找市值和日期列 - 改进查找逻辑
        market_cap_cols = [col for col in df.columns if '市值' in col or 'market_cap' in col.lower()]
        
        # 更广泛的日期列查找
        date_cols = []
        date_keywords = ['date', 'time', '日期', '时间', 'datetime', 'timestamp', '年', '月', '日']
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in date_keywords):
                date_cols.append(col)
            # 检查是否是日期类型
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                date_cols.append(col)
        
        # 如果还没找到，尝试检测第一列是否是日期
        if not date_cols and len(df.columns) > 0:
            first_col = df.columns[0]
            try:
                sample_value = df[first_col].dropna().iloc[0] if len(df[first_col].dropna()) > 0 else None
                if sample_value:
                    pd.to_datetime(sample_value, errors='raise')
                    date_cols.append(first_col)
            except:
                pass
        
        if not market_cap_cols:
            # 如果没有找到市值列，尝试使用第一个数值列
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                market_cap_col = numeric_cols[0]
            else:
                return jsonify({'success': False, 'error': '未找到市值数据'}), 404
        else:
            market_cap_col = market_cap_cols[0]
        
        # 准备数据 - 改进日期处理
        dates = []
        values = []
        
        if date_cols:
            date_col = date_cols[0]
            try:
                # 尝试多种日期格式转换
                df['_date'] = pd.to_datetime(df[date_col], errors='coerce', infer_datetime_format=True)
                # 过滤掉无效日期（1970-01-01通常是转换失败的结果）
                df_valid = df[df['_date'].notna() & (df['_date'] > pd.Timestamp('2000-01-01'))].copy()
                
                if len(df_valid) > 0:
                    df_sorted = df_valid.sort_values('_date')
                    dates = df_sorted['_date'].dt.strftime('%Y-%m-%d').tolist()
                    values = df_sorted[market_cap_col].tolist()
                else:
                    # 如果日期转换失败，使用索引作为X轴
                    dates = [f"数据点{i+1}" for i in range(len(df))]
                    values = df[market_cap_col].tolist()
            except Exception as e:
                # 日期转换失败，使用索引
                dates = [f"数据点{i+1}" for i in range(len(df))]
                values = df[market_cap_col].tolist()
        else:
            # 没有日期列，使用索引
            dates = [f"数据点{i+1}" for i in range(min(len(df), 100))]  # 限制显示前100个点
            values = df[market_cap_col].head(100).tolist()
        
        # 限制数据点数量，避免前端渲染过慢
        max_points = 500
        if len(dates) > max_points:
            # 均匀采样
            step = len(dates) // max_points
            dates = dates[::step]
            values = values[::step]
        
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'values': values,
                'label': market_cap_col,
                'date_column_found': len(date_cols) > 0,
                'total_points': len(df)
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/reports')
@login_required
def api_reports():
    """获取报告列表"""
    try:
        reports = []
        if os.path.exists(REPORTS_DIR):
            for filename in os.listdir(REPORTS_DIR):
                filepath = os.path.join(REPORTS_DIR, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    reports.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'type': 'pdf' if filename.endswith('.pdf') else 'excel'
                    })
        
        return jsonify({
            'success': True,
            'data': sorted(reports, key=lambda x: x['created'], reverse=True)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/<filename>')
@login_required
def api_download_report(filename):
    """下载报告"""
    try:
        filepath = os.path.join(REPORTS_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/<filename>', methods=['DELETE'])
@login_required
def api_delete_report(filename):
    """删除报告"""
    try:
        filepath = os.path.join(REPORTS_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({
                'success': True,
                'message': '报告删除成功'
            })
        else:
            return jsonify({'success': False, 'error': '文件不存在'}), 404
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/generate_report', methods=['POST'])
@login_required
def api_generate_report():
    """生成报告"""
    try:
        report_type = request.json.get('report_type', 'quarterly')
        
        analyzer = get_analyzer()
        generator = ReportGenerator(
            data_cache['cleaned_data'],
            data_cache['kpi_results'],
            analyzer.trend_analysis
        )
        
        if report_type == 'daily':
            report_path = generator.generate_daily_report()
        elif report_type == 'weekly':
            report_path = generator.generate_weekly_report()
        elif report_type == 'quarterly':
            report_path = generator.generate_quarterly_report()
        elif report_type == 'yearly':
            report_path = generator.generate_yearly_report()
        else:
            return jsonify({'success': False, 'error': '不支持的报告类型'}), 400
        
        filename = os.path.basename(report_path)
        
        return jsonify({
            'success': True,
            'message': '报告生成成功',
            'filename': filename
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/refresh_data', methods=['POST'])
@login_required
def api_refresh_data():
    """刷新数据"""
    try:
        # 清除缓存，重新加载数据
        data_cache['raw_data'] = None
        data_cache['cleaned_data'] = None
        data_cache['kpi_results'] = None
        data_cache['analyzer'] = None
        data_cache['loader'] = None
        
        # 重新加载
        get_analyzer()
        
        return jsonify({
            'success': True,
            'message': '数据刷新成功',
            'last_update': data_cache['last_update']
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/data_management')
@login_required
def data_management():
    """数据管理页面"""
    return render_template('data_management.html')

@app.route('/reports')
@login_required
def reports():
    """报告页面"""
    return render_template('reports.html')

@app.route('/settings')
@login_required
def settings():
    """设置页面"""
    return render_template('settings.html')

@app.route('/api/crawler_status')
@login_required
def api_crawler_status():
    """获取爬虫状态（预留接口）"""
    return jsonify({
        'success': True,
        'data': {
            'status': '未启用',
            'last_run': None,
            'next_run': None,
            'message': '数据爬取功能待实现'
        }
    })

@app.route('/api/users')
@super_admin_required
def api_get_users():
    """获取所有用户列表（仅超级管理员）"""
    try:
        users_list = []
        for username, user in users_db.items():
            users_list.append({
                'id': user.id,
                'username': user.username,
                'role': user.role
            })
        return jsonify({
            'success': True,
            'data': users_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
@super_admin_required
def api_create_user():
    """创建新用户（仅超级管理员）"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({'success': False, 'error': '用户名和密码不能为空'}), 400
        
        if username in users_db:
            return jsonify({'success': False, 'error': '用户名已存在'}), 400
        
        # 验证角色
        valid_roles = ['user', 'admin', 'super_admin']
        if role not in valid_roles:
            return jsonify({'success': False, 'error': f'无效的角色，必须是: {", ".join(valid_roles)}'}), 400
        
        # 创建新用户
        new_id = str(max([int(u.id) for u in users_db.values()], default=0) + 1)
        new_user = User(new_id, username, generate_password_hash(password), role)
        users_db[username] = new_user
        save_users(users_db)
        
        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'data': {
                'id': new_user.id,
                'username': new_user.username,
                'role': new_user.role
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
@super_admin_required
def api_update_user(user_id):
    """更新用户信息（仅超级管理员）"""
    try:
        data = request.json
        user = None
        
        # 查找用户
        for u in users_db.values():
            if u.id == user_id:
                user = u
                break
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404
        
        # 不能修改自己的角色（防止失去超级管理员权限）
        if user.id == current_user.id and 'role' in data:
            return jsonify({'success': False, 'error': '不能修改自己的角色'}), 400
        
        # 更新密码
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        # 更新角色
        if 'role' in data:
            valid_roles = ['user', 'admin', 'super_admin']
            if data['role'] not in valid_roles:
                return jsonify({'success': False, 'error': f'无效的角色，必须是: {", ".join(valid_roles)}'}), 400
            user.role = data['role']
        
        save_users(users_db)
        
        return jsonify({
            'success': True,
            'message': '用户更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['DELETE'])
@super_admin_required
def api_delete_user(user_id):
    """删除用户（仅超级管理员）"""
    try:
        user = None
        username_to_delete = None
        
        # 查找用户
        for username, u in users_db.items():
            if u.id == user_id:
                user = u
                username_to_delete = username
                break
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404
        
        # 不能删除自己
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': '不能删除自己的账户'}), 400
        
        # 删除用户
        del users_db[username_to_delete]
        save_users(users_db)
        
        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'API端点不存在'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
