<template>
  <div class="ranking-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排名分析</span>
        </div>
      </template>

      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-form :model="filterForm" inline>
          <el-form-item label="科目">
            <el-select v-model="filterForm.subject" placeholder="选择科目">
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
          <el-form-item label="显示数量">
            <el-select v-model="filterForm.limit" placeholder="选择数量">
              <el-option label="前10名" :value="10" />
              <el-option label="前20名" :value="20" />
              <el-option label="前50名" :value="50" />
              <el-option label="前100名" :value="100" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadTopPerformers" :loading="loading">
              查询
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ topPerformers.length }}</div>
                <div class="stat-label">优秀学生数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ uniqueSchools }}</div>
                <div class="stat-label">涉及学校数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ averageScore }}</div>
                <div class="stat-label">平均分</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ filterForm.subject }}</div>
                <div class="stat-label">当前科目</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 排名表格 -->
      <div class="ranking-table">
        <h3>{{ filterForm.subject }} 排名前{{ filterForm.limit }}名</h3>
        <el-table :data="topPerformers" style="width: 100%" stripe>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="student_id" label="学号" width="120" />
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="school" label="学校" />
          <el-table-column prop="current_class" label="班级" width="100" />
          <el-table-column prop="score" label="分数" width="80">
            <template #default="scope">
              <el-tag type="success">{{ scope.row.score }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rank_school" label="校排名" width="80" />
          <el-table-column prop="rank_city" label="市排名" width="80" />
          <el-table-column prop="rank_province" label="省排名" width="80">
            <template #default="scope">
              <el-tag 
                :type="getRankTagType(scope.row.rank_province)"
                effect="dark"
              >
                {{ scope.row.rank_province }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="exam_name" label="考试名称" />
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewStudentDetail(scope.row.student_id)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 学校分布图表 -->
      <div v-if="topPerformers.length > 0" class="chart-section">
        <h3>学校分布统计</h3>
        <div class="chart-container">
          <v-chart class="chart" :option="schoolChartOption" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
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
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  name: 'RankingAnalysis',
  components: {
    VChart
  },
  data() {
    return {
      filterForm: {
        subject: '总分',
        limit: 20
      },
      topPerformers: [],
      loading: false,
      schoolChartOption: {}
    }
  },
  computed: {
    uniqueSchools() {
      const schools = new Set(this.topPerformers.map(p => p.school).filter(s => s))
      return schools.size
    },
    averageScore() {
      if (this.topPerformers.length === 0) return 0
      const total = this.topPerformers.reduce((sum, p) => sum + (parseFloat(p.score) || 0), 0)
      return (total / this.topPerformers.length).toFixed(1)
    }
  },
  mounted() {
    this.loadTopPerformers()
  },
  methods: {
    async loadTopPerformers() {
      this.loading = true
      try {
        const result = await api.getTopPerformers(this.filterForm.subject, this.filterForm.limit)
        this.topPerformers = result.top_performers || []
        this.updateSchoolChart()
      } catch (error) {
        this.$message.error('加载数据失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },

    updateSchoolChart() {
      if (this.topPerformers.length === 0) return

      // 统计各学校人数
      const schoolStats = {}
      this.topPerformers.forEach(performer => {
        const school = performer.school || '未知学校'
        schoolStats[school] = (schoolStats[school] || 0) + 1
      })

      const data = Object.entries(schoolStats).map(([name, value]) => ({
        name,
        value
      }))

      this.schoolChartOption = {
        title: {
          text: '优秀学生学校分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'middle'
        },
        series: [
          {
            name: '学生数量',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            data: data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
    },

    getRankTagType(rank) {
      if (rank <= 10) return 'danger'
      if (rank <= 50) return 'warning'
      if (rank <= 100) return 'info'
      return ''
    },

    viewStudentDetail(studentId) {
      this.$router.push({
        path: '/student',
        query: { studentId }
      })
    }
  },
  watch: {
    '$route.query.studentId': {
      immediate: true,
      handler(studentId) {
        if (studentId) {
          // 如果从其他页面跳转过来带有学生ID，可以在这里处理
        }
      }
    }
  }
}
</script>

<style scoped>
.ranking-analysis {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-section {
  margin-bottom: 20px;
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
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.ranking-table {
  margin-bottom: 30px;
}

.chart-section {
  margin-top: 30px;
}

.chart-container {
  height: 400px;
  margin: 20px 0;
}

.chart {
  height: 100%;
  width: 100%;
}
</style>