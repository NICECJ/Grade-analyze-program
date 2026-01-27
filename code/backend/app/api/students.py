from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import tempfile
import os
import pandas as pd

from ..database import get_db
from ..schemas.student import StudentCreate, StudentResponse, StudentImportRequest, StudentUpdate
from ..services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/import", response_model=dict)
async def import_students(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """批量导入学生信息"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件格式")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # 读取Excel文件
        df = pd.read_excel(tmp_file_path)
        
        # 处理学生数据
        students_data = []
        for _, row in df.iterrows():
            if pd.notna(row.get('姓名')) or pd.notna(row.get('name')):
                student_data = StudentCreate(
                    name=str(row.get('姓名') or row.get('name')),
                    school=str(row.get('学校') or row.get('school', '未知学校')),
                    current_class=str(row.get('班级') or row.get('class', '')) if pd.notna(row.get('班级') or row.get('class')) else None,
                    grade_level=str(row.get('年级') or row.get('grade', '')) if pd.notna(row.get('年级') or row.get('grade')) else None
                )
                students_data.append(student_data)
        
        # 批量导入
        student_service = StudentService(db)
        imported_count = await student_service.bulk_import_students(students_data)
        
        return {
            "message": "学生信息导入成功",
            "imported_count": imported_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
    finally:
        os.unlink(tmp_file_path)

@router.get("/search")
async def search_students(
    name: Optional[str] = Query(None, description="学生姓名"),
    school: Optional[str] = Query(None, description="学校名称"),
    current_class: Optional[str] = Query(None, description="班级"),
    exam_type: Optional[str] = Query(None, description="考试类型"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """搜索学生（支持分页）"""
    student_service = StudentService(db)
    result = await student_service.search_students_paginated(
        name=name, 
        school=school, 
        current_class=current_class,
        exam_type=exam_type,
        page=page, 
        size=size
    )
    return result

@router.get("/school/{school}", response_model=List[StudentResponse])
async def get_students_by_school(school: str, db: AsyncSession = Depends(get_db)):
    """获取某学校的所有学生"""
    student_service = StudentService(db)
    students = await student_service.get_students_by_school(school)
    return students

@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    """创建学生"""
    student_service = StudentService(db)
    return await student_service.create_student(student)

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    """获取学生详情"""
    student_service = StudentService(db)
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int, 
    student_update: StudentUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新学生信息"""
    student_service = StudentService(db)
    student = await student_service.update_student(student_id, student_update)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@router.delete("/{student_id}")
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    """删除学生及其所有成绩记录"""
    student_service = StudentService(db)
    success = await student_service.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="学生不存在")
    return {"message": "学生删除成功", "student_id": student_id}