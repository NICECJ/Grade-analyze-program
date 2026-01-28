# 成绩分析系统 (Grade Analysis System)

一个基于Vue 3 + FastAPI的高中成绩分析管理系统，专为新高考模式设计。

## 功能特性

### 📊 成绩管理
- **Excel批量导入**：支持自定义列映射的Excel文件导入
- **标准模板导入**：支持新高考模式的标准化成绩模板
- **手工录入**：支持单个学生成绩的手动录入
- **成绩分析**：详细的考试成绩分析和可视化展示

### 👥 学生管理
- **学生信息管理**：支持学生基本信息的增删改查
- **选科组合**：支持物理类/历史类及各种选科组合
- **批量导入**：支持Excel批量导入学生信息

### 📈 数据分析
- **排名分析**：支持校级、市级、省级排名统计
- **趋势分析**：学生成绩变化趋势和排名波动分析
- **成绩分布**：直观的成绩分布图表展示
- **对比分析**：支持考试间的成绩对比

### 🎯 新高考支持
- **考试类型**：物理类/历史类分类管理
- **选科组合**：支持3+1+2模式的所有选科组合
- **赋分制度**：支持原始分和赋分成绩的双重记录
- **等级考试**：支持校级、市级、省级考试管理

## 技术栈

### 前端
- **Vue 3**：现代化的前端框架
- **Element Plus**：UI组件库
- **Vue Router**：路由管理
- **ECharts**：数据可视化
- **Vite**：构建工具

### 后端
- **FastAPI**：高性能Python Web框架
- **SQLAlchemy**：ORM数据库操作
- **MySQL/MariaDB**：数据库
- **Pandas**：数据处理
- **Pydantic**：数据验证

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+ 或 MariaDB 10.3+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/NICECJ/Grade-analyze-program.git
cd Grade-analyze-program
```

2. **后端设置**
```bash
cd code
# 创建虚拟环境
python -m venv venv
# 激活虚拟环境 (Windows)
venv\Scripts\activate
# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate
# 安装依赖
pip install -r requirements.txt
```

3. **数据库配置**
```bash
# 复制环境配置文件
cp .env.example .env
# 编辑 .env 文件，配置数据库连接信息
# 初始化数据库
python init_db_v2.py
```

4. **前端设置**
```bash
cd frontend
npm install
```

5. **启动服务**
```bash
# 启动后端 (在 code 目录下)
python start_backend.py

# 启动前端 (在 code/frontend 目录下，新开一个终端)
npm run dev
```

6. **访问系统**
- 前端地址：http://localhost:5173
- 后端API文档：http://localhost:8000/docs

## 项目结构

```
Grade-analyze-program/
├── code/                          # 主要代码目录
│   ├── backend/                   # 后端代码
│   │   ├── app/                   # FastAPI应用
│   │   │   ├── api/              # API路由
│   │   │   ├── database/         # 数据库模型
│   │   │   ├── schemas/          # Pydantic模型
│   │   │   └── services/         # 业务逻辑
│   │   └── main.py               # 应用入口
│   ├── frontend/                  # 前端代码
│   │   ├── src/                  # Vue源码
│   │   │   ├── components/       # Vue组件
│   │   │   └── api.js           # API封装
│   │   └── package.json          # 前端依赖
│   ├── backups/                   # 数据备份
│   ├── templates/                 # Excel模板
│   ├── .env.example              # 环境配置示例
│   ├── requirements.txt          # Python依赖
│   └── start_backend.py          # 后端启动脚本
├── data/                          # 示例数据
└── README.md                      # 项目说明
```

## 使用说明

### 1. 学生信息管理
- 进入"学生管理"模块
- 支持Excel批量导入或手动添加学生信息
- 可设置学生的考试类型和选科组合

### 2. 成绩导入
- **标准模板导入**：下载标准模板，按格式填写后导入
- **自定义导入**：上传Excel文件，自定义列映射关系
- **手工录入**：单个学生成绩的详细录入

### 3. 成绩分析
- 选择考试查看详细的成绩分析
- 支持按考试类型筛选
- 查看成绩分布和排名统计

### 4. 数据导出
- 支持成绩数据的Excel导出
- 支持排名数据的导出

## 数据库设计

### 主要数据表
- **exams**：考试信息表
- **students**：学生信息表
- **subjects**：科目信息表
- **grades**：成绩记录表
- **subject_combinations**：选科组合表

### 关键字段
- 支持原始分和赋分成绩
- 支持校级、市级、省级排名
- 支持考试类型和选科组合

## 服务器部署

### Windows服务器
1. 安装Python 3.8+、Node.js 16+、MySQL
2. 按照上述安装步骤配置项目
3. 使用PM2或Windows服务实现后台运行

### Linux服务器
1. 安装Python 3.8+、Node.js 16+、MySQL
2. 按照上述安装步骤配置项目
3. 使用systemd或PM2实现后台运行

### 后台运行（可选）
使用PM2管理进程：
```bash
# 安装PM2
npm install -g pm2

# 启动后端
pm2 start "python start_backend.py" --name "grade-backend"

# 启动前端
pm2 start "npm run dev" --name "grade-frontend"

# 保存配置
pm2 save
pm2 startup
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目地址：https://github.com/NICECJ/Grade-analyze-program
- 问题反馈：https://github.com/NICECJ/Grade-analyze-program/issues

## 更新日志

### v1.0.0 (2026-01-28)
- 初始版本发布
- 支持新高考模式的成绩管理
- 完整的前后端分离架构
- 支持多种成绩导入方式
- 丰富的数据分析功能