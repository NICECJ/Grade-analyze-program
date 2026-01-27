// API 接口封装
const API_BASE_URL = '/api'

// 通用请求函数
async function request(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// 考试相关API
const exams = {
  // 获取所有考试
  async getExams() {
    return request('/exams/')
  },

  // 获取考试报告
  async getExamReport(examId) {
    return request(`/exams/${examId}/report`)
  },

  // 获取上一次考试ID
  async getPreviousExam(examId) {
    return request(`/exams/${examId}/previous`)
  },

  // 删除考试
  async deleteExam(examId) {
    return request(`/exams/${examId}`, { method: 'DELETE' })
  },

  // 创建考试
  async createExam(examData) {
    const formData = new FormData()
    Object.keys(examData).forEach(key => {
      formData.append(key, examData[key])
    })
    
    const response = await fetch(`${API_BASE_URL}/exams/create`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '创建考试失败' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }
    
    return response.json()
  }
}

// 学生相关API
const students = {
  // 获取学生列表
  async getStudents(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return request(`/students/?${queryString}`)
  },

  // 创建学生
  async createStudent(studentData) {
    return request('/students/', {
      method: 'POST',
      body: JSON.stringify(studentData)
    })
  },

  // 更新学生
  async updateStudent(studentId, studentData) {
    return request(`/students/${studentId}`, {
      method: 'PUT',
      body: JSON.stringify(studentData)
    })
  },

  // 删除学生
  async deleteStudent(studentId) {
    return request(`/students/${studentId}`, { method: 'DELETE' })
  },

  // 搜索学生
  async searchStudents(params) {
    const queryString = new URLSearchParams(params).toString()
    return request(`/students/search?${queryString}`)
  }
}

// 成绩相关API
const grades = {
  // 获取学生成绩历史
  async getStudentHistory(studentName, school) {
    // 首先搜索学生获取ID
    const searchStudents = await request(`/students/search?name=${encodeURIComponent(studentName)}&school=${encodeURIComponent(school)}`)
    if (searchStudents.length === 0) {
      throw new Error('未找到该学生')
    }
    
    const studentId = searchStudents[0].id
    return request(`/grades/student/${studentId}/history`)
  },

  // 获取排名趋势（模拟数据，实际需要后端实现）
  async getRankTrend(studentName, school, subject) {
    // 这里返回模拟数据，实际应该调用后端API
    return {
      trend_data: [],
      warnings: []
    }
  },

  // 手工导入成绩
  async manualImport(gradeData) {
    return request('/grades/manual-import', {
      method: 'POST',
      body: JSON.stringify(gradeData)
    })
  }
}

// 导出API对象
export default {
  exams,
  students,
  grades
}