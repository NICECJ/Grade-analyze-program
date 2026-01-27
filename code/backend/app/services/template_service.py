"""
标准模板导入服务
支持预定义的Excel模板格式，自动识别和导入
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import re
from ..schemas.exam import ExamType, ExamLevel, ScoreType

class TemplateService:
    """标准模板导入服务"""
    
    # 标准列名映射
    STANDARD_COLUMNS = {
        # 学生信息
        '姓名': 'name',
        '学校': 'school', 
        '班级': 'current_class',
        '年级': 'grade_level',
        
        # 必修科目
        '语文': 'chinese',
        '数学': 'math',
        '英语': 'english',
        
        # 主科（物理类/历史类）
        '物理': 'physics',
        '历史': 'history',
        
        # 选考科目（四选二）
        '生物': 'biology',
        '化学': 'chemistry', 
        '地理': 'geography',
        '政治': 'politics',
        
        # 总分
        '总分': 'total_score'
    }
    
    # 排名列识别模式
    RANK_PATTERNS = {
        'school': r'校.*排.*名?|学校.*排.*名?',
        'city': r'市.*排.*名?|地市.*排.*名?',
        'province': r'省.*排.*名?|全省.*排.*名?'
    }
    
    def __init__(self):
        pass
    
    def detect_template_type(self, df: pd.DataFrame) -> Tuple[ExamType, Dict[str, str]]:
        """
        检测模板类型和列映射
        返回: (考试类型, 列映射字典)
        """
        columns = df.columns.tolist()
        column_mapping = {}
        
        # 检测考试类型
        has_physics = any('物理' in col for col in columns)
        has_history = any('历史' in col for col in columns)
        
        if has_physics and not has_history:
            exam_type = ExamType.PHYSICS
        elif has_history and not has_physics:
            exam_type = ExamType.HISTORY
        else:
            # 默认物理类，或者根据数据量判断
            exam_type = ExamType.PHYSICS
        
        # 基础列映射
        for col in columns:
            col_clean = col.strip()
            
            # 直接匹配标准列名
            if col_clean in self.STANDARD_COLUMNS:
                column_mapping[col] = self.STANDARD_COLUMNS[col_clean]
                continue
            
            # 模糊匹配学生信息
            if '姓名' in col_clean or '学生' in col_clean:
                column_mapping[col] = 'name'
            elif '学校' in col_clean:
                column_mapping[col] = 'school'
            elif '班级' in col_clean:
                column_mapping[col] = 'current_class'
            elif '年级' in col_clean:
                column_mapping[col] = 'grade_level'
            
            # 科目成绩匹配
            elif self._is_subject_score_column(col_clean):
                subject, score_type, rank_type = self._parse_subject_column(col_clean)
                if subject:
                    if rank_type:
                        column_mapping[col] = f"{subject}_{rank_type}"
                    elif score_type:
                        column_mapping[col] = f"{subject}_{score_type}_score"
                    else:
                        column_mapping[col] = f"{subject}_original_score"
        
        return exam_type, column_mapping
    
    def _is_subject_score_column(self, col_name: str) -> bool:
        """判断是否为科目成绩列"""
        subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '总分']
        return any(subject in col_name for subject in subjects)
    
    def _parse_subject_column(self, col_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        解析科目列名
        返回: (科目名, 成绩类型, 排名类型)
        """
        # 科目映射
        subject_map = {
            '语文': 'chinese',
            '数学': 'math', 
            '英语': 'english',
            '物理': 'physics',
            '化学': 'chemistry',
            '生物': 'biology',
            '历史': 'history',
            '地理': 'geography',
            '政治': 'politics',
            '总分': 'total_score'
        }
        
        subject = None
        score_type = None
        rank_type = None
        
        # 识别科目
        for chinese_name, english_name in subject_map.items():
            if chinese_name in col_name:
                subject = english_name
                break
        
        if not subject:
            return None, None, None
        
        # 识别排名类型
        for rank_key, pattern in self.RANK_PATTERNS.items():
            if re.search(pattern, col_name):
                # 检查是否为赋分排名
                if '赋分' in col_name or '等级' in col_name:
                    rank_type = f"scaled_rank_{rank_key}"
                else:
                    rank_type = f"rank_{rank_key}"
                break
        
        # 识别成绩类型
        if '赋分' in col_name or '等级' in col_name:
            score_type = 'scaled'
        elif '原始' in col_name:
            score_type = 'original'
        
        return subject, score_type, rank_type
    
    def validate_template(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[str]:
        """
        验证模板数据
        返回错误信息列表
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['name', 'school', 'current_class']
        mapped_fields = set(column_mapping.values())
        
        for field in required_fields:
            if field not in mapped_fields:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查数据完整性
        if 'name' in mapped_fields:
            name_col = next(k for k, v in column_mapping.items() if v == 'name')
            if df[name_col].isnull().any():
                errors.append("姓名字段存在空值")
        
        # 检查至少有一个成绩字段
        score_fields = [v for v in mapped_fields if v.endswith('_score') or 'score' in v]
        if not score_fields:
            errors.append("未找到任何成绩字段")
        
        return errors
    
    def process_template_data(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                             subject_combination: Optional[str] = None) -> Dict:
        """
        处理模板数据，转换为标准格式
        """
        # 重命名列
        df_mapped = df.rename(columns=column_mapping)
        
        # 数据清洗
        df_mapped = self._clean_data(df_mapped)
        
        # 分离学生信息和成绩信息
        student_fields = ['name', 'school', 'current_class', 'grade_level']
        students_data = []
        grades_data = []
        
        for _, row in df_mapped.iterrows():
            if pd.isna(row.get('name')):
                continue
                
            # 学生信息
            student_info = {
                'name': self._safe_str_convert(row.get('name', '')),
                'school': self._safe_str_convert(row.get('school', '未知学校')),
                'current_class': self._safe_str_convert(row.get('current_class', '')),
                'grade_level': self._safe_str_convert(row.get('grade_level', '')) if pd.notna(row.get('grade_level')) else None,
                'subject_combination': subject_combination  # 添加选科组合
            }
            students_data.append(student_info)
            
            # 成绩信息
            student_grades = []
            for col, value in row.items():
                # 只处理真正的成绩字段，排除排名字段
                if (col.endswith('_score') or col.endswith('_original_score') or col.endswith('_scaled_score')) and pd.notna(value):
                    # 确保不是排名字段
                    if any(rank_word in col for rank_word in ['rank_', '_rank']):
                        continue
                        
                    # 解析科目和成绩类型
                    if col.endswith('_original_score'):
                        subject_name = col.replace('_original_score', '')
                        score_type = 'original'
                    elif col.endswith('_scaled_score'):
                        subject_name = col.replace('_scaled_score', '')
                        score_type = 'scaled'
                    elif col.endswith('_score'):
                        subject_name = col.replace('_score', '')
                        score_type = 'original'  # 默认为原始成绩
                    else:
                        continue
                    
                    # 转换科目名称
                    subject_chinese = self._get_chinese_subject_name(subject_name)
                    
                    # 跳过无效的科目名称
                    if subject_chinese == subject_name and subject_name not in ['chinese', 'math', 'english', 'physics', 'chemistry', 'biology', 'history', 'geography', 'politics', 'total_score']:
                        continue
                    
                    grade_info = {
                        'student_key': f"{student_info['school']}_{student_info['current_class']}_{student_info['name']}",
                        'subject_name': subject_chinese,
                        'score_type': score_type,
                        'score': self._safe_float_convert(value),
                        # 原始排名
                        'rank_school': self._get_rank_value(row, f"{subject_name}_rank_school"),
                        'rank_city': self._get_rank_value(row, f"{subject_name}_rank_city"),
                        'rank_province': self._get_rank_value(row, f"{subject_name}_rank_province"),
                        # 赋分排名
                        'scaled_rank_school': self._get_rank_value(row, f"{subject_name}_scaled_rank_school"),
                        'scaled_rank_city': self._get_rank_value(row, f"{subject_name}_scaled_rank_city"),
                        'scaled_rank_province': self._get_rank_value(row, f"{subject_name}_scaled_rank_province")
                    }
                    student_grades.append(grade_info)
            
            grades_data.extend(student_grades)
        
        return {
            'students': students_data,
            'grades': grades_data,
            'total_students': len(students_data),
            'total_grades': len(grades_data)
        }
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗"""
        # 创建副本避免修改原始数据
        df = df.copy()
        
        # 去除空行
        df = df.dropna(how='all')
        
        # 简化数据清洗，只处理字符串列
        try:
            for col in df.columns:
                if col in df.columns and hasattr(df[col], 'dtype') and df[col].dtype == 'object':
                    # 正确地将每个值转换为字符串并去除空格
                    df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)
        except Exception as e:
            print(f"Warning: Data cleaning failed: {e}")
            # 如果清洗失败，直接返回原数据
            pass
        
        return df
    
    def _safe_str_convert(self, value) -> str:
        """安全的字符串转换"""
        if pd.isna(value):
            return ''
        
        # 如果是pandas Series，取第一个值
        if hasattr(value, 'iloc'):
            value = value.iloc[0] if len(value) > 0 else ''
        
        try:
            return str(value).strip()
        except (ValueError, TypeError):
            return ''
    
    def _safe_float_convert(self, value) -> Optional[float]:
        """安全的浮点数转换"""
        if pd.isna(value):
            return None
        
        try:
            str_value = str(value).strip()
            if str_value in ['-', '', 'nan', 'NaN']:
                return None
            return float(str_value)
        except (ValueError, TypeError):
            return None
    
    def _get_rank_value(self, row: pd.Series, rank_field: str) -> Optional[int]:
        """获取排名值"""
        if rank_field not in row or pd.isna(row[rank_field]):
            return None
        
        try:
            rank_str = str(row[rank_field]).strip()
            if rank_str in ['-', '', 'nan', 'NaN']:
                return None
            return int(float(rank_str))
        except (ValueError, TypeError):
            return None
    
    def _get_chinese_subject_name(self, english_name: str) -> str:
        """将英文科目名转换为中文"""
        name_map = {
            'chinese': '语文',
            'math': '数学',
            'english': '英语',
            'physics': '物理',
            'chemistry': '化学',
            'biology': '生物',
            'history': '历史',
            'geography': '地理',
            'politics': '政治',
            'total_score': '总分'
        }
        return name_map.get(english_name, english_name)
    
    def generate_template_example(self, exam_type: ExamType) -> pd.DataFrame:
        """生成标准模板示例"""
        if exam_type == ExamType.PHYSICS:
            columns = [
                '姓名', '学校', '班级', '年级',
                # 语文（必修，只有原始成绩）
                '语文', '语文校排名', '语文市排名', '语文省排名',
                # 数学（必修，只有原始成绩）
                '数学', '数学校排名', '数学市排名', '数学省排名', 
                # 英语（必修，只有原始成绩）
                '英语', '英语校排名', '英语市排名', '英语省排名',
                # 物理（必修，只有原始成绩）
                '物理', '物理校排名', '物理市排名', '物理省排名',
                # 四选二科目（可选，原始+赋分）
                # 化学
                '化学', '化学赋分', '化学校排名', '化学市排名', '化学省排名', 
                '化学赋分校排名', '化学赋分市排名', '化学赋分省排名',
                # 生物
                '生物', '生物赋分', '生物校排名', '生物市排名', '生物省排名',
                '生物赋分校排名', '生物赋分市排名', '生物赋分省排名',
                # 地理
                '地理', '地理赋分', '地理校排名', '地理市排名', '地理省排名',
                '地理赋分校排名', '地理赋分市排名', '地理赋分省排名',
                # 政治
                '政治', '政治赋分', '政治校排名', '政治市排名', '政治省排名',
                '政治赋分校排名', '政治赋分市排名', '政治赋分省排名',
                # 总分（原始+赋分）
                '总分', '总分赋分', '总分校排名', '总分市排名', '总分省排名',
                '总分赋分校排名', '总分赋分市排名', '总分赋分省排名'
            ]
        else:  # 历史类
            columns = [
                '姓名', '学校', '班级', '年级',
                # 语文（必修，只有原始成绩）
                '语文', '语文校排名', '语文市排名', '语文省排名',
                # 数学（必修，只有原始成绩）
                '数学', '数学校排名', '数学市排名', '数学省排名',
                # 英语（必修，只有原始成绩）
                '英语', '英语校排名', '英语市排名', '英语省排名', 
                # 历史（必修，只有原始成绩）
                '历史', '历史校排名', '历史市排名', '历史省排名',
                # 四选二科目（可选，原始+赋分）
                # 化学
                '化学', '化学赋分', '化学校排名', '化学市排名', '化学省排名',
                '化学赋分校排名', '化学赋分市排名', '化学赋分省排名',
                # 生物
                '生物', '生物赋分', '生物校排名', '生物市排名', '生物省排名',
                '生物赋分校排名', '生物赋分市排名', '生物赋分省排名',
                # 地理
                '地理', '地理赋分', '地理校排名', '地理市排名', '地理省排名',
                '地理赋分校排名', '地理赋分市排名', '地理赋分省排名',
                # 政治
                '政治', '政治赋分', '政治校排名', '政治市排名', '政治省排名',
                '政治赋分校排名', '政治赋分市排名', '政治赋分省排名',
                # 总分（原始+赋分）
                '总分', '总分赋分', '总分校排名', '总分市排名', '总分省排名',
                '总分赋分校排名', '总分赋分市排名', '总分赋分省排名'
            ]
        
        # 创建示例数据
        sample_data = [
            ['张三', '示例学校', '高三1班', '高三'] + [0] * (len(columns) - 4),
            ['李四', '示例学校', '高三2班', '高三'] + [0] * (len(columns) - 4)
        ]
        
        return pd.DataFrame(sample_data, columns=columns)