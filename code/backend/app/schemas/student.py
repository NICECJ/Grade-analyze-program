from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .exam import ExamType

class StudentBase(BaseModel):
    name: str
    school: str
    current_class: str  # 班级必填，作为主码的一部分
    grade_level: Optional[str] = None
    exam_type: Optional[ExamType] = None  # 物理类/历史类
    subject_combination: Optional[str] = None  # 选科组合：物化生、史化地等

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    name: Optional[str] = None
    school: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    school: str
    current_class: str
    grade_level: Optional[str]
    exam_type: Optional[ExamType]
    subject_combination: Optional[str]
    
    class Config:
        from_attributes = True

class StudentImportRequest(BaseModel):
    students: List[StudentCreate]