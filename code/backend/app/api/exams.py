from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import tempfile
import os
import pandas as pd
from datetime import datetime

from ..database import get_db, Exam
from ..schemas.exam import ExamResponse, FilePreviewResponse, GradeImportRequest, StandardTemplateImportRequest, ExamType, ExamLevel
from ..services.excel_service import ExcelService
from ..services.grade_service import GradeService

router = APIRouter(prefix="/exams", tags=["exams"])

excel_service = ExcelService()

@router.post("/preview", response_model=FilePreviewResponse)
async def preview_excel_file(file: UploadFile = File(...)):
    """预览Excel文件，返回列名和样本数据"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件格式")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        preview_data = excel_service.preview_excel(tmp_file_path)
        
        # 检测成绩表结构
        df = pd.read_excel(tmp_file_path)
        structure = excel_service.detect_grade_structure(df)
        
        return {
            **preview_data,
            "structure": structure
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.unlink(tmp_file_path)

@router.post("/import-grades")
async def import_grade_data(
    file: UploadFile = File(...),
    import_data: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """导入成绩数据到数据库"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件格式")
    
    try:
        # 解析导入配置
        import_request = GradeImportRequest.parse_raw(import_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"导入配置解析失败: {str(e)}")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # 备份原始文件
        backup_path = excel_service.backup_file(tmp_file_path, import_request.exam_name)
        
        # 创建考试记录
        grade_service = GradeService(db)
        exam = await grade_service.create_exam(
            import_request.exam_name, 
            import_request.exam_date,
            import_request.exam_type,
            import_request.exam_level,
            backup_path
        )
        
        # 读取Excel数据
        df = pd.read_excel(tmp_file_path)
        
        # 批量导入数据
        imported_count = await grade_service.bulk_import_grades(
            exam.id, df, import_request.column_mappings
        )
        
        return {
            "message": "成绩导入成功",
            "exam_id": exam.id,
            "imported_records": imported_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
    finally:
        os.unlink(tmp_file_path)

@router.get("/", response_model=List[ExamResponse])
async def get_exams(db: AsyncSession = Depends(get_db)):
    """获取所有考试列表"""
    from sqlalchemy import select
    result = await db.execute(select(Exam).order_by(Exam.exam_date.desc()))
    exams = result.scalars().all()
    return exams

@router.get("/{exam_id}/report")
async def get_exam_report(exam_id: int, db: AsyncSession = Depends(get_db)):
    """获取考试成绩报告"""
    grade_service = GradeService(db)
    report = await grade_service.get_exam_grade_report(exam_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    return report

@router.get("/{exam_id}/previous")
async def get_previous_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    """获取上一次考试ID用于对比"""
    grade_service = GradeService(db)
    previous_exam_id = await grade_service.get_previous_exam_for_comparison(exam_id)
    
    if not previous_exam_id:
        return {"previous_exam_id": None}
    
    return {"previous_exam_id": previous_exam_id}

@router.delete("/{exam_id}")
async def delete_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    """删除考试及其相关数据"""
    from sqlalchemy import select, delete
    
    # 检查考试是否存在
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    try:
        # 删除相关成绩数据
        from ..database.models import Grade
        await db.execute(delete(Grade).where(Grade.exam_id == exam_id))
        
        # 删除考试记录
        await db.execute(delete(Exam).where(Exam.id == exam_id))
        
        await db.commit()
        
        return {"message": "考试删除成功", "exam_id": exam_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
@router.post("/import-standard-template")
async def import_standard_template(
    file: UploadFile = File(...),
    import_data: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """标准模板导入成绩数据"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件格式")
    
    try:
        # 解析导入配置
        import_request = StandardTemplateImportRequest.parse_raw(import_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"导入配置解析失败: {str(e)}")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # 备份原始文件
        backup_path = excel_service.backup_file(tmp_file_path, import_request.exam_name)
        
        # 读取Excel数据
        df = pd.read_excel(tmp_file_path)
        print(f"Excel columns: {df.columns.tolist()}")  # 调试信息
        print(f"Excel shape: {df.shape}")  # 调试信息
        
        # 使用标准模板导入
        grade_service = GradeService(db)
        result = await grade_service.import_standard_template(
            import_request.exam_name,
            import_request.exam_date,
            import_request.exam_type,
            import_request.exam_level,
            df,
            backup_path,
            import_request.subject_combination
        )
        
        return {
            "message": "标准模板导入成功",
            **result
        }
    
    except Exception as e:
        import traceback
        print(f"Import error: {str(e)}")  # 调试信息
        print(f"Traceback: {traceback.format_exc()}")  # 调试信息
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
    finally:
        os.unlink(tmp_file_path)

@router.get("/template-example/{exam_type}")
async def get_template_example(exam_type: ExamType):
    """获取标准模板示例"""
    from ..services.template_service import TemplateService
    template_service = TemplateService()
    
    try:
        example_df = template_service.generate_template_example(exam_type)
        
        # 转换为JSON格式返回
        return {
            "exam_type": exam_type.value,
            "columns": example_df.columns.tolist(),
            "sample_data": example_df.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成模板示例失败: {str(e)}")

@router.get("/ranking/{exam_type}/{subject}")
async def get_ranking_by_type(
    exam_type: ExamType,
    subject: str,
    score_type: str = "original",
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """按考试类型获取排名"""
    from ..schemas.exam import ScoreType
    
    try:
        score_type_enum = ScoreType.ORIGINAL if score_type == "original" else ScoreType.SCALED
        grade_service = GradeService(db)
        
        ranking = await grade_service.get_ranking_by_type(
            exam_type, subject, score_type_enum, limit
        )
        
        return {
            "exam_type": exam_type.value,
            "subject": subject,
            "score_type": score_type,
            "ranking": ranking
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取排名失败: {str(e)}")

@router.get("/combination-ranking")
async def get_combination_ranking(
    main_subject: str,
    elective_subjects: str,  # 逗号分隔的选考科目
    exam_level: ExamLevel,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """获取选课组合排名"""
    try:
        elective_list = [s.strip() for s in elective_subjects.split(',') if s.strip()]
        
        grade_service = GradeService(db)
        ranking = await grade_service.get_subject_combination_ranking(
            main_subject, elective_list, exam_level, limit
        )
        
        return {
            "main_subject": main_subject,
            "elective_subjects": elective_list,
            "exam_level": exam_level.value,
            "ranking": ranking
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取选课组合排名失败: {str(e)}")

@router.post("/create")
async def create_exam(
    exam_name: str = Form(...),
    exam_date: str = Form(...),
    exam_type: ExamType = Form(...),
    exam_level: ExamLevel = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """创建新考试"""
    try:
        from datetime import datetime
        exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d')
        
        grade_service = GradeService(db)
        exam = await grade_service.create_exam(
            exam_name, exam_date_obj, exam_type, exam_level, ""
        )
        
        return {
            "id": exam.id,
            "exam_name": exam.exam_name,
            "exam_date": exam.exam_date,
            "exam_type": exam.exam_type.value,
            "exam_level": exam.exam_level.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建考试失败: {str(e)}")