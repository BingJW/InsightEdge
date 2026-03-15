import os,sys,logging
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ======================= Debug & 路径配置区 =======================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from config import TARGET_URLS, DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataScraper:
    def __init__(self, target_urls, base_save_dir):
        """
        初始化爬虫类
        :param target_urls: config 中的目标 URL 字典
        :param base_save_dir: config 中的 DATA_DIR
        """
        self.target_urls = target_urls
        # 在 DATA_DIR 下新建一个文件夹存放抓取结果，防止覆盖作为网站数据源的源文件
        self.save_dir = base_save_dir
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def scrape_table_data(self, url):
        """
        对传入的数据落地页 URL 进行爬取，提取表格数据并返回。
        """
        print(f"  ├── 正在请求: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status() 
        except requests.RequestException as e:
            print(f"  └── [-] 请求失败: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='dataframe')
        if not table:
            print(f"  └── [-] 网页中未找到目标表格")
            return []

        headers = []
        thead = table.find('thead')
        if thead:
            headers = [th.text.strip() for th in thead.find_all('th')]

        data = []
        tbody = table.find('tbody')
        rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:]
        
        for row in rows:
            cells = row.find_all('td')
            if not cells:
                continue
            row_values = [cell.text.strip() for cell in cells]
            row_dict = dict(zip(headers, row_values))
            data.append(row_dict)

        return data

    def run(self):
        """
        执行全站遍历爬取，并按层级结构保存为 Excel 文件
        """
        print(f"[*] 开始全站爬取任务...")
        print(f"[*] 抓取结果将统一保存至: {self.save_dir}\n")
        
        # 遍历一级 key (文件名)
        for file_name, sheets in self.target_urls.items():
            print(f"[+] 开始处理目标文件: {file_name}")
            
            # 为当前抓取的数据生成保存路径
            save_path = os.path.join(self.save_dir, file_name)
            
            try:
                # 使用 pandas 的 ExcelWriter，这样可以将多个 sheet 写入同一个 Excel 文件中
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    
                    # 遍历二级 key (Sheet 名) 和对应的 URL
                    for sheet_name, url in sheets.items():
                        # 调用抓取函数
                        data = self.scrape_table_data(url)
                        
                        if data:
                            # 将抓取到的 List[dict] 转换为 DataFrame
                            df = pd.DataFrame(data)
                            # 写入对应的 Sheet 中，不保留 DataFrame 的默认数字索引
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            print(f"  └── [√] {sheet_name}: 成功抓取并写入 {len(data)} 条数据")
                        else:
                            # 如果该页面没有数据，创建一个空表占位
                            df = pd.DataFrame()
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            print(f"  └── [!] {sheet_name}: 未抓取到数据，已创建空表")
                            
            except Exception as e:
                print(f"[-] 保存文件 {file_name} 时发生错误: {e}")
            
            print("-" * 40)
            
        print("[*] 所有爬取与保存任务已圆满完成！")

# --- 启动代码 ---
if __name__ == '__main__':
    # 实例化爬虫并运行
    scraper = DataScraper(target_urls=TARGET_URLS, base_save_dir=DATA_DIR)
    scraper.run()