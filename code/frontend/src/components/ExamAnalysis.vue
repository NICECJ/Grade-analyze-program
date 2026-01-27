<template>
  <div class="exam-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考试详情分析</span>
        </div>
      </template>

      <!-- 考试选择 -->
      <div class="exam-selection">
        <el-form :model="searchForm" inline>
          <el-form-item label="选择考试">
            <el-select 
              v-model="searchForm.examId" 
              placeholder="请选择考试"
              @change="loadExamReport"
              style="width: 300px;"
            >
              <el-option
                v-for="exam in exams"
                :key="exam.id"
                :label="`${exam.exam_name} (${formatDate(exam.exam_date)})`"
                :value="exam.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="考试类型">
            <el-select 
              v-model="searchForm.examType" 
              placeholder="选择考试类型"
              @change="filterByExamType"
              style="width: 150px;"
            >
              <el-option label="全部" value="" />
              <el-option label="物理类" value="PHYSICS" />
              <el-option label="历史类" value="HISTORY" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadExamReport" :loading="loading">
              查看分析
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 考试概览 -->
      <div v-if="examReport" class="exam-overview">
        <h3>考试概况</h3>
        <el-row :gutter="20">
          <el-col :span="4">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ filteredStudentCount }}</div>
                <div class="stat-label">参考学生数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ examReport.subjects.length }}</div>
                <div class="stat-label">考试科目数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ formatDate(examReport.exam_date) }}</div>
                <div class="stat-label">考试日期</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ examReport.exam_type || '混合' }}</div>
                <div class="stat-label">考试类型</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ examReport.exam_level || '未知' }}</div>
                <div class="stat-label">考试级别</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ examReport.exam_name }}</div>
                <div class="stat-label">考试名称</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 平均分展示 -->
        <div class="average-scores" v-if="averageScores">
          <h4>各科平均分</h4>
          <el-row :gutter="15">
            <el-col :span="4" v-for="(avg, subject) in averageScores" :key="subject">
              <el-card class="avg-score-card">
                <div class="avg-score-content">
                  <div class="subject-name">{{ subject }}</div>
                  <div class="avg-score">{{ avg.toFixed(1) }}</div>
                  <div v-if="previousAverages[subject]" class="score-change">
                    <span :class="getChangeClass(avg - previousAverages[subject])">
                      <el-icon v-if="avg > previousAverages[subject]"><ArrowUp /></el-icon>
                      <el-icon v-else-if="avg < previousAverages[subject]"><ArrowDown /></el-icon>
                      <el-icon v-else><Minus /></el-icon>
                      {{ Math.abs(avg - previousAverages[subject]).toFixed(1) }}
                    </span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 成绩分布图表 -->
      <div v-if="examReport" class="charts-section">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card>
              <template #header>
                <span>成绩分布</span>
              </template>
              <div class="chart-container">
                <v-chart class="chart" :option="scoreDistributionOption" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 详细成绩表格 -->
      <div v-if="examReport" class="grades-table">
        <h3>学生成绩详情</h3>
        <div class="table-controls">
          <el-input
            v-model="searchText"
            placeholder="搜索学生姓名或学校"
            style="width: 300px; margin-right: 10px;"
            clearable
          />
          <el-select v-model="classFilter" placeholder="筛选班级" clearable style="width: 150px; margin-right: 10px;">
            <el-option
              v-for="cls in availableClasses"
              :key="cls"
              :label="cls"
              :value="cls"
            />
          </el-select>
        </div>
        
        <el-table 
          :data="processedStudentGrades" 
          style="width: 100%; margin-top: 20px;" 
          stripe
          :default-sort="{prop: 'total_rank_province', order: 'ascending'}"
          size="small"
        >
          <el-table-column prop="student_name" label="姓名" width="80" fixed="left" align="center" />
          <el-table-column prop="school" label="学校" width="100" align="center" />
          <el-table-column prop="current_class" label="班级" width="70" align="center" />
          <el-table-column prop="subject_combination" label="选科类型" width="80" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.exam_type === 'PHYSICS' ? 'primary' : 'success'" size="small">
                {{ scope.row.subject_combination || (scope.row.exam_type === 'PHYSICS' ? '物理类' : '历史类') }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 必修科目 -->
          <el-table-column prop="chinese_score" label="语文" width="70" align="center" />
          <el-table-column prop="math_score" label="数学" width="70" align="center" />
          <el-table-column prop="english_score" label="英语" width="70" align="center" />

          <!-- 主科（物理/历史） -->
          <el-table-column prop="main_subject_score" label="物理/历史" width="90" align="center" />

          <!-- 四选二科目 -->
          <el-table-column label="选考科目1" width="180" v-if="hasElectiveSubjects" align="center">
            <el-table-column prop="elective1_original" label="原始" width="60" align="center" />
            <el-table-column prop="elective1_scaled" label="赋分" width="60" align="center" />
            <el-table-column prop="elective1_name" label="科目" width="60" align="center" />
          </el-table-column>

          <el-table-column label="选考科目2" width="180" v-if="hasElectiveSubjects" align="center">
            <el-table-column prop="elective2_original" label="原始" width="60" align="center" />
            <el-table-column prop="elective2_scaled" label="赋分" width="60" align="center" />
            <el-table-column prop="elective2_name" label="科目" width="60" align="center" />
          </el-table-column>

          <!-- 总分 -->
          <el-table-column label="总分" width="240" align="center">
            <el-table-column prop="total_original" label="赋分前" width="60" align="center" />
            <el-table-column prop="total_scaled" label="赋分后" width="60" align="center" />
            <el-table-column prop="total_original_rank" label="赋分前排名" width="60" align="center" />
            <el-table-column prop="total_scaled_rank" label="赋分后排名" width="60" align="center" />
          </el-table-column>

          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewStudentDetail(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'
import api from '../api'

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  name: 'ExamAnalysis',
  components: {
    VChart,
    ArrowUp,
    ArrowDown,
    Minus
  },
  data() {
    return {
      searchForm: {
        examId: null,
        examType: ''
      },
      exams: [],
      examReport: null,
      previousExamReport: null, // 上一次考试数据，用于对比
      loading: false,
      searchText: '',
      classFilter: '',
      scoreDistributionOption: {},
      averageScores: {},
      previousAverages: {}
    }
  },
  computed: {
    filteredStudentCount() {
      if (!this.examReport) return 0
      return this.processedStudentGrades.length
    },

    availableClasses() {
      if (!this.examReport) return []
      const classes = new Set()
      this.examReport.grades.forEach(grade => {
        if (grade.current_class) {
          classes.add(grade.current_class)
        }
      })
      return Array.from(classes).sort()
    },

    hasElectiveSubjects() {
      if (!this.examReport) return false
      return this.examReport.subjects.some(subject => 
        ['化学', '生物', '地理', '政治'].includes(subject)
      )
    },

    processedStudentGrades() {
      if (!this.examReport) return []
      
      // 按学生分组处理成绩
      const studentGrades = {}
      
      this.examReport.grades.forEach(grade => {
        const key = `${grade.student_name}_${grade.school}_${grade.current_class}`
        
        if (!studentGrades[key]) {
          studentGrades[key] = {
            student_name: grade.student_name,
            school: grade.school,
            current_class: grade.current_class,
            exam_type: grade.exam_type,
            subject_combination: grade.subject_combination,
            subjects: {}
          }
        }
        
        studentGrades[key].subjects[grade.subject_name] = {
          original_score: grade.original_score,
          scaled_score: grade.scaled_score,
          rank_school: grade.rank_school,
          rank_city: grade.rank_city,
          rank_province: grade.rank_province,
          scaled_rank_school: grade.scaled_rank_school,
          scaled_rank_city: grade.scaled_rank_city,
          scaled_rank_province: grade.scaled_rank_province
        }
      })

      // 转换为表格数据格式
      const result = Object.values(studentGrades).map(student => {
        const subjects = student.subjects
        const processedStudent = {
          ...student,
          // 必修科目
          chinese_score: subjects['语文']?.original_score || subjects['语文']?.scaled_score,
          chinese_rank: subjects['语文']?.rank_province,
          math_score: subjects['数学']?.original_score || subjects['数学']?.scaled_score,
          math_rank: subjects['数学']?.rank_province,
          english_score: subjects['英语']?.original_score || subjects['英语']?.scaled_score,
          english_rank: subjects['英语']?.rank_province,
          
          // 主科（物理/历史）
          main_subject_score: subjects['物理']?.original_score || subjects['历史']?.original_score,
          main_subject_rank: subjects['物理']?.rank_province || subjects['历史']?.rank_province,
          
          // 总分
          total_original: subjects['总分']?.original_score,
          total_scaled: subjects['总分']?.scaled_score,
          total_original_rank: subjects['总分']?.rank_province,
          total_scaled_rank: subjects['总分']?.scaled_rank_province
        }

        // 处理选考科目
        const electiveSubjects = ['化学', '生物', '地理', '政治'].filter(sub => subjects[sub])
        if (electiveSubjects.length >= 1) {
          const elective1 = electiveSubjects[0]
          processedStudent.elective1_name = elective1
          processedStudent.elective1_original = subjects[elective1]?.original_score
          processedStudent.elective1_scaled = subjects[elective1]?.scaled_score
          processedStudent.elective1_rank = subjects[elective1]?.scaled_rank_province || subjects[elective1]?.rank_province
        }
        
        if (electiveSubjects.length >= 2) {
          const elective2 = electiveSubjects[1]
          processedStudent.elective2_name = elective2
          processedStudent.elective2_original = subjects[elective2]?.original_score
          processedStudent.elective2_scaled = subjects[elective2]?.scaled_score
          processedStudent.elective2_rank = subjects[elective2]?.scaled_rank_province || subjects[elective2]?.rank_province
        }

        // 添加与上次考试的对比数据
        if (this.previousExamReport) {
          this.addComparisonData(processedStudent)
        }

        return processedStudent
      })

      // 应用筛选
      return result.filter(student => {
        let matches = true
        
        if (this.searchText) {
          matches = matches && (
            student.student_name.includes(this.searchText) ||
            student.school.includes(this.searchText)
          )
        }
        
        if (this.classFilter) {
          matches = matches && student.current_class === this.classFilter
        }
        
        if (this.searchForm.examType) {
          matches = matches && student.exam_type === this.searchForm.examType
        }
        
        return matches
      })
    }
  },
  mounted() {
    this.loadExams()
    
    // 检查URL参数中是否有examId
    if (this.$route.query.examId) {
      this.searchForm.examId = parseInt(this.$route.query.examId)
      this.loadExamReport()
    }
  },
  methods: {
    async loadExams() {
      try {
        this.exams = await api.exams.getExams()
      } catch (error) {
        this.$message.error('加载考试列表失败: ' + (error.response?.data?.detail || error.message))
      }
    },

    async loadExamReport() {
      if (!this.searchForm.examId) {
        this.$message.error('请选择考试')
        return
      }

      this.loading = true
      try {
        this.examReport = await api.exams.getExamReport(this.searchForm.examId)
        
        // 加载上一次考试数据用于对比
        await this.loadPreviousExamReport()
        
        // 计算平均分
        this.calculateAverageScores()
        
        // 更新图表
        this.updateCharts()
      } catch (error) {
        this.$message.error('加载考试报告失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.loading = false
      }
    },

    async loadPreviousExamReport() {
      try {
        // 获取上一次考试ID
        const response = await fetch(`/api/exams/${this.searchForm.examId}/previous`)
        const data = await response.json()
        
        if (data.previous_exam_id) {
          this.previousExamReport = await api.exams.getExamReport(data.previous_exam_id)
          this.calculatePreviousAverages()
        }
      } catch (error) {
        console.warn('无法加载上一次考试数据:', error)
      }
    },

    calculateAverageScores() {
      if (!this.examReport) return
      
      const subjectScores = {}
      const subjectCounts = {}
      
      this.examReport.grades.forEach(grade => {
        const subject = grade.subject_name
        const score = grade.original_score || grade.scaled_score
        
        if (score && !isNaN(score)) {
          if (!subjectScores[subject]) {
            subjectScores[subject] = 0
            subjectCounts[subject] = 0
          }
          subjectScores[subject] += parseFloat(score)
          subjectCounts[subject]++
        }
      })
      
      this.averageScores = {}
      Object.keys(subjectScores).forEach(subject => {
        this.averageScores[subject] = subjectScores[subject] / subjectCounts[subject]
      })
    },

    calculatePreviousAverages() {
      if (!this.previousExamReport) return
      
      const subjectScores = {}
      const subjectCounts = {}
      
      this.previousExamReport.grades.forEach(grade => {
        const subject = grade.subject_name
        const score = grade.original_score || grade.scaled_score
        
        if (score && !isNaN(score)) {
          if (!subjectScores[subject]) {
            subjectScores[subject] = 0
            subjectCounts[subject] = 0
          }
          subjectScores[subject] += parseFloat(score)
          subjectCounts[subject]++
        }
      })
      
      this.previousAverages = {}
      Object.keys(subjectScores).forEach(subject => {
        this.previousAverages[subject] = subjectScores[subject] / subjectCounts[subject]
      })
    },

    addComparisonData(student) {
      if (!this.previousExamReport) {
        return
      }
      
      // 创建上次考试的学生成绩映射
      const previousGradesMap = {}
      this.previousExamReport.grades.forEach(grade => {
        const key = `${grade.student_name}_${grade.school}_${grade.current_class}`
        if (!previousGradesMap[key]) {
          previousGradesMap[key] = {}
        }
        previousGradesMap[key][grade.subject_name] = grade
      })
      
      const studentKey = `${student.student_name}_${student.school}_${student.current_class}`
      const previousGrades = previousGradesMap[studentKey]
      
      if (previousGrades) {
        // 计算各科排名变化
        if (previousGrades['语文']) {
          student.chinese_rank_change = this.calculateRankChange(
            student.chinese_rank, 
            previousGrades['语文'].rank_province
          )
        }
        
        if (previousGrades['数学']) {
          student.math_rank_change = this.calculateRankChange(
            student.math_rank, 
            previousGrades['数学'].rank_province
          )
        }
        
        if (previousGrades['英语']) {
          student.english_rank_change = this.calculateRankChange(
            student.english_rank, 
            previousGrades['英语'].rank_province
          )
        }
        
        // 主科排名变化
        const mainSubject = student.exam_type === 'PHYSICS' ? '物理' : '历史'
        if (previousGrades[mainSubject]) {
          student.main_subject_rank_change = this.calculateRankChange(
            student.main_subject_rank,
            previousGrades[mainSubject].rank_province
          )
        }
        
        // 选考科目排名变化
        if (student.elective1_name && previousGrades[student.elective1_name]) {
          student.elective1_rank_change = this.calculateRankChange(
            student.elective1_rank,
            previousGrades[student.elective1_name].scaled_rank_province || previousGrades[student.elective1_name].rank_province
          )
        }
        
        if (student.elective2_name && previousGrades[student.elective2_name]) {
          student.elective2_rank_change = this.calculateRankChange(
            student.elective2_rank,
            previousGrades[student.elective2_name].scaled_rank_province || previousGrades[student.elective2_name].rank_province
          )
        }
        
        // 总分排名变化
        if (previousGrades['总分']) {
          student.total_original_rank_change = this.calculateRankChange(
            student.total_original_rank,
            previousGrades['总分'].rank_province
          )
          
          student.total_scaled_rank_change = this.calculateRankChange(
            student.total_scaled_rank,
            previousGrades['总分'].scaled_rank_province || previousGrades['总分'].rank_province
          )
        }
      }
    },

    calculateRankChange(currentRank, previousRank) {
      if (!currentRank || !previousRank) return null
      return currentRank - previousRank // 正数表示排名下降，负数表示排名上升
    },

    filterByExamType() {
      // 当考试类型筛选改变时，重新处理数据
      this.updateCharts()
    },

    updateCharts() {
      this.updateScoreDistribution()
    },

    updateScoreDistribution() {
      if (!this.examReport) return
      
      // 创建成绩分布饼状图 - 使用750分制的分段
      const scoreRanges = [
        { name: '优秀 (675-750)', min: 675, max: 750, count: 0 },
        { name: '良好 (600-674)', min: 600, max: 674, count: 0 },
        { name: '中等 (525-599)', min: 525, max: 599, count: 0 },
        { name: '及格 (450-524)', min: 450, max: 524, count: 0 },
        { name: '待提高 (0-449)', min: 0, max: 449, count: 0 }
      ]
      
      // 统计总分分布（使用赋分后总分）
      this.processedStudentGrades.forEach(student => {
        const score = student.total_scaled || student.total_original
        if (score && !isNaN(score)) {
          const normalizedScore = parseFloat(score)
          const range = scoreRanges.find(r => normalizedScore >= r.min && normalizedScore <= r.max)
          if (range) range.count++
        }
      })
      
      this.scoreDistributionOption = {
        title: {
          text: '总分成绩分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}人 ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [{
          name: '学生数量',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          data: scoreRanges.filter(r => r.count > 0).map(r => ({
            name: r.name,
            value: r.count
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: false
          },
          label: {
            show: true,
            position: 'center'
          }
        }]
      }
    },

    getChangeClass(change) {
      if (change > 0) return 'score-increase'
      if (change < 0) return 'score-decrease'
      return 'score-no-change'
    },

    getRankChangeClass(change) {
      if (change < 0) return 'rank-improve' // 排名下降是进步
      if (change > 0) return 'rank-decline' // 排名上升是退步
      return 'rank-no-change'
    },

    getRankChangeIcon(change) {
      if (change < 0) return 'ArrowUp' // 排名进步
      if (change > 0) return 'ArrowDown' // 排名退步
      return 'Minus'
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    },

    viewStudentDetail(student) {
      this.$router.push({
        path: '/student-analysis',
        query: { 
          name: student.student_name, 
          school: student.school 
        }
      })
    }
  }
}
</script>

<style scoped>
.exam-analysis {
  max-width: 1600px;
  margin: 0 auto;
}

.exam-selection {
  margin-bottom: 30px;
}

.exam-overview {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 15px;
}

.stat-number {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.average-scores {
  margin-top: 25px;
}

.avg-score-card {
  text-align: center;
  margin-bottom: 10px;
}

.avg-score-content {
  padding: 12px;
}

.subject-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.avg-score {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.score-change {
  font-size: 12px;
}

.score-increase {
  color: #67C23A;
}

.score-decrease {
  color: #F56C6C;
}

.score-no-change {
  color: #909399;
}

.rank-improve {
  color: #67C23A;
  font-size: 11px;
}

.rank-decline {
  color: #F56C6C;
  font-size: 11px;
}

.rank-no-change {
  color: #909399;
  font-size: 11px;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-container {
  height: 400px;
}

.chart {
  height: 100%;
  width: 100%;
}

.grades-table {
  margin-top: 30px;
  width: 100%;
  overflow-x: auto;
}

.table-controls {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

/* 表格列宽优化 */
:deep(.el-table .cell) {
  padding: 0 5px;
  font-size: 12px;
  text-align: center;
}

:deep(.el-table th) {
  padding: 8px 0;
  text-align: center;
  background-color: #f5f7fa;
}

:deep(.el-table td) {
  padding: 6px 0;
  text-align: center;
}

/* 排名变化样式 */
.rank-change {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rank-change > div:first-child {
  font-weight: bold;
}

.rank-change > div:last-child {
  font-size: 10px;
  display: flex;
  align-items: center;
  gap: 2px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .exam-analysis {
    max-width: 100%;
    padding: 0 10px;
  }
}

/* 表格滚动 */
.grades-table :deep(.el-table) {
  font-size: 12px;
  width: 100% !important;
  table-layout: fixed;
}

.grades-table :deep(.el-table__body-wrapper) {
  max-height: 600px;
  overflow-y: auto;
}
</style>