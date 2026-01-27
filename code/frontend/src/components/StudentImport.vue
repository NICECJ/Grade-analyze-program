<template>
  <div class="student-import">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生信息批量导入</span>
        </div>
      </template>

      <div class="import-section">
        <el-alert
          title="导入说明"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          <p>请上传包含学生信息的Excel文件，支持以下字段：</p>
          <ul>
            <li><strong>姓名</strong>（必填）：学生姓名</li>
            <li><strong>学校</strong>（必填）：所属学校</li>
            <li><strong>班级</strong>（可选）：所在班级</li>
            <li><strong>年级</strong>（可选）：年级信息</li>
          </ul>
        </el-alert>

        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          accept=".xlsx,.xls"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将学生信息Excel文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 .xlsx/.xls 文件，文件大小不超过10MB
            </div>
          </template>
        </el-upload>

        <div v-if="selectedFile" class="file-info">
          <p><strong>已选择文件:</strong> {{ selectedFile.name }}</p>
          <div class="action-buttons">
            <el-button type="primary" @click="importStudents" :loading="importing">
              开始导入
            </el-button>
            <el-button @click="clearFile">清除文件</el-button>
          </div>
        </div>

        <!-- 导入结果 -->
        <div v-if="importResult" class="result-section">
          <el-result
            icon="success"
            title="导入成功"
            :sub-title="`成功导入 ${importResult.imported_count} 名学生`"
          >
            <template #extra>
              <el-button type="primary" @click="resetForm">继续导入</el-button>
              <el-button @click="$router.push('/grade-import')">导入成绩</el-button>
            </template>
          </el-result>
        </div>
      </div>

      <!-- 学生搜索和管理 -->
      <el-divider content-position="left">学生管理</el-divider>
      
      <div class="search-section">
        <el-form :model="searchForm" inline>
          <el-form-item label="姓名">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入学生姓名"
              clearable
            />
          </el-form-item>
          <el-form-item label="学校">
            <el-input
              v-model="searchForm.school"
              placeholder="请输入学校名称"
              clearable
            />
          </el-form-item>
          <el-form-item label="班级">
            <el-input
              v-model="searchForm.current_class"
              placeholder="请输入班级"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchStudents" :loading="searching">
              搜索
            </el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 学生列表 -->
      <div class="students-table">
        <el-table :data="students" style="width: 100%" stripe>
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="school" label="学校" />
          <el-table-column prop="current_class" label="班级" width="120" />
          <el-table-column prop="grade_level" label="年级" width="100" />
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewStudentGrades(scope.row)"
              >
                查看成绩
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="students.length === 0 && !searching" class="empty-state">
          <el-empty description="暂无学生数据，请先导入学生信息" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'StudentImport',
  data() {
    return {
      selectedFile: null,
      importing: false,
      importResult: null,
      searchForm: {
        name: '',
        school: '',
        current_class: ''
      },
      students: [],
      searching: false
    }
  },
  mounted() {
    this.searchStudents()
  },
  methods: {
    handleFileChange(file) {
      this.selectedFile = file.raw
      this.importResult = null
    },

    async importStudents() {
      if (!this.selectedFile) {
        this.$message.error('请先选择文件')
        return
      }

      this.importing = true
      try {
        this.importResult = await api.students.importStudents(this.selectedFile)
        this.$message.success('学生信息导入成功!')
        this.searchStudents() // 刷新学生列表
      } catch (error) {
        this.$message.error('导入失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.importing = false
      }
    },

    clearFile() {
      this.selectedFile = null
      this.$refs.uploadRef.clearFiles()
    },

    resetForm() {
      this.selectedFile = null
      this.importResult = null
      this.$refs.uploadRef.clearFiles()
    },

    async searchStudents() {
      this.searching = true
      try {
        const params = {}
        if (this.searchForm.name) params.name = this.searchForm.name
        if (this.searchForm.school) params.school = this.searchForm.school
        if (this.searchForm.current_class) params.current_class = this.searchForm.current_class

        this.students = await api.students.searchStudents(params)
      } catch (error) {
        this.$message.error('搜索失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.searching = false
      }
    },

    resetSearch() {
      this.searchForm = {
        name: '',
        school: '',
        current_class: ''
      }
      this.searchStudents()
    },

    viewStudentGrades(student) {
      this.$router.push({
        path: '/student-analysis',
        query: { 
          name: student.name, 
          school: student.school 
        }
      })
    }
  }
}
</script>

<style scoped>
.student-import {
  max-width: 1200px;
  margin: 0 auto;
}

.import-section {
  margin-bottom: 30px;
}

.file-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.action-buttons {
  margin-top: 15px;
}

.result-section {
  margin-top: 30px;
}

.search-section {
  margin-bottom: 20px;
}

.students-table {
  margin-top: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}
</style>