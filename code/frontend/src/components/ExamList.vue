<template>
  <div class="exam-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考试管理</span>
          <el-button type="primary" @click="$router.push('/grade-import')">
            <el-icon><Plus /></el-icon>
            导入新考试
          </el-button>
        </div>
      </template>

      <!-- 统计信息 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ exams.length }}</div>
                <div class="stat-label">考试总数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ totalStudents }}</div>
                <div class="stat-label">参考学生</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ recentExam?.exam_name || '暂无' }}</div>
                <div class="stat-label">最近考试</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ formatDate(recentExam?.exam_date) || '暂无' }}</div>
                <div class="stat-label">最近日期</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-section">
        <el-form :model="searchForm" inline>
          <el-form-item label="考试名称">
            <el-input
              v-model="searchForm.examName"
              placeholder="请输入考试名称"
              clearable
              style="width: 200px;"
            />
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px;"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="filterExams">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 考试列表 -->
      <div class="exam-table">
        <el-table 
          :data="filteredExams" 
          style="width: 100%" 
          stripe
          :default-sort="{prop: 'exam_date', order: 'descending'}"
        >
          <el-table-column prop="exam_name" label="考试名称" min-width="200">
            <template #default="scope">
              <div class="exam-name">
                <strong>{{ scope.row.exam_name }}</strong>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="exam_date" label="考试日期" width="120" sortable>
            <template #default="scope">
              <el-tag type="info">{{ formatDate(scope.row.exam_date) }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="import_time" label="导入时间" width="200" sortable>
            <template #default="scope">
              {{ formatDateTime(scope.row.import_time) }}
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag type="success">已完成</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="300" fixed="right">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewExamDetail(scope.row)"
              >
                查看详情
              </el-button>
              <el-button 
                type="warning" 
                size="small" 
                @click="downloadBackup(scope.row)"
                v-if="scope.row.raw_file_path"
              >
                下载备份
              </el-button>
              <el-popconfirm
                title="确定要删除这个考试吗？删除后无法恢复！"
                @confirm="deleteExam(scope.row)"
                confirm-button-text="确定删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
              >
                <template #reference>
                  <el-button 
                    type="danger" 
                    size="small"
                  >
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <div v-if="filteredExams.length === 0" class="empty-state">
          <el-empty description="暂无考试数据">
            <el-button type="primary" @click="$router.push('/grade-import')">
              导入第一个考试
            </el-button>
          </el-empty>
        </div>
      </div>

      <!-- 批量操作 -->
      <div v-if="exams.length > 0" class="batch-actions">
        <el-divider content-position="left">批量操作</el-divider>
        <el-alert
          title="危险操作"
          type="warning"
          description="批量删除操作将永久删除选中的考试及其所有成绩数据，请谨慎操作！"
          :closable="false"
          style="margin-bottom: 15px;"
        />
        <el-button type="danger" @click="showBatchDeleteDialog = true">
          批量删除考试
        </el-button>
      </div>
    </el-card>

    <!-- 批量删除对话框 -->
    <el-dialog
      v-model="showBatchDeleteDialog"
      title="批量删除考试"
      width="500px"
    >
      <el-alert
        title="警告"
        type="error"
        description="此操作将永久删除选中的考试及其所有相关数据，无法恢复！"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-checkbox-group v-model="selectedExams">
        <div v-for="exam in exams" :key="exam.id" style="margin-bottom: 10px;">
          <el-checkbox :label="exam.id">
            {{ exam.exam_name }} ({{ formatDate(exam.exam_date) }})
          </el-checkbox>
        </div>
      </el-checkbox-group>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showBatchDeleteDialog = false">取消</el-button>
          <el-button 
            type="danger" 
            @click="batchDeleteExams"
            :disabled="selectedExams.length === 0"
            :loading="batchDeleting"
          >
            确定删除 ({{ selectedExams.length }})
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'ExamList',
  data() {
    return {
      exams: [],
      filteredExams: [],
      loading: false,
      searchForm: {
        examName: '',
        dateRange: []
      },
      showBatchDeleteDialog: false,
      selectedExams: [],
      batchDeleting: false
    }
  },
  computed: {
    totalStudents() {
      // 这里可以添加统计逻辑，暂时返回0
      return 0
    },
    recentExam() {
      if (this.exams.length === 0) return null
      return this.exams.reduce((latest, exam) => {
        return new Date(exam.exam_date) > new Date(latest.exam_date) ? exam : latest
      })
    }
  },
  mounted() {
    this.loadExams()
  },
  methods: {
    async loadExams() {
      this.loading = true
      try {
        this.exams = await api.exams.getExams()
        this.filteredExams = [...this.exams]
      } catch (error) {
        this.$message.error('加载考试列表失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.loading = false
      }
    },

    filterExams() {
      let filtered = [...this.exams]
      
      // 按考试名称筛选
      if (this.searchForm.examName) {
        filtered = filtered.filter(exam => 
          exam.exam_name.includes(this.searchForm.examName)
        )
      }
      
      // 按日期范围筛选
      if (this.searchForm.dateRange && this.searchForm.dateRange.length === 2) {
        const [startDate, endDate] = this.searchForm.dateRange
        filtered = filtered.filter(exam => {
          const examDate = new Date(exam.exam_date)
          return examDate >= startDate && examDate <= endDate
        })
      }
      
      this.filteredExams = filtered
    },

    resetSearch() {
      this.searchForm = {
        examName: '',
        dateRange: []
      }
      this.filteredExams = [...this.exams]
    },

    viewExamDetail(exam) {
      this.$router.push({
        path: '/exam-analysis',
        query: { examId: exam.id }
      })
    },

    async deleteExam(exam) {
      try {
        await api.exams.deleteExam(exam.id)
        this.$message.success('考试删除成功')
        this.loadExams() // 重新加载列表
      } catch (error) {
        this.$message.error('删除失败: ' + (error.response?.data?.detail || error.message))
      }
    },

    async batchDeleteExams() {
      if (this.selectedExams.length === 0) {
        this.$message.warning('请选择要删除的考试')
        return
      }

      this.batchDeleting = true
      try {
        // 逐个删除选中的考试
        for (const examId of this.selectedExams) {
          await api.exams.deleteExam(examId)
        }
        
        this.$message.success(`成功删除 ${this.selectedExams.length} 个考试`)
        this.showBatchDeleteDialog = false
        this.selectedExams = []
        this.loadExams() // 重新加载列表
      } catch (error) {
        this.$message.error('批量删除失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.batchDeleting = false
      }
    },

    downloadBackup(exam) {
      // 这里可以添加下载备份文件的逻辑
      this.$message.info('备份下载功能开发中...')
    },

    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('zh-CN')
    },

    formatDateTime(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.exam-list {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-section {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.search-section {
  margin-bottom: 20px;
}

.exam-table {
  margin-bottom: 30px;
}

.exam-name {
  display: flex;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.batch-actions {
  margin-top: 30px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>