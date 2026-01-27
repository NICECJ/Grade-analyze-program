# 成绩分析系统 (GradeInsights)

基于 FastAPI + Vue 3 + MySQL 的成绩管理平台，支持动态 Excel 映射导入、原始文件备份，并提供学生历次联考排名波动分析。

## 技术架构

- **后端**: FastAPI (Python)
- **前端**: Vue 3 + Element Plus
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy + aiomysql
- **数据处理**: Pandas

## 功能特性

1. **动态Excel导入**: 支持任意格式Excel文件，通过UI映射字段
2. **原始文件备份**: 自动备份上传的Excel文件
3. **学生成绩分析**: 查看学生历史成绩和排名趋势
4. **排名波动预警**: 自动检测排名异常变化
5. **统计分析**: 各科排名前N学生统计

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### 2. 数据库配置

创建数据库：
```sql
CREATE DATABASE grade_insights CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `.env` 文件中的数据库连接信息：
```
DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/grade_insights
```

### 3. 后端启动

```bash
cd code
pip install -r requirements.txt
python start_backend.py
```

后端服务将在 http://localhost:8000 启动
API文档: http://localhost:8000/docs

### 4. 前端启动

```bash
cd code/frontend
npm install
npm run dev
```

前端服务将在 http://localhost:3000 启动

## 数据库设计

### 核心表结构

**exams (考试批次表)**
- id: 主键
- exam_name: 考试名称
- raw_file_path: 原始文件路径
- import_time: 导入时间

**students (学生表)**
- student_id: 学号(主键)
- name: 姓名
- school: 学校
- current_class: 班级

**grades (成绩表)**
- id: 主键
- exam_id: 考试ID(外键)
- student_id: 学号(外键)
- subject: 科目
- score: 分数
- rank_school: 校排名
- rank_city: 市排名
- rank_province: 省排名

## API接口

### 主要接口

- `POST /exams/preview` - 预览Excel文件
- `POST /exams/import` - 导入Excel数据
- `GET /students/{student_id}/history` - 获取学生历史成绩
- `GET /analysis/top-performers` - 获取排名前N学生
- `GET /analysis/rank-trend/{student_id}` - 获取学生排名趋势

## 使用说明

### 1. 数据导入

1. 在"数据导入"页面上传Excel文件
2. 系统自动解析文件列名
3. 配置字段映射关系
4. 输入考试名称并开始导入

### 2. 学生分析

1. 在"学生分析"页面输入学号
2. 选择要分析的科目
3. 查看学生信息、排名趋势图和历史成绩

### 3. 排名分析

1. 在"排名分析"页面选择科目和显示数量
2. 查看排名前N的学生列表
3. 查看学校分布统计图表

## 波动预警算法

系统会自动计算相邻两次考试的排名差：
```
ΔRank = Rank_new - Rank_old
```

当 |ΔRank| > 50 时，系统会标记为预警。

## 文件结构

```
code/
├── main.py              # FastAPI主应用
├── database.py          # 数据库配置和模型
├── models.py            # Pydantic模型
├── services.py          # 业务逻辑服务
├── requirements.txt     # Python依赖
├── .env                # 环境配置
├── start_backend.py    # 后端启动脚本
├── backups/            # Excel文件备份目录
└── frontend/           # Vue前端项目
    ├── src/
    │   ├── components/ # Vue组件
    │   ├── api/       # API接口
    │   └── main.js    # 入口文件
    └── package.json   # 前端依赖
```

## 注意事项

1. 确保MySQL服务正常运行
2. 首次启动会自动创建数据库表
3. Excel文件会自动备份到 `backups/` 目录
4. 支持的Excel格式：.xlsx, .xls
5. 学号是系统的核心关联键，确保唯一性

## 开发说明

- 后端使用异步SQLAlchemy，支持高并发
- 前端使用Element Plus组件库，界面美观
- 支持CORS跨域请求
- 使用ECharts进行数据可视化
- 支持文件上传和字段动态映射