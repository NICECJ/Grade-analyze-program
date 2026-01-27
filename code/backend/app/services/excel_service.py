import pandas as pd
import os
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime

class ExcelService:
    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def preview_excel(self, file_path: str) -> Dict[str, Any]:
        """预览Excel文件，返回列名和样本数据"""
        try:
            df = pd.read_excel(file_path)
            return {
                "columns": df.columns.tolist(),
                "sample_data": df.head(5).to_dict('records')
            }
        except Exception as e:
            raise ValueError(f"无法读取Excel文件: {str(e)}")
    
    def backup_file(self, file_path: str, exam_name: str) -> str:
        """备份原始文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{exam_name}_{timestamp}.xlsx"
        backup_path = os.path.join(self.backup_dir, filename)
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def detect_grade_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检测成绩表结构，识别科目列"""
        columns = df.columns.tolist()
        
        # 基本信息字段
        basic_fields = []
        # 科目成绩字段
        subject_fields = []
        # 排名字段
        rank_fields = []
        
        # 常见的基本信息字段
        basic_keywords = ['姓名', '学校', '班级', '年级', 'name', 'school', 'class']
        # 常见的科目
        subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '总分']
        # 排名关键词
        rank_keywords = ['排名', '名次', 'rank']
        
        for col in columns:
            col_lower = col.lower()
            
            # 判断是否为基本信息字段
            if any(keyword in col for keyword in basic_keywords):
                basic_fields.append(col)
            # 判断是否为排名字段
            elif any(keyword in col for keyword in rank_keywords):
                rank_fields.append(col)
            # 判断是否为科目成绩字段
            elif any(subject in col for subject in subjects):
                subject_fields.append(col)
            # 数值列可能是成绩
            elif df[col].dtype in ['int64', 'float64']:
                subject_fields.append(col)
        
        return {
            "basic_fields": basic_fields,
            "subject_fields": subject_fields,
            "rank_fields": rank_fields,
            "suggested_mappings": self._suggest_mappings(columns)
        }
    
    def _suggest_mappings(self, columns: List[str]) -> Dict[str, str]:
        """建议字段映射"""
        mappings = {}
        
        # 映射规则
        mapping_rules = {
            'name': ['姓名', 'name', '学生姓名'],
            'school': ['学校', 'school', '学校名称'],
            'current_class': ['班级', 'class', '所在班级'],
            'grade_level': ['年级', 'grade', '年级'],
        }
        
        # 科目映射
        subject_rules = {
            '语文': ['语文', 'chinese'],
            '数学': ['数学', 'math'],
            '英语': ['英语', 'english'],
            '物理': ['物理', 'physics'],
            '化学': ['化学', 'chemistry'],
            '生物': ['生物', 'biology'],
            '历史': ['历史', 'history'],
            '地理': ['地理', 'geography'],
            '政治': ['政治', 'politics'],
            '总分': ['总分', 'total']
        }
        
        for col in columns:
            col_lower = col.lower()
            
            # 匹配基本字段
            for field, keywords in mapping_rules.items():
                if any(keyword in col_lower for keyword in keywords):
                    mappings[col] = field
                    break
            
            # 匹配科目字段
            for subject, keywords in subject_rules.items():
                if any(keyword in col_lower for keyword in keywords):
                    mappings[col] = f"{subject}_score"
                    break
        
        return mappings