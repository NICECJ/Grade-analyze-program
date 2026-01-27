from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..services.grade_service import GradeService
from ..services.student_service import StudentService
from ..schemas.student import StudentCreate

router = APIRouter(prefix="/grades", tags=["grades"])

class ManualGradeData(BaseModel):
    subject_name: str
    original_score: float = None
    scaled_score: float = None
    rank_province: int = None
    scaled_rank_province: int = None

class ManualGradeImportRequest(BaseModel):
    exam_id: int
    student: Dict[str, Any]
    grades: List[ManualGradeData]

@router.post("/manual-import")
async def manual_import_grades(
    request: ManualGradeImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """手工导入单个学生的成绩"""
    try:
        grade_service = GradeService(db)
        student_service = StudentService(db)
        
        # 创建或更新学生信息
        student_create = StudentCreate(**request.student)
        student = await student_service.upsert_student_by_class_name(student_create)
        
        # 导入成绩
        imported_count = 0
        for grade_data in request.grades:
            # 获取或创建科目
            subject = await grade_service.get_or_create_subject(grade_data.subject_name)
            
            # 检查是否已存在该学生在该考试中的该科目成绩
            from sqlalchemy import select, and_
            from ..database.models import Grade
            
            existing_grade_result = await db.execute(
                select(Grade).where(
                    and_(
                        Grade.exam_id == request.exam_id,
                        Grade.student_id == student.id,
                        Grade.subject_id == subject.id
                    )
                )
            )
            existing_grade = existing_grade_result.scalar_one_or_none()
            
            if existing_grade:
                # 更新现有成绩
                existing_grade.original_score = grade_data.original_score
                existing_grade.scaled_score = grade_data.scaled_score
                existing_grade.rank_province = grade_data.rank_province
                existing_grade.scaled_rank_province = grade_data.scaled_rank_province
            else:
                # 创建新成绩记录
                new_grade = Grade(
                    exam_id=request.exam_id,
                    student_id=student.id,
                    subject_id=subject.id,
                    original_score=grade_data.original_score,
                    scaled_score=grade_data.scaled_score,
                    rank_province=grade_data.rank_province,
                    scaled_rank_province=grade_data.scaled_rank_province
                )
                db.add(new_grade)
            
            imported_count += 1
        
        await db.commit()
        
        return {
            "message": "成绩录入成功",
            "student_name": student.name,
            "imported_grades": imported_count
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"成绩录入失败: {str(e)}")

@router.get("/student/{student_id}/history")
async def get_student_grade_history(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取学生成绩历史"""
    try:
        grade_service = GradeService(db)
        
        # 通过学生ID获取成绩历史
        from sqlalchemy import select, text
        query = text("""
            SELECT st.name, st.school, st.current_class,
                   e.exam_name, e.exam_date, s.name as subject_name, 
                   g.original_score, g.scaled_score, g.rank_school, g.rank_city, g.rank_province,
                   g.scaled_rank_school, g.scaled_rank_city, g.scaled_rank_province
            FROM grades g
            JOIN exams e ON g.exam_id = e.id
            JOIN subjects s ON g.subject_id = s.id
            JOIN students st ON g.student_id = st.id
            WHERE g.student_id = :student_id
            ORDER BY e.exam_date DESC, s.name
        """)
        
        result = await db.execute(query, {"student_id": student_id})
        grades = [dict(row._mapping) for row in result]
        
        if not grades:
            raise HTTPException(status_code=404, detail="未找到学生成绩记录")
        
        return {
            "student_id": student_id,
            "student_name": grades[0]['name'],
            "school": grades[0]['school'],
            "current_class": grades[0]['current_class'],
            "grades": grades
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学生成绩历史失败: {str(e)}")