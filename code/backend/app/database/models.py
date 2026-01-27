from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, BigInteger, ForeignKey, Text, Enum, Boolean
from sqlalchemy.sql import func
import enum

# 枚举定义
class ExamType(enum.Enum):
    PHYSICS = "PHYSICS"
    HISTORY = "HISTORY"

class ExamLevel(enum.Enum):
    SCHOOL = "SCHOOL"
    CITY = "CITY" 
    PROVINCE = "PROVINCE"

class ScoreType(enum.Enum):
    ORIGINAL = "ORIGINAL"
    SCALED = "SCALED"
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_name = Column(String(100), nullable=False)
    exam_date = Column(DateTime, nullable=False)
    exam_type = Column(Enum(ExamType), nullable=False)  # 物理类/历史类
    exam_level = Column(Enum(ExamLevel), nullable=False)  # 校级/市级/省级
    raw_file_path = Column(String(255))
    import_time = Column(DateTime, default=func.now())
    
    # 关系
    grades = relationship("Grade", back_populates="exam")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    school = Column(String(100), nullable=False)
    current_class = Column(String(50), nullable=False)  # 班级作为主码的一部分
    grade_level = Column(String(20))  # 年级：高一、高二、高三
    exam_type = Column(Enum(ExamType))  # 学生的考试类型：物理类/历史类
    subject_combination = Column(String(50))  # 选科组合：物化生、史化地等
    
    # 关系
    grades = relationship("Grade", back_populates="student")
    
    # 复合唯一约束：同一学校内班级+姓名唯一
    __table_args__ = (
        {'mysql_charset': 'utf8mb4'},
    )

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)  # 语文、数学、英语等
    category = Column(String(20))  # 必修、选修
    is_scalable = Column(Boolean, default=False)  # 是否需要赋分（四选二科目）
    
    # 关系
    grades = relationship("Grade", back_populates="subject")

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    
    # 原始成绩和排名
    original_score = Column(DECIMAL(5, 2))  # 原始成绩
    rank_school = Column(Integer)           # 原始成绩校排名
    rank_city = Column(Integer)             # 原始成绩市排名
    rank_province = Column(Integer)         # 原始成绩省排名
    
    # 赋分成绩和排名（适用于选考科目和总分）
    scaled_score = Column(DECIMAL(5, 2))    # 赋分成绩
    scaled_rank_school = Column(Integer)    # 赋分成绩校排名
    scaled_rank_city = Column(Integer)      # 赋分成绩市排名
    scaled_rank_province = Column(Integer)  # 赋分成绩省排名
    
    # 关系
    exam = relationship("Exam", back_populates="grades")
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    
    @property
    def score(self):
        """默认返回原始成绩，如果没有则返回赋分成绩"""
        return self.original_score or self.scaled_score
    
    def get_score(self, score_type: ScoreType):
        """根据成绩类型返回对应分数"""
        if score_type == ScoreType.SCALED:
            return self.scaled_score or self.original_score
        return self.original_score or self.scaled_score
    
    def get_rank(self, rank_level: str, score_type: ScoreType):
        """根据排名级别和成绩类型返回对应排名"""
        if score_type == ScoreType.SCALED:
            if rank_level == 'school':
                return self.scaled_rank_school or self.rank_school
            elif rank_level == 'city':
                return self.scaled_rank_city or self.rank_city
            elif rank_level == 'province':
                return self.scaled_rank_province or self.rank_province
        else:
            if rank_level == 'school':
                return self.rank_school
            elif rank_level == 'city':
                return self.rank_city
            elif rank_level == 'province':
                return self.rank_province
        return None

class SubjectCombination(Base):
    __tablename__ = "subject_combinations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exam_type = Column(Enum(ExamType), nullable=False)  # 物理类/历史类
    main_subject = Column(String(20), nullable=False)   # 物理 或 历史
    elective_subjects = Column(String(100))  # 选考科目，逗号分隔，如"生物,化学"
    
    # 关系
    student = relationship("Student")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)