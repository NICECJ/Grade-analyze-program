import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 学生相关API
  students: {
    // 批量导入学生
    importStudents(file) {
      const formData = new FormData()
      formData.append('file', file)
      return api.post('/students/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },

    // 搜索学生（支持分页）
    searchStudents(params) {
      return api.get('/students/search', { params })
    },

    // 获取学校学生
    getStudentsBySchool(school) {
      return api.get(`/students/school/${school}`)
    },

    // 创建学生
    createStudent(studentData) {
      return api.post('/students/', studentData)
    },

    // 更新学生
    updateStudent(studentId, studentData) {
      return api.put(`/students/${studentId}`, studentData)
    },

    // 删除学生
    deleteStudent(studentId) {
      return api.delete(`/students/${studentId}`)
    },

    // 获取学生详情
    getStudent(studentId) {
      return api.get(`/students/${studentId}`)
    }
  },

  // 考试相关API
  exams: {
    // 预览Excel文件
    previewExcel(file) {
      const formData = new FormData()
      formData.append('file', file)
      return api.post('/exams/preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },

    // 导入成绩数据
    importGrades(file, importData) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('import_data', JSON.stringify(importData))
      return api.post('/exams/import-grades', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },

    // 获取考试列表
    getExams() {
      return api.get('/exams/')
    },

    // 获取考试报告
    getExamReport(examId) {
      return api.get(`/exams/${examId}/report`)
    },

    // 删除考试
    deleteExam(examId) {
      return api.delete(`/exams/${examId}`)
    },

    // 标准模板导入
    importStandardTemplate(file, importData) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('import_data', JSON.stringify(importData))
      return api.post('/exams/import-standard-template', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },

    // 获取模板示例
    getTemplateExample(examType) {
      return api.get(`/exams/template-example/${examType}`)
    },

    // 按类型获取排名
    getRankingByType(examType, subject, scoreType = 'original', limit = 50) {
      return api.get(`/exams/ranking/${examType}/${subject}`, {
        params: { score_type: scoreType, limit }
      })
    },

    // 获取选课组合排名
    getCombinationRanking(mainSubject, electiveSubjects, examLevel, limit = 50) {
      return api.get('/exams/combination-ranking', {
        params: { 
          main_subject: mainSubject,
          elective_subjects: electiveSubjects,
          exam_level: examLevel,
          limit 
        }
      })
    }
  },

  // 成绩相关API
  grades: {
    // 获取学生成绩历史
    getStudentHistory(name, school) {
      return api.get('/grades/student-history', {
        params: { name, school }
      })
    },

    // 获取排名前N的学生
    getTopPerformers(subject = '总分', limit = 10) {
      return api.get('/grades/top-performers', {
        params: { subject, limit }
      })
    },

    // 获取学生排名趋势
    getRankTrend(name, school, subject = '总分') {
      return api.get('/grades/rank-trend', {
        params: { name, school, subject }
      })
    }
  }
}