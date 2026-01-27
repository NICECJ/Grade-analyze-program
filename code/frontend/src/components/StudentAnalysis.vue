<template>
  <div class="student-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生成绩分析</span>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="search-section">
        <el-form :model="searchForm" inline>
          <el-form-item label="学生姓名">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入学生姓名"
              @keyup.enter="searchStudent"
            />
          </el-form-item>
          <el-form-item label="学校">
            <el-input
              v-model="searchForm.school"
              placeholder="请输入学校名称"
              @keyup.enter="searchStudent"
            />
          </el-form-item>
          <el-form-item label="科目">
            <el-select v-model="searchForm.subject" placeholder="选择科目">
              <el-option label="总分" value="总分" />
              <el-option label="语文" value="语文" />
              <el-option label="数学" value="数学" />
              <el-option label="英语" value="英语" />
              <el-option label="物理" value="物理" />
              <el-option label="化学" value="化学" />
              <el-option label="生物" value="生物" />
              <el-option label="历史" value="历史" />
              <el-option label="地理" value="地理" />
              <el-option label="政治" value="政治" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchStudent" :loading="loading">
              查询
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 学生信息 -->
      <div v-if="studentData" class="student-info">
        <h3>学生信息</h3>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="姓名">
            {{ studentData.student_name }}
          </el-descriptions-item>
          <el-descriptions-item label="学校">
            {{ studentData.school || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="班级">
            {{ studentData.current_class || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="学生ID">
            {{ studentData.student_id }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 排名趋势图 -->
      <div v-if="trendData" class="trend-section">
        <h3>{{ searchForm.subject }} 排名趋势分析</h3>
        <div class="chart-container">
          <v-chart class="chart" :option="chartOption" />
        </div>
        
        <!-- 波动预警 -->
        <div v-if="trendData.warnings && trendData.warnings.length > 0" class="warnings">
          <h4>波动预警</h4>
          <el-alert
            v-for="warning in trendData.warnings"
            :key="warning.exam"
            :title="`${warning.exam}: 排名${warning.type === 'improvement' ? '提升' : '下降'}${Math.abs(warning.rank_change)}名`"
            :type="warning.type === 'improvement' ? 'success' : 'warning'"
            style="margin-bottom: 10px;"
          />
        </div>
      </div>

      <!-- 历史成绩表格 -->
      <div v-if="studentData" class="history-section">
        <h3>历史成绩</h3>
        <el-table :data="studentData.grades" style="width: 100%">
          <el-table-column prop="exam_name" label="考试名称" />
          <el-table-column prop="subject_name" label="科目" />
          <el-table-column prop="score" label="分数" />
          <el-table-column prop="rank_school" label="校排名" />
          <el-table-column prop="rank_city" label="市排名" />
          <el-table-column prop="rank_province" label="省排名" />
          <el-table-column prop="exam_date" label="考试时间">
            <template #default="scope">
              {{ formatDate(scope.row.exam_date) }}
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
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '../api'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  name: 'StudentAnalysis',
  components: {
    VChart
  },
  data() {
    return {
      searchForm: {
        name: '',
        school: '',
        subject: '总分'
      },
      studentData: null,
      trendData: null,
      loading: false,
      chartOption: {}
    }
  },
  mounted() {
    // 检查路由参数
    if (this.$route.query.name && this.$route.query.school) {
      this.searchForm.name = this.$route.query.name
      this.searchForm.school = this.$route.query.school
      this.searchStudent()
    }
  },
  methods: {
    async searchStudent() {
      if (!this.searchForm.name || !this.searchForm.school) {
        this.$message.error('请输入学生姓名和学校')
        return
      }

      this.loading = true
      try {
        // 获取学生历史数据
        this.studentData = await api.grades.getStudentHistory(
          this.searchForm.name, 
          this.searchForm.school
        )
        
        // 过滤指定科目的成绩数据用于趋势分析
        if (this.studentData && this.studentData.grades) {
          const subjectGrades = this.studentData.grades.filter(
            grade => grade.subject_name === this.searchForm.subject
          )
          
          this.trendData = {
            trend_data: subjectGrades.map(grade => ({
              exam_name: grade.exam_name,
              exam_date: grade.exam_date,
              rank_school: grade.rank_school,
              rank_city: grade.rank_city,
              rank_province: grade.rank_province,
              score: grade.score
            })),
            warnings: this.calculateWarnings(subjectGrades)
          }
        }
        
        this.updateChart()
      } catch (error) {
        this.$message.error('查询失败: ' + (error.message || '未知错误'))
        this.studentData = null
        this.trendData = null
      } finally {
        this.loading = false
      }
    },

    calculateWarnings(grades) {
      const warnings = []
      if (grades.length < 2) return warnings
      
      // 按考试日期排序
      const sortedGrades = grades.sort((a, b) => new Date(a.exam_date) - new Date(b.exam_date))
      
      for (let i = 1; i < sortedGrades.length; i++) {
        const current = sortedGrades[i]
        const previous = sortedGrades[i - 1]
        
        if (current.rank_province && previous.rank_province) {
          const rankChange = current.rank_province - previous.rank_province
          
          // 排名变化超过10名时发出预警
          if (Math.abs(rankChange) > 10) {
            warnings.push({
              exam: current.exam_name,
              type: rankChange < 0 ? 'improvement' : 'decline',
              rank_change: rankChange
            })
          }
        }
      }
      
      return warnings
    },

    updateChart() {
      if (!this.trendData || !this.trendData.trend_data) return

      const data = this.trendData.trend_data
      const examNames = data.map(item => item.exam_name)
      const schoolRanks = data.map(item => item.rank_school)
      const cityRanks = data.map(item => item.rank_city)
      const provinceRanks = data.map(item => item.rank_province)

      this.chartOption = {
        title: {
          text: `${this.searchForm.subject} 排名趋势`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['校排名', '市排名', '省排名'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: examNames,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          inverse: true, // 排名越小越好，所以反转Y轴
          name: '排名'
        },
        series: [
          {
            name: '校排名',
            type: 'line',
            data: schoolRanks,
            smooth: true,
            lineStyle: {
              color: '#409EFF'
            }
          },
          {
            name: '市排名',
            type: 'line',
            data: cityRanks,
            smooth: true,
            lineStyle: {
              color: '#67C23A'
            }
          },
          {
            name: '省排名',
            type: 'line',
            data: provinceRanks,
            smooth: true,
            lineStyle: {
              color: '#E6A23C'
            }
          }
        ]
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }
  },
  watch: {
    'searchForm.subject'() {
      if (this.studentData) {
        this.searchStudent()
      }
    }
  }
}
</script>

<style scoped>
.student-analysis {
  max-width: 1200px;
  margin: 0 auto;
}

.search-section {
  margin-bottom: 20px;
}

.student-info {
  margin-bottom: 30px;
}

.trend-section {
  margin-bottom: 30px;
}

.chart-container {
  height: 400px;
  margin: 20px 0;
}

.chart {
  height: 100%;
  width: 100%;
}

.warnings {
  margin-top: 20px;
}

.history-section {
  margin-top: 30px;
}
</style>