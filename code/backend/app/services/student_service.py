from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, delete
from sqlalchemy.orm import selectinload

from ..database.models import Student, ExamType
from ..schemas.student import StudentCreate, StudentResponse, StudentUpdate

class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_student(self, student_data: StudentCreate) -> Student:
        """创建学生"""
        student = Student(**student_data.dict())
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student
    
    async def get_student_by_name_school(self, name: str, school: str) -> Optional[Student]:
        """根据姓名和学校查找学生"""
        result = await self.db.execute(
            select(Student).where(
                and_(Student.name == name, Student.school == school)
            )
        )
        return result.scalar_one_or_none()
    
    async def upsert_student(self, student_data: StudentCreate) -> Student:
        """插入或更新学生信息"""
        existing_student = await self.get_student_by_name_school(
            student_data.name, student_data.school
        )
        
        if existing_student:
            # 更新现有学生信息
            for key, value in student_data.dict().items():
                if value is not None:
                    setattr(existing_student, key, value)
            student = existing_student
        else:
            # 创建新学生
            student = Student(**student_data.dict())
            self.db.add(student)
        
        await self.db.commit()
        await self.db.refresh(student)
        return student
    
    async def bulk_import_students(self, students_data: List[StudentCreate]) -> int:
        """批量导入学生"""
        imported_count = 0
        
        for student_data in students_data:
            await self.upsert_student(student_data)
            imported_count += 1
        
        return imported_count
    
    async def get_students_by_school(self, school: str) -> List[Student]:
        """获取某学校的所有学生"""
        result = await self.db.execute(
            select(Student).where(Student.school == school)
        )
        return result.scalars().all()
    
    async def search_students_paginated(self, name: Optional[str] = None, 
                                   school: Optional[str] = None,
                                   current_class: Optional[str] = None,
                                   exam_type: Optional[str] = None,
                                   page: int = 1, size: int = 20) -> Dict[str, Any]:
        """分页搜索学生"""
        query = select(Student)
        
        conditions = []
        if name:
            conditions.append(Student.name.like(f"%{name}%"))
        if school:
            conditions.append(Student.school.like(f"%{school}%"))
        if current_class:
            conditions.append(Student.current_class == current_class)
        if exam_type:
            try:
                exam_type_enum = ExamType(exam_type)
                conditions.append(Student.exam_type == exam_type_enum)
            except ValueError:
                pass  # 忽略无效的exam_type值
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 获取总数
        count_query = select(func.count(Student.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 分页查询
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(Student.id)
        
        result = await self.db.execute(query)
        students = result.scalars().all()
        
        return {
            "students": students,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    async def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """根据ID获取学生"""
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()

    async def update_student(self, student_id: int, student_update: StudentUpdate) -> Optional[Student]:
        """更新学生信息"""
        student = await self.get_student_by_id(student_id)
        if not student:
            return None
        
        # 更新字段
        update_data = student_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(student, key, value)
        
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def delete_student(self, student_id: int) -> bool:
        """删除学生及其所有成绩记录"""
        student = await self.get_student_by_id(student_id)
        if not student:
            return False
        
        try:
            # 删除相关成绩记录
            from ..database.models import Grade
            await self.db.execute(delete(Grade).where(Grade.student_id == student_id))
            
            # 删除学生记录
            await self.db.execute(delete(Student).where(Student.id == student_id))
            
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_student_by_class_name(self, school: str, current_class: str, name: str) -> Optional[Student]:
        """根据学校、班级、姓名查找学生"""
        result = await self.db.execute(
            select(Student).where(
                and_(
                    Student.school == school,
                    Student.current_class == current_class,
                    Student.name == name
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def upsert_student_by_class_name(self, student_data: StudentCreate) -> Student:
        """按班级+姓名插入或更新学生信息"""
        existing_student = await self.get_student_by_class_name(
            student_data.school, student_data.current_class, student_data.name
        )
        
        if existing_student:
            # 更新现有学生信息
            for key, value in student_data.dict().items():
                if value is not None:
                    setattr(existing_student, key, value)
            student = existing_student
        else:
            # 创建新学生
            student = Student(**student_data.dict())
            self.db.add(student)
        
        await self.db.commit()
        await self.db.refresh(student)
        return student