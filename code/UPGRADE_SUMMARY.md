# 成绩分析系统 v2.0 升级总结

## 主要改进

### 1. 数据模型重构
- **去除学号依赖**：改用姓名+学校作为学生唯一标识
- **多科目支持**：支持同时导入多个科目的成绩
- **规范化设计**：分离学生、考试、科目、成绩四个实体
- **关系优化**：使用外键建立正确的数据关系

### 2. 后端架构重组
```
code/backend/
├── app/
│   ├── __init__.py
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── students.py      # 学生相关API
│   │   ├── exams.py         # 考试相关API
│   │   └── grades.py        # 成绩相关API
│   ├── database/            # 数据库模型
│   │   ├── __init__.py
│   │   └── models.py
│   ├── schemas/             # Pydantic模型
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── exam.py
│   │   └── grade.py
│   └── services/            # 业务逻辑
│       ├── __init__.py
│       ├── student_service.py
│       ├── grade_service.py
│       └── excel_service.py
└── main.py                  # 应用入口
```

### 3. 功能模块分离

#### 学生管理模块
- **批量导入学生信息**：支持Excel批量导入学生基本信息
- **学生搜索**：按姓名、学校、班级搜索学生
- **学生信息管理**：查看和管理学生基本信息

#### 成绩导入模块
- **智能字段识别**：自动识别Excel中的学生信息和成绩字段
- **多科目映射**：支持同时映射多个科目的成绩和排名
- **灵活配置**：用户可自定义字段映射关系

#### 分析模块分离
- **学生分析**：个人成绩历史和趋势分析
- **考试分析**：整场考试的统计分析和可视化
- **排名分析**：各科目排名统计

### 4. 前端功能增强

#### 新增页面
- **学生导入页面**：专门的学生信息批量导入
- **成绩导入页面**：改进的成绩导入流程，支持多科目
- **考试分析页面**：以考试为单位的分析视图

#### 改进功能
- **智能字段映射**：自动建议字段映射关系
- **多科目支持**：一次导入多个科目的成绩
- **更好的可视化**：成绩分布图、学校分布图等

### 5. 数据库表结构

#### 新表结构
```sql
-- 考试表
CREATE TABLE exams (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exam_name VARCHAR(100) NOT NULL,
    exam_date DATETIME NOT NULL,
    raw_file_path VARCHAR(255),
    import_time DATETIME DEFAULT NOW()
);

-- 学生表
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    school VARCHAR(100) NOT NULL,
    current_class VARCHAR(50),
    grade_level VARCHAR(20)
);

-- 科目表
CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE,
    category VARCHAR(20)
);

-- 成绩表
CREATE TABLE grades (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    score DECIMAL(5,2),
    rank_school INT,
    rank_city INT,
    rank_province INT,
    FOREIGN KEY (exam_id) REFERENCES exams(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);
```

### 6. API接口重构

#### 学生相关API
- `POST /api/students/import` - 批量导入学生
- `GET /api/students/search` - 搜索学生
- `GET /api/students/school/{school}` - 获取学校学生

#### 考试相关API
- `POST /api/exams/preview` - 预览Excel文件
- `POST /api/exams/import-grades` - 导入成绩数据
- `GET /api/exams/{exam_id}/report` - 获取考试报告

#### 成绩相关API
- `GET /api/grades/student-history` - 获取学生成绩历史
- `GET /api/grades/top-performers` - 获取排名前N学生
- `GET /api/grades/rank-trend` - 获取排名趋势

## 使用说明

### 1. 启动系统
```bash
# 初始化数据库
python init_db_v2.py

# 启动后端
python start_backend.py

# 启动前端
cd frontend
npm run dev
```

### 2. 使用流程
1. **导入学生信息**：在"学生导入"页面批量导入学生基本信息
2. **导入成绩数据**：在"成绩导入"页面导入考试成绩，支持多科目
3. **查看分析**：
   - 学生分析：查看个人成绩趋势
   - 考试分析：查看整场考试统计
   - 排名分析：查看各科排名情况

### 3. Excel文件格式要求

#### 学生信息文件
| 姓名 | 学校 | 班级 | 年级 |
|------|------|------|------|
| 张三 | 一中 | 高三1班 | 高三 |

#### 成绩文件
| 姓名 | 学校 | 班级 | 语文 | 数学 | 英语 | 语文校排名 | 数学校排名 | ... |
|------|------|------|------|------|------|-----------|-----------|-----|
| 张三 | 一中 | 高三1班 | 120 | 135 | 110 | 15 | 8 | ... |

## 技术改进

1. **代码组织**：采用标准的FastAPI项目结构
2. **类型安全**：使用Pydantic进行数据验证
3. **异步支持**：全面使用异步数据库操作
4. **错误处理**：完善的错误处理和用户反馈
5. **可扩展性**：模块化设计，易于扩展新功能

## 兼容性说明

- 新版本与旧版本数据库不兼容，需要重新导入数据
- 前端界面完全重新设计，提供更好的用户体验
- API接口有重大变更，如有第三方集成需要更新