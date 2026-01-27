from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

class ExamType(str, Enum):
    PHYSICS = "PHYSICS"
    HISTORY = "HISTORY"

class ExamLevel(str, Enum):
    SCHOOL = "SCHOOL"
    CITY = "CITY"
    PROVINCE = "PROVINCE"

class ScoreType(str, Enum):
    ORIGINAL = "ORIGINAL"
    SCALED = "SCALED"

class ExamBase(BaseModel):
    exam_name: str
    exam_date: datetime
    exam_type: ExamType
    exam_level: ExamLevel

class ExamCreate(ExamBase):
    raw_file_path: Optional[str] = None

class ExamResponse(BaseModel):
    id: int
    exam_name: str
    exam_date: datetime
    exam_type: ExamType
    exam_level: ExamLevel
    raw_file_path: Optional[str]
    import_time: datetime
    
    class Config:
        from_attributes = True

class FilePreviewResponse(BaseModel):
    columns: List[str]
    sample_data: List[Dict[str, Any]]

class ColumnMapping(BaseModel):
    excel_column: str
    system_field: str

class GradeImportRequest(BaseModel):
    exam_name: str
    exam_date: datetime
    exam_type: ExamType
    exam_level: ExamLevel
    column_mappings: List[ColumnMapping]

class StandardTemplateImportRequest(BaseModel):
    exam_name: str
    exam_date: datetime
    exam_type: ExamType
    exam_level: ExamLevel
    subject_combination: Optional[str] = None  # 选科组合，如"物化生"、"史化地"等