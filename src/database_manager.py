"""
数据存储与处理模块
支持MySQL和MongoDB存储
"""
import pandas as pd
import pymysql
from pymongo import MongoClient
from sqlalchemy import create_engine
import logging
from config import DATABASE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_type='mysql'):
        self.db_type = db_type
        self.connection = None
        self.engine = None
        
        if db_type == 'mysql':
            self._connect_mysql()
        elif db_type == 'mongodb':
            self._connect_mongodb()
    
    def _connect_mysql(self):
        """连接MySQL数据库"""
        try:
            config = DATABASE_CONFIG['mysql']
            self.engine = create_engine(
                f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}",
                echo=False
            )
            logger.info("MySQL数据库连接成功")
        except Exception as e:
            logger.error(f"MySQL连接失败: {str(e)}")
    
    def _connect_mongodb(self):
        """连接MongoDB数据库"""
        try:
            config = DATABASE_CONFIG['mongodb']
            self.client = MongoClient(f"mongodb://{config['host']}:{config['port']}/")
            self.db = self.client[config['database']]
            logger.info("MongoDB数据库连接成功")
        except Exception as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
    
    def save_data(self, cleaned_data, table_prefix='cleaned_'):
        """保存清洗后的数据"""
        if self.db_type == 'mysql':
            self._save_to_mysql(cleaned_data, table_prefix)
        elif self.db_type == 'mongodb':
            self._save_to_mongodb(cleaned_data, table_prefix)
    
    def _save_to_mysql(self, cleaned_data, table_prefix):
        """保存到MySQL"""
        if self.engine is None:
            logger.error("MySQL连接未建立")
            return
        
        for key, df in cleaned_data.items():
            if df is not None:
                try:
                    table_name = f"{table_prefix}{key}"
                    df.to_sql(table_name, self.engine, if_exists='replace', index=False)
                    logger.info(f"数据已保存到MySQL表: {table_name}")
                except Exception as e:
                    logger.error(f"保存数据到MySQL失败 {key}: {str(e)}")
    
    def _save_to_mongodb(self, cleaned_data, table_prefix):
        """保存到MongoDB"""
        if not hasattr(self, 'db'):
            logger.error("MongoDB连接未建立")
            return
        
        for key, df in cleaned_data.items():
            if df is not None:
                try:
                    collection_name = f"{table_prefix}{key}"
                    collection = self.db[collection_name]
                    # 删除旧数据
                    collection.delete_many({})
                    # 插入新数据
                    records = df.to_dict('records')
                    if records:
                        collection.insert_many(records)
                    logger.info(f"数据已保存到MongoDB集合: {collection_name}")
                except Exception as e:
                    logger.error(f"保存数据到MongoDB失败 {key}: {str(e)}")
    
    def save_kpis(self, kpi_results, table_name='kpi_results'):
        """保存KPI结果"""
        if self.db_type == 'mysql':
            self._save_kpis_to_mysql(kpi_results, table_name)
        elif self.db_type == 'mongodb':
            self._save_kpis_to_mongodb(kpi_results, table_name)
    
    def _save_kpis_to_mysql(self, kpi_results, table_name):
        """保存KPI到MySQL"""
        if self.engine is None:
            logger.error("MySQL连接未建立")
            return
        
        kpi_data = []
        for category, kpis in kpi_results.items():
            for kpi_name, kpi_value in kpis.items():
                kpi_data.append({
                    'category': category,
                    'kpi_name': kpi_name,
                    'kpi_value': kpi_value,
                    'update_time': pd.Timestamp.now()
                })
        
        if kpi_data:
            kpi_df = pd.DataFrame(kpi_data)
            try:
                kpi_df.to_sql(table_name, self.engine, if_exists='append', index=False)
                logger.info(f"KPI数据已保存到MySQL表: {table_name}")
            except Exception as e:
                logger.error(f"保存KPI到MySQL失败: {str(e)}")
    
    def _save_kpis_to_mongodb(self, kpi_results, table_name):
        """保存KPI到MongoDB"""
        if not hasattr(self, 'db'):
            logger.error("MongoDB连接未建立")
            return
        
        kpi_data = {
            'update_time': pd.Timestamp.now(),
            'kpis': kpi_results
        }
        
        try:
            collection = self.db[table_name]
            collection.insert_one(kpi_data)
            logger.info(f"KPI数据已保存到MongoDB集合: {table_name}")
        except Exception as e:
            logger.error(f"保存KPI到MongoDB失败: {str(e)}")
    
    def query_data(self, table_name, conditions=None):
        """查询数据"""
        if self.db_type == 'mysql':
            return self._query_from_mysql(table_name, conditions)
        elif self.db_type == 'mongodb':
            return self._query_from_mongodb(table_name, conditions)
    
    def _query_from_mysql(self, table_name, conditions):
        """从MySQL查询"""
        if self.engine is None:
            logger.error("MySQL连接未建立")
            return None
        
        try:
            query = f"SELECT * FROM {table_name}"
            if conditions:
                query += f" WHERE {conditions}"
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"MySQL查询失败: {str(e)}")
            return None
    
    def _query_from_mongodb(self, table_name, conditions):
        """从MongoDB查询"""
        if not hasattr(self, 'db'):
            logger.error("MongoDB连接未建立")
            return None
        
        try:
            collection = self.db[table_name]
            if conditions:
                cursor = collection.find(conditions)
            else:
                cursor = collection.find()
            df = pd.DataFrame(list(cursor))
            return df
        except Exception as e:
            logger.error(f"MongoDB查询失败: {str(e)}")
            return None
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.db_type == 'mysql' and self.engine:
            self.engine.dispose()
            logger.info("MySQL连接已关闭")
        elif self.db_type == 'mongodb' and hasattr(self, 'client'):
            self.client.close()
            logger.info("MongoDB连接已关闭")


if __name__ == "__main__":
    from data_loader import DataLoader
    from data_cleaner import DataCleaner
    
    loader = DataLoader()
    raw_data = loader.load_all_excel_files()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all_data(raw_data)
    
    # 测试MySQL存储（需要先配置数据库）
    # db_manager = DatabaseManager('mysql')
    # db_manager.save_data(cleaned_data)
    # db_manager.close_connection()
    
    # 测试MongoDB存储（需要先配置数据库）
    # db_manager = DatabaseManager('mongodb')
    # db_manager.save_data(cleaned_data)
    # db_manager.close_connection()




