from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from sqlalchemy.orm import selectinload, joinedload
import pandas as pd
from datetime import datetime

from ..database.models import Exam, Student, Subject, Grade, ExamType, ExamLevel, ScoreType
from ..schemas.exam import GradeImportRequest, ColumnMapping, StandardTemplateImportRequest
from ..schemas.grade import StudentGradeHistory, ExamGradeReport
from .student_service import StudentService
from .template_service import TemplateService

class GradeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.student_service = StudentService(db)
        self.template_service = TemplateService()
    
    async def create_exam(self, exam_name: str, exam_date: datetime, exam_type: ExamType, 
                         exam_level: ExamLevel, raw_file_path: str) -> Exam:
        """创建考试记录"""
        exam = Exam(
            exam_name=exam_name, 
            exam_date=exam_date,
            exam_type=exam_type,
            exam_level=exam_level,
            raw_file_path=raw_file_path
        )
        self.db.add(exam)
        await self.db.commit()
        await self.db.refresh(exam)
        return exam
    
    async def get_or_create_subject(self, subject_name: str) -> Subject:
        """获取或创建科目"""
        result = await self.db.execute(
            select(Subject).where(Subject.name == subject_name)
        )
        subject = result.scalar_one_or_none()
        
        if not subject:
            subject = Subject(name=subject_name)
            self.db.add(subject)
            await self.db.commit()
            await self.db.refresh(subject)
        
        return subject
    
    async def bulk_import_grades(self, exam_id: int, df: pd.DataFrame, 
                               column_mappings: List[ColumnMapping]) -> int:
        """批量导入成绩数据"""
        # 创建映射字典
        mapping_dict = {cm.excel_column: cm.system_field for cm in column_mappings}
        
        # 重命名DataFrame列
        df_mapped = df.rename(columns=mapping_dict)
        
        imported_count = 0
        
        # 获取所有科目列（除了基本信息列）
        basic_fields = {'name', 'school', 'current_class', 'grade_level'}
        subject_columns = [col for col in df_mapped.columns 
                          if col not in basic_fields and col.endswith('_score')]
        
        for _, row in df_mapped.iterrows():
            # 处理学生信息
            if 'name' not in row or pd.isna(row['name']):
                continue
                
            student_data = {
                'name': str(row['name']),
                'school': str(row.get('school', '未知学校')),
                'current_class': str(row.get('current_class', '')) if pd.notna(row.get('current_class')) else None,
                'grade_level': str(row.get('grade_level', '')) if pd.notna(row.get('grade_level')) else None
            }
            
            # 获取或创建学生
            from ..schemas.student import StudentCreate
            student_create = StudentCreate(**student_data)
            student = await self.student_service.upsert_student(student_create)
            
            # 处理各科成绩
            for subject_col in subject_columns:
                if subject_col in row and pd.notna(row[subject_col]):
                    # 提取科目名称（去掉_score后缀）
                    subject_name = subject_col.replace('_score', '')
                    subject = await self.get_or_create_subject(subject_name)
                    
                    # 安全转换分数
                    score_value = None
                    try:
                        score_str = str(row[subject_col]).strip()
                        if score_str and score_str != '-' and score_str.lower() != 'nan':
                            score_value = float(score_str)
                    except (ValueError, TypeError):
                        score_value = None
                    
                    # 创建成绩记录
                    grade_data = {
                        'exam_id': exam_id,
                        'student_id': student.id,
                        'subject_id': subject.id,
                        'score': score_value
                    }
                    
                    # 添加排名信息（如果有的话）
                    rank_fields = ['rank_school', 'rank_city', 'rank_province']
                    for rank_field in rank_fields:
                        rank_col = f"{subject_name}_{rank_field}"
                        if rank_col in row and pd.notna(row[rank_col]):
                            try:
                                rank_str = str(row[rank_col]).strip()
                                if rank_str and rank_str != '-' and rank_str.lower() != 'nan':
                                    grade_data[rank_field] = int(float(rank_str))
                            except (ValueError, TypeError):
                                pass  # 忽略无法转换的排名数据
                    
                    grade = Grade(**grade_data)
                    self.db.add(grade)
                    imported_count += 1
        
        await self.db.commit()
        return imported_count
    
    async def get_student_grade_history(self, student_name: str, school: str) -> Optional[StudentGradeHistory]:
        """获取学生成绩历史"""
        # 获取学生信息
        student = await self.student_service.get_student_by_name_school(student_name, school)
        if not student:
            return None
        
        # 获取成绩历史
        query = text("""
            SELECT e.exam_name, e.exam_date, s.name as subject_name, 
                   g.original_score, g.scaled_score, g.rank_school, g.rank_city, g.rank_province,
                   g.scaled_rank_school, g.scaled_rank_city, g.scaled_rank_province
            FROM grades g
            JOIN exams e ON g.exam_id = e.id
            JOIN subjects s ON g.subject_id = s.id
            WHERE g.student_id = :student_id
            ORDER BY e.exam_date DESC, s.name
        """)
        
        result = await self.db.execute(query, {"student_id": student.id})
        raw_grades = [dict(row._mapping) for row in result]
        
        # 处理成绩数据，添加兼容的score字段
        grades = []
        for grade in raw_grades:
            grade_dict = dict(grade)
            # 添加兼容的score字段（优先使用原始成绩，如果没有则使用赋分成绩）
            grade_dict['score'] = grade_dict['original_score'] or grade_dict['scaled_score']
            grades.append(grade_dict)
        
        return StudentGradeHistory(
            student_id=student.id,
            student_name=student.name,
            school=student.school,
            current_class=student.current_class,
            grades=grades
        )
    
    async def get_exam_grade_report(self, exam_id: int) -> Optional[ExamGradeReport]:
        """获取考试成绩报告"""
        # 获取考试信息
        result = await self.db.execute(select(Exam).where(Exam.id == exam_id))
        exam = result.scalar_one_or_none()
        if not exam:
            return None
        
        # 获取考试成绩，包含学生的考试类型和选科组合
        query = text("""
            SELECT st.name as student_name, st.school, st.current_class,
                   st.exam_type, st.subject_combination,
                   sub.name as subject_name, 
                   g.original_score, g.scaled_score,
                   g.rank_school, g.rank_city, g.rank_province,
                   g.scaled_rank_school, g.scaled_rank_city, g.scaled_rank_province
            FROM grades g
            JOIN students st ON g.student_id = st.id
            JOIN subjects sub ON g.subject_id = sub.id
            WHERE g.exam_id = :exam_id
            ORDER BY st.name, sub.name
        """)
        
        result = await self.db.execute(query, {"exam_id": exam_id})
        raw_grades = [dict(row._mapping) for row in result]
        
        # 处理成绩数据，添加默认的score字段用于兼容
        grades = []
        for grade in raw_grades:
            grade_dict = dict(grade)
            # 添加兼容的score字段（优先使用原始成绩，如果没有则使用赋分成绩）
            grade_dict['score'] = grade_dict['original_score'] or grade_dict['scaled_score']
            grades.append(grade_dict)
        
        # 获取科目列表
        subjects = list(set(grade['subject_name'] for grade in grades))
        
        # 统计学生数量
        students = list(set(grade['student_name'] for grade in grades))
        
        return ExamGradeReport(
            exam_id=exam.id,
            exam_name=exam.exam_name,
            exam_date=exam.exam_date,
            exam_type=exam.exam_type.value if exam.exam_type else None,
            exam_level=exam.exam_level.value if exam.exam_level else None,
            total_students=len(students),
            subjects=subjects,
            grades=grades
        )
    
    async def get_previous_exam_for_comparison(self, current_exam_id: int) -> Optional[int]:
        """获取用于对比的上一次考试ID"""
        # 获取当前考试信息
        result = await self.db.execute(select(Exam).where(Exam.id == current_exam_id))
        current_exam = result.scalar_one_or_none()
        if not current_exam:
            return None
        
        # 查找同类型的上一次考试
        query = text("""
            SELECT id FROM exams 
            WHERE exam_date < :current_date 
            AND exam_type = :exam_type
            ORDER BY exam_date DESC 
            LIMIT 1
        """)
        
        result = await self.db.execute(query, {
            "current_date": current_exam.exam_date,
            "exam_type": current_exam.exam_type.value
        })
        previous_exam = result.scalar_one_or_none()
        
        return previous_exam[0] if previous_exam else None
    
    async def get_top_performers(self, subject_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取某科目排名前N的学生"""
        query = text("""
            SELECT st.name, st.school, st.current_class,
                   g.original_score, g.scaled_score, g.rank_school, g.rank_city, g.rank_province,
                   g.scaled_rank_school, g.scaled_rank_city, g.scaled_rank_province,
                   e.exam_name, e.exam_date
            FROM grades g
            JOIN students st ON g.student_id = st.id
            JOIN subjects sub ON g.subject_id = sub.id
            JOIN exams e ON g.exam_id = e.id
            WHERE sub.name = :subject_name AND g.rank_province IS NOT NULL
            ORDER BY g.rank_province ASC
            LIMIT :limit
        """)
        
        result = await self.db.execute(query, {"subject_name": subject_name, "limit": limit})
        raw_results = [dict(row._mapping) for row in result]
        
        # 处理成绩数据，添加兼容的score字段
        results = []
        for row in raw_results:
            row_dict = dict(row)
            # 添加兼容的score字段（优先使用原始成绩，如果没有则使用赋分成绩）
            row_dict['score'] = row_dict['original_score'] or row_dict['scaled_score']
            results.append(row_dict)
        
        return results
    async def import_standard_template(self, exam_name: str, exam_date: datetime, 
                                     exam_type: ExamType, exam_level: ExamLevel,
                                     df: pd.DataFrame, backup_path: str, 
                                     subject_combination: Optional[str] = None) -> Dict[str, Any]:
        """标准模板导入"""
        # 检测模板类型和列映射
        detected_type, column_mapping = self.template_service.detect_template_type(df)
        
        # 验证模板
        errors = self.template_service.validate_template(df, column_mapping)
        if errors:
            raise ValueError(f"模板验证失败: {'; '.join(errors)}")
        
        # 处理模板数据
        processed_data = self.template_service.process_template_data(df, column_mapping, subject_combination)
        
        # 创建考试记录
        exam = await self.create_exam(exam_name, exam_date, exam_type, exam_level, backup_path)
        
        # 导入学生和成绩数据
        imported_count = await self._import_processed_data(exam.id, processed_data)
        
        return {
            "exam_id": exam.id,
            "detected_type": detected_type.value,
            "imported_students": len(processed_data['students']),
            "imported_grades": imported_count,
            "column_mapping": column_mapping,
            "subject_combination": subject_combination
        }
    
    async def _import_processed_data(self, exam_id: int, processed_data: Dict) -> int:
        """导入处理后的数据"""
        imported_count = 0
        student_cache = {}  # 缓存学生信息，避免重复查询
        
        # 按学生分组处理成绩
        grades_by_student = {}
        for grade in processed_data['grades']:
            student_key = grade['student_key']
            if student_key not in grades_by_student:
                grades_by_student[student_key] = []
            grades_by_student[student_key].append(grade)
        
        # 处理每个学生的数据
        for student_info in processed_data['students']:
            student_key = f"{student_info['school']}_{student_info['current_class']}_{student_info['name']}"
            
            # 获取或创建学生
            if student_key not in student_cache:
                from ..schemas.student import StudentCreate
                student_create = StudentCreate(**student_info)
                student = await self.student_service.upsert_student_by_class_name(student_create)
                student_cache[student_key] = student
            else:
                student = student_cache[student_key]
            
            # 处理该学生的成绩
            if student_key in grades_by_student:
                for grade_info in grades_by_student[student_key]:
                    # 获取或创建科目
                    subject = await self.get_or_create_subject(grade_info['subject_name'])
                    
                    # 创建成绩记录
                    grade_data = {
                        'exam_id': exam_id,
                        'student_id': student.id,
                        'subject_id': subject.id,
                        # 原始排名
                        'rank_school': grade_info.get('rank_school'),
                        'rank_city': grade_info.get('rank_city'),
                        'rank_province': grade_info.get('rank_province'),
                        # 赋分排名
                        'scaled_rank_school': grade_info.get('scaled_rank_school'),
                        'scaled_rank_city': grade_info.get('scaled_rank_city'),
                        'scaled_rank_province': grade_info.get('scaled_rank_province')
                    }
                    
                    # 根据成绩类型设置分数
                    if grade_info.get('score_type') == 'scaled':
                        grade_data['scaled_score'] = grade_info['score']
                    else:
                        grade_data['original_score'] = grade_info['score']
                    
                    grade = Grade(**grade_data)
                    self.db.add(grade)
                    imported_count += 1
        
        await self.db.commit()
        return imported_count
    
    async def get_ranking_by_type(self, exam_type: ExamType, subject_name: str, 
                                 score_type: ScoreType = ScoreType.ORIGINAL,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """按考试类型获取排名"""
        if score_type == ScoreType.SCALED:
            score_field = "g.scaled_score"
            rank_field = "g.scaled_rank_province"
        else:
            score_field = "g.original_score"
            rank_field = "g.rank_province"
        
        query = text(f"""
            SELECT st.name, st.school, st.current_class, st.exam_type,
                   {score_field} as score, 
                   g.rank_school, g.rank_city, g.rank_province,
                   g.scaled_rank_school, g.scaled_rank_city, g.scaled_rank_province,
                   e.exam_name, e.exam_date
            FROM grades g
            JOIN students st ON g.student_id = st.id
            JOIN subjects sub ON g.subject_id = sub.id
            JOIN exams e ON g.exam_id = e.id
            WHERE sub.name = :subject_name 
            AND (st.exam_type = :exam_type OR st.exam_type IS NULL)
            AND {score_field} IS NOT NULL
            ORDER BY {rank_field} ASC, {score_field} DESC
            LIMIT :limit
        """)
        
        result = await self.db.execute(query, {
            "subject_name": subject_name,
            "exam_type": exam_type.value,
            "limit": limit
        })
        return [dict(row._mapping) for row in result]
    
    async def get_subject_combination_ranking(self, main_subject: str, elective_subjects: List[str],
                                            exam_level: ExamLevel, limit: int = 50) -> List[Dict[str, Any]]:
        """获取选课组合排名"""
        # 构建科目列表
        all_subjects = ['语文', '数学', '英语', main_subject] + elective_subjects + ['总分']
        subjects_str = "', '".join(all_subjects)
        
        query = text(f"""
            SELECT st.name, st.school, st.current_class,
                   GROUP_CONCAT(
                       CONCAT(sub.name, ':', 
                              COALESCE(g.scaled_score, g.original_score)
                       ) ORDER BY sub.name
                   ) as scores,
                   SUM(CASE WHEN sub.name = '总分' THEN COALESCE(g.scaled_score, g.original_score) ELSE 0 END) as total_score,
                   MIN(CASE WHEN sub.name = '总分' THEN COALESCE(g.scaled_rank_province, g.rank_province) ELSE NULL END) as total_rank
            FROM grades g
            JOIN students st ON g.student_id = st.id
            JOIN subjects sub ON g.subject_id = sub.id
            JOIN exams e ON g.exam_id = e.id
            WHERE sub.name IN ('{subjects_str}')
            AND e.exam_level = :exam_level
            AND (g.original_score IS NOT NULL OR g.scaled_score IS NOT NULL)
            GROUP BY st.id, st.name, st.school, st.current_class
            HAVING COUNT(DISTINCT sub.name) = :subject_count
            ORDER BY total_score DESC
            LIMIT :limit
        """)
        
        result = await self.db.execute(query, {
            "exam_level": exam_level.value,
            "subject_count": len(all_subjects),
            "limit": limit
        })
        return [dict(row._mapping) for row in result]