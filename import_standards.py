#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测规范数据导入脚本
用于将CSV文件中的检测规范数据导入到数据库中
"""

import pandas as pd
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目配置和扩展
from config import config
from app.extensions import init_db
from app.models.detection.detection_standard import DetectionStandard


def import_standards(csv_file_path, config_name='default'):
    """
    从CSV文件导入检测规范数据到数据库
    
    Args:
        csv_file_path: CSV文件路径
        config_name: 配置名称，默认为'default'
    """
    try:
        # 获取配置
        app_config = config[config_name]
        print(f"使用配置: {config_name}")
        print(f"数据库URL: {app_config.SQLALCHEMY_DATABASE_URI}")
        
        # 初始化数据库
        engine, SessionLocal = init_db(app_config)
        session = SessionLocal()
        
        print(f"开始导入检测规范数据，文件路径: {csv_file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(csv_file_path)
        print(f"CSV文件读取成功，共 {len(df)} 条数据")
        
        # 遍历数据行
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # 转换日期格式
                effective_time = None
                if pd.notna(row['生效日期']) and row['生效日期']:
                    effective_time = datetime.strptime(row['生效日期'], '%Y/%m/%d').date()
                
                invalid_time = None
                if pd.notna(row['失效日期']) and row['失效日期']:
                    invalid_time = datetime.strptime(row['失效日期'], '%Y/%m/%d').date()
                
                # 转换替代规范ID
                replace_id = None
                if pd.notna(row['替代规范ID']) and row['替代规范ID']:
                    replace_id = int(row['替代规范ID'])
                
                # 创建检测规范对象
                standard = DetectionStandard(
                    standard_code=row['规范编号'],
                    standard_name=row['规范名称'],
                    standard_type=row['规范类型'],
                    effective_time=effective_time,
                    invalid_time=invalid_time,
                    status=row['状态'],
                    replace_id=replace_id,
                    remark=row['备注'] if pd.notna(row['备注']) else None
                )
                
                # 检查是否已存在
                existing_standard = session.query(DetectionStandard).filter(
                    DetectionStandard.standard_code == row['规范编号']
                ).first()
                
                if existing_standard:
                    # 更新现有记录
                    existing_standard.standard_name = standard.standard_name
                    existing_standard.standard_type = standard.standard_type
                    existing_standard.effective_time = standard.effective_time
                    existing_standard.invalid_time = standard.invalid_time
                    existing_standard.status = standard.status
                    existing_standard.replace_id = standard.replace_id
                    existing_standard.remark = standard.remark
                    session.merge(existing_standard)
                    print(f"更新规范: {row['规范编号']} - {row['规范名称']}")
                else:
                    # 插入新记录
                    session.add(standard)
                    print(f"插入规范: {row['规范编号']} - {row['规范名称']}")
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"处理第 {index+1} 行数据时出错: {row['规范编号']} - {row['规范名称']}")
                print(f"错误信息: {str(e)}")
                continue
        
        # 提交事务
        session.commit()
        print(f"\n数据导入完成！")
        print(f"成功导入: {success_count} 条")
        print(f"导入失败: {error_count} 条")
        
    except Exception as e:
        print(f"导入过程中发生错误: {str(e)}")
        if 'session' in locals():
            session.rollback()
        raise
    finally:
        if 'session' in locals():
            session.close()


if __name__ == "__main__":
    csv_file = "d:\Projects\jy_syzn\规范.csv"
    import_standards(csv_file)
