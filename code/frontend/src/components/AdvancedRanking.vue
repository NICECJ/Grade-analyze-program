<template>
  <div class="advanced-ranking">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>高级排名分析</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :model="filterForm" inline>
        <el-form-item label="分析类型">
          <el-radio-group v-model="analysisType" @change="onAnalysisTypeChange">
            <el-radio-button label="type">按考试类型</el-radio-button>
            <el-radio-button label="combination">按选课组合</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <!-- 按考试类型分析 -->
      <div v-if="analysisType === 'type'" class="type-analysis">
        <el-form :model="typeFilter" inline>
          <el-form-item label="考试类型">
            <el-select v-model="typeFilter.exam_type" placeholder="选择考试类型">
              <el-option label="物理类" value="物理类" />
              <el-option label="历史类" value="历史类" />
            </el-select>
          </el-form-item>
          <el-form-item label="科目">
            <el-select v-model="typeFilter.subject" placeholder="选择科目">
              <el-option label="总分" value="总分" />
              <el-option label="语文" value="语文" />
              <el-option label="数学" value="数学" />
              <el-option label="英语" value="英语" />
              <el-option v-if="typeFilter.exam_type === '物理类'" label="物理" value="物理" />
              <el-option v-if="typeFilter.exam_type === '历史类'" label="历史" value="历史" />
              <el-option label="化学" value="化学" />
              <el-option label="生物" value="生物" />
              <el-option label="地理" value="地理" />
              <el-option label="政治" value="政治" />
            </el-select>
          </el-form-item>
          <el-form-item label="成绩类型">
            <el-select v-model="typeFilter.score_type" placeholder="选择成绩类型">
              <el-option label="原始成绩" value="original" />
              <el-option label="赋分成绩" value="scaled" />
            </el-select>
          </el-form-item>
          <el-form-item label="显示数量">
            <el-input-number v-model="typeFilter.limit" :min="10" :max="200" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadTypeRanking" :loading="loading">
              查询排名
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 按选课组合分析 -->
      <div v-if="analysisType === 'combination'" class="combination-analysis">
        <el-form :model="combinationFilter" inline>
          <el-form-item label="主科">
            <el-select v-model="combinationFilter.main_subject" placeholder="选择主科">
              <el-option label="物理" value="物理" />
              <el-option label="历史" value="历史" />
            </el-select>
          </el-form-item>
          <el-form-item label="选考科目">
            <el-select 
              v-model="combinationFilter.elective_subjects" 
              multiple 
              placeholder="选择选考科目（四选二）"
              :max-collapse-tags="2"
            >
              <el-option label="化学" value="化学" />
              <el-option label="生物" value="生物" />
              <el-option label="地理" value="地理" />
              <el-option label="政治" value="政治" />
            </el-select>
          </el-form-item>
          <el-form-item label="考试级别">
            <el-select v-model="combinationFilter.exam_level" placeholder="选择考试级别">
              <el-option label="校级" value="校级" />
              <el-option label="市级" value="市级" />
              <el-option label="省级" value="省级" />
            </el-select>
          </el-form-item>
          <el-form-item label="显示数量">
            <el-input-number v-model="combinationFilter.limit" :min="10" :max="200" />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="loadCombinationRanking" 
              :loading="loading"
              :disabled="!canQueryCombination"
            >
              查询排名
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 排名结果 -->
      <div v-if="rankingData.length > 0" class="ranking-results">
        <el-divider content-position="left">
          <span v-if="analysisType === 'type'">
            {{ typeFilter.exam_type }} - {{ typeFilter.subject }} 排名
            ({{ typeFilter.score_type === 'original' ? '原始成绩' : '赋分成绩' }})
          </span>
          <span v-else>
            {{ combinationFilter.main_subject }}+{{ combinationFilter.elective_subjects.join('+') }} 组合排名
          </span>
        </el-divider>

        <!-- 统计信息 -->
        <div class="stats-info">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总人数" :value="rankingData.length" />
            </el-col>
            <el-col :span="6" v-if="analysisType === 'type'">
              <el-statistic 
                title="平均分" 
                :value="averageScore" 
                :precision="2" 
              />
            </el-col>
            <el-col :span="6" v-if="analysisType === 'type'">
              <el-statistic 
                title="最高分" 
                :value="maxScore" 
                :precision="2" 
              />
            </el-col>
            <el-col :span="6" v-if="analysisType === 'type'">
              <el-statistic 
                title="最低分" 
                :value="minScore" 
                :precision="2" 
              />
            </el-col>
          </el-row>
        </div>

        <!-- 排名表格 -->
        <el-table 
          :data="rankingData" 
          style="width: 100%; margin-top: 20px"
          stripe
          :default-sort="{prop: 'rank_province', order: 'ascending'}"
        >
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="school" label="学校" width="120" />
          <el-table-column prop="current_class" label="班级" width="100" />
          
          <el-table-column v-if="analysisType === 'type'" prop="score" label="成绩" width="80" sortable>
            <template #default="scope">
              <el-tag :type="getScoreType(scope.row.score)">
                {{ scope.row.score }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column v-if="analysisType === 'combination'" prop="total_score" label="总分" width="80" sortable>
            <template #default="scope">
              <el-tag type="danger">
                {{ scope.row.total_score }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column v-if="analysisType === 'combination'" prop="scores" label="各科成绩" min-width="200">
            <template #default="scope">
              <div class="subject-scores">
                <el-tag 
                  v-for="scoreItem in parseScores(scope.row.scores)" 
                  :key="scoreItem.subject"
                  size="small"
                  style="margin: 2px;"
                >
                  {{ scoreItem.subject }}: {{ scoreItem.score }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="rank_school" label="校排名" width="80" sortable />
          <el-table-column prop="rank_city" label="市排名" width="80" sortable />
          <el-table-column prop="rank_province" label="省排名" width="80" sortable />
          
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button 
                type="text" 
                size="small" 
                @click="viewStudentDetail(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 导出功能 -->
        <div class="export-actions" style="margin-top: 20px; text-align: right;">
          <el-button @click="exportRanking">
            <el-icon><Download /></el-icon>
            导出排名数据
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && rankingData.length === 0 && hasQueried" class="empty-state">
        <el-empty description="暂无排名数据">
          <el-button type="primary" @click="resetFilters">重新查询</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'AdvancedRanking',
  data() {
    return {
      analysisType: 'type',
      loading: false,
      hasQueried: false,
      rankingData: [],
      
      typeFilter: {
        exam_type: '物理类',
        subject: '总分',
        score_type: 'original',
        limit: 50
      },
      
      combinationFilter: {
        main_subject: '物理',
        elective_subjects: [],
        exam_level: '省级',
        limit: 50
      }
    }
  },
  computed: {
    canQueryCombination() {
      return this.combinationFilter.main_subject && 
             this.combinationFilter.elective_subjects.length >= 2 &&
             this.combinationFilter.exam_level
    },
    
    averageScore() {
      if (this.rankingData.length === 0) return 0
      const total = this.rankingData.reduce((sum, item) => sum + (item.score || 0), 0)
      return total / this.rankingData.length
    },
    
    maxScore() {
      if (this.rankingData.length === 0) return 0
      return Math.max(...this.rankingData.map(item => item.score || 0))
    },
    
    minScore() {
      if (this.rankingData.length === 0) return 0
      return Math.min(...this.rankingData.map(item => item.score || 0))
    }
  },
  methods: {
    onAnalysisTypeChange() {
      this.rankingData = []
      this.hasQueried = false
    },

    async loadTypeRanking() {
      if (!this.typeFilter.exam_type || !this.typeFilter.subject) {
        this.$message.error('请选择考试类型和科目')
        return
      }

      this.loading = true
      try {
        // 转换中文考试类型为英文枚举值
        const examTypeMap = {
          '物理类': 'PHYSICS',
          '历史类': 'HISTORY'
        }
        const examTypeEnum = examTypeMap[this.typeFilter.exam_type]
        
        const response = await api.exams.getRankingByType(
          examTypeEnum,
          this.typeFilter.subject,
          this.typeFilter.score_type,
          this.typeFilter.limit
        )
        
        this.rankingData = response.ranking || []
        this.hasQueried = true
        
        if (this.rankingData.length === 0) {
          this.$message.info('未找到符合条件的排名数据')
        }
      } catch (error) {
        this.$message.error('查询失败: ' + (error.response?.data?.detail || error.message))
        this.rankingData = []
      } finally {
        this.loading = false
      }
    },

    async loadCombinationRanking() {
      if (!this.canQueryCombination) {
        this.$message.error('请完整填写查询条件')
        return
      }

      this.loading = true
      try {
        // 转换中文考试级别为英文枚举值
        const examLevelMap = {
          '校级': 'SCHOOL',
          '市级': 'CITY',
          '省级': 'PROVINCE'
        }
        const examLevelEnum = examLevelMap[this.combinationFilter.exam_level]
        
        const response = await api.exams.getCombinationRanking(
          this.combinationFilter.main_subject,
          this.combinationFilter.elective_subjects.join(','),
          examLevelEnum,
          this.combinationFilter.limit
        )
        
        this.rankingData = response.ranking || []
        this.hasQueried = true
        
        if (this.rankingData.length === 0) {
          this.$message.info('未找到符合条件的选课组合数据')
        }
      } catch (error) {
        this.$message.error('查询失败: ' + (error.response?.data?.detail || error.message))
        this.rankingData = []
      } finally {
        this.loading = false
      }
    },

    getScoreType(score) {
      if (score >= 90) return 'success'
      if (score >= 80) return 'warning'
      if (score >= 60) return 'info'
      return 'danger'
    },

    parseScores(scoresStr) {
      if (!scoresStr) return []
      
      return scoresStr.split(',').map(item => {
        const [subject, score] = item.split(':')
        return { subject: subject?.trim(), score: score?.trim() }
      }).filter(item => item.subject && item.score)
    },

    viewStudentDetail(student) {
      this.$router.push({
        path: '/student-analysis',
        query: { 
          name: student.name, 
          school: student.school 
        }
      })
    },

    exportRanking() {
      if (this.rankingData.length === 0) {
        this.$message.warning('没有数据可导出')
        return
      }

      // 准备导出数据
      const exportData = this.rankingData.map((item, index) => {
        const baseData = {
          '序号': index + 1,
          '姓名': item.name,
          '学校': item.school,
          '班级': item.current_class,
          '校排名': item.rank_school || '',
          '市排名': item.rank_city || '',
          '省排名': item.rank_province || ''
        }

        if (this.analysisType === 'type') {
          baseData['成绩'] = item.score || ''
        } else {
          baseData['总分'] = item.total_score || ''
          baseData['各科成绩'] = item.scores || ''
        }

        return baseData
      })

      // 使用CSV格式导出
      const headers = Object.keys(exportData[0])
      let csvContent = headers.join(',') + '\n'
      
      exportData.forEach(row => {
        const values = headers.map(header => {
          const value = row[header] || ''
          // 如果值包含逗号或引号，需要用引号包围
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return value
        })
        csvContent += values.join(',') + '\n'
      })
      
      // 创建Blob并下载
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      
      const filename = this.analysisType === 'type' 
        ? `${this.typeFilter.exam_type}_${this.typeFilter.subject}_排名.csv`
        : `${this.combinationFilter.main_subject}+${this.combinationFilter.elective_subjects.join('+')}_组合排名.csv`
      
      link.setAttribute('download', filename)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      this.$message.success('导出成功（CSV格式）')
    },

    resetFilters() {
      if (this.analysisType === 'type') {
        this.typeFilter = {
          exam_type: '物理类',
          subject: '总分',
          score_type: 'original',
          limit: 50
        }
      } else {
        this.combinationFilter = {
          main_subject: '物理',
          elective_subjects: [],
          exam_level: '省级',
          limit: 50
        }
      }
      this.rankingData = []
      this.hasQueried = false
    }
  }
}
</script>

<style scoped>
.advanced-ranking {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.type-analysis, .combination-analysis {
  margin: 20px 0;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stats-info {
  margin: 20px 0;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 4px;
}

.subject-scores {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.export-actions {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}
</style>