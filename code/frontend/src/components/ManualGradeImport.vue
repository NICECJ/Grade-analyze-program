<template>
  <div class="manual-grade-import">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>手工录入成绩</span>
        </div>
      </template>

      <el-form :model="gradeForm" :rules="rules" ref="gradeFormRef" label-width="120px">
        <!-- 考试信息 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择考试" prop="examId">
              <el-select 
                v-model="gradeForm.examId" 
                placeholder="请选择考试"
                style="width: 100%;"
                @change="onExamChange"
              >
                <el-option
                  v-for="exam in exams"
                  :key="exam.id"
                  :label="`${exam.exam_name} (${formatDate(exam.exam_date)})`"
                  :value="exam.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <el-button type="success" @click="showCreateExamDialog = true">
                新建考试
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 学生信息 -->
        <el-divider content-position="left">学生信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学生姓名" prop="studentName">
              <el-input 
                v-model="gradeForm.studentName" 
                placeholder="请输入学生姓名"
                @blur="searchExistingStudent"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学校" prop="school">
              <el-input v-model="gradeForm.school" placeholder="请输入学校名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="班级" prop="currentClass">
              <el-input v-model="gradeForm.currentClass" placeholder="请输入班级" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="考试类型" prop="examType">
              <el-select v-model="gradeForm.examType" placeholder="选择考试类型" style="width: 100%;">
                <el-option label="物理类" value="PHYSICS" />
                <el-option label="历史类" value="HISTORY" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="选科组合" prop="subjectCombination">
              <el-select v-model="gradeForm.subjectCombination" placeholder="选择选科组合" style="width: 100%;">
                <el-option label="物化生" value="物化生" />
                <el-option label="物化地" value="物化地" />
                <el-option label="物化政" value="物化政" />
                <el-option label="物生地" value="物生地" />
                <el-option label="物生政" value="物生政" />
                <el-option label="物地政" value="物地政" />
                <el-option label="史化生" value="史化生" />
                <el-option label="史化地" value="史化地" />
                <el-option label="史化政" value="史化政" />
                <el-option label="史生地" value="史生地" />
                <el-option label="史生政" value="史生政" />
                <el-option label="史地政" value="史地政" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 成绩录入 -->
        <el-divider content-position="left">成绩录入</el-divider>
        
        <!-- 必修科目 -->
        <h4>必修科目</h4>
        <el-row :gutter="15">
          <el-col :span="8" v-for="subject in requiredSubjects" :key="subject">
            <el-card class="subject-card">
              <template #header>
                <span>{{ subject }}</span>
              </template>
              <el-form-item :label="`${subject}成绩`" :prop="`subjects.${subject}.score`">
                <el-input-number 
                  v-model="gradeForm.subjects[subject].score" 
                  :min="0" 
                  :max="150" 
                  :precision="1"
                  style="width: 100%;"
                  placeholder="请输入成绩"
                />
              </el-form-item>
              <el-form-item :label="`${subject}排名`">
                <el-input-number 
                  v-model="gradeForm.subjects[subject].rank" 
                  :min="1" 
                  style="width: 100%;"
                  placeholder="省排名"
                />
              </el-form-item>
            </el-card>
          </el-col>
        </el-row>

        <!-- 主科（物理/历史） -->
        <h4>主科</h4>
        <el-row :gutter="15">
          <el-col :span="8">
            <el-card class="subject-card">
              <template #header>
                <span>{{ gradeForm.examType === 'PHYSICS' ? '物理' : '历史' }}</span>
              </template>
              <el-form-item :label="`成绩`" :prop="`subjects.${gradeForm.examType === 'PHYSICS' ? '物理' : '历史'}.score`">
                <el-input-number 
                  v-model="gradeForm.subjects[gradeForm.examType === 'PHYSICS' ? '物理' : '历史'].score" 
                  :min="0" 
                  :max="100" 
                  :precision="1"
                  style="width: 100%;"
                  placeholder="请输入成绩"
                />
              </el-form-item>
              <el-form-item :label="`排名`">
                <el-input-number 
                  v-model="gradeForm.subjects[gradeForm.examType === 'PHYSICS' ? '物理' : '历史'].rank" 
                  :min="1" 
                  style="width: 100%;"
                  placeholder="省排名"
                />
              </el-form-item>
            </el-card>
          </el-col>
        </el-row>

        <!-- 选考科目 -->
        <h4>选考科目</h4>
        <el-row :gutter="15">
          <el-col :span="8" v-for="subject in electiveSubjects" :key="subject">
            <el-card class="subject-card" v-if="isSubjectSelected(subject)">
              <template #header>
                <span>{{ subject }}</span>
              </template>
              <el-form-item :label="`原始成绩`" :prop="`subjects.${subject}.originalScore`">
                <el-input-number 
                  v-model="gradeForm.subjects[subject].originalScore" 
                  :min="0" 
                  :max="100" 
                  :precision="1"
                  style="width: 100%;"
                  placeholder="原始成绩"
                />
              </el-form-item>
              <el-form-item :label="`赋分成绩`" :prop="`subjects.${subject}.scaledScore`">
                <el-input-number 
                  v-model="gradeForm.subjects[subject].scaledScore" 
                  :min="30" 
                  :max="100" 
                  :precision="1"
                  style="width: 100%;"
                  placeholder="赋分成绩"
                />
              </el-form-item>
              <el-form-item :label="`排名`">
                <el-input-number 
                  v-model="gradeForm.subjects[subject].rank" 
                  :min="1" 
                  style="width: 100%;"
                  placeholder="省排名"
                />
              </el-form-item>
            </el-card>
          </el-col>
        </el-row>

        <!-- 总分 -->
        <h4>总分</h4>
        <el-row :gutter="15">
          <el-col :span="12">
            <el-card class="subject-card">
              <template #header>
                <span>总分</span>
              </template>
              <el-form-item label="赋分前总分" prop="subjects.总分.originalScore">
                <el-input-number 
                  v-model="gradeForm.subjects['总分'].originalScore" 
                  :min="0" 
                  :max="750" 
                  :precision="1"
                  style="width: 100%;"
                  placeholder="赋分前总分"
                />
              </el-form-item>
              <el-form-item label="赋分后总分" prop="subjects.总分.scaledScore">
                <el-input-number 
                  v-model="gradeForm.subjects['总分'].scaledScore" 
                  :min="0" 
                  :max="750" 
                  :precision="1"
                  style="width: 100%;"
                  placeholder="赋分后总分"
                />
              </el-form-item>
              <el-form-item label="赋分前排名">
                <el-input-number 
                  v-model="gradeForm.subjects['总分'].originalRank" 
                  :min="1" 
                  style="width: 100%;"
                  placeholder="赋分前省排名"
                />
              </el-form-item>
              <el-form-item label="赋分后排名">
                <el-input-number 
                  v-model="gradeForm.subjects['总分'].scaledRank" 
                  :min="1" 
                  style="width: 100%;"
                  placeholder="赋分后省排名"
                />
              </el-form-item>
            </el-card>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <el-form-item style="margin-top: 30px;">
          <el-button type="primary" @click="submitGrades" :loading="submitting">
            提交成绩
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="success" @click="calculateTotal">自动计算总分</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 新建考试对话框 -->
    <el-dialog v-model="showCreateExamDialog" title="新建考试" width="500px">
      <el-form :model="newExamForm" :rules="examRules" ref="newExamFormRef" label-width="100px">
        <el-form-item label="考试名称" prop="examName">
          <el-input v-model="newExamForm.examName" placeholder="请输入考试名称" />
        </el-form-item>
        <el-form-item label="考试日期" prop="examDate">
          <el-date-picker
            v-model="newExamForm.examDate"
            type="date"
            placeholder="选择考试日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="考试类型" prop="examType">
          <el-select v-model="newExamForm.examType" placeholder="选择考试类型" style="width: 100%;">
            <el-option label="物理类" value="PHYSICS" />
            <el-option label="历史类" value="HISTORY" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试级别" prop="examLevel">
          <el-select v-model="newExamForm.examLevel" placeholder="选择考试级别" style="width: 100%;">
            <el-option label="校级" value="SCHOOL" />
            <el-option label="市级" value="CITY" />
            <el-option label="省级" value="PROVINCE" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateExamDialog = false">取消</el-button>
        <el-button type="primary" @click="createExam" :loading="creatingExam">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'ManualGradeImport',
  data() {
    return {
      gradeForm: {
        examId: null,
        studentName: '',
        school: '',
        currentClass: '',
        examType: 'PHYSICS',
        subjectCombination: '',
        subjects: {}
      },
      newExamForm: {
        examName: '',
        examDate: null,
        examType: 'PHYSICS',
        examLevel: 'SCHOOL'
      },
      exams: [],
      submitting: false,
      creatingExam: false,
      showCreateExamDialog: false,
      requiredSubjects: ['语文', '数学', '英语'],
      electiveSubjects: ['化学', '生物', '地理', '政治'],
      rules: {
        examId: [{ required: true, message: '请选择考试', trigger: 'change' }],
        studentName: [{ required: true, message: '请输入学生姓名', trigger: 'blur' }],
        school: [{ required: true, message: '请输入学校名称', trigger: 'blur' }],
        currentClass: [{ required: true, message: '请输入班级', trigger: 'blur' }],
        examType: [{ required: true, message: '请选择考试类型', trigger: 'change' }]
      },
      examRules: {
        examName: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
        examDate: [{ required: true, message: '请选择考试日期', trigger: 'change' }],
        examType: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
        examLevel: [{ required: true, message: '请选择考试级别', trigger: 'change' }]
      }
    }
  },
  mounted() {
    this.loadExams()
    this.initializeSubjects()
  },
  watch: {
    'gradeForm.examType'() {
      this.initializeSubjects()
    },
    'gradeForm.subjectCombination'() {
      this.initializeSubjects()
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

    initializeSubjects() {
      const subjects = {}
      
      // 初始化必修科目
      this.requiredSubjects.forEach(subject => {
        subjects[subject] = {
          score: null,
          rank: null
        }
      })
      
      // 初始化主科
      const mainSubject = this.gradeForm.examType === 'PHYSICS' ? '物理' : '历史'
      subjects[mainSubject] = {
        score: null,
        rank: null
      }
      
      // 初始化选考科目
      this.electiveSubjects.forEach(subject => {
        subjects[subject] = {
          originalScore: null,
          scaledScore: null,
          rank: null
        }
      })
      
      // 初始化总分
      subjects['总分'] = {
        originalScore: null,
        scaledScore: null,
        originalRank: null,
        scaledRank: null
      }
      
      this.gradeForm.subjects = subjects
    },

    isSubjectSelected(subject) {
      if (!this.gradeForm.subjectCombination) return false
      return this.gradeForm.subjectCombination.includes(subject)
    },

    async searchExistingStudent() {
      if (!this.gradeForm.studentName || !this.gradeForm.school) return
      
      try {
        // 搜索现有学生信息
        const students = await api.students.searchStudents({
          name: this.gradeForm.studentName,
          school: this.gradeForm.school
        })
        
        if (students.length > 0) {
          const student = students[0]
          this.gradeForm.currentClass = student.current_class
          this.gradeForm.examType = student.exam_type || 'PHYSICS'
          this.gradeForm.subjectCombination = student.subject_combination || ''
          this.$message.success('已找到学生信息并自动填充')
        }
      } catch (error) {
        console.warn('搜索学生信息失败:', error)
      }
    },

    onExamChange() {
      // 当选择考试时，可以根据考试类型自动设置学生考试类型
      const selectedExam = this.exams.find(exam => exam.id === this.gradeForm.examId)
      if (selectedExam && selectedExam.exam_type) {
        this.gradeForm.examType = selectedExam.exam_type
      }
    },

    calculateTotal() {
      const subjects = this.gradeForm.subjects
      let originalTotal = 0
      let scaledTotal = 0
      
      // 计算必修科目总分
      this.requiredSubjects.forEach(subject => {
        if (subjects[subject].score) {
          originalTotal += subjects[subject].score
          scaledTotal += subjects[subject].score
        }
      })
      
      // 计算主科总分
      const mainSubject = this.gradeForm.examType === 'PHYSICS' ? '物理' : '历史'
      if (subjects[mainSubject].score) {
        originalTotal += subjects[mainSubject].score
        scaledTotal += subjects[mainSubject].score
      }
      
      // 计算选考科目总分
      this.electiveSubjects.forEach(subject => {
        if (this.isSubjectSelected(subject)) {
          if (subjects[subject].originalScore) {
            originalTotal += subjects[subject].originalScore
          }
          if (subjects[subject].scaledScore) {
            scaledTotal += subjects[subject].scaledScore
          }
        }
      })
      
      // 设置总分
      subjects['总分'].originalScore = originalTotal || null
      subjects['总分'].scaledScore = scaledTotal || null
      
      this.$message.success('总分计算完成')
    },

    async createExam() {
      try {
        await this.$refs.newExamFormRef.validate()
        
        this.creatingExam = true
        
        // 创建考试
        const examData = {
          exam_name: this.newExamForm.examName,
          exam_date: this.newExamForm.examDate.toISOString().split('T')[0],
          exam_type: this.newExamForm.examType,
          exam_level: this.newExamForm.examLevel
        }
        
        const newExam = await api.exams.createExam(examData)
        this.exams.unshift(newExam)
        this.gradeForm.examId = newExam.id
        this.showCreateExamDialog = false
        this.$message.success('考试创建成功')
        
        // 重置表单
        this.$refs.newExamFormRef.resetFields()
      } catch (error) {
        this.$message.error('创建考试失败: ' + error.message)
      } finally {
        this.creatingExam = false
      }
    },

    async submitGrades() {
      try {
        await this.$refs.gradeFormRef.validate()
        
        this.submitting = true
        
        // 准备提交数据
        const submitData = {
          exam_id: this.gradeForm.examId,
          student: {
            name: this.gradeForm.studentName,
            school: this.gradeForm.school,
            current_class: this.gradeForm.currentClass,
            exam_type: this.gradeForm.examType,
            subject_combination: this.gradeForm.subjectCombination
          },
          grades: []
        }
        
        // 处理各科成绩
        Object.keys(this.gradeForm.subjects).forEach(subjectName => {
          const subjectData = this.gradeForm.subjects[subjectName]
          
          if (subjectName === '总分') {
            // 处理总分
            if (subjectData.originalScore || subjectData.scaledScore) {
              submitData.grades.push({
                subject_name: '总分',
                original_score: subjectData.originalScore,
                scaled_score: subjectData.scaledScore,
                rank_province: subjectData.originalRank,
                scaled_rank_province: subjectData.scaledRank
              })
            }
          } else if (this.electiveSubjects.includes(subjectName) && this.isSubjectSelected(subjectName)) {
            // 处理选考科目
            if (subjectData.originalScore || subjectData.scaledScore) {
              submitData.grades.push({
                subject_name: subjectName,
                original_score: subjectData.originalScore,
                scaled_score: subjectData.scaledScore,
                rank_province: subjectData.rank
              })
            }
          } else if (subjectData.score) {
            // 处理必修科目和主科
            submitData.grades.push({
              subject_name: subjectName,
              original_score: subjectData.score,
              rank_province: subjectData.rank
            })
          }
        })
        
        // 提交数据
        await api.grades.manualImport(submitData)
        this.$message.success('成绩录入成功')
        this.resetForm()
      } catch (error) {
        this.$message.error('成绩录入失败: ' + error.message)
      } finally {
        this.submitting = false
      }
    },

    resetForm() {
      this.$refs.gradeFormRef.resetFields()
      this.initializeSubjects()
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.manual-grade-import {
  max-width: 1200px;
  margin: 0 auto;
}

.subject-card {
  margin-bottom: 15px;
}

.subject-card .el-card__header {
  padding: 10px 20px;
  background-color: #f5f7fa;
}

.subject-card .el-form-item {
  margin-bottom: 15px;
}

h4 {
  color: #409EFF;
  margin: 20px 0 15px 0;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .manual-grade-import {
    padding: 0 10px;
  }
  
  .el-col {
    margin-bottom: 15px;
  }
}
</style>