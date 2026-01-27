import requests
from bs4 import BeautifulSoup
import argparse
import json
import sys
import urllib.parse

def construct_url(keyword):
    """
    根据关键词构造请求URL
    
    参数:
        keyword: 搜索关键词
    
    返回:
        str: 完整的请求URL
    """
    base_url = "http://www.csres.com/s.jsp"
    # 对关键词进行URL编码
    encoded_keyword = urllib.parse.quote(keyword)
    fixed_params = "submit12=标准搜索&xx=on&wss=on&zf=on&fz=on&pageSize=40&pageNum=1&SortIndex=1&WayIndex=0&nowUrl="
    url = f"{base_url}?keyword={encoded_keyword}&{fixed_params}"
    return url

def fetch_standard_info(keyword):
    """
    根据关键词搜索并提取标准信息
    
    参数:
        keyword: 搜索关键词
    
    返回:
        list: 包含标准信息的字典列表，每个字典包含standard_number, standard_name, implementation_date, status字段
    """
    try:
        # 1. 构造请求URL
        url = construct_url(keyword)
        print(f"请求URL: {url}")
        
        # 2. 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'http://www.csres.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # 检查请求是否成功
        
        # 添加调试信息：检查响应状态码和内容长度
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容长度: {len(response.text)} 字符")
        
        # 3. 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 添加调试信息：检查是否找到相关标准的提示
        crumb_trail = soup.find(class_='crumbTrail')
        if crumb_trail:
            print(f"面包屑信息: {crumb_trail.get_text(strip=True)}")
        
        # 4. 提取数据
        # 定位表格 - 尝试多种方式
        # 方式1：按class查找
        table = soup.find('table', class_='heng')
        
        # 方式2：如果方式1失败，尝试查找所有表格并检查是否包含th元素
        if not table:
            print("方式1：未找到class='heng'的表格，尝试方式2")
            all_tables = soup.find_all('table')
            print(f"共找到 {len(all_tables)} 个表格")
            
            for i, tbl in enumerate(all_tables):
                # 检查表格是否包含表头
                if tbl.find('th'):
                    print(f"表格 {i+1} 包含表头")
                    # 检查表头内容
                    ths = tbl.find_all('th')
                    th_texts = [th.get_text(strip=True) for th in ths]
                    print(f"表头内容: {th_texts}")
                    # 如果表头包含"标准编号"，则认为是目标表格
                    if any("标准编号" in th_text for th_text in th_texts):
                        table = tbl
                        print(f"找到目标表格: 表格 {i+1}")
                        break
        
        if not table:
            print("未找到包含标准数据的表格")
            # 保存响应内容到文件，便于调试
            with open('response_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("响应内容已保存到 response_debug.html 文件，便于调试")
            return []
        
        # 查找所有数据行
        data_rows = []
        rows = table.find_all('tr')
        print(f"表格中共找到 {len(rows)} 行")
        
        for i, row in enumerate(rows):
            # 数据行有onclick属性，表头行没有
            if row.get('onclick'):
                data_rows.append(row)
                print(f"找到数据行: 行 {i+1}")
        
        if not data_rows:
            print(f"未找到与关键词 '{keyword}' 相关的标准数据")
            return []
        
        # 提取每个数据行的字段
        standard_info_list = []
        for row in data_rows:
            tds = row.find_all('td')
            if len(tds) < 5:
                print(f"跳过字段数量不足的行，仅找到 {len(tds)} 个字段")
                continue  # 跳过字段数量不足的行
            
            standard_info = {
                'standard_number': tds[0].get_text(strip=True),
                'standard_name': tds[1].get_text(strip=True),
                'implementation_date': tds[3].get_text(strip=True),
                'status': tds[4].get_text(strip=True)
            }
            standard_info_list.append(standard_info)
        
        print(f"共找到 {len(standard_info_list)} 条相关标准")
        return standard_info_list
        
    except requests.exceptions.RequestException as e:
        print(f"错误：网络请求失败 - {e}")
        return []
    except Exception as e:
        print(f"错误：数据提取失败 - {e}")
        import traceback
        traceback.print_exc()
        return []

def output_results(results, output_format="text"):
    """
    输出结果
    
    参数:
        results: 包含标准信息的字典列表
        output_format: 输出格式，可选值为"text"（默认）或"json"
    """
    if not results:
        print("没有找到相关标准信息")
        return
    
    if output_format == "json":
        # JSON格式输出
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        print("\n=== 搜索结果 ===")
        for i, info in enumerate(results, 1):
            print(f"\n{'-'*50}")
            print(f"序号：{i}")
            print(f"标准编号：{info['standard_number']}")
            print(f"标准名称：{info['standard_name']}")
            print(f"实施日期：{info['implementation_date']}")
            print(f"状态：{info['status']}")
        print(f"\n{'-'*50}")
        print(f"共找到 {len(results)} 条标准")

def parse_arguments():
    """
    解析命令行参数
    
    返回:
        argparse.Namespace: 包含解析结果的命名空间对象
    """
    parser = argparse.ArgumentParser(description="工标网标准信息爬虫")
    parser.add_argument(
        "--keyword", "-k", 
        type=str, 
        help="搜索关键词",
        nargs="?"  # 允许可选，这样可以在没有参数时进入交互模式
    )
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default="text",
        choices=["text", "json"],
        help="输出格式，可选值：text（默认）、json"
    )
    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 获取关键词，如果命令行没有提供则进入交互模式
    keyword = args.keyword
    if not keyword:
        try:
            keyword = input("请输入搜索关键词：").strip()
        except KeyboardInterrupt:
            print("\n用户中断操作")
            sys.exit(0)
    
    if not keyword:
        print("错误：搜索关键词不能为空")
        sys.exit(1)
    
    # 调用函数获取标准信息
    standard_info_list = fetch_standard_info(keyword)
    
    # 输出结果
    output_results(standard_info_list, args.output)
