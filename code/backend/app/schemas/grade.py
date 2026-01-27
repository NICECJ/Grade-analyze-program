from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class GradeBase(BaseModel):
    score: Optional[Decimal] = None
    rank_school: Optional[int] = None
    rank_city: Optional[int] = None
    rank_province: Optional[int] = None

class GradeCreate(GradeBase):
    exam_id: int
    student_id: int
    subject_id: int

class GradeResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    subject_id: int
    score: Optional[Decimal]
    rank_school: Optional[int]
    rank_city: Optional[int]
    rank_province: Optional[int]
    
    # 关联数据
    exam_name: Optional[str] = None
    student_name: Optional[str] = None
    subject_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class StudentGradeHistory(BaseModel):
    student_id: int
    student_name: str
    school: str
    current_class: Optional[str]
    grades: List[Dict[str, Any]]

class ExamGradeReport(BaseModel):
    exam_id: int
    exam_name: str
    exam_date: datetime
    exam_type: Optional[str] = None
    exam_level: Optional[str] = None
    total_students: int
    subjects: List[str]
    grades: List[Dict[str, Any]]

class RankTrendPoint(BaseModel):
    exam_name: str
    exam_date: datetime
    subject_name: str
    rank_school: Optional[int]
    rank_city: Optional[int]
    rank_province: Optional[int]
    score: Optional[Decimal]