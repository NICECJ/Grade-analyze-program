<template>
  <div class="student-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生信息管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            添加学生
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="输入学生姓名" clearable />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="searchForm.school" placeholder="输入学校名称" clearable />
        </el-form-item>
        <el-form-item label="班级">
          <el-input v-model="searchForm.current_class" placeholder="输入班级" clearable />
        </el-form-item>
        <el-form-item label="考试类型">
          <el-select v-model="searchForm.exam_type" placeholder="选择考试类型" clearable>
            <el-option label="物理类" value="PHYSICS" />
            <el-option label="历史类" value="HISTORY" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchStudents" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 学生列表 -->
      <el-table 
        :data="students" 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="school" label="学校" width="150" />
        <el-table-column prop="current_class" label="班级" width="100" />
        <el-table-column prop="grade_level" label="年级" width="80" />
        <el-table-column prop="exam_type" label="考试类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.exam_type === 'PHYSICS' ? 'primary' : 'success'">
              {{ scope.row.exam_type === 'PHYSICS' ? '物理类' : '历史类' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="subject_combination" label="选科组合" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.subject_combination" size="small">
              {{ scope.row.subject_combination }}
            </el-tag>
            <span v-else class="text-gray">未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editStudent(scope.row)">
              编辑
            </el-button>
            <el-button type="info" size="small" @click="viewGrades(scope.row)">
              成绩
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteStudent(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑学生对话框 -->
    <el-dialog 
      v-model="showAddDialog" 
      :title="editingStudent ? '编辑学生信息' : '添加学生'"
      width="600px"
    >
      <el-form :model="studentForm" :rules="studentRules" ref="studentFormRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="studentForm.name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="学校" prop="school">
          <el-input v-model="studentForm.school" placeholder="请输入学校名称" />
        </el-form-item>
        <el-form-item label="班级" prop="current_class">
          <el-input v-model="studentForm.current_class" placeholder="请输入班级" />
        </el-form-item>
        <el-form-item label="年级" prop="grade_level">
          <el-select v-model="studentForm.grade_level" placeholder="选择年级">
            <el-option label="高一" value="高一" />
            <el-option label="高二" value="高二" />
            <el-option label="高三" value="高三" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试类型" prop="exam_type">
          <el-radio-group v-model="studentForm.exam_type">
            <el-radio label="PHYSICS">物理类</el-radio>
            <el-radio label="HISTORY">历史类</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="选科组合" prop="subject_combination">
          <el-select v-model="studentForm.subject_combination" placeholder="选择选科组合">
            <el-option label="不设置" value="" />
            <el-optgroup label="物理类组合" v-if="studentForm.exam_type === 'PHYSICS'">
              <el-option label="物化生" value="物化生" />
              <el-option label="物化地" value="物化地" />
              <el-option label="物化政" value="物化政" />
              <el-option label="物生地" value="物生地" />
              <el-option label="物生政" value="物生政" />
              <el-option label="物地政" value="物地政" />
            </el-optgroup>
            <el-optgroup label="历史类组合" v-if="studentForm.exam_type === 'HISTORY'">
              <el-option label="史化生" value="史化生" />
              <el-option label="史化地" value="史化地" />
              <el-option label="史化政" value="史化政" />
              <el-option label="史生地" value="史生地" />
              <el-option label="史生政" value="史生政" />
              <el-option label="史地政" value="史地政" />
            </el-optgroup>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" @click="saveStudent" :loading="saving">
            {{ editingStudent ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'StudentManagement',
  data() {
    return {
      loading: false,
      saving: false,
      students: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      
      searchForm: {
        name: '',
        school: '',
        current_class: '',
        exam_type: ''
      },
      
      showAddDialog: false,
      editingStudent: null,
      studentForm: {
        name: '',
        school: '',
        current_class: '',
        grade_level: '',
        exam_type: 'PHYSICS',
        subject_combination: ''
      },
      
      studentRules: {
        name: [
          { required: true, message: '请输入学生姓名', trigger: 'blur' }
        ],
        school: [
          { required: true, message: '请输入学校名称', trigger: 'blur' }
        ],
        current_class: [
          { required: true, message: '请输入班级', trigger: 'blur' }
        ],
        exam_type: [
          { required: true, message: '请选择考试类型', trigger: 'change' }
        ]
      }
    }
  },
  
  mounted() {
    this.searchStudents()
  },
  
  methods: {
    async searchStudents() {
      this.loading = true
      try {
        const params = {
          ...this.searchForm,
          page: this.currentPage,
          size: this.pageSize
        }
        
        // 移除空值参数
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const response = await api.students.searchStudents(params)
        this.students = response.students || []
        this.total = response.total || 0
      } catch (error) {
        this.$message.error('搜索失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.loading = false
      }
    },
    
    resetSearch() {
      this.searchForm = {
        name: '',
        school: '',
        current_class: '',
        exam_type: ''
      }
      this.currentPage = 1
      this.searchStudents()
    },
    
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.searchStudents()
    },
    
    handleCurrentChange(val) {
      this.currentPage = val
      this.searchStudents()
    },
    
    editStudent(student) {
      this.editingStudent = student
      this.studentForm = {
        name: student.name,
        school: student.school,
        current_class: student.current_class,
        grade_level: student.grade_level || '',
        exam_type: student.exam_type || 'PHYSICS',
        subject_combination: student.subject_combination || ''
      }
      this.showAddDialog = true
    },
    
    async saveStudent() {
      if (!this.$refs.studentFormRef) return
      
      const valid = await this.$refs.studentFormRef.validate()
      if (!valid) return
      
      this.saving = true
      try {
        if (this.editingStudent) {
          // 更新学生
          await api.students.updateStudent(this.editingStudent.id, this.studentForm)
          this.$message.success('学生信息更新成功')
        } else {
          // 添加学生
          await api.students.createStudent(this.studentForm)
          this.$message.success('学生添加成功')
        }
        
        this.showAddDialog = false
        this.searchStudents()
      } catch (error) {
        this.$message.error('保存失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.saving = false
      }
    },
    
    cancelEdit() {
      this.showAddDialog = false
      this.editingStudent = null
      this.studentForm = {
        name: '',
        school: '',
        current_class: '',
        grade_level: '',
        exam_type: 'PHYSICS',
        subject_combination: ''
      }
    },
    
    async deleteStudent(student) {
      try {
        await this.$confirm(`确定要删除学生 "${student.name}" 吗？这将同时删除该学生的所有成绩记录。`, '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await api.students.deleteStudent(student.id)
        this.$message.success('学生删除成功')
        this.searchStudents()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    },
    
    viewGrades(student) {
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
.student-management {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.text-gray {
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>